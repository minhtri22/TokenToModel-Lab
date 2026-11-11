# TTM CF1 — Frozen O0 step1024 / CPU DEV-only — execution attempt and source HOLD

**Ngày:** 2026-11-11  
**Task:** `TTM_O0_CF1_FROZEN_STEP1024_DEV_ONLY_ONESHOT_CPU_TEACHER_FORCED_EVAL_AND_OWNER_ADJUDICATION`  
**Quyết định một lần:** `HOLD_RUNTIME_PINNED_BPE_NOT_READABLE`; **không có phép chấm DEV neural và không chấm FINAL**.

## 1. Công việc đã thực sự chạy

- Nạp checkpoint gốc `/mnt/data/checkpoint.pt` bằng CPU, SHA-256 đọc thực `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; `step=1024`; `P02Config` chính xác, `3,749,376` tham số.
- Khôi phục file `src/p02/transformer_core.py` **nguyên byte từ GitHub**, Git blob được tái tính là `9762343e06cf800b50574c2871ae1ed58537fb18` (5.160 byte). `load_state_dict(strict=True)` PASS. Chạy một forward CPU giả lập chỉ trên dãy token `[65,66,67,68,69,70]` và kiểm tra finite logits kích thước `[1,6,2048]` PASS. **Không gọi mô hình với bất kỳ ngữ cảnh DEV nào**.
- Kiểm lại `CF1_DEV_MODEL_INPUT_ONLY.json` trên đúng 36 cặp: SHA-256 `81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed`.
- Chạy lại `cf1_cpu_scorer_unit_qa.py` đã khóa từ GitHub trên **checkpoint thật, fixture token byte giả lập**: PASS **25/25**. Kiểm thử này chỉ xác minh logic scorer/loss/negative QA; không phải kết quả O0 trên DEV.

## 2. Điều kiện chặn không được bỏ qua

Manifest tokenizer **đúng nguyên file** `T1_BPE2048_REAL_TRAIN_MANIFEST.json`, SHA-256 bắt buộc `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, hiện **không có trong container CPU**. Có thể thấy tên file dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t1_real_source_v1\` qua RemoteDesktop ở bước đầu, nhưng các lần đọc tiếp theo của connector trả **internal error**. Bản trích cục bộ thiếu số cặp BPE và bị bộ kiểm tra toàn vẹn loại; **không** sử dụng token IDs giả định để chạy model.

Vì vậy, **0/36 cặp được chấm**; `144 teacher-forced completions=NOT_EXECUTED`; không có `PAIR_BOTH_CORRECT`, không có NLL hoặc marginal logprob để phân xử. **Không** gọi `CF1=FAIL_NEURAL` khi mô hình chưa chạy; chỉ `HOLD_RUNTIME_SOURCE`.

## 3. Một fallback executable, giới hạn đúng project root

Đã commit [`cf1_dev_only_one_shot_owner_cpu.py`](../../tools/research/narrative_cf1/cf1_dev_only_one_shot_owner_cpu.py) trên nhánh nghiên cứu. Script là wrapper cho scorer exact GitHub hiện hữu: không sử dụng dịch vụ mạng hoặc checkout nhánh khác, lấy **đúng Git blob** của P02, BPE source, scorer, DEV input+oracle từ `git cat-file blob`, kiểm file checkpoint/manifest SHA256 trước khi làm bất kỳ forward nào; tạo output trong `_tmp` của repository, từ chối chạy nếu thư mục one-shot đã có; checkpoint không bao giờ ghi. Source được cung cấp để chủ dự án chạy trực tiếp trên Windows khi nguồn private đúng SHA sẵn sàng. **Wrapper chưa được thực thi trên Windows ở lượt này**.

Trên PowerShell 5.1:
```powershell
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
# Locate the exact step-1024 checkpoint within the project root.
$checkpoint = Get-ChildItem -LiteralPath $root -Filter checkpoint.pt -File -Recurse -ErrorAction Stop |
    Where-Object { (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash -eq 'CB985751795C8328AD65ACF7CA4C1033CE35182C1BFBDB8C38550DE629CB271B' } |
    Select-Object -First 1 -ExpandProperty FullName
if (-not $checkpoint) { throw 'EXACT_STEP1024_CHECKPOINT_NOT_FOUND_WITHIN_PROJECT' }
$script=Join-Path $root 'tools\research\narrative_cf1\cf1_dev_only_one_shot_owner_cpu.py'
if (-not (Test-Path -LiteralPath $script)) {
    throw 'PINNED_CF1_RUNNER_NOT_AVAILABLE_LOCALLY__FETCH_RESEARCH_BRANCH_FIRST'
}
& $python $script --repo-root $root --checkpoint $checkpoint
if ($LASTEXITCODE -ne 0) { throw 'CF1_DEV_ONLY_ONESHOT_NOT_PASS' }
```

**Nếu local checkout vẫn ở main (không có runner trên disk):** trước khi gọi đoạn lệnh trên, có thể lấy chính xác blob runner vào **`_tmp` trong project** mà không chuyển nhánh hoặc sửa main:

```powershell
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$python='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
git -C $root fetch origin research/ttm-o0-narrative-cf1-source-scorer-blind-readiness-20261111
if ($LASTEXITCODE -ne 0) { throw 'CF1_PINNED_SOURCE_FETCH_FAILED' }
$blob='14109c8d4e27a874e1832a480a0d7eeebed78b2f'
$script=Join-Path $root '_tmp\cf1_dev_only_one_shot_owner_cpu.py'
if (Test-Path -LiteralPath $script) { throw 'ONE_SHOT_RUNNER_ALREADY_STAGED' }
& $python -c 'import pathlib,subprocess,sys,hashlib; b=subprocess.check_output(["git","-C",sys.argv[1],"cat-file","blob",sys.argv[3]]); h=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest(); assert h==sys.argv[3]; pathlib.Path(sys.argv[2]).write_bytes(b)' $root $script $blob
if ($LASTEXITCODE -ne 0) { throw 'CF1_RUNNER_GIT_BLOB_PIN_FAILED' }
```

Sau đó chạy phần tìm `$checkpoint` và lệnh `& $python $script --repo-root $root --checkpoint $checkpoint` ở trên; không sử dụng dòng `$script=Join-Path ... tools\research ...` nếu file đó chưa có ở local checkout. Việc fetch chỉ thêm Git objects/ref tracking; không checkout, không merge.

**Chú ý:** Git objects cần đã được fetch về local repo; nếu thiếu object, script FAIL trước khi tạo output. Không chạy lại khi có `_tmp\TTM_CF1_STEP1024_DEV36_ONE_SHOT_20261111`; kiểm tra output/receipt thay vì đổi tên job hoặc chạy thêm lần.

## 4. Phán quyết khoa học

- `FROZEN_O0_SOURCE_CHECK=PASS_SCOPED`, `CPU_SYNTHETIC_FORWARD=PASS`, `SCORER_QA=PASS_25/25`.
- `DEV_NEURAL_SCORES=NOT_EXECUTED`; `FINAL=SEALED_HOLD`; `TTM_TEST_Q1Q2=UNTOUCHED`.
- Bộ CF1 đã có **heuristic bề mặt 36/36 trên DEV** trong hồ sơ trước; dù sau này O0 đạt 100%, chỉ có thể nói về *contextual continuation preference* trong phạm vi truyện được tạo, không chứng minh state reasoning hoặc sự cần thiết của O1.
- `TRAINING/GPU=NO`; `O1=DEFER`; không cập nhật P02, checkpoint, `lineage.md`, PR13, hay `main`.

**Bước thực hiện tiếp theo:** `TTM_CF1_EXACT_LOCAL_BPE_MANIFEST_DEV36_ONESHOT_OWNER_EXECUTION_AND_GITHUB_RECEIPT` — chỉ thực hiện khi manifest/checkpoint đã được pin chính xác trên máy Windows, chạy **một** lượt DEV CPU và đẩy receipt/QA lên cùng nhánh nghiên cứu; không chạm FINAL hay science GPU. Tránh tạo micro-permit mới.
