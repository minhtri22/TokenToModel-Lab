# TTM-Small-4M — Tích hợp T1/T3: nguồn dữ liệu thật, điểm lưu mô hình (Checkpoint) và khôi phục (Resume)

> **Bản diễn giải tiếng Việt của hướng dẫn gói T1/T3 tại thời điểm đóng gói.** Những dòng `CHƯA TẢI`, `NOT_EXECUTED` và hướng dẫn chỉ chạy một lần phản ánh trạng thái lúc tạo gói, không được chạy lại chỉ vì đọc bản dịch. Kết quả mới nhất xem [biên bản T1–T3](../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md); [hướng dẫn gốc đã khóa](../../../tools/pilot_t1t3/README_TTM_T1_T3_VI.md) giữ nguyên.

**Trạng thái:** T2 F32 kỹ thuật PASS đã khóa. T1 nguồn thực CHƯA TẢI/CHƯA CHẠY; T3 đã PASS trên CPU cục bộ, nhưng Colab/Google Drive thực tế CHƯA CHẠY. **T4 khoa học CHƯA ĐƯỢC PHÉP.**

## Cấu trúc gói

- `source_t2/*`: bảy tệp mã và tình huống kiểm thử (Fixtures) gốc của T2 F32, kiểm từng SHA-256 từ ZIP đã PASS; thêm công cụ phụ trợ (Helper) GGUF V3 có SHA-256 chính xác (Exact). Đây là bản thực thi T2 cuối cùng, không phải V5B F16.
- `t1_source_split_bộ tách token (Tokenizer).py`: tải hai tệp TinyStories gốc phiên bản (Revision) đã khóa, kiểm SHA256, trình phân tích theo luồng (Streaming Parser) với EOS, chọn TRAIN/VAL/TEST theo hàm băm truyện (Story Hash), chống trùng hoàn toàn (Exact Deduplication) và độ tương đồng Jaccard theo nhóm năm từ (Word 5-gram), huấn luyện mã hóa theo cặp byte (BPE) trên TRAIN thật. Không đưa văn bản thô (Raw Text) vào biên bản GitHub.
- `t1_real_bộ tách token (Tokenizer)_native.py`: nạp mã hóa theo cặp byte (BPE) thật từ T1, xuất GGUF F32 với trọng số ngẫu nhiên của P02 (Random Weights), kiểm tra 20 mã token (Token IDs) và 10 vectơ giá trị dự đoán (Logits) qua `llama.cpp` chương trình gốc (Native Backend) đã ghim. Không sử dụng TEST truyện.
- `t3_resume_smoke.py`, `p02_source_exact.py`: điểm lưu/khôi phục (Checkpoint/Resume) trên dữ liệu tổng hợp, đủ mô hình (Model), bộ tối ưu (Optimizer), lịch học (Scheduler), RNG Python/PyTorch, bộ lấy mẫu (Sampler) và vị trí đọc (Cursor).
- `TTM_T3_Colab_Drive_Resume_Synthetic_20261108.ipynb`: sổ tay (Notebook) tự chứa P02 và bộ chạy (Runner) có kiểm SHA; chỉ chạy sau khi người dùng gắn Drive và cấp GPU Colab. Sau khi chạy, đồng bộ và ngắt kết nối Drive (Flush/Unmount) rồi đọc file từ Google Drive độc lập.
- `Run-TTM-T1T3-Integrated-PS51.ps1`: kiểm tra trước (Preview) / thực thi (Execute) trên Windows, lưu mã bằng commit trong cây làm việc Git cô lập (Isolated Worktree) **bên trong repo** lên PR #12 đúng HEAD, rồi chạy T1 đúng một lần. Nếu lỗi bất kỳ giữ thư mục/bằng chứng; không tự chạy lại (Rerun).

## Nguồn dữ liệu gốc (Original Source)

- Kho dữ liệu (Repository): https://huggingface.co/datasets/roneneldan/TinyStories
- Phiên bản (Revision): `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`
- `TinyStories-train.txt`: `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`
- `TinyStories-valid.txt`: `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`
- Giấy phép (License): `CDLA-Sharing-1.0` — có điều kiện nếu công bố/phân phối lại dữ liệu, KHÔNG đưa truyện gốc chưa xử lý (Raw Stories) lên GitHub. https://cdla.dev/sharing-1-0/

