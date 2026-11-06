# P01 I0A-S — Thẩm định độc lập sau lượt triển khai mã nguồn tĩnh B

**Mã:** `TTM_P01_I0A_S_B_ONE_SHOT_STATIC_AUTHORING_RESULT_AND_INDEPENDENT_QA`  
**Ngày đánh giá:** 06/11/2026 (đánh giá GitHub sau console của người dùng).  
**Repository:** `https://github.com/minhtri22/TokenToModel-Lab.git`.  
**Nhánh triển khai (không thay đổi trong QA này):** `implementation/p01-i0a-s-f0-static-20261106`.  
**Commit khóa:** `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`.  
**Parent verified through Git data:** `cb91bae3201f9ef6bc7f26fe045ad51aa01b9279`.  
**Thẩm định này chỉ đọc mã GitHub và console do người dùng gửi. Không chạy/import Python P01, không thực thi tests, không gọi Windows Job Object hay tạo fixture.**

## 1. Provenance

Người dùng cung cấp transcript PowerShell 5.1 trên máy `DESKTOP-4PSD0G2`. Chương trình kiểm `SCRIPT_SHA256=PASS` cho SHA-256 script `247646832e5939fd9cf9d3329eedb89fad394fd418c46caa354e1f65042dd6f1`. Bắt đầu `2026-11-05T19:28:59.0252054Z` (02:28:59 ngày 06/11 ICT). Log báo `RAM_FREE_GIB=12.728`, `D_FREE_GIB=34.830`, `PREWRITE_CHECK=PASS`, tạo worktree mới đúng tên, push một nhánh mới và kết thúc `TTM_P01_I0A_S_B_END` với `QA0_DYNAMIC_EXECUTION=NOT_PERFORMED`, `E0_SCIENTIFIC_EXECUTION=NOT_PERFORMED`, `CLEANUP=NONE`.

**Giới hạn chứng cứ:** console là trích từ hội thoại, không có file gốc signed receipt; không thể từ GitHub tự xác minh trạng thái RAM/ACL/worktree sạch trên Windows **sau** khi chạy. `PREWRITE_CHECK=PASS` là lời báo của chương trình; GitHub giúp kiểm nội dung được đẩy lên.

## 2. Kiểm toán Git và phạm vi

- GitHub ref `refs/heads/implementation/p01-i0a-s-f0-static-20261106` trỏ chính xác commit `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`.
- Git commit có chính xác **một parent** là `cb91bae3201f9ef6bc7f26fe045ad51aa01b9279`; compare GitHub từ parent sang ref: `ahead_by=1`, `behind_by=0`.
- Chính xác **12 tệp** có trạng thái `added`, không tệp `modified/deleted/renamed`, không tác động P00, `main`, `lineage.md`, `docs` P00 hoặc cấu hình P00 trong commit triển khai.
- `main=92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`; PR #4 vẫn Draft, chưa merge, ở thời điểm kiểm tra.
- Không có QA0/CI status hợp lệ được dùng để suy luận runtime PASS.

## 3. Đọc lại nội dung và băm SHA-256 độc lập

Hàm SHA-256 thuần JavaScript được kiểm bằng chuỗi chuẩn `abc` → `ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`; sau đó được áp dụng lên UTF-8 nội dung từng file đọc từ GitHub `fetch_file(ref=7e8b37d...)`. Băm so với `FILE_SHA256` trong console Windows **12/12 khớp**:

| Đường dẫn mới | SHA-256 đọc lại trên GitHub |
|---|---|
| `src/p01/byte_bpe.py` | `c6ca8b5aa9c7847b3d3fbbf2920cc283f5156d11b576d3f05c820bfaba88135e` |
| `src/p01/data_dedup_split.py` | `53b7357479c0f3dbc37d17daefee2056e73d967710a92b7dda0e87cad30cdbeb` |
| `qa/p01/f0_fixture_generator.py` | `82b0a7a60c09517a8e831fac0f524a7760068cb56c21296b5c234842cd3f211e` |
| `qa/p01/independent_checker.py` | `ba700b3d18faf423b7c10206cca87a6d216ef34c4af94e39fc48e7d643f6d7e6` |
| `qa/p01/checker_contract_cases.py` | `6928a08cff41f899472040ea1310734dd4a4deb808a2c8c48e17e23ce9e934a5` |
| `runtime/p01/windows_job_guard.py` | `14cd10f039217d9ead2c9f875578b28ef9cc90f5a5ae1d8eb354fc6802e52bd0` |
| `runtime/p01/write_quota_broker.py` | `bab9a1dde2a2b421520919d8736a9d015e144e060fa1b1629bc276f3a18a6bf7` |
| `runtime/p01/source_scope_guard.py` | `c7a99f05ce142d15a3c75d364f86ddda8aa4ea1a16364afc382403c4d7392594` |
| `runtime/p01/evidence_manifest.py` | `d36db806bf263a2d99747d8d572052657fd523fa65f9defd61133c9856bc13a7` |
| `configs/p01_f0_static_i0a.json` | `320b500d92aeff8e28e5a020d74b8c443309208f309543675f57e325de7da842` |
| `qa/p01/golden_vectors.json` | `006498774789b00bac3af5482152d3d9a3a1f4ad06f097a2dd0535b947909bc1` |
| `docs/qa/P01_I0A_STATIC_IMPLEMENTATION_REVIEW.md` | `92bb6d8a9de78d3175977ab5e4d2e3e4fe06e845a321e1390aeb5b37e6693d6a` |

