# TTM P04 — Phán quyết QA Windows CPU và điều kiện đóng P04 trong phạm vi synthetic

Ngày 07/11/2026. PR #8 HEAD nguyên gốc đã chạy: `9d9a366c92b14f8e235a20954fa2782a17d74a49`; base `94b01b4817c3c11c8b9a9cbbc01bfc867066a596`.

## Kết luận

**`P04_PASS_SCOPED_SYNTHETIC_CPU_READY_FOR_EXACT_HEAD_MERGE`**. Các yêu cầu kỹ thuật P04 đã kiểm tra trong phạm vi CPU/đầu vào synthetic: checkpoint lưu mới không ghi đè, phục hồi trọng số chính xác với SHA-256 và mã BPE pin, sinh token theo seed/top-k, chống input sai, đánh giá NLL/perplexity trên synthetic held-out, không cập nhật trọng số.

Không tuyên bố P04 đã đánh giá chất lượng mô hình trên văn bản thật, không đánh đồng synthetic held-out với held-out của F1. P03 chưa hề huấn luyện mô hình ngôn ngữ trên corpus thật; kết quả P04 này chỉ xác nhận **cơ chế đánh giá hoạt động đúng**.

## Bằng chứng và bản ghi FAIL được bảo toàn

1. V1 FAIL tiền kiểm ở `git ls-remote origin` khi lệnh không chạy trong repo. Receipt gốc còn ở `evidence/p04/TTM_P04_WINDOWS_CPU_SYNTHETIC_QA_20261107_20261107T222344_P6284.json`; SHA-256 `02f5b48c6fd1f615096a895b3b51185aa3f172630909e3526d0c5e2ef5db3d13`. Hai bộ QA chưa chạy trong lượt này; không có worktree tạo ra. Không sửa hoặc xóa biên bản FAIL.
2. V2 sửa đúng một bước Git CWD, PowerShell script SHA-256 `b6e65851adbe204085842998ab6b3f11622c04255266e29ba805e53842db6c9f`. Receipt `evidence/p04/TTM_P04_WINDOWS_CPU_SYNTHETIC_QA_20261107_20261107T223213_P32016.json`, SHA-256 `3a9ff268acfa4371c9ab2026ae17afdd19fb398b8039b0ffa2127f8e906884b6`.
3. Byte receipt V2 đã được khôi phục chính xác với UTF-8 BOM và CRLF; Git blob `7636b4113478f8c6dfde7040a16a3026b90b6751` trùng byte tệp đính kèm gốc. Git và 5 source blobs khớp.
4. Unit: **6/6 PASS**, exit 0, `Ran 6 tests in 0.142s / OK`. SHA log theo runner `ee61c2c948533426a5d63278c502b31430af5c61d9398e16c0019894741afe62`.
5. Independent: **4/4 PASS**, exit 0; gồm khôi phục thông số, từ chối sai tokenizer, greedy so với sequential argmax và tính lại NLL synthetic heldout mà trọng số không đổi. SHA log theo runner `0973efb1b5b73d363d5184e39b21082683ff1b712c759cde8456a45c0daa58ac`.
6. Lưu ý minh bạch: log unit do PowerShell tạo có dòng `NativeCommandError` ở header của test đầu tiên khi ghép luồng stderr, nhưng phép kiểm thử hoàn tất với mã thoát 0, cả sáu test `ok`, không có thất bại trong unittest. SHA hai log được lấy từ receipt Windows; lượt thẩm định đọc nội dung nhưng không tính lại byte SHA hai log.
7. Python 3.12.10, PyTorch 2.11.0+cpu; ghi nhận cleanup `PASS_OWNED_WORKTREE_ONLY`. Runner không sửa local `main`; local HEAD `92facee15...` cũ, đồng bộ là việc tách riêng.

## Phạm vi và hướng P05

- Dữ liệu: `SYNTHETIC_TOKEN_IDS_ONLY`; không dùng WP30 TEST, không mở real heldout. F1 ban đầu chỉ cho E0 BPE nội bộ; không có quyền suy diễn cho huấn luyện GPT công khai.
- Không thực hiện huấn luyện P03 mới trong lượt P04; không có checkpoint từ huấn luyện GPT thực trên corpus.
- `lineage.md` không đổi trong PR này vì đây là QA kỹ thuật, không phải công bố một kết quả khoa học về khả năng tổng quát.
- Sau khi PR #8 được rà soát và merge đúng HEAD, `P04_TECHNICAL_EXIT=PASS_SCOPED_SYNTHETIC_CPU`, có thể mở nhánh P05 Dense KV Cache chỉ cho QA kỹ thuật. Các phép đo held-out thật vẫn `NOT_EXECUTED`, phải được xử lý bằng quyết định nguồn và thực nghiệm riêng.

**Bước tiếp theo:** Rà soát exact HEAD/diff/receipt và merge PR #8 nếu GitHub không có conflict; sau đó mở P05 từ main merge commit, không chạy lại P01–P04.
