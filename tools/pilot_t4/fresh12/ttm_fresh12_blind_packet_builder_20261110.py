#!/usr/bin/env python3
"""Prepare sealed 24-pair neutral-ID reviewer packet from existing 48, without new inference."""
import base64,csv,hashlib,hmac,json,os,re,sys,uuid,zlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
P=Path('/mnt/data/ttm_fresh12_executor_private');sys.path.insert(0,str(P))
from ttm_tokenizer_private import BPE2048
SHA=lambda b:hashlib.sha256(b).hexdigest()
sha_file=lambda p:SHA(Path(p).read_bytes())
def freeze(path,obj):
 with path.open('x',encoding='utf-8',newline='\n') as f:
  json.dump(obj,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
raw=json.load(open(P/'FRESH12_PRIVATE_RAW_48_UNADJUDICATED.json'))
assert raw['n_generations']==48 and raw['status']=='EXECUTED_48_UNADJUDICATED'
owner=json.load(open('/mnt/data/TTM_FRESH12_OWNER_PRIVATE_DECRYPTION_KEY_DO_NOT_GITHUB.json'))
key=bytes.fromhex(owner['key_hex']);assert len(key)==32
seed=AESGCM(key).decrypt(base64.b64decode('FJHA1Ku4+8oBMCgf'),base64.b64decode('caKCwszdf8TQwvLi3JP6Vb1nt8xFBxxxeIqn4whjbtz+r8O2T9ntjS27w9W5JNuZ'),b'TTM_SMALL4M_FRESH12_A_B_ALLOCATION_SEED_V1')
assert SHA(seed)=='5efcfa520f604d21d96fb62d27987003c21fe991c51d5974cd6ff24a64ddc4c4'
prompts=json.load(open(P/'prompts.json')); ids=[x['id'] for x in prompts];by_id={x['id']:x['text'] for x in prompts}
rank=sorted(ids,key=lambda i:hmac.new(seed,b'BALANCE:'+i.encode(),hashlib.sha256).digest())
trim_A_1024=set(rank[:6]);assert len(trim_A_1024)==6
rec={(r['prompt_id'],r['checkpoint_step'],r['condition']):r for r in raw['results']}
assert len(rec)==48
bpe=BPE2048(P/'bpe_pairs.b64')
for r in raw['results']:
 assert r['prompt_clean']==by_id[r['prompt_id']]
 clean=r['condition']=='TRIMMED_NO_TRAILING_ASCII_SPACE'
 assert r['prompt_token_ids']==bpe.encode(r['prompt_clean']+('' if clean else ' '))
 assert r['generated_token_count']==len(r['generated_token_ids'])<=64
 assert all(x!=256 and 0<=x<2048 for x in r['generated_token_ids'])
 assert bpe.decode(r['generated_token_ids'])==r['generated_text']
 assert SHA(r['generated_text'].encode())==r['generated_text_sha256']
 assert r['seed']==20261109+int(r['prompt_id'][1:])
 assert r['decoder']=='greedy_argmax'
 if r['stop_reason']=='length':assert len(r['generated_token_ids'])==64
 else:assert r['stop_reason']=='eos'
order=sorted(((pid,step) for pid in ids for step in (1024,1280)),key=lambda x:hmac.new(seed,('PACKET_ORDER_V1|'+x[0]+'|'+str(x[1])).encode(),hashlib.sha256).digest())
assert len(order)==24
packet=[];private_mapping=[];n_trimA=0
for idx,(pid,step) in enumerate(order,1):
 trimA=(pid in trim_A_1024) if step==1024 else (pid not in trim_A_1024)
 condA='TRIMMED_NO_TRAILING_ASCII_SPACE' if trimA else 'BASELINE_FINAL_ASCII_SPACE'
 condB='BASELINE_FINAL_ASCII_SPACE' if trimA else 'TRIMMED_NO_TRAILING_ASCII_SPACE'
 original_A=rec[(pid,step,condA)]['generated_text'];original_B=rec[(pid,step,condB)]['generated_text']
 norm_A=original_A.lstrip(' \t\r\n');norm_B=original_B.lstrip(' \t\r\n')
 pair_id=f'R{idx:02d}'
 packet.append({'pair_id':pair_id,'prompt':by_id[pid],'output_A':norm_A,'output_B':norm_B})
 private_mapping.append({'pair_id':pair_id,'prompt_id':pid,'checkpoint_step':step,'A_condition':condA,'B_condition':condB,'A_raw_sha256':SHA(original_A.encode()),'B_raw_sha256':SHA(original_B.encode()),'A_display_sha256':SHA(norm_A.encode()),'B_display_sha256':SHA(norm_B.encode())})
 n_trimA+=int(trimA)
assert n_trimA==12
assert sum(x['A_condition']=='TRIMMED_NO_TRAILING_ASCII_SPACE' and x['checkpoint_step']==1024 for x in private_mapping)==6
assert sum(x['A_condition']=='TRIMMED_NO_TRAILING_ASCII_SPACE' and x['checkpoint_step']==1280 for x in private_mapping)==6
assert all(not re.search(r'F\d\d|C1024|C1280|step\s*1024|step\s*1280|BASELINE_FINAL|TRIMMED_NO_TRAILING',x['pair_id']) for x in packet)
freeze(P/'FRESH12_BLINDED_REVIEWER_PACKET.json',{'schema':'ttm.fresh12.reviewer_only.blinded_packet.v1','reviewer_id_scope':'CODEX_AI_REVIEWER_ONLY','n_pairs':24,'n_texts':48,'pairs':packet,'notice':'No checkpoint, condition, token IDs or source mapping labels; display whitespace normalized only at leading edge.'})
freeze(P/'FRESH12_PRIVATE_MAPPING.json',{'schema':'ttm.fresh12.owner_private.r_ids.v1','mapping':private_mapping,'allocation_seed_sha256':SHA(seed),'original_allocation_private_file_sha256_unverified':'ed22d6fc6d2075a7d7aedb1512aba9ae4034b95dd39fbe9c5c4a5c86a4aad9ed'})
with (P/'FRESH12_REVIEWER_SCORE_TEMPLATE_R01_R24.csv').open('x',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['pair_id','A_adherence','A_coherence','A_consistency','B_adherence','B_coherence','B_consistency','reviewer_id','note'])
 for row in packet:w.writerow([row['pair_id']]+['']*8)
md=['# FRESH12 — Gói đánh giá nội dung ẩn nhãn (24 cặp A/B)','',
    '**Người chấm:** Codex AI (REVIEWER_ONLY). 24 cặp, 48 văn bản. Không dùng tài liệu giải mù hoặc các báo cáo kết quả trước để chấm.','',
    '**Hướng dẫn:** chấm riêng phần tiếp nối A/B, mỗi trục từ 0–3: bám prompt, mạch lạc, nhất quán. Bỏ qua khoảng trắng đầu phần sinh. Không suy đoán nhãn model/điều kiện.','',
    '**Rubric:** bám prompt 0=bỏ hoàn toàn nhân vật/vật/mục tiêu, 1=giữ một chi tiết nhưng bỏ nhiệm vụ, 2=giữ nhiều yếu tố và tiếp nối có liên quan, 3=giữ đầy đủ nhân vật/vật/mục tiêu và diễn tiến; mạch lạc 0=vụn rời, 1=ít câu hiểu được, 2=phần lớn sự kiện liên kết, 3=truyện tiến triển rõ; nhất quán 0=đổi chủ thể/mâu thuẫn, 1=đứt đoạn nhiều, 2=khá ổn định, 3=ổn định xuyên suốt.','']
for r in packet:
 md+=['## '+r['pair_id'],'','**Prompt:** '+r['prompt'],'','**A:**','', '~~~text',r['output_A'],'~~~','', '**B:**','', '~~~text',r['output_B'],'~~~','']
(P/'FRESH12_BLINDED_REVIEWER_PACKET.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
# Use fresh nonce to encrypt private labelled raw and mapped row assignment; no key in ciphertext.
inner={'raw':raw,'mapping':private_mapping,'allocation_seed_sha256':SHA(seed),'model_source_git_blob':'9762343e06cf800b50574c2871ae1ed58537fb18','pre_run_commit':'cf0b11db6862c16bfe4a8690c6137a92f1d67a3b'}
inner_bytes=json.dumps(inner,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode();compressed=zlib.compress(inner_bytes,9)
nonce=os.urandom(12);aad=b'TTM_FRESH12_PRIVATE_RAW48_MAPPING_AESGCM_V1'
cipher=AESGCM(key).encrypt(nonce,compressed,aad)
freeze(P/'FRESH12_ENCRYPTED_RAW_AND_MAPPING.json',{'schema':'ttm.fresh12.encrypted.raw_and_mapping.v1','encryption':'AES-256-GCM','compression':'zlib level9','nonce_b64':base64.b64encode(nonce).decode(),'aad_utf8':aad.decode(),'ciphertext_with_tag_b64':base64.b64encode(cipher).decode(),'plaintext_uncompressed_sha256':SHA(inner_bytes),'plaintext_bytes':len(inner_bytes),'compressed_bytes':len(compressed),'owner_key_sha256':sha_file('/mnt/data/TTM_FRESH12_OWNER_PRIVATE_DECRYPTION_KEY_DO_NOT_GITHUB.json'),'reviewer_must_not_decrypt':True})
assert zlib.decompress(AESGCM(key).decrypt(nonce,cipher,aad))==inner_bytes
freeze(P/'FRESH12_PACKET_QA_PUBLIC.json',{'schema':'ttm.fresh12.blind_packet.material_QA.v1','source_raw_sha256':sha_file(P/'FRESH12_PRIVATE_RAW_48_UNADJUDICATED.json'),'raw_claim_sha256':sha_file(P/'FRESH12_SINGLE_BATCH_CLAIM.json'),'n_new_generations':48,'n_pairs':24,'n_score_cells':144,'A_trimmed_count':12,'A_baseline_count':12,'checkpoint_subgroups_A_trimmed_each':6,'unique_pair_ids':24,'reviewer_pair_prefix':'R','legacy_reviewer_template_checkpoint_leak':'CORRECTED_BY_PRE_RUN_AMENDMENT_A01','reviewer_packet_json_sha256':sha_file(P/'FRESH12_BLINDED_REVIEWER_PACKET.json'),'reviewer_packet_md_sha256':sha_file(P/'FRESH12_BLINDED_REVIEWER_PACKET.md'),'reviewer_score_template_sha256':sha_file(P/'FRESH12_REVIEWER_SCORE_TEMPLATE_R01_R24.csv'),'encrypted_private_raw_mapping_sha256':sha_file(P/'FRESH12_ENCRYPTED_RAW_AND_MAPPING.json'),'private_mapping_sha256':sha_file(P/'FRESH12_PRIVATE_MAPPING.json'),'owner_key_not_exported':True,'test_reads':0,'q1q2_reads':0,'training_steps':0,'semantic_scores':0,'verdict':'READY_FOR_CODEX_SCOPED_AI_BLINDED_REVIEW','pr13_hold':True,'main_unchanged':True,'lineage_L0017_unchanged':True})
print('FRESH12_BLIND_PACKET_READY_PAIRS=24')
print('FRESH12_AB_COUNTS=12_12_CHECKPOINT_6_6')
print('FRESH12_RAW_SOURCE_SHA256='+sha_file(P/'FRESH12_PRIVATE_RAW_48_UNADJUDICATED.json'))
for name in ['FRESH12_BLINDED_REVIEWER_PACKET.json','FRESH12_BLINDED_REVIEWER_PACKET.md','FRESH12_REVIEWER_SCORE_TEMPLATE_R01_R24.csv','FRESH12_ENCRYPTED_RAW_AND_MAPPING.json','FRESH12_PACKET_QA_PUBLIC.json']:
 print(name,'bytes', (P/name).stat().st_size,'sha256',sha_file(P/name))
