# LINEAGE — APPEND ONLY

> Quy định: Không sửa/xóa/đổi thứ tự entry đã ghi nhận. Mọi đính chính tạo entry mới trỏ entry cũ. Ghi cả hoạt động kỹ thuật, nghiên cứu, huấn luyện, QA PASS/FAIL và kết quả không kết luận. Nhật ký chi tiết đặt tại `experiments/`.

## L0000 — 2026-11-05 — Thiết kế quản trị ban đầu

- Loại: PROJECT_DESIGN
- Trạng thái: DESIGN_ONLY — không phải QA PASS hoặc kết quả thực nghiệm.
- Phạm vi: GPT decoder-only từ đầu; training pipeline; dense và paged KV; inference; benchmarking; commercial review; book.
- Baseline: gói code tham chiếu phase0 trong `reference/phase0/`; chưa chốt baseline trên máy người dùng.
- Bằng chứng: `PROJECT_CHARTER.md`, `docs/PHASE_PLAN.md`, `docs/GOVERNANCE.md`.
- Quyết định: Repository và phạm vi đã được người dùng xác nhận. Gói P00 mới là bản ứng viên; chưa có QA trên Windows và chưa được merge.

## L0001 — 2026-11-05 — P00 CPU reference smoke (không phải QA Windows)

- Loại: ENGINEERING_REFERENCE_QA.
- Nguồn: nhánh `feature/p00-source-docs-diagrams-20261105`, commit nguồn `2a8565c1fb669e1a46b07fd9ca18e16f4b438110`.
- Cấu hình: `configs/phase0_reference.json`, SHA-256 `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`.
- Kết quả: REFERENCE_CPU_SMOKE_PASS_8_OF_8; 5 bài model/attention/KV và 3 bài nhật ký.
- Môi trường: Linux x86_64, Python 3.13.5, PyTorch 2.10.0+cpu; **không phải máy Windows người dùng**.
- Biên bản: `experiments/runs/TTM_P00_CONTAINER_REFERENCE_20261105_01.json`; log: `artifacts/qa/TTM_P00_CONTAINER_REFERENCE_20261105_01.log`.
- Trạng thái QA độc lập trên Windows: PENDING. Huấn luyện khoa học: NOT_PERFORMED.
- Quyết định: chưa cho phép merge P00 vào `main`.

## L0002 — 2026-11-05 — Windows PowerShell 5.1 bootstrap FAIL / repair

- Loại: ENGINEERING_INFRASTRUCTURE_QA_FAILURE (không phải kết quả khoa học).
- Lỗi: `CallDepthOverflow` do định nghĩa `function Git` trùng tên lệnh `git` (PowerShell không phân biệt chữ hoa/thường), trước khi chạy bài thử khoa học.
- Phạm vi mã cũ: commit `24223818af8b05e5546462eb759c591a083ab202`; script sha `60be1d43a857a643d39388533f870ec967b7b84dff456b0a51e83a4dadf68548`.
- Sửa lỗi trên nhánh P00, kiểm tra lại mã script ở commit `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- Bằng chứng: `docs/qa/P00_PS51_CALLDEPTH_RECOVERY_20261105.md`.
- Quyết định: FAIL hạ tầng được giữ; không tính là FAIL mô hình và không cấp quyền rerun khoa học.

## L0003 — 2026-11-05 — Windows local QA 13/13 PASS

- Loại: ENGINEERING_LOCAL_WINDOWS_QA.
- Source commit: `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- Run: `TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z`.
- Kết quả: 5/5 test GPT/Attention/Paged KV + 8/8 test registry/harness = 13/13 PASS.
- Model SHA-256: `821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea`.
- Config SHA-256: `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`; trạng thái config `PROPOSED_NOT_FROZEN`.
- Receipt SHA-256: `6f30d4450199d471acd5e5a9c7b8264bc8fdc653bdc3b76ba5bfa8afa47034ee`.
- Bằng chứng: `artifacts/qa/p00/TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z.json` và hai stderr logs.
- Kết luận: LOCAL_WINDOWS_QA_PASS. QA độc lập lúc này vẫn PENDING.

## L0004 — 2026-11-05 — Independent Windows QA 6/6 PASS

