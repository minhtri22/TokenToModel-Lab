# TTM D1 — one targeted Qwen tokenizer/teacher-forcing completion; NO downloads, NO science.
# Use AFTER the consumed V3 result, in the SAME Colab runtime when possible.
import os, sys, pathlib, json, hashlib, datetime, importlib.metadata, time
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

V3_RUN='ttm_embedgemma2_d1_t4_preflight_st610_once_v1'
FOLLOWUP_RUN='ttm_embedgemma2_d1_t4_qwen_tokenizer_followup_once_v1'
QWEN_SHA='7ae557604adf67be50417f59c2c2f167def9a775'
V3_CLAIM_SHA='2ce14ab0c890a53042862c2b376ab12e2927c15ae1c1d1d3e9075f386b4a5999'
V3_RESULT_SHA='ce693326af246fdf2a3806427b46d89ce05e944a4c99e442b24004677e892427'
DRIVE=pathlib.Path('/content/drive/MyDrive/TTM_EmbeddingGemma2_D1_Preflight')
WORK=pathlib.Path('/content/ttm_embeddinggemma2_d1_preflight_st610_v1')
CLAIM=DRIVE/(FOLLOWUP_RUN+'_CLAIM.json')
RESULT=DRIVE/(FOLLOWUP_RUN+'_RESULT.json')

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda:fh.read(1048576),b''):
            h.update(block)
    return h.hexdigest()

# Before CLAIM: require the immutable V3 failure and all previously PASSED stages.
if not sys.platform.startswith('linux') or not pathlib.Path('/content').exists():
    raise RuntimeError('Require same Google Colab Linux, no alternative compute')
try:
    import google.colab
except ImportError as exc:
    raise RuntimeError('Require Google Colab runtime') from exc
if not DRIVE.is_dir():
    raise RuntimeError('Mount the EXISTING Google Drive first. No new claim made')
for suffix,expected in [('CLAIM',V3_CLAIM_SHA),('RESULT',V3_RESULT_SHA)]:
    p=DRIVE/(V3_RUN+'_'+suffix+'.json')
    if not p.is_file() or sha256(p)!=expected:
        raise RuntimeError('V3 '+suffix+' original receipt missing/changed. STOP, no claim')
prior=json.loads((DRIVE/(V3_RUN+'_RESULT.json')).read_text(encoding='utf-8'))
required={'squad_exact_digest','model_file_sha256_calculated_local_not_remote_attested',
          'squad_shape_and_selection','embedding_fp32_sanity','colab_tesla_t4'}
passed={s['step'] for s in prior.get('steps',[]) if s.get('status')=='PASS'}
assert prior['run_id']==V3_RUN and prior['status']=='FAIL_OR_BLOCKED_NO_SCIENCE'
assert prior['error']['message']=='qwen_tokenizer_ids: FAIL: invalid tokenization'
assert required.issubset(passed) and prior.get('science_executed') is False
assert prior.get('embedding_smoke',{}).get('shape')==[2,768]
assert prior.get('embedding_smoke',{}).get('finite') is True
assert importlib.metadata.version('transformers')=='5.22.1'
assert torch.cuda.is_available() and 'T4' in torch.cuda.get_device_name(0)
if CLAIM.exists() or RESULT.exists():
    raise FileExistsError('Follow-up CLAIM/RESULT already exists: never rerun or overwrite')

# Existing V3 Qwen snapshot, or its currently loaded model; no network and no new weights.
SNAP=WORK/'hf_cache'/'models--Qwen--Qwen2.5-0.5B-Instruct'/'snapshots'/QWEN_SHA
if not SNAP.is_dir():
    raise FileNotFoundError('Existing pinned Qwen snapshot absent; STOP before CLAIM, do not download')
qmeta=next(x for x in prior['downloaded_file_manifests']
           if x['repo']=='Qwen/Qwen2.5-0.5B-Instruct' and x['revision']==QWEN_SHA)
for fname in ('model.safetensors','tokenizer.json','tokenizer_config.json','config.json'):
    source=next(x for x in qmeta['files'] if x['name']==fname)
    p=SNAP/fname
    if not p.is_file() or p.stat().st_size!=source['bytes'] or sha256(p)!=source['sha256']:
        raise RuntimeError('Qwen source SHA mismatch for '+fname+'; STOP before CLAIM')

