#!/usr/bin/env python3
"""Prospective-to-V3-CPU AI-custody substitution gate. NOT human certification.

Use two already-completed ChatGPT blind review JSON files with pinned raw SHA256,
match their public questions/index to the V3 source fixture, and compare choices
ONLY after both reviews were submitted. Does not invoke any retriever or Reader.
"""
from __future__ import annotations
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

FIXTURE_SHA256 = 'd473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543'
AI_FILES = {
    'A': {'sha256':'46c9fad4b77065cf086213c64ee04145704efa8d6dd3cfbad56d80c9e1d68ed6',
          'rater_id':'CHATGPT_AI_RATER_A'},
    'B': {'sha256':'fd719ada13d2e44a72d29af04d18bb5d839547b288046ce410cfa9e5b7e49cdf',
          'rater_id':'CHATGPT_AI_RATER_B'},
}
AI_PACKET_SCHEMA = 'ttm.vm.v3.p1.blinded_independent_human_review.v1'
REQUIRED_ROW = {'case_id','question','public_index','selected_key','reason','confidence'}
REQUIRED_TOP = {'schema','slot','fixture_sha256','rater_id','reviewed_at_iso8601',
                'attest_no_gold_or_other_review_access','attest_independent_semantic_mapping','cases'}


def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def parse_review(raw:bytes,slot:str)->dict:
    if slot not in AI_FILES: raise ValueError('INVALID_AI_SLOT')
    if sha256(raw)!=AI_FILES[slot]['sha256']:
        raise ValueError('AI_REVIEW_RAW_SHA256_MISMATCH_'+slot)
    obj=json.loads(raw.decode('utf-8'))
    if set(obj)!=REQUIRED_TOP or obj['schema']!=AI_PACKET_SCHEMA or obj['slot']!=slot:
        raise ValueError('AI_PACKET_SCHEMA_SLOT_MISMATCH_'+slot)
    if obj['fixture_sha256']!=FIXTURE_SHA256 or obj['rater_id']!=AI_FILES[slot]['rater_id']:
        raise ValueError('AI_FIXTURE_OR_RATER_ID_MISMATCH_'+slot)
    # The human attestation booleans MUST remain false even for approved AI.
    if obj['attest_no_gold_or_other_review_access'] is not False or obj['attest_independent_semantic_mapping'] is not False:
        raise ValueError('AI_CANNOT_CLAIM_HUMAN_ATTESTATION_'+slot)
    date_str=obj['reviewed_at_iso8601']
    if not isinstance(date_str,str):raise ValueError('MISSING_REVIEW_DATE_'+slot)
    dt=datetime.fromisoformat(date_str)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError('REVIEW_TIMESTAMP_MISSING_TZ_'+slot)
    rows=obj['cases']
    if not isinstance(rows,list) or len(rows)!=32:raise ValueError('AI_NOT_32_ROWS_'+slot)
    return obj


def validate_two_ai_reviews(cases:list[dict],fixture_sha256:str,a_raw:bytes,b_raw:bytes)->dict:
    """Private target_key is read here ONLY after public AI selections finalized."""
    if fixture_sha256!=FIXTURE_SHA256:raise ValueError('WRONG_FROZEN_V3_FIXTURE')
    p1=[c for c in cases if c['stratum']=='P1_UNSEEN_PARAPHRASE']
    if len(cases)!=256 or len(p1)!=32:raise ValueError('INVALID_V3_CASE_SET')
    packets={slot:parse_review(raw,slot) for slot,raw in (('A',a_raw),('B',b_raw))}
    selected={}
    for slot,packet in packets.items():
        values=[]
        for row,c in zip(packet['cases'],p1):
            if set(row)!=REQUIRED_ROW:raise ValueError('AI_PUBLIC_ROW_SCHEMA_'+slot)
            if row['case_id']!=c['case_id'] or row['question']!=c['question'] or row['public_index']!=c['public_index']:
                raise ValueError('AI_PUBLIC_INDEX_OR_ORDER_DRIFT_'+slot)
            choice=row['selected_key']
            if not isinstance(choice,str) or choice not in {v['key'] for v in c['public_index']}:
                raise ValueError('AI_ROW_NO_VALID_SELECTED_KEY_'+slot)
            if type(row['confidence']) is not int or not 0<=row['confidence']<=3:
                raise ValueError('AI_CONFIDENCE_INVALID_'+slot)
            if not isinstance(row['reason'],str) or len(row['reason'].strip())<8:
                raise ValueError('AI_REASON_MISSING_'+slot)
            values.append(choice)
        selected[slot]=values
    if selected['A']!=selected['B']:
        raise ValueError('AI_RATERS_DISAGREE_HOLD')
    if any(choice!=case['target_key'] for choice,case in zip(selected['A'],p1)):
        raise ValueError('AI_AGREEMENT_PRIVATE_GOLD_MISMATCH_HOLD')
    if packets['A']['rater_id']==packets['B']['rater_id']:
        raise ValueError('IDENTICAL_RATER_IDS')
    return {
        'schema':'ttm.vm.v3.p1.ai_substitute_custody.v1',
        'status':'PASS_TWO_AI_BLIND_REVIEW_SOURCE_AND_GOLD_32_OF_32_EXPLORATORY',
        'scientific_class':'AI_ASSISTED_EXPLORATORY_SCOPED',
        'amendment':'PROSPECTIVE_TO_CPU_POST_AI_REVIEWS',
        'fixture_sha256':FIXTURE_SHA256,
        'raw_review_sha256':{'A':AI_FILES['A']['sha256'],'B':AI_FILES['B']['sha256']},
        'reviewed_cases':32,'agent_agreement':32,'agent_A_gold_match':32,'agent_B_gold_match':32,
        'human_reviewers':0,'human_gate_satisfied':False,'ai_substitution_accepted_by_owner':True,
        'independence':'TWO_AI_SESSIONS_SELF_REPORTED_CLEAN_NOT_CRYPTOGRAPHICALLY_PROVEN',
        'TEST_opened':False,'reader_forward_calls':0,'science_executed':False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root',required=True,type=Path)
    ap.add_argument('--fixture',required=True,type=Path)
    ap.add_argument('--review-a',required=True,type=Path)
    ap.add_argument('--review-b',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    root=args.project_root.resolve(strict=True)
    for n in ('fixture','review_a','review_b'):
        path=getattr(args,n).resolve(strict=True)
        if not path.is_relative_to(root):raise ValueError('INPUT_OUTSIDE_OWNER_PROJECT_ROOT_'+n)
    out=args.out.resolve()
    if not out.is_relative_to(root) or out.exists():raise FileExistsError('REFUSE_OUTSIDE_OR_RECEIPT_OVERWRITE')
    fixture_bytes=args.fixture.read_bytes()
    if sha256(fixture_bytes)!=FIXTURE_SHA256:raise ValueError('FIXTURE_SHA_NOT_PINNED')
    from v3_fresh256_fixture import build,serialized
    cases=build()
    if fixture_bytes!=serialized(cases):raise ValueError('FIXTURE_SOURCE_BYTES_DIFFER')
    receipt=validate_two_ai_reviews(cases,FIXTURE_SHA256,args.review_a.read_bytes(),args.review_b.read_bytes())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'AI_P1':'PASS_32_32',
                      'human_gate':'NOT_SATISFIED','SCIENCE':False,'TEST':False},sort_keys=True))

if __name__=='__main__':main()