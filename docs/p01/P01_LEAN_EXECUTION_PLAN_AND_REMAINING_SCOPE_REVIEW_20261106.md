# P01 — Rà soát phần còn lại và kế hoạch thực hiện tinh gọn (Lean Execution)

**Mã công việc:** `TTM_P01_LEAN_EXECUTION_PLAN_AND_REMAINING_SCOPE_REVIEW`  
**Ngày:** 06/11/2026. **Kho:** `https://github.com/minhtri22/TokenToModel-Lab`.  
**Phạm vi:** tài liệu rà soát và kế hoạch; **không** sửa nguồn đã khóa, không chạy test, không cấp quyền dữ liệu hay huấn luyện.  
**Nguồn đối chiếu:**
- `main=92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`;
- `implementation/p01-i0a-s-f0-static-20261106=b793191932d794e53d88e275a45bad571750a9c3`;
- `design/p01-tokenizer-data-prereg-20261105=4048e029cc12cc7edcac5c8a3d59c4793334407d` **trước** khi bổ sung biên bản này, PR #4 Draft;
- `docs/PHASE_PLAN.md`, `docs/TRAINING_PROTOCOL.md`, `docs/p01/P01_DESIGN_PREREGISTRATION.md`, `P01_METRICS_AND_QA_GATES.md`, `P01_D1_H01_DETERMINISTIC_BPE_SPEC.md`, `P01_D1_H03_DEDUP_SPLIT_SPEC.md`, `P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md`, và các biên bản F0/C09 ngày 06/11.

## I. Nguyên tắc không thay đổi

Giữ nguyên **P00 → P01 → P02 → P03 → P04 → P05 ... P12**: P02 hoàn thiện Transformer Core; **P03** mới hoàn thiện và chạy Training Loop mô hình GPT; **P04** làm Evaluation, Checkpoint, Held-out. P01 chỉ học/đo **tokenizer B1** trên TRAIN được cho phép sau cổng E0, **không huấn luyện GPT**. Không đổi kiến trúc P00, cấu hình `vocab_size=256` hay hợp đồng B0/B1; B1 token ID ≥256 **không** được đưa vào P00. Không sửa các giá trị khoa học đã khóa, không nhìn TEST trước quyết định đánh giá, giữ PASS/FAIL/INCONCLUSIVE. `lineage.md` append-only cho **kết quả khoa học**; không thêm nhật ký sửa code, lỗi hạ tầng hoặc QA kỹ thuật.

**Chủ trương tinh gọn:** hợp nhất các thao tác thường nhật thành **một chu kỳ ba bước cho mỗi gói công việc**. Không tách kiểm SHA, AST, Git status, đọc log, QA tĩnh thành nhiều lượt xin phép khi cùng phạm vi và không đổi mã. Riêng **dữ liệu chưa có quyền, thực nghiệm E0, runtime bảo mật Windows/nguồn đặc quyền và xóa/merge** vẫn giữ quyết định riêng đúng ngưỡng rủi ro.

## II. Hiện trạng xác minh, phân biệt mức chứng cứ

