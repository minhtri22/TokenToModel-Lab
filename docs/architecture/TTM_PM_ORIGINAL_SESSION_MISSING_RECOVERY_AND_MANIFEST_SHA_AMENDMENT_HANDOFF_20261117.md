# TTM PM — Colab ORIGINAL_SESSION_PARENT_MISSING và sửa manifest SHA trước science

**Operation:** `TTM_PM_ORIGINAL_SESSION_MISSING_TECH40_RECOVERY_AND_MANIFEST_SHA_AMENDMENT_20261117`  
**Ngày:** 17/11/2026 · **PR:** #44 · **Source-of-truth:** GitHub.  
**Original main:** `59ee3f30b996405fddc087ab60102b59a021f8ea`, không thay đổi.

## 1. Đọc log owner và phân xử đúng gate

Owner Colab: `MODE=BRIDGE_PREFLIGHT`, `EXACT_SOURCE_PINS_PASS=8`, `SCIENCE_REQUESTED=false`, exit code 1 do `find_original(): ORIGINAL_SESSION_PARENT_MISSING`.

Đây là không tìm thấy **thư mục tạm của runtime** `/content/TTM_MATCHED_4M_SESSIONS`; chưa tới bước hash receipt, TinyStories, checkpoint, optimizer, hoặc TEST. Không suy diễn nguyên nhân chắc chắn: runtime mới/reset, nội dung bị dọn hoặc đường dẫn khác đều có thể. Colab thực tế cần readback.

Đã tìm trên Google Drive nối với ChatGPT theo tên `TECHNICAL_SYNTHETIC_40.json`, `TTM_40_1024`, `TECH40`: không có kết quả. Kết quả này không chứng minh file đã bị xóa; chỉ không tìm thấy trong phạm vi Drive đã lập chỉ mục. Log owner vẫn là bằng chứng scoped TECH40 PASS; **raw receipt SHA còn HOLD**.

## 2. Blocker tiếp theo được source QA phát hiện

Runner gốc Git blob `113434e25fe19cff27b47f428cf99a0a57ae4fcf` và runner sửa GPU `933f42b514de5fac650bfa2a421844c51b9b7c64` đều khai báo:

`MANIFEST_SHA = "ef2e6e67d49b1d5a921b1051df329f15574f1c10cece49468acb53322d650"` — **61 ký tự, không thể là SHA-256**.

Dấu SHA-256 **thực** từ Google Drive private TinyStories manifest được kiểm tra trước đó:

`ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650` — 64 ký tự.

Do `validate_pack_files` so sánh byte hash với hằng sai, **bất kỳ** phiên huấn luyện thực nào chạy trực tiếp runner gốc trước bản sửa đều sẽ dừng với `HISTORICAL_TRAIN_VAL_BYTES_NOT_IDENTICAL`. Đây là lỗi implement trước khoa học chứ không phải lỗi dữ liệu.

**Khắc phục hạn định:** `tech40_continuation.restore_frozen_runner_manifest_digest_in_memory(original_runner)` chỉ sửa hằng `MANIFEST_SHA` trong module Python đã import, sau khi kiểm tra giá trị lỗi 61-char đúng SHA nguồn bất biến; nếu source khác thì từ chối. Git blob runner, toàn bộ hàm khoa học, recipe SHA, dữ liệu và checkpoint không thay đổi. QA đã bổ sung trường hợp 61→64 và mismatch âm. Hai quyết định Q4 ghim SHA manifest **thực**.

**Lưu ý custody receipt cũ:** SHA ứng viên được ước tính từ stdout không chứng minh file gốc. Bridge chỉ chấp nhận byte thật có SHA-256 tính lại **trùng `SESSION_STATUS.json.technical_receipt_sha256`**, khóa phiên, nội dung receipts và source Git blob đều khớp. Không phục dựng file khi mất.

## 3. Hai tuyến giải quyết — cùng một quyết định PM có điều kiện, không micro-permit

### A. Có receipt gốc (ưu tiên, không chạy lại TECH40)

Trong Colab, `MODE="SESSION_LOCATE"`. Nếu còn receipt và lock/status gốc, dùng `MODE="BRIDGE_PREFLIGHT"`, rồi `MODE="CONTINUE_VERIFIED_40_1024"`. `OLD_SESSION_EXPLICIT` được hỗ trợ nếu owner có thư mục phiên gốc ở vị trí khác. Runner cũ chỉ được import sau exact blob validation, manifest SHA correction explicit/allowlisted.

### B. Không còn bất kỳ receipt gốc nào (phương án recovery thực, **có chạy TECH40 mới**)

