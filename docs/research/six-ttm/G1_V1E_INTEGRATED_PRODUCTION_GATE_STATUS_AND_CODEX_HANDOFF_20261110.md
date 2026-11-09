# HANDOFF — TTM × SIX G1 integrated production gates + methods v1e

**Task:** `TTM_SIX_G1_INTEGRATED_PREEXECUTION_PRODUCTION_GATES_AND_METHODS_CLOSURE`  
**Ngày:** 2026-11-10  
**Phán quyết hiện hành:** `HOLD`. `G1_SCIENCE_LOCK=HOLD`. 

## 1. Nguồn, chain-of-custody và scope

- Origin: `https://github.com/minhtri22/TokenToModel-Lab`.
- Nhánh triển khai **mới**, không sửa đè v1c: `implementation/ttm-six-g1-production-gates-methods-v1e-20261110`; xuất phát từ `81795e794550d6f8ff3515ce3332b7c053197b46`.
- Frozen research v1c: `d5d0c5346a595557a76349f900d09be50bce289c`.
- Độc lập Codex v1c: `d478282e16a4728f064892564b949e671e13cdd2` (`HOLD`).
- Độc lập Codex Windows: `efbbc1fddfd61e775d30a0481622312f8fb93c51` (`HOLD`).
- Không thay đổi `main`, PR #12, `lineage.md`, manifest gốc, TTM-Small-4M checkpoint hoặc các Qwen technical one-shot đã tiêu thụ.
- Mẫu kiểm tra: chỉ ký số bằng Ed25519 ephemeral in-memory, byte payload hư cấu, không có quyền dữ liệu thực. **Không** đọc TEST, không chạy teacher, không sử dụng Colab GPU.

## 2. Các tệp mới (tương ứng trên nhánh v1e)

| File dưới `scripts/research/six_ttm/` | Mục đích |
|---|---|
| `g1_signed_boundary_contract_v1e_candidate.py` | Xác minh chữ ký Ed25519 từ ba trust anchor khác nhau (owner, writer, witness), kiểm exact pins/rights và nonce/expiry; **không** cho phép science |
| `test_g1_signed_boundary_v1e_negative.py` | Synthetic negative tests: chữ ký, key swap, SHA bytes, replay, pack provenance, thời hạn và thiếu quyền |
| `g1_win32_job_failure_path_v1e_candidate.py` | Win32 suspended-child Job Object candidate; terminate đúng HANDLE con đã tạo trên đường lỗi chưa assign/resume |
| `test_g1_win32_job_failure_path_v1e_static.py` | Static safety test không yêu cầu Windows |
| `Run-G1-Win32FailureModes-PS51-V1E.ps1` | QA Windows 5.1 chỉ cho **hai** nhánh lỗi mới; lưu log trong `_tmp`, không chạy lại 45 ca |

Tài liệu khoa học: `docs/research/six-ttm/G1_METHODS_V1E_PRETEST_FROZEN_AMENDMENT_CANDIDATE_20261110.md`. Không tự thay threshold/split của G1.

## 3. Đã thực thi — QA của bên triển khai, không phải Codex

- Linux CPU Python 3.13.5, cryptography 46.0.4, pytest 9.0.2.
- `python -m pytest -q --disable-warnings` trong thư mục sáu tệp v1e → **61 tests PASS** (53 signed-boundary + 8 Win32 static).
- `python g1_win32_job_failure_path_v1e_candidate.py --mode status` xác nhận `production_qualified=false`, `real_gpu_used=false`, `science_executed=false`.
- Không có Windows target execution trên bản v1e; các ca injected Assign/Resume **NOT_TESTED_WINDOWS**, không được hưởng nhãn PASS từ gói Job Object cũ.
- Không tạo key owner thật, worker SID, ACL production, writer service, external witness endpoint hay T4 watchdog.

## 4. Sáu hard gate — chốt thiếu gì cho một vòng implementation cuối

| Gate | v1e source coverage | Production quyết định | Bằng chứng/đầu việc thực tế còn thiếu |
|---|---|---|---|
| **Owner/trusted launcher** | Exact signed owner contract, pin source/phase/run/dataset, reject reviewer=author; key thật `None` | `HOLD_NOT_PROVISIONED` | Owner-controlled public pin, launcher process riêng, code hash trusted, quyền nguồn và thời hạn. Owner ký *một quyết định khoa học riêng* sau adjudication |
| **Split/TEST broker** | Không cung cấp broker/service; đọc TEST chỉ trong v1c đã đóng băng và chưa được mở | `HOLD_NOT_IMPLEMENTED` | Principal/SID được cấp thực, DACL owner/broker riêng, TEST synthetic `AccessDenied` khi chạy bằng worker token kể cả alias/hardlink/junction, chứng minh tương tự trên Colab |
| **Trusted pack/writer ledger** | Phần kiểm chứng chữ ký writer ràng buộc đúng SHA của bytes nhận, run/split/seq/witness ack | `HOLD_NO_TRUSTED_WRITER` | Writer độc lập với worker, fsync, atomic recovery pack+receipt+ledger, crash injection ở mọi ranh giới, không tự phát hành receipt từ worker |
| **Monotonic witness/one-shot** | Xác minh fresh Ed25519 ACK, seq/previous/event/nonce/expiry và ba key riêng | `HOLD_NO_EXTERNAL_WITNESS` | Service append-only ngoài miền rollback controller **và** worker; latest-tip challenge cho mỗi quyết định và replay sau restore cả hai miền; signing key ở trust domain riêng |
| **GPU watchdog** | Mã candidate sửa failure cleanup, Linux static 8 PASS; Windows QA bản cũ đã PASS harmless child | `HOLD_V1E_WIN_TARGET_AND_T4_NOT_TESTED` | Run 2 Win32 fault modes trên Windows 11, xác minh không orphan/process tree; OS kill-capable supervisor và cumulative 3600s/model, 7200s/run, ≤12GiB T4 peak trên môi trường GPU được cấp phép |
| **Scientific methods** | v1e amendment candidate: group dependence, bootstrap fixed SST, CKA tolerance, power và INCONCLUSIVE | `REVIEW_HOLD` | Độc lập review code/estimand; quyền broker kiểm near duplicates trước science; chứng minh null exchangeability và power prospective, nếu thiếu giữ HOLD hoặc INCONCLUSIVE |

