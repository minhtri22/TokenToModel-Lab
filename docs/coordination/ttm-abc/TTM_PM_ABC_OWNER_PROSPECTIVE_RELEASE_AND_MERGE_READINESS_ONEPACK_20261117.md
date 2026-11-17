# PM / Owner OnePack — ABC prospective release readiness và exact merge dependency

**Operation:** `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE`  
**Ngày:** 2026-11-17 (Asia/Bangkok) · **Chế độ:** `EXACT_GITHUB_READBACK · DESIGN_ONLY · NO_NEW_SCIENCE · NO_MODEL_RUN · NO_MERGE`  
**Kho sự thật:** `minhtri22/TokenToModel-Lab`; snapshot `main=f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`.  
**Thẩm quyền:** PM lập kế hoạch/đề xuất; owner chưa đưa ra chữ ký/GO cho I2 hoặc SFT hoặc merge trong lượt này. Không được tự suy ra chữ ký owner từ một bình luận GitHub.

## 1. Quyết định duy nhất của lượt PM

**`PASS_OWNER_READINESS_DECISION_PACKET_DESIGN_SCOPED`** — đủ tài liệu để owner thấy chính xác bằng chứng đã đạt, chứng cứ thiếu và lựa chọn cần phân xử.

**Khuyến nghị về thực thi ngay:** `A_I2=HOLD_RELEASE` · `REAL_SFT=HOLD_RELEASE` · `MERGE=HOLD_OWNER_AUTHORIZATION` · `OWNER_GO=NOT_GRANTED`.

Quyết định này **không** đổi `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` (PM trước đó đã PASS), A I1 measurement `CLOSED_PASS_SCOPED`, A V4 `DESIGN_ACCEPT_SCOPED`, B M3 scoped PASS kèm V3 native HOLD/dissent, C M4 design PASS, B/C v2 engineering PASS. Những trạng thái PASS đó **không chuyển** thành quyền chạy thật.

**Định nghĩa cổng:** release execution của mỗi lane chỉ có thể được owner cân nhắc khi **các R0–R8 áp dụng cho chính lane đó** được độc lập chứng minh trên một exact candidate và một phạm vi run hữu hạn. **Không có chín micro-permits.** Chỉ một hồ sơ A-I2 và một hồ sơ real-SFT, gắn những chứng cứ đã khóa; một lần phân xử owner tổng hợp về từng lựa chọn sau khi có đủ bằng chứng, thay vì từng file một. Việc merge là **quyết định riêng**; một science HOLD không có nghĩa docs-only tuyệt đối không được xét merge, và một merge PASS không có nghĩa science GO.

## 2. Nguồn bất biến đã đối chiếu

