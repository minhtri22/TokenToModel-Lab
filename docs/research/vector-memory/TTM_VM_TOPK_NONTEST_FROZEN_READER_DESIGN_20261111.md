# TTM — Frozen Reader Top-k: thiết kế PROBE mới không dùng TEST

**Operation:** `TTM_VM_EXTERNAL_FACTS_RETRIEVED_TOPK_NONTEST_READINESS_AND_FROZEN_READER_GENERALIZATION_DESIGN`
**Date:** 2026-11-11 · **Status:** `DESIGN_SOURCE_STATIC_QA_ONLY` · **Branch:** `research/ttm-vector-memory-architecture-20261111`

## 1. Động cơ khoa học

L0020 `PASS_DEV_SCREEN_GO_CANDIDATE_SCOPED`: no-memory NLL 6.947507, correct-memory 3.816948, wrong-memory 5.298715. Đây là kết quả sàng lọc DEV 64 truyện với Oracle chọn chính xác một bản ghi, **không chứng minh retriever tự tìm được tri thức**. Lượt CPU TRAIN/DEV L0020 đã tiêu thụ; không chấm lại DEV, không huấn luyện tiếp và không mở TEST.

Reader gốc Git blob `7ce728b2874284b87933237c890e54ce3d9fd651` chỉ học với một bản ghi active; query/key projections bị đóng băng vì attention singleton. Top-3 sẽ tạo tình huống **nhiều bản ghi active ngoài phân phối huấn luyện**. Do đó, tách phép đo `Recall@k` của retriever khỏi Answer-only NLL của frozen Reader.

## 2. PROBE hoàn toàn mới

- Generator đã khóa: `tools/research/vector-memory/topk_nontest_probe.py`, Git blob `b08e2120a2ac9d4e270ee48fdca77e4a4743e22c`, seed `TTM_VM_FRESH_NONTEST_TOPK_PROBE_20261111_V1`.
- Đúng **128** truyện thuộc split `non_test_probe`; **32** memory cards/truyện; một key đúng + **4 hard negatives** chỉ khác một ký tự + 27 distractors; 16 nhãn cân bằng (8 truyện/nhãn).
- Tất cả 4.096 keys nội bộ đều khác nhau; key PROBE không trùng các aliases TRAIN256/DEV64 trước đó; question không chứa gold answer. `wrong_memory` chỉ thay value của target, giữ nguyên keys/positions/distractors.
- PROBE public-seed deterministic là **exploratory**; không gọi là blind heldout hoặc TEST. Không dùng PROBE để train, chọn checkpoint/hyperparameter hay dò tham số retriever.
- QA tĩnh trên generator và vector mock: `PASS_STATIC_DESIGN_QA_38/38`. **Đây chưa phải Recall@k thực hay mô hình inference**.

## 3. Retriever và đối chứng đã khóa

**Primary `R_FULL_COSINE`:** encode **toàn question** bằng T1 BPE thật, lấy mean embedding từ tied token table của checkpoint P02 step1280; encode từng memory **key** theo cùng cách; cosine + tie-break lexical key. Giao diện `rank_frozen_full_question_cosine(question,cards,text_to_ids,frozen_embedding_weight)` không nhận answer/target_key và không được exact-match. Xếp 32 records rồi mới tạo mask Top-1 hoặc Top-3. Scorer mới được truy cập target_key để tính hit sau ranking.

**Retrieval-only control `R_LEX_TRIGRAM`:** overlap ký tự 3-gram giữa toàn question và mỗi key; chỉ ghi Recall@1/@3, không đưa vào so sánh NLL sau khi xem PROBE. **Oracle-1:** exact lookup từ entity hiển thị trong question, dùng làm positive upper bound, tuyệt đối không làm primary.

Trên cùng ngân hàng 32 cards: Top-1 chỉ mở 1 key; Top-3 mở 3 key. Reader không thay đổi source/weights. **Không gọi `encode_cards_for_reader` của Oracle Reader trong đường non-Oracle**, vì hàm đó tự sinh Oracle mask. Thay bằng key/value encoding frozen T1 + embedding và mask lấy duy nhất từ retrieval rank; dùng `GatedOracleReader.forward` gốc.

## 4. Đối chứng Reader (chỉ thiết kế, chưa chấm)

| Arm | Memory | Mục đích |
|---|---|---|
| A | Không memory | Frozen GPT bypass |
| O1 | Oracle top-1 correct | Reader positive control trên PROBE mới |
| B1 / C1 | R_FULL Top-1 đúng / tráo target value | Tách retrieval một bản ghi khỏi khả năng đọc value |
| B3 / C3 | R_FULL Top-3 đúng / tráo target value | Kiểm tra attention nhiều bản ghi với Reader frozen |

Rank đúng/sai phải identical trước khi swap value; khi target không thuộc Top-k, swap không được ảnh hưởng logits Reader. NLL phải chỉ chấm token answer (teacher forcing); mỗi truyện đồng trọng số.

## 5. Khóa trước lượt inference mới

- Pin checkpoint SHA256: `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; T1 manifest SHA256: `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- **Chưa có SHA binary của `reader_private.pt`** được xác minh. Trước phép đo phải SHA-pin private Reader checkpoint một-shot L0020 với `steps=128`, giữ nguyên 110.689 tham số đã học. Không tái train Reader.
- Một lần inference CPU FP32 trên 128 PROBE, các arm cố định A/O1/B1/C1/B3/C3. Chỉ một lượt xếp hạng frozen R_FULL và R_LEX; tuyệt đối không score lại TRAIN/DEV/TEST. One-shot started marker trước mọi science scoring, không overwrite/auto-retry.
- Tiêu chí sàng lọc đề xuất cần được freeze trong runner trước inference: `R_FULL Recall@3 >= 0.95` và B3 vượt A, C3 mỗi chênh lệch NLL trung bình theo truyện `>= 0.05`, cận dưới paired bootstrap 95% `>0` (1.000 mẫu, seeds 20261114/20261115). K1 là diagnostic bắt buộc, không được thay thế chỉ tiêu K3 hậu nghiệm.
- Nếu Recall@3 thấp: `FAIL_RETRIEVAL_SCOPED`. Nếu Recall đạt nhưng K3 NLL FAIL và K1 PASS: `FAIL_MULTI_RECORD_READER_GENERALIZATION_SCOPED`. Nếu Oracle-1 FAIL: `HOLD_READER_PROBE_DOMAIN_SHIFT`. Nếu cả recall và K3 đạt: chỉ `GO_CANDIDATE_NONTEST_SCOPED`, **không mở TEST**.

## 6. Trạng thái, bằng chứng, bước sau

Đã tạo PROBE 128 mới với SHA256 `88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11` (tệp chứa từng case/answer **không upload GitHub**). SHA256 generator `a86c8f659c86921695f8653000986ffc34472d88b1466d7b900104e7c4e661f8`. Source QA Python đạt **38/38**; không nạp trained Reader, không chấm NLL, không GPU hoặc TEST.

`lineage.md` **không thêm entry** cho thiết kế/QA kỹ thuật; L0020 giữ nguyên; `main` không đổi.

**Bước thực hiện tiếp theo:** `TTM_VM_TOPK_NONTEST_FROZEN_READER_ONE_SHOT_SOURCE_INTEGRATION_AND_PREEXEC_QA` — tích hợp non-Oracle key/value encoder + frozen Reader scoring, pin SHA Reader và QA negative/hard-negative trên nguồn; sau đó mới quyết định một phép đo CPU duy nhất, TEST tiếp tục niêm phong.
