# G1 v1b · Phản biện độc lập sáu hard gate

**Ngày 09/11/2026, giờ Việt Nam**  
**Phán quyết duy nhất · `HOLD`**  
**`G1_SCIENCE_LOCK=HOLD`**

`reviewer_id=codex-distinct-g1-v1b-20261109-01a1bfe5-23f5`. Tôi thực hiện lượt review riêng với tác giả v1b và chịu trách nhiệm về QA. Ohm `01a1c009-f718-7531-a4c1-8c8552e26a63` rà soát tĩnh về phương pháp. Nietzsche `01a1c009-f835-7c53-aae7-56c06ae2dfd4` rà soát tĩnh về bảo mật và vận hành. Hai subagent không chạy QA, không nhận dữ liệu riêng và không ký thay owner. Tôi không phát hành permit.

## Baseline

Origin fetch/push đều là `https://github.com/minhtri22/TokenToModel-Lab.git`. Hai lần `git ls-remote` xác nhận `research/ttm-six-cross-model-representation-transfer-20261109` tại `cd6998b2459039a35fcca390958687ddb0b15340`. So với `d42ebb741d95338d64ae420dd86f3ab10ed591ad` ghi trong handoff, HEAD đi trước hai commit và chỉ thay handoff Markdown và dispatch JSON. Local và remote main cùng `b57b44e7287f842e81050c1faee337f636333dd0`. Repo gốc giữ nguyên ba mục untracked `_runtime/`, `demos/`, `experiments/p01/`. Tôi lấy metadata Git vào kho tạm bằng `git fetch --depth=1 --filter=blob:none`, kiểm `git ls-tree` rồi xuất bytes qua GitHub API và kiểm lại `git hash-object --no-filters` trước và sau QA. [Commit](https://github.com/minhtri22/TokenToModel-Lab/commit/cd6998b2459039a35fcca390958687ddb0b15340) · [So sánh hai mốc](https://github.com/minhtri22/TokenToModel-Lab/compare/d42ebb741d95338d64ae420dd86f3ab10ed591ad...cd6998b2459039a35fcca390958687ddb0b15340).

| Tệp thuộc scripts/research/six_ttm | Git blob |
|---|---|
| `g1_science_guard_v1b.py` | `d67b35cd8cba907904d0f23ccedd4b6b68d4850f` |
| `g1_science_core_v1b.py` | `94611c0449001230b2957487e152cd706f817516` |
| `g1_science_private_feature_extractor_v1b.py` | `2802c810d76b40e291188b2186439f53ccda0e13` |
| `test_g1_v1b_negative_qa.py` | `7e4270732b4c2f81b1677b82647456067989750d` |

Tôi đọc toàn bộ handoff, review độc lập trước, kế hoạch và báo cáo sửa, receipt tác giả, hợp đồng v1/v1a, receipt metadata 29 gate, phạm vi owner và hồ sơ technical Qwen. Receipt công bố T1 SHA-256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`, G1 SHA-256 `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6` và 128/64/64. Tôi kiểm pin và hồ sơ công bố, chưa tự băm manifest riêng. Phạm vi owner đã ghi chỉ gồm TRAIN cục bộ để seal và QA metadata. [Review trước](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/docs/research/six-ttm/G1_CODEX_DISTINCT_PREEXECUTION_REVIEW_HOLD_20261109.md) · [Phạm vi owner](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/docs/research/six-ttm/G1_OWNER_PRIVATE_DATA_SCOPE_ACCEPTANCE_FOR_SEAL_AND_QA_20261109.json) · [Receipt metadata](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/docs/research/six-ttm/G1_PRIVATE_MANIFEST_SEAL_AND_29_GATE_METADATA_QA_PASS_20261109.json).

## QA thực tế và tái lập

Chạy Windows CPU, Python 3.12.10, NumPy 2.4.4, cryptography 46.0.6. Chạy từ `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_V1B_CODEX_DISTINCT_REREVIEW_20261109`. Các tệp prereg/receipt công khai và producer v1a cạnh harness đều kiểm Git blob. Producer `aee230060f8202907953e0eeab0ae5b1099a584e` chỉ nhận file tổng hợp do harness tạo, với pin giả lập.

~~~powershell
$env:CUDA_VISIBLE_DEVICES='-1'
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:TEMP=(Get-Location).Path
$env:TMP=$env:TEMP
python -B .\test_g1_v1b_negative_qa.py
python -B .\g1_science_guard_v1b.py --mode selftest
python -B .\g1_science_core_v1b.py --mode synthetic-qa
python -B .\g1_science_private_feature_extractor_v1b.py --mode synthetic-qa
python -B .\reviewer_adversarial_v1b.py
~~~

- **Tái chạy QA tác giả.** 38/38, exit 0. Ba mode bổ sung exit 0, gồm guard key chưa provision, core 6 checks và extractor 8 probe. [Log tái chạy tác giả](pinned_author_qa_reproduction_cpu.log) · SHA-256 `99b11c445622643c9144d1be787c9564c93bfcdd59642ea27eb3552cd9dc4583`.
- **Harness riêng của reviewer.** 71 quan sát gồm **54 kiểm soát hoạt động và 17 lần tái lập thiếu sót/lỗi**. Exit 0 của harness nghĩa là các quan sát đã được tái lập, gồm cả lỗi. Các ca entry point vượt cổng quyền dùng stub và fixture tổng hợp. [Mã harness](reviewer_adversarial_v1b.py) · SHA-256 `30a814e165cec1bd123b005dc88af3ddb3ce88faaf252b11779971e883e0ffa7` · [Log reviewer](reviewer_adversarial_cpu.log) · SHA-256 `f1d68259ffe1acfee7996b0388b07cbdc6fce7cd347229143d1ed786492169bc`.

## Sáu nhóm hard gate

PASS/FAIL mô tả từng kiểm soát. NOT_TESTED mô tả phần triển khai chưa có bằng chứng vận hành.

### 1. AUTHORITY

**PASS** cho việc từ chối khi pin production chưa provision và chữ ký kiểm thử. Hai CLI thật dừng trên envelope giả. Fixture Ed25519 từ chối khóa lạ tự ký, chữ ký lệch khóa, payload sửa sau ký, hết hạn, thiếu author, reviewer trùng author, và sai phase/workspace/run/blob của runner. Khóa thử nghiệm chỉ ở RAM, không dùng trong CLI.

**HIGH · FAIL ràng buộc đầy đủ.** Payload được ký bằng khóa thử nghiệm đã ghim vẫn qua khi thiếu HEAD, thiếu phạm vi chi tiết, khai owner/reviewer tùy ý, hoặc ghi sai blob runner còn lại/amendment. Mỗi entry point chỉ đối chiếu blob chính nó. Guard import chưa được khóa qua launcher bất biến. **NOT_TESTED** quyền owner production. Pin hiện `None`. [Guard L41–80](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_guard_v1b.py#L41-L80) · [Core L112–118](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L112-L118) · [Extractor L82–86](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_private_feature_extractor_v1b.py#L82-L86).

### 2. SPLIT-BROKER

**PASS** cho bỏ full scan trong đường extractor. Trap TRAIN/DEV chỉ nhận đúng hai tên file split. Freeze thiếu, rỗng, sai hash hoặc sai run dừng trước GPU/nguồn.

**HIGH · FAIL cách ly khi plaintext đã truy cập được.** Hardlink Windows từ payload held-out giả sang tên TRAIN cho phép đọc bytes trước khi kiểm split. Validator freeze nhận digest đúng trên tài liệu thiếu seed/điểm DEV, 1.000 alpha boolean, digest phi hex, hoặc TRAIN/DEV digest `null`. **NOT_TESTED** broker production, ACL/release và quyền staging. Cần broker có quyền tối thiểu và giữ TEST bất khả truy cập trước khi xác nhận freeze. [Extractor L120–140](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_private_feature_extractor_v1b.py#L120-L140) · [Guard L216–246](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_guard_v1b.py#L216-L246).

### 3. PACK/LEDGER

**PASS** cho kiểm digest đã biết tin cậy. Giữ 64 ID đúng thứ tự nhưng thay tensor và tự cập nhật receipt vẫn bị từ chối. Đổi file sau lần đọc giữ nguyên buffer đã băm và parse. ZIP bomb, member quá cỡ, symlink và junction Windows thật bị chặn trên đường đọc.

**HIGH · FAIL xuất bản nguyên khối và ràng buộc path.** Fault trước hardlink không tạo tên cuối. Fault sau hardlink hoặc trước publish receipt để pack mồ côi. Qua junction làm root, writer ghi đích thật rồi mới từ chối ở postcheck. Mock swap ở `os.open` cho thấy handle chưa gắn với identity đã kiểm. Manifest hash và parse vẫn mở riêng. **NOT_TESTED** trusted writer, ACL production và commit nguyên khối cho pack/receipt/freeze. [Guard L83–156](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_guard_v1b.py#L83-L156) · [Core L88–109](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L88-L109) · [Extractor L318–325](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_private_feature_extractor_v1b.py#L318-L325).

### 4. ONE-SHOT

**PASS** cho marker local. Tám worker đồng thời chỉ một thắng. Fault trước marker không mở dữ liệu. Fault sau marker hoặc tại ranh giới đọc giữ marker và chặn lượt sau khi marker còn.

**CRITICAL · FAIL chuyển trạng thái.** Finalize thật từ chối freeze hợp lệ do chính `prepare` tạo. Replay mang `fit_dev_frozen_v1`, tệp mang `fit_dev_frozen_v1b`, phép so bao gồm `schema`, dẫn đến `FIT_DEV_SELECTION_CHANGED` trước TEST-read marker. TEST extraction là nhánh riêng có thể đã tiêu thụ quyền mở prefix nếu được cấp phép. Harness kiểm nhánh marker đọc riêng bằng stub chỉ sửa nhãn schema trong replay để tới nhánh đó. Xóa marker fixture cho phép lặp extraction và read sau STOP. **NOT_TESTED** external monotonic ledger chống rollback. [Core L161–172](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L161-L172) · [Core L323–355](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L323-L355) · [Extractor L277–299](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_private_feature_extractor_v1b.py#L277-L299).

### 5. GPU GUARD

**PASS** cho phép kiểm hợp tác 60 phút/model và 120 phút/run trên fake clock khi có số cộng dồn. Mock peak reserved 13 GiB bị từ chối cuối lượt. Tám file source và mười file target khớp SHA công bố trong technical receipts. Mock sửa tokenizer/config/index đều dừng trước local loader.

**HIGH · FAIL enforcement chủ động.** Load, forward và cleanup bị chặn trong fixture vẫn sống qua mốc 3.600 giây, chỉ báo quá hạn sau khi được trả về. Thiếu số cộng dồn thì khởi tạo 0. Peak là PyTorch allocator check cuối lượt, chưa chứng minh cap toàn thiết bị. **NOT_TESTED** watchdog OS, free-tier, endurance production. Loader hiện gọi `snapshot_download`. Bản khóa tương lai cần nguồn load nội bộ/offline và bảo vệ các file từ lúc hash đến lúc loader mở. [Budget L249–269](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_guard_v1b.py#L249-L269) · [Extractor L143–239](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_private_feature_extractor_v1b.py#L143-L239).

### 6. METHODS

**PASS** cho ridge và DEV selection trong fixture. Primal độc lập khớp alpha A/B/oracle, 1.000 null alpha và digest hoán vị. Chạy đủ 1.000 fit null, 1.000 CKA null và 2.000 bootstrap. TRAIN std probe bằng 0, DEV SST bằng 0, alpha/count sai bị từ chối. Full TEST SST và CKA phương sai 0 trả terminal inconclusive ở hàm đánh giá. Tám cặp probe đúng từng chuỗi và thứ tự, kể cả dấu cách đầu. Hash canonical `8daf50dc85d3bbd30061707186b1a1ef6172b8407b56dda5fea6e55d483406fe`.

**CRITICAL · FAIL kiểm định hình học.** Với centered Gram bất biến qua toàn bộ hoán vị, hai công thức observed/null làm tròn khác nhau và phép `>=` xếp mọi tie thấp hơn observed. Fixture cho `p=1/1001` thay vì `1`, vượt sai ngưỡng `0.01`. Dùng chung phép tính trên centered Gram đã khóa và khóa quy tắc tie. **NOT_TESTED** exchangeability và near-duplicate thật. [Core L175–181](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L175-L181) · [Core L224–241](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L224-L241) · [Guard L297–303](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_guard_v1b.py#L297-L303).

**Privacy.** Hai CLI thật trên envelope giả trả JSON STOP không chứa sentinel, workspace, traceback hoặc payload ngoại lệ. Kiểm kê tên tệp tại commit ghim không thấy feature NPZ, plaintext split, TinyStories text hoặc safetensors. Điều này chưa xác lập log thư viện lúc dùng GPU, ACL, retention hoặc nội dung toàn bộ lịch sử Git.

## Phân xử amendment

- **Bootstrap.** Chấp nhận fixed-full-TEST-SST cho endpoint feasibility có điều kiện. Resample paired chênh lệch squared loss theo truyện, giữ 8 mẫu số SST so với TRAIN mean và lấy phân vị 2,5%. Điểm trên toàn cohort vẫn là chênh macro-R² so với TRAIN mean. Khoảng lấy mẫu có điều kiện trên fit và mẫu số đã khóa. Fixture 63+1 có **766/2.000** draw bỏ truyện lệch và lower bound **0,0**. Giữ terminal inconclusive khi full SST hoặc CKA suy biến, và giữ trạng thái terminal khi lỗi sau tiêu thụ. [Guard L272–294](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_guard_v1b.py#L272-L294).
- **Mapping v1a.** Chấp nhận first occurrence 0-based, hash-sort và exact dedup trước split 128/64/64. Fixture 277 hàng cho 276 raw ID, 273 sau loại một normalized story trùng và hai prefix trùng. Đảo thứ tự input cho cùng output. Giữ manifest hiện hữu. Exact dedup chưa chứng minh near-duplicate families, tính trao đổi được của hai phép hoán vị hoặc tính độc lập của story bootstrap. Nếu thấy phụ thuộc nhóm đáng kể, chốt xử lý nhóm trước release và không tái chọn cohort sau outcome. Chồng lấn với pretraining Qwen chưa rõ. [V1a amendment](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/docs/research/six-ttm/G1_V1A_DATA_MAPPING_DEDUP_FUNCTIONAL_ALIGNMENT_AMENDMENT_REVIEW_CANDIDATE_20261109.md#L11-L31).
- **A→P/B-direct.** Cùng lưới ridge nhưng A dùng target hidden lúc TRAIN và thêm lựa chọn alpha của P trên DEV. A→P affine theo source features gốc. Báo A, B và oracle, diễn giải A–B ở mức mô tả. Fixture cho R² A `0.98710085`, B `0.98745279`, oracle `0.99536269` và lower bootstrap `0.78746336`. Shuffle TRAIN kiểm lợi thế ghép đúng TRAIN, CKA kiểm ghép đúng TEST, CI so với TRAIN mean. Tín hiệu bề mặt chung có thể ảnh hưởng cả hai phép hoán vị. Xoay trực giao toàn hạng **sau** chuẩn hóa là kiểm tra trung tính, sai khác dự đoán tối đa `1.07e-14` trong fixture. Đưa F vào QA trung tính, ghi rõ bỏ layer 14 và source-response diagnostics, giữ retrieval ở mức mô tả với quy tắc tie rõ. [Core L121–172](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/scripts/research/six_ttm/g1_science_core_v1b.py#L121-L172) · [Phương pháp gốc](https://github.com/minhtri22/TokenToModel-Lab/blob/cd6998b2459039a35fcca390958687ddb0b15340/docs/research/six-ttm/G1_SCIENCE_PREREG_V1_METHODS_AND_THRESHOLDS_20261109.md#L63-L95).
- **Phạm vi.** Giữ 8 probe, 128/64/64, lưới `{1,10,100}`, 1.000 shuffle TRAIN, 1.000 CKA null, 2.000 bootstrap, và các ngưỡng A R² `≥0.10`, gain trên shuffle p95 `≥0.10`, p shuffle/CKA `≤0.01`, lower bootstrap `>0`, oracle R² `≥0.20`. Bản amendment cần nói rõ verdict âm và mọi terminal inconclusive. Mẫu 64 truyện chỉ phục vụ scoped feasibility. Power, cơ chế nhân quả SIX và lợi ích huấn luyện TTM chưa được xác lập.

## Một gói xử lý tiếp theo

1. Sửa freeze schema, yêu cầu đủ khóa/digest đúng kiểu, so đầy đủ và thử chuyển trạng thái prepare → finalize bằng fixture. Dùng chung phép tính CKA observed/null và khóa quy tắc tie. Ghim source và amendment mới.
2. Trong cùng gói, tích hợp launcher đã bảo vệ, authority pin do owner quản lý, broker có quyền tối thiểu và trusted ledger ở ngoài workspace. Ràng buộc owner/reviewer/author, HEAD, guard và hai runner, amendment, manifest, phase/scope/workspace/run/expiry. Bảo vệ TEST trước freeze. Commit pack/receipt/freeze qua một trạng thái có thể xác thực. Ghi chuyển trạng thái bất hồi chuyển từ `ADMITTED` đến `TERMINAL`, kể cả STOP hoặc mất workspace.
3. Ghép watchdog có quyền kill và budget bền qua split, sau đó chạy **một** QA tích hợp trên dữ liệu giả cho crash, race, rollback, privacy và tài nguyên. Bản ghim mới đi qua một reviewer độc lập trước một quyết định owner về science và quyền dữ liệu. Giữ nguyên hai technical smoke đã tiêu thụ.

**Bảo toàn.** Không chạy G1 science, không mở TEST riêng tư, không tải Qwen, không sửa checkpoint, không reseal. Các tệp mới chỉ nằm trong `_tmp` bị Git ignore. Main và PR #12 đã đóng được kiểm lại cùng SHA. Blob `lineage.md` trên main, index và working file đều `971fbd8eccdf4719fee6b83a3c0f4c44b13ebaa9`. Blob trên nhánh nghiên cứu ghim là `b7c19da4e77e26e3ad301b771af560f8f8795159`. Không commit hay push.