| Nhóm | Source/evidence exact SHA | Nghĩa đã chứng minh |
|---|---|---|
| PM shared charter | [commit `403491b698ba6586193f2ff2ae00c4441c10c595`](https://github.com/minhtri22/TokenToModel-Lab/commit/403491b698ba6586193f2ff2ae00c4441c10c595), blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` | Namespaces, A/C/B owner, agreement anti-drift |
| A I1 executable source | `ec197b5f00d3a037420390edd11ee55047e1d37f`; [I1 review `e3e1c802...`](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md) | Scorer/fixture correctness 35/35 distinct + native custody 38/38, 80/80, 5/5; **no I2** |
| A V4 accepted design | `e6746184603f038b49d1e7d472367b6354474ba2`; A packet **PR33** `7639a53b9d76e16abfa4211cf239c5c3e9d6c940`, A requirements blob `3de320f1e734c7610fb750477803b082fefff753` | Signed epoch/dual SHA/one-shot design accepted; 65 negatives/3 positives **planned, not executed** |
| B M3 | [PR34](https://github.com/minhtri22/TokenToModel-Lab/pull/34) `43896bcd034c82e8433bc6a2b53eefbd936616fb`; [B G5/G6 PM review](https://github.com/minhtri22/TokenToModel-Lab/blob/fdffbf2cc3c517d25dddae89501c091c58f2608d/docs/research/ttm-abc/track-b/independent_review/B_G5_G6_V3_FULL_RECEIPT_INTEGRATED_PM_ADJUDICATION_20261116.md) | Synthetic GPT Core engineering scoped PASS; immutable V3 native negative `HOLD_NATIVE_QA`, `HOLD_PEAK_ACCOUNTING` dissent |
| C M4/prospective protocol | [PR35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) `4efe93ce0a3910c449972b3f7e9911a004fe2b3c`, corrected registry blob `364a15d305b71e0c236a27409430f1e27e14aa70` | C design & F01/F02/F03 source agreement, **not** real data/gold/weights admission |
| B/C v2 | [PR36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) `09de6a46574146d863f416e056fcf01091f3efb8`, tested B code `a83e1526bce842761f3051dad28b90a55395a6aa`; [PM review](https://github.com/minhtri22/TokenToModel-Lab/blob/82aaf2a881bd677afd8f6e600eb570aea897fdba/docs/research/ttm-abc/bc-sft/independent_review/BC_V2_F05_F06_PM_FINAL_DISTINCT_ENGINEERING_ADJUDICATION_20261117.md) | Synthetic CPU interface v2 engineering PASS, no SFT optimizer/real model weights |
| B A/C feasibility | [PR37](https://github.com/minhtri22/TokenToModel-Lab/pull/37) `ff4304e04f44de69a07cd767b2a7f400d6e95e88`; machine remap blob `c2d4a050f35218de2c023d3a5c50fb3454404c23` | 37 A/26 C/14 B-facing rows, 63 distinct fields, direct T4→BC tokenizer `INCOMPATIBLE` |
| PM ABC final design alignment | [Final PM report `fa28b89e...`](https://github.com/minhtri22/TokenToModel-Lab/blob/fa28b89e4ee93b3de4561deaa2a7b9a086fa340b/docs/coordination/ttm-abc/TTM_PM_ABC_CCR01_F01_F03_FINAL_DISTINCT_EXACT_SOURCE_ADJUDICATION_20261117.md) and [Issue #32 decision](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6939252896) | `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`, **not** release approval |

GitHub PR metadata và changed-file inventory vừa đọc lại từ exact HEAD. Mọi PR #28/#33/#34/#35/#36/#37 hiện **Draft/Open/unmerged**. GitHub `mergeable=true` chỉ nói đến phép kiểm so sánh **với base riêng của PR**, không phải review/owner permission hay integration QA của toàn bộ cây. Các nhãn title/status JSON có thể cũ hơn PM adjudication (PR #28 title HOLD I1, PR #35 title PM HOLD, PR #36 title BC5 HOLD; một số A/C status snapshot cũng lịch sử). Quyết định có thẩm quyền phải dựa **exact source + distinct verdict với phạm vi**, không dựa title.

## 3. Cây phụ thuộc và ma trận merge

```text
main f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3
├── PR #28 ebdc54575eed1ff60c402eecf60289f408bb38ca   [A parent; HOLD source/admission history]
│   └── PR #33 7639a53b9d76e16abfa4211cf239c5c3e9d6c940 [A I1 measurement PASS + V4 design]
├── PR #34 43896bcd034c82e8433bc6a2b53eefbd936616fb   [B synthetic engineering PASS w/ dissent]
│   └── PR #36 09de6a46574146d863f416e056fcf01091f3efb8 [BC v2 synthetic engineering PASS]
│       └── PR #37 ff4304e04f44de69a07cd767b2a7f400d6e95e88 [B prospective docs mapping PASS]
└── PR #35 4efe93ce0a3910c449972b3f7e9911a004fe2b3c [C separate design/source tests]
```

**Bằng chứng base (GitHub metadata):** #28/base=main; #33/base nhánh HEAD #28; #34/base=main; #36/base nhánh HEAD #34; #37/base nhánh HEAD #36; #35/base=main. **Đây là thứ tự phụ thuộc Git, không phải lệnh merge**.

| PR / phần | Exact HEAD | Source phạm vi | PM review merge eligibility *hiện tại* |
|---|---|---|---|
| #28 | `ebdc5457...` | Q001 pre-exec/guard/native candidate, 63 đường dẫn thay đổi | **`HOLD_SEPARATE_BOUNDARY_AUDIT`**: parent có trạng thái native/owner HOLD lịch sử; không mang cả nhánh vào main dựa trên I1 PASS của PR con |
| #33 (trên #28) | `7639a53b...` | I1 scorer/source QA + V4 thiết kế, 49 đường dẫn riêng trong delta so với #28 | **`REVIEW_CANDIDATE_NOT_MERGE_AUTHORIZED`**: muốn merge code I1 phải kiểm phạm vi và thực thi của parent; có thể đề xuất clean PASS-only extraction mới sau independent QA, **chưa thực hiện** |
| #34 | `43896bcd...` | 11 đường dẫn B Core/CI/test/doc | **`REVIEW_CANDIDATE_WITH_V3_DISSENT`**: scoped M3 PASS nhưng V3 native receipt FAIL vẫn nguyên, kiểm exact main/integration QA trước khi đề nghị merge |
| #36 (trên #34) | `09de6a46...` | 27 đường dẫn BC bridge/CI/tests/actual byte bundle | **`REVIEW_CANDIDATE_DEPENDS_PR34`**: F01–F06/BC5 PASS engineering scoped, không cho phép giả định real-T4 codec |
| #37 (trên #36) | `ff4304e0...` | 8 đường dẫn docs/evidence (mới so với #36) | **`DESIGN_DOCS_REVIEW_CANDIDATE_DEPENDS_PR36`**: các status source scoped không là release permit |
| #35 | `4efe93ce...` | 30 đường dẫn C design, tests và CI | **`INDEPENDENT_DESIGN_REVIEW_CANDIDATE`**: có thể xét độc lập trên base main sau source/security/QA, không xem là science GO |

**Kiểm tra trùng đường dẫn (filename-level, không phải semantic/runtime merge QA):**
- PR #28 vs PR #33 có **2 file cùng đường dẫn** đã sửa trong cùng chuỗi A: `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/independent_negative_qa_v3.py` và `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py`. Điều này đòi kiểm version và QA khi xây merged tree; **không** được cherry-pick tùy ý code của parent.
- Các cặp thay đổi được đối chiếu giữa nhánh A và nhánh B/C/C, giữa C và B/BC/B37, cũng như #34↔#36 và #36↔#37 tại các delta PR riêng đều có **0 trùng tên file**. Không có xung đột path trực tiếp trong các cặp đã kiểm **không chứng minh** API/CI, bản quyền, science hoặc mọi merge sequence an toàn.
- Source change counts cho snapshot: #28=63, #33 vs #28=49, #34=11, #36 vs #34=27, #37 vs #36=8, #35=30. Chưa chạy phép merge hoặc CI trên merged tree.

**Phương án thứ tự trong tương lai, CHỈ KHI owner cấp quyền và QA lại exact merged tree:** chuỗi A `#28 → #33` (hoặc một PR clean-scoped độc lập đã review nếu #28 vẫn HOLD); chuỗi B `#34 → #36 → #37`; PR #35 độc lập theo phụ thuộc Git nhưng phải rà soát tests/workflow CI. Mỗi bước thay đổi base có thể làm changed-file diff, pin và kiểm thử không còn tương đương; cần khóa exact source tiếp, không viện dẫn nguyên vẹn `mergeable=true`. Chỉ merge **những artifact đạt gate đúng phạm vi**, ghi trên lineage cả HOLD/FAIL bằng đường dẫn nguồn; không merge mã từ nhánh HOLD chỉ để đơn giản hoá cây.

## 4. Ma trận R0–R8 cho hai lựa chọn owner — chính xác điều kiện còn thiếu

| Gate | Lựa chọn A-I2 Q001 (one-shot đã khóa) | Lựa chọn real SFT / Data×Compute (prospective) | Status PM |
|---|---|---|---|
| **R0 — Exact code/graph** | I1 source `ec197...` PASS; PR28→33 có dependency và release guard cũ chưa chấp nhận phán quyết I1 mới | ABC logical contract PASS; PR34→36→37 + PR35 chưa tích hợp thành exact real-study runner | `PASS_DESIGN_SOURCE_ONLY / HOLD_FINAL_EXECUTABLE_SOURCE` |
| **R1 — Metric/gold** | M0 v3 gold-blind I1 PASS cho 80 fixture/5 nhóm; **chưa có I2 real checkpoint scores**; phải sử dụng predeclared Q001 estimand/stop, không biến fixture thành phát hiện năng lực | Endpoint C `val_bpb` định nghĩa đúng nhưng source/gold/rater chưa qualified; stop CE tách riêng; no partial BPE byte loss | `A_I1_PASS_SCOPED / C_GOLD_HOLD` |
| **R2 — Rights/splits** | Cần nối nguồn I2/Q001 và quyền sử dụng (nếu áp dụng) vào exact source/freeze manifest và bảo đảm TEST hiện có không bị mở lại; không bắt người dùng cấp lẻ từng file | Real TinyStories/other source bytes/license/allowed action, rights/PII/copyright, family-disjoint TRAIN/VAL/fresh TEST, TRAIN-only tokenizer, near-dup + contamination evidence chưa cung cấp | `HOLD_PROSPECTIVE_SOURCE_ADMISSION` |
| **R3 — Model/tokenizer/checkpoint** | A có historical source/bpe/fixture SHA và tiền kiểm custody riêng; cần exact I2 model/checkpoint/optimizer-step/config/tokenizer-on-run readback cho một candidate và proof no wrong alias | **Hard `INCOMPATIBLE`** nếu dùng trực tiếp BC/v2 pack với T4 BPE; historical T4 real weight SHA/read-only strict load chưa có; sidecar byte-span+role option design-only, no assistant EOT from metadata | `HOLD_EXACT_RUNTIME_BINDING / HOLD_SFT_CODEC` |
| **R4 — Native resource** | Bounded Windows owner host, Job Object memory, watchdog full process tree, time/disk/child cleanup và target one-shot negative on exact I2 runner; không mượn synthetic B M3 PASS | Target T4 GPU/CPU, actual batch/context/precision, FLOPs, VRAM/RAM hard caps, data IO/eval/checkpoint overhead và stop guard cần đo; **74s/1024, 13min/44M** chưa có original raw receipt cho GO | `HOLD_NEW_NATIVE_AND_GPU_EVIDENCE` |
| **R5 — Owner authority/atomic evidence** | **Critical:** historical owner-internal preflight exit2 `HOLD_OWNER_INTERNAL_I1_NOT_PASS`; V4 signed ReleaseTBS/policy_epoch, dual RAW/TAG, frozen global `H_SLOT_V3` là design; trusted Ed25519 roles, native parent-handle/no-replace, W1/W2 race, crash/ledger and antirollback chưa executed | Cần evidence append-only/checkpoint READY-last/FS constraints cho new SFT runner; **không tự chuyển** I2-specific signed Q001 slot/TBS sang SFT; BC v2 `verify_bundle()` path symlink ≠ untrusted reparse/TOCTOU proof | `A_V4_DESIGN_ACCEPT_SCOPED / HOLD_NATIVE_OWNER_AUTHORITY` |
| **R6 — Prereg/fairness** | Đối chiếu original frozen Q001 hypothesis/endpoint/fresh TEST reader=0, one-shot identity and whether existing prereg applies unchanged; **không tự tạo mới Q001** | Khóa riêng future primary bpb, research question, arm, seed, family sample size, paired equal *measured* FLOPs, thresholds/CI/stopping before new outputs; 44M chỉ planning hypothesis | `HOLD_PROSPECTIVE_FROZEN_CANDIDATE` |
| **R7 — Independent exact candidate QA** | I1 distinct QA 35/35 và Windows custody 38/38 đã PASS; V4 65 negative + 3 positive = **0 executed**, missing native races/signer/one-shot end-to-end proof | B/C v2 Windows/Linux synthetic QA already PASS, nhưng actual T4 checkpoint+token byte span/real source/native host independent candidate QA = **NOT_EXECUTED** | `HOLD_NEW_EXACT_RUNTIME_INDEPENDENT_QA` |
| **R8 — One owner GO/HOLD** | Owner chưa cấp exact signed one-shot release, không nonce/dispatch | Owner chưa cấp exact study scope/data/compute/GPU budget/rights/run GO | **`HOLD_OWNER_GO_NOT_GRANTED`** |

**Lưu ý:** B native V3 trong lịch sử có FAIL của test memory-negative/peak accounting, dù PM đã phân xử B-M3 synthetic engineering PASS đúng phạm vi. Không được dùng V3 như bằng chứng hard-cap PASS cho các runner I2/SFT thật. `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` không xóa `INCOMPATIBLE_DIRECT_T4_BC`.

## 5. Hai tập chứng cứ tối thiểu — tránh micro-permits

### Lane A — `A_I2_EXACT_RELEASE_WITNESS_PACKET` (chưa tồn tại đầy đủ)

Một gói duy nhất cần chứa: exact I2 executable source/parent dependency, original Q001 prereg/frozen 80-case identity & source/rights, real checkpoint+tokenizer bytes/sha binding, resource bounds trên owner host, V4 trusted signer/principal/policy epoch+antirollback, native ancestor-handle/no-replace ledger/writer crash+reboot negative QA, evidence READY-last/raw+tag final readback, distinct exact-candidate QA và một quyết định owner có scope/expiry/budget/H_SLOT_V3; không đăng ký science SLOT mới. Nếu bất cứ mục nào thiếu hoặc FAIL, **one-shot I2 vẫn HOLD**. Đây là đề xuất **gói witness** chứ không phải yêu cầu xin phép từng thành phần.

### Lane SFT — `C_B_REAL_SFT_SCIENCE_WITNESS_PACKET` (chưa tồn tại đầy đủ)

Một gói duy nhất cần chứa: exact real source/license/rights+family splits/heldout SHA, pretrained original weight+training tokenizer+optimizer config/strict load evidence, versioned solution to T4 BPE-vs-BC-v2 special ID collision (hoặc một checkpoint/tokenizer lineage mới), full coverage raw UTF-8 byte offsets + no-cross-boundary mask for byte bpb, C-approved gold/endpoints/stop CE controls, frozen equal-measured-compute prereg and checkpoint selection, bounded GPU/host native budget, reproducible immutable receipt, independent source/native QA, exact owner GO for **new scope**. Không thể dùng manifest `weights=NOT_CREATED` của BC v2 để thay thế real checkpoint. Nếu thiếu thì **SFT HOLD**.

**Ưu tiên hiện tại không phải chạy benchmark hoặc tìm thêm một QA nhỏ:** làm rõ/hợp nhất hai gói witness trên kho source người sở hữu đang có, nhưng không sửa mã hoặc chạy bất cứ kiểm thử native/science nào trong lượt review này. Nếu tài sản nguồn không nằm trong repository, đánh dấu `OWNER_PRIVATE_CUSTODY_UNVERIFIED` và cho phép owner cung cấp **một** gói bằng chứng riêng khi muốn xét science, không suy diễn missing là rights-invalid.

## 6. Merge decision tách biệt với science decision

- **Không merge bất cứ PR nào trong lượt này.** `mergeable=true` không đủ. Chưa kiểm tra branch protections/rulesets, final combined CI, independent merged-tree QA hay owner merge authorization.
- **Không gộp nguyên cây FAIL/HOLD:** PR #28 vẫn có owner/native pre-exec HOLD; I1 đã CLOSED ở #33 không làm cha PASS mọi phương diện. Nếu owner chỉ muốn tài liệu và scorer I1 đã QA, xem xét tạo một **clean-scope review candidate** sau khi thiết kế diff và độc lập QA, không cherry-pick tự động.
- **Không buộc design merge phải đợi science GO:** C #35 và B #37 có thể là **ứng viên xem xét** doc/design/test theo QA riêng, nhưng chưa phải PASS merge; B #37 vẫn phụ thuộc parent B/C nếu merge nguyên branch. PM nên phân loại docs-only vs code/CI and exact scope before proposal.
- **Lineage append-only:** main `lineage.md` Git blob `3409e036241deb1da6674619a2abc834bea8a2d6` có L0000–L0029. Trước đó đã có đề xuất năm ứng viên ABC trong [governance snapshot](https://github.com/minhtri22/TokenToModel-Lab/blob/c4c8cccaa0bde34a5e93024c7c4e12be2d60a582/docs/coordination/ttm-abc/TTM_PM_ABC_LINEAGE_APPEND_CANDIDATES_20261117.md); không cấp số L tiếp theo nếu chưa đọc tail mới trong lượt append. Ghi nhận lịch sử PASS/HOLD/FAIL với exact branch refs ngay cả khi nhánh chưa merge. `lineage.md` **không bị thay đổi** trong lượt này.

## 7. Owner decision card — **đề xuất**, không phải owner đã ký

| Quyết định owner tương lai | Tùy chọn hợp lệ sau evidence | Trạng thái tại snapshot này |
|---|---|---|
| `A_I2_OWNER_DECISION` | `GO_EXACT_ONE_SHOT` hoặc `HOLD`, trỏ signed release+global slot và exact runnable/checkpoint/dataset/budget | **`HOLD_RECOMMENDED`** |
| `REAL_SFT_OWNER_DECISION` | `GO_EXACT_PROSPECTIVE_RUN` hoặc `HOLD`, trỏ independently checked data/weights/byte masks/host budget | **`HOLD_RECOMMENDED`** |
| `PR_MERGE_OWNER_DECISION` | `ALLOW_SCOPED_MERGE_SET` kèm thứ tự exact SHA và merged-tree QA hoặc `HOLD` | **`HOLD_RECOMMENDED`** |

*Không có owner GO/permission trong tài liệu này. Khi chọn GO sau này phải có nguồn/địa chỉ và quyền ký thực, không coi bình luận assistant hay GitHub account là chữ ký Ed25519 người sở hữu.* Một câu quyết định đồng thời có thể chọn A-I2 HOLD / SFT HOLD / merge docs-only theo scope nếu đã có nguồn đủ, nhưng không suy theo phạm vi khác.

## 8. Formal PM closure và next step duy nhất

**Gate của operation:** `PASS_OWNER_READINESS_DECISION_PACKET_DESIGN_SCOPED` vì đã khóa và đối chiếu dependency, chứng cứ hiện có, gap R0–R8, đường GO/HOLD future, rõ trách nhiệm và phạm vi. **Trạng thái của hai science lanes:** `A_I2_HOLD · REAL_SFT_HOLD`. **Merge:** `HOLD_MERGE_AUTHORIZATION`.

**Bước tiếp theo — duy nhất, không mở micro-permit:** `TTM_PM_ABC_OWNER_SINGLE_INTEGRATED_RELEASE_AND_MERGE_DECISION_PACKET_ADJUDICATION_GATE`. Owner xem xét cùng một packet, có thể giữ HOLD cả ba lựa chọn khi source thiếu; chỉ khi exact witness và independent QA đủ mới cân nhắc phạm vi GO/merge. Không tự bắt đầu run hoặc xây thêm ticket chỉ để bù từng field.

**Bất biến:** `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED · A_I1_CLOSED_PASS · A_V4_DESIGN_ACCEPTED · B_M3_PASS_SCOPED_WITH_DISSENT · C_M4_PASS_DESIGN · BC_V2_PASS_ENGINEERING · A_I2_HOLD · REAL_SFT_HOLD · OWNER_GO_NOT_GRANTED · NO_NEW_SCIENCE · NO_MERGE · MAIN_UNCHANGED · LINEAGE_UNCHANGED`.
