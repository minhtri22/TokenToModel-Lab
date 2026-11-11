# TTM Vector Memory — Top-k non-Oracle / Frozen Reader: tích hợp nguồn và tiền kiểm

**Operation:** `TTM_VM_TOPK_NONTEST_FROZEN_READER_ONE_SHOT_SOURCE_INTEGRATION_AND_PREEXEC_QA`  
**Nhánh:** `research/ttm-vector-memory-architecture-20261111`  
**Trạng thái kỹ thuật:** `PASS_SCOPED_SOURCE_INTEGRATION` · **Trạng thái phát hành khoa học:** `HOLD_PRIVATE_READER_SHA_OWNER`  
**Không huấn luyện, không chạy PROBE inference, không chấm lại DEV, không mở TEST, không GPU, không merge main.**

## 1. Thay đúng thành phần, giữ Reader gốc

- Reader **thực của thiết kế L0020** được import từ `oracle_reader_source_only.py`, Git blob **`7ce728b2874284b87933237c890e54ce3d9fd651`**. Không viết lại hoặc sửa `GatedOracleReader.forward` / `logits_from_hidden` để tạo kết quả mới.
- Bộ tích hợp mới: `tools/research/vector-memory/topk_reader_integration.py`, Git blob **`ccab713f8c5a4b913259088225daffcf5382be41`**; hàm `encode_topk_inputs(question,correct_cards,wrong_cards,tokenizer,frozen_embedding,k=1|3)`.
- Retriever chính sử dụng `rank_frozen_full_question_cosine` từ generator đã khóa Git blob **`b08e2120a2ac9d4e270ee48fdca77e4a4743e22c`**. Đầu vào xếp hạng chỉ là **toàn câu hỏi, khóa card, tokenizer T1 và embedding P02 frozen**. Không truyền `answer`, `target_key`, `gold`, không gọi `oracle_key_mask` hoặc `oracle_upper_bound_rank` trong đường Top-k.
- Thứ tự 32 key và mask Top-1/Top-3 được tính **một lần**, sử dụng nguyên vẹn cho memory đúng/sai. Giá trị hai nhánh được mã hóa riêng bằng T1 frozen embedding; thay value không được đổi keys, cosine ranks hoặc mask. No-memory tạo mảng 0 bản ghi, Reader bypass.
- Tất cả dữ liệu card/embedding dùng để kiểm thử nguồn là **mock token byte ASCII + random frozen CPU embedding**, không chứa thông tin từ trained Reader, từ TEST, hay từ DEV khoa học.
- **Giới hạn kiến trúc:** Reader L0020 chỉ học với Oracle singleton một bản ghi active và Query/Key projections đã frozen. Vì thế Top-3 có thể thất bại cả khi recall retriever đúng; một thất bại không tự động định danh lỗi Retriever.

## 2. QA thực sự đã thực hiện

- **42/42 PASS**: nguồn Reader gốc và PROBE đúng Git blob, PROBE 128 truyện đúng SHA `88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11`, 32 cards/story, Top-1/Top-3 mask đúng, rank không phụ thuộc giá trị, bypass exact, selected/missed counterfactual, key reorder, bad K/size/IDs rejected, phép kiểm tra metadata Reader source và âm tính; kết quả JSON nguồn SHA256 **`44c16412860eb8e0605a727a92ad864f080f5bd16eed0b8e11a1bd29415a7154`**. Script 42 test kèm gói ZIP công khai.
- **28/28 PASS** bởi đường kiểm toán thứ hai `topk_reader_compact_independent_audit.py` Git blob **`30920a7b837343606fa8e200c8cc1c79c4a706d8`**; JSON nguồn SHA256 **`7e084cd962267b745c87306835821f0984ba6f8c09327123132afdab686504ef`**.
- Source-only và synthetic kiểm được khi memory sai chỉ đổi value của target: nếu target nằm trong Top-k, thay value làm thay đổi logits ở Reader mô phỏng; nếu target không được retrieve, output không đổi bit-exact. Tắt memory giữ logits bằng frozen head bit-exact.
- Kiểm tra quy trình custody bằng một **tệp state giả lập**: 8 tensor đúng shape/metadata step 128 được chấp nhận; sai step, sai source pin, thiếu tensor, NaN đều bị từ chối trong suite tích hợp.
- **Không có trained Reader inference, không đo Recall@k thật, không chấm NLL; đây không phải QA của năng lực mô hình.** Hai bộ QA không phải hai cuộc tái thực hiện khoa học độc lập.