**PM Q4 riêng:** `GO_CONDITIONAL_FRESH_TECH40_RECOVERY_1024_VAL_ONLY`; riêng cho tình huống mất file gốc, không phải ủy quyền chung và không phải phục hồi giả chứng cứ.

- `MODE="RECOVERY_PREFLIGHT"`: kiểm Git blob nguồn, quyết định Q4, SHA-256 NPZ/manifest/checkpoint, owner Drive mount, không tạo file, không huấn luyện. Từ chối khi tìm thấy receipt gốc trong thư mục phiên hoặc Drive backup; ưu tiên tuyến A.
- `MODE="RECOVERY_ONEPACK"`, `RECOVERY_RUN_ID` **mới, duy nhất**: trên Colab T4, kiểm CUDA/Python/VRAM trước, ghi `RECOVERY_Q4_LOCK.json` lên owner Drive, chạy **40 bước synthetic mới** bằng runner gốc đã sửa hằng manifest trong RAM và lưu **receipt thực** `TECHNICAL_SYNTHETIC_40.json` lên Drive. Chỉ khi receipt mới PASS và kiểm tra exact source/data/checkpoint đã đạt thì khởi tạo GPT P02 mới seed 20261108 huấn luyện TinyStories 1024 bước; checkpoint 256/512/768/1024; so sánh historical LEFT@1024 vs new RIGHT@1024 trên 256 VAL, 2.000 bootstrap. Không truy cập TEST.
- Nếu Colab preempted sau checkpoint có `READY.json`, dùng `MODE="RECOVERY_RESUME"`, `RESUME_FROM_STEP=256|512|768`; nếu đã huấn luyện xong và chỉ thiếu paired VAL thì `RECOVERY_RESUME` với `None`. Không đổi `RECOVERY_RUN_ID`.
- Mọi dữ liệu/receipt mới được ghi ở owner Drive: `/content/drive/MyDrive/TTM/ttm-small-pilot/TTM_FRESH40_RECOVERY__<RECOVERY_RUN_ID>`. Không chuyển trọng số của 40 synthetic sang huấn luyện mới.

Điều kiện phản bác: thiếu owner Drive, không đúng T4, thiếu SHA private, checkpoint lịch sử thay đổi, source blob drift, Q4 drift, output có sẵn, hoặc tìm được receipt gốc đều phải **HOLD** trước huấn luyện, không fallback tự động.

## 4. QA nguồn, bằng chứng và diễn giải khoa học

Các file:
- `src/ttm_new_gpt_baseline/tech40_continuation.py`: tuyến A và correction SHA in-memory.
- `src/ttm_new_gpt_baseline/tech40_fresh_recovery.py`: tuyến B với fresh tech40 và recovery.
- `tests/ttm_new_gpt_baseline/test_tech40_continuation.py`, `test_tech40_fresh_recovery.py`.
- `docs/architecture/TTM_PM_Q4_TECH40_REUSE_1024_VAL_ONLY_DECISION_20261117.json`, `TTM_PM_MISSING_TECH40_RECOVERY_Q4_DECISION_20261117.json`.
- `notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb` triển khai cả hai chế độ và cố định source SHA.

Source QA tại commit code `f4916c342e534c6ceea6f63271ad7fdba7376e06`: **PASS** Python3.12 Ubuntu/Windows, 13 runner tests + 56 separate source/negative QA tests mỗi OS. Native CPU synthetic full P02 checkpoint resume PASS scoped, không phải GPU T4 TinyStories.

**Hạn chế:** các kiểm thử do cùng trợ lý tạo và chạy trên môi trường GitHub Actions, chưa phải đánh giá tổ chức/human độc lập. Không thể chạy Colab của owner từ GitHub CI. `NEW1024=NOT_EXECUTED`, `PAIRED_VAL=NOT_EXECUTED`, `TEST_NOT_ACCESSED`.

**Khoa học:** hai model vẫn cùng GPT P02/seed/dữ liệu/optimizer. Kết quả new@1024 chỉ là **replication**, chưa phải chứng cứ một phương pháp mới cải thiện Small-4M. Nghiên cứu so sánh SSM/SSM+Ledger là hướng riêng biệt, không trộn trong này.

**Bước thực hiện tiếp theo — duy nhất:** owner chạy `SESSION_LOCATE` trên Colab; nếu receipt gốc mất, `RECOVERY_PREFLIGHT` rồi `RECOVERY_ONEPACK`. Không yêu cầu owner viết lại receipt, tạo permit hay sửa script thủ công; mặc định notebook vẫn `SOURCE_QA`.
