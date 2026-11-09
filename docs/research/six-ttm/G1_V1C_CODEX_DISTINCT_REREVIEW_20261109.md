# TTM × SIX G1 v1c — Báo cáo phản biện độc lập và phân xử một gói hard gate

**Ngày:** 09/11/2026 (Asia/Ho_Chi_Minh)
**Reviewer ID:** codex-native2-distinct-g1-v1c-20261109
**Vai trò:** Reviewer khoa học/bảo mật độc lập với agent triển khai nguồn v1c. Không sử dụng subagent.
**Phạm vi:** Kiểm thử CPU với dữ liệu tổng hợp (synthetic QA), đối kháng do reviewer thiết kế và phân tích nguồn tĩnh.
**Review schema:** ttm.six.g1.v1c.distinct_preexecution_review.v1
**Task:** TTM_SIX_XMODEL_G1_V1C_DISTINCT_CODEX_REREVIEW_AND_SINGLE_INTEGRATED_HARD_GATE_CLOSURE

## 1. Danh tính nguồn và môi trường

- Repository/origin đã kiểm bằng git remote: https://github.com/minhtri22/TokenToModel-Lab.git.
- Research branch được kiểm từ origin bằng git ls-remote: research/ttm-six-cross-model-representation-transfer-20261109, HEAD **d5d0c5346a595557a76349f900d09be50bce289c**.
- Local main và origin/main đều tại **b57b44e7287f842e81050c1faee337f636333dd0** lúc kiểm tra. Checkout main vẫn trên main, không ghi đè các untracked files hiện hữu.
- Kiểm thử được lưu tại **D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_V1C_CODEX_DISTINCT_REREVIEW_20261109**. Worktree riêng dựa trên exact reviewed HEAD.
- Thiết bị **DESKTOP-4PSD0G2**, Windows 11 build 26300, Python 3.12.10, NumPy 2.4.4, cryptography 46.0.6, CPU-only. Không chạy CUDA/Qwen.
- T1 metadata SHA-256 **9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9** và G1 sealed metadata SHA-256 **6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6** là **pin tài liệu được đối chiếu**, không phải manifest private được mở/băm lại. Split ghi trong hợp đồng là TRAIN 128 / DEV 64 / TEST 64.

Năm Git blob tại exact commit được xác minh bằng git rev-parse HEAD:path và đối chiếu riêng với git hash-object --no-filters của bản stage test.

| Nguồn dưới scripts/research/six_ttm/ | Git blob SHA-1 | Tree so với bản stage |
| --- | --- | --- |
| g1_science_guard_v1c.py | 4554a3e12911cbf0606a8be053660cad0c38f374 | PASS |
| g1_science_core_v1c.py | f591bd617feb007c20023a313ebc5f429471d8b2 | PASS |
| g1_science_private_feature_extractor_v1c.py | 9bb28fe39999fba0bab5474e2644b11f7940c06a | PASS |
| test_g1_v1c_critical_qa.py | 01030f2aba4a7356d093664c628973a73b458475 | PASS |
| test_g1_v1c_hard_gate_negative_qa.py | 9d824034124f210d9dd58c23954d4da66ba119c2 | PASS |

Bốn bản sao v1b lịch sử đã đối chiếu qua git hash-object --no-filters: guard **d67b35cd8cba907904d0f23ccedd4b6b68d4850f**, core **94611c0449001230b2957487e152cd706f817516**, extractor **2802c810d76b40e291188b2186439f53ccda0e13**, negative QA **7e4270732b4c2f81b1677b82647456067989750d**. Báo cáo v1b reviewer có blob **73e646a8b642873e7fceaf1cf1f92db02c772348**. Các bản test v1b chỉ dùng synthetic input.

## 2. Kết quả thực thi đã đối chiếu

**Replay kiểm thử của tác giả trên CPU** được chạy trước trong review task và log đã được đối chiếu SHA-256. Đây là tái chạy chương trình kiểm thử do tác giả viết, không chuyển 29 kết quả sang nhãn kiểm chứng độc lập.

| Entrypoint chạy ở isolated QA directory (Python -B, CPU) | Quan sát | Phân loại |
| --- | --- | --- |
| test_g1_v1c_critical_qa.py | 7/7; freeze replay, CKA invariant p=1, informative p=1/1001 | AUTHOR_TEST_REPLAY_PASS |
| test_g1_v1c_hard_gate_negative_qa.py | 22/22 negative cases | AUTHOR_TEST_REPLAY_PASS |
| g1_science_guard_v1c.py --mode selftest | key production chưa provision, science_authorized=false | PASS_SCOPED_SELFTEST |
| g1_science_core_v1c.py --mode synthetic-qa | 6 kiểm tra synthetic | PASS_SCOPED_SELFTEST |
| g1_science_private_feature_extractor_v1c.py --mode synthetic-qa | 8 probes synthetic | PASS_SCOPED_SELFTEST |