# v5 change: apply_chat_template returns BatchEncoding by default, not list.
qtoken=globals().get('tokenizer')
if qtoken is None or getattr(qtoken,'name_or_path',None)!=str(SNAP):
    qtoken=AutoTokenizer.from_pretrained(str(SNAP),local_files_only=True)
messages=[{'role':'user','content':'Synthetic protocol check: the dummy code is silver. Give its color.'}]
prefix_ids=qtoken.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=False)
answer_ids=qtoken.encode('silver',add_special_tokens=False)
packed=qtoken.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,return_dict=True)
assert isinstance(prefix_ids,list) and len(prefix_ids)>0
assert isinstance(answer_ids,list) and len(answer_ids)>0
assert all(isinstance(t,int) and 0<=t<qtoken.vocab_size for t in prefix_ids+answer_ids)
assert list(packed['input_ids'])==prefix_ids  # consistent v5 dict/list interface
print('TTM_QWEN_TOKENIZER_PRECLAIM=PASS', 'prefix',len(prefix_ids),'answer',len(answer_ids))

start=time.monotonic()
stamp=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt={'schema':'ttm.embeddinggemma2.d1.t4.qwen_targeted_followup.v1',
         'run_id':FOLLOWUP_RUN,'parent_run_id':V3_RUN,'parent_result_sha256':V3_RESULT_SHA,
         'model_revision':QWEN_SHA,'created_utc':stamp(),'status':'STARTED',
         'scope':'synthetic Qwen tokenizer and teacher-forcing only; no dataset/model download',
         'science_executed':False,'rgold_read':False,'test_scored':False,
         'model_download':False,'adapter_training':False,
         'steps':[{'step':'preclaim_v3_receipts_source_tokenizer','status':'PASS'}]}
# Only now create a unique one-shot marker. This never changes V1 or V3 receipts.
fd=os.open(str(CLAIM),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w',encoding='utf-8') as f:
    json.dump({'run_id':FOLLOWUP_RUN,'parent_run':V3_RUN,'utc':stamp(),'scope':'no science'},f)
    f.flush();os.fsync(f.fileno())
try:
    qmodel=globals().get('model')
    if qmodel is None or getattr(qmodel.config,'model_type',None)!='qwen2':
        qmodel=AutoModelForCausalLM.from_pretrained(str(SNAP),local_files_only=True,dtype=torch.float16).to('cuda').eval()
    qmodel.eval()
    for p in qmodel.parameters(): p.requires_grad_(False)
    token_ids=prefix_ids+answer_ids
    ids=torch.tensor([token_ids],device='cuda',dtype=torch.long)
    labels=ids.clone();labels[:,:len(prefix_ids)]=-100
    with torch.inference_mode():
        logits=qmodel(input_ids=ids).logits
        nll=torch.nn.functional.cross_entropy(logits[:,:-1,:].float().reshape(-1,logits.shape[-1]),
                 labels[:,1:].reshape(-1),ignore_index=-100)
    scored=int((labels[:,1:]!=-100).sum().item())
    ok=bool(torch.isfinite(nll).item()) and scored==len(answer_ids)
    receipt['qwen']={'prefix_tokens':len(prefix_ids),'answer_tokens':len(answer_ids),
                     'scored_labels':scored,'synthetic_answer_only_nll':float(nll.item()),
                     'finite':bool(torch.isfinite(nll).item()),
                     'gpu':torch.cuda.get_device_name(0),
                     'transformers_version':importlib.metadata.version('transformers'),
                     'max_gpu_allocated_bytes':int(torch.cuda.max_memory_allocated())}
    if not ok: raise AssertionError('Qwen NLL or answer-only mask invalid')
    receipt['steps'].append({'step':'qwen_teacher_forcing_sanity','status':'PASS'})
    receipt['status']='PASS_TARGETED_QWEN_TECHNICAL_ONLY_NO_SCIENCE'
except BaseException as exc:
    receipt['status']='FAIL_TARGETED_QWEN_NO_SCIENCE'
    receipt['error']={'type':type(exc).__name__,'message':str(exc)[:500]}
finally:
    receipt['ended_utc']=stamp()
    receipt['elapsed_seconds']=round(time.monotonic()-start,3)
    # Exclusive RESULT creation: no prior output is overwritten.
    with RESULT.open('x',encoding='utf-8') as f:
        json.dump(receipt,f,indent=2,ensure_ascii=False)
        f.write('\n')
    print('TTM_QWEN_FOLLOWUP_STATUS='+receipt['status'])
    print('TTM_QWEN_FOLLOWUP_RESULT='+str(RESULT))