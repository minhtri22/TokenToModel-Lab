# TTM-Small-4M × EmbeddingGemma 2 — Đọc lại niêm phong nguồn mới và kiểm thử kết nối bốn checkpoint CPU

**Ngày:** 09/11/2026. **Công việc:** `TTM_SMALL4M_EMBEDDINGGEMMA2_NEW_HOLDOUT_WINDOWS_SOURCE_SEAL_READBACK_AND_INDEPENDENT_CPU_MODEL_BINDING_QA`.

**Phán quyết có giới hạn:** `PASS_SCOPED_TECHNICAL_PUBLIC_SEAL_AND_FOUR_CHECKPOINT_SYNTHETIC_BINDING`. **Chưa** đạt `PASS_INDEPENDENT_PRIVATE_SEAL_READBACK` và chưa chứng minh `ORIGINAL_GPU_NUMERIC_PARITY`. Không sử dụng GPU, không huấn luyện, không chấm 320 truyện mới, không đọc nội dung TEST.

## 1. Biên bản trên máy chủ sở hữu

Chủ dự án chạy đúng mã đã ghim từ commit `02d5385732f13e0df265d87e09b8127add0292d3`, xác nhận:
- `SOURCE_SHA256_PASS` cho `ttm_gemma2_holdout_seal.py` và `ttm_gemma2_independent_cpu_scorer.py`.
- Kiểm thử tổng hợp `14/14` và `12/12`, `PASS_RAW_SPLIT_BPE_PINS`.
- `seal-membership`: `MEMBERSHIP_SEALED_NOT_EVALUATED`; **320 truyện**, **75.798 nhãn**, quét **2.119.489 truyện TRAIN**, `rejected_near_full_train=0`, `rejected_near_internal=0`.
- Dấu SHA-256 của `MEMBERSHIP_PRIVATE.json`: `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`.

Thông qua công cụ đọc tệp từ xa, đã đọc lại trực tiếp `_tmp/ttm_gemma2_new_holdout_membership_v1_20261109/SOURCE_SEAL_PUBLIC.json` và thấy đúng các giá trị trên; đã xác nhận tệp `MEMBERSHIP_PRIVATE.json` có tồn tại. Tuy nhiên, nội dung tệp JSON riêng tư lưu thành **một dòng lớn**, vượt giới hạn trả về 20.000 ký tự của công cụ, vì vậy **chưa thể băm độc lập toàn bộ byte riêng tư hoặc kiểm hết 320 ID từ xa**. Nói chính xác: `PASS_PUBLIC_RECEIPT_READBACK`, `HOLD_PRIVATE_BYTES_INDEPENDENT_ATTESTATION`.

