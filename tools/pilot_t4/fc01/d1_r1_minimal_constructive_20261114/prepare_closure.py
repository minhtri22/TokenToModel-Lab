#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
J=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
A=json.loads((P/'TTM_D1_R1_BOUNDED_CONSTRUCTIVE_SEARCH_RECEIPT_20261114.json').read_text())
B=json.loads((P/'TTM_D1_R1_BOUNDED_PAIRED_CONSTRUCTIVE_PROBE_20261114.json').read_text())
CATS=['entity_location','causal_reasoning','rule_constraint','goal_persistence']
OP='TTM_SMALL4M_D1_R1_MINIMAL_SEMANTIC_CONTRACT_FREEZE_AND_CONSTRUCTIVE_FOUR_CATEGORY_FEASIBILITY_SINGLE_REVIEW_GATE'
freeze={
'schema':'ttm.d1.r1.prospective_minimal_semantic_contract_source_freeze.v1','operation':OP,
'freeze_classification':'FROZEN_WITHIN_THIS_SOURCE_TEST_PACKET_PENDING_INDEPENDENT_REVIEW_NOT_AUTHORIZED_V6_AMENDMENT',
'frozen_scientific_head':'dd52804685d186c17e600221ffb16ce78aea12ea',
'prior_evidence_commit':'d24c50ad8a9e377264dd8fa073bcc553824f8992',
'frozen_v6_git_blob_sha1':'c6ac330c40e31035116add165ef30fa58af59639',
'proposed_semantics_id':'R1_PROSPECTIVE_PHYSICAL_P1_20261114',
'policy_decisions':{
'TRANSFER':'Require holder=a0, recipient=a1, same agent location and strict expired protection. Move item only to co-located recipient. Frozen V6 has no co-location check: material amendment.',
'CARRY':'Target unheld at actor location OR already held by actor; actor moves to a different location and all items held by actor follow. Frozen V6 precondition only unheld: material amendment.',
'RELOCATE':'Only unheld item at a0 current location; destination different; change item location only.',
'RETAIN':'Actor currently holds target; time horizon must strictly increase protected_until, horizon >=current_time; inclusive protection through horizon; no minimal-horizon cost or label-conditioned tiebreak. Frozen V6 uses set, not monotone max: material amendment.',
'WAIT':'Must target pending scheduled trigger in future; atomic advance all intermediate clock ticks in order; fire scheduled triggers then exogenous request, with protection guard ahead of transfer; clear defer_until on arrival. Frozen V6 lacks explicit advance in original AM01 effect: material amendment.',
'ACTIVATE':'OFF→ON, immediately fire linked trigger if present, no hidden causal link.',
'GENESIS':'T0 intrinsic assigned holders allowed if co-located with their item, all power OFF, triggers false, no defer, schedules only future T1/T2/NONE, no exogenous request at T0. Initial-state axiom only, not historical predecessor proof.',
'EXOGENOUS':'At most one request (at∈{T1,T2,NONE}, item, recipient), processed only during atomic WAIT tick; require holder, nonself, unprotected, colocated; if blocked it stays blocked (no rescheduling). This fluent is not in the original frozen V6 AM01 state fluents.',
'ACTION_COST':'For reachability categories choose all shortest feasible plans by number of actions ≤3 with no lexical tiebreak. For goal_persistence use pure hold-through-T2 safety and optional *explicit goal of stationary item location*; enumerate ALL successful one-step interventions, never choose one by desired horizon.',
'PRIORITY':'Scheduled trigger first, then exogenous transfer request, protection guard wins at equal time. CARRY relocates all held items atomically.'
},
'known_conflicts_with_original_V6':['TRANSFER no colocation in frozen V6','CARRY original target unheld','WAIT old effect only defers, new atomic time update','extra external transfer request fluent not in original V6','RETAIN prior version may reduce protection, new candidate disallows'],
'decision':'FREEZE_PROSPECTIVE_SOURCE_ASSUMPTIONS_FOR_BOUNDED_FEASIBILITY_ONLY; NOT_SCIENCE_NOT_OWNER_ADOPTION',
'owner_decision':'NOT_SUBSTITUTED_NOT_REQUESTED',
'rights_custody':'NOT_EXECUTED',
'preserve':{'D1_BRIDGE_SCIENCE':'HOLD','TEST_Q1Q2':'SEALED','FC02':'NOT_OPENED','GPU':0,'TRAIN':0,'INFERENCE':0,'FROZEN_V6':'UNCHANGED','MAIN':'UNCHANGED','lineage.md':'UNCHANGED'}
}
(P/'TTM_D1_R1_PROSPECTIVE_MINIMAL_SEMANTIC_CONTRACT_FREEZE_20261114.json').write_text(J(freeze))
# all 32 required slot records, zero are silently substituted by earlier public blueprints
slots=[]
for c in CATS:
 for role in ('TRAIN','STRUCTURAL_OOD'):
  for i in range(1,5):
   slots.append({'slot_id':f'{c.upper()}_{role}_{i:02d}','category':c,'design_split':role,
                 'typed_actual_new_skeleton':'NOT_CREATED','genesis_and_oracle_source':'NOT_EXECUTED_NEW_SKELETON',
                 'canonical_action_causal_graph_sha256':None,'matched_world_action_witness':None,
                 'source_only_admission':'HOLD_NOT_PROVEN',
                 'reason':'Bounded constructive search failed to prove 4 OOD/category; source blueprint materialization withheld to avoid false novelty.'})
