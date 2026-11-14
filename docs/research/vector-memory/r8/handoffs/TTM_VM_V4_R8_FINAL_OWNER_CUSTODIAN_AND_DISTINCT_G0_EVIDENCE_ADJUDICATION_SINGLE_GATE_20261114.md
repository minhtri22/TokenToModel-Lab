# HANDOFF CUỐI — TTM VM V4 R8 · Owner G1 + Custodian G2 + Distinct Reviewer G0

**Operation:** `TTM_VM_V4_R8_FINAL_OWNER_CUSTODIAN_AND_DISTINCT_G0_EVIDENCE_ADJUDICATION_SINGLE_GATE`  
**Ngày:** 2026-11-14  
**Nhiệm vụ:** Một lượt tổng hợp chứng cứ cuối để trả đúng **một** quyết định `GO_R8_D_CANDIDATE_AUTHORING_ONLY` hoặc `HOLD_INTEGRATED`. Không mở V5/V6, micro-permit hay chuỗi handoff tiếp theo.  
**Người nhận:** Reviewer AI **khác người đã triển khai F02/F03**; reviewer có quyền kiểm toán nguồn công khai, nhưng **không được tự nhận là owner hoặc private custodian**.
**Mode:** G0/G1/G2 evidence readback; `NO_R8_GENERATION`, `NO_CAL`, `NO_TEST`, `NO_READER`, `NO_GPU`, `NO_PROBE256`. Không tự cấp giấy phép triển khai khi chưa có chứng cứ.

## 1. Source-of-truth (khóa theo commit, không dùng HEAD trôi)
- Repo: `minhtri22/TokenToModel-Lab`.
- Frozen scientific V4 design: `b8410d9c1f77a733036e980b567de73c316f8725`.
- Historical source QA 37/37 at `cf38f8792253fe106cbb6a641f189882fb96e9d5`, GitHub Actions [43573016701](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701); KHÔNG chạy lại.
- Prior AI independent G0/G1/G2 HOLD finding: report commit `21724303b68e08ab3dcc8cb7dd59feea444f8a1e`, including F02 branch ordering and F03 unrestricted categorical values.
- **Final F02/F03 source correction**: `b77bc04a511fa9d98ba70314df84c62a3af0500b`; exactly four files changed: `docs/research/vector-memory/r8/integrated_closure/gold_contract.py`, `restricted_oracles.py`, `test_g0_f01_f03_targeted.py`, and `docs/research/vector-memory/r8/R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json`.
- **Focused QA**: GitHub Actions [43577175641](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43577175641); `completed/success`, `head_sha=b77bc04a511fa9d98ba70314df84c62a3af0500b`, 18 current targeted regressions + 2 prior affected assertions = `20/20 PASS`; only non-R8 symbolic fixtures. QA classified `SAME_AGENT_SEPARATE_CHECKER`, not G0 independent.
- **Last closure report commit**: `7d5b807d22a7dfdf1a9a36548496638187806c7b`. Exact path `docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_V4_F02_F03_ONE_PACKET_INTEGRATED_CLOSURE_20261114.md`. That commit only adds the report, not code.
- Source SHA-256 from focused CI: `gold_contract.py=e1cdb9973c23d35ad99eebd32a3f38e681bdae5e17132e27319672593b785fb6`, `restricted_oracles.py=c9b08238703088e60c7873f951814e579518d0bee183e2ceb85a681ca7b1b4d3`, `test_g0_f01_f03_targeted.py=9a8c6da952f722d128c573ab578cb30e830c72aebbbcf16d153ac739434803af`, `test_integrated_source_only.py=e4402b825eba932c6ae5a0e3054a1cafe85d835c645be7d80df2a6b10c3f811f`.
- G1/G2 baseline: `docs/research/vector-memory/r8/integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json` (source commit `b77bc04a...`), still `PENDING/NOT_ATTESTED/NOT_VERIFIED`. **Template ≠ approval**.