- Loại: ENGINEERING_INDEPENDENT_FIXTURE_QA.
- Source commit được kiểm định: `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- Run: `TTM_P00_INDEPENDENT_QA_20261105T051340397776Z`.
- 6/6: numerical parity, future-token isolation, request isolation, zero-on-release, OOM state integrity, next-token gradient = PASS.
- Metrics: max_abs_logit_error `2.384185791015625e-07`; causal_prefix_error `0`; next_token_smoke_loss `5.489449977874756` (không đại diện kết quả đào tạo khoa học).
- Environment: Windows 11, Python 3.13.12, PyTorch 2.12.0+cpu.
- Receipt SHA-256: `b657b40e3da40060ef6c2e2b81239c64539f93100e169dae4920135ad6f16c38`.
- Bộ kiểm thử tách khỏi unit test phát triển; không khẳng định kiểm định bên thứ ba.
- Bằng chứng: `artifacts/qa/p00/TTM_P00_INDEPENDENT_QA_20261105T051340397776Z.json`, `artifacts/qa/p00/TTM_P00_INDEPENDENT_WINDOWS_QA.py`.
- Kết luận: INDEPENDENT_WINDOWS_FUNCTIONAL_QA_PASS trong phạm vi CPU correctness.

## L0005 — 2026-11-05 — P00 scoped formal QA adjudication

- Loại: ENGINEERING_QA_ADJUDICATION.
- Quyết định: `PASS_SCOPED_CORRECTNESS` — giữ P00 làm mốc kỹ thuật đầu tiên sau khi hoàn thành merge gate.
- Bằng chứng: `docs/qa/P00_FORMAL_ADJUDICATION_20261105.md` và `experiments/comparisons/P00_REFERENCE_BASELINE_20261105.md`.
- Không có baseline performance predecessor, không suy diễn speedup, chất lượng ngôn ngữ, kết quả GPU hoặc commercialization.
- Huấn luyện khoa học: `NOT_PERFORMED`. Config scientific lock: `NOT_FROZEN`.
- Giới hạn: tiếp tục dùng nguồn kỹ thuật đã kiểm định tại commit `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`; các commit hồ sơ mới sau đó không được thay đổi mã, config hoặc test được kiểm định.
- Quyết định merge: xét PR #1 sau khi xác minh exact PR head và nhánh `main`, không dọn worktree.

## L0006 — 2026-11-05 — Kiểm toán P00 sau hợp nhất GitHub và rà soát tài liệu

- Loại: kiểm toán mốc kỹ thuật (ENGINEERING_BASELINE_AUDIT) và chuẩn hóa tài liệu (DOCUMENTATION_REVIEW).
- Yêu cầu hợp nhất (Pull Request) #1 đã được hợp nhất vào GitHub `main` lúc `2026-11-05T05:21:08Z`, commit `8df22f5f29e645b2becff936daccbd32ac780661`.
- Nguồn mã đã kiểm định: `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`. Năm tệp mô hình, KV, kiểm thử, cấu hình và trình chạy QA trên `main` giữ nguyên nội dung so với nguồn kiểm định.
- Bằng chứng: QA Windows cục bộ `13/13 PASS`, QA bổ sung độc lập `6/6 PASS`. Mã SHA-256 của hai biên bản lần lượt `6f30d4450199d471acd5e5a9c7b8264bc8fdc653bdc3b76ba5bfa8afa47034ee` và `b657b40e3da40060ef6c2e2b81239c64539f93100e169dae4920135ad6f16c38`.
- Tại thời điểm kiểm toán, local `main` và local `origin/main` vẫn ở `f2ed098b033431924a3cbabdc9af89d7bbd7b378`, **chưa đồng bộ** với GitHub. Trạng thái sạch Git chưa được xác minh bằng CLI.
- Cấu hình P00 vẫn `PROPOSED_NOT_FROZEN`. Chỉ cho phép nhận diện mốc đối chứng kỹ thuật về tính đúng chức năng CPU, không phải khóa huấn luyện hoặc kết luận tăng tốc.
- Rà soát tài liệu: phát hiện hướng dẫn còn bằng tiếng Anh và ngôn ngữ không nhất quán. Chuẩn bị nhánh riêng `docs/p00-post-merge-audit-vietnamese-20261105`; giữ nguyên biên bản lịch sử và sơ đồ nguồn, thêm chú giải tiếng Việt.
- Báo cáo: `docs/qa/P00_POST_MERGE_AUDIT_20261105.md`; thuật ngữ: `docs/TERMINOLOGY_VI.md`; chú giải hồ sơ gốc: `docs/qa/P00_HISTORICAL_RECORDS_VI.md`.
- Quyết định: `GITHUB_P00_BASELINE=PASS`; `LOCAL_MAIN_SYNC=HOLD`; `DOCUMENTATION_BRANCH_QA=PENDING`; `P01_NOT_AUTHORIZED`. Chưa tạo/xóa/dọn cây làm việc Git (worktree).
- Bước tiếp theo: kiểm tra an toàn local Git chỉ đọc, kiểm thử độc lập nhánh tài liệu, rồi mới xem xét đồng bộ tiến nhanh (Fast-forward) và hợp nhất tài liệu.

## L0007 — 2026-11-05 — Đồng bộ tiến nhanh local P00 đạt

- Loại: kiểm toán đồng bộ kỹ thuật (ENGINEERING_LOCAL_FAST_FORWARD_ADJUDICATION).
- Tệp gốc trên Windows: `evidence/p00/TTM_P00_MAIN_FAST_FORWARD_20261105T075432222Z.json`; SHA-256 `f452b99c531bb8bdba26249b4ef07172044c582471ab87c48285954490fbb4ab`.
- Local `main` và `origin/main` sau đồng bộ khớp GitHub `main` tại `8df22f5f29e645b2becff936daccbd32ac780661`.
- Chế độ `EXACT_PIN_FAST_FORWARD_ONLY`; `protected_file_count=11`; `cleanup=NONE`; `training=NOT_PERFORMED`.
- Worktree nguồn P00 giữ nguyên `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- Biên bản và tham chiếu Git đọc lại qua RemoteMCP; bốn tệp quan trọng được đối chiếu SHA-256 trực tiếp và khớp.
- Quyết định: `LOCAL_P00_FAST_FORWARD=PASS`; không suy ra P01 được cấp quyền.
- Hồ sơ thẩm định: `docs/qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md`.