Nguồn gốc: TinyStories original revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; TRAIN SHA256 `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`, VALID SHA256 `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`, T1 split SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`, BPE file SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.

## 2. Kiểm toán kỹ thuật bốn checkpoint đã khóa

Sử dụng bản sao riêng tư của bốn checkpoint A/B/C/D đã tải trong lượt thẩm định L0016, **băm lại SHA-256** và nạp bằng PyTorch CPU, `weights_only=True`. Dựng lại cấu trúc P02 độc lập gồm embedding, learned position, bốn block (attention/MLP/LayerNorm), head; A weight-tied, B untied, C/D dùng nguồn donor 512 chiều qua ridge 256 chiều và fallback.

| Nhánh | Checkpoint SHA256 | Load strict | CPU synthetic | Độ lệch nhân quả theo tiền tố |
|---|---|---|---|---:|
| A | `ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081` | PASS | PASS | 0,0 |
| B | `a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c` | PASS | PASS | 0,0 |
| C | `ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d` | PASS | PASS | 0,0 |
| D | `db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e` | PASS | PASS | 0,0 |

Mỗi model cho tensor logits `[1,8,2048]` hữu hạn; kiểm tra tiền tố dài/ngắn bằng token IDs giả lập. Thêm bốn phép nối trực tiếp bộ chấm CPU `score_story_windows()` với từng model thật trên **một truyện giả lập**: cả bốn PASS, đếm đúng tám nhãn, không in giá trị NLL. Kiểm thử âm tính và xây dựng model tổng hợp độc lập bổ sung **8/8 + 6/6 PASS**. Đây chỉ là kiểm thử kỹ thuật; **không chứng minh phép suy luận có logits đúng bằng implementation GPU gốc**.

**Số tham số riêng biệt (theo mô hình độc lập):** A 3.749.376; B 4.273.664; C/D 4.929.024. Điều này tiếp tục nhấn mạnh so sánh C với A/B không có số tham số/FLOPs bằng nhau.

## 3. Biên bản tái tạo không nhạy cảm

- `TTM_ttm_gemma2_holdout_independent_readback.py`, SHA256 `bb49af35a9b1ff04c58125ddc004538ad2067aef00701c0e09356fd03f692a40`: kiểm toán byte SHA, ID unique, thứ tự ranking, target counts, nguồn/split, loại trừ nhóm T1 và old TEST bucket, từ chối chạy science. **Fixture-qa 8/8 PASS; chưa chạy chế độ readback trên Windows**.
- `TTM_ttm_gemma2_cpu_checkpoint_binding_qa.py`, SHA256 `016c2fdc8df2cab642b52f1c7111a5a6694944c8fd06e2cfd4d373d42a2dc438`: bộ dựng mô hình độc lập và QA chỉ trên synthetic IDs; fixture 6/6 PASS, bốn checkpoint thật CPU PASS; không công bố checkpoint.
- Bản JSON kỹ thuật: `artifacts/qa/ttm-embeddinggemma2/TTM_NEW_HOLDOUT_SEAL_READBACK_AND_CPU2048_BINDING_QA_20261109.json`; không có danh sách 320 ID, mã token, vector hay trọng số.

Các mã Python nói trên được cung cấp như tệp tải trong cuộc hội thoại; mã băm được ghim trong báo cáo. Chưa xác nhận đã sao chép vào Windows hoặc ghi chúng như blob source trong commit này; không giả nhận có bản sao source GitHub khi chưa có.

## 4. Những điều chưa được phép kết luận

- Giấy phép nguồn cho phép sử dụng tính toán theo điều kiện; quyền xuất bản/model release là cổng riêng.
- Việc loại trùng nguyên bản với TRAIN và nhóm pilot được thực hiện trong bộ chạy gốc. Bộ niêm phong quét toàn TRAIN bằng 5-gram nhưng chưa kiểm tra **gần trùng với toàn bộ văn bản VALIDATION/TEST pilot trước đó**; không mở TEST cũ để vá điểm này.
- Việc chọn đúng 320 truyện từ tập nguồn VALID chưa từng chấm trước không đủ để khẳng định *donor EmbeddingGemma 2 chưa từng nhìn thấy dữ liệu đó* trong tiền huấn luyện.
- Bốn checkpoint là cùng lượt huấn luyện được chọn theo tín hiệu VALIDATION trước; kiểm định trên 320 truyện chưa dùng sẽ là thử nghiệm xác nhận **cho checkpoint cố định**, không phải lặp độc lập theo seed.
- Không có nhãn PASS/FAIL khoa học mới. `lineage.md` tiếp tục ghi đến L0016, **không nối thêm**.

## 5. Quyết định bước kế tiếp

**Cổng kỹ thuật cần hoàn tất một lần, không mở nhiều micro-permits:** trên Windows chạy script đọc lại `MEMBERSHIP_PRIVATE.json` **chỉ đọc** để đối chiếu byte SHA và 320 định danh; đồng thời chuẩn bị kiểm tra parity code gốc GPU trên vài token giả lập bằng một runner riêng đã khóa, không sử dụng nguồn TRAIN/VAL/TEST. Nếu cả hai PASS, chốt lại hợp đồng một lượt đánh giá thật. Nếu thất bại thì HOLD, không tự thay manifest hay tự chấm.

**Không** chấm tập mới, không GPU, không sửa chương trình khoa học hoặc `lineage.md` trong bước này.
