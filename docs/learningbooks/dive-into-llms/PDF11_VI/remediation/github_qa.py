#!/usr/bin/env python3
"""Separate checker of immutable input PDF pages and rewritten PDF candidates.

Does not use or import the writer. This is independent *code path*, not an
independent human or second language model evaluation.
"""
import argparse,collections,fitz,hashlib,json,re,unicodedata
from pathlib import Path

PIN='f84c04268794ef94f8949808bbc14ab8636763a0'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tokens(s):
 s=unicodedata.normalize('NFKC',s).lower()
 return collections.Counter(re.findall(r'[\w\u00c0-\u1ef9]+',s))

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--baseline',required=True)
 parser.add_argument('--output',required=True)
 parser.add_argument('--receipt',required=True)
 a=parser.parse_args();before=Path(a.baseline);out=Path(a.output)
 base=json.loads((out/'INTEGRATION_MANIFEST_20261116.json').read_text(encoding='utf-8'))
 rem=json.loads((out/'REMEDIATION_MANIFEST_20261116.json').read_text(encoding='utf-8'))
 assert base['source_commit']==PIN and rem['source_pin']==PIN and len(rem['output_files'])==11
 errors=[];bad_chars=[];bad_token=[];upper_text_diff=[];per=[];visual=[]
 for inp,fil in zip(base['files'],rem['output_files']):
  chapter=inp['chapter'];name=inp['bilingual_path'];notes=fil['md_path']
  if chapter!=fil['chapter']: errors.append('ORDER_CHAPTER_MISMATCH')
  if sha(before/name)!=inp['bilingual_sha256']: errors.append(f'BASE_PDF_HASH_{chapter}')
  if sha(before/notes)!=inp['notes_sha256']: errors.append(f'BASE_NOTES_HASH_{chapter}')
  if sha(out/name)!=fil['pdf_sha256']: errors.append(f'OUTPUT_PDF_HASH_{chapter}')
  if sha(out/notes)!=fil['md_sha256']: errors.append(f'OUTPUT_NOTES_HASH_{chapter}')
  old=fitz.open(before/name);new=fitz.open(out/name)
  md=(out/notes).read_text(encoding='utf-8')
  if '\x14' in md:errors.append(f'UNPRINTABLE_IN_NOTES_{chapter}')
  heads=list(re.finditer(r'(?m)^## Trang (\d+)/(\d+)\s*\n',md))
  if len(heads)!=fil['pages']:errors.append(f'NOTES_PAGE_COUNT_{chapter}')
  entries={}
  for i,m in enumerate(heads):entries[int(m.group(1))]=md[m.end():(heads[i+1].start() if i+1<len(heads) else len(md))]
  if len(old)!=len(new) or len(old)!=fil['pages']:errors.append(f'PAGE_COUNT_{chapter}')
  matches=0
  for i in range(min(len(old),len(new))):
   p=new[i];q=old[i];clip=fitz.Rect(0,0,1280,752)
   if q.get_text(clip=clip)!=p.get_text(clip=clip):upper_text_diff.append([chapter,i+1])
   if i in {0,len(old)//2,len(old)-1}:
    a1=q.get_pixmap(matrix=fitz.Matrix(.5,.5),clip=clip,alpha=False).samples
    a2=p.get_pixmap(matrix=fitz.Matrix(.5,.5),clip=clip,alpha=False).samples
    if len(a1)!=len(a2):errors.append(f'RENDER_SIZE_{chapter}:{i+1}')
    else:
     mae=sum(abs(x-y) for x,y in zip(a1,a2))/len(a1)
     visual.append([chapter,i+1,round(mae,4)])
     if mae>0.22:errors.append(f'ORIGINAL_SLIDE_CHANGED_{chapter}:{i+1}')
   text=p.get_text()
   if 'NỘI DUNG TIẾNG VIỆT' not in text or PIN not in text:errors.append(f'PIN_OR_LABEL_{chapter}:{i+1}')
   vi=text.split('NỘI DUNG TIẾNG VIỆT',1)[-1]
   controls=sorted({ord(c) for c in vi if unicodedata.category(c)=='Cc' and c not in '\n\r\t'})
   if controls or '\ufffd' in vi:bad_chars.append([chapter,i+1,controls])
   matched=sum((tokens(entries.get(i+1,''))&tokens(vi)).values())
   total=sum(tokens(entries.get(i+1,'')).values())
   if total and matched/total<.98:bad_token.append([chapter,i+1,round(matched/total,3)])
   if (chapter,i+1)==(2,47) and not all(t in vi for t in ('→','90','54')):errors.append('COT_MISSING_SYMBOLS')
   if (chapter,i+1)==(4,14) and '####' not in vi:errors.append('GSM8K_MISSING_SYMBOLS')
   if (chapter,i+1)==(11,17) and not {'θ','η','←','∇'}.issubset(set(vi)):errors.append('PG_MISSING_SYMBOLS')
   matches+=1
  per.append({'chapter':chapter,'pages':matches,'new_pdf_sha256':sha(out/name),'new_notes_sha256':sha(out/notes)})
  old.close();new.close()
 if upper_text_diff:errors.append('UPPER_TEXT_DRIFT')
 if bad_chars:errors.append('REPLACEMENT_OR_CONTROL_CHAR')
 if bad_token:errors.append('MARKDOWN_CONTENT_MISSING_IN_PDF')
 if sum(x['pages'] for x in per)!=495:errors.append('NOT_495_PAGES')
 result={'operation':'DIVE_INTO_LLMS_11PDF_VI_FIDELITY_REMEDIATION_AND_INDEPENDENT_LANGUAGE_QA_ONEPACK',
   'qa_scope':'INDEPENDENT_CODE_PATH_STATIC_ONLY_NOT_INDEPENDENT_LANGUAGE_REVIEW',
   'source_pin':PIN,'total_pages':sum(x['pages'] for x in per),
   'static_qa':'PASS' if not errors else 'FAIL',
   'slide_visual_samples':len(visual),'slide_visual_mae_max':max((v[2] for v in visual),default=0),
   'control_or_replacement_pages':bad_chars,'missing_note_text_pages':bad_token,
   'upper_source_text_differences':upper_text_diff,
   'documents':per,'errors':errors,'translation_fidelity':'HOLD_NOT_FULL_LITERAL',
   'independent_human_linguistic_qa':'NOT_EXECUTED',
   'science_execution':False}
 path=Path(a.receipt);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'static_qa':result['static_qa'],'pages':result['total_pages'],'errors':errors,'controls':len(bad_chars),'token_drift':len(bad_token)}))
 if errors:raise SystemExit(1)

if __name__=='__main__':main()
