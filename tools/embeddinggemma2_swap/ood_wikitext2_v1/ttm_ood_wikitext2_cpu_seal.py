#!/usr/bin/env python3
"""WikiText-2 raw OOD256 source admission, T1 frozen tokenizer, private seal. CPU ONLY.
Never loads models, computes logits/NLL, changes lineage or writes outside TTM root.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, sys, urllib.request
from pathlib import Path
from statistics import median

REV='6231e49f19a707241d6b84d9cff60a3a86b85a85'
URL='https://huggingface.co/datasets/Salesforce/wikitext/resolve/'+REV+'/wikitext-2-raw-v1/train-00000-of-00001.parquet'
WIKI_SHA='49280f3dd993cbdfd322186194133d5d1935f81e1c91064c239f2a70ebb02701'
BPE_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
BPE_BLOB='fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
SPLIT_SHA='9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
TRAIN_SHA='c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f'
VALID_SHA='94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'
H320_SHA='bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47'
H512_SHA='544c30b470f5e8718ba35fe016b0f52cac95e559020eae2806e1ff7291a03661'
H768_SHA='0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f'
DOMAIN=b'TTM_GEMMA2_OOD_WIKITEXT2_RAW_DOCS_V1_20261111\0'
OP='TTM_GEMMA2_OOD_WIKITEXT2_PINNED_CORPUS_T1_BPE_CPU_FEASIBILITY_AND_PRIVATE_MEMBERSHIP_SEAL'
SUBDIR='_tmp/ttm_gemma2_ood_wikitext2_cpu_v1_20261111'
EOS=b'<|endoftext|>'

def fail(code): raise RuntimeError('HOLD_'+code)
def insist(ok,code):
    if not ok: fail(code)
def sha(b): return hashlib.sha256(b).hexdigest()
def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()
def gitblob(path):
    b=path.read_bytes(); return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def jbytes(obj):return (json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
def load_json(path,pin):
    insist(path.is_file() and not path.is_symlink(),'MISSING_PRIVATE_SOURCE_'+path.name)
    insist(file_sha(path)==pin,'PRIVATE_SOURCE_SHA_'+path.name)
    return json.loads(path.read_text(encoding='utf-8'))
def safe_root(root):
    root=Path(root).resolve(strict=True)
    insist(root.is_dir() and (root/'.git').exists() and root.name.casefold()=='tokentomodel-lab','ROOT_BAD')
    if os.name=='nt': insist(str(root).casefold()==r'd:\work\research\tokentomodel-lab','WINDOWS_ROOT_BAD')
    return root

def top_title(line):
    # WikiText-2 level-1 title: ' = Some Title = ', NOT '= = Section = ='.
    m=re.fullmatch(r'=\s+([^=\n]+?)\s+=',line.strip())
    return m.group(1).strip() if m else None

def section_heading(line):
    s=line.strip()
    return bool(s.startswith('=') and s.endswith('=') and re.fullmatch(r'(?:=\s*){1,5}[^=\n]+?(?:\s*=){1,5}',s))

def parse_articles(lines):
    docs=[];content=None;title_count=0
    for row in lines:
        insist(isinstance(row,str),'NON_STRING_ROW')
        # Parquet text rows correspond to lines; preserve spaces, normalize CR/LF only.
        s=row.rstrip('\r\n')
        insist('\x00' not in s,'NUL_TEXT')
        title=top_title(s)
        if title is not None:
            if content is not None: docs.append('\n'.join(content).strip('\n'))
            content=[];title_count+=1
            continue
        if content is None:
            insist(not s.strip(),'TEXT_BEFORE_FIRST_TITLE')
            continue
        if section_heading(s): continue
        content.append(s)
    if content is not None:docs.append('\n'.join(content).strip('\n'))
    insist(580<=title_count<=650 and len(docs)==title_count,'ARTICLE_COUNT_OUT_OF_EXPECTED_600_RANGE')
    insist(all(len(d.encode('utf-8'))>0 for d in docs),'EMPTY_ARTICLE')
    return docs

def word5(text):
    words=text.casefold().split()
    return frozenset(tuple(words[i:i+5]) for i in range(len(words)-4))
def near(a,b):
    if not a or not b:return False
    aa,bb=len(a),len(b)
    if min(aa,bb)<.85*max(aa,bb):return False
    hits=len(a.intersection(b));return hits/(aa+bb-hits)>=.85

def story_iter(path,chunk_size=1<<20):
    buf=b''
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(chunk_size),b''):
            buf+=chunk
            while True:
                at=buf.find(EOS)
                if at<0:break
                raw=buf[:at].strip(b' \t\r\n');buf=buf[at+len(EOS):]
                if raw: yield raw
            insist(len(buf)<(1<<23),'STORY_TOO_LARGE')
    raw=buf.strip(b' \t\r\n')
    if raw: yield raw

def obtain_parquet(out):
    target=out/'wikitext2_raw_train_pinned.parquet';partial=target.with_suffix('.parquet.partial')
    if target.is_file():
        insist(file_sha(target)==WIKI_SHA,'PARQUET_EXISTING_SHA_DRIFT');return target
    insist(not target.exists() and not partial.exists(),'PARQUET_PARTIAL_OR_UNEXPECTED')
    req=urllib.request.Request(URL,headers={'User-Agent':'TTM-GEMMA2-OOD-source-audit/1.0'})
    with urllib.request.urlopen(req,timeout=120) as response,partial.open('xb') as f:
        insist(response.status==200,'DOWNLOAD_HTTP_STATUS')
        size=0
        while True:
            chunk=response.read(1<<20)
            if not chunk:break
            size+=len(chunk);insist(size<20_000_000,'PARQUET_DOWNLOAD_TOO_LARGE')
            f.write(chunk)
        f.flush();os.fsync(f.fileno())
    insist(file_sha(partial)==WIKI_SHA,'PARQUET_DOWNLOAD_SHA_MISMATCH');os.replace(partial,target)
    return target

def load_private_members(root):
    tmp=root/'_tmp'
    split=load_json(tmp/'ttm_t1_real_source_v1/T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json',SPLIT_SHA)
    groups=split.get('splits',{});insist(set(['TRAIN','VAL','TEST']).issubset(groups),'T1_SPLIT_SCHEMA')
    insist([len(groups[n]) for n in ('TRAIN','VAL','TEST')]==[2048,256,64],'T1_SPLIT_LENGTHS')
    older=load_json(tmp/'ttm_gemma2_new_holdout_membership_v1_20261109/MEMBERSHIP_PRIVATE.json',H320_SHA)
    h512=load_json(tmp/'ttm_causal6_h512_seal_v1_20261109/H512_PRIVATE_MEMBERSHIP.json',H512_SHA)
    h768=load_json(tmp/'ttm_semantic4x3_h768_seal_v1_20261110/H768_MEMBERSHIP_PRIVATE.json',H768_SHA)
    def membership(x,expected):
        for key in ('story_sha256_ordered','story_sha256','selected_story_sha256','story_hashes'):
            if isinstance(x.get(key),list):
                vals=x[key];insist(len(vals)==expected and all(isinstance(h,str) and re.fullmatch(r'[0-9a-f]{64}',h) for h in vals),'HISTORICAL_HASH_SCHEMA');return vals
        fail('HISTORICAL_MEMBERSHIP_LAYOUT')
    old320=membership(older,320);old512=membership(h512,512);old768=membership(h768,768)
    histories=set(groups['TRAIN']+groups['VAL']+groups['TEST']+old320+old512+old768)
    return groups,histories

def historical_near(root,selected,groups):
    base=root/'datasets/tinystories_v1_original_pinned'
    train=base/'TinyStories-train.txt';valid=base/'TinyStories-valid.txt'
    insist(train.is_file() and valid.is_file(),'TINY_RAW_MISSING')
    # Both pinned, not any re-download. Checks all source bytes and scans selected source only.
    insist(file_sha(train)==TRAIN_SHA and file_sha(valid)==VALID_SHA,'TINY_RAW_SHA')
    tset=set(groups['TRAIN']);vset=set(groups['VAL']);refs=[];counts={}
    for name,p,needed in [('TRAIN',train,tset),('VAL',valid,vset)]:
        got={};n=0
        for raw in story_iter(p):
            n+=1;h=sha(raw)
            if h in needed and h not in got:
                got[h]=word5(raw.decode('utf-8','strict'))
        insist(set(got)==needed,'MISSING_ORIGINAL_'+name)
        counts[name]=n;refs.extend(got.values())
    insist(counts=={'TRAIN':2119489,'VAL':21990},'TINY_RAW_STORY_COUNTS')
    sels=[word5(d['text']) for d in selected]
    for i,s in enumerate(sels):
        for t in sels[:i]:insist(not near(s,t),'OOD_INTERNAL_NEAR_DUP')
        for t in refs:insist(not near(s,t),'OOD_TO_T1_TRAIN_VAL_NEAR_DUP')
    return counts

def execute(root):
    root=safe_root(root)
    out=root/SUBDIR;out.mkdir(parents=True,exist_ok=True)
    target=out/'OOD256_PRIVATE_MEMBERSHIP.json'
    insist(not target.exists() and not (out/'OOD256_PUBLIC_SEAL.json').exists() and not (out/'OOD256_PRIVATE_WINDOWS.npz').exists(),'ALREADY_SEALED_NO_OVERWRITE')
    source=root/'tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py'
    insist(source.is_file() and gitblob(source)==BPE_BLOB,'T1_BPE_SOURCE_BLOB')
    manifest=root/'_tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json'
    m=load_json(manifest,BPE_SHA)
    sys.path.insert(0,str(source.parent))
    from ttm_gpt2_bpe2048 import BPE2048
    tokenizer=BPE2048.from_manifest(m)
    groups,histories=load_private_members(root)
    parquet=obtain_parquet(out)
    try: import pyarrow.parquet as pq
    except ImportError:fail('PYARROW_REQUIRED_IN_PROJECT_ENV')
    table=pq.read_table(parquet,columns=['text'])
    insist(table.num_rows==36718 and table.column_names==['text'],'WIKITEXT_PARQUET_SCHEMA_OR_ROW_COUNT')
    docs=parse_articles(table.column('text').to_pylist())
    records=[]
    for i,text in enumerate(docs):
        original=text.encode('utf-8');h=sha(original)
        insist(h not in histories,'OOD_EXACT_OVERLAP_HISTORICAL')
        ids=tokenizer.encode(text)
        insist(tokenizer.decode(ids)==text,'BPE_ROUNDTRIP')
        insist(all(0<=v<2048 and v!=256 for v in ids),'BPE_ID_OUT_OF_RANGE')
        if len(ids)>=513:
            words=max(1,len(text.split()))
            rank=sha(DOMAIN+h.encode('ascii'))
            records.append({'ordinal':i,'sha256':h,'rank':rank,'tokens':len(ids),'words':words,'text':text,'ids513':ids[:513],'fragment':len(ids)/words})
    insist(len(records)>=256,'INSUFFICIENT_ELIGIBLE_ARTICLES')
    records.sort(key=lambda r:(r['rank'],r['sha256']))
    chosen=records[:256]
    insist(len(set(z['sha256'] for z in chosen))==256,'SELECTED_SHA_DUPLICATES')
    fragmentation=median(r['fragment'] for r in chosen)
    insist(fragmentation<=4.0,'BPE_FRAGMENT_MEDIAN_TOO_HIGH')
    counts=historical_near(root,chosen,groups)
    import numpy as np
    xs=[];ys=[]
    for r in chosen:
        ids=r['ids513'];insist(len(ids)==513,'BPE_513_EXPECTED')
        for offset in (0,256):xs.append(ids[offset:offset+256]);ys.append(ids[offset+1:offset+257])
    x=np.asarray(xs,dtype=np.int16);y=np.asarray(ys,dtype=np.int16)
    insist(x.shape==y.shape==(512,256) and int((x<0).sum())==0 and int((y<0).sum())==0,'WINDOWS_BAD')
    private={'schema':'ttm.gemma2.ood.wikitext2.private_membership.v1','operation':OP,
       'source_revision':REV,'parquet_sha256':WIKI_SHA,'t1_bpe_manifest_sha256':BPE_SHA,
       'source_articles':len(docs),'eligible_articles':len(records),
       'selection_domain_ascii_nul':DOMAIN.decode('ascii'),'selected_count':256,
       'scored_targets_per_document':512,'scored_targets_total':131072,
       'selected':[{'source_ordinal':r['ordinal'],'text_sha256':r['sha256'],'rank_sha256':r['rank'],
        'bpe_total_tokens':r['tokens'],'whitespace_words':r['words']} for r in chosen],
       'no_model_forward':True,'inference_executed':False,'training_executed':False}
    public={'schema':'ttm.gemma2.ood.wikitext2.public_seal.v1','status':'SEALED_SOURCE_ONLY_NOT_SCORED',
      'operation':OP,'source_revision':REV,'parquet_sha256':WIKI_SHA,'t1_bpe_manifest_sha256':BPE_SHA,
      'source_rows':table.num_rows,'source_articles':len(docs),'eligible_articles':len(records),
      'selected_articles':256,'selected_windows':512,'scored_targets_total':131072,
      'median_bpe_tokens_per_whitespace_word':fragmentation,'historic_source_counts':counts,
      'near_duplicate_selected_internal':0,'near_duplicate_to_T1_train2048_val256':0,
      'history_exact_intersection':0,'pretraining_overlap':'UNKNOWN','model_forward_calls':0,
      'science_executed':False,'GPU':False,'lineage_modified':False,
      'rights':'CC BY-SA / GFDL attribution and redistributive obligations preserved; private outputs not public'}
    # Only after every gate has succeeded, publish the three immutable private files.
    target.write_bytes(jbytes(private)) if not target.exists() else fail('OUTPUT_CONFLICT')
    pubpath=out/'OOD256_PUBLIC_SEAL.json';winpath=out/'OOD256_PRIVATE_WINDOWS.npz'
    with winpath.open('xb') as fd:
        np.savez_compressed(fd,x=x,y=y,story_index=np.repeat(np.arange(256,dtype=np.int32),2),
         count=np.full(512,256,dtype=np.int16))
        fd.flush();os.fsync(fd.fileno())
    public.update({'private_membership_sha256':file_sha(target),'private_windows_sha256':file_sha(winpath)})
    with pubpath.open('xb') as f:f.write(jbytes(public));f.flush();os.fsync(f.fileno())
    print('TTM_GEMMA2_OOD_SOURCE_SEAL=PASS_CPU_SOURCE_ONLY')
    print('TTM_GEMMA2_OOD_PUBLIC_SEAL='+str(pubpath))
    print('TTM_GEMMA2_OOD_PUBLIC_SHA256='+file_sha(pubpath))
    print('TTM_GEMMA2_OOD_256_DOCS=PASS; MODEL_FORWARD=0; GPU=0; SCIENCE=NOT_EXECUTED')

def fixture():
    a=' = First = \n';b=' = = Section = = \n'
    insist(top_title(a)=='First' and top_title(b) is None,'FIXTURE_TITLE')
    insist(section_heading(b),'FIXTURE_SUBHEADING')
    s1=word5('one two three four five six');s2=word5('one two three four five six')
    insist(near(s1,s2) and not near(s1,word5('another completely different five word example')),'FIXTURE_NEAR')
    insist(sha(DOMAIN+b'0'*64)!=sha(b'0'*64),'FIXTURE_RANK_DOMAIN')
    print('TTM_GEMMA2_OOD_CPU_FIXTURE=PASS_4; NO_DOWNLOAD_NO_MODEL')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['fixture','execute'],required=True)
    ap.add_argument('--repo',default='');a=ap.parse_args()
    try:
        if a.mode=='fixture':fixture()
        else:
            insist(bool(a.repo),'ROOT_REQUIRED');execute(a.repo)
    except Exception as ex:
        print('TTM_GEMMA2_OOD_STATUS=HOLD; REASON='+str(ex),file=sys.stderr)
        raise
