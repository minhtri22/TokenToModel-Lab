# TTM PR #12 — Exact-head provenance and integrated QA closeout (source recovery)

**Ngày:** 2026-11-09. **Kho:** `minhtri22/TokenToModel-Lab`. **Trạng thái:** `SOURCE_PROVENANCE=PASS_20_FILES`, `OFFLINE_QA=PASS_233_TESTS_PLUS_Q1Q2_CONTRACT`, `MERGE=HOLD`.

## 1. Bằng chứng chính xác

Từ HEAD kiểm toán `dcf953e74df2029c7fef078314ae3999d5489561`, đã đưa 20 tệp nguồn nguyên byte và tất cả manifests vào cùng nhánh PR #12 bằng commit `b6e36d21b47d27619e2ee02ff15b0377d9cca9d4`. GitHub `git tree` readback cho thấy đủ **8 V5, 5 inference-only, 7 Q1/Q2**. Mỗi Git blob đối chiếu thành công với SHA1 Git blob của nguồn gốc; SHA-256 tương ứng nằm trong manifest ZIP gốc/receipt.

Đặc biệt: `Invoke-TTM-T5-Timewait-V5-PS51.ps1` là wrapper nguyên bản chưa vá, `*.patched.ps1` là wrapper sau vá đã dùng native; **không tự dùng lại các script one-shot V5 đã tiêu thụ**. Mục đích của việc lưu nguồn là audit và phục hồi kỹ thuật, không phải cấp quyền chạy lại.

## 2. Kiểm thử tích hợp tại môi trường ngoại tuyến

Trên Python 3.13.5, tách vào thư mục mới, xác minh SHA của từng tệp, chạy 5 nhóm: **47 V5 + 12 inference-only + 114 dual-attestation + 60 TCP-guard = 233 kiểm thử PASS**, và QA nguồn Q1/Q2 PASS (16 prompt, Q1 48 lần sinh theo kế hoạch, Q2 24 phép đo + 2 warmup). Receipt trên máy kiểm toán: SHA256 `0da3414ff251ddcf6a47f0692210e01e2893ada8fa1511309810931be426d632`. **Chưa chạy Windows T1–T4 synthetic regressions trên đúng HEAD mới**; không thay những receipt native V5 đã đóng.

## 3. Trạng thái merge

`HOLD`, dù GitHub không có xung đột, vì còn thiếu Windows T1–T4 integrated QA, kiểm toán quyền nguồn/dữ liệu công bố, rà soát CI và phạm vi PR rộng. Kết quả T4 VAL/TEST và T5 Ollama PASS được giữ nguyên; `T5_STRICT_PARITY=FAIL_7_OF_8` vẫn FAIL.

## 4. Đường QA Windows một lượt (chỉ fixtures)

Mã nguồn: `tools/qa/ttm_pr12_github_single_integrated_qa.py` và `tools/qa/Invoke-TTM-PR12-GitHub-Integrated-QA-PS51.ps1`. Quy trình tải từ GitHub theo commit, kiểm nguồn, clone vào project `_tmp` duy nhất, chạy QA T1/T2/T4 + T5/Q1Q2, ghi cả FAIL, push bằng Git fast-forward (không force), đọc lại từng receipt theo commit SHA, mới dọn tạm. **Chưa gọi Windows native** trong lượt này, mọi QA Windows ghi `PENDING`. Nếu thiếu thư viện hoặc nguồn phụ, báo HOLD đúng nguyên nhân, không tự cài package, chạy lại science hay mở nhánh mới.

**Bước thực hiện tiếp theo:** `TTM_PR12_GITHUB_SOURCE_EXACT_HEAD_WINDOWS_INTEGRATED_QA_AND_MERGE_REVIEW`. Đánh giá merge cuối lượt: `HOLD`; không merge, không đổi `main` hoặc `lineage.md` và không xóa nguồn/evidence lịch sử.
