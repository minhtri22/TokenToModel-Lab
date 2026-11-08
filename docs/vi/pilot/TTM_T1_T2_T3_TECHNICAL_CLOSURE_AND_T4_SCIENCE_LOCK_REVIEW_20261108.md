# TTM-Small-4M — Đóng các cổng kỹ thuật T1–T3 và rà soát khóa khoa học T4 (Science Lock)

**Ngày:** 08/11/2026. **Kho mã nguồn (Repository):** `minhtri22/TokenToModel-Lab`. **Yêu cầu hợp nhất (Pull Request):** PR #12, bản nháp (Draft). **Mốc `main` gốc:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`. **Thực nghiệm khoa học:** chưa thực hiện. Không tự hợp nhất, không thay đổi P00–P12/P07 và không ghi kiểm thử kỹ thuật vào `lineage.md`.

> Bản tiếng Việt này dẫn chiếu [hồ sơ gốc đã khóa](../../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). Tất cả mã định danh, số đo, giá trị SHA và phán quyết được giữ nguyên.

## 1. Phán quyết kỹ thuật sau khi đọc lại độc lập (Independent Readback)

| Cổng kiểm định | Phán quyết | Bằng chứng và giới hạn |
|---|---|---|
| Nguồn gốc T1 | **PASS** | TinyStories `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. SHA-256 nguồn TRAIN: `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`; VALID: `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`. Không công bố văn bản truyện thô. |
| Chia tập và rò rỉ dữ liệu T1 | **PASS, trong tập thử nghiệm giới hạn (Bounded Pilot)** | Kiểm toán độc lập `PASS_INDEPENDENT_T1_REAL_SOURCE_SPLIT_BPE_NATIVE_QA`; **2.048 TRAIN / 256 VAL / 64 TEST**, kiểm tra trùng chính xác và trùng gần giữa các tập con đang dùng. Không khẳng định đã kiểm tra trùng gần với tất cả truyện nguồn TRAIN không được chọn. SHA-256 báo cáo: `0fd1c3e9b97478e35e292b4c5a68c49757cc736136d9aafcbe00129dbc8dfea5`. |
| Bộ tách token BPE T1 trên dữ liệu thật | **PASS** | Học từ **768** truyện TRAIN được chọn, **2.048 mã token (Token IDs)**, **1.791 phép hợp nhất (Merges)**, chỉ dùng TRAIN. SHA-256 bản kê chia tập (Split Manifest) `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; bản kê BPE `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. |
| T2 xuất GGUF F32 và kiểm tra bằng `llama.cpp` | **PASS_SCOPED** | Mã đối tượng Git (Git Blob) của P02: `9762343e06cf800b50574c2871ae1ed58537fb18`; commit `llama.cpp`: `372dc5ca157276beb6c67b2e92477e8d662e964a`. So khớp mã token **20/20**, các vectơ giá trị dự đoán trước chuẩn hóa (Logits) **10/10** với sai lệch tuyệt đối lớn nhất `0.0008438229900207261` ≤ `0.001`; không sai lựa chọn đứng đầu (Top-1). Dùng BPE thật chỉ học TRAIN. Đây là **bằng chứng khả thi khi xuất checkpoint mô hình chưa huấn luyện**, không phải kết quả khoa học hay kiểm thử T5 trên mô hình đã học. |
| Kiểu số F16 trên chương trình gốc (Native Backend) | **BLOCKED_OPTIONAL** | Lỗi kiểu dữ liệu trộn trong biểu đồ tính toán CPU của V4/V5B được giữ nguyên. Tuyến bắt buộc hiện dùng F32; F16/Q8/Q4 là hướng tối ưu tùy chọn, không được đổi kết quả lỗi cũ thành PASS. |
| T3 khôi phục tổng hợp trên CPU cục bộ | **PASS** | So sánh **20 bước liên tục** với **10 bước + checkpoint + 10 bước**: sai lệch loss/trọng số/bộ tối ưu bằng 0 trên dữ liệu tổng hợp (Synthetic Data). |
| T3 khôi phục tổng hợp trên **Colab Tesla T4 + Google Drive** | **PASS_INDEPENDENT** | Giữ nguyên checkpoint bước 10 từ lượt lỗi, lưu lịch sử lỗi cũ, thực thi phục hồi tại thư mục kế tiếp `t3_resume_synthetic_20261108_v1_recovery_01`. So sánh 20 với 10+10 bước: sai lệch loss/trọng số/bộ tối ưu bằng 0; trạng thái lịch học (Scheduler), bộ lấy mẫu (Sampler), sinh số ngẫu nhiên (RNG) Python/CPU/CUDA khớp. Báo cáo và môi trường đã được tải độc lập từ Drive, rồi đối chiếu đúng mã đối tượng Git (Git Blob). |
| Huấn luyện khoa học T4 | **NOT_EXECUTED; LOCK=HOLD** | Kiểm thử kỹ thuật T1–T3 không tự cấp quyền huấn luyện khoa học hoặc quyết định các giả thuyết H1/H2/H3. |

## 2. Lỗi T3 ban đầu và lịch sử phục hồi hợp lệ

GPU Colab gốc: **Tesla T4**, phiên bản `torch 2.14.1+cu130`, CUDA `13.0`. Lượt `t3_resume_synthetic_20261108_v1` phát sinh `TypeError: RNG state must be a torch.ByteTensor` do `torch.load(..., map_location=cuda)` chuyển trạng thái RNG vốn dành cho CPU sang CUDA. Phải giữ nguyên trạng thái dừng (STOP) của lượt này; **không đổi nhãn thành PASS**.

Checkpoint gốc `checkpoint_step10.pt` trên Google Drive có **45.069.785 byte**, SHA-256 `3546105cb736084956c8d4bea6950fe931b658845ed29a5791c6669b40f67382`. Đã kiểm tra trên Colab và kiểm tra độc lập lần nữa bằng cách tải toàn bộ tệp khoảng 45 MB. Tệp báo hoàn tất sau khi ghi (READY-last) `READY.json` có SHA-256 `c77231124003199573227425b3cdeea94f0544eec8cf0906c4443af6b6591765`, cũng tồn tại bền vững. Không sửa hoặc ghi đè checkpoint.

Lượt phục hồi riêng T3B đọc checkpoint gốc với `map_location='cpu'`, tiếp tục **10 bước CUDA** và đối chiếu với mốc **20 bước liên tục** trên cùng thiết bị. Báo cáo `T3_ORIGINAL_CHECKPOINT_SALVAGE_REPORT.json` xác nhận `pass=true`, `PASS_RECOVERED_ORIGINAL_STEP10_CHECKPOINT`, `steps_contiguous=20`, `steps_resumed_from_original_checkpoint=10`; sai lệch loss, trọng số, bộ tối ưu và trạng thái checkpoint ở bước 10 bằng 0; scheduler/sampler/RNG khớp; `science_executed=false`.

**Bằng chứng đối chiếu độc lập Google Drive ↔ GitHub (Independent Evidence Readback):**

| Hiện vật (Artifact), tiền tố `evidence/pilot/t3-colab/` | SHA-256 tính từ byte Drive | Mã Git blob SHA-1 khớp |
|---|---|---|
| `ORIGINAL_READY_STEP10.json` | `c77231124003199573227425b3cdeea94f0544eec8cf0906c4443af6b6591765` | `e159510a7e6daeeab9b775ab8e8bff3aa31692dc` |
| `T3_ORIGINAL_CHECKPOINT_SALVAGE_REPORT.json` | `27431e5f2df96bb566a972191c5bed5e25e5f4e04e590e19d2957c479abb3e4a` | `303968fda01dcab3319ee2d9d688615c71ec855a` |
| `COLAB_ENVIRONMENT.json` | `b25e0ff054c02bf93db72d75aff087f8d378df98ef2d6974f3bc6c44350de139` | `6d13d280bdfdad19f9f552b51f7caf7291be861d` |
| `COLAB_PIP_FREEZE.txt` | `a6eebfff272109bc4732b72d4bb1a0892d73e3db37c8f35d3afd7f32dcff0b80` | `056c738d87865d6632e80c03262b28fc1e5b8456` |

Thư mục Drive gốc: `https://drive.google.com/drive/folders/1CkAH90idd-6BM6_3fvS0U0QqdOENrWLi`; thư mục phục hồi: `https://drive.google.com/drive/folders/1CuO93H0_gzJPW71fh_DYAQZfoCcV6Not`. **Checkpoint nhị phân vẫn lưu trên Google Drive riêng tư, không đăng lên GitHub công khai.** Lệnh `drive.flush_and_unmount()` thành công; ba tệp kết quả được đọc độc lập và khớp.