## L0008 — 2026-11-05 — Rà soát tài liệu P00 lần hai đạt

- Loại: kiểm tra độc lập theo bộ tiêu chí riêng (ENGINEERING_DOCUMENTATION_SECOND_PASS_QA).
- Nhánh: `docs/p00-post-merge-audit-vietnamese-20261105`, gốc `8df22f5f29e645b2becff936daccbd32ac780661`.
- Kiểm tra tĩnh ban đầu: 13/13 PASS; đối chiếu lần hai: 15/15 PASS trong phạm vi văn bản, Git và bằng chứng, không phải kiểm thử mô hình mới hoặc thẩm định bên thứ ba.
- Phát hiện và xử lý trạng thái tài liệu cũ: mô tả trước đồng bộ được bảo toàn như ảnh chụp lịch sử, có tài liệu thẩm định đồng bộ và phụ lục cập nhật.
- Không đổi mã nguồn, cấu hình, bài test, dữ liệu hoặc biên bản QA gốc; chỉ thay nội dung Markdown và bổ sung các mốc lịch sử.
- Bằng chứng: `docs/qa/P00_DOCUMENTATION_STATIC_QA_20261105.md`, `docs/qa/P00_DOCUMENTATION_INDEPENDENT_REVIEW_20261105.md`, `docs/qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md`.
- Giới hạn: chưa chỉnh ảnh SVG/PNG; chưa kiểm thử dựng sách; cấu hình khoa học vẫn `PROPOSED_NOT_FROZEN`.
- Quyết định: `DOCUMENTATION_SECOND_PASS_QA=PASS_15_OF_15`; có thể xem xét hợp nhất PR #2 sau kiểm tra chính xác commit HEAD và `main`. Không dọn worktree và chưa mở P01.

## L0009 — 2026-11-05 — Hoàn tất đồng bộ PR #2 và xác lập mốc P00

