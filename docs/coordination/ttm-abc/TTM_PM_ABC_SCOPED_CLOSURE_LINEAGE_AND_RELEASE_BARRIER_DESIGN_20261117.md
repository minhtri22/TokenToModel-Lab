# TTM PM — A/B/C scoped closure, lineage inventory và prospective release barriers

**Operation:** `TTM_PM_ABC_SCOPED_ENGINEERING_CLOSURE_LINEAGE_INVENTORY_AND_PROSPECTIVE_RELEASE_BARRIER_DESIGN_SINGLE_GATE`
**Ngày phân xử:** 2026-11-17 (Asia/Bangkok) · **Chế độ:** DESIGN_ONLY / EXISTING_SOURCE_READBACK · **Không phải science admission hoặc merge permit**.
**Kho sự thật:** `minhtri22/TokenToModel-Lab` · `main` chính xác tại lúc kiểm toán `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` · `lineage.md` main Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`, kết thúc tại L0029 (30 entry L0000–L0029).

## I. Phán quyết PM tích hợp — kết quả có phạm vi

| Track / Gate | Quyết định hiện hành | Chứng cứ chính và ranh giới |
|---|---|---|
| A M0/I1 | **`I1_PASS_SCOPED_MEASUREMENT`** | PR #33 source `ec197b5f00d3a037420390edd11ee55047e1d37f`; QA độc lập 35/35, custody Windows 38/38, 80/80 case + 5/5 group; fixture SHA256 `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`; đo lường M0, **không chứng minh model capability** |
| A release/I2 | **`HOLD_RELEASE_PREFLIGHT` / `I2_NOT_EXECUTED`** | Preflight owner-internal exit 2 `HOLD_OWNER_INTERNAL_I1_NOT_PASS`; receipt/freeze SHA pin, no-overwrite TOCTOU và ràng buộc reparse/đường dẫn còn là điều kiện phát hành; không thay đổi guard chỉ để PASS |
| B M3/B-G0..B-G6 | **`PASS_ENGINEERING_BASELINE_SCOPED_BY_PRIOR_PM`**, có dissent | B source PR #34 `43896bcd034c82e8433bc6a2b53eefbd936616fb`; synthetic CPU GPT train/eval/resume, CI + owner native; khác với năng lực khoa học |
| B native V3 lịch sử | **`HOLD_NATIVE_QA` immutable** | Receipt SHA256 `063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188`; intentionally negative memory exit 1/MemoryError nhưng `PeakJobMemoryUsed=429174784` > cap 268435456; differential 3/3 ủng hộ hard rejection, chưa giải thích kernel peak; reviewer `HOLD_PEAK_ACCOUNTING` được ghi riêng |
| C M4/C-G5 | **`PASS_DESIGN_SCOPED`** | C source `185d465c31f5f4bef6220be95e39dac1ae81c5b8`, distinct review `9fac5a675955d8b91d6855d27907f239cbfb745f`, 35/35 và C-F01/F02 đã sửa. Real data C-G1 HOLD; gold/rubric C-G2 UNPROVEN; C-G3/G6 DESIGN_ONLY; C-G7 NOT_AUTHORIZED; C-G8 NOT_EXECUTED |
| B–C synthetic SFT interface | **`BC_INTERFACE_PASS_ENGINEERING_SCOPED`** | B PR #36 source CI `a83e1526bce842761f3051dad28b90a55395a6aa`; exact PR HEAD `09de6a46574146d863f416e056fcf01091f3efb8`; C contract QA 34/34 x Windows/Linux; PM distinct 12/12 per OS; 8/8 frozen artifact+manifest Git blobs; CPU forward/backward không optimizer |
| BC-0..BC-5 | **`PASS_ENGINEERING_SCOPED`**, F01–F06 closed trong scope tin cậy | Identity UTF-8 C→byte B, role/mask/+1, metadata-only checkpoint, 7 SHA trên byte lưu, canonical LF và rejection giả mạo/symlink ở mức path; không chứng nhận dữ liệu/custody chưa tin cậy hoặc race-safe IO |
| Real SFT, A I2, M5–M8 science / GPU / TEST | **`NOT_AUTHORIZED / NOT_EXECUTED`** | Không có bằng chứng chạy mới trên thực nghiệm A/B/C ở gate này; các nghiên cứu TTM lịch sử trong main lineage không bị phủ nhận |
| Merge / release | **`HOLD_OWNER_DECISION`** | PR #28/#33/#34/#35/#36 đều Draft/unmerged tại snapshot; GitHub `mergeable=true` không tương đương được phép merge |

## II. Exact Git dependency tree và snapshot

```text
main @ f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3
├─ PR #28 (Draft) @ ebdc54575eed1ff60c402eecf60289f408bb38ca
│  └─ PR #33 (Draft) @ 771314c07ba061ebeb1baa87018248ed73181079
│      └─ A I1 measured/executable source @ ec197b5f00d3a037420390edd11ee55047e1d37f
├─ PR #34 (Draft) @ 43896bcd034c82e8433bc6a2b53eefbd936616fb
│  └─ PR #36 (Draft) @ 09de6a46574146d863f416e056fcf01091f3efb8
│      └─ B–C corrected/CI-tested code @ a83e1526bce842761f3051dad28b90a55395a6aa
└─ PR #35 (Draft) @ 00afd25aa2234e30f7602592d49d5d9f2947965b
   └─ C design reviewed source @ 185d465c31f5f4bef6220be95e39dac1ae81c5b8