## 3. Quyết định tổng hợp cuối cùng trước khi cho phép T4 (Science Admission)

Các cổng kiểm tra **kỹ thuật** của T1/T2/T3 đã **đóng**. Không tạo thêm vòng cấp phép cho từng kiểm tra thông thường và không chạy lại các lượt đã tiêu thụ. Chỉ còn năm nhóm điều kiện khoa học quan trọng, phải khóa và chấp thuận trong **một lần tiền đăng ký (Preregistration) kết hợp kiểm tra năng lực**:

1. **Quyền nguồn, phạm vi và chính sách dữ liệu (Dataset Policy):** chấp thuận nghĩa vụ giấy phép của nguồn gốc và giới hạn công bố; xác nhận tập pilot **2.048/256/64** và **768** truyện TRAIN để học BPE; ghi rõ giới hạn trùng gần chỉ trong tập con hoạt động. Khóa bản kê dữ liệu (Manifest), niêm phong tập TEST (Test Seal), SHA nguồn, SHA bộ tách token, hạt giống thực nghiệm một lần (One-shot Seed). Giữ riêng dữ liệu truyện thô.
2. **Giả thuyết và đánh giá khoa học (Scientific Hypotheses and Evaluation):** H1 yêu cầu mất mát log âm trên VALID (Negative Log-Likelihood, NLL) ít nhất **5% thấp hơn** đối chứng bigram làm trơn cộng-alpha (Add-alpha Smoothed Bigram), đồng thời khoảng tin cậy bootstrap ở mức truyện (Story-level Bootstrap) **95%** của chênh lệch NLL không chứa số 0. H2 đánh giá tương đương phục hồi (Resume Parity). H3 kiểm tra xuất checkpoint đã huấn luyện sang GGUF/Ollama trên Windows. Khóa mã đối chứng đồng đều/đơn từ/cặp từ (Uniform/Unigram/Bigram), alpha, **1.000 vòng bootstrap** và seed, chỉ lựa chọn dựa trên VAL và chỉ mở tập TEST giữ riêng đúng một lần.
3. **Ngân sách huấn luyện hữu hạn (Finite Training Budget):** đề xuất **1.024 bước cập nhật bộ tối ưu × 4.096 token đích/bước**, seed **20261108**, AdamW có tốc độ học tối đa (Peak Learning Rate) **3e-4**, làm nóng (Warmup) **32 bước**, lịch cosine xuống **3e-5**, đánh giá VALID mỗi **128 bước**, giới hạn **90 phút GPU**. Trước khi mở khoa học, cần một bài thử năng lực tổng hợp (Synthetic Capacity Smoke) hữu hạn để chọn cỡ lô hiệu dụng (Effective Batch), lô nhỏ (Microbatch), tích lũy gradient (Gradient Accumulation), định dạng số FP32/độ chính xác hỗn hợp (Automatic Mixed Precision, AMP) và ngân sách VRAM; khóa môi trường Colab và thời gian dự kiến. Kiểm thử 20 bước với lô `2×32` **chưa** chứng minh mức 4.096 token/bước chạy đủ trong 90 phút. Nếu không đáp ứng, giữ HOLD và điều chỉnh tiền đăng ký **trước khi chạy khoa học**, không tự ý giảm ngân sách.
4. **Bộ thực thi huấn luyện T4 (Training Implementation):** triển khai và khóa phiên bản bộ nạp dữ liệu (Data Loader) chỉ đọc TRAIN, không đọc TEST; bản kê nguồn và tokenizer, bộ tối ưu/lịch học, đường cong loss và số đo từng lô, bộ đánh giá đối chứng, checkpoint đầy đủ trên Drive theo cơ chế READY-last và phục hồi con trỏ/RNG. Chạy một lần kiểm tra tích hợp không dùng dữ liệu khoa học (Zero-science Preflight), kiểm tra dung lượng lưu trữ. **Bộ chạy T4 và checkpoint T4 chưa được triển khai/kiểm chứng tới mức đủ cấp khóa khoa học**; notebook T3 không phải chương trình huấn luyện T4.
5. **Quản trị (Governance):** thẩm định độc lập tiền đăng ký và cấp quyền khoa học một lần, chỉ sau khi toàn bộ điều kiện PASS. `lineage.md` chỉ ghi bổ sung (Append-only) các kết quả khoa học PASS/FAIL; không đưa lỗi hạ tầng và log kỹ thuật vào lịch sử khoa học. P00–P12 không đổi, P07 bảo toàn; PR #12 vẫn là bản nháp (Draft) cho đến khi rà soát xong nguồn và hợp đồng.

## 4. Trạng thái cuối và bước tiếp theo

`T1_INDEPENDENT=PASS_SCOPED` · `T2_F32=PASS_SCOPED` · `T3_COLAB_DRIVE_SYNTHETIC_RESUME=PASS_INDEPENDENT` · `T3_ORIGINAL_FAILED_RUN=STOP_PRESERVED` · `F16=BLOCKED_OPTIONAL` · `T4_CAPACITY=NOT_VALIDATED_FOR_4096_TOKENS_STEP` · `T4_TRAINER=NOT_LOCKED` · `SCIENCE_LOCK=HOLD` · `T4_TRAIN=NOT_STARTED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_T4_SINGLE_INTEGRATED_PREREG_FINALIZATION_AND_SYNTHETIC_CAPACITY_PREFLIGHT` — giải quyết năm nhóm điều kiện trong **một lần thẩm định phối hợp**, khóa SHA/ngưỡng đánh giá/ngân sách và thông số thực thi, xin phân xử độc lập khóa khoa học; chỉ sau đó mới xem xét một lượt huấn luyện T4 trên Colab.
