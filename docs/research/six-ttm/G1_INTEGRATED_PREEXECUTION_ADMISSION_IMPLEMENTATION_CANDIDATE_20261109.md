# G1 — Gói tiền thực nghiệm tích hợp tối thiểu: ứng viên triển khai, chưa cấp science

**Ngày:** 09/11/2026  
**Task:** `TTM_SIX_G1_INTEGRATED_PREEXECUTION_ADMISSION_MINIMAL_IMPLEMENTATION_AND_DISTINCT_READJUDICATION`  
**Phán quyết hiện thời:** `HOLD` — `G1_SCIENCE_LOCK=HOLD`.

## 1. Xuất xứ và bằng chứng không thay đổi

- Repo: `minhtri22/TokenToModel-Lab`.
- Research v1c đã khóa: `d5d0c5346a595557a76349f900d09be50bce289c`.
- Codex review commit: `d478282e16a4728f064892564b949e671e13cdd2`, nhánh `review/ttm-six-g1-v1c-codex-distinct-20261109`.
- Báo cáo phản biện: `docs/research/six-ttm/G1_V1C_CODEX_DISTINCT_REREVIEW_20261109.md` tại commit review trên. Kết luận **HOLD**: 29/29 QA tác giả tái chạy; 63 quan sát độc lập gồm 51 control PASS, 2 CKA PASS và 10 khiếm khuyết/thiếu sót tái lập.
- Manifest T1: `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; G1 128/64/64: `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`.
- Hai lỗi CRITICAL của v1b (freeze schema/replay và CKA false-positive) **PASS độc lập trong v1c CPU synthetic**, **không mở lại**.

## 2. Phạm vi ứng viên triển khai trong đợt này

Ứng viên là **controller mô phỏng (simulation controller)** chứ không phải launcher production. Mục đích là làm rõ hợp đồng giao tiếp và kiểm chứng các phản ví dụ bằng dữ liệu giả. Không chạy Qwen, không đọc TinyStories, không truy cập manifest private/TEST, không cấp phép dữ liệu hoặc khoa học.

Tệp nguồn: `scripts/research/six_ttm/g1_admission_controller_candidate.py` — Git blob SHA-1: `0459faca82b6e00ad7312c882ae42e0e6aaf60ab`.

QA: `scripts/research/six_ttm/test_g1_integrated_admission_negative.py` — Git blob SHA-1: `fc999aa4963cefbc56a4eba2a066d4e8a7b1f747`.

Receipt QA: `docs/research/six-ttm/G1_ADMISSION_CPU_SYNTHETIC_RECEIPT_20261109.json`.

### Tính năng chạy được trong môi trường mô phỏng

1. **Ledger:** SQLite transactional `BEGIN IMMEDIATE`, `synchronous=FULL`, chuỗi trạng thái có `run_id`, số thứ tự, hash và STOP terminal. Trạng thái còn khi chỉ xóa worker workspace. **Không chống được rollback cả DB controller**.
2. **Split gate:** đọc nguồn synthetic TEST chỉ khi ở `FIT_FROZEN`, ghi trạng thái `TEST_EXTRACT_CONSUMED` **trước byte read**; từ chối symlink, hardlink `st_nlink>1` và sai định danh file handle. **Vẫn cần broker thực sở hữu TEST bytes dưới principal riêng**.
3. **Pack writer prototype:** ghi pack qua staging + fsync + exclusive hardlink publish; state intent trước ghi và terminal khi phát hiện lỗi. **Chưa có trusted writer, transaction atomic liên miền và receipt được ký/chứng thực**.
4. **One-shot prototype:** monotonic state trong DB độc lập với worker workspace; chống replay cục bộ. **Không có off-host/off-worker immutable witness** đủ chống rollback từ chủ thể có quyền sửa DB.
5. **Watchdog CPU:** `Popen` giám sát, dừng process group (Linux) hoặc `taskkill /T /F` (Windows được thiết kế, **chưa kiểm thật**). Không được đánh đồng với watchdog T4, VRAM cap hoặc tài nguyên liên mô hình.
6. **Authority:** `OWNER_ED25519_PUBLIC_KEY_SHA256=None` và `production_admission_gate()` luôn STOP. Bất kỳ cờ `..._attested=True` trong lời gọi không thay được chứng cứ owner, reviewer và launcher. Không tạo khóa bí mật, không cho phép science.

### Kết quả CPU synthetic

`PASS_INTEGRATED_ADMISSION_SYNTHETIC_ONLY`, **33 kiểm tra**, chạy dưới Python 3.13.5 trên Linux CPU. Các trường hợp gồm: duplicate run, thiếu freeze, state-skip, sha sai, commit lỗi, hardlink/symlink, đóng TEST, xóa worker workspace rồi replay, cumulative budget, từ chối permit, timeout ép dừng child. Đây là **QA của người triển khai**, không phải reviewer độc lập hoặc môi trường Windows/Colab T4.

## 3. Quy tắc đóng sáu hard gate bằng một gói

| Gate | Bằng chứng ứng viên | Bằng chứng còn thiếu để PASS production |
|---|---|---|
| Owner authority | Entrypoint production khóa cứng STOP | Owner custody và public-key pin thật, Ed25519 signature/launcher/source pins; reviewer≠author, data-rights, expiry; negative QA theo đúng identity production |
| Split broker | Synthetic TEST pre-freeze denied; reject hardlink/symlink | Trusted broker chạy dưới OS principal độc lập, thực thi ACL TEST trước freeze; kiểm hardlink/junction/alias tại Windows và khi chuyển sang Colab; TEST không nằm trong thư mục worker có thể đọc |
| Pack provenance/ledger | SQLite transaction, simulated pack/hash | Trusted writer, signed/attested stage receipt, pack bytes/manifest/IDs verified, crash-recovery atomic hoặc fail-terminal; không có orphan được xem là committed |
| One-shot | No replay khi chỉ xóa worker root, marker không là nguồn quyền | External append-only witness không chịu rollback cùng worker/controller, durable state transitions và kiểm tra rollback cả controller DB; không thay thế bằng JSON/SQLite cùng principal |
| GPU watchdog | Linux CPU child forced-kill synthetic | Windows/Colab true OS kill test, T4 memory guard ≤12GiB, total budget ≤7.200 s, per-model ≤3.600 s, ledger persisted and witness, không chạy lại technical smoke cũ |
| Scientific methods | CKA v1c có QA độc lập CPU | **Một** sửa đổi tiền đăng ký được reviewer duyệt: v1a dedup/mapping, v1b bootstrap fixed full-TEST SST, v1c CKA 64ε tie rule, exchangeability/near-duplicates, 64-story power hạn chế; không điều chỉnh sau TEST |

## 4. Điều kiện để gọi đây là triển khai production

Chỉ khi tất cả sáu gate có bằng chứng thực tế, gồm **trusted OS principal, owner-controlled signing key và off-worker/off-controller witness**, mới có thể tạo một launcher được ghim SHA, tách hẳn khỏi code v1c đã khóa. Cần kiểm chứng exact source blob, workspace, run ID, split, phase, model revision, owner data scope và budget bằng chứng được ký. Cả controller và worker đều phải fail-closed nếu mất quyền truy cập witness/trust source. Không có chế độ fallback trả về PASS.

**Không dùng ứng viên này làm launcher để mở Qwen G1**. `production_admission_gate` là chốt chặn cố định. Khi chuẩn bị production, phải phát hành artifact/version **mới**, QA độc lập và phân xử một lần; không gỡ HOLD chỉ bằng 33 synthetic PASS.

## 5. Ranh giới nghiên cứu và bản sửa phương pháp

- Không thay T1 2.368 IDs, G1 256 prefix, hai Qwen technical one-shot đã dùng, v1a/v1b/v1c, `main`, PR #12, `lineage.md`, TTM-Small-4M hoặc SIX upstream.
- Chưa có kết quả khoa học. Không tự phê duyệt quyền xử lý TinyStories ở Colab hay lưu derived feature tensors.
- Cần reviewer quyết định rõ CKA tie tolerance 64ε có bảo đảm đủ kiểm soát type-I và fairness hay cần amendment mới; không thay đổi dựa theo TEST.
- G1 dừng ở `SCOPED_FEASIBILITY` kể cả khi PASS; chưa chứng minh cơ chế SIX riêng hoặc lợi ích huấn luyện TTM.

## 6. Phán quyết của gói ứng viên

`G1_ADMISSION_CANDIDATE_IMPLEMENTED=YES`  
`SYNTHETIC_CPU_QA=PASS_33`  
`PRODUCTION_AUTHORITY=NOT_PROVISIONED`  
`WINDOWS_ACL_AND_SPLIT_BROKER=NOT_TESTED`  
`EXTERNAL_ROLLBACK_WITNESS=NOT_IMPLEMENTED`  
`REAL_T4_WATCHDOG=NOT_TESTED`  
`METHODS_AMENDMENT=DISTINCT_REVIEW_PENDING`  
`DISTINCT_READJUDICATION=NOT_PERFORMED`  
`OWNER_SCIENCE_PERMIT=NOT_ISSUED`  
`G1_SCIENCE_LOCK=HOLD`

**Bước thực hiện tiếp theo:** `TTM_SIX_G1_TRUSTED_RUNTIME_OWNER_SCOPE_AND_WITNESS_INTEGRATION_ONE_PACKET` — triển khai trust boundary thật, một quyết định quyền dữ liệu của owner, QA negative trên Windows/Colab và một phán quyết reviewer tích hợp. Không lặp lại các technical one-shot đã khóa.
