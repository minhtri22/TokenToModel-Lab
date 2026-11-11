#!/usr/bin/env python3
"""FRESH16 V2 post-inference blinded packet gate. No model import or forward.

S2 packet is released only after SHA-locked S1 individual scores are anchored in
Git history. Final unblind is allowed only after a separate S2 SHA anchor.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

REL = 'tools/research/ttm_small4m_quality_gap/ttm_fresh16_v2_packet_gate.py'
S1_ANCHOR = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_S1_SCORE_SHA_ANCHOR.json'
S2_ANCHOR = 'artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_S2_PAIR_SHA_ANCHOR.json'


def need(ok,reason):
    if not ok:raise RuntimeError(reason)


def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',required=True,choices=('package-s2','unblind'))
    ap.add_argument('--project-root',required=True,type=Path)
    ap.add_argument('--worktree',required=True,type=Path)
    ap.add_argument('--run-dir',required=True,type=Path)
    ap.add_argument('--expected-head',required=True)
    ap.add_argument('--s1-scores',required=True,type=Path)
    ap.add_argument('--s1-anchor-commit',required=True)
    ap.add_argument('--s2-scores',type=Path)
    ap.add_argument('--s2-anchor-commit',default='')
    args=ap.parse_args()
    root=args.project_root.resolve(strict=True)
    work=args.worktree.resolve(strict=True)
    mod_file=work/'tools/research/ttm_small4m_quality_gap/ttm_fresh16_v2_e0.py'
    spec=importlib.util.spec_from_file_location('fresh16_e0_packet_helper',mod_file)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    mod.fixed_source(root,work,args.expected_head)
    need(mod.git_blob(mod.project_file(root,work/REL))==mod.git(work,'rev-parse','HEAD:'+REL),
         'PACKET_SOURCE_NOT_COMMITTED')
    prepared=load(mod.project_file(root,args.run_dir/'PREPARED.json'))
    finish=load(mod.project_file(root,args.run_dir/'RUN_FINISHED.json'))
    private_map=mod.project_file(root,args.run_dir/'BLIND_MAP_PRIVATE.json')
    rows=mod.map_validate(load(private_map))
    need(prepared['sealed_map_sha256']==mod.sha(private_map) and
         prepared['source_head']==args.expected_head and finish.get('original_outputs')==32,
         'OUTPUT_OR_MAP_SOURCE_DRIFT')
    packet=mod.project_file(root,args.run_dir/'S1_BLIND_PACKET_PRIVATE.json')
    need(finish['S1_packet_sha256']==mod.sha(packet),'S1_PACKET_SHA_DRIFT')
    s1=mod.project_file(root,args.s1_scores)
    first=load(s1)
    need(first.get('schema')=='ttm.fresh16.v2.s1_individual_scores.v1' and
         first.get('rater_identity_and_version') and len(first.get('records',[]))==32,
         'S1_SCORE_FILE_SCHEMA_INVALID')
    byid={r['opaque_id']:r for r in first['records']}
    need(len(byid)==32 and set(byid)=={x['opaque_id'] for x in rows},'S1_IDS_MISMATCH')
    s1_packet_byid={x['opaque_id']:x for x in load(packet)['records']}
    for rid,row in byid.items():
        need(type(row.get('adherence_0_3')) is int and row['adherence_0_3'] in (0,1,2,3),
             'S1_ADHERENCE_INVALID')
        need(all(type(row.get(k)) is int and row[k] in (0,1,2,3)
                 for k in ('coherence_0_3','entity_consistency_0_3','causal_continuation_0_3')),
             'S1_SECONDARY_INVALID')
        if row['adherence_0_3']>=2:
            span=row.get('generated_event_text_span')
            need(isinstance(span,str) and bool(span) and
                 span in s1_packet_byid[rid]['generated_text_only'] and
                 row.get('has_new_event_after_slot') is True,
                 'S1_GE2_MISSING_EXACT_EVENT_EVIDENCE')
    s1_anchor=mod.load_json_from_git(work,args.s1_anchor_commit,S1_ANCHOR)
    need(s1_anchor.get('s1_score_file_sha256')==mod.sha(s1) and
         s1_anchor.get('sealed_map_sha256')==mod.sha(private_map) and
         s1_anchor.get('source_head')==args.expected_head,
         'S1_SHA_NOT_COMMITTED_BEFORE_PAIR_RELEASE')
    if args.mode=='package-s2':
        groups={}
        for row in rows:groups.setdefault(row['opaque_pair_id'],[]).append(row)
        pack=[]
        for pairid,two in groups.items():
            packet_rows=[]
            for info in two:
                rid=info['opaque_id']
                packet_rows.append({'opaque_id':rid,
                                    'prompt_text':s1_packet_byid[rid]['prompt_text'],
                                    'generated_text_only':s1_packet_byid[rid]['generated_text_only'],
                                    'locked_s1_adherence_0_3':byid[rid]['adherence_0_3']})
            pack.append({'opaque_pair_id':pairid,'members':packet_rows})
        need(len(pack)==16,'S2_PAIR_PACKET_CARDINALITY_INVALID')
        out=args.run_dir/'S2_BLIND_PACKET_PRIVATE.json'
        mod.new_json(out,{'schema':'ttm.fresh16.v2.s2_packet.v1',
                          's1_score_file_sha256':mod.sha(s1),'pairs':pack})
        print('FRESH16_E0_S2_PACKET=CREATED_16_PAIRS_CHECKPOINT_MASKED')
        print('FRESH16_E0_S2_PACKET_SHA256='+mod.sha(out))
        return
    need(args.s2_scores is not None and len(args.s2_anchor_commit)==40,
         'S2_SCORES_OR_ANCHOR_MISSING')
    s2_packet=mod.project_file(root,args.run_dir/'S2_BLIND_PACKET_PRIVATE.json')
    pairs=load(s2_packet)
    need(pairs['s1_score_file_sha256']==mod.sha(s1) and len(pairs['pairs'])==16,
         'S2_PACKET_NOT_PREPARED')
    s2=mod.project_file(root,args.s2_scores)
    pair_scores=load(s2)
    need(pair_scores.get('schema')=='ttm.fresh16.v2.s2_pair_scores.v1' and
         pair_scores.get('s1_score_file_sha256')==mod.sha(s1) and
         len(pair_scores.get('records',[]))==16 and
         pair_scores.get('adjudicator_identity_and_version'), 'S2_SCORE_FILE_SCHEMA_INVALID')
    decisions={x['opaque_pair_id']:x for x in pair_scores['records']}
    need(len(decisions)==16 and set(decisions)=={x['opaque_pair_id'] for x in pairs['pairs']},
         'S2_PAIR_IDS_MISMATCH')
    for pair in pairs['pairs']:
        decision=decisions[pair['opaque_pair_id']]
        values=[x['locked_s1_adherence_0_3'] for x in pair['members']]
        need(type(decision.get('h2_binary')) is int and decision['h2_binary'] in (0,1),
             'S2_BINARY_INVALID')
        need(set(decision.get('member_opaque_ids',[]))==set(x['opaque_id'] for x in pair['members']),
             'S2_PAIR_MEMBERS_CHANGED')
        need(decision['h2_binary']==0 or (min(values)>=2 and
             decision.get('semantic_contrast_class') in ('SEMANTIC_ROLE_BINDING','FACT_CONDITIONED_ACTION') and
             bool(decision.get('swap_countercheck_result')) and bool(decision.get('pair_evidence'))),
             'S2_POSITIVE_UNSUPPORTED_BY_LOCKED_S1')
    s2_anchor=mod.load_json_from_git(work,args.s2_anchor_commit,S2_ANCHOR)
    need(s2_anchor.get('s2_pair_file_sha256')==mod.sha(s2) and
         s2_anchor.get('s1_score_file_sha256')==mod.sha(s1) and
         s2_anchor.get('sealed_map_sha256')==mod.sha(private_map) and
         s2_anchor.get('source_head')==args.expected_head,
         'S2_SHA_NOT_COMMITTED_BEFORE_UNBLIND')
    h1=sum(byid[x['opaque_id']]['adherence_0_3']>=2 for x in rows if x['checkpoint_step']==1024)
    pairs1024={x['opaque_pair_id']:x['pair_id'] for x in rows if x['checkpoint_step']==1024}
    h2=sum(decisions[pid]['h2_binary'] for pid in pairs1024)
    cats={'CP01':'entity_location','CP02':'entity_location','CP03':'causal_reasoning',
          'CP04':'causal_reasoning','CP05':'rule_constraint','CP06':'rule_constraint',
          'CP07':'goal_persistence','CP08':'goal_persistence'}
    by_category={cat:sum(decisions[pid]['h2_binary'] for pid,id_ in pairs1024.items() if cats[id_]==cat)
                 for cat in set(cats.values())}
    verdict=('QUALITY_CANDIDATE_SCOPED_STEP1024_ONLY' if h1>=12 and h2>=6 and
             min(by_category.values())>=1 else 'NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED')
    report={'schema':'ttm.fresh16.v2.final_tally.v1','source_head':args.expected_head,
            'original_outputs':32,'primary_checkpoint_step':1024,
            'step1280_role':'DESCRIPTIVE_ONLY','H1_num_ge2':h1,'H1_denominator':16,
            'H2_pairs':h2,'H2_denominator':8,'H2_category_successes':by_category,
            'S1_scores_sha256':mod.sha(s1),'S2_scores_sha256':mod.sha(s2),
            'sealed_map_sha256':mod.sha(private_map),'verdict':verdict,
            'scientific_scope':'LOCAL_CONTEXT_FACT_CONDITIONED_CONTINUATION_EXPLORATORY'}
    mod.new_json(args.run_dir/'FINAL_TALLY_PRIVATE.json',report)
    print('FRESH16_E0_FINAL_VERDICT='+verdict)

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,ImportError) as exc:
        print('FRESH16_E0_PACKET_HOLD='+type(exc).__name__+':'+str(exc),file=sys.stderr)
        raise SystemExit(2)