- Loại: kiểm toán đồng bộ và đóng mốc kỹ thuật (ENGINEERING_BASELINE_FINALIZATION).
- Đường dẫn chuẩn: `D:\WORK\RESEARCH\TokenToModel-Lab`; GitHub: `minhtri22/TokenToModel-Lab`.
- Biên bản Windows: `TTM_P00_DOC_PR2_FAST_FORWARD_20261105T081134196Z.json`; SHA-256 `9159499147c7b47b61427af6712adc33152401c1545f538ae890d4bad7305ed4`.
- Tệp gốc đã được đọc qua RemoteMCP và bản lưu trên GitHub `artifacts/qa/p00/TTM_P00_DOC_PR2_FAST_FORWARD_20261105T081134196Z.json` khớp nguyên nội dung.
- Local `main`, `origin/main`, GitHub `main` tại thời điểm đối chiếu: `c66e27a5d1e68958d42c825fd40f8a273994e0a0`; PR #2 đã hợp nhất.
- Đã đọc lại độc lập SHA-256 **13/13 tệp** được liệt kê trong biên bản; tất cả khớp. Worktree P00 vẫn giữ `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`. Dọn dẹp: `NONE`.
- PR #2 chỉ thay đổi 25 tệp Markdown; mã mô hình so với nguồn đã kiểm định giữ nguyên. Không chạy lại QA mô hình hoặc huấn luyện khoa học.
- Báo cáo: `docs/qa/P00_DOC_PR2_LOCAL_SYNC_AND_BASELINE_CLOSURE_20261105.md`.
- Quyết định: `P00_PR2_LOCAL_SYNC=PASS`; `P00_ENGINEERING_BASELINE_FINALIZED=PASS_SCOPED_CPU_CORRECTNESS`.
- Giới hạn: cấu hình P00 vẫn `PROPOSED_NOT_FROZEN`; chưa có bằng chứng chất lượng ngôn ngữ đã huấn luyện, GPU hoặc tăng tốc PagedAttention. `P01_ADMISSION=NOT_AUTHORIZED` cho đến cổng quyết định riêng.
- Không sửa bất kỳ mục L0000–L0008 nào; không xóa worktree, không dọn tệp trên Windows.

## L0010 — 2026-11-05 — Thiết kế và tiền đăng ký P01, chưa thực thi

