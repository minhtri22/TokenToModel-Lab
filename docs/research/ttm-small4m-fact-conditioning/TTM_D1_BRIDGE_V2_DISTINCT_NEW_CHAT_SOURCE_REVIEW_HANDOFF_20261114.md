# HANDOFF — D1 Bridge V2 / distinct AI source-only science review

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`  
**Ngày:** 14/11/2026  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Review frozen input HEAD:** `750533c1c2945594d827c886aaa275c49fb980d7`  
**Vai trò:** Independent AI Scientific Design Reviewer (agent AI ở phiên khác).  
**Chế độ:** `READ_ONLY / NO_GPU / NO_TRAIN / NO_EVAL_GOLD / NO_PRIVATE_MAPPING / DESIGN_ONLY`.  
**Tiền đề:** V1 có independent AI review `HOLD_REVISE_BEFORE_PREREG`; V2 là **sửa đổi nguồn triển vọng**, **chưa** đủ điều kiện science GO.

## 1. Đọc nguồn đúng pinned commit, đối chiếu Git blob

| Input | Git blob SHA-1 | Link |
|---|---|---|
| V2 AM01–AM06 source/design MD | `354291ec54803bd9764728ee858abd83a71ca4b6` | [V2 MD](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_SINGLE_PACKET_AM01_AM06_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md) |
| V2 machine JSON | `66ce607eb13e4c64994fecd4a40a2c3da94d19dc` | [V2 JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_AM01_AM06_SINGLE_PACKET_PREREG_DESIGN_HOLD_20261114.json) |
| V2 self-authored QA source JS | `7ee503f19613899ecd9bbe788dd995ad10415575` | [QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/tools/pilot_t4/fc01/ttm_d1_bridge_v2_source_only_contract_qa_20261114.js) |
| V2 scoped QA receipt | `2f468a743b3e44ef5d307810b70ab74000ce0a61` | [QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_SINGLE_PACKET_SOURCE_ONLY_QA_AND_HOLD_20261114.json) |
| Independent V1 review Markdown | `8fd942d60e79e5b78cc342505d92a4dbcaefc540` | [Review MD](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md) |
| Independent V1 review JSON | `580e7269f66e900b8fe40584fd73d5ce0f001566` | [Review JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json) |
| lineage.md L0017 | `34a59b7ee76bf6cab5a7abfcdf687a38a6dc3d7d` | [Lineage](https://github.com/minhtri22/TokenToModel-Lab/blob/750533c1c2945594d827c886aaa275c49fb980d7/lineage.md) |

Nếu không thể mở đủ nguồn hoặc blob không khớp, báo `HOLD_SOURCE_UNAVAILABLE`, không suy đoán. Các mã trên là Git blob SHA-1; SHA-256 nguyên báo cáo V1 `7369882b5615785628bd93b006157423f2b8377e265e3c3098429eabd60ab97c`; biên nhận V1 `21c1e07b13ce1cd39d77200247b5f1a6c9fbbd49fffa7f90821c9a429f28034b`.

## 2. Phản biện V2 theo AM01–AM06 (PASS/HOLD/FAIL và mức rủi ro mỗi trục)

**AM01 / R1:** Typed AST + finite action-table semantic equivalence có thật sự bắt được đổi tên, đảo điều kiện, ưu tiên, negation, time-order? Phân biệt `semantic AST equivalence` với `same final action` — hai cấu trúc khác quy trình có thể trùng outcome hữu hạn. Cần quy tắc finite-state coverage, UNCERTAIN→HOLD, khả năng tạo 4 OOD skeleton/category thật sự độc lập. Không công nhận non-overlap PASS khi data/checker chưa tồn tại.

**AM02 / R2:** Oracle gold A/B có phân biệt thật và duy nhất? Typed action grammar đo đúng hành động hay chỉ khả năng khớp công thức do prompt gợi ý? Đánh giá chính sách synonyms, negation, quoted answers, multiple actions, EOS/truncation, prompt≤224 + new≤32 bao gồm special tokens. Đề xuất các adversarial fixture **nguồn-only, không dùng EVAL**; độ nhạy/đặc hiệu parser chưa kiểm.

**AM03 / R3:** Đã thay 5-seed sign-flip bằng **12-seed one-sided exact sign test** với k≥10, p(k≥10)=79/4096; kiểm độc lập bảng k=9,10,11,12 và sensitivity q=.7/.8/.9. Kiểm null `P_training_rng(d_s>0)≤.5`, điều kiện các PRNG streams độc lập, fixed seed list và ý nghĩa scientific claims; **không** coi exact sign test kiểm định `mean effect≥+.10` — +10pp vẫn decision gate mô tả. Kiểm crossed resampling: cùng skeleton và lexical families ở 12 seed, không bootstrap skeleton riêng từng seed; n=4 skeleton/category. Power total science gate có thể rất thấp, tính toán minh họa phải ghi rõ không dùng FC01.

**AM04 / R4:** Kiểm category rules `4/4 Δ≥0, 3/4 Δ≥+.05, C absolute≥.25`, pilot-informed threshold provenance, thứ tự `HOLD_INVALID_PROTOCOL` trước outcome, effect gate +10pp chỉ mô tả; có còn false positives do vài lexical worlds/skeleton dễ?

**AM05 / R5:** ACL chỉ là bảng role; chưa có chứng cứ key/permissions thực. Đánh giá thiếu hụt route leak từ pretrained parent TinyStories, grammar, AST normalizer, parser, condition/gold cues, logs. Chiến lược độc lập source QA có tránh custodian đọc TRAIN/owner thấy sealed EVAL? Không đọc private thật.

**AM06 / R6:** Thiết kế tăng từ 15 lên **36 arm-runs** (9.216 steps; 18.432 generations). Kiểm Free T4/paid $0 có thực tế không, C contrast objective có extra forward/negative exposure khác B, thế nào là controlled objective-only và đâu là equal-token/updates chứ không equal-FLOPs? Checkpoint resume sau **nonzero AdamW moments**, RNG, scheduler, sampler, atomic restore, fail-closed negative corrupt cases. Không tự cấp khoa học GO.

## 3. Phạm vi và sự độc lập

- Không tin `SOURCE_ONLY_QA_44/44` và 9/9 negatives tự soạn là độc lập; đọc code, kiểm trường, tìm sai logic. Checker chỉ chặn tampering của JSON spec chứ **không** kiểm AST/parser runtime.
- Không dùng kết quả FC01 exploratory để chỉnh threshold hoặc dựng outcomes D1. Không chạy GPU/inference/training, không tạo TRAIN/EVAL/gold, không mở TEST/Q1Q2 hoặc mapping, không sửa V1/V2/lineage/main.
- Reviewer ở **chat tách biệt** và tự khai báo mức độc lập; không khẳng định human review hay external identity verification.

## 4. Output duy nhất của lượt review

Xuất báo cáo `TTM_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_20261114.md` và máy `TTM_D1_BRIDGE_V2_DISTINCT_AI_REVIEW_RECEIPT_20261114.json`. Mỗi AM01–AM06 phải có verdict, evidence ref, issue-ID, mức CRITICAL/HIGH/MEDIUM/LOW, đề xuất *must-fix*, và khả năng thay đổi V2 nếu cần — **mọi sửa đổi phải thành V3, không overwrite V2**. Báo cáo phải nói rõ `AST_NONOVERLAP=NOT_EXECUTED`, `PARSER_RUNTIME_QA=NOT_EXECUTED`, `FREE_T4_FEASIBILITY=NOT_VERIFIED` nếu không có byte chứng cứ thật.

**Một quyết định cuối về thiết kế:** `GO_DESIGN_ONLY` / `HOLD_REVISE_BEFORE_PREREG` / `FAIL_INVALID_DESIGN` / `HOLD_SOURCE_UNAVAILABLE`; còn `D1_SCIENCE_RELEASE=HOLD` trong mọi trường hợp.

Kết thúc bằng đúng một **Bước thực hiện tiếp theo** cho owner. Không micro-permits.

**Bắt đầu source review ngay khi nhận**, không cần thủ tục accept riêng. 