Các SHA trên là thông tin xác minh từ Hugging Face, **không phải đã đọc hai tệp dữ liệu gốc (Raw) trên máy Windows**. Bộ tải mới thực sự kiểm tra byte. Nếu mạng mất, giữ `.partial` và dừng, không chạy lại tự động. Yêu cầu còn đủ dung lượng ổ D cho xấp xỉ 2 GB nguồn và hiện vật. Nếu thời gian tải lớn hoặc Colab không cấp GPU, không tự đổi nguồn, hạt giống (Seed) hoặc ngân sách (Budget).

## Quy tắc chia cho tập thử nghiệm giới hạn (Pilot) (đề xuất cần đồng ý trong tiền đăng ký)

- Duyệt toàn bộ TRAIN gốc, loại bản trùng chính xác (Exact Duplicates); chọn 2.048 truyện TRAIN bằng hàm băm có hạt giống (Seed Hash), lọc trùng gần word-5gram Jaccard `>=0.85` trong tập con (Subset).
- VALID gốc được phân nhóm theo hàm băm (Hash) 80% VAL / 20% TEST, loại trùng lặp chính xác (Exact Overlap) với toàn bộ TRAIN gốc. Chọn tập đánh giá hoạt động **256 VAL, 64 TEST**, lọc trùng gần với TRAIN được dùng và lẫn nhau. Điều này KHÔNG chứng minh không có trùng gần trong toàn bộ kho không dùng.
- Tokenizer học **768 truyện từ TRAIN đã chọn**, không VAL/TEST. mã hóa theo cặp byte (BPE) đúng 2.048 ID, 1.791 merge; bản tối ưu đã xác minh cùng kết quả với T2 trên 720 truyện TRAIN tổng hợp. Mô hình ~3.75M vẫn chưa được huấn luyện.
- T1 manifest lưu SHA IDs và thống kê, không lưu nội dung story. TEST không đọc khi fit bộ tách token (Tokenizer).

Các tập con này cần được phê duyệt rõ trong hợp đồng T1 trước khi chạy science T4; không âm thầm coi là toàn bộ TinyStories.

## Windows

1. Tải ZIP và kiểm SHA256 theo biên bản giao; giải nén vào thư mục mới `C:\Users\minht\Downloads\TTM_T1_T3_INTEGRATED_20261108`.
2. Kiểm `Get-FileHash` script và cú pháp PS 5.1, chạy `-Mode Preview`. Không có ghi file hay tải dữ liệu.
3. Nếu mọi pin PASS, chạy **một** `-Mode Execute`. Trình chạy dùng worktree trong `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees`, push mã lên nhánh PR #12 sau kiểm SHA và dọn đúng worktree do nó tạo khi push/readback PASS. Sau đó mới tải, kiểm SHA raw TinyStories, chia split và học mã hóa theo cặp byte (BPE) TRAIN-only; dùng `llama.cpp` F32 CPU kiểm tra lại.
4. Nếu bất kỳ bước nào FAIL/STOP, giữ nguyên log/partial/result, không gọi lại Execute. Không sửa `main`, P07, hay `lineage.md`.

## Google Colab

1. Mở Google Colab, `File > Upload notebook`, chọn `TTM_T3_Colab_Drive_Resume_Synthetic_20261108.ipynb`.
2. Cấu hình `Python 3` + GPU (T4 nếu được cấp), chạy lần lượt 4 ô code. Gắn Drive của chính tài khoản người dùng. Không chạy T4 science.
3. Notebook ghi dưới `MyDrive/TTM/ttm-small-pilot/t3_resume_synthetic_20261108_v1/`: checkpoint (~45 MB), `READY.json`, `T3_RESUME_REPORT.json`, `COLAB_PIP_FREEZE.txt` và `COLAB_ENVIRONMENT.json`. Ô cuối cùng `flush_and_unmount()`.
4. Không chạy lại cùng `RUN_ID` khi đã có thư mục. Gửi báo cáo + SHA hoặc cho phép đọc độc lập qua Google Drive connector để kết luận T3.

## Kết luận hiện tại

`T2_F32=PASS_TECHNICAL` · `T1_SOURCE_META_LICENSE=PASS_WITH_CONDITIONS` · `T1_RAW_SHA/SPLIT/mã hóa theo cặp byte (BPE)=NOT_EXECUTED` · `T3_LOCAL_CPU_RESUME=PASS` · `T3_COLAB_DRIVE=NOT_EXECUTED` · `T4_SCIENCE=NOT_AUTHORIZED`.