- Loại: thiết kế nghiên cứu và quản trị (RESEARCH_DESIGN_ONLY / PREREG_DRAFT).
- Nhánh tài liệu: `design/p01-tokenizer-data-prereg-20261105`, gốc GitHub `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.
- Mục tiêu: hợp đồng bộ tách token (Tokenizer) và dữ liệu (Data Pipeline), đường byte B0 256 mã để đối chứng P00, ứng viên BPE B1 tách biệt; không thay Embedding P00 hoặc mã đã được QA.
- Tài liệu: `docs/p01/P01_DESIGN_PREREGISTRATION.md`, `docs/p01/P01_DATA_AND_SPLIT_PLAN.md`, `docs/p01/P01_METRICS_AND_QA_GATES.md`, `docs/p01/P01_WINDOWS_WORKSPACE_PREFLIGHT.md`.
- Cổng kỹ thuật: 100% hoàn nguyên byte/Unicode, 0 mã ngoài miền, 0 giao cắt nhóm dữ liệu giữa TRAIN/VALIDATION/TEST, 0 nguồn chưa đủ quyền, tái lập SHA-256; tỷ lệ token/byte chỉ là số đo, không tuyên bố cải thiện khi chưa có corpus.
- Tình trạng dữ liệu: `NOT_SELECTED`; ngưỡng gần trùng, seed, ngân sách RAM/đĩa và kích thước vocab BPE chưa được khóa. `PREREGISTRATION_LOCK=NOT_ISSUED`.
- Kiểm tra tĩnh: 16/16 tiêu chí nội dung đạt; 16/16 điều kiện kiểm tra tĩnh chương trình PowerShell đạt. Ghi lại lần kiểm tra từ khóa đầu tiên 15/16 do tiêu chí dò tiếng Anh không khớp chú thích tiếng Việt, không phải FAIL khoa học.
- Bằng chứng: `docs/p01/P01_D0_STATIC_QA_20261105.md`.
- Local `main` ở `c66e27a5d1e68958d42c825fd40f8a273994e0a0` khi đọc metadata qua RemoteMCP, còn GitHub `main` ở `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`; chưa có kết quả `git status` và chưa thực hiện đồng bộ Windows ở bước này.
- Không tải dữ liệu, không chạy huấn luyện tokenizer/GPT, không tạo worktree P01, không xóa hoặc dọn worktree P00, không tiêu thụ seed khoa học.
- Quyết định: `P01_D0_DESIGN_ONLY`, `P01_D0_STATIC_QA_PASS`, `P01_INDEPENDENT_METHOD_REVIEW_PENDING`, `P01_IMPLEMENTATION_NOT_AUTHORIZED`.
- Bước tiếp theo: tiền kiểm và đồng bộ Git local đúng commit nếu điều kiện an toàn đạt; sau đó thẩm định độc lập hồ sơ D0 trước mọi khóa hoặc triển khai.

## L0011 — 2026-11-05 — Đồng bộ Windows P01 đạt, thẩm định thiết kế D0 có điều kiện

- Loại: kiểm toán cơ sở kỹ thuật (ENGINEERING_BASELINE_SYNC) và thẩm định phương pháp thiết kế (DESIGN_METHOD_REVIEW); **không phải** kết quả khoa học.
- Biên bản Windows `TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json`; SHA-256 `ee69f32a993d011b35173074a5ea221bdffc3feb70c780b532f045e9beb58b7f`.
- Đã đọc lại bản gốc từ Windows qua RemoteMCP và tải nguyên văn lên `artifacts/qa/p01/TTM_P01_BASELINE_FAST_FORWARD_20261105T083903147Z.json`.
- Local `main`, `origin/main` và GitHub `main` tại thời điểm đối chiếu cùng commit `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`; worktree P00 giữ `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- 15/15 tệp được bảo vệ đã được kiểm tra SHA-256 trực tiếp và khớp biên bản; `cleanup=NONE`, `training=NOT_PERFORMED`, `p01_authorized=false`.
- Thẩm định D0 theo nội dung khác với kiểm tra từ khóa: **10/10 điều kiện tính nhất quán của thiết kế** đạt về mặt đặc tả. **5/5 điều kiện để khóa D1 vẫn chưa được đáp ứng**: thuật toán BPE, nguồn/giấy phép dữ liệu, phát hiện gần trùng và chia tập, F0/QA độc lập, ngân sách thực thi.
- Hồ sơ: `docs/p01/P01_D0_INDEPENDENT_METHOD_REVIEW_20261105.md`; tiền kiểm Windows có phụ lục kết quả cập nhật `docs/p01/P01_WINDOWS_WORKSPACE_PREFLIGHT.md`.
- Quyết định: `P01_LOCAL_BASELINE_SYNC=PASS`; `P01_D0_METHOD_REVIEW=PASS_SCOPED_DESIGN`; `P01_D1_PREREG_LOCK=HOLD_H01_H05`; `P01_IMPLEMENTATION_NOT_AUTHORIZED`.
- Không huấn luyện tokenizer/GPT, không tải dữ liệu, không tạo worktree P01, không dọn P00 hoặc thay mã nguồn P00.
- Bước tiếp theo: xử lý rõ 5 thiếu hụt H01–H05 trong một hồ sơ kế nhiệm chỉ chứa thiết kế, sau đó thẩm định độc lập D1 và ra quyết định riêng, không mở thực thi tự động.

## L0012 — 2026-11-05 — Hoàn thiện đặc tả D1 H01–H05, khóa khoa học vẫn HOLD

