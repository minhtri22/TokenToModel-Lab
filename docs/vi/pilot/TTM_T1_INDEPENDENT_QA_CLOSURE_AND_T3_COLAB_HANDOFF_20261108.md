# TTM T1 — Đóng kiểm toán độc lập (Independent QA) và bàn giao T3 cho Google Colab/Google Drive (08/11/2026)

> **Bản tiếng Việt của biên bản lịch sử.** Nội dung trạng thái bên dưới phản ánh **thời điểm lập tài liệu gốc**, khi T3 trên Colab chưa thực hiện. Kết quả T3 đã hoàn thành sau đó phải đối chiếu với [biên bản đóng T1–T3 hiện hành](../../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). [Văn bản gốc](../../pilot/TTM_T1_INDEPENDENT_QA_CLOSURE_AND_T3_COLAB_HANDOFF_20261108.md) được giữ nguyên.

## Bằng chứng đã khóa (Frozen Evidence) — không chạy lại T1

- Tệp người dùng cung cấp `TTM_T1_INDEPENDENT_QA.json` được tính mã băm SHA-256 độc lập: `0fd1c3e9b97478e35e292b4c5a68c49757cc736136d9aafcbe00129dbc8dfea5`, dung lượng **1.882 byte**. Nội dung trùng bản JSON đọc trực tiếp trên Windows. Bản đã đưa lên GitHub tại `evidence/pilot/t1-real/TTM_T1_INDEPENDENT_QA.json` có mã đối tượng Git (Git Blob) `3b5613fdabc00f44b7524ac9dad486b1be5c3b00`.
- Phán quyết kiểm toán: `PASS_INDEPENDENT_T1_REAL_SOURCE_SPLIT_BPE_NATIVE_QA`. Phiên bản dữ liệu (Dataset Revision): `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. SHA-256 của nguồn TRAIN: `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`; nguồn VALID: `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`.
- Thống kê kiểm tra độc lập: quét **2.119.489** truyện TRAIN, phát hiện **320.241** lần trùng hoàn toàn; quét **21.990** truyện VALID, loại **6.601** truyện trùng hoàn toàn với toàn bộ nguồn TRAIN ban đầu. Tập thử nghiệm giới hạn (Pilot Subset): **2.048 TRAIN / 256 VAL / 64 TEST**. Kiểm tra trùng gần theo độ tương đồng Jaccard của cụm năm từ (5-word Jaccard) với ngưỡng **0,85** chỉ áp dụng cho các tập con đang sử dụng; **không chứng minh** toàn bộ truyện TRAIN chưa chọn không trùng gần. `train_near_rejected_by_independent_audit=0`.
- SHA-256 của bản kê chia tập (Split Manifest): `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`. SHA-256 tệp bộ tách token BPE học từ TRAIN: `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. Mã băm bên trong bản kê: `6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6`. Bộ BPE được học từ **768** truyện TRAIN, gồm **2.048** mã token và **1.791** phép hợp nhất (Merges).
- Bộ tách token kiểm tra qua chương trình suy luận gốc (Native llama.cpp) ở độ chính xác F32: **20/20 mã token khớp chính xác**, **10/10** phép đối chiếu giá trị dự đoán trước chuẩn hóa (Logits) có lựa chọn cao nhất (Top-1) khớp. Sai lệch tuyệt đối tối đa (Maximum Absolute Error) `0.0008438229900207261`, dưới ngưỡng `0.001`. SHA-256 tệp GGUF: `68c0684d75fe12965427c93f34052172d59b480a74f52804648a4751ed5c8747`; biên bản suy luận gốc: `04ade9824c4f63f0f3a169bb918cd78bd4c4133965168e4aec5bd85f83868ea3`.

## Phán quyết và giới hạn (Adjudication and Limits)

