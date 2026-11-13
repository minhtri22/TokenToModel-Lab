# TTM Vector Memory V4 — Nguồn, quyền sử dụng, ứng viên CPU, CAL/PROBE

**Operation:** `TTM_VM_V4_CAL64_PROBE256_SOURCE_RIGHTS_ANNOTATION_CANDIDATE_PIN_AND_INTEGRATED_SOURCE_QA_ONEPACKET`  
**Date:** 2026-11-13. **Release:** `HOLD_OWNER_RIGHTS_MODEL_BYTES_CAL_THRESHOLD_AND_PROBE_CUSTODY`.  
**Scope:** source-only; no V4 science, Reader, GPU or sealed TEST. V2/V3 one-shot consumed, lineage L0023 and main unchanged.

## Nguồn đã xây dựng

- `tools/research/vector-memory/v4_fixed_retrieval_calibration.py`: BM25, Unicode char-3gram TF-IDF, pinned T1/P02 mean cosine wrapper, BGE pretrained semantic candidate, frozen single-threshold CAL optimization.
- `tools/research/vector-memory/v4_source_rights_annotation_custody.py`: quyền nguồn, case schema, CAL/PROBE disjoint-family, blind AI reviews và private trace có **selected_key thật**.
- `tools/research/vector-memory/v4_independent_source_mock_qa.py`: 60 điều kiện source/negative QA được viết, chỉ dùng mock trong RAM, chưa chạy trên Windows ở thời điểm đóng gói.
- `tools/research/vector-memory/Invoke-TTM-VM-V4-Source-Only-OnePacket-QA-PS51.ps1`: kiểm Git blob và chạy Python 3.12 mock QA một lượt, không có science dispatch.
- `artifacts/research/vector-memory/TTM_VM_V4_SOURCE_RIGHTS_CUSTODY_OWNER_TEMPLATE_20261113.json`: mẫu trống, **không phải bằng chứng được cấp quyền**.
- `artifacts/research/vector-memory/TTM_VM_V4_BGE_SMALL_UPSTREAM_CANDIDATE_AND_BASELINE_SOURCE_PIN_20261113.json`: pin model và baseline, trạng thái bytes owner chờ xác minh.

