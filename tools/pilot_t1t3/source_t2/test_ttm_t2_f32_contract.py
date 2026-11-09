"""Static CPU zero-science reference QA; no native backend used here."""
import hashlib
import json
import os
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
V3_DIR=Path(os.environ.get('TTM_T2_V3_DIR', str(Path.home()/'Downloads'/'TTM_T2_V3'))).resolve()
REPO=Path(os.environ.get('TTM_T2_QA_REPO','D:/WORK/RESEARCH/TokenToModel-Lab')).resolve()
sys.path.insert(0,str(V3_DIR))
from ttm_gpt2_bpe2048 import (train_only,synthetic_train_stories,Story,pretok,BPE2048,
                               EOS_ID,N_MERGES,VOCAB_SIZE,canonical_bytes,sha)
from t2_gguf_cpu import (load_model, parse_gguf)
from ttm_t2_f32_integrated import (export_f32_with_tokenizer,load_v3,
                         FROZEN_FIXTURE_SHA,SYNTHETIC_MANIFEST_SHA)

@pytest.fixture(scope='session')
def bpe():
    b=train_only(synthetic_train_stories(),'SYNTHETIC_TRAIN_FIXTURE')
    return b

@pytest.fixture(scope='session')
def fixtures():
    f=ROOT/'TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json'
    assert hashlib.sha256(f.read_bytes()).hexdigest()==FROZEN_FIXTURE_SHA
    return json.loads(f.read_text('utf-8'))


def test_frozen_fixtures_new_and_distinct(fixtures):
    assert len(fixtures['tokenizer_text_cases'])==20
    assert len(fixtures['numeric_id_cases'])==10
    assert len({c['id'] for c in fixtures['tokenizer_text_cases']})==20
    assert len({c['id'] for c in fixtures['numeric_id_cases']})==10
    from t2_llama_parity import FIXTURE_IDS, FIXTURE_TEXT
    assert not any(c['text'] in FIXTURE_TEXT for c in fixtures['tokenizer_text_cases'])
    assert not any(c['ids'] in FIXTURE_IDS for c in fixtures['numeric_id_cases'])
    assert fixtures['source_kind']=='SYNTHETIC_FIXTURE_ONLY'


def test_bpe_exact_vocabulary_and_manifest(bpe):
    assert len(bpe.tokens)==VOCAB_SIZE
    assert len(bpe.pairs)==N_MERGES
    assert bpe.tokens[EOS_ID]=='<|endoftext|>'
    assert bpe.manifest()['manifest_sha256']==SYNTHETIC_MANIFEST_SHA
    tokens,merges=bpe.gguf_token_merges()
    assert len(merges)==1791 and len(set(merges))==1791
    assert all(' ' in m for m in merges)


def test_manifest_tamper_rejected(bpe):
    man=bpe.manifest()
    restored=BPE2048.from_manifest(man)
    assert restored.encode('hello world')==bpe.encode('hello world')
    man['tokens'][0]='tampered'
    with pytest.raises(ValueError,match='TOKENIZER_MANIFEST_SHA_MISMATCH'):
        BPE2048.from_manifest(man)


def test_all_frozen_text_roundtrip(fixtures,bpe):
    for c in fixtures['tokenizer_text_cases']:
        assert ''.join(pretok(c['text']))==c['text']
        assert bpe.decode(bpe.encode(c['text']))==c['text']
        assert all(0<=x<2048 for x in bpe.encode(c['text']))


def test_reject_val_and_test_without_costly_train():
    base=synthetic_train_stories()
    for split in ('TEST','VAL'):
        row=base[0]
        bad=[Story(row.story_id,row.text,split,row.source)] + base[1:]
        with pytest.raises(ValueError,match='TRAIN_ONLY_GATE_REJECTED_VAL_TEST'):
            train_only(bad,'SYNTHETIC_TRAIN_FIXTURE')


def test_reject_wrong_split_source():
    row=synthetic_train_stories()[0]
    bad=[Story(row.story_id,row.text,'TRAIN','TinyStories-valid.txt')]
    with pytest.raises(ValueError,match='TRAIN_ONLY_SOURCE_BOUNDARY_VIOLATION'):
        train_only(bad,'SYNTHETIC_TRAIN_FIXTURE')


def test_reject_duplicate_story():
    row=synthetic_train_stories()[0]
    with pytest.raises(ValueError,match='MISSING_OR_DUPLICATE_STORIES'):
        train_only([row,row],'SYNTHETIC_TRAIN_FIXTURE')


def test_reject_unknown_token_and_eos(bpe):
    with pytest.raises(ValueError,match='TOKEN_ID_OUT_OF_RANGE'):
        bpe.decode([2048])
    with pytest.raises(ValueError,match='EOS_IN_TEXT_DECODE'):
        bpe.decode([EOS_ID])


def test_reject_wrong_source_kind():
    with pytest.raises(ValueError,match='SOURCE_KIND_NOT_AUTHORIZED'):
        train_only(synthetic_train_stories(),'VALID_DATASET')


def test_bpe_export_roundtrip_p02_f32(bpe,tmp_path):
    v3=load_v3(V3_DIR/'t2_gguf_cpu.py')
    repo=REPO
    model=load_model(repo)
    target=tmp_path/'f32_new_bpe.gguf'
    record=export_f32_with_tokenizer(target,model,bpe,v3)
    assert record['max_abs_weight_error']==0
    assert record['tensor_count']==52
    assert record['size_bytes']>14_000_000
    meta,weights,_=parse_gguf(target)
    assert meta['tokenizer.ggml.pre']=='gpt-2'
    assert meta['tokenizer.ggml.tokens']==list(bpe.tokens)
    with pytest.raises(FileExistsError):
        export_f32_with_tokenizer(target,model,bpe,v3)


def test_no_live_science_or_real_data():
    script=(ROOT/'ttm_t2_f32_integrated.py').read_text('utf-8')
    assert 'PINNED_TINYSTORIES_TRAIN' not in script
    assert "'SYNTHETIC_TRAIN_FIXTURE_ONLY_NOT_TINYSTORIES'" in script
    assert "DIRECTORY_NAME='f32_pretok_trainonly_v1'" in script
