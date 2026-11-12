#!/usr/bin/env python3
"""Generate blind P1 review packets; verify independent human attestations.

Never auto-approve a proposed new paraphrase. Reviewers independently map
query to one public card, without access to answer, gold, or each other.
This is an owner-local SOURCE custody check, NOT Reader inference.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from v3_fresh256_fixture import build, serialized

P1='P1_UNSEEN_PARAPHRASE'
EXPECTED_NAMES=('P1_REVIEW_A_TEMPLATE.json','P1_REVIEW_B_TEMPLATE.json')


def h(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()


def public_view(case:dict)->dict:
    # No gold_action, target_key, answer, stratum, truth_constraints, memory values.
    return {'case_id':case['case_id'],'question':case['question'],
            'public_index':case['public_index']}


def review_packet(fixture_sha:str, cases:list[dict], slot:str)->dict:
    if slot not in ('A','B'):raise ValueError('INVALID_RATER_SLOT')
    rows=[]
    for case in cases:
        view=public_view(case)
        rows.append({**view,'selected_key':None,'reason':'','confidence':None})
    return {'schema':'ttm.vm.v3.p1.blinded_independent_human_review.v1',
            'slot':slot,'fixture_sha256':fixture_sha,
            'rater_id':None,'reviewed_at_iso8601':None,
            'attest_no_gold_or_other_review_access':False,
            'attest_independent_semantic_mapping':False,
            'cases':rows}


def validate_receipts(fixture_cases:list[dict],fixture_sha:str,a:dict,b:dict)->dict:
    p1=[c for c in fixture_cases if c['stratum']==P1]
    if len(p1)!=32:raise ValueError('NOT_32_P1_CASES')
    gold={x['case_id']:x['target_key'] for x in p1}
    ratings=[]
    for slot,receipt in (('A',a),('B',b)):
        expected=review_packet(fixture_sha,p1,slot)
        if receipt.get('schema')!=expected['schema'] or receipt.get('slot')!=slot:
            raise ValueError('RATER_PACKET_SCHEMA_SLOT_MISMATCH')
        if receipt.get('fixture_sha256')!=fixture_sha:
            raise ValueError('RATER_PACKET_FIXTURE_HASH_MISMATCH')
        if not isinstance(receipt.get('rater_id'),str) or len(receipt['rater_id'].strip())<3:
            raise ValueError('RATER_IDENTITY_NOT_ATTESTED')
        if not isinstance(receipt.get('reviewed_at_iso8601'),str) or 'T' not in receipt['reviewed_at_iso8601']:
            raise ValueError('RATER_TIME_NOT_ATTESTED')
        if receipt.get('attest_no_gold_or_other_review_access') is not True or receipt.get('attest_independent_semantic_mapping') is not True:
            raise ValueError('RATER_INDEPENDENCE_OR_SEMANTIC_ATTESTATION_MISSING')
        rows=receipt.get('cases')
        if not isinstance(rows,list) or len(rows)!=32:raise ValueError('WRONG_RATER_CASE_COUNT')
        selection={}
        for row,ref in zip(rows,expected['cases']):
            for key in ('case_id','question','public_index'):
                if row.get(key)!=ref[key]:raise ValueError('BLINDED_CASE_CONTENT_MODIFIED:'+key)
            if set(row)!=set(ref):raise ValueError('RATER_PACKET_EXTRA_FIELD')
            sk=row.get('selected_key')
            if sk is not None and (not isinstance(sk,str) or sk not in {x['key'] for x in ref['public_index']}):
                raise ValueError('RATER_INVALID_SELECTION')
            if not isinstance(row.get('reason'),str) or len(row['reason'].strip())<8:
                raise ValueError('RATER_REASON_MISSING')
            confidence=row.get('confidence')
            if type(confidence) is not int or not 0<=confidence<=3:
                raise ValueError('RATER_CONFIDENCE_INVALID')
            selection[row['case_id']]=sk
        ratings.append((receipt['rater_id'].strip().casefold(),selection))
    if ratings[0][0]==ratings[1][0]:raise ValueError('TWO_DISTINCT_REVIEWERS_REQUIRED')
    left,right=ratings[0][1],ratings[1][1]
    consensus=sum(left[k] is not None and left[k]==right[k] for k in gold)
    agreement_with_private_truth=sum(left[k]==right[k]==gold[k] for k in gold)
    if consensus!=32 or agreement_with_private_truth!=32:
        raise ValueError('RATER_DISAGREEMENT_OR_GOLD_MISMATCH_HOLD_DATA_ADJUDICATION')
    return {'status':'PASS_TWO_DISTINCT_BLIND_HUMAN_ATTESTATIONS',
            'rater_ids':[x[0] for x in ratings],
            'agreed_correct_p1':agreement_with_private_truth,
            'cases':32,'fixture_sha256':fixture_sha,
            'limitations':'Attestation is declared by reviewers; this verifier cannot prove offline separation or authenticity cryptographically.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--fixture',type=Path,required=True)
    p.add_argument('--packet-dir',type=Path,required=True)
    p.add_argument('--generate-once',action='store_true')
    p.add_argument('--review-a',type=Path)
    p.add_argument('--review-b',type=Path)
    p.add_argument('--receipt-out',type=Path)
    args=p.parse_args()
    root=args.project_root.resolve(strict=True)
    fixture=args.fixture.resolve(strict=True)
    if not fixture.is_relative_to(root):raise ValueError('FIXTURE_OUTSIDE_ROOT')
    original=fixture.read_bytes()
    cases=build()
    if original!=serialized(cases):raise ValueError('FROZEN_FIXTURE_BYTES_MISMATCH')
    digest=h(original)
    packetdir=args.packet_dir.resolve()
    if not packetdir.is_relative_to(root):raise ValueError('REVIEW_PACKET_OUTSIDE_ROOT')
    p1=[c for c in cases if c['stratum']==P1]
    if args.generate_once:
        packetdir.mkdir(parents=True,exist_ok=True)
        for slot,name in zip(('A','B'),EXPECTED_NAMES):
            out=packetdir/name
            if out.exists():raise FileExistsError('REVIEW_TEMPLATE_NO_OVERWRITE')
            out.write_text(json.dumps(review_packet(digest,p1,slot),indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print(json.dumps({'status':'PENDING_INDEPENDENT_HUMAN_REVIEW','cases':32,'blinded_templates':2,
                          'science_execution':False,'test_opened':False}))
        return
    if not (args.review_a and args.review_b and args.receipt_out):
        raise SystemExit('NO_APPROVAL_WITHOUT_TWO_INDEPENDENT_REVIEW_FILES')
    for rp in (args.review_a,args.review_b):
        if not rp.resolve(strict=True).is_relative_to(root):raise ValueError('REVIEW_OUTSIDE_ROOT')
    receipt=validate_receipts(cases,digest,json.loads(args.review_a.read_text()),json.loads(args.review_b.read_text()))
    out=args.receipt_out.resolve()
    if not out.is_relative_to(root) or out.exists():raise FileExistsError('REVIEW_RECEIPT_REFUSE_OVERWRITE_OR_OUTSIDE_ROOT')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(receipt['status'])
if __name__=='__main__':main()
