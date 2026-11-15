# TTM-Small-4M Foundation First — Owner Integrated Design Adjudication

**Ngày quyết định:** 2026-11-15
**Operation:** TTM_SMALL4M_FOUNDATION_FIRST_F01_F05_OWNER_INTEGRATED_DESIGN_ADJUDICATION_SINGLE_GATE
**Owner decision:** ACCEPT_GO_DESIGN_SCOPED_CLOSE_F01_F05
**Scope:** DESIGN_ONLY · SCIENCE_HOLD · NO_GPU · NO_TRAIN · NO_INFERENCE · NO_MERGE
**Nguồn quyết định:** owner xác nhận rõ trong cuộc trò chuyện: chấp nhận GO_DESIGN_SCOPED để đóng năm finding ở đúng phạm vi. Đây là bản ghi quyết định của owner theo hội thoại, không phải chữ ký số, không phải chứng thực độc lập của con người cho kết quả khoa học.

## A. Source of truth & exact reviewed candidate

- Repository: https://github.com/minhtri22/TokenToModel-Lab
- Baseline main (frozen reference): fbe4a1ed58eef66f896bbfe0471926b7cc45298e
- Candidate trước sửa (HOLD): 4c97f2b1d1836b31d55b649e78a8b69fecc44482
- Exact remediation candidate được reviewer độc lập đánh GO: 97731311ba2fc3a8000c2532bd4e5a0470c437ba
- Nhánh lưu closure: research/ttm-small4m-foundation-first-single-gate-20261115
- Review operation: TTM_SMALL4M_FOUNDATION_FIRST_F01_F05_DISTINCT_INDEPENDENT_REMEDIATION_REVIEW_SINGLE_GATE
- Original independent verdict at old candidate: HOLD_REVISE_DESIGN; giữ nguyên lịch sử, không hồi tố ghi đè.
- Re-review verdict at remediated candidate: GO_DESIGN_SCOPED, independent AI source/design review; NOT human/clinical/legal attestation and NOT science GO.

## B. Owner adjudication — five findings, one integrated decision

| Finding | Reviewer severity | Owner closure | Phạm vi giới hạn |
|---|---|---|---|
| SM4M-IR-F01 | HIGH | CLOSED_DESIGN | M0 gốc chỉ kiểm cực tính 111/000; tám pattern riêng actor/object/goal vẫn là thiết kế prospective, semantic isolation và gold chưa kiểm chứng |
| SM4M-IR-F02 | HIGH | CLOSED | A/C mean A=C=0.6667/3, delta=0; không đồng nhất với H-DATA H0=H1=0/3 |
| SM4M-IR-F03 | MEDIUM | CLOSED | H-DATA 24 pairs, 48 continuations, 144 primary axis-scores đều 0, 240 total axis-scores; 144 không phải số trường hợp độc lập |
| SM4M-IR-F04 | MEDIUM | CLOSED_DESIGN | M0 TP/TN≥28/32 mỗi trục/rater, agreement≥0.85; proposed matches≥55/64 và custody vẫn chặn ở preexec |
| SM4M-IR-F05 | LOW | CLOSED | FRESH16 S1=32 outputs, S2=16 counterfactual pairs; không có inter-rater agreement trên shared items |

**Owner integrated decision:** chấp nhận reviewer GO_DESIGN_SCOPED và đóng đúng năm finding tại phạm vi thiết kế, không tuyên bố tìm ra root cause. Phán quyết reviewer trước HOLD vẫn là lịch sử chính xác của candidate cũ. Không có science execution hoặc metric được tạo mới.

## C. Independent audit evidence — committed raw-byte preservation

Source attachment SHA-256 đã tính từ tệp owner cung cấp; khi tạo Git blobs, từng Git blob SHA-1 khớp với hash Git tính từ chính raw attachment bytes. Không giả định SHA-1 là SHA-256, không có private checkpoint/data custody mới.