**Bộ đối kháng do reviewer thiết kế**, chạy trong cùng task ở một lần CPU-only, có 63 quan sát gồm **51 CONTROL_PASS**, **10 DEFECT_REPRODUCED** và **2 PASS_CKA**. Exit code của harness bằng 0 vì harness **đã bắt được các phản ví dụ mong đợi**, không phải 63/63 hard gate PASS. Trong 10 quan sát khiếm khuyết có **2 CRITICAL v1b lịch sử**, **4 quan sát thiếu launcher/nguồn tin cậy xuyên thành phần**, và **4 quan sát thiếu broker, trusted pack, atomic commit, monotonic one-shot**. Đây là các lần quan sát, không khẳng định 10 lỗi độc lập mới.

**CLI pre-TEST bổ sung** gọi đúng đường prepare → finalize trên v1b và v1c, dùng TRAIN/DEV synthetic, mock có khai báo rõ cho permit/manifest/pack I/O. Kết quả v1b dừng tại STOP_G1_FIT_DEV_SELECTION_CHANGED. V1c vượt freeze/replay và dừng tại STOP_G1_TEST_PACK_SHA_MISSING do fixture cố ý không cấp TEST digest. Cả hai đều **0 lượt mở TEST, marker chưa tiêu thụ, exit code của harness 0**. Kết quả xác nhận entrypoint trước TEST trong fixture, **chưa chứng minh production end-to-end**.

Hình thức kiểm thử được tái lập từ thư mục evidence bằng lệnh Python -B cho năm entrypoint ở bảng trên, sau đó chạy Python -B với reviewer_independent_adversarial_v1c.py và reviewer_cli_freeze_pretest_v1c.py khi các source v1b/v1c đã được stage cạnh nhau. Log lưu output từng quan sát. Hai harness độc lập dùng mock hoặc synthetic Ed25519 key trong RAM, không sở hữu production permit.

## 3. Hai CRITICAL — so sánh v1b và v1c

### CRITICAL A. Freeze và replay DEV

**v1b, DEFECT_REPRODUCED:** prepare/finalize tạo freeze schema ttm.six.g1.fit_dev_frozen_v1b nhưng hàm prepare tái tính trả ttm.six.g1.fit_dev_frozen_v1. So sánh gây STOP_G1_FIT_DEV_SELECTION_CHANGED trước bước mở TEST. Kiểm chứng cả qua trực tiếp hàm và đường CLI có mock.

**v1c, PASS_INDEPENDENT_SYNTHETIC:** prepare dùng cùng schema; replay trùng alpha/seed, 1.000 null alpha, permutation digest và freeze SHA. Đã thử freeze sai run/pack SHA, thiếu alpha/seed, alpha boolean, digest không phải hex, nulls thiếu, hash cũ, JSON rỗng và trường dư. Chúng đều bị từ chối. Marker TEST không bị dùng ở bước xác minh DEV. Tham chiếu nguồn: core v1c L161-L171 và L353-L380; guard v1c L237-L272.

**Giới hạn:** giao thức sản xuất bảo vệ TEST và tính bất hồi chuyển sau crash chưa được chứng minh.

### CRITICAL B. False-positive CKA

**v1b, DEFECT_REPRODUCED:** centered Gram bất biến với hoán vị 64 hàng cho p=**0.000999000999000999** vì observed và null đi qua phép tính số học khác thứ tự. Bằng chứng số đã ghi observed 1.0000000000000013, null 0.9999999999999998 đến 1.0.

**v1c, PASS_INDEPENDENT_SYNTHETIC:** cùng Gram/denominator được dùng lại cho 1.000 null. Predicate null >= observed - tol, với tol=64 × epsilon(float64) × max(1, |observed|), cho **p=1.0** ở bất biến. Reviewer kiểm lại 1.000 phép hoán vị và p-value cộng một. Với fixture ghép thực sự có tương quan, p=**0.000999000999000999**. Với hình học suy biến, trạng thái **INCONCLUSIVE_GEOMETRY_DEGENERATE**. Hai thử nghiệm scale 0.1 và 1000.0 vẫn đi qua nhánh CKA. Tham chiếu core v1c L179-L211.

