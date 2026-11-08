# TTM T5 — Tiếp nhận kết quả QA tĩnh Windows cho TCP owner guard V3 (2026-11-09)

## 1. Kết quả và xuất xứ
- Người dùng đã chạy `Check-TTM-T5-TCP-Guard-V3-PS51.ps1` trên Windows. Console: `T5_V3_SOURCE_SHA256=PASS`, **60/60** unittest `ok`, `Ran 60 tests in 0.077s`, `OK`, `T5_V3_WINDOWS_STATIC_QA=PASS_60_OF_60`.
- Hai bài negative QA `test_execute_argument_rejected_by_argparse` và `test_execution_lock_blocks_before_evidence` đều PASS. Dòng `invalid choice: 'execute'` là phản ứng đã dự kiến, không phải lỗi kiểm định.
- Báo cáo từ console, **không phải** phép chạy Windows trực tiếp bởi agent. Danh sách 60 bài kiểm thử đối chiếu từ nguồn checker đã ghim trong PR #12.
- Gói nguồn ZIP: SHA256 `ab4bcbe1d9e591f124b90fc5d342e93b6ae0a042b405053cbd7b437d8d691c71`; manifest và 60 tên bài thử đã được đối chiếu trên nguồn.

## 2. Phân xử
- `V3_WINDOWS_SOURCE_STATIC_QA=PASS_SCOPED_60_OF_60`.
- `V3_SOURCE_ONLY_EXECUTION_LOCK=ACTIVE_NO_RUNTIME_PERMIT`: candidate hiện chỉ chấp nhận `--mode contract`, và hàm `execute()` có khóa cứng. Nghiêm cấm thay thế bằng `--mode execute` trên tệp hiện tại.
- `V3_TCP_TABLE_NATIVE_READBACK=NOT_EXECUTED`: 60 bài thử chỉ dùng fake adapters; chưa gọi bảng TCP thực trên Windows bằng candidate.
- `V3_OLLAMA_COMPATIBILITY=NOT_TESTED` (chưa nhập GGUF, chưa sinh token); V1/V2 đã tiêu thụ và giữ nguyên.
- `T5_FULL_LOGITS=FAIL_7_OF_8_PRESERVED`; không thay `lineage.md`, GGUF/checkpoint, hoặc `main`.

## 3. Quyết định và giới hạn
Chấp nhận phần **kiểm định tĩnh V3** và đóng bước sửa nguồn. Không coi `PASS_60_OF_60` là đủ để **mở khóa thực thi của bản candidate hiện tại**. Mở khóa chỉ qua một bản **release candidate mới có SHA riêng**, kèm kiểm tra đóng lỗi cho đường chạy thật: xác thực bằng chứng Windows, PID + creation time + executable path, `State=Listen`, loopback bind, tái xác nhận sau HTTP, model-store project-local, fail-closed khi kết quả không nhất quán; kiểm định độc lập trước khi cấp lệnh thử một lần.

**Bước thực hiện tiếp theo:** `TTM_T5_TCP_OWNER_GUARD_V3_GUARDED_SINGLE_SMOKE_RELEASE_CANDIDATE_QA_THEN_EXECUTION_DECISION` — gộp sửa bản chạy thật và một quyết định duy nhất. Không chạy V1/V2, không chạy `--mode execute` trên source-only V3 hiện tại, chưa mở thử nghiệm khoa học mới.
