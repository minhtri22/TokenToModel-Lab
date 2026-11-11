# CF1 DEV36 — Thực thi một lần trên máy chủ Windows và nguồn sự thật GitHub

**Ngày:** 2026-11-11  
**Task:** `TTM_CF1_EXACT_LOCAL_BPE_MANIFEST_DEV36_ONESHOT_OWNER_EXECUTION_AND_GITHUB_RECEIPT`  
**Trạng thái hiện tại:** `REMOTE_EXECUTION=BLOCKED_TOOL_INTERNAL_ERROR`, `DEV_NEURAL=NOT_EXECUTED`, `ONE_SHOT=NOT_CONSUMED_BY_THIS_REMOTE_ATTEMPT`. Không có point score để phân xử.  
**Mục tiêu vẫn giữ:** O0 bước 1.024, 36 cặp DEV public, 144 likelihood tính bằng teacher forcing, CPU không optimizer/GPU. Không đọc FINAL hoặc TEST/Q1Q2.

## Bằng chứng lỗi runtime hiện tại

RemoteDesktop link Primary thất bại nội bộ ở cả `device_list`, `read_file` exact Windows BPE manifest và `project_register`; thử nhiều lần không đạt. **Không có task lease, routed job hoặc execution marker đã được chấp nhận**, không sinh bản chấm DEV. Manifest BPE gốc SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` chưa sẵn có nguyên byte trong Linux runtime; bản trích thiếu bị từ chối. Không dùng tokenizer thay thế.

Có đủ nguồn trên GitHub:
- [Bộ chạy PowerShell 5.1 chính xác, tự đẩy evidence lên nhánh riêng](../../tools/research/narrative_cf1/Run-TTM-CF1-DEV36-Once-Owner-PS51-20261111.ps1)
- [Python one-shot source runner theo Git blob](../../tools/research/narrative_cf1/cf1_dev_only_one_shot_owner_cpu.py)
- [Receipt lưu lỗi Remote và kiểm toán guard tĩnh 13/13](../../artifacts/qa/ttm-narrative-cf1/CF1_DEV36_OWNER_EXECUTION_REMOTE_BLOCK_AND_PINNED_PS51_HANDOFF_20261111.json)

## Chạy an toàn trên Windows PowerShell 5.1 (chỉ một lần)

**Chỉ cần chạy khối sau trong PowerShell, không cần checkout nhánh nghiên cứu hoặc tải ZIP.** Git fetch chỉ kéo nguồn, không sửa `main` trong working tree. Dùng chính Python 3.12 của máy và Git blob đầy đủ đã ghim; không dùng PowerShell redirection vì làm đổi byte.

```powershell
$ErrorActionPreference = 'Stop'
$root   = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$branch = 'research/ttm-o0-narrative-cf1-source-scorer-blind-readiness-20261111'
$blob   = '59a7e90e7e1284303bda716937b4632094d77693'
$script = Join-Path $root '_tmp\Run-TTM-CF1-DEV36-Once-Owner-PS51-20261111.ps1'

if (-not (Test-Path -LiteralPath $root)) { throw 'TTM_PROJECT_ROOT_NOT_FOUND' }
if (Test-Path -LiteralPath $script) { throw 'PINNED_WRAPPER_ALREADY_STAGED_REFUSE_OVERWRITE' }
& git -C $root fetch --no-tags origin $branch
if ($LASTEXITCODE -ne 0) { throw 'PINNED_GITHUB_FETCH_FAILED' }
& $python -c 'import pathlib,subprocess,sys,hashlib; b=subprocess.check_output(["git","-C",sys.argv[1],"cat-file","blob",sys.argv[3]]); h=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest(); assert h==sys.argv[3]; pathlib.Path(sys.argv[2]).open("xb").write(b)' $root $script $blob
if ($LASTEXITCODE -ne 0) { throw 'GIT_BLOB_BINARY_SHA_MISMATCH' }
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
if ($LASTEXITCODE -ne 0) { throw 'CF1_DEV36_OWNER_ONE_SHOT_HOLD_OR_FAIL_NO_REPLAY' }
```

**Điều kiện preflight:** 
- Checkpoint gốc nằm **trong** `D:\WORK\RESEARCH\TokenToModel-Lab` và hash SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Script có thể tự tìm `*.pt`, hoặc nhận `-Checkpoint 'D:\WORK\RESEARCH\TokenToModel-Lab\<path-to-pinned-pt>'`.
- Manifest BPE tại `_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json`, SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Python 3.12 có torch và regex. Bộ chạy **không cài thêm phụ thuộc** hoặc tạo mô hình khác.
- Thư mục `_tmp\TTM_CF1_STEP1024_DEV36_ONE_SHOT_20261111` và nhánh `evidence/ttm-cf1-step1024-dev36-once-20261111` chưa tồn tại. Nếu đã tồn tại, **dừng và đọc bằng chứng cũ**; không replay, đổi ngày, đổi seed hay đổi execution ID.

**Nếu PASS:** script tự đẩy trên GitHub nhánh evidence riêng, bao gồm `CF1_FROZEN_O0_DEV36_SCORES.json`, `CF1_DEV36_OWNER_LOCAL_ADJUDICATION.json`, log stdout/stderr, SHA256 của score/report. Sau push phải xác minh remote HEAD trùng local commit SHA; script làm sẵn. **Không merge main**, không sửa PR#13 hoặc `lineage.md`. Nếu push thất bại, giữ dữ liệu trong project, không chạy lại inference.

## Cách phân xử khi đã có output thật

Chỉ sau khi nhận được receipt thực thi 36 cặp, đối chiếu tỷ lệ `PAIR_BOTH_CORRECT`, hai margin context, C1/C2/C3 và heuristic bề mặt 36/36. Không cho phép dùng nó để claim O1 có lợi hoặc mô hình đã học state logic, vì CF1 có một shortcut 36/36. FINAL vẫn HOLD; dữ liệu mới không làm hợp thức hóa benchmark CF1 thành blind FINAL.

**Bước thực hiện tiếp theo:** thực thi chính xác một lần bằng PS5.1 trên máy owner, sau đó `TTM_CF1_DEV36_OWNER_LOCAL_EVIDENCE_READBACK_AND_SCIENCE_SCOPE_ADJUDICATION`. Nếu preflight FAIL thì giữ trạng thái HOLD, không phát sinh micro-permit.