## 2. G0 — Reviewer độc lập kiểm tra mã thật, chỉ một lượt
Review trực tiếp `gold_contract.py`, `restricted_oracles.py`, danh mục O3 trong JSON, và `test_g0_f01_f03_targeted.py` tại `b77bc04a...`. Không chấm chỉ theo tuyên bố của implementation agent; đối chiếu source + tests + CI + V4 semantic requirements:
1. **F01 (bảo toàn):** `_o1_features` dùng row-position decile, card count và order extrema; **không** dùng key length/metadata. O2 được phép kiểm metadata riêng.
2. **F02 (đã sửa, cần thẩm định):** `resolve()` xem xét verified, time-valid, *equal-rank* `DEFEATER` / `NEGATIVE_RECEIPT` **trước** nhánh thiếu CORE; trả `INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT`, không gán gold ABSTAIN. Dependency cycles/missing proof refs phải là INVALID_FIXTURE; valid missing premise hoặc superior negative là ABSTAIN theo contract. Kiểm tra hai test mới khi thiếu `AUTHORIZED`, cả negative với equal authority, và test old `test_08`/`test_10`.
3. **F03 (đã sửa, cần thẩm định):** `O3_CATEGORICAL_ENUMS` đóng kín `status`, `authority_role`, `source_format`; `_o3_features` và `validate_split` đều chặn giá trị identifier ngoài enum **trước model.fit**. `markergram` chỉ dùng từ nằm trong marker set. Đối chiếu mã với JSON contract, kiểm missing/normalize behavior, và bộ negative enum injection.
4. **B03/B04/B05 continuity:** G_pre blueprint / G_post case IDs và twins, no cross-fold repartition, O5 TRAIN-only + OOF warning và Holm scoped, R8-D exploratory descriptive only. Không suy ra `NO_LEAKAGE_PROVEN` từ không bác bỏ null. Nêu **bất kỳ** sai lệch vật chất mới thấy được, không tự sửa và tự chấm PASS trong cùng reviewer trace.
5. **Kết luận G0:** `PASS_INDEPENDENT_SOURCE_PROTOCOL_SCOPED` nếu thật sự không còn mismatch material trong phạm vi source/prereg; nếu còn thì `HOLD` với đường dẫn/function/line và counterexample. Một AI reviewer khác phiên làm code là independent AI source review, **không phải human peer-review, không phải R8 scientific execution**. Không yêu cầu chạy lại QA 37 hoặc 20 khi SHA unchanged.

## 3. G1 — Một quyết định owner hợp lệ, không ký thay
**Owner** phải chủ động xác nhận/khước từ đủ bốn điểm bằng một biên nhận có thể quy trách nhiệm (scope, date, provenance):
- Objective: `ADOPT_R8_D_DESCRIPTIVE_ONLY` hoặc `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO`. Với 32 pairs, lựa chọn R8-C confirmatory nghĩa NO-GO cho candidate này.
- Blind raters: `FOUR_RATERS_TWO_PER_CASE` hoặc `TWO_RATERS_DISJOINT`. Proposal 4 raters tạo 128 ratings cho 64 cases, mỗi rater 32 cases; không ai được xem cả hai twins của cùng pair. Chưa được mở chat rater.
- Synthetic toy domain `P-REC-V1` và one-key `SELECT/ABSTAIN` semantics: explicit approve/reject.
- Source authorization: `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY`, rights/provenance, phạm vi sử dụng và PII/privacy controls, cùng owner identity/authority/date.
Không dùng AI reviewer làm người phê duyệt. Không có owner receipt thì `G1=HOLD_OWNER_NOT_ATTESTED`.

## 4. G2 — Private custodian xác minh điều kiện trước sinh, không yêu cầu gold chưa tồn tại
Custodian **có quyền thực tế** phải kiểm tra kho private và quyền truy cập/ACL, retention/access policy, sentinel **non-R8** read/write/readback có SHA-256 thực, quy định bảo vệ/kiểm soát HMAC key, và exact source/validator/runtime lock theo corrected SHA. Dùng quyền truy cập đã được cấp, không tự đoán một private path, không tạo/dùng R8 gold. Public report chỉ đưa non-secret PASS/HOLD và hashes source/sentinel cho phép; tuyệt đối không công khai private locator, ACL nhạy cảm, secret, private gold hoặc key-to-pair mapping.
`R8=NOT_GENERATED`: không đòi pre-generation SHA của gold R8. Khi G3 được cấp phép, việc xác nhận byte gold/candidate và packet là bước hậu sinh riêng trước G4/G5.
Không có custodian receipt xác minh độc lập => `G2=HOLD_PRIVATE_CUSTODY_NOT_VERIFIED`.

## 5. Một adjudication cuối
- **GO:** `GO_R8_D_CANDIDATE_AUTHORING_ONLY` **iff** G0=PASS nguồn/giao thức phạm vi đã khóa; G1=PASS vì owner chọn R8-D, phê duyệt domain, rater, rights/PII; G2=PASS private preflight/source-lock và không có blocker còn lại. GO chỉ là tính sẵn sàng cho một one-shot **candidate authoring sẽ được thực hiện riêng sau**; không tự sinh R8, không CAL/threshold/TEST/PROBE/Reader/GPU.
- **HOLD:** `HOLD_INTEGRATED` khi một trong ba gate chưa có chứng cứ hợp lệ; đưa đúng một danh sách chứng cứ còn thiếu, phân vai rõ, không mở loop handoff tiếp.
- Quyền khoa học: giữ `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `Reader=0`, `GPU=NO`, `PROBE256=SEALED`.

**Deliverable:** ONE public-safe independent G0/G1/G2 adjudication report. Nếu được giao ghi evidence GitHub, chỉ thêm **một** report final, đọc lại commit/byte SHA và không chạm nguồn đã kiểm thử. Nếu owner/custodian evidence chưa có, vẫn phản hồi `HOLD_INTEGRATED` đúng sự thật, không dựng biên nhận giả. Không tạo thêm handoff, branch, phần mềm, blind rater chat hoặc micro-permit. 