- Loại: thiết kế phương pháp, đối chiếu QA tài liệu (RESEARCH_DESIGN_REVIEW_ONLY), **không phải kết quả thực nghiệm hoặc huấn luyện**.
- Nhánh `design/p01-tokenizer-data-prereg-20261105` tiếp tục từ nguồn P00 `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`; yêu cầu hợp nhất PR #4 giữ dạng nháp, chưa hợp nhất.
- H01: đã đặc tả BPE byte tất định, quy tắc phá hòa bằng ID số nguyên, ghép không chồng lấn, định dạng `merges.ttmbpe` nhị phân có thứ tự, bộ từ vựng 2048 là ứng viên chính; chưa chạy.
- H02: đã đặc tả danh mục chứng minh quyền sử dụng, **chưa có nguồn corpus thật được duyệt**; tiếp tục HOLD.
- H03: đã đề xuất khóa đối chiếu NFC riêng, ngưỡng gần trùng theo Levenshtein/Jaccard, nhóm liên thông, seed chia tập `20261105`, tối thiểu 30 nhóm và 0 giao cắt, **chưa đánh giá trên corpus thật**.
- H04: đã định nghĩa F00–F11 bằng byte hex + SHA-256 và oracle âm tính; kiểm tra độc lập ở môi trường chuẩn bị **12/12 SHA-256 khớp**, 3/3 chuỗi UTF-8 lỗi bị từ chối bởi thư viện chuẩn. Chưa có bộ kiểm tra P01 thực thi trên Windows.
- H05: ngân sách ứng viên 64 MiB nguồn, tối đa 2000 tài liệu, RAM đỉnh 4 GiB, RAM trống tối thiểu 8 GiB, D: trống tối thiểu 16 GiB, 1800 giây; chưa đo tài nguyên hiện tại, chưa kiểm tra guard hoặc cấp quyền.
- Bộ kiểm tra tĩnh 18/18 tiêu chí nhất quán D1 đạt; lần kiểm tra từ khóa đầu tiên đạt 17/18 do dò khác cách diễn đạt “tối thiểu 30 nhóm”, đã chỉnh điều kiện dò. **Không được suy diễn 18/18 là chất lượng tokenizer**.
- Hồ sơ `docs/p01/P01_D1_H01_DETERMINISTIC_BPE_SPEC.md`, `docs/p01/P01_D1_H03_DEDUP_SPLIT_SPEC.md`, `docs/p01/P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md`, `docs/p01/P01_D1_H04_FIXTURES_AND_INDEPENDENT_QA_SPEC.md`, `docs/p01/P01_D1_METHOD_REVIEW_AND_LOCK_GATE_20261105.md`.
- Quyết định: `P01_D1_DOCUMENT_GAP_CLOSURE=PASS_SCOPED`, `P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD_SOURCE_QA_RESOURCE`, `P01_IMPLEMENTATION_NOT_AUTHORIZED`.
- Không tải dữ liệu, không học BPE, không huấn luyện GPT, không tạo worktree P01, không dọn worktree P00, không mở TEST hoặc tiêu thụ seed khoa học.
- Bước tiếp theo: cung cấp bằng chứng quyền dữ liệu hoặc giới hạn rõ P01 chỉ thử dữ liệu F0; chuẩn bị bộ QA độc lập/nguồn lực ở cổng riêng, sau đó quyết định có khóa D1 hay không.
## L0013 — 2026-11-05 — Tiền thẩm định H02/H04/H05 chỉ đọc, khóa D1 vẫn HOLD

