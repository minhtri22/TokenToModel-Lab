# P01 — Tiền kiểm nơi làm việc Windows và đồng bộ mốc P00 trước thiết kế thực thi

**Ngày:** 05/11/2026  
**Trạng thái:** `READ_ONLY_METADATA_PASS_LOCAL_GIT_STATUS_PENDING`  
**Mốc GitHub `main` đã kiểm tra:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Mốc local `main` và `origin/main` đã đọc qua RemoteMCP:** `c66e27a5d1e68958d42c825fd40f8a273994e0a0`.  
**Cây làm việc P00 được bảo toàn:** `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.

## 1. Kiểm tra đã thực hiện, chỉ đọc

- Thiết bị `DESKTOP-4PSD0G2` trực tuyến; đã đọc `.git/HEAD`, `.git/refs/heads/main`, `.git/refs/remotes/origin/main` và nhánh P00 qua RemoteMCP.
- Đúng workspace `D:\WORK\RESEARCH\TokenToModel-Lab`; project RemoteMCP `prj_7ff9a13a92022806cecf44b7` còn loại `NON_GIT`, task cũ `tsk_fcaae8452d82e4872bc1748e` vẫn `RECOVERABLE`. Không đăng ký lại, chuyển binding hoặc sử dụng task khoa học để thực thi hành chính.
- GitHub `main` đã có commit hồ sơ PR #3 `92face...`, local vẫn ở commit trước đó `c66e...`.
- **Chưa có đầu ra `git status` mới được thực thi trên Windows trong bước này.** Do đó không thể cấp kết luận trạng thái sạch hoặc tự động đồng bộ qua công cụ từ xa.

## 2. Chương trình PowerShell có kiểm tra trước khi viết

**Tên tệp:** `TTM_P01_BASELINE_SYNC_PREFLIGHT.ps1`, tải qua đường liên kết của phiên ChatGPT đã cung cấp.  
**Vị trí được phép lưu:** `D:\WORK\RESEARCH\TokenToModel-Lab\tmp\TTM_P01_BASELINE_SYNC_PREFLIGHT.ps1`.  
**SHA-256 tệp:** `b75a60dd924a5963d0cec976542de86cab63dc76f281f5c66a8ff4572e53d911`.

Kiểm tra tĩnh được thực hiện ở môi trường chuẩn bị: **16/16 tiêu chí PASS**. Đây là kiểm tra tĩnh mã script, **chưa phải kết quả thực thi Windows**.

Chương trình sẽ từ chối nếu phát hiện sai nguồn Git, sai nhánh, sai commit, đường dẫn thoát khỏi workplace, điểm nối (Junction) hoặc liên kết tượng trưng (Symlink) trong vùng kiểm tra, trạng thái Git bẩn, worktree P00 đổi commit, SHA biên bản cũ sai, hoặc GitHub `main` đã thay đổi.

Nếu kiểm tra hợp lệ, chương trình chỉ:
1. Tải tham chiếu `main` đã ghim chính xác từ GitHub; kiểm tra không phân kỳ.
2. Kiểm tra tập tệp thay đổi của PR #3 phải đúng **4 tệp hồ sơ**: `lineage.md`, `artifacts/qa/p00/TTM_P00_DOC_PR2_FAST_FORWARD_20261105T081134196Z.json`, `docs/qa/P00_DOC_PR2_LOCAL_SYNC_AND_BASELINE_CLOSURE_20261105.md`, `docs/qa/P00_DOC_PR2_SYNC_AUDIT_STATIC_QA_20261105.md`.
3. Chỉ đồng bộ tiến nhanh (Fast-forward) `main` từ `c66e...` đến `92face...`, không tạo commit hợp nhất mới.
4. Xác minh lại **15 tệp bảo vệ** (13 tệp theo biên bản PR #2, biên bản PR #2 và chính script đang chạy), mỗi tệp phải có SHA-256 trước/sau giống nhau.
5. Tạo một biên bản mới theo mã thời gian trong `evidence/p00/`, không ghi đè.
6. Giữ nguyên cây làm việc P00; không tạo cây P01, không dọn dẹp, không tải corpus hoặc chạy huấn luyện.

## 3. Lệnh chạy trên máy Windows, sau khi tải đúng tệp

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$script = Join-Path $root 'tmp\TTM_P01_BASELINE_SYNC_PREFLIGHT.ps1'
$expectedSha = 'b75a60dd924a5963d0cec976542de86cab63dc76f281f5c66a8ff4572e53d911'

if (-not (Test-Path -LiteralPath $script -PathType Leaf)) {
    throw 'TTM_P01_SCRIPT_MISSING'
}
if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ine $expectedSha) {
    throw 'TTM_P01_SCRIPT_SHA256_MISMATCH'
}
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script
```