slot={'schema':'ttm.d1.r1.constructive_32_slot_admission_matrix.v1','operation':OP,'required':{'total':32,'train':16,'ood':16,'per_category_train':4,'per_category_ood':4},'actual_new':0,'admitted_ood':0,'slots':slots,
'not_a_claim_of_global_impossibility':True}
(P/'TTM_D1_R1_32_CONSTRUCTIVE_ADMISSION_MATRIX_20261114.json').write_text(J(slot))
readiness={'schema':'ttm.d1.r1.source_only_constructive_readiness_and_custody.v1','operation':OP,
'baseline_and_shortcuts':{
'prior_category_side_baseline':'10/32 old OOD sides inherited, not rerun','prior_shallow_source_baseline':'64/64 old sides against prior receipt, inherited not rerun',
'current_new_skeleton_source_baseline':'NOT_EXECUTED_NO_ADMITTED_NEW_SKELETON',
'matched_world_nonoverlap':'NOT_PROVEN',
'policy':'Category + side, goal-only, guard/event cue, shallow rules, action-frequency, counterfactual irrelevant-field and role-relabel tests must pass on actual admitted AST before design GO; a weak baseline alone does not prove novelty.'},
'renderer_parser_T1':{'preview_old':'INHERITED_SOURCE_REPORT_ONLY','new_renderer':'NOT_IMPLEMENTED_FOR_ADMITTED_NEW_AST','production_parser':'NOT_VERIFIED','tokenizer_T1_SHA':'NOT_VERIFIED','token_lengths':'NOT_EXECUTED','grammar_positive_64':'NOT_EXECUTED','grammar_negative_64':'NOT_EXECUTED','guard':'Never render split, IDs, provenance, gold, oracle fields or truth labels; test cue balance after formal AST admission.'},
'eval_rights_private_custody':{'role_matrix':'PROSPECTIVE_OWNER_PREREG_PRIVATE_CUSTODIAN_INDEPENDENT_AUDITOR_BLIND_SCORER','source_rights_license_PII':'NOT_VERIFIED','private_EVAL_AST':'NOT_CREATED','private_gold':'NOT_CREATED','private_HMAC_KEY':'NOT_CREATED','key_id_rotation':'SPEC_DESIGN_ONLY','signed_ledger_and_root':'NOT_EXECUTED','ACL_denial_and_replay_tamper':'NOT_EXECUTED','blind_mapping':'NOT_CREATED','unseal_order':'Prereg+design GO, rights, custodian, private EVAL freeze with HMAC and source provenance, independent nonoverlap signed audit, parser/model/output SHA freeze, blind scoring, authorized postlock unseal; no post-outcome replacements.','public_blueprints_as_eval':'FORBIDDEN'},
'go_decision':'HOLD_INTEGRATED_ALL_FOUR_CATEGORY_EVIDENCE_MISSING'}
(P/'TTM_D1_R1_CONSTRUCTIVE_SHORTCUT_RENDER_CUSTODY_GATES_20261114.json').write_text(J(readiness))
summary={c:A['category_counts'][c] for c in CATS}
pairs={c:B['summary'][c] for c in CATS}
receipt={'schema':'ttm.d1.r1.minimal_semantics_constructive_single_gate_adjudication.v1','operation':OP,
'review_type':'AI_SOURCE_ONLY_AUTHOR_WITH_STANDALONE_PYTHON_REFERENCE_NO_DISTINCT_EXTERNAL_REVIEWER',
'source_of_truth':'GitHub prior exact d24c50ad commit and frozen dd5280 V6 contract',
'source_blueprints_sha256':'6d45a667a8e1f0a3c513c50951b2624d5fbebe3cde85c9934b41fb8dcf712e83',
'source_checker_receipt_sha256':'8ec56fe2e24950417b65f3853e477790221f7414ab96b95aadcc4fe379f91964',
'contract_file':'TTM_D1_R1_PROSPECTIVE_MINIMAL_SEMANTIC_CONTRACT_FREEZE_20261114.json',
'bounded_search':{'scenario_total':sum(x['searched_scenarios'] for x in summary.values()),'unique_case_total':sum(x['status_counts'].get('UNIQUE',0) for x in summary.values()),'category':summary,'depth_max':3,'goal_classification':'reachability vs persistence pure-safety'},
'matched_AB_one_fluent_probe':{'pair_total':sum(x['one_fluent_AB_distinct_first_action_pairs'] for x in pairs.values()),'category':pairs,'method_limit':'coarse motif is NOT canonical action-causal graph equivalence'},
'fresh_new_source_only_checks':{'positive':sum(v=='PASS' for v in A['new_targeted_checks'].values()),'total':len(A['new_targeted_checks']),'checks':A['new_targeted_checks'],'old_historic_13_13_12_12_rerun':False},
'actual_new_32_skeletons_count':0,'actual_new_train_count':0,'actual_new_ood_count':0,'accepted_new_ood':0,
'counterexample_persistence':{'bounded_family':'single exogenous transfer request T1/T2/NONE, pure safety through T2, optional stationary-location goal','unique_scenarios':6,'all_six_first_action':'RETAIN i0 T0 T2','matched_AB_distinct_first_action_one_fluent_pairs':0,
'claim_limit':'Only a fixed finite bounded grammar. Not a mathematical upper bound over full V6.'},
'no_formal_full_graph_certification':True,
'parsing_custody':'NOT_EXECUTED',
'distinct_external_reviewer':'NOT_EXECUTED',
'verdict':'HOLD_ONTOLOGY_FEASIBILITY',
'recommendation':'Stop generating 32 replacement skeletons under this D1 Bridge formulation; require independently adjudicated new task/ontology semantic amendment or narrow scientifically valid benchmark before attempting again. Preserve frozen V6, no science permission.',
'preserved_gates':freeze['preserve']}
(P/'TTM_D1_R1_CONSTRUCTIVE_SINGLE_GATE_ADJUDICATION_RECEIPT_20261114.json').write_text(J(receipt))
md=f'''# TTM-Small-4M D1 Bridge R1 — Minimal semantic contract và bounded constructive feasibility

**Operation:** `{OP}`  
**Input evidence:** GitHub exact commit `d24c50ad8a9e377264dd8fa073bcc553824f8992`  
**Frozen science:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**Scope:** SOURCE-ONLY, không tạo EVAL/gold, không GPU/TRAIN/INFERENCE.  
**Single design adjudication:** **`HOLD_ONTOLOGY_FEASIBILITY`**.

## 1. Hợp đồng ngữ nghĩa đã được *freeze* ở phạm vi thử nghiệm nguồn

Đã tạo `TTM_D1_R1_PROSPECTIVE_MINIMAL_SEMANTIC_CONTRACT_FREEZE_20261114.json`: lựa chọn **physical co-located TRANSFER**, CARRY target có thể đang được holder giữ và lan truyền tọa độ của mọi item đang giữ, WAIT xử lý clock và event theo từng tick, RETAIN tăng protection và không ưu tiên horizon theo nhãn gold, T0 cho phép custody ban đầu theo initialization axioms và từ chối request ở T0. Shortest path theo số hành động tối đa 3 cho goal reachability; goal persistence đánh giá pure safety đến T2 và tất cả action một bước, không có cost/tie break tự phát.

**Đây là versioned candidate freeze để truy nguyên phép tìm kiếm, không phải phê duyệt sửa frozen V6.** Frozen V6 không có `TRANSFER` co-location, không có exogenous-request fluent trong AM01, `WAIT` chỉ ghi defer ở hợp đồng gốc, `CARRY` gốc yêu cầu target unheld. Các khác biệt là material amendments. Không thể dùng source QA mới để ký `V6_ACCEPTED`.

## 2. Tìm kiếm hữu hạn thực sự đã chạy

`constructive_search.py` dùng Python standard library và **không import generator/checker lịch sử**. Duyệt tích Descartes khai báo tường minh trong source, sinh toàn bộ world T0 hợp lệ trong từng subgrammar, áp dụng sáu transition, BFS giữ **mọi first action** cùng độ dài ngắn nhất (depth <=3, edge cap 3500); persistence dùng pure safety qua event. `pairwise_constructive_probe.py` xét cặp world cùng goal, khác đúng một typed state fluent và hành động đầu tiên thực sự khác.

| Category | World+goal thử | Unique first action | Cặp A/B một fluent, khác hành động | Motif proxy thô |
|---|---:|---:|---:|---:|
| entity_location | 96 | 20 | 2 | 1 |
| causal_reasoning | 54 | 16 | 1 | 1 |
| rule_constraint | 108 | 52 | 29 | 3 |
| goal_persistence | 72 | 6 | **0** | **0** |
| **TOTAL** | **330** | **94** | **32** | — |

12/12 phép kiểm **mới của chính engine nguồn** PASS (co-location, protection, held CARRY propagation, WAIT/clock, genesis, T0 request, RETAIN no-tiebreak). Không chạy lại historical 13/13 hoặc 12/12.

**Giới hạn có ý nghĩa:** Ở goal_persistence, sáu ca unique đều là một motif `RETAIN i0 T0 T2` khi request tại T2, target và người nhận cùng vị trí, và task đồng thời yêu cầu item giữ nguyên vị trí. Thay đổi holder i1 hay protection T0/T1 không tạo dependency topology mới. Các ca request tại T1 hoặc không có request tạo đa nghiệm do nhiều hành động bảo toàn safety. Không tìm được A/B counterfactual một fluent có unique **và** khác hành động trong subgrammar này.

Trong `causal_reasoning`, motif một-fluent hợp lệ duy nhất của search là đổi lịch WAIT, chưa phải action-causal structural OOD. Trong `rule_constraint`, ba motif chỉ là **proxy** sau bỏ nhãn role/time, không phải chứng minh độc lập 3 topology. Nhiều unique world không chứng minh có bốn OOD mới.

**Không suy diễn kết quả tìm kiếm thành định lý bất khả thi toàn bộ ontology**: fixed role names, goal forms, chỉ một external request, time T0–T2, depth≤3 và các lựa chọn domain cụ thể. Không duyệt tất cả goal/horizon/causal transition graph khả dĩ trong V6.

## 3. Tình trạng 16 TRAIN + 16 OOD và 64-pair admission

**0** new science-admissible TRAIN, **0** new science-admissible OOD. `TTM_D1_R1_32_CONSTRUCTIVE_ADMISSION_MATRIX_20261114.json` giữ đủ 32 slot ở `HOLD_NOT_PROVEN`. Không tạo thêm blueprint tô nhãn TRAIN/OOD từ kết quả subgrammar chỉ để cho đủ 4+4/category. **64 cặp chứng nhận nonoverlap mới: `NOT_EXECUTED_NO_32_ADMITTED_INPUTS`.** 64 cặp nguồn cũ ở commit `d24c50ad...` vẫn là negative controls: 5 direct và 9 swapped exact worlds, 55/64 coarse proxy trùng, không chứng minh novelty dương. Không cộng các proxy.

Các ca illustrative có nguồn và oracle trong receipt `TTM_D1_R1_BOUNDED_CONSTRUCTIVE_SEARCH_RECEIPT_20261114.json` **không** được coi là skeleton scientific-admissible hoặc gold.

## 4. Source shortcut, renderer/parser và EVAL custody

Renderer production, parser T1, tokenizer SHA và grammar test 64+/64− **chưa thực hiện** vì chưa có AST được chấp nhận. Baseline category+side 10/32 và shallow 64/64 của blueprint cũ chỉ là số liệu kế thừa; không được dùng làm PASS cho candidate mới. Khi nào có AST mới hợp lệ, phải có matched-world, goal-only, field-cue, lexical leakage và action-frequency baselines trước design GO.

Custody mới ở mức protocol: quyền nguồn/PII theo nguồn và split, custodian độc lập/2-party trust roles, canonical JSON domain-separated HMAC private AST+gold, signed ledger root, ACL denial/replay/tamper, opaque scoring IDs, unseal sau khi khóa parser/model/outputs. **CUSTODY_NOT_EXECUTED, RIGHTS_NOT_VERIFIED, PRIVATE_EVAL_NOT_CREATED, GOLD_NOT_CREATED.** Public exploratory examples không được tái sử dụng làm blind gold.

## 5. Kết luận và khuyến nghị nghiên cứu

**`HOLD_ONTOLOGY_FEASIBILITY`.** Trong phạm vi exploratory grammar hữu hạn đã duyệt không có bộ 4 OOD category nào được chứng nhận; đặc biệt `goal_persistence` không có cặp A/B distinct-first-action một fluent đạt tiêu chí. Không tự khẳng định ontology toàn cục vô nghiệm. Với yêu cầu R1 4 OOD/category và bốn category bắt buộc, **dừng sản xuất blueprint theo công thức D1 Bridge hiện hành**. Muốn tiếp tục hướng khoa học, cần thiết kế lại benchmark/ontology một cách công khai, hoặc giảm phạm vi giả thuyết theo prereg amendment riêng; không nâng source demo thành confirmatory science.

### Các gate bảo toàn

`D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `GPU=0`, `TRAINING=0`, `INFERENCE=0`, `FROZEN_V6=UNCHANGED`, `MAIN=UNCHANGED`, `lineage.md=UNCHANGED`.

## Bước thực hiện tiếp theo — duy nhất

`TTM_SMALL4M_D1_R1_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_DECISION_SINGLE_GATE`

Giao reviewer độc lập đánh giá liệu giới hạn tìm kiếm và lựa chọn prospective physical semantics có đủ thuyết phục để **đóng D1 Bridge R1 theo thiết kế hiện tại** và mở đề xuất benchmark kế nhiệm (design-only, không science permit), thay vì tiếp tục vòng sinh 32 blueprint. Nếu reviewer bác bỏ phạm vi tìm kiếm, yêu cầu một phản ví dụ *constructive* thực sự: 4 OOD/category, per-OOD canonical action-causal graph nonoverlap và matched-world witnesses, với unique oracle dưới semantics được ghi nhận. Chỉ một GO/HOLD về thiết kế; không chạy mô hình.
'''
(P/'TTM_D1_R1_MINIMAL_CONTRACT_CONSTRUCTIVE_FEASIBILITY_REPORT_20261114.md').write_text(md)
handoff=f'''# HANDOFF — TTM D1 R1 minimal semantics, constructive feasibility

**Operation:** `{OP}`\n**Source:** `d24c50ad8a9e377264dd8fa073bcc553824f8992`\n**Frozen V6:** `dd52804685d186c17e600221ffb16ce78aea12ea`\n**Verdict:** `HOLD_ONTOLOGY_FEASIBILITY`\n**Review mode:** source-only; no EVAL/gold, no science run.

Read exactly: `TTM_D1_R1_PROSPECTIVE_MINIMAL_SEMANTIC_CONTRACT_FREEZE_20261114.json`, `constructive_search.py`, `pairwise_constructive_probe.py`, both JSON receipts, 32-slot matrix, custody readiness JSON, Markdown closure.

The proposed physical co-location semantics are a **material new candidate**, not frozen V6; new status is a source-test assumption freeze only. Run independent reviewer **only to adjudicate construct validity and the bounded feasibility implication**, not re-run old QA 13/13 and 12/12. The 330-case search gives 94 unique first-action individual cases, only 32 one-fluent same-goal paired counterfactuals, and the `goal_persistence` subgrammar has **zero** such pairs. No OOD novelty is proven; no 32 new admissible ASTs were fabricated. This is NOT a mathematical impossibility theorem for full V6. Formal independent external review NOT_EXECUTED.

## Key decisions to assess
1. Is physical TRANSFER co-location a scientifically justified material amendment, or should remote transfer V6 remain authoritative?\n2. Can an acceptable nonarbitrary persistence objective yield unique oracle without hidden cost?\n3. Can a separate constructive witness supply four true OOD causal topologies/category with full 64 matrices and matched-world unique oracles?\n4. If not, recommend STOP/REDESIGN of D1 Bridge as currently formulated, not superficial relabeling.\n5. Custody remains DESIGN_ONLY. No blind EVAL/gold, rights or parser claim.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SMALL4M_D1_R1_HOLD_CLOSURE_AND_BENCHMARK_REDESIGN_DECISION_SINGLE_GATE` — one independent decision GO/HOLD for present formulation, preserving all scientific locks.
'''
(P/'TTM_D1_R1_CONSTRUCTIVE_INDEPENDENT_REVIEW_HANDOFF_20261114.md').write_text(handoff)
# manifest hashed, no self reference
paths=[x for x in P.iterdir() if x.is_file() and x.name!='TTM_D1_R1_SOURCE_PACKET_SHA256_MANIFEST_20261114.json']
manifest={'schema':'ttm.d1.r1.source_packet_sha256_manifest.v1','operation':OP,'files':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(paths)}}
(P/'TTM_D1_R1_SOURCE_PACKET_SHA256_MANIFEST_20261114.json').write_text(J(manifest))
print('FILES',len(manifest['files'])+1,'SCENARIOS',receipt['bounded_search']['scenario_total'],'PAIRED',receipt['matched_AB_one_fluent_probe']['pair_total'])
