# P01 I0A-S — Phân xử sửa mã tĩnh và chuẩn bị smoke F0 (QA0 chưa chạy)

**Thao tác:** `TTM_P01_I0A_S_STATIC_SOURCE_FIXUP_AND_QA0_F0_SMOKE_PREP`  
**Ngày:** 06/11/2026. **Repo:** `minhtri22/TokenToModel-Lab`.  
**Nhánh mã:** `implementation/p01-i0a-s-f0-static-20261106`.  
**Commit tiền nhiệm:** `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`.  
**Commit đã ghi mã sửa và suite QA0:** `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Nhánh tài liệu:** `design/p01-tokenizer-data-prereg-20261105`; PR #4 là Draft, chưa được hợp nhất tại lúc phát hành báo cáo.

## 1. Ràng buộc và trạng thái

Đây là **lượt sửa mã nguồn** sau khi I0A-S tạo đúng 12 file lần đầu; không phải chạy lại I0A-S hay mở bất kỳ lượt khoa học nào. Mã QA0 mới **chưa được thực thi, chưa import vào interpreter, chưa có signed receipt**. QA0 vẫn cần quyết định runtime một lần riêng, sau khi có cách ly thật hoặc môi trường kỹ thuật được chứng minh an toàn.

Nhánh triển khai có **đúng một commit kế tiếp**, GitHub `ahead_by=1,behind_by=0` từ `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`. Có **5 đường dẫn thay đổi**:
- Modified: `runtime/p01/source_scope_guard.py`, `src/p01/byte_bpe.py`, `src/p01/data_dedup_split.py`.
- Added: `qa/p01/qa0_f0_smoke_test.py`, `docs/qa/P01_I0A_S_F0_SMOKE_PREPARATION.md`.
- Không thay P00, `main`, `lineage.md`, cấu hình P00, data/model/trainer hay nhánh thiết kế trong commit mã.

**Lưu ý nguồn làm việc:** mã mới được ghi lên **GitHub** bằng atomic tree+commit+ref fast-forward với expected old head; **chưa đồng bộ về worktree Windows**. Không được tự reset/clean worktree để đồng bộ.

## 2. Hai phát hiện cũ và cách sửa

**FINDING-01 — kiểm kiểu trước truy cập dữ liệu:** `classify_f0_documents` hiện kiểm tra `type(doc) is Document`, `document_id` chuỗi không rỗng, `raw` đúng bytes, `approved/pii_reviewed is True`, ID không trùng và số byte cộng dồn **trước** `sorted()` hoặc `canonical_key`. Dữ liệu UTF-8 không hợp lệ được cách ly bằng lỗi `SourceScopeError("QUARANTINE_OR_REJECT")`; `assign_splits` từ chối group-id sai cấu trúc trước khi `bytes.fromhex`. **Chưa có kết quả chạy thử trên Windows.**

**FINDING-02 — chuỗi marker không đủ chứng minh nguồn:** helper `require_f0_literal_bytes` mới đối chiếu SHA-256 bytes với đúng 12 mẫu `F00..F11` và oracle `M01=abababab`. Cả `learn_merges_f0_qa0_only` và `classify_f0_documents` đều dùng helper này, nên **chỉ cấp marker đúng** không còn đủ để đưa bất kỳ byte nào vào hai hàm này. Đây là **giới hạn nội dung**, không phải cơ chế chứng thực quyền nguồn; không chứng minh worker không đọc/ghi ngoài workspace và không mở H02/F1/F2/TEST. `ByteBPE.encode_bytes` vẫn cho phép hoàn nguyên byte tùy ý theo hợp đồng B0; không coi nó là hàm ingest corpus.

Đã xác minh riêng SHA-256 oracle M01 trong môi trường đánh giá độc lập: `SHA256(b"abababab")=9ba3d1c770bd1d031494bbd49d53e1e0b6b5512a4b3a2d56d274e4bb173a2a00`.

## 3. Danh sách 10 bài smoke chuẩn bị

`qa/p01/qa0_f0_smoke_test.py` chứa **10 phương thức** `unittest.TestCase.test_*`; đây chỉ là **bộ mã nguồn**, không tạo receipt tự động, không có `__main__`, không gọi subprocess, không thực hiện ghi tệp hay truy cập mạng.

| Case | Nội dung kiểm tra | Đích xác nhận |
|---|---|---|
| S01 | B0 đầy đủ byte 0..255 | Round-trip |
| S02 | F00–F11, băm nguồn và round-trip | Byte exact |
| S03 | Unicode dạng dựng sẵn/tổ hợp, UTF-8 lỗi | Strict, không thay byte |
| S04 | ID âm, bool, float, ngoài miền | Từ chối |
| S05 | M01 từ F0, merges và SHA độc lập | Byte BPE tất định |
| S06 | Sửa 1 byte hoặc thêm byte vào merges | Checker độc lập từ chối |
| S07 | Document kiểu sai hoặc trường sai | Từ chối trước khi đọc thuộc tính |
| S08 | F02/F03 nhóm canonical, ít hơn 30 group | Same group, split từ chối |
| S09 | Dữ liệu/marker không được phép | F0 content pin và admission từ chối |
| S10 | Guard/Write Broker/corpus/receipt chưa có | Fail-closed |

Các kiểm tra tĩnh GitHub đã thực hiện: readback branch `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`; đúng 1 commit, 5 path; 10 định nghĩa method test, không có tự chạy hay import subprocess/network hoặc file write trong test; soát nội dung check trước sort và bytes pin. **Chưa chạy `ast.parse`/compile độc lập trên chính byte của toàn bộ mã GitHub trong bước này; không được ghi `SYNTAX_QA_PASS` từ kiểm tra tên hàm đơn thuần.** Bộ suite không thay thế test âm tính W01–W12 và không đủ để kết luận Windows Job Object/Write Broker hoạt động.

## 4. Phán quyết

`I0A_SOURCE_FIXUP_COMMITTED=YES`  
`I0A_FIXUP_BASE_SHA=7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`  
`I0A_FIXUP_HEAD_SHA=f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`  
`I0A_FIXUP_GIT_SCOPE=PASS_3_MODIFIED_2_ADDED`  
`I0A_FIXUP_STATIC_CONTENT_REVIEW=PASS_SCOPED_WITH_CAVEATS`  
`I0A_FIXUP_EXTERNAL_PYTHON_SYNTAX_CHECK=NOT_EXECUTED`  
`QA0_F0_SMOKE_SUITE=PREPARED_10_NOT_EXECUTED`  
`QA0_DYNAMIC_PERMIT=NOT_GRANTED`  
`E0_SCIENCE_PERMIT=NOT_GRANTED`  
`P00_CLEANUP_AUTHORIZED=false`  
`P01_WORKTREE_CLEANUP_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`.

**Bước tiếp theo:** `TTM_P01_QA0_F0_SMOKE_SAFE_SYNC_STATIC_PREFLIGHT_AND_RUNTIME_DECISION`. Kiểm tra worktree P01 Windows **chỉ đọc**: Git status sạch, exact origin, HEAD cũ `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`, branch và đường dẫn trong project; sau đó, nếu đủ điều kiện, chỉ `git fetch` + `merge --ff-only` tới `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0` (không reset/clean). Kiểm tra cú pháp source bằng AST **không import** và khóa runtime sandbox trước khi phê duyệt đúng một lượt smoke. Không tự chạy smoke vì có suite.
