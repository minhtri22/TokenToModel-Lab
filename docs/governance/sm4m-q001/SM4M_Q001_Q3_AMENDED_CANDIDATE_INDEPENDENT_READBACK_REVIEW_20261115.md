# SM4M-Q001 — Q3 Amended Candidate: Distinct Independent Readback Review

**Ngày:** 15/11/2026  
**Operation:** `SM4M_Q001_Q3_EXACT_AMENDED_CANDIDATE_DISTINCT_READBACK_AND_REREVIEW_SINGLE_GATE`  
**Repo:** `minhtri22/TokenToModel-Lab` · **PR:** [#21](https://github.com/minhtri22/TokenToModel-Lab/pull/21)  
**Exact amended candidate HEAD:** `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`  
**Original Q3 HEAD:** `3c53d062c7c6ff4218d80177253dd1c061ac6362`  
**Frozen baseline main HEAD:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`  
**Chế độ:** `READ_ONLY · EXACT_SOURCE_ONLY · NO_MODEL_RUN · NO_SCIENCE`  

## 1. Reviewer independence và verdict

**`PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED`** — chỉ PASS mức nhất quán tài liệu nguồn, phạm vi bằng chứng và hợp đồng admission có điều kiện. Không phải admission của bộ dữ liệu thật, không phải khoa học PASS, không xác định nguyên nhân lỗi T4, không duyệt Q4 hay merge.

Review này được thực hiện trong một phiên phân tích riêng biệt, không phải phiên tác giả Q2 hay tác giả remediation Q3. Tôi trực tiếp đọc commit pin, độc lập tính lại raw SHA-256 và chạy bộ kiểm tra logic nguồn riêng; không sử dụng kết quả author QA 60/60 như bằng chứng độc lập. Danh tính/quan hệ tổ chức của các tác giả không được chứng thực ngoài metadata GitHub.

Ba kết luận gốc được giữ nguyên: `KEEP_HISTORICAL_REFERENCE_ONLY`, `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`, `ROOT_CAUSE_NOT_IDENTIFIED`.

## 2. GitHub source custody và diff

- PR #21 ở trạng thái **Draft, chưa merge**; `main` tại `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`.
- Amended commit `c37ac0b3901eb6fd9c658d818c02e85f66b7936e` có **parent trực tiếp** `3c53d062c7c6ff4218d80177253dd1c061ac6362`; compare `ahead=1, behind=0`.
- Exact amendment có **8 path**: 7 added, 1 modified, không thay source code, `lineage.md` hoặc các bảy original-Q2 files.

| Changed path (so với original Q3) | Git blob SHA-1 | Raw SHA-256 |
|---|---|---|
| [SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json) (added) | `10d901906c24ca4a0bc93827e45982390cc18ae5` | `6e1585ef0483d4460dae9b57832c751bb9deb57e07ad231fb67cb7f04b8d1f1b` |
| [SM4M_Q001_Q3_EXTERNAL_REVIEW_INTAKE_VERIFICATION_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q3_EXTERNAL_REVIEW_INTAKE_VERIFICATION_20261115.json) (added) | `c9adc573af5c3417a3f09d80a4d456bca4d0c818` | `8b2a4b0d564e4a83a329727268b635714344fc76e64cdd4a0b5f2cbcd9f2639a` |
| [SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AUTHOR_QA_RECEIPT_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AUTHOR_QA_RECEIPT_20261115.json) (added) | `7d1538399ad74807a86d2553f9511afd65ce3aa2` | `8268f7308b0ad241ea78d18d1c324a9a7dd65a25ab523d4a4c62adb8545cd544` |
| [ACTIVE_RESEARCH_GATE.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/ACTIVE_RESEARCH_GATE.md) (modified) | `e3e096d43e2c042b2d542bcf4383d52e1328c1c2` | `f586706699434d40bcca7ae716ffb052a685dfd724c2c8c81a800475eae19e50` |
| [SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md) (added) | `cbe529125d158c535c568fbed7bcffbdc8819cca` | `1dcf30b34ea38a2a4de35c23141d84c292817f838132d17b813057fb9c20ae9f` |
| [SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md) (added) | `0b85f84cfd17ff0612291706c5d0fa36d86800c7` | `e619ea9460abd112ab32016e7644c273a6cce2d20044fe8bd0e129d18d820680` |
| [SM4M_Q001_Q3_EXACT_AMENDED_READBACK_HANDOFF_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q3_EXACT_AMENDED_READBACK_HANDOFF_20261115.md) (added) | `0f74300f920cdb78a2369345825b651ea1e23223` | `e16464da88e57aa60105335dc6820ba9dc328855eb4b4d0cb47ab329e88ffbc6` |
| [SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AND_PHASE_CONTRACT_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q3_INTEGRATED_REMEDIATION_AND_PHASE_CONTRACT_20261115.md) (added) | `735861c41c4ab793a8af385779a22ae0284976e1` | `9ddf7102b50bae0aa47d3a9d31173d5416b43fcbf84fd90a0eb72e5491bee571` |

### Bảy Q2 nguyên bản — byte custody

Độc lập đọc lại từ amended HEAD: **Git blob SHA-1 7/7 khớp**, **raw SHA-256 7/7 khớp** với owner acceptance. Đây là kiểm byte tài liệu public, không phải checkpoint/model/data private.

| Original file | Git blob SHA-1 | Raw SHA-256 | Check |
|---|---|---|---|
| [SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md) | `b289f1056a9c0bb862a4813cbf0d2189b34c233d` | `4973ad744f5d2e2e9e89f46e7890a37833c43cd99fdb82405be2148a580bce06` | PASS |
| [SM4M_Q001_AUDIT_RECEIPT_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_AUDIT_RECEIPT_20261115.json) | `74023311e224e552c46899a7547eb5f73deddc52` | `9fbfb2b185043685b5d24e352eb7b029b6fc36098f5a735cd699b9b5f2261f4a` | PASS |
| [SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_LITERATURE_TRIAGE_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_LITERATURE_TRIAGE_20261115.md) | `380582a4f1260dfda28d39e0cb56be2fc02709c5` | `34c553d10250b8403a4d2e7170ce6f0329fa14284ea5018f59de35af94622d36` | PASS |
| [SM4M_Q001_AUTHOR_ADVERSARIAL_LITERATURE_QA_RECEIPT_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_AUTHOR_ADVERSARIAL_LITERATURE_QA_RECEIPT_20261115.json) | `c984ca474c112494bfe472d4293c2da7e4a6eefb` | `5254fbb557c2074d95d7aa65e14e6c2924e8da1979e12f6fe4b1340958303a65` | PASS |
| [SM4M_Q001_Q2_CAUSAL_EVIDENCE_ADMISSION_LOCK_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_ADMISSION_LOCK_20261115.md) | `d82202778fe3bc620335af18b0fa7ea1fec4094c` | `b34ad81e81e90ba5873cb1c8207592f8b078023aba60f2e57cd7ef1229376a8e` | PASS |
| [SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json) | `b7e87dbdd31c6624387f9943d7ff7db8efa8663a` | `306d32086fa1e19a910070577e0f9fbd7d0a130d792ff225e1f35768237a105b` | PASS |
| [SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_RECEIPT_20261115.json](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_RECEIPT_20261115.json) | `a3a22b0cc8515979c9034d02e497ecf8f7b1fee4` | `ed0bc795c3d129cdf4c99761f96cb04888a0c9cebfb83010c0463c712be4e403` | PASS |

- Original Q3 report Markdown: raw SHA-256 `e619ea9460abd112ab32016e7644c273a6cce2d20044fe8bd0e129d18d820680` — **PASS**.
- Original Q3 JSON receipt: chỉ có digest đã tuyên bố `529490652a7f140153292ec090496c1b5deec8ca36f54b25aa5b63c98cbd08ba` và derived intake trên GitHub. ZIP reported SHA-256 `816938d1d08479947c21206b6eeacc41da43c07abc29ac42dc31b0a844ae089d`; không có ZIP nguyên byte để independently rehash. **NOT_VERIFIED_FROM_GITHUB**; không mạo nhận derived intake là original.

## 3. Findings — exact source/lines

### Q3-F01 (HIGH): PASS — [`artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json`](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json)

- `conditions_before_authoring` tại **L421–429** có `AD-03`, `AD-06`; `conditions_before_freeze` tại **L460–468** lặp lại các điều kiện, trước model run hoặc scoring.
- `conditions_before_scoring` tại **L430–438** chỉ cho `AD-03_RECHECK_NOT_FIRST_APPEARANCE` và `AD-06_RECHECK_NOT_FIRST_APPEARANCE`; các stop rules tại **L491+** chặn authoring/freeze.
- Negative symbolic checks chứng minh hidden-only gold và thiếu cặp đổi một biến bị từ chối **ngay trước authoring và freeze**. Programmatic oracle riêng yêu cầu preregistered contract, provenance và equal information budget; không đưa hidden metadata vào rater-visible gold.

### Q3-F02 (HIGH): PASS — [`docs/governance/ACTIVE_RESEARCH_GATE.md`](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/ACTIVE_RESEARCH_GATE.md)

- L9–31 có một Q001 active state: Q2 author frozen/owner scope accepted; Q3 HOLD awaiting rereview, Q4 not decided; `main_sync` vẫn blocked.
- L48–53 chỉ có một current next step. Không còn hai bước cạnh tranh hoặc old `Q2_NOT_COMPLETED`/`Q3_NOT_REVIEWED` ở active register. Trạng thái đề xuất PR được phân biệt rõ với `main` thực tế.

### Q3-F03 (MEDIUM): PASS — [`artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json`](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json)

- L12–42: `AD-01R` rights trước unauthorized content access/production authoring; `AD-01T` exact tokenizer/split trước token-sensitive item freeze; `AD-01C` checkpoint byte trước bất kỳ model execution nào.
- Cả ba subconditions `NOT_VERIFIED_IN_Q2` và chỉ thuộc **một AD-01 staged contract**, không phát sinh ba new permits. Pure read-only design vẫn hợp lệ mà không cần truy xuất private checkpoint.

### Q3-F04 (LOW): PASS — [`docs/governance/sm4m-q001/SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md`](https://github.com/minhtri22/TokenToModel-Lab/blob/c37ac0b3901eb6fd9c658d818c02e85f66b7936e/docs/governance/sm4m-q001/SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md)

- L68 P05 sửa đúng thành **“Maximization-based decoding”**. Bản original Q2 vẫn exact, và kết luận `decoder-only rescue` bị suy yếu dưới D1 EXP32 vẫn không đổi.

## 4. Independent symbolic adversarial source checks

Reviewer định nghĩa logic kiểm tra phase từ các mảng machine-readable và đối chiếu 18 điều kiện/fixture. **18/18 PASS**, trong đó gồm 9 negative cases, 2 positive hypothetical cases, 7 phase invariants.

| Loại fixture | Stage | Kết quả mong đợi / quan sát |
|---|---|---|
| Gold hidden-only | BEFORE_AUTHORING + BEFORE_FREEZE | REJECT / REJECT |
| No valid one-variable pair | BEFORE_AUTHORING + BEFORE_FREEZE | REJECT / REJECT |
| Unauthorized source rights | BEFORE_AUTHORING | REJECT / REJECT |
| Tokenizer/split not verified (token-sensitive) | BEFORE_FREEZE | REJECT / REJECT |
| Checkpoint bytes unavailable | BEFORE_MODEL_EXECUTION | REJECT / REJECT |
| Owner Q4 authority absent | BEFORE_AUTHORING | REJECT / REJECT |
| Rater calibration absent | BEFORE_SCORING | REJECT / REJECT |
| All hypothetical conditions true | BEFORE_AUTHORING | ACCEPT-CONTRACT / ACCEPT-CONTRACT |

**Giới hạn:** Những case này là symbolic negative-fixture tests đối với contract tài liệu, không phải fixture trong dataset, không kiểm runner implementation, model, gold thật hay thực thi khoa học.

## 5. Regression và admission status

- `source_outcomes`: **10/10 giống nguyên bản** (T4 VAL/TEST64; FRESH12; FRESH16 V2; CF1 DEV36; D1 EXP32; A/C FINAL24; H-DATA-S1; FC01; D1 R1).
- `causal_hypotheses`: **7/7 giống nguyên bản** (`H-METRIC`, `H-OBJECTIVE`, `H-DATA`, `H-DECODER`, `H-CONTEXT`, `H-CAPACITY`, `H-IMPL`).
- `source_pins`, 13 `literature_sources` và `input_files_sha256`: exact semantic comparison unchanged.
- `AD-00..AD-08` **9/9 original status unchanged**. AD-00 `PARTIAL_PUBLIC_SOURCE_MATCHED`; AD-01/02/03/04/05 still NOT VERIFIED; AD-06 NOT_EXECUTED; AD-07 NOT_FROZEN; AD-08 original historical Q2 status `Q3_AND_Q4_NOT_COMPLETED`. Không có điều kiện nào được công nhận admission PASS.
- `AD-01R/T/C` đều chưa xác minh. AD-03 source-visible witness và AD-06 matched one-variable/equal-budget vẫn thiếu dữ liệu sản xuất và chưa admission. Không sửa nguyên trạng lịch sử, không cấp quyền Q4, gold hoặc science.

**Lưu ý giải thích dữ liệu:** trong v2, các trường `boundaries.Q2/Q3` và `terminal_disposition.independent_review` vẫn sao chép status theo *thời điểm Q2 gốc*, không phải current active register. Trường `remediation_provenance.current_q3_governance_context`, `remediation_state`, và `ACTIVE_RESEARCH_GATE.md` mô tả trạng thái phát sinh sau đó. Downstream readers không được đọc các trường historical này như live status. Đây là caveat, không phải trở ngại F02 còn lại vì canonical active register đã nhất quán.

## 6. Quyết định và hard boundaries

**Một verdict:** `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED`.

`root_cause_identified=false`; `science=false`; `model_inference=false`; `training=false`; `gpu=false`; `new_gold=false`; `scorer=false`; `test_final_replay=false`; `new_research_branch=false`; `code_patch=false`; `lineage_change=false`; `owner_Q4_decision=false`; `merge=false`.

PASS chỉ xác nhận remediation source/design timing + governance consistency. **KHÔNG** mở baseline cho science, không chốt root cause, không làm F0–F2, và PR #21 vẫn Draft chưa merge.

**Bước thực hiện tiếp theo — duy nhất:** owner xem xét **Q4 closure và quyết định merge GO/HOLD cho PR #21** trong một lượt, trên exact reviewed HEAD; không tự merge, không cấp permit khoa học. Nếu owner giữ HOLD thì bảo toàn nguyên các bằng chứng và nhánh hiện tại.

**Machine receipt:** `SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_RECEIPT_20261115.json` · SHA-256 `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f`.

**Publication:** hai output được tạo độc lập ở working container, **chưa đưa lên GitHub** vì handoff quy định `READ_ONLY`, không thay đổi PR/commit. GitHub vẫn là nguồn sự thật cho tất cả input evidence.
