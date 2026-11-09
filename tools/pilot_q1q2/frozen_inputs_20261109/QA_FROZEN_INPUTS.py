#!/usr/bin/env python3
# Source-only fixture QA. Does not call Ollama or access TRAIN/VAL/TEST.
import json,hashlib,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'Q1Q2_LOCK_MANIFEST.json').read_text(encoding='utf-8'))
for fn,want in M['files_sha256'].items():
    assert hashlib.sha256((ROOT/fn).read_bytes()).hexdigest()==want, ('PIN_CHANGED',fn)
prompt=json.loads((ROOT/'Q1_ORIGINAL_PROMPTS.json').read_text(encoding='utf-8'))
config=json.loads((ROOT/'Q1Q2_FROZEN_CONFIG.json').read_text(encoding='utf-8'))
q1=json.loads((ROOT/'Q1_FROZEN_48_RUN_MATRIX.json').read_text(encoding='utf-8'))['rows']
q2=json.loads((ROOT/'Q2_FROZEN_24_MEASUREMENT_MATRIX.json').read_text(encoding='utf-8'))
p=prompt['items'];ids=[x['id'] for x in p]
assert len(p)==len(set(ids))==16
assert len({x['prompt'] for x in p})==16
assert collections.Counter(x['group'] for x in p)=={'everyday':8,'cause_effect':4,'consistency':4}
assert all(x['prompt'].isascii() and 15<=len(x['prompt'].split())<=60 for x in p)
assert len(q1)==48 and len({x['run_id'] for x in q1})==48
assert collections.Counter(x['condition'] for x in q1)=={'GREEDY':16,'SAMPLED':32}
assert all(x['prompt_id'] in ids and x['num_predict']==64 and x['num_ctx']==256 for x in q1)
assert all(x['temperature']==0 for x in q1 if x['condition']=='GREEDY')
assert all(x['temperature']==0.8 and x['top_p']==0.9 and x['seed'] in (101,102) for x in q1 if x['condition']=='SAMPLED')
assert len(q2['rows'])==24 and len(q2['warmups'])==2
assert len({x['run_id'] for x in q2['rows']})==24
assert set(x['num_ctx'] for x in q2['rows'])=={128,256}
assert all(x['num_predict']==32 and x['prompt_id'] in ids for x in q2['rows'])
assert all(x['run_id'] not in {r['run_id'] for r in q1} for x in q2['rows'])
assert config['q1']['total_generations']==48 and config['q2']['total_measured_generations']==24
assert config['model']['gguf_sha256']=='5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5'
assert 'NO_SEALED_TEST_NO_TRAIN' in config['preflight_requirements']
print('TTM_PR12_Q1Q2_STATIC_QA=PASS_ALL_ASSERTIONS')
print('Q1_FROZEN_48=PASS Q2_FROZEN_24=PASS WARMUPS=2')
print('NATIVE_OLLAMA=NOT_EXECUTED TEST_DATA=NOT_ACCESSED TRAINING=NOT_EXECUTED')