**Verdict:** `SOURCE_IDENTITY_READBACK=PASS_12_OF_12`, `COMMIT_SCOPE=PASS_12_ADDED_0_MODIFIED_0_DELETED`.

## 4. Kiểm toán nguồn tĩnh — lưu ý không đồng nghĩa QA runtime

**Đạt theo kiểm toán cú pháp/phạm vi bằng cách đọc nguồn:**
- `src/p01/byte_bpe.py` có giao diện B0, B1, luật phá hòa từ `Counter` và sắp cặp theo `(-freq,pair)`; magic 11 byte; parser merges có kiểm tra count/rank/ID và trailing/truncated; chưa có bài thử động.
- `qa/p01/independent_checker.py` không import tokenizer/generator, có kiểm thử cấu trúc merges và M01 golden theo SHA literal; mới là checker **từng phần**, chưa chạy C01–C10.
- `runtime/p01/windows_job_guard.py:25` từ chối chạy worker qua `GuardNotEstablished` và `runtime/p01/write_quota_broker.py:23` từ chối ghi qua `BrokerUnavailable`; đây là **stub fail-closed**, không phải Job Object hoặc broker thật.
- `runtime/p01/evidence_manifest.py` tự nêu đây là serializer rút gọn, **không** phải JCS RFC8785 đầy đủ, và từ chối cấp runtime receipt ở `:27`.
- `runtime/p01/source_scope_guard.py` từ chối F1/F2 và scientific TEST, nhưng marker string không phải chứng thực nguồn độc lập.

**Hai điểm cần sửa/xác minh trước QA0:**
1. **I0A-FINDING-01 (P2, sửa mã nguồn):** `src/p01/data_dedup_split.py:70-77` đọc `d.raw` và `d.document_id` **trước khi** kiểm tra `isinstance(doc, Document)`; đầu vào sai kiểu có thể gây `AttributeError/TypeError` thay vì `SourceScopeError` được định nghĩa cho từ chối. Kiểm tra kiểu và từng trường trước khi `sum`/`sorted`, và viết negative oracle riêng. Đây là phát hiện phân tích mã, **chưa được chạy để tái hiện**.
2. **I0A-FINDING-02 (P1, ranh giới QA0):** `src/p01/byte_bpe.py:85` và `src/p01/data_dedup_split.py:66,114` chỉ so chuỗi `admission == QA0_F0_SYNTHETIC_ONLY`. Chuỗi này không chứng minh đầu vào là F0 được phép hoặc token hệ thống bị hạn chế. Vì thế không được coi đây là cơ chế admission an toàn hay cho phép học trên corpus. QA0 cần tầng thực thi bên ngoài và bộ kiểm tra nguồn; mã chưa được chạy.

**Các khoảng trống công khai và dự kiến:** `windows_job_guard`, `write_quota_broker`, `evidence_manifest` chưa hoàn thành QA0. Không tự chấm FAIL chức năng runtime vì chúng chưa được cấp phép và cố ý là stub. Không chứng minh H03 full split leak audit, golden case matrix C01–C10/W01–W12 đã qua kiểm thử.

## 5. Phán quyết và tính bất biến

`TTM_P01_I0A_S_IMPLEMENTATION_SOURCE_IDENTITY=PASS`  
`TTM_P01_I0A_S_GIT_COMMIT_SCOPE=PASS`  
`TTM_P01_I0A_S_STATIC_CODE_REVIEW=PASS_WITH_FINDINGS`  
`TTM_P01_I0A_S_COMPLETION=SOURCE_ONLY_COMPLETED`  
`TTM_P01_I0A_SOURCE_GAPS=OPEN_2`  
`TTM_P01_QA0_FUNCTIONAL_READINESS=HOLD_FIX_AND_ISOLATION`  
`TTM_P01_QA0_DYNAMIC_TESTS=NOT_EXECUTED`  
`TTM_P01_E0_SCIENTIFIC_EXECUTION=NOT_PERFORMED`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`  
`P01_WORKTREE_CLEANUP_AUTHORIZED=false`.

Không ghi `lineage.md`: đây là kết quả quản trị triển khai/QA tĩnh, không phải kết quả khoa học. Bản phân xử này đặt trong nhánh thiết kế, **không sửa commit `7e8b37d...`** của mã triển khai.

**Bước tiếp theo:** `TTM_P01_I0A_S_STATIC_SOURCE_FIXUP_AND_QA0_F0_SMOKE_PREP`. Sửa có giới hạn 2 điểm và xác định một lượt smoke QA0 chỉ dùng fixture F0, có bảo vệ hệ thống tệp; tuyệt đối không huấn luyện BPE trên dữ liệu thật hoặc chạy GPT trước QA0/E0.
