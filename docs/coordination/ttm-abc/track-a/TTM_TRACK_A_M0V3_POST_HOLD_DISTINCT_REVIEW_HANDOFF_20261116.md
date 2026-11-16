# HANDOFF — Track A Q001 M0 v3 · Reviewer độc lập sau khi sửa F01/F02

**Operation tiếp nhận:** `A_M0_V3_F01_F02_AND_ONEPACK_DISTINCT_EXACT_SOURCE_REVIEW_SINGLE_GATE`  
**Repository:** `minhtri22/TokenToModel-Lab` · **Branch:** `research/ttm-track-a-small4m-diagnosis-20261116` · **PR:** [#33 DRAFT](https://github.com/minhtri22/TokenToModel-Lab/pull/33), stacked on PR #28 `ebdc54575eed1ff60c402eecf60289f408bb38ca`  
**Mode:** READ-ONLY private fixture · NO I2 · NO MODEL · NO MERGE · independent assessor khác Agent A.  
**Hiện trạng khi bàn giao:** `AUTHOR_REMEDIATION_QA_PASS · FROZEN_REAL_FIXTURE_PRESERVED · I1_HOLD_AWAIT_DISTINCT_REASSESSMENT`.

## 1. Phân biệt rõ bằng chứng cũ và phần sửa mới

Phán quyết độc lập trước sửa [REVIEW.md](https://github.com/minhtri22/TokenToModel-Lab/blob/05041501bfe84822feffd39290c6800b2152055a/artifacts/ttm-abc/track-a/M0_V3_DISTINCT_I1_20261116/REVIEW.md) tại commit `05041501bfe84822feffd39290c6800b2152055a` là **`HOLD_I1`**, có hai blocker thực tế: F01 NLL full-vocab bằng 0 với 2048 logits float32 đều ~1e20, F02 nguồn SHA không khóa thực thi bytecode `.pyc` giả. Không sửa/ghi đè báo cáo hay receipt độc lập ấy.

Nguồn tokenizer TRAIN-only thật được reviewer trước xác minh bằng SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. **Fixture thật đã được đóng băng duy nhất một lần**, SHA-256 `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`; manifest SHA-256 `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`. Reviewer đã chứng minh 80/80 case và 5/5 group digest khớp. Chỉ **đọc lại** những byte này, tuyệt đối **không tái tạo** fixture hay đổi seed/role/parent.

[Receipt sửa F01/F02 của Agent A](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-track-a-small4m-diagnosis-20261116/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_REMEDIATION_20261116/QA_RECEIPT.json) chỉ xác nhận **tác giả đã sửa source và chạy QA**, không tự cấp `I1_PASS`.

## 2. Exact source byte pins để kiểm toán

| Thành phần | SHA-256 canonical Git LF | SHA-256 Windows checkout CRLF |
|---|---|---|
| `track_a_m0_v3/q001_m0_goldblind.py` | `2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac` | `d76936db04caec358ddfb6947656d60023dee7de5c3388f810c7ecbf08288b63` |
| `preexec_candidate_20261116/ttm_sm4m_diag_q001.py` | `20c147f9f2629c494c157da5bab3519e01d755096638adfd10e07bb5dda3c4b8` | `9a6a6bbcdd1ce80d40cc40b2b6dce1b46ca2932806fc0f77b036681a401eee0e` |
| `track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1` | `6506ddf1e5b98793a4b2a3ba3b7aaf089f8692b64f4e0f6b53899b3c28d1a76d` | `40b3bfc6c235e272f70b033d4cf75ed8baca38c84c01ee20aacd701e30b670e5` |

**Lưu ý:** Tên OnePack `Freeze` là lịch sử. Source sau sửa **bắt buộc** tham số `-ReadbackOnly` và không còn gọi `fixture-freeze`. Git HEAD, Git blob LF, byte checkout LF/CRLF và source SHA được kiểm tra độc lập; mixed-EOL không được chấp nhận.

Manifest của fixture thật **vẫn gắn hash scorer trước sửa** `98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587`. Runner mới chỉ cho phép ngoại lệ readback cho **cặp records và manifest byte-exact** đã đóng băng, khi toàn bộ nội dung tương đương manifest v3 mới ngoại trừ trường SHA của scorer; không chuyển nhãn lịch sử thành fixture mới. Xác minh logic `read_frozen_fixture` bằng checker độc lập.

## 3. QA tác giả đã chạy

[GitHub Actions run #43903520071](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43903520071) trên **Windows Server 2022 · Python 3.12.10 · PowerShell 5.1 source/AST**:

| Suite | Kết quả | Phạm vi |
|---|---:|---|
| Adversarial unittest | **31/31 PASS** | bao gồm 2048 logits đồng đều ở mức float32 ~1e20, bất biến cộng hằng số, `.pyc` giả |
| Guarded runner source QA | **18/18 PASS** | không tải checkpoint |
| Negative QA | **48/48 PASS** | bao gồm native exit 86 chính xác, bác generic exit 86 và exit 0 |
| Author mock checks | **10/10 PASS** | mô phỏng, không phải private fixture |
| OnePack PS5.1 | **PASS AST/source** | chưa thực thi đọc lại byte thật sau sửa |

**F01** sửa thành `(max_logit-gold_logit)+log(fsum(exp(logit-max_logit)))` để tránh mất `log(2048)` bởi floating-point cancellation. **F02** đọc source một lần, xác minh exact SHA của raw LF/CRLF cùng SHA canonical LF, rồi `compile()` đúng buffer đó và `exec()` trực tiếp; không dùng `importlib SourceFileLoader` hoặc nạp `.pyc`. Unit test dựng `.pyc` có mtime/size hợp lệ: loader cũ nạp sentinel (positive reproduction), loader mới không nạp sentinel.

Native Job Object guard `HOLD_WINJOB_LIMIT_READBACK_MISMATCH` có thể kết thúc với mã 86 trước kiểm tra admission. Harness chỉ cho PASS fail-closed với **đúng chuỗi guard đó**, hoặc exit 2 với `HOLD_` chuẩn; exit 86 chung chung và exit 0 bị bác. Điều này sửa sai khác 44/45 tại host reviewer nhưng **chưa phải native rerun trên cùng Windows host**.

## 4. Việc của Agent độc lập — một lượt duy nhất

1. Từ **HEAD mới nhất của PR #33**, đọc toàn bộ source patch, tính lại hash Git LF, Windows CRLF và đối chiếu từng byte với bảng trên; xác nhận PR #28/main/lineage/Track B/C không đổi.
2. Chạy checker **do reviewer tự viết** trên bản scorer/runner đã vá, tái hiện riêng hai phản chứng F01/F02 (dùng cả đỉnh logit 1e20, case shift, `.pyc` giả có mtime/size hợp lệ, sai CRC/source, EOL hỗn hợp). Đối chiếu NLL với `ln(2048)=7.6246189861593985`, tie abstain và đầy đủ full-vocab 2048.
3. **Không đóng băng lại.** Từ máy Windows có byte fixture thật, dùng OnePack đã vá **chỉ với `-ReadbackOnly`** và exact HEAD/runner SHA. Nó phải đọc đúng BPE/records/manifest SHA đã khóa, kiểm 80 case và 5 group metadata, đối chiếu Git blob và xuất SHA-only receipt mới *không overwrite*. Nếu script không tìm đúng private directory hoặc source pin không khớp, kết luận **HOLD**, không tự đổi path/seed hay tái tạo records.
4. Tự kiểm thêm source/runtime negative trên Windows PS5.1 / Python 3.12: frozen readback, tampered record/manifest, old scorer pin compatibility chính xác, fail-closed trust anchors và mã exit Job Object 86. Phân biệt run thực trên Windows với QA AST trong GitHub Actions.
5. Rà soát trước-sau: kết quả độc lập 05041501 là lịch sử bất biến; source mới chỉ sửa metric và loader, không thay đổi câu hỏi, case, split, gold, old TEST/FRESH16/FINAL24/EXP32 hoặc checkpoint. `release-preflight` vẫn phải từ chối do `HOLD_OWNER_INTERNAL_I1_NOT_PASS` cho đến khi I1 được phân xử và release contract mới hợp lệ.
6. Ghi **một** quyết định chính thức `I1_PASS_SCOPED_MEASUREMENT` hoặc `HOLD_I1` với danh tính phiên reviewer, commit chính xác, source/custody SHA, native logs đã lọc riêng tư và negative table; push evidence **chỉ sanitized** lên nhánh PR #33. Không tự sửa lỗi rồi tự ký một PASS nếu thấy blocker mới.

### Cách chạy OnePack readback-only khi reviewer đã xác minh HEAD

Từ Windows PowerShell 5.1, sau khi lưu **byte chính xác của OnePack từ GitHub HEAD vào một đường dẫn mới nằm trong project root**:

```powershell
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Head = (& git -C $Root ls-remote origin refs/heads/research/ttm-track-a-small4m-diagnosis-20261116) -split '\s+' | Select-Object -First 1
if ($LASTEXITCODE -ne 0 -or $Head -notmatch '^[a-f0-9]{40}$') { throw 'HOLD_HEAD_PIN' }
$Script = Join-Path $Root '_tmp\Invoke-TrackA-M0V3-PostFixReadback-PS51.ps1'
if (Test-Path -LiteralPath $Script) { throw 'HOLD_NO_OVERWRITE' }
$Spec = $Head + ':tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1'
$Lines = @(& git -C $Root show $Spec)
if ($LASTEXITCODE -ne 0) { throw 'HOLD_GIT_SHOW' }
[IO.File]::WriteAllText($Script, ($Lines -join [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
& $Script -ReadbackOnly -ExpectedCommit $Head -ExpectedRunnerSha256 '9a6a6bbcdd1ce80d40cc40b2b6dce1b46ca2932806fc0f77b036681a401eee0e'
```

**Đây là hướng dẫn reviewer, không phải receipt đã chạy trong phiên Agent A.** Nếu công cụ Windows hoạt động khác giả định, reviewer phải xác nhận và lưu cách materialize byte trong evidence; không coi template bootstrap là một kiểm thử PASS.

## 5. Quy tắc đóng Gate

`I1_PASS_SCOPED_MEASUREMENT` chỉ nếu hai phản chứng được loại bỏ với source được pin, readback fixture thật đã lưu PASS, QA native ảnh hưởng đạt và reviewer khác Agent A tự phân xử theo exact HEAD. Nếu thiếu bất cứ điều kiện nào: `HOLD_I1` và ghi blocker thực, tránh tạo micro-permits. Dù I1 PASS scoped, **không đồng nghĩa có quyền chạy I2**.

**Bước tiếp theo — duy nhất:** `A_M0_V3_F01_F02_AND_ONEPACK_DISTINCT_EXACT_SOURCE_REVIEW_SINGLE_GATE`.

**Bảo toàn:** `I2_NOT_EXECUTED · MODEL_FORWARD_0 · OPTIMIZER_STEPS_0 · PRIVATE_FIXTURE_UNCHANGED · HISTORICAL_I1_HOLD_PRESERVED · PR33_DRAFT · NO_MERGE`.