**Phương pháp:** phép tolerance 64ε có hiệu ứng lên tie, type-I và power. Đây là sửa đổi tiền đăng ký (prospective preregistration amendment). Reviewer xác nhận hành vi số học trong synthetic fixtures và **giữ phân xử phương pháp mở**, chưa chấp thuận như quy tắc science cuối cùng.

## 4. Sáu hard gate — phân xử một gói tích hợp

Cột **Local** phân loại hành vi test thực sự. Cột **Production** dùng **NOT_TESTED** nếu thiếu bằng chứng từ môi trường tin cậy thật. Mức độ phản ánh rủi ro nếu chạy science ngay.

| Hard gate | Local evidence / kết quả | Production | Severity và thiếu hụt cần đóng |
| --- | --- | --- | --- |
| **1. Owner authority** | PASS kiểm chữ ký Ed25519 synthetic, key thiếu, chữ ký sai, owner/reviewer trùng, expiry/scope/HEAD-format sai; **FAIL** 4 quan sát thiếu xác thực xuyên thành phần bởi launcher tin cậy | **NOT_TESTED** | HIGH. Owner key thực chưa provision (guard L16, L41-L80); source HEAD, guard/core/extractor/amendment và trusted launcher chưa được chứng thực nguyên khối. |
| **2. Split broker / TEST isolation** | PASS TEST gate từ chối đọc khi chưa freeze; **FAIL** synthetic hardlink alias được trình bày dưới tên TRAIN trong khi nội dung là heldout sentinel | **NOT_TESTED** | HIGH. open_split_payload đọc file theo tên (guard L275-L284); trusted broker, Windows ACL/isolation/hardlink deny, quyền trước freeze chưa có bằng chứng. |
| **3. Pack provenance / ledger** | PASS trusted digest mismatch bị từ chối; **FAIL** pack numeric đổi cùng tự tạo receipt vẫn tự nhất quán, và crash injection tạo orphan pack | **NOT_TESTED** | HIGH. Authenticated external writer, transaction pack+receipt+freeze/lineage chưa chứng minh; guard L145-L177, extractor L318-L325, core L344-L352. |
| **4. One-shot** | PASS marker có khóa tạo mới; **FAIL** xóa/rollback marker fixture cho phép cấp lại quyền chạy | **NOT_TESTED** | CRITICAL ở ranh giới chống phát lại. Marker nằm trong workspace rollback được (core L375-L380; extractor L277-L299). Cần monotonic ledger ngoài miền ghi của worker, crash/terminal durable. |
| **5. GPU watchdog** | PASS cooperative Budget.check tại lần poll sau mốc 3.601 giây; external kill **NOT_TESTED** | **NOT_TESTED** | HIGH. Không có bằng chứng OS forced-kill khi forward/load treo, VRAM, 3.600 giây/mô hình và 7.200 giây/toàn lượt trên host dự kiến (guard L287-L310; extractor L201-L231). |
| **6. Scientific methods** | PASS synthetic ridge primal/dual, rotation neutrality, 1.000 shuffle + 1.000 CKA null + 2.000 paired bootstrap, degenerate SST, 8 exact probes. CKA amendment vẫn cần phân xử | **NOT_TESTED** | HIGH. Chưa xác thực exchangeability/near-duplicate families ngoài synthetic, power cho TEST=64, v1a dedup và v1b bootstrap estimand / v1c tie rule trong amendment duy nhất. |

**Tích hợp hard-gate admission chưa đóng:** test-local PASS chỉ xác nhận các kiểm soát đã kiểm. Các FAIL ở trên là phản ví dụ cụ thể cho boundary còn thiếu. Production NOT_TESTED không thể nâng thành PASS từ tính chất fail-closed của mã.

## 5. Giới hạn khoa học và bảo toàn quyền

- Kết quả G1 dự kiến chỉ kết luận scoped cross-model representation feasibility, không chứng minh cơ chế nhân quả đặc thù SIX, ưu thế so với linear direct probe, hoặc tác dụng huấn luyện TTM.
- A→P và B-direct có ngân sách thông tin và lựa chọn alpha khác nhau; phải diễn giải hiệu số ở mức mô tả theo hợp đồng. Không diễn giải kết quả âm như không có biểu diễn chuyển giao nếu hình học/SST suy biến hoặc power chưa đủ.
- TEST=64 chưa có bảo đảm 80% statistical power. Near duplicates, tính trao đổi được của permutations/bootstrap, overlap pretraining và ảnh hưởng first-occurrence dedup là các giả định khoa học còn mở.
- Trong phiên review không đọc nội dung TinyStories/TEST, không tạo feature pack real, không chạy Qwen, không tải weights và không cấp permit. Chỉ dùng synthetic story IDs và synthetic numeric arrays.
- Mã nguồn v1c, manifest, main, PR #12, lineage.md và checkpoint không được sửa.

