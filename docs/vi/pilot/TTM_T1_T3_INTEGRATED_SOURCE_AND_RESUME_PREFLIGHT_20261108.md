# TTM-Small-4M — Tiền kiểm tích hợp (Integrated Preflight) nguồn T1 và phục hồi T3 trên Colab/Drive

**Ngày:** 08/11/2026. **Yêu cầu hợp nhất (Pull Request):** PR #12, bản nháp (Draft). Đây là kế hoạch kiểm thử nguồn và dữ liệu tổng hợp (Synthetic QA), **không phải lượt huấn luyện khoa học T4**.

> **Ảnh chụp kế hoạch lịch sử:** nhiều cổng ghi `NOT_EXECUTED` vì tại thời điểm viết chưa có dữ liệu và kết quả Colab. Hiện T1–T3 đã PASS kỹ thuật theo [biên bản đóng tổng hợp](../../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md); không thay đổi kết quả lịch sử trong [bản gốc](../../pilot/TTM_T1_T3_INTEGRATED_SOURCE_AND_RESUME_PREFLIGHT_20261108.md).

## Rà soát nguồn và quyền sử dụng (Source and Rights Review)

- Nguồn Hugging Face được ghim: `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. Chỉ chấp nhận hai tệp gốc `TinyStories-train.txt` và `TinyStories-valid.txt`, không chuyển sang phiên bản V2 hoặc dữ liệu Parquet tái tạo.
- Mã SHA-256 từ metadata nguồn chính thức: TRAIN `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f` (xấp xỉ **1,92 GB**); VALID `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4` (xấp xỉ **19,4 MB**). **Ở thời điểm lập tài liệu**, đây mới là mã băm nguồn công bố, chưa phải SHA đo trực tiếp trên máy; việc tải và kiểm SHA độc lập còn `NOT_EXECUTED`.
- Giấy phép trên thẻ dữ liệu (Dataset Card) là `CDLA-Sharing-1.0`: https://cdla.dev/sharing-1-0/. Việc sử dụng để tính toán tuân theo điều khoản nguồn; công bố lại dữ liệu thô hoặc dữ liệu tăng cường phải xét nghĩa vụ giấy phép và ghi nguồn. Không đưa nội dung truyện gốc lên kho GitHub công khai. Chưa có xác nhận độc lập riêng về quyền thương mại, quyền riêng tư và quyền nội dung.
- Dấu phân tách truyện: chuỗi byte UTF-8 `<|endoftext|>`. Trình phân tích theo luồng (Streaming Parser) giữ SHA nguồn và nhận dạng truyện bằng SHA-256 từng truyện, chỉ loại khoảng trắng ở hai đầu, bảo toàn Unicode và CRLF bên trong. Ở thời điểm này trình phân tích mới kiểm tra trên dữ liệu mô phỏng chia khúc; còn phải kiểm ranh giới đầu/cuối trên dữ liệu thật.

## Đề xuất quy tắc chọn tập T1 giới hạn (Bounded Pilot Selection) — chờ chấp thuận

- Đầu tiên đọc cả hai tệp TRAIN và VALID gốc và đối chiếu SHA. Loại truyện TRAIN trùng hoàn toàn bằng mã băm, rồi chọn tất định **2.048** truyện TRAIN theo mức ưu tiên dựa trên hash của nội dung và hạt giống (Seed). Loại trùng gần trong mẫu TRAIN theo độ tương đồng Jaccard của cụm năm từ (5-word Jaccard), ngưỡng từ **0,85**.
- Từ nguồn VALID, chia nhóm tất định bằng hàm băm: **80% VAL / 20% TEST**. Loại bản trùng hoàn toàn với **toàn bộ nguồn TRAIN thô**. Sau đó lấy tập đánh giá hữu hạn **VAL=256 / TEST=64**, kiểm hết các cặp trùng gần ở ngưỡng Jaccard ≥0,85 giữa TRAIN mẫu và các truyện đánh giá đã nhận. Không đưa toàn bộ VALID gốc vào hiện vật công khai. Các mã định danh TEST được niêm phong trong bản kê (Sealed Manifest), không dùng khi học BPE.
- Học BPE từ **768 truyện TRAIN đầu tiên** theo thứ tự hash ưu tiên, **không dùng VAL/TEST**. Hợp đồng: 256 mã byte cơ sở, mã kết thúc (EOS) có ID **256** và **1.791** phép hợp nhất (Merges). Phép tối ưu đếm đoạn duy nhất theo trọng số (Weighted Unique Segments) đã cho **1.791/1.791** phép hợp nhất đúng thứ tự so với mã T2 tham chiếu trên **720** truyện TRAIN tổng hợp. Phải lưu regex, token, thứ tự hợp nhất, SHA nguồn và xác nhận với chương trình gốc (Native Parity).
- Quy mô tập thử nghiệm giới hạn này là **thay đổi phải chấp thuận rõ** so với cách mô tả chia dữ liệu ban đầu, trước khi huấn luyện T4 khoa học. Mức suy rộng của kết quả chỉ giới hạn trong tập pilot đã chọn. Kiểm tra trùng gần toàn diện **trên tập hoạt động**, không có nghĩa tất cả gần 2 triệu truyện TRAIN gốc và toàn VALID đều đã không trùng gần.
- Các trạng thái lúc viết: `T1_REAL_SOURCE_SPLITS=NOT_EXECUTED`, `T1_REAL_TRAIN_BPE=NOT_EXECUTED`, `T1_REAL_BPE_LLAMA_PARITY=NOT_EXECUTED`. Bộ mã đã được đóng gói để chạy một lượt trên Windows: đọc nguồn, đối chiếu SHA, chia tập, học BPE và xác nhận GGUF F32; chưa tiêu thụ hạt giống khoa học.

## T3 — Điểm lưu và phục hồi huấn luyện (Checkpoint and Resume)

- Mã đối tượng Git (Git Blob) P02: `9762343e06cf800b50574c2871ae1ed58537fb18`. Mô hình gồm **3.749.376 tham số**, độ dài ngữ cảnh (Context) **256**, số mã token **2.048**.
- **Kiểm thử CPU cục bộ bằng dữ liệu tổng hợp đã PASS:** 20 bước liên tục so với 10 bước + lưu checkpoint + khôi phục + 10 bước trên PyTorch `2.10.0+cpu`. Sai lệch tuyệt đối lớn nhất của loss/trọng số/bộ tối ưu bằng **0**; trạng thái scheduler khớp, sampler và RNG Python được khôi phục. Checkpoint lưu mô hình, bộ tối ưu, scheduler, sampler, RNG PyTorch CPU/CUDA và vị trí đọc (Cursor). Tệp khoảng **45.067.099 byte**, SHA-256 `7aec610f77a3d50079706e5bbbda11a63b81801b45b2255a6ea322b6a531afda`. Bản kê READY-last và kiểm tra SHA đều PASS **trên mô phỏng hệ thống tệp Drive cục bộ**.
- **Lúc này chưa chạy trên Colab/Google Drive thật.** Notebook đã đóng mã nguồn P02/bộ chạy có SHA. Khi được cấp quyền, Colab gắn MyDrive và yêu cầu GPU CUDA thật, ghi checkpoint vào `MyDrive/TTM/ttm-small-pilot/t3_resume_synthetic_20261108_v1/`, ghi danh sách thư viện `pip freeze`, thông tin PyTorch/CUDA và chạy `drive.flush_and_unmount()`. Phải đọc lại độc lập từ Drive trước khi có thể kết luận PASS Colab.
- GPU T4 chỉ hiển thị như một **lựa chọn dự kiến trong ảnh**, chưa phải bảo đảm có phần cứng hoặc thời gian phiên chạy; tài nguyên Colab có thể thay đổi.

## Bàn giao mã nguồn T2 đã lưu trữ (Archived Source Handoff)

- Kết quả T2 trước đó PASS kỹ thuật với bộ tách token **20/20** và logits **10/10** trên F32, trong khi F16 vẫn bị chặn và không bắt buộc. Gói `TTM_SMALL4M_T2_F32_GPT2_TRAIN_ONLY_INTEGRATED_QA_20261108.zip` có SHA-256 `d6fd9d09a031c4c19e099f0d66d7d5fcccc0e8543ea602d7268ec6cb415dbcb9`; đã đọc lại byte và xác minh SHA từng **7** tệp thành phần. Một gói tích hợp chứa các tệp nguồn đó cùng mã T1/T3 và notebook Colab.
- Bộ PowerShell sẽ tạo cây làm việc Git phụ (Git Worktree) **bên trong** thư mục dự án, kiểm tra từng SHA rồi lưu lên nhánh PR. **Tại thời điểm lập tài liệu:** chưa có commit mã, không được tự nhận đã lưu trữ trước khi đọc lại commit GitHub.

## Bảng quyết định tích hợp tại thời điểm lập tài liệu

| Cổng | Trạng thái khi ghi biên bản |
|---|---|
| T2 F32 GGUF / chương trình gốc trên dữ liệu tổng hợp | PASS kỹ thuật đã khóa |
| T2 F16 | BLOCKED — tuyến tối ưu tùy chọn |
| Nhận dạng nguồn dữ liệu, thẻ nguồn và giấy phép T1 | PASS metadata, còn điều kiện khi công bố |
| SHA byte gốc TRAIN/VALID trên Windows | NOT_EXECUTED |
| Chia tập theo truyện, chống trùng gần và BPE từ TRAIN thật | NOT_EXECUTED |
| T3 CPU tổng hợp 20 so với 10+10 | **PASS** |
| T3 Colab CUDA và Drive READY/đọc lại | **NOT_EXECUTED** |
| Lưu mã nguồn T2/T1/T3 trên PR | READY — chờ commit và đọc lại SHA |
| Khóa khoa học T4 (Science Lock) | **HOLD / NOT_STARTED** |

**Bước thực hiện tiếp theo (ở thời điểm đó):** tiền kiểm tích hợp nguồn trên Windows và lưu mã đã khóa lên PR; chạy một lượt T1 thật và một lượt Colab T3 tổng hợp; sau đó đọc biên bản Drive và SHA nguồn để quyết định cấp quyền tiền đăng ký khoa học. **Không tự chạy lại** các lượt đã tiêu thụ; không ghi QA hạ tầng vào `lineage.md`.