Model được chọn trước khi biên soạn CAL: **`BAAI/bge-small-en-v1.5`**, tiếng Anh, MIT, ~33.4M parameters. Revision upstream bất biến `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, file `model.safetensors` SHA256 `3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad`. Nguồn: https://huggingface.co/BAAI/bge-small-en-v1.5 . **Chưa kiểm các byte trên Windows; tokenizer/config SHA chưa khóa local.** `LocalBGE` chỉ đọc local files, kiểm SHA, CPU FP32 2 threads, CLS pooling + L2, không download lúc science và không train.

## Chính sách quyền, tác giả và thẩm định

CAL/PROBE chỉ được biên soạn từ (1) nội dung English owner-authored có owner attestation thật, hoặc (2) nguồn được cho phép sử dụng với license/permission receipt thật. Không tự suy ra rights từ URL công khai; không PII. Nếu source chỉ do owner biên soạn thì kết luận chỉ là authored naturalistic, không tuyên bố web-scale retrieval.

Độc lập theo bốn trục: `source_document_cluster`, `entity_family`, `author_style`, `paraphrase_family`. Không dùng V2/V3 PROBE để chọn ngưỡng; sealed TEST tuyệt đối không đọc. Hai AI phiên riêng chấm mù tất cả case CAL và PROBE ở từng thời điểm đúng, phân loại `AI_ASSISTED_EXPLORATORY` chứ không tuyên bố human. Mỗi packet có question + public index 32 cards; rater chọn một key hoặc null, reason và confidence, không xem gold, source generator, candidate outputs hay review của người còn lại. Bất đồng → `HOLD_ANNOTATION_DISPUTE`, không sửa gold sau khi nhìn prediction.

## Đúng thứ tự tiền đăng ký

1. Pin ứng viên/baselines/grammar và owner-local model SHA; source-only QA 60/60 trên mock. Nếu QA fail, sửa code **trước khi tạo dữ liệu**.
2. Quyền nguồn và tác giả được owner ký. Biên soạn **CAL64** (8 strata × 8, mỗi case 32 cards), hai AI review, thẩm định nhãn. CAL chỉ hiệu chỉnh threshold, không train/finetune.
3. CAL threshold cố định: 200 điểm 0.005..1.000 + always-abstain; ≤1 false selection/32 negative; tối đa đúng trên 24 primary positive; tie ưu tiên coverage thấp rồi threshold chặt hơn. Baseline tốt nhất chọn trên CAL, tie BM25 > char3gram > T1. Commit receipt SHA threshold và CAL trước khi tạo PROBE.
4. **Sau khi đã xác minh receipt threshold và thứ tự Git commits**, mới biên soạn **PROBE256** (8 strata × 32), khác hoàn toàn về source/entity/style/paraphrase. Hai AI blind review trước science; khóa source bytes SHA. Không được tạo PROBE sớm.
5. Chỉ sau native QA, rights, source/model pins, CAL threshold, two AI receipts, raw private trace policy và owner single GO/HOLD mới xét CPU one-shot. Marker trước first actual PROBE retrieval; never retry; không Reader cho negative, không TEST/GPU.

Các ngưỡng khoa học không sửa: correct SELECT ≥60/96; P1 ≥18/32, P2/P3 ≥16/32; correct ABSTAIN ≥120/128; semantic gain ≥10/96 trên CAL-best baseline, paired bootstrap CI95 lower>0; Reader n=96 positive Answer-only NLL differences A−B1/C1−B1 ≥0.05 với lower CI>0, Oracle control ≥0.05.

**Không được giả mạo trạng thái:** `CAL=NOT_GENERATED`, `PROBE=NOT_GENERATED`, `RIGHTS=NOT_ATTESTED`, `LOCAL_MODEL_BYTES=NOT_VERIFIED`, `NATIVE_QA=NOT_EXECUTED`, `SCIENCE=HOLD`.

## Bước thực hiện tiếp theo

`TTM_VM_V4_OWNER_SOURCE_MODEL_BYTES_RIGHTS_CAL64_RATER_AND_THRESHOLD_FREEZE_BEFORE_PROBE_ONEPACKET`: owner chạy 60 mock QA trên Windows, kiểm local BGE SHA và quyền nguồn, sau đó tạo CAL64 và hai AI blind review để khóa threshold. **Không sinh PROBE, Reader inference hoặc mở TEST trong bước này.**

## Phụ lục nguồn/QA tích hợp (13/11/2026)

Sau báo cáo nguồn ban đầu, đã bổ sung **bộ đóng gói owner-authored input** `tools/research/vector-memory/v4_cal_probe_private_packet_assembler.py` và `tools/research/vector-memory/v4_assembler_source_mock_qa.py` (20 source-only mock checks). `assemble()` chỉ đọc dữ liệu đã được owner cung cấp/attest, không tự tạo câu hỏi. `CAL` xuất private bundle và hai public AI-review packet. `PROBE` đòi receipt threshold CAL đã khóa, kiểm SHA của private CAL, source-rights custody **CAL riêng** và 4 family-disjoint axes trước khi được phép đóng gói.

**Cảnh báo:** trường `cal_rights_manifest_sha256` trong source-lock PROBE phải giữ hash quyền CAL đã khóa; `rights_manifest_sha256` là hash quyền của nguồn PROBE mới. Không ép hai manifest phải bằng nhau, vì nguồn V4 được thiết kế không trùng. Cần kiểm Git commit chronology độc lập; verifier Python chỉ xác minh hash/schema và các khai báo.

Script chủ máy mới **thay** bản kiểm mock 60 đơn lẻ: `tools/research/vector-memory/Invoke-TTM-VM-V4-Integrated-Source-OnePacket-QA-PS51.ps1`. Script pin source commit `df31f91925c76753c4413a8bd58e727c7af7df89`, chạy **60 + 20 = 80 mock source checks** và tạo biên nhận `TTM_VM_V4_NATIVE_SOURCE_QA80_HOLD_RECEIPT_20261113.json`. Đây là source-only/mock QA, **KHÔNG phải CAL64, PROBE256 hoặc scientific execution**. Tại lúc cập nhật, 80 mock tests **đã định nghĩa nhưng chưa có owner native receipt**. Không dùng `PASS_80/80` trước khi chính chủ máy chạy kiểm định.

**Phán quyết giữ nguyên:** `HOLD_OWNER_RIGHTS_MODEL_BYTES_CAL_THRESHOLD_AND_PROBE_CUSTODY`; no Reader, training, GPU, sealed TEST, L0024 hoặc main merge.