| Hạng mục P01 | Mức chứng cứ | Kết luận |
|---|---|---|
| H01 B0 byte 0..255, Unicode strict, invalid IDs | `qa/p01/qa0_f0_smoke_test.py`, biên bản `P01_QA0_F0_OFFHOST_EXPLICIT_RERUN_PASS_20261106.md` ghi 10/10 trong offhost Linux | **PASS F0 chức năng**, không phải Windows QA0 |
| H01 B1 merges M01, serial binary/independent golden | 10/10 F0 gồm S05–S06; `src/p01/byte_bpe.py` và independent checker | **PASS đúng fixture M01**; chưa chứng minh 2 process + TRAIN có phép |
| H03 canonicalization, near duplicate, union-find | `src/p01/data_dedup_split.py`; S07–S08 kiểm invalid document và F02/F03 group | **Mã có, QA một phần**; chưa đủ oracle transitivity/ranh giới 0.85/0.8 và 30+ nhóm |
| H03 80/10/10 group split, zero leakage | Có hàm `assign_splits`, seed và hợp đồng; S08 chỉ xác nhận từ chối dưới 30 nhóm | **CHƯA có kết quả kiểm định tích hợp 30+ nhóm**; chưa có report group/raw/canonical cross-split 0 |
| H02 nguồn/giấy phép/PII | `P01_DATA_AND_SPLIT_PLAN.md`, `P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md`; `source_scope_guard` chỉ giới hạn F0 | **HOLD F1/F2**: chưa thấy danh mục `ALLOW` có bằng chứng quyền sử dụng; không suy đoán có/không dữ liệu ở máy ngoài GitHub |
| B1 học TRAIN, two-process reproducibility | Hàm F0 chỉ chấp nhận 12 hash F0 và M01, không phải pipeline ingest F1 | **Chưa có đường nạp F1 được duyệt**, chưa chạy B1 trên TRAIN |
| H05 Windows Job Object | `windows_job_guard.py` đã có Win32 ctypes/memory-limit/attach primitives nhưng `start_worker` vẫn từ chối | **PARTIAL CODE_ONLY**; thiếu restricted launcher, attestation, watchdog và thử âm tính kernel |
| H05 Write Broker | `write_quota_broker.py` kiểm path/quota trên bộ đếm mô phỏng; `write_file` vẫn từ chối | **DRY_RUN_ONLY**; chưa có broker chống reparse, create-new nguyên tử, ACL, account/quota thực |
| C09 negative QA | 12 `unittest` policy/mock đã viết tại `qa/p01/independent_windows_guard_policy_negative.py` | **PREPARED_NOT_EXECUTED** theo báo cáo; không phải 12 Windows W01–W12 |
| Evidence/JCS | `runtime/p01/evidence_manifest.py` mới là subset serializer, từ chối runtime receipt | **Chưa hoàn chỉnh** provenance, manifest/runtime readback, độc lập đối chiếu SHA |
| B0/B1 token/byte, compression, runtime usage | Có hợp đồng đo trong `P01_METRICS_AND_QA_GATES.md` | **CHƯA đo** trên tập được duyệt |
| Git/main/P00 | `main=92facee15...`, P01 branch riêng, PR #4 vẫn Draft | **Bảo toàn**, không tự merge hay dọn |

**Không đồng nhất:** `F0_10_OF_10_PASS` với `P01_CLOSE=PASS`; `C09_GITHUB_STATIC_REVIEW=PASS` với `WINDOWS_W01_W12=PASS`; tài liệu D0/D1 ghi trạng thái `DESIGN_ONLY` là ảnh chụp lịch sử, **không phải** phủ định các commit triển khai F0 sau đó. Biên bản F0 offhost là QA kỹ thuật, không chứng minh network/OS guard Windows. Theo báo cáo C09, worktree Windows chưa chắc đã đồng bộ tới `b7931919...`; không đoán trạng thái hiện tại từ GitHub.

## III. Quy trình ba bước cho mỗi gói công việc

**Bước A — Tiền kiểm gộp (Preflight, một lần):** kiểm exact repo/origin/branch/HEAD, trạng thái Git sạch, ranh giới đường dẫn, SHA bộ đầu vào, Python và mức RAM/đĩa hiện hữu; xác nhận fixture/nguồn đã được duyệt và tiêu chí PASS/FAIL. Nếu chưa thay môi trường hay phạm vi, **tái sử dụng bằng chứng còn hiệu lực**; không lập ba giấy phép khác nhau cho một AST, một SHA và một lần đọc log.

**Bước B — Triển khai + chạy gộp (Implementation & Execution):** một commit nguồn scoped, một batch test đủ phủ tiêu chí, giới hạn tài nguyên và chống lặp ngoài ý muốn; lưu log, hash, negative cases. Đối với fixture nhỏ F0, test thuần logic được chạy trong môi trường phù hợp, không được ghi là chứng nhận OS guard. Đối với E0 trên F1 được phép, run/seed/split/dataset/hash bắt buộc khóa trước khi tiêu thụ dữ liệu.

**Bước C — QA độc lập + phán quyết (Independent QA & Adjudication, một lượt):** checker độc lập kiểm output, nguồn, cross-split collisions, SHA, mức phủ và kết quả. Một biên bản cuối `PASS/FAIL/INCONCLUSIVE/HOLD`, ghi cả thất bại, quyết định chuyển tiếp. Không tách nhiều lượt chấp thuận khi đủ bằng chứng cùng phạm vi.

**Ngoại lệ không tinh giản:** quyền dữ liệu/PII, ranh giới bảo mật Windows thực, khoa học E0/TEST one-shot, thay kiến trúc hoặc dữ liệu, merge và cleanup riêng. Không dùng chỉ `python -I -S -B` hay chuỗi admission làm OS sandbox.

## IV. Ba gói để hoàn thành P01