`T1_REAL_SOURCE_SPLIT_TRAIN_ONLY_BPE_F32=PASS_INDEPENDENT_TECHNICAL_SCOPED`: đã kiểm chứng nguồn gốc dữ liệu, tính toàn vẹn của phép chia trong tập thử nghiệm giới hạn và sự tương đương giữa bộ tách token / GGUF. **Không** được diễn giải thành đã loại trùng gần toàn bộ dữ liệu chưa sử dụng hoặc đã huấn luyện mô hình thực.

Quy mô tập con nêu trên vẫn là một điều chỉnh cần được chấp thuận trong tiền đăng ký tổng hợp (Integrated Preregistration) trước khi mở thực nghiệm khoa học. Kiểm thử kỹ thuật (Engineering QA) **không tạo bằng chứng kết quả khoa học**. Tệp `lineage.md` chỉ được ghi bổ sung (Append-only) và không bị chỉnh sửa ở bước này.

## Bước T3 được dự kiến tại thời điểm lập biên bản (Historical T3 Handoff)

- Sổ tay Colab (Notebook) đã khóa trong repository: `tools/pilot_t1t3/TTM_T3_Colab_Drive_Resume_Synthetic_20261108.ipynb`, mã đối tượng Git `92f76f1f3232c899771184e627e7d85a5495bf1e`.
- Môi trường thực thi (Runtime) trên Google Colab yêu cầu GPU CUDA được người dùng cấp quyền. Không huấn luyện T4, không đọc TinyStories. Notebook tích hợp mã P02 và bộ chạy đã ghim SHA. So sánh **20 bước liên tục** với **10 bước → lưu điểm khôi phục mô hình (Checkpoint) lên Drive → đọc lại → khôi phục (Resume) → 10 bước**, bảo toàn mô hình, bộ tối ưu (Optimizer), lịch học (Scheduler), trạng thái RNG Python/PyTorch/CUDA, bộ lấy mẫu (Sampler) và vị trí đọc dữ liệu (Cursor). Các tệp đầu ra: `READY.json`, `checkpoint_step10.pt`, `T3_RESUME_REPORT.json`, `COLAB_PIP_FREEZE.txt`, `COLAB_ENVIRONMENT.json`, dưới `MyDrive/TTM/ttm-small-pilot/t3_resume_synthetic_20261108_v1/`; cuối cùng đồng bộ và ngắt kết nối (Flush/Unmount).
- **Không chỉ dựa vào nhật ký Colab:** sau khi ngắt kết nối, cần đọc độc lập các tệp từ Google Drive, đối chiếu SHA của `READY.json` với byte thực của `.pt`, kiểm tra báo cáo `pass=true`, thiết bị CUDA, sai lệch loss/model/optimizer/scheduler/sampler và SHA môi trường. Nếu không đọc được toàn bộ byte checkpoint, kết luận chỉ có thể là một phần hoặc tạm giữ (HOLD), không tuyên bố đã kiểm chứng lưu trữ bền vững.
- Ở thời điểm tài liệu này được lập, tìm kiếm `ttm-small-pilot` trên Google Drive chưa có kết quả nên ghi `T3_COLAB_DRIVE=NOT_EXECUTED`. Đây **không phải trạng thái hiện hành sau T3B**.

**Trạng thái lịch sử:** `T1_INDEPENDENT=PASS_SCOPED`, `T2_F32=PASS`, `T3_LOCAL_CPU_RESUME=PASS`, `T3_COLAB_DRIVE=NOT_EXECUTED`, `T4_SCIENCE_LOCK=HOLD`, `T4_GPU_TRAIN=NOT_STARTED`. PR #12 còn là bản nháp (Draft); không hợp nhất (Merge), không sửa P07.

**Bước tiếp theo tại thời điểm đó:** thực hiện một lượt kiểm thử Colab/Drive tổng hợp, đọc lại độc lập bằng chứng Drive và thẩm định tổng hợp. Không chạy lại T1; không tách các kiểm tra kỹ thuật nhỏ thành thủ tục cấp phép riêng.
