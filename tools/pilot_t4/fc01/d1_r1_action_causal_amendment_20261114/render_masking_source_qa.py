#!/usr/bin/env python3
"""SOURCE ONLY preview renderer and cue masking self-audit (never emits dataset).
Do NOT equate this with tokenizer-verified final T1 parser or EVAL prompt renderer.
"""
import json,argparse,re
from pathlib import Path
FORBIDDEN=('split_design','structure_index','skeleton_id','mechanism_hypothesis','source_amendment_status',
           'TRAIN_DESIGN','STRUCTURAL_OOD_DESIGN','TR01','TR02','TR03','TR04','OD01','OD02','OD03','OD04',
           'oracle','gold','answer_key')

def preview(bp,side):
 s=bp['world_'+side];g=bp['task']['goal'];category=bp['task']['task_kind']
 # Always render the same typed fluents in same sorted order, neither split markers
 # nor public AST names/IDs; a future science renderer will need additional QA.
 lines=[f'Task kind: {category.replace("_"," ")}.',
        'Actor: a0. Reason from the following complete state facts and task goal.',
        'State:']
 for field in sorted(s):
  val=s[field]
  if isinstance(val,dict):
   for k in sorted(val):lines.append(f'{field}.{k}={json.dumps(val[k],ensure_ascii=False)}')
  else:lines.append(f'{field}={json.dumps(val,ensure_ascii=False)}')
 lines.append('Goal: '+json.dumps(g,ensure_ascii=False,sort_keys=True))
 lines.append('Return one next action respecting the six typed verbs and temporal rules.')
 out='\n'.join(lines)
 for word in FORBIDDEN:
  if re.search(re.escape(word),out,re.I):raise ValueError('SPLIT_OR_GOLD_CUE:'+word)
 return out

def audit(data):
 prompts=[preview(s,side) for s in data['skeletons'] for side in ('A','B')]
 assert len(prompts)==64
 return {'rendered_public_preview_count_in_memory_only':len(prompts),
  'identifiers_split_labels_gold_cues':'NOT_PRESENT_IN_PREVIEW',
  'tokenizer_T1_max_length':'NOT_VERIFIED',
  'final_parser_source':'NOT_IMPLEMENTED',
  'science_prompt_release':'NOT_AUTHORIZED'}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('path');ns=ap.parse_args()
 d=json.loads(Path(ns.path).read_text(encoding='utf8'));print(json.dumps(audit(d),sort_keys=True))