**Không** tải script bằng URL nhánh không ghim nếu chưa kiểm tra SHA-256; không tự sửa script sau khi ghim. Nếu không thể thực thi Windows hoặc gặp lỗi, giữ trạng thái `LOCAL_SYNC_HOLD`, lưu console; **không** dùng `reset --hard`, `git clean`, sửa thủ công ref hoặc tạo worktree mới để lách cổng.

## 4. Kết luận về điều kiện tài nguyên

Chưa đo mới dung lượng trống ổ D: hay RAM khả dụng cho BPE/corpus vì bước này không được phép chạy tải dữ liệu hoặc huấn luyện. Các ngân sách `max_source_bytes`, `max_ram_peak_bytes`, `max_disk_bytes` đều `NOT_LOCKED`. Không dùng thông số phần cứng cấu hình lắp đặt thay cho đo tài nguyên tức thời.

**Trạng thái:** `LOCAL_MAIN_HEAD_STALE_AS_OBSERVED`; `LOCAL_FAST_FORWARD_NOT_EXECUTED`; `P01_WORKTREE_NOT_CREATED`; `P01_DATA_NOT_DOWNLOADED`; `P01_TRAINING_NOT_EXECUTED`.

**Bước tiếp theo:** chạy script đã khóa, xác minh biên bản qua đường dẫn gốc, sau đó thẩm định độc lập thiết kế/tiền đăng ký trước khi xem xét quyền triển khai P01. Việc đồng bộ `main` mới không tự cấp quyền dùng dữ liệu hay huấn luyện.

## 5. Phụ lục sau lần chạy — Đồng bộ Windows đã đạt

Các thông tin `LOCAL_MAIN_HEAD_STALE_AS_OBSERVED` và `LOCAL_FAST_FORWARD_NOT_EXECUTED` trong các mục trước phản ánh **thời điểm tiền kiểm ban đầu**, không phải trạng thái hiện hành.

- Biên bản đã chạy: `D:\WORK\RESEARCH\TokenToModel-Lab\evidence\p00\TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json`.
- SHA-256 của biên bản gốc: `ee69f32a993d011b35173074a5ea221bdffc3feb70c780b532f045e9beb58b7f`.
- Đã xác minh trực tiếp local `main`, `origin/main`, GitHub `main` cùng commit `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.
- Kiểm tra SHA-256 từng tệp được bảo vệ: **15/15 PASS** trên máy Windows, không chỉ dựa vào nội dung báo cáo.
- Worktree P00 vẫn ở `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`. Không dọn dẹp.
- Bản lưu biên bản gốc trên nhánh thiết kế: `artifacts/qa/p01/TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json` — đọc lại cùng nội dung byte sau khi đẩy GitHub.
- Báo cáo thẩm định: `docs/p01/P01_D0_INDEPENDENT_METHOD_REVIEW_20261105.md`.

**Quyết định cập nhật:** `P01_LOCAL_BASELINE_SYNC=PASS`, `P01_D0_DESIGN_REVIEW=PASS_SCOPED`, `P01_D1_SCIENTIFIC_LOCK=HOLD`, `P01_IMPLEMENTATION_NOT_AUTHORIZED`.

Trạng thái đồng bộ nêu trên chỉ đúng tại thời điểm kiểm tra. Sau khi nhánh tài liệu được hợp nhất nếu có, local `main` sẽ cần được xác minh lại trước một thao tác Git mới; không tự kéo/đẩy dữ liệu hoặc sửa mã.
