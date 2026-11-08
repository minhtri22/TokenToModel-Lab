"""Deterministic notebook generator. No runtime execution or secrets."""
from pathlib import Path
import json,base64,hashlib
ROOT=Path(__file__).parent
intro='''# TTM T3 — Colab/Google Drive checkpoint/resume, 100% synthetic

**Không tải TinyStories, không huấn luyện khoa học.** Notebook ghi checkpoint PyTorch đầy đủ lên Google Drive: model/optimizer/scheduler/RNG/cursor. So sánh 20 bước liên tục với 10 bước + lưu + đọc lại từ Drive + 10 bước, dùng đúng mã P02 đã khóa. **T4 khoa học chưa được cấp phép.**

Chạy từng ô một. Notebook chỉ dùng GPU nếu Colab cấp CUDA và sẽ từ chối chạy âm thầm trên CPU. Không chạy lại cùng run ID sau lỗi. Cuối cùng phải flush/unmount Drive và kiểm chứng file trên Drive độc lập.
'''
preamble="import os, sys, base64, hashlib, pathlib, subprocess, json\nos.environ['CUBLAS_WORKSPACE_CONFIG'] = ':4096:8'\nROOT=pathlib.Path('/content/ttm_t3_frozen')\nROOT.mkdir(parents=True,exist_ok=True)\n"
for name in ['p02_source_exact.py','t3_resume_smoke.py']:
    data=(ROOT/name).read_bytes()
    raw=base64.b64encode(data).decode('ascii')
    digest=hashlib.sha256(data).hexdigest()
    preamble+=f"raw=base64.b64decode('{raw}')\n"
    preamble+=f"assert hashlib.sha256(raw).hexdigest()=='{digest}', 'EMBEDDED_SOURCE_SHA_MISMATCH:{name}'\n"
    preamble+=f"p=ROOT/'{name}'\n"
    preamble+=f"if p.exists() and p.read_bytes()!=raw: raise RuntimeError('SOURCE_CHANGED:{name}')\n"
    preamble+="p.write_bytes(raw)\n"
preamble+="print('TTM_T3_NOTEBOOK_SOURCE_READBACK=PASS')\n"
mount='''from google.colab import drive
drive.mount('/content/drive')
from pathlib import Path
DRIVE_ROOT=Path('/content/drive/MyDrive/TTM/ttm-small-pilot')
assert Path('/content/drive/MyDrive').is_dir(), 'GOOGLE_DRIVE_MOUNT_NOT_READY'
DRIVE_ROOT.mkdir(parents=True, exist_ok=True)
RUN_ID='t3_resume_synthetic_20261108_v1'
assert not (DRIVE_ROOT/RUN_ID).exists(), 'T3_RUN_ID_CONSUMED_NO_RERUN'
print('TTM_T3_COLAB_DRIVE_MOUNT=PASS')
'''
execute='''import torch, sys, subprocess, json, os, hashlib, platform
if not torch.cuda.is_available():
    raise RuntimeError('COLAB_CUDA_GPU_NOT_ALLOCATED; T3 Colab GPU test cannot silently use CPU')
print('TTM_T3_GPU='+torch.cuda.get_device_name(0))
print('TTM_T3_TORCH='+str(torch.__version__))
run=subprocess.run([sys.executable,str(ROOT/'t3_resume_smoke.py'),
 '--p02',str(ROOT/'p02_source_exact.py'), '--drive-root',str(DRIVE_ROOT),
 '--run-id',RUN_ID,'--device','cuda'],capture_output=True,text=True,timeout=600)
print(run.stdout)
if run.stderr: print(run.stderr[-4000:])
if run.returncode:raise RuntimeError('TTM_T3_COLAB_RESUME_FAIL:'+str(run.returncode))
report_path=DRIVE_ROOT/RUN_ID/'T3_RESUME_REPORT.json'
report=json.loads(report_path.read_text('utf8'))
assert report['pass'] and report['device'].startswith('cuda'), 'BAD_COLAB_T3_REPORT'
freeze=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)
freeze_file=DRIVE_ROOT/RUN_ID/'COLAB_PIP_FREEZE.txt'
assert not freeze_file.exists()
freeze_file.write_text(freeze,encoding='utf8')
env={'schema':'ttm.t3.colab.env.v1','python':sys.version,'platform':platform.platform(),
 'torch':str(torch.__version__),'cuda':str(torch.version.cuda),
 'gpu_name':torch.cuda.get_device_name(0),
 'pip_freeze_sha256':hashlib.sha256(freeze.encode()).hexdigest(),
 'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest(),
 'science_executed':False}
(DRIVE_ROOT/RUN_ID/'COLAB_ENVIRONMENT.json').write_text(json.dumps(env,indent=2,sort_keys=True)+'\\n',encoding='utf8')
print('TTM_T3_COLAB_MOUNTED_DRIVE_RESUME=PASS; NEED_FLUSH_AND_EXTERNAL_READBACK')
print('TTM_T3_REPORT_SHA256='+env['report_sha256'])
'''
final='''from google.colab import drive
# Flush/unmount only when all preceding cells PASS. This is not a network-independent
# durability guarantee: check files through Google Drive after it finishes.
drive.flush_and_unmount()
print('TTM_T3_COLAB_DRIVE_FLUSH=COMPLETED; INDEPENDENT_DRIVE_READBACK_STILL_REQUIRED')
'''
nb={'cells':[], 'metadata':{'colab':{'name':'TTM_T3_Colab_Drive_Resume_Synthetic_20261108.ipynb','provenance':[]},'kernelspec':{'display_name':'Python 3','name':'python3'},'language_info':{'name':'python'}},'nbformat':4,'nbformat_minor':5}
for text,kind in [(intro,'markdown'),(preamble,'code'),(mount,'code'),(execute,'code'),(final,'code')]:
    cell={'cell_type':kind,'metadata':{},'source':text.splitlines(keepends=True)}
    if kind=='code':cell.update({'execution_count':None,'outputs':[]});compile(text,str(ROOT/'COLAB'), 'exec')
    nb['cells'].append(cell)
out=ROOT/'TTM_T3_Colab_Drive_Resume_Synthetic_20261108.ipynb'
out.write_text(json.dumps(nb,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('NOTEBOOK_SOURCE_SYNTAX=PASS',len(nb['cells']),'cells',hashlib.sha256(out.read_bytes()).hexdigest())