- Loại: rà soát quyền dữ liệu, tài nguyên và oracle (DESIGN_GOVERNANCE_READONLY), không phải thực nghiệm hay huấn luyện P01.
- Nhánh: `design/p01-tokenizer-data-prereg-20261105`; mốc main tại thời điểm thẩm định: `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.
- H02: chưa có nguồn F1/F2 nào với `admission_decision=ALLOW` và SHA-256 nguồn. Wikimedia mới là ứng viên xem điều khoản, không chọn hay tải corpus; `H02=HOLD_NO_VERIFIED_SOURCE`.
- H05: máy Windows `machine-1` trực tuyến, nhịp báo node có chữ ký, active node jobs = 0; không có số đo RAM khả dụng hoặc D: trống, bộ giới hạn tài nguyên chưa QA; `H05=HOLD_RESOURCE_METRICS_AND_GUARD`.
- H04: tái tính SHA-256 cho 12 mẫu byte F00–F11, 12/12 khớp; F02/F03 có cùng NFC nhưng khác byte; F06–F08 bị UTF-8 strict từ chối 3/3. Chỉ kiểm tra oracle, chưa có checker P01 chạy trên Windows.
- Chương trình chỉ đọc `TTM_P01_D1_RESOURCE_READONLY_PREFLIGHT.ps1`, SHA-256 `e48e6a101e640a483f727786e50032f04e1b39bdbc6c6b97b75d9c437c606606` đã chuẩn bị; chưa được chạy trên Windows.
- Báo cáo: `docs/p01/P01_D1_SOURCE_RIGHTS_READONLY_REVIEW_20261105.md`, `docs/p01/P01_D1_WINDOWS_RESOURCE_READONLY_REVIEW_20261105.md`, `docs/p01/P01_D1_INDEPENDENT_QA_READONLY_PREAUTH_20261105.md`, `docs/p01/P01_D1_READONLY_PREAUTH_ADJUDICATION_20261105.md`.
- Kết luận: `P01_D1_READONLY_PREAUTH=COMPLETED_WITH_HOLD`; `P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD`; `P01_IMPLEMENTATION_NOT_AUTHORIZED`.
- Không tạo worktree P01, không tải dữ liệu, không huấn luyện BPE/GPT, không hợp nhất PR #4, không dọn worktree P00.
- Bước tiếp theo: đo RAM/D: chỉ đọc trên Windows và chứng minh quyền nguồn hoặc quyết định F0-only; sau đó tiền thẩm định checker độc lập.

## L0014 — 2026-11-05 — Thẩm định số đo RAM/đĩa P01 chỉ đọc; phạm vi nguồn F0-only

- Loại: tiền kiểm tài nguyên và quyết định phạm vi thiết kế (RESOURCE_PREAUTH_READONLY / SOURCE_SCOPE_DECISION), **không** phải kết quả khoa học.
- Console Windows người dùng cung cấp: `2026-11-05T11:01:18.0864528Z`, máy `DESKTOP-4PSD0G2`, local `main=92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`. SHA-256 chương trình đã ghim: `e48e6a101e640a483f727786e50032f04e1b39bdbc6c6b97b75d9c437c606606`.
- RAM khả dụng `10.959 GiB >= 8 GiB`; D: còn trống `34.869 GiB >=16 GiB`; D: sau dự phòng `32.807 GiB >=12 GiB`. Ba điều kiện tài nguyên ứng viên đạt tại thời điểm đo, **không chứng minh** bộ giới hạn runtime hoặc thời gian.
- Bản chép console có ghi rõ nguồn người dùng, không phải receipt ký số của Windows: `artifacts/qa/p01/TTM_P01_D1_RESOURCE_READONLY_USER_CONSOLE_20261105T110118Z.txt`.
- H02 chưa có nguồn F1/F2 được xác minh giấy phép/PII/SHA, vì vậy `P01_SOURCE_SCOPE=F0_ONLY_DESIGN_AND_ORACLE_REVIEW` và không thu nhận corpus.
- H04 có hợp đồng QA độc lập C01–C10 ở mức thiết kế; checker chưa được viết, chưa có QA động.
- Hồ sơ: `docs/p01/P01_D1_WINDOWS_RESOURCE_SNAPSHOT_ADJUDICATION_20261105.md`, `docs/p01/P01_D1_H04_INDEPENDENT_CHECKER_DESIGN_GATE_20261105.md`.
- Quyết định: `H05_RESOURCE_SNAPSHOT=PASS_CANDIDATE`; `H05_RESOURCE_GUARD_QA=HOLD`; `H02_SOURCE_RIGHTS=HOLD`; `P01_D1_PREREG_LOCK=NOT_GRANTED`; `P01_IMPLEMENTATION_NOT_AUTHORIZED`.
- Không tạo worktree P01, không tải dữ liệu, không huấn luyện BPE/GPT, không hợp nhất PR #4 và không dọn P00.

## L0015 — 2026-11-05 — Thẩm định hợp đồng checker độc lập C01–C10, I0 vẫn HOLD

- Loại: đánh giá phương pháp ở mức tài liệu (DESIGN_CONTRACT_ADJUDICATION_ONLY); không phải kết quả QA động, kiểm tra bên thứ ba hay thực nghiệm.
- Nhánh `design/p01-tokenizer-data-prereg-20261105` PR #4 tiếp tục là bản nháp; nguồn thẩm định ban đầu ở HEAD `29a486fce0944bd2b726322ea3a6b1abb64f9c5e`, mốc GitHub main `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.
- Các hợp đồng `C01` (toàn miền byte B0) và `C02` (12 mẫu F0 có oracle byte) đạt **PASS_DESIGN**; `C03–C10` là **HOLD_DESIGN**, chưa đủ bằng chứng/oracle từ chối hoặc cơ chế kiểm định độc lập. `FAIL_DESIGN=0`; tất cả `NOT_EXECUTED`.
- Các khoảng trống chặn I0: `G04-01` ma trận API/lỗi; `G04-02` oracle BPE nhiều vòng/merges sai; `G04-03` trùng/gần trùng sát ngưỡng; `G04-04` tái lập/snapshot TRAIN và chặn TEST; `G04-05` nguồn/PII; `G04-06` cơ chế giới hạn RAM/đĩa/thời gian; `G04-07` manifest và biên bản bất biến; `G04-08` thẩm định lại.
- Báo cáo: `docs/p01/P01_D1_H04_C01_C10_CONTRACT_ADJUDICATION_20261105.md`.
- Quyết định: `P01_D1_H04_CONTRACT_ADJUDICATION=HOLD_WITH_SCOPED_PASS`, `P01_D1_SCIENTIFIC_LOCK=NOT_GRANTED`, `P01_I0_IMPLEMENTATION=NOT_AUTHORIZED`.
- Không tạo worktree P01, không tải corpus, không chạy tokenizer/BPE/GPT, không hợp nhất PR #4 và không dọn dẹp P00.
- Bước kế tiếp: sửa hợp đồng checker ở mức thiết kế G04-01..07 và xét G04-08 ở quyết định độc lập trước bất kỳ permit I0.
## L0016 — 2026-11-05 — Sửa oracle H04 G04-01..07 và thẩm định G04-08, còn hai HOLD