## 3. Khóa nguồn và trọng số riêng tư trên Windows

- Reader riêng tư duy nhất từ lần huấn luyện L0020: `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1\reader_private.pt`.
- Đường preexec mới: `tools/research/vector-memory/topk_private_reader_custody_preexec.py` (Git blob **`688d97e8389a8052a4e405632bdbf7d261bc306b`**), đọc **byte SHA256**, tải `weights_only=True` với CPU chỉ để kiểm shape, source pins và `steps=128`. Không gọi `forward`, không tính logits, không mở TEST, không đổi file.
- Biên bản Windows in ra `PRIVATE_READER_SHA256=<hash>`, 8 tensor, `SOURCE_STRUCTURE=PASS` và tạo JSON owner receipt riêng dưới `_evidence\vector-memory`. **Không gửi bản nhị phân Reader lên GitHub.**
- Do công cụ từ xa không cung cấp hash binary được kiểm chứng ở thời điểm biên soạn, **không tự điền hoặc phỏng đoán SHA256**. Cổng `PRIVATE_READER_SHA256=PENDING_OWNER_WINDOWS` vẫn HOLD đến khi nhận và đối chiếu owner readback.
- PowerShell 5.1 `Invoke-TTM-VM-TopK-NonTest-FrozenReader-Preexec-PS51.ps1` chạy **gộp một lượt** 28/28 QA trên Windows và custody Reader. Tất cả bên trong project root D:, không tải tệp vào C: hoặc thay science checkout `c41b6c8`; dùng worktree riêng `worktrees\ttm-vm-topk-source-20261112`.
- Mọi output QA refuse overwrite. Không có hành vi `--execute-once` trên Reader science runner. Nếu QA FAIL, HOLD không tự sửa, không chạy khoa học.

## 4. Hợp đồng khoa học còn được giữ nguyên

Theo thiết kế đã khóa trước PROBE: 128 câu hỏi NONTEST, mỗi câu hỏi 32 cards gồm 1 đúng + 4 hard negatives + 27 nhiễu; primary cosine full-question với tied embedding P02 step1280; frozen Reader cuối bước 128; các nhánh A bypass, O1 Oracle upper bound, B1/C1 Top1, B3/C3 Top3. PROBE SHA256 `88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11`. Tiêu chí sàng lọc prospective vẫn là Recall@3≥95%; `NLL(A)-NLL(B3)` và `NLL(C3)-NLL(B3)` đều ≥0,05 và cận dưới bootstrap báo cáo 95% >0 (1.000 bootstrap, seeds 20261114/20261115). **Các kết quả này CHƯA ĐƯỢC ĐO.**

Nếu một phép đo sau này được cấp quyền, nó phải dùng đúng Reader SHA mới khóa, một lần inference CPU trên PROBE và không điều chỉnh tham số từ PROBE; không giải mã TEST, không huấn luyện và không chấm lại DEV lịch sử. Bài toán này vẫn exploratory, không phải TEST confirmatory.

## 5. Phán quyết cuối của bước này

**`SOURCE_INTEGRATION_QA=PASS_42/42` · `SECONDARY_QA=PASS_28/28` · `PRIVATE_READER_SHA256=PENDING` · `TOPK_SCIENCE=HOLD` · `TRAINING=NO` · `TEST=SEALED` · `GPU=NO` · `LINEAGE=L0020_UNCHANGED` · `MAIN=UNCHANGED`.**

**Bước thực hiện tiếp theo:** `TTM_VM_TOPK_OWNER_PRIVATE_READER_SHA_READBACK_AND_SINGLE_CPU_PROBE_GO_HOLD` — dùng một gói PowerShell đã lưu để khóa SHA Reader và độc lập QA Windows; sau đó đưa ra một quyết định GO/HOLD duy nhất cho phép đo CPU không phải TEST, không mở micro-permit.