### L1 — QA tích hợp thuần F0; hoàn thiện độ phủ không đụng corpus

**Mục đích:** hoàn thành phần B0/B1 thuần kỹ thuật, không chạy lại S01–S10 đã PASS. Tập trung vào những trường hợp chưa được chứng minh:
- Bổ sung checker cho B1 serialize/deserialize, tie-break, overlap, boundary tài liệu; kiểm tra trật tự đầu vào cho kết quả ổn định.
- Kiểm tra H03 trùng tuyệt đối/canonical/near-duplicate, transitivity và các ngưỡng phân loại đã khóa. Gán 30+ **nhóm ID tổng hợp** để kiểm split và zero cross-split collisions. Nếu cần full pipeline 30+ synthetic documents, tạo **tuyến QA-fixture riêng** được review; **không** lén nới `F0_LITERAL_SHA256` hoặc giả lập F1 là dữ liệu đã có quyền.
- Kiểm tính đúng hợp đồng tương thích P00: B0 0..255, dài >64 báo lỗi ở ranh giới model; B1 >=256 không nạp trực tiếp embedding 256. Không sửa P00.
- Nhóm C01–C08/C10 theo phạm vi áp dụng, thay cho nhiều round nhỏ; đọc lại kết quả chỉ **một** lượt QA độc lập.
- Chạy 12 pure policy/mock test của C09 một lần khi chốt mã mới, **không** báo chúng là W01–W12.

**PASS L1 nếu:** byte identity/roundtrip chính xác, golden oracle và independent checker khớp, các kiểm thử âm tính từ chối, F0 split 30+ groups tất định và 0 overlap trên dữ liệu tổng hợp, không có nguồn ngoài phạm vi hoặc mã P00 bị thay. **PASS L1 không cấp quyền E0.**

### L2 — Đóng điều kiện nguồn dữ liệu, runtime E0 tối thiểu an toàn

**Mục đích:** chuẩn bị đường F1 có quyền và giới hạn tiến trình thực, không tải/tự chọn corpus.
- Cần **ít nhất một snapshot F1 do chủ dự án xác nhận quyền**: source manifest `source_id/license_id/permitted_uses/PII/source_sha256`, số tài liệu, số nhóm, nguồn gốc, điều khoản tạo dẫn xuất; chưa có thì `HOLD_SOURCE_RIGHTS`, không tự chuyển từ repo khác hay web.
- Có >/=30 nhóm sau dedup và nhóm đã được review (hoặc `INSUFFICIENT_GROUPS`, không tự hợp thức hóa TEST). Khóa seed chia tập, tỷ lệ, group/canonical/raw hash, ngưỡng near-duplicate trước khi nhìn TEST.
- Triển khai entrypoint F1/rights admission tách khỏi `learn_merges_f0_qa0_only`; không đổi B0 và không làm yếu F0 pin. TRAIN-only BPE; VALIDATION dùng theo thỏa thuận, TEST seal.
- Với tác vụ sử dụng dữ liệu thật hoặc ghi, hoàn thiện và kiểm định môi trường runtime tương ứng. Hiện C09 chỉ là partial Windows primitives + dry-run; cần restricted worker + broker và W01–W12 native nếu sử dụng đường Windows với bảo vệ đã quy định. Chỉ chạy test áp lực trong ngân sách được duyệt; không phải tải 4 GiB RAM hay tạo tệp 2 GiB để minh họa.
- Nếu F1 chưa sẵn, kết thúc gói với `L2=HOLD_SOURCE_RIGHTS` và tiếp tục công việc mã thuần L1/L2 có thể kiểm chứng; **không** tuyên bố P01 đã đóng.

**PASS L2 nếu:** nguồn có quyền, split đủ nhóm, bảo vệ tài nguyên đúng rủi ro, entrypoint không nhận dữ liệu cấm và negative QA độc lập có biên bản. Đây là một cổng kiểm soát thực chất, không phải chuỗi permit tách nhỏ.

### L3 — E0 tokenizer B1 và so sánh kỹ thuật B0/B1; phân xử P01