- Loại: kiểm toán và sửa hợp đồng thiết kế (DESIGN_ONLY_ORACLE_REPAIR_AND_METHOD_REVIEW); **không** có chạy checker/tokenizer hay thực nghiệm.
- Nhánh: `design/p01-tokenizer-data-prereg-20261105` PR #4, đối chứng GitHub main `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.
- Trước sửa tại L0015: C01–C02 `PASS_DESIGN`, C03–C10 `HOLD_DESIGN`. Giữ nguyên L0015 để bảo toàn lịch sử.
- Đã bổ sung các bảng A01–A10 (lỗi API, miền ID, UTF-8), M01–M04 (BPE nhiều vòng, giới hạn ranh giới, parse merges), K01–K08 (trùng/gần trùng, giao cắt, chia tập), snapshot TRAIN, ma trận quyền nguồn, hợp đồng giới hạn toàn cây tiến trình và bằng chứng bất biến.
- Phát hiện lỗi oracle khi viết G04-03 lần đầu: với |A|=18 và |B|=19, khi số giao đổi từ 17 xuống 16 thì union phải đổi từ 20 lên 21. Đã sửa trong đặc tả trước G04-08. Đây là lỗi tài liệu thiết kế, không phải lỗi bài chạy khoa học.
- Thẩm định chéo G04-08: G04-01/02/04/05/07 `PASS_DESIGN`, G04-03/06 `HOLD_DESIGN`. C01–C06/C08/C10 `PASS_DESIGN`, C07/C09 `HOLD_DESIGN`, `FAIL_DESIGN=0`; tất cả C01–C10 `NOT_EXECUTED`.
- Điều kiện còn thiếu: mẫu văn bản byte sinh đúng Jaccard 5-gram sát ngưỡng; chọn chính xác bộ đếm memory, cơ chế gắn Job Object và oracle dừng an toàn trên Windows. Cần golden manifest trước I0.
- Hồ sơ nguồn: `docs/p01/P01_D1_G04_01_03_ORACLE_REPAIR_DESIGN_20261105.md`, `docs/p01/P01_D1_G04_04_07_FAIL_CLOSED_REPAIR_DESIGN_20261105.md`, `docs/p01/P01_D1_G04_08_INDEPENDENT_CONTRACT_READBACK_20261105.md`.
- Quyết định: `TTM_P01_D1_G04_08_DESIGN_REVIEW=COMPLETED_WITH_HOLD`; `TTM_P01_I0_IMPLEMENTATION_PERMIT=NOT_GRANTED`; `TTM_P01_D1_SCIENTIFIC_LOCK=NOT_GRANTED`.
- Giữ PR #4 ở trạng thái nháp, không tạo worktree P01, không tải corpus, không huấn luyện, không sửa P00 hoặc dọn dẹp.
- Bước kế tiếp: `TTM_P01_D1_G04_03_06_REMAINING_DESIGN_HOLD_CLOSURE`.