- ORIGINAL_HOLD_REVIEW_REPORT (HOLD_REVISE_DESIGN): docs/research/ttm-small4m-foundation-first/reviews/TTM_SMALL4M_FOUNDATION_FIRST_DISTINCT_INDEPENDENT_REVIEW_20261115.md — SHA-256 3113f5b7c38e794de0504c859bdc0c0ee63d9fe5b285b2c9f29eb2ca194c84f4; Git blob SHA-1 2bb77049ae4a3082d5c0a2e05a403e60b9b135ea.
- ORIGINAL_HOLD_REVIEW_RECEIPT (HOLD_REVISE_DESIGN): artifacts/research/ttm-small4m-foundation-first/reviews/TTM_SMALL4M_FOUNDATION_FIRST_INDEPENDENT_REVIEW_RECEIPT_20261115.json — SHA-256 e8bc21c533d46d3212fd8bac779d4e5e01ab8e906decce208261def2548158ef; Git blob SHA-1 1080797cd6056a144efe2cd3f2a8e3621a9a9298.
- REMEDIATION_GO_REVIEW_REPORT (GO_DESIGN_SCOPED): docs/research/ttm-small4m-foundation-first/reviews/TTM_SMALL4M_FOUNDATION_FIRST_F01_F05_DISTINCT_REMEDIATION_REVIEW_20261115.md — SHA-256 673dc3df32fce8d795d48a536c6de9c3e0ee683dc7e0615a7911b584f9d1bf73; Git blob SHA-1 aaaead20b51a1c1e753d7805005105e197ee6af7.
- REMEDIATION_GO_REVIEW_RECEIPT (GO_DESIGN_SCOPED): artifacts/research/ttm-small4m-foundation-first/reviews/TTM_SMALL4M_FOUNDATION_FIRST_F01_F05_INDEPENDENT_REVIEW_RECEIPT_20261115.json — SHA-256 1cb661ac4af314c0ac77c3d450eea52013cd0549e2ef053496174683119f4fb8; Git blob SHA-1 fe60dc041a1efd5f0240cf51d848db2cd579bad7.

## D. Không cấp quyền cho F2 execution hoặc nghiên cứu khác

- SM4M-F0: PASS_SOURCE_SCOPED (architecture blob unchanged); SM4M-F1: remediation accepted; SM4M-F2: GO_DESIGN_SCOPED_ONLY, M0_EXECUTION=NOT_AUTHORIZED, PREEXEC_BLOCK=TRUE.
- SM4M-F3=NOT_OPENED; SM4M-F4=NOT_OPENED; ROOT_CAUSE_IDENTIFIED=NO; OWNER_SCIENCE_GO=NOT_GRANTED.
- M0 gốc 32 positives/32 negatives, hai blind raters, sensitivity/specificity ≥28/32 từng rater/từng axis, agreement ≥0.85 từng axis — không thay MD1.
- Prospective per-axis/partial/ambiguous design chưa có data, gold, sample allocation, negative-control acceptance, nguồn rights/PII, anti-shortcut verification, scorer custody, signed frozen contract hoặc owner execution permit.
- No GPU, no inference, no training, no TEST/FINAL re-use, no result re-score, no checkpoint/data change, no PR/merge.
- EmbeddingGemma 2 và Vector Memory tiếp tục độc lập; mọi HOLD/FAIL/PASS trước đó bảo toàn, không đưa donor/retriever/Reader vào Small-4M.
- TTM PR #20 có F01–F04 riêng về governance/inventory, không phải năm finding Small-4M này; không tự adjudicate hoặc merge PR #20.

## E. Append-only lineage & governance integration

- Đã tạo closure record và giữ nguyên bốn independent review evidence blobs. Không sửa hoặc xóa historical evidence.
- lineage.md ở branch Foundation First và main baseline vẫn giữ nguyên: main đang đến L0028; PR #20 Draft trên nhánh khác đã dùng L0029. Không tự tái sử dụng ID L0029 hoặc sửa main, tránh lineage ID collision.
- Khi owner cho phép governance integration, thực hiện một phép hợp nhất append-only có kiểm toán source refs để đặt một global lineage ID duy nhất cho closure này. Không hiểu việc deferred integration là thiếu owner decision: closure đã được ghi tại đây.

## F. Bước thực hiện tiếp theo — duy nhất

Chỉ khi owner muốn chuyển sang F2: xem xét một gói thiết kế tiền thực thi prospective M0/axis-specific với frozen scoring/gold/anti-shortcut/rights/independent QA; vẫn không được dispatch khoa học cho đến khi có một quyết định GO riêng. Hiện tại gate owner adjudication này kết thúc ở DESIGN_CLOSED, SCIENCE_HOLD.

**Terminal:** OWNER_DESIGN_ACCEPTED · F01_F05_CLOSED_SCOPED · M0_PREEXEC_BLOCK · F3_F4_NOT_OPENED · LINEAGE_GLOBAL_INTEGRATION_DEFERRED · SCIENCE_HOLD · MERGE_NOT_AUTHORIZED.
