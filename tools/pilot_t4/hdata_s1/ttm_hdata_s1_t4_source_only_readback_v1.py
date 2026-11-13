#!/usr/bin/env python3
"""Owner Colab T4 *preexec only*: verify source+data pins, metadata sampler, DEV BPE, immutable parent.
Zero model construction, model.forward, loss backward, optimizer steps, inference and FINAL text read.
Use owner-mounted files; this never grants training permission.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,pathlib,torch,sys
PACK='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
BPE='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
PARENT='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
DEV='60e514a2329abe6b6df673058ee7656bb57287758c6ee4cc861a396a1788ba3d'
EXPECTED_PLAN='bcb354d29540e3a348b76173cdad1a6e2832dc81f995c717b68be6926d456591'

def sha(path):
    with open(path,'rb') as f:
        h=hashlib.sha256()
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        return h.hexdigest()

def require(b,n):
    if not b:raise RuntimeError('HDATA_T4_SOURCE_HOLD:'+n)

def import_pinned(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser()
    for p in ('pack','manifest','parent','science_lock','bpe','dev','sampler_script','bpe_script','out'):ap.add_argument('--'+p.replace('_','-'),required=True)
    a=ap.parse_args()
    require(torch.cuda.is_available(),'CUDA_NOT_AVAILABLE')
    props=torch.cuda.get_device_properties(0)
    require('T4' in props.name and props.total_memory>=14*1024**3,'EXPECTED_TESLA_T4')
    require(str(torch.__version__).startswith('2.14.1+cu130'),'FROZEN_TORCH_VERSION_DRIFT')
    require(sha(a.pack)==PACK,'PACK_SHA')
    require(sha(a.bpe)==BPE,'BPE_SHA')
    require(sha(a.parent)==PARENT,'PARENT_SHA')
    require(sha(a.dev)==DEV,'DEV_SHA')
    require(not pathlib.Path(a.out).exists(),'RECEIPT_ALREADY_EXISTS')
    s=import_pinned('ttm_hdata_sampler_preexec',a.sampler_script)
    b=import_pinned('ttm_hdata_bpe_preexec',a.bpe_script)
    require(s.PACK_SHA==PACK and s.PARENT_SHA==PARENT,'SAMPLER_CODE_CONTRACT')
    require(b.BPE_SHA==BPE and b.PARENT_SHA==PARENT,'BPE_CODE_CONTRACT')
    import tempfile
    with tempfile.TemporaryDirectory(prefix='ttm_hdata_preexec_no_train_') as root:
        temp=pathlib.Path(root)
        s.main(['--pack',a.pack,'--manifest',a.manifest,'--parent',a.parent,
                '--science-lock',a.science_lock,'--output',str(temp/'sampler.json')])
        # b.main() accepts normal process CLI; run via temporarily scoped sys.argv.
        old=sys.argv
        try:
            sys.argv=['ttm_hdata_bpe', '--manifest',a.bpe,'--dev',a.dev,'--parent',a.parent,'--output',str(temp/'bpe.json')]
            b.main()
        finally:sys.argv=old
        sampler=json.loads((temp/'sampler.json').read_bytes())
        bj=json.loads((temp/'bpe.json').read_bytes())
        require(sampler['paired_schedule_digest']==EXPECTED_PLAN,'CPU_T4_SAMPLER_SCHEDULE_DRIFT')
        require(sampler['metadata_pause_resume_64_64']=='PASS_EXACT','SAMPLER_RESUME')
        require(all(sampler['thresholds'].values()),'REAL_TRAIN_MANIPULATION')
        require(bj['bpe_roundtrip_pass']==12,'BPE_ROUNDTRIP')
    result={'schema':'ttm.hdata_s1.owner_colab_t4.source_only_preexec_receipt.v1',
       'runtime_torch':str(torch.__version__),'gpu':props.name,'gpu_memory_bytes':props.total_memory,
       'source_pins':{'train_pack_sha256':PACK,'bpe_sha256':BPE,'parent_sha256':PARENT,'dev_sha256':DEV,
          'sampler_source_sha256':sha(a.sampler_script),'bpe_checker_sha256':sha(a.bpe_script)},
       'cpu_metadata_schedule_sha256':EXPECTED_PLAN,
       'real_sampler_budget':'128_steps_4096_labels_2928_windows_each',
       'real_sampler_coverage_early_gates':'PASS',
       'bpe_roundtrip_DEV':'PASS_12_OF_12',
       'sampler_resume_metadata':'PASS_64_PLUS_64',
       'training_resume_dynamic':'NOT_EXECUTED',
       'rights_scope_owner':'NOT_GRANTED_HDATA_S1',
       'model_forward':0,'optimizer_steps':0,'final_prompt_access':False,
       'release':'HOLD_OWNER_RIGHTS_AND_REAL_TRAINER_RESUME'}
    pathlib.Path(a.out).parent.mkdir(parents=True,exist_ok=True)
    with open(a.out,'x',encoding='utf8') as out:json.dump(result,out,ensure_ascii=False,sort_keys=True,indent=2);out.write('\n')
    print('HDATA_S1_T4_PREEXEC_SOURCE_PIN=PASS')
    print('HDATA_S1_RECEIPT_SHA256='+sha(a.out))
    print('HDATA_S1_MODEL_FORWARD=0')
    print('HDATA_S1_TRAIN=0')
    print('HDATA_S1_RELEASE=HOLD_OWNER_RIGHTS_AND_REAL_TRAINER_RESUME')

if __name__=='__main__':main()
