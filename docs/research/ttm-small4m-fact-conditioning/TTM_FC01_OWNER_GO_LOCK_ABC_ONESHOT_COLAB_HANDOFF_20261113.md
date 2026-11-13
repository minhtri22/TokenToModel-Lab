# FC01 V2 — Owner GO lock và bàn giao một lượt A/B/C trên Colab T4 FP32

**Operation:** `TTM_SMALL4M_FC01_OWNER_SINGLE_GO_LOCK_AND_ABC_ONE_SHOT_T4_FP32_EXECUTION`

**Owner authorization:** người dùng đã nhắn `Tôi cho phép thực hiện` ngày 13/11/2026. Không suy diễn đây là chữ ký mật mã (cryptographic signature).

## Trạng thái thực tế

- Quyết định readiness từ gói zero-step trước đó: `GO_FOR_ALL_THREE_ARMS`, nguồn, quyền self-attestation, T4 FP32 và snapshot Drive SHA đã kiểm.
- Đã phát hành `FC01_OWNER_GO.json` vào thư mục riêng tư `TTM/ttm-small-pilot/ttm_small4m_fc01_fact_conditioning_20261113/input/` trên Google Drive, **SHA-256 `8b274e3bc976e73ad25a689e8044dda2fcb98766a8d2cdd890cb08d6f582c091`**. Đã đọc lại byte từ Drive và xác minh bằng đúng mã hàm `validate_go()` của runner V2 trên CPU: **PASS**.
- Đã bổ sung 3 module Python bị thiếu trực tiếp lên Drive mà không yêu cầu user download: `fc01_build_private_corpus.py` (`a9978a19…`), `fc01_integrated_static_qa.py` (`f4f205ed…`), `fc01_pinned_bpe.py` (`d90ddbcd…`). Byte từ Drive đã đọc lại, SHA-256 PASS cả 3.
- Đã xác nhận folder input chứa 10 tệp khoa học + 1 GO lock. Không công bố raw corpus, checkpoint hay private holdout trên GitHub.
- **`COLAB_KERNEL_JOB=NOT_SUBMITTED`**, **`FC01_TRAINING=NOT_STARTED`**, **`NEW_OPTIMIZER_STEPS=0`**, **`EVAL64=NOT_EXECUTED`**. Google Drive connector có thể đọc/ghi file nhưng **không có API truy cập hay chạy kernel Colab**. Không đánh tráo GitHub notebook/GO thành chạy khoa học.

## Hợp đồng thực thi

- Frozen runner ở chính thư mục Drive input: `fc01_train_eval_once.py`; file SHA `b786a4468ba104786df7683da9b1cf19d2334d9cc203dd19c3e7d6f10e2e93be`.
- Bất biến (immutable): corpus V2 SHA `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3`, P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, checkpoint step1024 SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, T1 BPE SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, T4 private TRAIN/VAL pack SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`.
- **Ba nhánh, một release:** A=`A_BASE_MLE` → B=`B_CF_MLE` → C=`C_CF_CONTRAST`, mỗi arm 256 optimizer steps, tổng 768. FP32, Colab Free Tesla T4, paid USD=0, 3600 GPU seconds/arm, tổng 10800 seconds. Cấm nguồn khác, seed khác hoặc micro-permit tự động.
- Sau A/B/C mới chạy `evaluate` trên FC01 EVAL64 nội bộ và `secondary` tạo gói blind96 chưa chấm điểm. D1 confirmatory và TEST/Q1Q2 giữ nguyên SEALED/HOLD.
- Notebook đặt `CUBLAS_WORKSPACE_CONFIG=:4096:8` trước các tiến trình Python child trên CUDA; kiểm GO SHA và mọi SHA input, chạy audit trước science, giám sát cap bằng timeout, ghi log, biên nhận terminal, tuyệt đối không tự động rerun hoặc reseed.
- Bản snapshot step0 đã PASS chỉ xác minh thành phần lưu/khôi phục; không giả định restore AdamW tại bước 64 đã PASS. Nếu lỗi, giữ bằng chứng, trạng thái HOLD terminal, không tự khởi chạy lượt khác.

## Một thao tác cần thực hiện trên Colab

Notebook GitHub đã khóa:

`tools/pilot_t4/fc01/TTM_FC01_OWNER_GO_ABC_ONESHOT_T4_FP32_20261113.ipynb`

1. Mở notebook trong Google Colab (có thể vào `File → Open notebook → GitHub`, dùng đường dẫn GitHub từ HEAD ghi trong giao diện).
2. Chọn đúng **Free Tesla T4** (không nâng cấp trả phí).
3. Chạy **một cell code duy nhất, một lần**. Notebook từ chối chạy nếu GO SHA thay đổi hoặc đã tồn tại output science.

Thư mục kết quả riêng tư sau khi chạy: `MyDrive/TTM/ttm-small-pilot/ttm_small4m_fc01_fact_conditioning_20261113/FC01_ABC_ONE_SHOT_V2_20261113/`.

Đầu ra quyết định: `FC01_ABC_ONE_SHOT_TERMINAL_RECEIPT.json` và `FC01_ONE_SHOT_TERMINAL_RECEIPT_SHA256` trên stdout, hoặc terminal HOLD có log chi tiết. Cần QA độc lập hậu nghiệm, không gọi kết quả A/B/C là PASS trước khi đối chiếu checkpoint/hash, budget và scorer.

**Next action:** `TTM_FC01_ONE_COLAB_CELL_EXECUTION_AND_TERMINAL_EVIDENCE_READBACK`; chỉ một lần chạy, không thêm quyền phê duyệt, không thay đổi hợp đồng. `MAIN=UNCHANGED`, `LINEAGE_MD=UNCHANGED` đến khi có evidence science terminal.