## 6. Gói khắc phục tích hợp tối thiểu

Một gói **G1_INTEGRATED_PREEXECUTION_ADMISSION**, được thực thi và đánh giá chung trong **một vòng reviewer re-adjudication**:

1. **Trusted launcher / owner authority**. Chứng thực owner public-key fingerprint được quản lý độc lập, bản ký duy nhất ràng buộc HEAD, cả ba executable blobs, amendment, owner/reviewer khác tác giả, source/split/run/phase/workspace/expiry, data rights. Test negative signature/code swap trước bất kỳ data/GPU.
2. **Trusted split broker**. Cô lập TEST bytes bằng principal/ACL riêng với worker TRAIN/DEV, chặn hardlink/junction/alias và chứng minh TEST không thể được mở trước freeze đã chứng thực.
3. **Authenticated transactional writer + monotonic ledger**. Receipt/tensor/freeze/source lineage gắn trusted writer và một trạng thái atomic recoverable; chuyển ADMITTED → CONSUMED → TERMINAL bền vững ngoài worker-controlled workspace, có kiểm chứng crash/concurrency/rollback.
4. **Supervised GPU worker + kill watchdog**. Controller ngoài tiến trình kill được worker khi vượt 3.600 giây mỗi model / 7.200 giây toàn lượt, lưu cumulative budget trong ledger và chứng minh resource-limits trên host mục tiêu bằng kiểm thử được cấp phép riêng.
5. **Single scientific amendment decision**. Phê chuẩn hoặc bác bỏ v1a dedup/mapping, v1b fixed-full-TEST-SST paired bootstrap và v1c CKA tie rule; khóa exchangeability, near-duplicate/group dependencies, cách báo negative/inconclusive và giới hạn power. Không điều chỉnh post-TEST.

Gói trên là **một admission package**, không phát hành sáu vi-giấy-phép kỹ thuật. Sau bằng chứng production và phân xử amendment mới trình chủ sở hữu quyết định science riêng.

## 7. Bằng chứng, SHA-256 và phán quyết

Các tệp bằng chứng không chứa private TEST/story source, hidden-state tensors real, owner secret, permit real hoặc 256 content-ID private. Đường dẫn dưới cùng thư mục reviewer-evidence/G1_V1C_CODEX_DISTINCT_20261109. SHA của tệp được lưu lại trong SHA256SUMS.txt (mỗi dòng là SHA-256 + tên file).

| Bằng chứng | SHA-256 |
| --- | --- |
| author_baseline_replay_cpu.log | 7371da27468f8b48000cb26d821170d80ac60079baf2f4f7c7b453a407e5ed30 |
| reviewer_independent_adversarial_v1c.py | 9335971a82980cc4dace1b5cd9891f4aaed382b9b5d29655104d62da527843c9 |
| reviewer_independent_adversarial_v1c.log | 372c08e101d01817d64aed54659fab335da274b4bf76323682d54584755feb3e |
| reviewer_independent_adversarial_v1c_receipt.json | 3eb16277f1920425872e4721ee09e65423bb1c12c26ac711e9279a11382f8057 |
| reviewer_cli_freeze_pretest_v1c.py | 0b9f7a4ce28f554db05f624fadfd656c0637bf252b6b8ef45862ce30d9d7a3f9 |
| reviewer_cli_freeze_pretest_v1c.log | d12fe97252402716249fce5b223e4076dab105a5feb168a050c8ac4a733c863e |

**Phán quyết độc lập duy nhất: HOLD**.

Hai CRITICAL v1b được tái lập, sửa v1c đã PASS trong phạm vi synthetic CPU và CLI pre-TEST mock. Hệ thống chưa có đủ bằng chứng production cho sáu hard gate, trong đó có các phản ví dụ trực tiếp cho split trust, pack transactions và one-shot rollback. Phán quyết này là review preexecution. **Reviewer không cấp phép science.**

G1_SCIENCE_LOCK=HOLD
SCIENCE_EXECUTED=NO
G1_PRIVATE_TEST_OPENED=NO
OWNER_SCIENCE_PERMIT=NOT_ISSUED

**Bước thực hiện tiếp theo** — TTM_SIX_G1_INTEGRATED_PREEXECUTION_ADMISSION_MINIMAL_IMPLEMENTATION_AND_DISTINCT_READJUDICATION. Chủ sở hữu phê duyệt phạm vi tích hợp một lần nếu muốn triển khai. Reviewer tiếp theo kiểm tra cả gói bằng các negative tests đã ghim trước khi có quyết định khoa học riêng.
