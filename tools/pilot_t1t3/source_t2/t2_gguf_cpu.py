#!/usr/bin/env python3
"""TTM P02 synthetic-only GGUF v3 exporter and independent readback.

No corpus access, network, GPU, checkpoint loading, or model training. The
synthetic token vocabulary is NOT the eventual TRAIN-only TinyStories BPE.
Usage: python tools/pilot_t2/t2_gguf_cpu.py export --repo . --out _tmp/ttm_t2/f32.gguf
       python tools/pilot_t2/t2_gguf_cpu.py readback --repo . --file _tmp/ttm_t2/f32.gguf
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import struct
import sys

import numpy as np
import torch

PIN_P02_BLOB = '9762343e06cf800b50574c2871ae1ed58537fb18'
PIN_LLAMA = '372dc5ca157276beb6c67b2e92477e8d662e964a'
SEED = 20261108
CFG = dict(vocab_size=2048, max_seq_len=256, n_embd=256, n_layer=4, n_head=4, norm_type='layernorm')
N_PARAMS = 3749376
MAGIC = b'GGUF'
VERSION = 3
ALIGN = 32
STRING = 8
ARRAY = 9
UINT32 = 4
INT32 = 5
FLOAT32 = 6
F32 = 0
F16 = 1


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def load_model(repo: Path):
    src = repo / 'src/p02/transformer_core.py'
    if not src.is_file() or git_blob_sha(src) != PIN_P02_BLOB:
        raise ValueError('P02_SOURCE_GIT_BLOB_PIN_MISMATCH')
    module_name = 'ttm_p02_t2_qa'
    spec = importlib.util.spec_from_file_location(module_name, src)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    torch.manual_seed(SEED)
    with torch.device('cpu'):
        model = module.GPT(module.P02Config(**CFG)).eval()
    model = model.float()
    n = sum(p.numel() for p in model.parameters())
    if n != N_PARAMS:
        raise ValueError(f'P02_PARAM_COUNT_MISMATCH:{n} != {N_PARAMS}')
    if model.head.weight.data_ptr() != model.tok.weight.data_ptr():
        raise ValueError('P02_TIED_HEAD_BROKEN')
    return model


def gpt2_byte_chars():
    bs = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
    cs = bs.copy(); n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b); cs.append(256 + n); n += 1
    return {b: chr(c) for b, c in zip(bs, cs)}


def synthetic_vocab():
    """Simple deterministic BPE proof fixture, NOT real TinyStories tokenizer.

    256 byte tokens, EOS=256, then exactly 1791 pair merges.
    This deliberately has no GPT-2 regex pretok and tests that gap explicitly.
    """
    mapping = gpt2_byte_chars()
    tokens = [mapping[i] for i in range(256)] + ['<|endoftext|>']
    merges = []
    for prefix in b'abcdefg':
        for suffix in range(256):
            if len(merges) == 1791:
                break
            left, right = mapping[prefix], mapping[suffix]
            merges.append(left + ' ' + right)
            tokens.append(left + right)
        if len(merges) == 1791:
            break
    assert len(tokens) == 2048 and len(merges) == 1791 and len(set(tokens)) == 2048
    return tokens, merges


def synth_tokenize(text: str, tokens: list[str], merges: list[str]) -> list[int]:
    """Whole-string byte-BPE oracle (independent from GPT2 regex).

    Rank merges are applied to adjacent token ID pairs until no pair remains.
    """
    charmap = gpt2_byte_chars()
    ids = list(text.encode('utf-8'))
    # All synthetic merges consist of two base-byte tokens, never longer.
    by_char = {token: i for i, token in enumerate(tokens[:256])}
    by_pair = {}
    for rank, merge in enumerate(merges):
        left, right = merge.split(' ', 1)
        by_pair[(by_char[left], by_char[right])] = (rank, 257 + rank)
    while len(ids) >= 2:
        candidate = [(by_pair[(ids[i], ids[i+1])][0], i, by_pair[(ids[i], ids[i+1])][1])
                     for i in range(len(ids) - 1) if (ids[i], ids[i+1]) in by_pair]
        if not candidate:
            break
        _, i, new_id = min(candidate)
        ids[i:i+2] = [new_id]
    return ids


def tensor_map(state: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
    mapped = {}
    def take(src, dst):
        if src not in state:
            raise ValueError('STATE_KEY_MISSING:'+src)
        if dst in mapped:
            raise ValueError('DUPLICATE_GGUF_TENSOR:'+dst)
        t = state[src].detach().cpu().contiguous()
        if not torch.isfinite(t).all().item():
            raise ValueError('NONFINITE:'+src)
        mapped[dst] = t
    take('tok.weight', 'token_embd.weight')
    take('pos.weight', 'position_embd.weight')
    take('final_ln.weight', 'output_norm.weight')
    take('final_ln.bias', 'output_norm.bias')
    for i in range(4):
        pairs = {
            f'blocks.{i}.ln1': f'blk.{i}.attn_norm',
            f'blocks.{i}.attn.qkv': f'blk.{i}.attn_qkv',
            f'blocks.{i}.attn.proj': f'blk.{i}.attn_output',
            f'blocks.{i}.ln2': f'blk.{i}.ffn_norm',
            f'blocks.{i}.mlp.0': f'blk.{i}.ffn_up',
            f'blocks.{i}.mlp.2': f'blk.{i}.ffn_down',
        }
        for src, dst in pairs.items():
            for suf in ('weight', 'bias'):
                take(src+'.'+suf, dst+'.'+suf)
    expected_state = {'tok.weight', 'pos.weight', 'final_ln.weight',
                      'final_ln.bias', 'head.weight'}
    expected_state.update(
        f'blocks.{i}.{mod}.{suffix}'
        for i in range(4)
        for mod in ('ln1', 'attn.qkv', 'attn.proj', 'ln2', 'mlp.0', 'mlp.2')
        for suffix in ('weight', 'bias')
    )
    if set(state) != expected_state:
        raise ValueError('UNMAPPED_STATE_KEYS')
    if len(mapped) != 52:
        raise ValueError('GGUF_TENSOR_COUNT_WRONG')
    # No transpose: nn.Linear already stores [out, in], which GGUF's
    # row-major tensor data expects. HF GPT2 Conv1D is [in, out] and its
    # upstream converter transposes; applying that here is a double transpose.
    return mapped


def packstr(s: str) -> bytes:
    b = s.encode('utf-8')
    return struct.pack('<Q', len(b)) + b


def packvalue(value):
    if isinstance(value, str):
        return STRING, packstr(value)
    if isinstance(value, int):
        return UINT32, struct.pack('<I', value)
    if isinstance(value, float):
        return FLOAT32, struct.pack('<f', value)
    if isinstance(value, tuple):
        elem_type, arr = value
        if elem_type == STRING:
            return ARRAY, struct.pack('<IQ', STRING, len(arr)) + b''.join(packstr(x) for x in arr)
        if elem_type == INT32:
            return ARRAY, struct.pack('<IQ', INT32, len(arr)) + struct.pack('<'+'i'*len(arr), *arr)
    raise TypeError('BAD_GGUF_METADATA_TYPE')


def build_metadata(tokens, merges):
    return {
        'general.architecture':'gpt2',
        'general.name':'TTM-Small-4M-T2-SYNTHETIC-UNTRAINED',
        'general.alignment':32,
        'general.file_type':0,
        'gpt2.context_length':256,
        'gpt2.block_count':4,
        'gpt2.embedding_length':256,
        'gpt2.feed_forward_length':1024,
        'gpt2.attention.head_count':4,
        'gpt2.attention.layer_norm_epsilon':1e-5,
        'tokenizer.ggml.model':'gpt2',
        'tokenizer.ggml.pre':'gpt-2',
        'tokenizer.ggml.tokens':(STRING,tokens),
        'tokenizer.ggml.token_type':(INT32,[3 if i == 256 else 1 for i in range(2048)]),
        'tokenizer.ggml.merges':(STRING,merges),
        'tokenizer.ggml.eos_token_id':256,
        'tokenizer.ggml.bos_token_id':256,
        'tokenizer.ggml.unknown_token_id':256,
    }


def align_up(n: int, alignment: int = ALIGN) -> int:
    return (n + alignment - 1) // alignment * alignment


def write_gguf(path: Path, model: torch.nn.Module, dtype: str) -> dict:
    if dtype not in ('f32', 'f16'):
        raise ValueError('BAD_DTYPE')
    tensors = tensor_map(model.state_dict())
    tokens, merges = synthetic_vocab()
    meta = build_metadata(tokens, merges)
    out_type = F32 if dtype == 'f32' else F16
    torch_dtype = torch.float32 if dtype == 'f32' else torch.float16
    encoded = []
    for name, v in tensors.items():
        arr = v.to(torch_dtype).numpy().astype('<f4' if dtype=='f32' else '<f2', copy=False)
        encoded.append((name, arr, arr.tobytes(order='C')))
    header = struct.pack('<4sIQQ', MAGIC, VERSION, len(encoded), len(meta))
    for key, val in meta.items():
        typ, payload = packvalue(val)
        header += packstr(key) + struct.pack('<I', typ) + payload
    offset = 0
    for name, array, raw in encoded:
        header += packstr(name) + struct.pack('<I', array.ndim)
        header += struct.pack('<'+'Q'*array.ndim, *reversed(array.shape))
        header += struct.pack('<IQ', out_type, offset)
        offset=align_up(offset+len(raw))
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError('GGUF_OUTPUT_ALREADY_EXISTS_NO_OVERWRITE')
    with path.open('xb') as f:
        f.write(header)
        f.write(b'\0'*(align_up(f.tell())-f.tell()))
        for _, arr, raw in encoded:
            f.write(raw)
            f.write(b'\0'*(align_up(len(raw))-len(raw)))
    return {'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes':path.stat().st_size,'n_tensors':len(encoded),'metadata_keys':len(meta),
            'dtype':dtype,'source_git_blob':PIN_P02_BLOB,'llama_cpp_sha':PIN_LLAMA,
            'trained':False,'tokenizer':'SYNTHETIC_ONLY_NOT_TRAIN_ONLY'}


def readstr(f):
    (n,) = struct.unpack('<Q', f.read(8))
    if n > 10_000_000:
        raise ValueError('STRING_SIZE_INVALID')
    return f.read(n).decode('utf-8')


def readvalue(f, typ):
    if typ == STRING: return readstr(f)
    if typ == UINT32: return struct.unpack('<I', f.read(4))[0]
    if typ == FLOAT32: return struct.unpack('<f', f.read(4))[0]
    if typ == ARRAY:
        t, n = struct.unpack('<IQ', f.read(12))
        if n > 10000: raise ValueError('ARRAY_TOO_LONG')
        if t == STRING: return [readstr(f) for _ in range(n)]
        if t == INT32: return list(struct.unpack('<'+'i'*n, f.read(4*n)))
    raise ValueError('UNSUPPORTED_GGUF_KV_TYPE:'+str(typ))


def parse_gguf(path: Path):
    with path.open('rb') as f:
        magic, ver, count, nkv=struct.unpack('<4sIQQ', f.read(24))
        if (magic,ver)!=(MAGIC,VERSION) or count>1000 or nkv>100:
            raise ValueError('GGUF_HEADER_INVALID')
        metadata={}
        for _ in range(nkv):
            key=readstr(f)
            (typ,)=struct.unpack('<I',f.read(4))
            if key in metadata: raise ValueError('DUPLICATE_METADATA')
            metadata[key]=readvalue(f,typ)
        desc={}
        for _ in range(count):
            name=readstr(f)
            (ndim,)=struct.unpack('<I',f.read(4))
            if ndim not in (1,2): raise ValueError('TENSOR_DIMS_INVALID')
            dims=struct.unpack('<'+'Q'*ndim,f.read(ndim*8))
            dtype,off=struct.unpack('<IQ',f.read(12))
            if name in desc:raise ValueError('DUPLICATE_TENSOR')
            desc[name]=(dims,dtype,off)
        data_start=align_up(f.tell(),metadata.get('general.alignment',ALIGN))
        tensors={}
        for name,(dims,dtype,off) in desc.items():
            if dtype not in (F32,F16): raise ValueError('TENSOR_DTYPE_INVALID')
            dt=np.dtype('<f4' if dtype==F32 else '<f2')
            sz=math.prod(dims)*dt.itemsize
            if data_start+off+sz>path.stat().st_size:raise ValueError('TENSOR_OUT_OF_RANGE')
            f.seek(data_start+off)
            tensors[name]=np.frombuffer(f.read(sz),dtype=dt).copy().reshape(tuple(reversed(dims)))
        return metadata,tensors,desc


def assert_readback(model, path, dtype):
    meta,tensors,desc=parse_gguf(path)
    expected=tensor_map(model.state_dict())
    assert set(tensors)==set(expected) and len(tensors)==52
    assert meta['general.architecture']=='gpt2'
    assert meta['gpt2.block_count']==4 and meta['gpt2.context_length']==256
    assert len(meta['tokenizer.ggml.tokens'])==2048
    assert len(meta['tokenizer.ggml.merges'])==1791
    maxerr=0.0
    for name,ref in expected.items():
        arr=tensors[name]
        assert arr.shape==tuple(ref.shape),(name,arr.shape,ref.shape)
        truth=ref.detach().numpy()
        err=float(np.max(np.abs(arr.astype('float32')-truth)))
        maxerr=max(err,maxerr)
        if dtype=='f32' and err!=0:raise AssertionError('GGUF_FP32_WEIGHT_PARITY:'+name)
        if dtype=='f16' and err>2e-4:raise AssertionError('GGUF_FP16_WEIGHT_ERROR:'+name+':'+str(err))
    return {'T2_GGUF_HEADER':'PASS','T2_GGUF_STRUCTURAL_TENSOR_QA':'PASS',
            'T2_GGUF_WEIGHT_READBACK':'PASS','max_abs_weight_error':maxerr,
            'TTM_LLAMA_CPP_LOGITS':'NOT_EXECUTED_NEEDS_PINNED_CPU_BACKEND',
            'TOKENIZER_LLAMA_PARITY':'NOT_EXECUTED_SYNTHETIC_ONLY'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['export','readback'])
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--out',type=Path)
    p.add_argument('--file',type=Path)
    p.add_argument('--dtype',choices=['f32','f16'],default='f32')
    args=p.parse_args()
    repo=args.repo.resolve(strict=True)
    if not (repo/'.git').exists() and not (repo/'.git').is_file():
        raise ValueError('NO_GIT_REPO_ROOT')
    model=load_model(repo)
    if args.action=='export':
        if args.out is None:raise ValueError('MISSING_OUT')
        target=args.out.resolve()
        # Do not write outside repo or follow external symlink directory.
        if repo not in target.parents:raise ValueError('OUTPUT_OUTSIDE_REPOSITORY')
        if target.parent.is_symlink():raise ValueError('SYMLINK_TARGET_PARENT')
        meta=write_gguf(target,model,args.dtype)
        meta.update(assert_readback(model,target,args.dtype))
    else:
        if args.file is None:raise ValueError('MISSING_FILE')
        meta=assert_readback(model,args.file.resolve(strict=True),args.dtype)
    print(json.dumps(meta,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