Chỉ mở khi L1/L2 đạt và tiền đăng ký E0 đã khóa. **Không huấn luyện GPT.**
- Học bộ BPE ứng viên **chỉ từ TRAIN** với cấu hình/seed/commit/corpus đã khóa; chạy hai tiến trình sạch độc lập, so chính xác SHA-256 của merges và vocab byte format. Không dùng TEST để chỉnh vocab/tie-break/near-duplicate/split.
- Kiểm trên TRAIN và VALIDATION đã tách: B0/B1 roundtrip = **100%** trên miền hợp lệ, invalid IDs không được nhận, byte fallback/UNK = 0, group/raw/canonical cross-split = **0**, nguồn chưa cho phép được nhận = **0**.
- Trình bày `tokens_per_byte`, tỷ lệ giảm token B1 so với B0, thời gian thực, RAM đỉnh, footprint, số OOM và artifact hashes. Không tuyên bố B1 giúp GPT loss hay tốc độ mô hình cải thiện khi chưa tới P03–P04.
- Independent checker kiểm provenance, TEST niêm phong, hash/split, tái lập và dữ liệu phát hiện lỗi. Nếu thiếu nguồn/mức phủ, đặt `HOLD` hoặc `INCONCLUSIVE`, không đánh tráo thành PASS.
- Lập **một** báo cáo cuối P01, mở PR riêng cho nhánh mã sau QA độc lập và quyết định merge riêng. Không tự merge PR #4.

**Đóng P01:** chỉ khi B0/B1 hợp đồng, dữ liệu và rights, QA tích hợp, nguồn/trình thực thi an toàn, B1 reproducibility, metrics và independent final QA đáp ứng tiêu chí vốn đã có. Sau đó mới chuyển P02, rồi **P03 Train**, **P04 Evaluation/Checkpoint**.

## V. Danh sách kiểm thử tích hợp tối thiểu (gom, không bỏ)

| Nhóm kiểm thử | Bộ kiểm tra gộp | Kết luận bắt buộc |
|---|---|---|
| K1 — B0/B1 byte & deterministic | S01–S06 dùng bằng chứng cũ + oracle mới cho tie/overlap/cross-document và 2-process merges | 100% roundtrip, byte SHA khớp, từ chối malformed |
| K2 — H03 dedup/split/leakage | raw/canonical/near duplicate + union-find transitivity + 30+ group seeded split + triple pairwise intersections | 0 overlap; determinism; reject insufficient groups |
| K3 — H02 quyền & PII | manifest positive/negative, reject unknown/denied, attempt TEST-as-TRAIN | 0 nguồn sai quyền đi vào TRAIN |
| K4 — H05 runtime/guard, independent negative | 12 pure mock/policy QA và native W01–W12 **nếu Windows E0 thực thi** | Không bypass/escape; nguồn guard chứng thực, không chỉ code |
| K5 — B0/B1 measurement & provenance | TRAIN-only BPE, separate clean runs, VAL metrics, readback SHA/receipt | merges SHA trùng; metrics đủ; TEST không dùng tune |

Không chạy lại những trường hợp PASS không bị thay đổi; giữ toàn bộ các bằng chứng lịch sử và không cập nhật kết quả một cách hồi tố.

## VI. Quyết định tại mốc rà soát

`P01_F0_CORE_FUNCTIONAL=PASS_10_OF_10_OFFHOST`  
`P01_H03_GROUP_SPLIT_INTEGRATION=NOT_ESTABLISHED`  
`P01_F1_SOURCE_ADMISSION=HOLD_NO_VERIFIED_ALLOW_MANIFEST`  
`P01_B1_LICENSED_TRAIN_E0=NOT_EXECUTED`  
`P01_C09_NATIVE_SECURITY=NOT_ESTABLISHED`  
`P01_PURE_POLICY_NEGATIVE_12=PREPARED_NOT_EXECUTED`  
`P01_FINAL_CLOSURE=NOT_YET`  
`P00_TO_P12_ROADMAP=UNCHANGED`  
`P01_LEAN_PROCESS=THREE_STEP_PER_SCOPED_WORK_PACKAGE`  
`SCIENCE_GATES_AND_SAFETY=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_P01_L1_F0_INTEGRATION_GAP_IMPLEMENTATION_AND_SINGLE_INDEPENDENT_QA`: chốt đúng bộ fixture/negative còn thiếu theo K1+K2, implement tách khỏi đường F1, rồi chạy một bộ QA logic **một lần** (không lặp F0 10/10), đọc kết quả độc lập và quyết định PASS/FAIL. Song song có thể tiếp nhận **thông tin nguồn F1 do người dùng thực sự sở hữu** cho L2, nhưng không được tự tải hay nhận dữ liệu chưa có quyền. C09 native QA và E0 là cổng riêng khi phát sinh quyền thực thi tương ứng.

**Không thực hiện gì ngoài việc ghi tài liệu này** trong thao tác rà soát.
