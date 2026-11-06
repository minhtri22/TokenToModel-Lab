# TTM P01 — Cổng quyết định cấp quyền I0A riêng biệt (chưa cấp)

**Mã cổng:** `TTM_P01_D1_I0A_SEPARATE_PERMIT_GATE_DECISION`  
**Ngày:** 05/11/2026. **Trạng thái:** `PREAUTH_HOLD_NOT_GRANTED`.  
**Repository:** `https://github.com/minhtri22/TokenToModel-Lab.git`.  
**Nhánh hồ sơ:** `design/p01-tokenizer-data-prereg-20261105`, PR #4 (Draft).  
**Mốc GitHub main bảo vệ:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Bản ghi này KHÔNG phải giấy phép triển khai hay bằng chứng worktree P01 tồn tại.**

## 1. Những điều kiện đã chứng minh và những điều kiện chưa chứng minh

- I0A-01: PASS_READONLY_OBSERVATION trên console do người dùng cung cấp, main/origin/P00 đúng mốc, 2 worktrees, Git sạch; cần recheck khi thực hiện một permit tương lai.
- I0A-02: **HOLD_FULL_PATH_ACL_AUDIT**. Chưa có kết quả Get-Acl trên các thư mục cha và .git/worktrees, chưa thẩm định ACE ghi, junction và ACL thực tế trong token của worker tương lai. Bằng chứng chỉ có `P01_CANDIDATE_EXISTS=False` và mô tả đường dẫn.
- I0A-03,04,05,06,08: PASS_DESIGN_ONLY. Golden bytes/allowlist/checker/Job Object mới ở mức đặc tả.
- I0A-07: PASS_TIMESTAMPED_SNAPSHOT (RAM 9.345 GiB, D: 34.830 GiB tại 21:21:38 ICT ngày 05/11/2026); phải đo lại tại thời điểm cấp phép.
- I0A-09: NOT_GRANTED; không có quyết định cụ thể của chủ sở hữu cho một lượt tạo worktree và viết mã.

**Phán quyết cổng:** `I0A_PREAUTH_ADMISSION=HOLD_PATH_ACL_AND_OWNER_PERMIT`; `I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`.

## 2. Điều kiện nếu muốn trình một permit mới trong tương lai

Một văn bản permit thực thi I0A riêng biệt phải chỉ rõ và được chủ sở hữu chấp thuận:
1. Exact commit `HEAD` của nhánh P01 và GitHub main, repo origin, đường dẫn local root và đề xuất worktree đúng một vị trí dưới project.
2. Allowlist tên từng tệp để tạo/sửa, vùng dữ liệu F0-only và denylist tất cả đường dẫn ngoài dự án/P00.
3. Đường QA tĩnh, điều kiện FAIL, SHA checker/generator sau triển khai, cơ chế không tự chạy kiểm thử động và không tự thu thập F1/F2.
4. Trần `max_job_commit_bytes=4294967296`, wall-clock 1800s, quota disk 2 GiB; làm rõ thiết kế guard tương lai, không dùng ngưỡng trước chạy thay QA0.
5. Một lượt duy nhất, không tự rerun, không merge, không cleanup, quyền Git push/bằng chứng và thẩm định độc lập.
6. Console ACL/path đọc được và đã được thẩm định; xử lý mọi nghi ngờ reparse và broad ACE; không xem kết quả Get-Acl của parent như bảo đảm sandbox isolation trong runtime.
7. Quyết định chữ nghĩa rõ `PERMIT_GRANTED` từ chủ sở hữu **trong một bước khác**, không suy từ việc đọc tài liệu này.

Khi chưa có những điều kiện này, **không được** `git worktree add`, tạo mã `qa/p01`/`runtime/p01`, lưu fixture, chạy Job Object/Write Broker, tải nguồn, học BPE/GPT hay hợp nhất PR.

## 3. Bất biến và giới hạn

- `P01_D1_SOURCE_SCOPE=F0_ONLY_DESIGN_AND_ORACLE_REVIEW`.
- `P01_D1_H04_CHECKER_CONTRACT=PASS_10_OF_10_DESIGN_ONLY`, `P01_D1_H04_DYNAMIC_QA=NOT_EXECUTED`.
- `P01_D1_H02_F1_F2_SOURCE_ADMISSION=HOLD`.
- `P01_D1_H05_GUARD_QA=NOT_EXECUTED`.
- `P01_D1_SCIENTIFIC_PREREG_LOCK=NOT_GRANTED`.
- `I0A_PATH_ACL_READONLY_CONSOLE=NOT_RECEIVED`.
- `I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`.
- `QA0_EXECUTION_PERMIT=NOT_GRANTED`.
- `E0_SCIENTIFIC_PERMIT=NOT_GRANTED`.
- `P01_WORKTREE_CREATE=false`, `P01_DOWNLOAD=false`, `P01_TRAINING=false`, `P00_CLEANUP=false`, `PR4_MERGE=false`.

**Bước tiếp theo:** `TTM_P01_D1_I0A_PATH_ACL_WINDOWS_CONSOLE_ADJUDICATION` — lấy đúng console read-only Get-Acl/reparse trên máy Windows, kiểm tra và phân xử PASS/HOLD/FAIL, sau đó mới xem xét một permit I0A chính xác riêng. Không tự cấp.