Không được biến các cổng này thành sáu giấy phép owner riêng. Chúng là **một gói admission** với bằng chứng gộp. Nhưng chữ ký/test synthetic và cùng người vận hành hai thư mục không phải bằng chứng production.

## 5. Yêu cầu kiểm định Codex độc lập

**Review task:** `TTM_SIX_G1_V1E_INTEGRATED_GATE_PRODUCTION_REVIEW_AND_MINIMAL_OWNER_DECISION`.

Codex phải xác minh origin, commit, SHA-1 Git blobs, các SHA-256 trong receipt và đúng mã đã chạy. Kiểm thử độc lập `61` ca chỉ khi cần; không chạy lại các ca author 45/29 hoặc Qwen technical smokes đã có chứng cứ. Chủ yếu cần thêm negative tests đối với (i) chữ ký giả với writer key, (ii) stale/cached ACK với challenge nonce mới, (iii) SOURCE HEAD swap, (iv) crash pack before/after receipt, (v) rollback cả hai miền, (vi) ACL bằng worker SID thật, (vii) suspended child failure paths trên Win32, (viii) chứng cứ OS T4 watchdog, (ix) giả định bootstrap/CKA/near-duplicate.

Phân loại từng gate `PASS/FAIL/NOT_TESTED` và **một phán quyết duy nhất** `PASS_DISTINCT_REVIEWER/HOLD/FAIL` với phạm vi và bằng chứng. `PASS` reviewer, nếu có, vẫn không cấp owner science permit. Nếu owner/key/ACL/external witness chưa provision, buộc tổng verdict `HOLD`, không mặc định FAIL khoa học.

Trong runbook Windows, khi được owner chạy, hãy đưa đúng `g1_win32_job_failure_path_v1e_candidate.py` vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`, đối chiếu SHA256 source rồi gọi `Run-G1-Win32FailureModes-PS51-V1E.ps1` trên PowerShell 5.1 không elevated. Runner chỉ tạo harmless suspended child (không GPU/TEST), không thay ACL, ghi receipt cục bộ và exit FAIL nếu child cleanup không xác nhận.

**Bảo mật:** Không commit raw SID/DACL, danh tính tài khoản, private source bytes, TEST IDs, private vectors, private keys, owner permit hoặc raw GPU telemetry có thông tin riêng. Giữ bằng chứng gốc trong `_tmp` dự án. Đẩy lên GitHub bản receipt đã khử dữ liệu + SHA, chỉ trên nhánh reviewer mới.

## 6. Quan hệ giữa thẩm định và science

1. Codex thẩm định v1e source+negative tests và v1e methods amendment, chỉ rõ blocker có bằng chứng.
2. Owner triển khai thực tế trong **một lô** tài khoản SID, broker, writer, witness độc lập, supervisor — hoặc quyết định không dùng full production assurance; không thể tự cho `PASS` nếu không tồn tại.
3. Một lượt Windows/Colab target QA tích hợp theo chính các negative tests chưa đạt, không rerun tests đã chốt.
4. Một phán quyết độc lập cho cả sáu gate.
5. **Chỉ sau đó** owner phê duyệt data rights/source staging/science one-shot riêng. G1 TEST vẫn không được mở trước các bước trên.

**CURRENT FINAL:** `V1E_SOURCE_VERSIONED=YES` · `AUTHOR_CPU_QA=PASS_61/61` · `WIN32_NEW_FAILURE_PATH=NOT_TESTED` · `PRODUCTION_TRUST_BOUNDARIES=HOLD` · `METHODS_V1E=REVIEW_PENDING` · `OWNER_SCIENCE_PERMIT=NOT_ISSUED` · `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_SIX_G1_V1E_INTEGRATED_GATE_PRODUCTION_REVIEW_AND_MINIMAL_OWNER_DECISION` — giao bộ nguồn/pins, receipt và tài liệu này cho Codex; Codex trả đúng một phán quyết và một danh sách blocker ngắn; sau đó owner thực hiện một gói provision hạ tầng được chứng thực, không mở science trước khi PASS.
