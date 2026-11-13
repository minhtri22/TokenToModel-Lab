# FC01 V2 — Owner exact-T1 BPE readiness PASS và quyết định khoa học duy nhất

**Operation:** `TTM_SMALL4M_FC01_V2_OWNER_EXACT_T1_SOURCE_QA_READBACK_AND_SINGLE_SCIENCE_GO_HOLD`  
**Ngày:** 13/11/2026  
**Phạm vi:** SOURCE/RIGHTS/DATA/RUNNER AUDIT; **không TRAIN/TEST/GPU**.  
**Owner technical QA:** `PASS_OWNER_SOURCE_QA_SCOPED`  
**Duy nhất một quyết định về science:** **`HOLD_PENDING_RIGHTS_ATTESTATION_AND_COLAB_FP32_DRIVE_RESUME_READINESS`**.

## 1. Kết quả thực tế từ máy owner

Owner chạy Python 3.12 và tích hợp QA source-only cho FC01 V2:

| Kiểm tra | Kết quả |
|---|---|
| V1 7 source SHA chuẩn | PASS |
| Transform thành V2 với 7 SHA khóa | PASS |
| 7 file V2 UTF-8 LF, no overwrite V1 | PASS |
| TinyStories TRAIN/VALID, T1 BPE, checkpoint1024, T4 private pack SHA | PASS |
| Corpus V2 nguyên bản mới | PASS; SHA `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3` |
| Families TRAIN/VAL/EVAL | 256 / 64 / 64; tổng 384 |
| Episodes A/B/C | 512 mỗi nhánh |
| Đẳng nhất B/C private corpus | TRUE |
| **BPE thực sự (exact frozen T1)** | **PASS**, context max 58/256 |
| Independent code self-authored static/negative QA | **16/16 PASS** |
| Trainer `--mode audit` với bundle P02/T1/checkpoint/corpus/T4 | **PASS SOURCE_ONLY** |
| Training/inference/GPU/TEST | **NOT EXECUTED** |

Đây là bằng chứng **nguồn và tính sẵn sàng của runner ở chế độ audit**, không có backprop/science inference mới. QA tĩnh do mã reviewer riêng thực hiện nhưng tự soạn, **không chứng nhận reviewer con người độc lập**.

## 2. Kiểm tra readback độc lập qua RemoteMCP V2 canonical

Kết nối machine-1 có heartbeat tươi, root `D:\WORK\RESEARCH`. Đã thấy đủ:

- `_tmp\fc01_onepacket_20261113_v2`: đúng 7 source file, ngoài thư mục `__pycache__`.
- `_tmp\TTM_FC01_OWNER_CORPUS_20261113_v2`: có `FC01_OWNER_PRIVATE_DATA.json` và `FC01_SAFE_DATA_GENERATION_RECEIPT.json`.
- `_tmp\TTM_FC01_SOURCE_BUNDLE_20261113_v2`: gồm P02 module, parent checkpoint, T1 manifest, T4 TRAIN/VAL NPZ+manifest, và corpus V2; **không có TEST**.
- SAFE corpus receipt trong thư mục private có SHA `becc040...aa3`, 512 episodes mỗi arm, B/C giống nhau và số family chính xác.

**Đọc đúng thời điểm:** trong `FC01_SAFE_DATA_GENERATION_RECEIPT.json` trường `BPE_exact_check=NOT_YET_EXECUTED_NEEDS_OWNER_PINNED_MANIFEST` phản ánh lúc generator tạo corpus. Nó **không ghi đè** kết quả `BPE_EXACT=PASS` mà owner thu được ở lượt kiểm định và runner audit **sau đó**.

**Giới hạn provenance:** công cụ readback xác nhận sự tồn tại và nội dung biên nhận an toàn, nhưng chưa tự băm lại byte đầy đủ của file private trên node trong chính lượt này. Không gán nhãn independent-remote-full-file-hash khi bằng chứng chỉ là console owner + readback safe receipt.

## 3. Vì sao không cấp GO training ngay

Readiness khoa học còn ba điều kiện tích hợp **chưa được chứng nhận**:

- **Quyền sử dụng:** nguồn TinyStories tại local đã pin SHA nhưng owner cần xác nhận giấy phép/attribution đúng cách trước khi dùng trong lượt thí nghiệm mới; corpus synthetic mới giữ private, không xuất lên GitHub.
- **Runtime và checkpoint:** Colab Free T4, Torch/CUDA, FP32 và khả năng load mô hình P02 checkpoint thật chưa có receipt zero-step thực tế.
- **Resume và chi phí:** snapshot checkpoint/optimizer/RNG/sampler cursor trên Google Drive, hash readback/restart logical run và trần **3 GPU-hours, $0 paid** chưa có thử nghiệm xác thực.

Việc một runner đạt `--mode audit` **không tương đương** với khả năng chạy 3 nhánh gradient/resume thành công hoặc chứng nhận science GO. Không đánh tráo kiểm tra mã nguồn với benchmark Colab.

**Decision:** `FC01_SOURCE_QA=PASS_SCOPED` + `FC01_SCIENCE=HOLD_PREEXEC`. Không cấp ba micro-permit và không thay đổi tiêu chí primary/margin/CI/seed.

## 4. Bảo vệ các lượt cũ và chứng cứ

- V1 corpus SHA `7214213c79002943cbb9f7d0c6c25a81ba7f522c7218dcd4297a2c8465084bd6` giữ nguyên như nguồn thất bại BPE trước huấn luyện.
- V2 corpus SHA `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3` cố định.
- `DEV32=CLOSED`; `D1_CONFIRMATORY_512=HOLD`; `TEST_Q1Q2=SEALED`; `FC02_CAPACITY=NOT_OPENED`.
- `TRAINING=NO`; `GPU=NO`; `NEW_INFERENCE=NO`.
- `lineage.md` và `main` không sửa; đây là tiền kiểm tra, không phải phân xử kết quả khoa học confirmatory.
- Không phát hành raw private corpus hoặc checkpoint gốc lên GitHub.

## 5. Bước thực hiện tiếp theo — một gói tích hợp, không micro-permit

`TTM_SMALL4M_FC01_T4_FP32_DRIVE_RESUME_RIGHTS_SINGLE_INTEGRATED_SCIENCE_RELEASE_GO_HOLD_ZERO_TRAIN_STEPS`

Chỉ thực hiện **một** lượt hoàn chỉnh và khoa học chưa train: xác minh owner quyền và attribution cho nguồn đã pin; khởi tạo Colab Free T4 và đọc checkpoint P02 thực dưới FP32 với **zero optimizer steps**; thử lưu/đọc lại snapshot Drive bao gồm model/optimizer/RNG/cursor; nhận receipt SHA, ước tính compute/time trước khi huấn luyện và quyết định GO/HOLD **một lần cho toàn bộ A/B/C**. Nếu không đủ điều kiện, ghi HOLD chứ không bỏ gate. Cấm dùng notebook để khởi chạy mô hình huấn luyện khi science release chưa được cấp.

**Biên nhận máy công khai an toàn:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_V2_OWNER_EXACT_T1_SOURCE_QA_READBACK_AND_SINGLE_SCIENCE_HOLD_20261113.json`.