Separate evidence, **không nằm trong main tree cho đến khi merge được cho phép**:
  B M3 scoped PM review @ fdffbf2cc3c517d25dddae89501c091c58f2608d
  B–C distinct PM final QA @ 82aaf2a881bd677afd8f6e600eb570aea897fdba
  C separate F05/F06 review @ 9578291ae7c64ac58960fca679356e956ad9d51b
```

Trạng thái nhánh là ảnh chụp tại thời điểm kiểm tra. Các PR ở chế độ Draft và chưa merge; không tự tính điều kiện merge từ nhãn `mergeable`. PR #33 phụ thuộc PR #28; PR #36 phụ thuộc PR #34; PR #35 tách từ main. Lượt này **không** đánh giá toàn bộ 65 nhánh trong inventory lịch sử, không giải quyết tất cả xung đột tích hợp hay ủy quyền merge.

## III. Lineage inventory — append-only proposal, chưa ghi vào `lineage.md`

`main/lineage.md` có 30 entry L0000–L0029, mới nhất L0029 (2026-11-14). PR #33/#34/#35/#36 không thay đổi `lineage.md` theo danh sách diff PR. Có bằng chứng mới từ 16–17/11 trên nhánh độc lập, vì vậy chuẩn bị các **mục ứng viên chưa cấp số L**:

| Khóa ứng viên | Loại | Cần ghi khi owner cho phép append | Không được viết như |
|---|---|---|---|
| `ABC-CAND-A-I1` | MEASUREMENT_VALIDITY_SCOPED | I1 PASS, exact source, fixture/QA, I2 HOLD, prior HOLD retained | success model forward hoặc I2 release |
| `ABC-CAND-B-M3` | ENGINEERING_QA_WITH_DISSENT | M3 PM scoped PASS; V3 native HOLD; differential PASS 3/3; peak counter unresolved, reviewer dissent | V3 script PASS hoặc cap kernel proven |
| `ABC-CAND-C-M4` | DESIGN_QA_SCOPED | C M4 design PASS 35/35; C-G1 HOLD, C-G2 UNPROVEN, M5–M8 not authorized | data rights/gold validated hoặc SFT efficacy |
| `ABC-CAND-BC-V2` | SYNTHETIC_INTERFACE_ENGINEERING_QA | C Part B, B corrected CI, PM distinct 12/12 per OS, F01–F06 closure; no real SFT | real checkpoint compatibility hoặc instruction improvement |
| `ABC-CAND-PM-CLOSURE` | PROGRAM_GOVERNANCE_DESIGN | scoped closes, release barrier HOLD, Git graph, owner decision proposal only | global science approval hoặc code merge |

Không sao chép/mượn ID Lxxxx của các nhánh phụ. Sau khi có merge/append riêng, kiểm tra lại `main` HEAD và tail lineage, cấp ID nối tiếp **tại thời điểm append**, giữ mọi entry L0000–L0029 nguyên văn, và trỏ đến evidence ở nhánh/commit immutable. Các FAIL/HOLD phải được ghi như lịch sử, không chuyển thành PASS vô điều kiện. Xem tài liệu ứng viên lineage đi kèm trong cùng nhánh governance.

## IV. Prospective release barrier matrix — các điều kiện cần, chưa cho phép chạy

| Barrier | Cho A I2 | Cho real SFT M6 | Điều kiện chứng minh trước khi xin quyết định owner | Trạng thái hiện tại |
|---|---|---|---|---|
| R0: exact source + dependency graph | REQUIRED | REQUIRED | Lock exact PR/source/base, model/tokenizer/adapter version, merged dependency policy; CI+QA on exact candidate | PARTIAL: code pins verified; no merge authorized |
| R1: valid measurement/gold/rater | REQUIRED | REQUIRED | A I1 frozen metric can be used only in its scope; science endpoint/rubric, negative/positive controls, rater independence and test non-leakage separately validated | A I1 PASS, C-G2 UNPROVEN, I2 HOLD |
| R2: provenance, rights, splits | REQUIRED for chosen assets | REQUIRED for real SFT corpus | Actual source bytes/terms/allowed uses, train-only tokenizer, contamination/near-dup and fresh heldout; no re-use of consumed historical TEST/FRESH16/FINAL24 as new confirmatory sets | C-G1 HOLD; no new admitted corpus |
| R3: checkpoint/tokenizer correspondence | REQUIRED | REQUIRED | Exact original checkpoint SHA/weights custody, tokenizer identity (B byte-ID synthetic v2 ≠ automatically historical T4 BPE), mapping, context/vocab, resume schema, reliable model-load contract | BC checkpoint is METADATA_ONLY, weights NOT_CREATED |
| R4: native resources and subprocess guard | REQUIRED | REQUIRED if execution | Resource budget and hard limit on exact owner host/runner, measured CPU/RAM/GPU/VRAM, watchdog, cleanup, fail-closed readback, stop conditions; do not reuse B-M3 V3 result as new permit | B-M3 scoped evidence, new SFT owner-native NOT_EXECUTED |
| R5: filesystem and evidence custody | REQUIRED | REQUIRED | No overwrite, immutable source/output, freeze receipt hash binding, parent reparse/junction policy, close check-then-write TOCTOU on untrusted paths or explicitly restrict trusted root | A OnePack gap; BC path-level trusted-root only |
| R6: frozen prereg and equal-budget study design | REQUIRED for any confirmatory science | REQUIRED | Hypotheses/endpoints/seeds/splits/decision rules, compute and target exposure parity, control arms, negative cases, boundary on reselection; one-shot study plan | DESIGN_ONLY / NOT_FROZEN for new study |
| R7: new independent exact-candidate QA | REQUIRED | REQUIRED | QA source/test custody, reviewer separate from author, negative controls, failure preservation, source+runtime+resource end-to-end checks and contradictions adjudicated | Scoped QA already PASS for A/B/C/BC, **not** for future real protocol |
| R8: owner GO/HOLD and explicit scope | REQUIRED | REQUIRED | One integrated, signed owner decision for exact study/run/budget/files/rights and no TEST reselection; default HOLD | NOT_GRANTED |

**Định nghĩa:** `PASS` của hàng R* trong tương lai cần **tất cả** điều kiện cần cho đúng phương án nghiên cứu; không lấy một giấy phép nhỏ cho mỗi tệp và không dùng `design-only` như permit. Gate tổng hợp: `RELEASE_READY = AND(R0..R8 applicable)` trên một exact release candidate. Khi chưa đầy đủ thì `HOLD`, không ước lượng GO. Không tự sửa preflight để đạt PASS; kế hoạch sửa phải qua source QA khác, không ghi đè lịch sử.

## V. Phân biệt kết quả khoa học và ý nghĩa phát hành

- A I1 là **validity của measurement**, không phải cải thiện khả năng của mô hình; I2 chưa được chạy.
- B M3 là **synthetic GPT Core engineering**; CI/owner-native có phạm vi và V3 memory peak dissent còn nguyên. Không suy ra model T4 đã huấn luyện thành công bằng B.
- C M4 là **validity của hợp đồng thiết kế synthetic**, không xác nhận dữ liệu thật, rubric theo gold thật, fairness equal-compute hoặc khả năng đạt instruction following.
- BC v2 là **giao diện đánh nhãn/bytes/mask chính xác**, không có optimizer step, không có SFT weights; checkpoint schema chỉ là metadata. Giá trị loss ~7.64458 trong P02 mock chỉ chứng minh đường forward/backward, không phải hiệu quả SFT.
- Dữ liệu/nghiên cứu khoa học TTM trước đó trong main lineage (T4 science, TEST64 tiêu thụ, các negative) vẫn giữ đúng trạng thái lịch sử. `NO_NEW_SCIENCE_THIS_OPERATION` không có nghĩa repository chưa từng nghiên cứu khoa học.

## VI. Xử lý metadata stale và trách nhiệm; không thực hiện trong lượt này

- B PR #34 `docs/coordination/ttm-abc/status/TTM_TRACK_B_STATUS.json` vẫn là ảnh chụp `HANDOFF_READY_AGENT_NOT_STARTED`, **không** phải trạng thái PM mới nhất. Sử dụng phán quyết B-M3 tại independent review exact commit, không âm thầm ghi đè status của B.
- C PR #35 `docs/coordination/ttm-abc/status/TTM_TRACK_C_STATUS.json` vẫn ghi BC5 HOLD từ trước review PM cuối, còn PR #36 title cũng ghi HOLD. Đây là **metadata cần đồng bộ prospective**, không làm mất hiệu lực quyết định scoped PM trên review SHA; chỉ cập nhật khi có nhiệm vụ tài liệu được duyệt và source pins không đổi.
- Evidence review commit tồn tại trên các nhánh độc lập, không có nghĩa file đó hiện nằm ở `main`. Lượt này chỉ tạo tài liệu governance trên nhánh khác tách từ main.
- Không tự trộn PR #33 vào main khi PR #28 chưa qua merge review; không tự merge PR #36 khi PR #34 chưa được xét. PR #35 có thể được thẩm định riêng về doc/design, nhưng không có owner merge permit.

## VII. Kết luận và bước kế nhiệm duy nhất

**PM closure:** `PASS_SCOPED_ABC_ENGINEERING_AND_DESIGN_INVENTORY` · `HOLD_ALL_PROSPECTIVE_RELEASES`.

**Bước thực hiện tiếp theo — duy nhất (chỉ lập gói quyết định, không cấp GO):**

`TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE`

Soạn **một** owner decision packet xem xét hai luồng A I2 và C M6 theo R0–R8, đồng thời xét merge dependency graph riêng. Nếu bất kỳ blocker nào thiếu evidence, giữ HOLD, không chạy bổ sung bằng cách mở các micro-permit; mọi science/merge cần một quyết định owner rõ ràng sau review. Không cần sửa các kỹ thuật đã PASS trong lượt hiện tại.

**Bất biến:** `A_I1_PASS · A_I2_HOLD · B_M3_PASS_SCOPED_WITH_DISSENT · C_M4_PASS_DESIGN · BC_INTERFACE_PASS_ENGINEERING_SCOPED · SCIENCE_NOT_EXECUTED_THIS_GATE · NO_MERGE · LINEAGE_MD_UNCHANGED`.

## VIII. Evidence anchors (immutable)

- A: [PR33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) · [I1 report](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md) · [A status](https://github.com/minhtri22/TokenToModel-Lab/blob/771314c07ba061ebeb1baa87018248ed73181079/docs/coordination/ttm-abc/status/TTM_TRACK_A_STATUS.json).
- B: [PR34](https://github.com/minhtri22/TokenToModel-Lab/pull/34) · [M3 original gate reconciliation](https://github.com/minhtri22/TokenToModel-Lab/blob/fdffbf2cc3c517d25dddae89501c091c58f2608d/docs/research/ttm-abc/track-b/independent_review/B_G5_G6_V3_FULL_RECEIPT_INTEGRATED_PM_ADJUDICATION_20261116.md).
- C: [PR35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) · [M4 independent 35/35](https://github.com/minhtri22/TokenToModel-Lab/blob/9fac5a675955d8b91d6855d27907f239cbfb745f/docs/research/ttm-abc/track-c/independent_review/C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_20261116.md).
- B/C: [PR36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) · [PM final QA](https://github.com/minhtri22/TokenToModel-Lab/blob/82aaf2a881bd677afd8f6e600eb570aea897fdba/docs/research/ttm-abc/bc-sft/independent_review/BC_V2_F05_F06_PM_FINAL_DISTINCT_ENGINEERING_ADJUDICATION_20261117.md) · [distinct CI](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43937370201).
- Main lineage: [lineage.md at main exact HEAD](https://github.com/minhtri22/TokenToModel-Lab/blob/f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3/lineage.md).
