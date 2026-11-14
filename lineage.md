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

## L0010 — 2026-11-07 — P01 F1 Wikipedia WP30, E0 byte-BPE một lượt, QA độc lập PASS (phạm vi nội bộ)

- Loại: SCIENTIFIC_TOKENIZER_EXPERIMENT; kết quả đo E0 thực trên 30 tài liệu Wikipedia tiếng Việt thuộc phạm vi F1 nội bộ; không phải chứng nhận chất lượng mô hình hoặc thương mại.
- Phạm vi đã khóa: H03 30 nhóm độc lập, split seed 20261105, TRAIN=24/VALIDATION=3/TEST=3; TEST niêm phong, không tham gia học BPE hay chọn cấu hình.
- E0 B0 byte round-trip 100%. B1 target/actual vocab 2048, 1792 merges. Hai worker Linux Docker độc lập có cùng SHA-256 `53aabcb8ac3a3c16c7cbd915b76eb82653a334c98381fad95a05eba0a9353f60`, huấn luyện chỉ trên TRAIN; thời gian lần lượt 6.787 và 7.817 giây.
- TRAIN byte/B0 tokens 1,127,975 → B1 tokens 288,526; VALIDATION byte/B0 tokens 147,164 → B1 tokens 38,992. Hoàn nguyên TRAIN/VALIDATION PASS; kiểm tra rò rỉ raw/canonical/group = 0/0/0.
- QA độc lập `INDEPENDENT_E0_QA_PASS` trên 30 nguồn SHA và 27 tài liệu round-trip; biên bản `experiments/p01/TTM_P01_F1_WP30_E0_DOCKER_20261107/independent_qa.json`, source `source_lock.json`, `e0_integrated_result.json`; receipt tại `evidence/p01/TTM_P01_F1_WP30_E0_DOCKER_20261107.json` (SHA từ console `acefa6dde2e2d5a683fc9da169b0d2c70e03bacd28457cdaae5351ccab9728b3`).
- Mã chạy V4 SHA-256 `7b36c6657957367908d26190b600e5e0b39c93007e455c0e20345ef48b29f2af`, Git blob `6baf7f94405a6e83ba40c92984f42f0531519ad4`; engine `2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d`, checker `ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1`.
- Phán quyết: `E0=PASS_CONFIRMED_IN_SCOPE`, `P01_TECHNICAL_EXIT=PASS_SCOPED_WP30`; chỉ P01 main closure sau review/merge. Bảo toàn lịch sử S1 FAIL và các biên bản trước; không chạy lại E0, không dùng dữ liệu TEST, không cấp quyền P03 huấn luyện mô hình hay phát hành công khai qua entry này.
- Hồ sơ phán quyết: `docs/p01/P01_F1_WP30_E0_FORMAL_ADJUDICATION_AND_P02_OPEN_GATE_20261107.md`; `artifacts/qa/p01/P01_F1_WP30_E0_FINAL_ADJUDICATION_20261107.json`.

## L0011 — 2026-11-08 — TTM Small4M T4: 1.024 bước TinyStories thật, H1 NLL VAL PASS

- Loại: **SCIENTIFIC_LANGUAGE_MODEL_TRAINING**; không phải kiểm thử kỹ thuật hoặc huấn luyện synthetic. RunID `t4_science_4m_1024_a2_20261108_v1`, seed 20261108, mô hình Transformer P02 3.749.376 tham số, vocabulary 2048, context 256.
- Tiền đăng ký: 2.048 truyện TRAIN / 256 VAL / 64 TEST niêm phong; BPE học trên 768 TRAIN; đúng 1.024 optimizer step × 4.096 nhãn token mục tiêu/bước = 4.194.304 lượt nhãn TRAIN; FP16, microbatch 8, tích lũy gradient động. 4 mốc checkpoint READY-last 256/512/768/1024. Đã hoàn thành 1.024/1.024 trong một phiên Colab không dừng chủ động tại 256.
- Giả thuyết xác nhận H1 khóa trước khi chạy: NLL VAL tại **chính checkpoint bước 1.024** thấp hơn bigram Add-α=0.1 fit từ TRAIN ít nhất **5%** và cận dưới khoảng tin cậy bootstrap 95% theo 256 truyện VAL, 1.000 resample seed 20261109, của `bigram_NLL-model_NLL` phải lớn hơn 0.
- **Kết quả khoa học:** `PASS_H1_CONFIRMATORY_VAL_SCOPE`. CPU QA độc lập nạp checkpoint thật bước 1.024 và tính lại từ chính TRAIN/VAL đã khóa: model VAL NLL **3.5223388517**, bigram VAL NLL **3.9972314170**, cải thiện **11.880537%**, chênh lệch tuyệt đối **0.4748925653**, bootstrap 95% **[0.4581867476, 0.4940615819]**. VAL chấm 61.122 nhãn trên 256 truyện, TEST **chưa truy cập**. Sai lệch so với báo cáo Colab của model NLL chỉ khoảng 5.2e-9.
- **Bằng chứng độc lập:** 4/4 checkpoint từ Drive được tải nguyên tệp (mỗi file 45.074.891 byte), SHA đúng READY; mở `weights_only=True` PASS; nhật ký 1.024 bước liên tục, mỗi bước 4.096 nhãn, các nhật ký checkpoint là tiền tố đúng của log cuối. Checkpoint 1.024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; final JSON SHA256 `5a6c0ab4da808bbe0bfaa0b6cde085277c1a8eb0735b73d24a3700e3f34f62c4`; khóa science SHA256 `fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817`; dữ liệu riêng tư SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`.
- Hồ sơ phán quyết: `docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md`; biên bản `evidence/pilot/t4-science/T4_A2_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION.json` (SHA256 `a5e76621b8dee312cd49ffe9fc6489548c3451ad4cd6baf8af3a7e0d0749219e`) và `T4_H1_INDEPENDENT_CPU_RECOMPUTE.json` (SHA256 `c3b60ea5f2c1398fec2d86be1438c9e153f0702d9cbef5bbbddbf0b8f148a6de`). Checkpoint và dữ liệu token chỉ nằm trong Drive riêng tư: `https://drive.google.com/drive/folders/1GK6OtQxyq5u1ALkXKdFygFT8uvhnL5-d`.
- Giới hạn: **chỉ chứng minh H1 NLL VAL so với bigram trong phạm vi pilot và một seed**; 498.287 vị trí TRAIN được dùng lại trung bình ~8,417×; không suy ra chất lượng văn bản, kết quả TEST hay khả năng áp dụng thương mại. Chưa làm kiểm định mù TEST (64 truyện), chưa xuất/kiểm chứng checkpoint đã train qua GGUF/llama.cpp/Ollama. Bộ đếm GPU 74,2535 giây là compute+VAL, không phải tổng thời gian phiên Colab.
- Tiếp theo: chỉ **một lần** đánh giá TEST niêm phong trên checkpoint bước 1.024 đã chọn trước, không huấn luyện lại hoặc điều chỉnh theo TEST; sau đó T5 xuất GGUF F32 và thử nghiệm máy cá nhân. Không thay đổi lịch sử L0000–L0010 hoặc các FAIL kỹ thuật đã lưu.

## L0012 — 2026-11-08 — TTM Small4M T4 TEST 64 truyện giữ lại: cải thiện NLL so với bigram (mô tả)

- Loại: **SCIENTIFIC_HELDOUT_TEST_ONE_SHOT**, không huấn luyện lại; RunID `ttm_t4_test_64_step1024_one_shot_20261108_v1`; `CLAIM.json` được ghi trước khi giải mã/đánh giá TEST, một lần duy nhất và không chạy lại; trạng thái `COMPLETED_TEST_ONE_SHOT_UNADJUDICATED` đã được thẩm định để phân loại kết quả.
- Mô hình cố định: chính checkpoint T4 đã huấn luyện bước **1.024**, SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; dữ liệu **64 truyện TEST đã khóa từ T1** (76 cửa sổ, 14.669 token mục tiêu), BPE chỉ học trên TRAIN. Không dùng TEST để lựa chọn checkpoint, điều chỉnh hyperparameter, đổi mô hình hay huấn luyện thêm.
- Kết quả TEST từ báo cáo gốc: **model NLL 3.48359107334**, bigram Add-α=0.1 chỉ fit TRAIN **3.97360374532**, chênh lệch tuyệt đối **0.49001267198**, cải thiện tương đối **12.3316944%**; unigram NLL 5.99091418635. Khoảng tin cậy bootstrap theo truyện 95% (1.000 resample, seed 20261109) cho lợi thế NLL **[0.45801078385, 0.52163911524]**, cả hai ngưỡng 5% và cận dưới >0 đều đạt theo báo cáo.
- **Phán quyết: `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`.** Đây là kiểm tra độc lập *về tập dữ liệu giữ lại* so với VAL đã dùng để chốt H1, nhưng không phải lần tái tính độc lập từng token TEST; biên bản duy nhất là phép đo TEST. Người kiểm định đã đọc nguyên biên bản trên Windows, đối chiếu nguồn/CLAIM và phép tính NLL, xác minh SHA256 báo cáo `7df02a53cb84d3026f3b259154e0c4f3dcc5fa27e16170e740fd570df059a50d` qua tái tạo chính xác byte-format CRLF của tệp gốc. TEST đã tiêu thụ; tuyệt đối không chạy lại.
- Lưu ý biểu mẫu: bộ đánh giá dùng lại tên trường `primary_*_val_nll`, schema và cảnh báo từ bộ VAL; wrapper thực tế định danh `eval_set=SEALED_TEST_64`, `test_stories=64`, `test_tokens_saved=false`. Giữ nguyên tệp gốc không sửa nhãn sau thực nghiệm; không suy diễn kết quả là chất lượng truyện do con người đánh giá.
- Bằng chứng không nhạy cảm trên PR #12: `evidence/pilot/t4-science/T4_TEST_64_ONE_SHOT_CLAIM.json`, `evidence/pilot/t4-science/T4_TEST_64_ONE_SHOT_ORIGINAL_REPORT.json`, báo cáo phân xử `docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md`. Dữ liệu TEST/tokens và checkpoint **không** đưa lên GitHub.
- T5 kỹ thuật liên quan: trọng số bước 1.024 đã xuất thành GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, 52/52 tensor readback PASS ở exporter; **chưa kiểm chứng đầu ra llama.cpp/Ollama trên mô hình đã train**. Đây không phải kết quả khoa học mới. Tiếp tục T5 mà không chạy lại T4/TEST hoặc thay đổi lịch sử L0000–L0011.

## L0013 — 2026-11-10 — TTM T5 KV F16/F32 × Flash 2×2: strict logits parity FAIL trong 32 phép đo tổng hợp mới

- Loại: **SCIENTIFIC_F32_GGUF_LOGIT_PARITY_DIAGNOSTIC**, thử nghiệm một lượt mới, kết quả âm tính có giá trị trong phạm vi khóa; không huấn luyện.
- Tiền đăng ký: `TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json`, Git blob `3b12cc1883ab20e2d9e3a92e6907586c1b4cad36`. 8 fixture token-ID mới `SYN01..SYN08` × 4 cấu hình: S0 F16+Flash ON, S1 F32+Flash OFF, S2 F32+Flash ON, S3 F16+Flash OFF. Mỗi kết quả gồm 2.048 logits của checkpoint 1.024; ngưỡng `max_abs≤0.001` cố định, không đổi sau đo.
- Cổng kỹ thuật trước thực nghiệm: model P02 checkpoint bước 1.024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; GGUF F32 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; EXE MSVC `0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537`. 13/13 bài QA tổng hợp PASS; `--self-check`, compiled constants và reference PyTorch F32 8×2048 đều PASS. Các biên bản FAIL kỹ thuật stage cũ được giữ nguyên.
- Chủ sở hữu phê duyệt một batch native 32 mới và thực thi thành công một lần duy nhất. Receipt Windows `RUN_RECEIPT.json` SHA256 `fcaea7a629bd6dda7a4f35b60da686b73b02bc0e9e56ebe7c380d9b9e4c7db09`; `AUDIT_FROZEN_NEW_32.json` SHA256 `8aca17561d6beca200fbc746854ab0186e5f3d75930737077111a86c475acc6c`. Cả hai SHA được tái tính độc lập từ readback tương ứng với CRLF Windows, đúng owner receipt; raw native JSONL SHA256 `544df628802591bcdda7ca9d6de4779d5e2872ee8b409c6710ede5bbf8ac19b8` do auditor đã ghi và liên kết receipt.
- **Phán quyết khoa học: `FAIL_STRICT_LOGITS_32_OF_32_SCOPED_SYNTHETIC`.** S0=0/8, S1=0/8, S2=0/8, S3=0/8 dưới ngưỡng 0,001, sai số max-abs lớn nhất 0,0044434023. Cả 32/32 vẫn giữ nguyên top-1. Flash ON quan sát 4 nút, OFF 0 nút theo từng dòng. **Đây không phải lỗi hạ tầng**: suy luận và audit 32 dòng hoàn tất.
- Kết luận nguyên nhân: đổi riêng KV F16/F32 và Flash ON/OFF **không đủ** cứu strict parity trong 8 fixture này vì S1 (F32+Flash OFF) vẫn FAIL 8/8; không chứng minh KV hay Flash không góp sai số. S0 và S2 có max/mean-abs metric bằng nhau ở 8/8, **không phải bằng chứng bitwise 2.048 logits giống hệt**. Trường `descriptive_contrasts` trừ max-abs là thống kê mô tả, không phải đo tác động nhân quả có dấu từng chiều.
- 8 fixture parity gốc vẫn `FAIL_7/8` bất biến; TEST/Q1Q2 không được truy cập, không train hay chọn checkpoint lại. Bằng chứng gốc thô nằm trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_kvflash_frozen_new_32_native_one_shot_v1_20261110`, không upload private checkpoint. Giới hạn: read_file remote cắt dòng JSONL 2048 logits quá dài nên kiểm tra lần hai trên receipt/audit; chính auditor độc lập đã đọc toàn bộ 32 dòng thô trên Windows.
- Báo cáo phân xử: `docs/pilot/TTM_T5_FROZEN_32_NATIVE_NEGATIVE_SCIENCE_ADJUDICATION_AND_MERGE_REVIEW_20261110.md`; biên bản `artifacts/qa/ttm-t5-parity/TTM_T5_FROZEN_32_NATIVE_STRICT_PARITY_NEGATIVE_SCIENCE_ADJUDICATION_20261110.json`. **Merge chính thức vẫn HOLD chờ review nhánh T5 riêng**, không ảnh hưởng PR #13.

## L0014 — 2026-11-10 — TTM T5 GPT2 GELU_ERF: xác nhận strict logit parity trên 4 fixture mới — PASS có giới hạn

- Loại: **SCIENTIFIC_CAUSAL_NUMERIC_PARITY_DISCOVERY_AND_HELDOUT_CONFIRMATION**; **phán quyết `PASS_HELDOUT_STRICT_LOGITS_4_OF_4_SCOPED_GELU_ERF`**, trên 4 fixture C01–C04 tiền đăng ký trước khi phân tích D01/D02, không huấn luyện hoặc truy cập TEST/Q1Q2. Không thay ngưỡng 0,001; không chạy lại 8 fixture gốc hoặc batch 32 lịch sử.
- Mô hình và nguồn khóa: checkpoint T4 bước **1.024** SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`. Prereg mới khóa C01–C04 Git blob `82fdd9fe716579181db648caa69170fb63d115a6`; tham chiếu CPU P02 F32 ZIP SHA256 `e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996`.
- Cơ chế: trong hai fixture khám phá D01 (1 token) và D02 (5 token), các thống kê sai khác tensor trước GELU giống nhau giữa hai binary, còn tại `ffn_gelu-0` xảy ra sai khác đầu tiên vượt độ nhạy chẩn đoán `1e-5` ở baseline. Thay **chỉ** lựa chọn hàm `LLM_FFN_GELU` của GPT-2 GGML thành `LLM_FFN_GELU_ERF` đưa cả D01/D02 về strict PASS; giữ CPU/KV F32/Flash OFF. Đây là chứng cứ can thiệp có kiểm soát cho **khác biệt biến thể GELU giữa GGML và PyTorch P02** trong phạm vi đã thử.
- Tập xác nhận C01 (2 token), C02 (4), C03 (11), C04 (17) đã chạy native **một batch duy nhất**, mỗi fixture so đúng **2.048 logits** so với tham chiếu đã khóa: max-abs lần lượt **0,000002811279296**, **0,000004769211426**, **0,000003819118652**, **0,000005725019530**. **4/4 strict PASS `max_abs≤0.001`**, tất cả top-1 trùng và 4 nút `ffn_gelu_erf-0` thật được kiểm chứng. Sai số lớn nhất thấp hơn ngưỡng ~174,67×.
- Provenance Windows: receipt `CONFIRMATORY_ONCE_RECEIPT.json` SHA256 `95ed3c419e42df493dc314abeb42e47afa1bf72fcb90d2c7246ff4c55d645e88`; independent checker `C01_C04_INDEPENDENT_STRICT_AUDIT.json` SHA256 `1d5e050e9aefbeb5720a5f86986ecbcffe2a51a8c7605d07c85467553b8b8887`; native JSONL SHA256 `9b674719010eb04ce14865104613de953030fed6febb653faa9b6bdc52f02027`; executable SHA256 `aa55f398617e8160013e3d1d8494986160d150f5052e44b39c8885f6f47a5df4`. Windows 12/12 negative QA PASS, self-check và native exit 0; full 4×2.048 so sánh đã được checker thực thi, còn remote readback chỉ kiểm receipt/audit/aggregate vì giới hạn đọc raw dòng dài.
- Bằng chứng GitHub: `artifacts/qa/ttm-t5-parity/TTM_T5_C01C04_GELU_ERF_HELDOUT_STRICT_4_OF_4_INDEPENDENT_ADJUDICATION_20261110.json` và `docs/pilot/TTM_T5_GELU_ERF_C01C04_HELDOUT_STRICT_PASS_INDEPENDENT_ADJUDICATION_AND_PR16_MERGE_REVIEW_20261110.md`. Raw checkpoint/reference và native tensors chỉ ở lưu trữ chủ dự án, không công khai trên GitHub.
- **Giới hạn và bảo toàn kết quả âm tính:** L0013 `FAIL_STRICT_LOGITS_32_OF_32_SCOPED_SYNTHETIC` vẫn giữ nguyên; 8 fixture gốc `FAIL_7/8` vẫn giữ nguyên vì không chạy lại. PASS mới **chỉ** áp dụng cho C01–C04 với bản sửa GELU_ERF, KV F32/Flash OFF; không kết luận Flash ON, F16, bất kỳ độ dài chuỗi hoặc tính tương đương bitwise phổ quát. PR #16 tiếp tục Draft/HOLD chờ đánh giá vệ sinh nguồn 83 tệp và quyết định merge của chủ dự án; `main` không thay đổi.

## L0015 — 2026-11-11 — TTM Small4M FRESH16 V2: chấm mù 32 đầu ra và phản thực 16 cặp — FAIL có giới hạn

- Loại: **SCIENTIFIC_LOCAL_CONTEXT_FACT_CONDITIONED_CONTINUATION_EXPLORATORY**; **phán quyết `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`**, giữ nguyên verdict máy `NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED`.
- Nguồn khoa học đã khóa: nhánh `research/ttm-small4m-prompt-adherence-continuation-design-20261111`, original source HEAD `c05872354d892a9656f8f98642866f7eebfd0f50`; runner Git blob `f069f2bdaa2d9691a1ce6c9746ff8f2923beb1d8`; mapping niêm phong SHA256 `eb570460b1423bb4b2355ccb5b7b56862c641721d5ecf62f7136224b71ea20a8`, anchor commit `d95b09f894dd7ef975b375a794f50a1d7905e0d6`. CPU sinh **32/32** đầu ra trong một lượt; không train/TEST/rerun; checkpoint **bước 1024 chính**, bước 1280 mô tả.
- Tiền đăng ký V2: H1 tại bước 1024 đạt nếu **≥12/16** `adherence≥2`; H2 đạt nếu **≥6/8** cặp và **≥1** cặp trong từng nhóm `entity_location`, `causal_reasoning`, `rule_constraint`, `goal_persistence`. Không sửa ngưỡng sau chấm.
- Kết quả chấm mù: S1 riêng biệt **32/32**, điểm adherence 28×1 và 4×0, **0** điểm ≥2; SHA256 `d08d59a9fe9738ef798aa2e0449345cb76e5c9f24f825a37685f928052028d35`, khóa commit `5fd1d923de52d18709a39332400e3e98e6dfb31d` **trước** khi cung cấp 16 cặp cho S2. S2 riêng biệt **16/16**, `h2_binary=0` ở **16/16**; SHA256 `517643feba73c96003334a1e8a9095ebd091aaff3e764ddd87faf91dbf78b31b`, khóa commit `9c02e0f3c7d3073e742de7fc75a08e5a48ec9afe` **trước** giải mù. Các nhãn phiên S1/S2 do owner cung cấp, không có session ID hệ thống.
- **Kết quả khoa học chính:** **H1=0/16, H2=0/8** tại checkpoint 1024; cả bốn nhóm H2 đều **0**. GATE FAIL trong phạm vi `LOCAL_CONTEXT_FACT_CONDITIONED_CONTINUATION_EXPLORATORY`. Bộ kiểm định gốc in `FRESH16_FINAL_TALLY=PASS_FROZEN_GATE_EXECUTED`, đó là PASS hoàn thành bộ đếm, **không phải** PASS H1/H2.
- Bằng chứng tally chính thức: `FINAL_TALLY_PRIVATE.json` **839 byte**, SHA256 `64ec345fef6ef2f1c8b08e847047e3d3ac53f7bcca83fe39ae10d27e69b6f181` đối chiếu byte đính kèm và readback Windows; tệp riêng tư tại `_tmp/ttm_fresh16_v2_e0_20261111/FINAL_TALLY_PRIVATE.json`. Hồ sơ phân xử: `docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md` và `artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCOPED_NEGATIVE_SCIENCE_ADJUDICATION_20261111.json`. Không đưa điểm từng trường hợp, output, token IDs hoặc mapping lên GitHub.
- Giới hạn: FAIL này **không phủ định** PASS NLL VAL/TEST ở L0011–L0012, không chứng minh mọi khả năng suy luận/ngữ nghĩa đều thất bại, không phải kết quả confirmatory của checkpoint 1280; không đo độ đồng thuận giữa nhiều người chấm cùng vai trò. Giữ nguyên tất cả lịch sử L0000–L0014; không merge main, không chọn lại checkpoint/đổi rubric, không chạy lại FRESH16 hoặc TEST.

## L0016 — 2026-11-13 — TTM-Small-4M FC01 V2: đóng nghiên cứu exploratory và thiết kế D1 Bridge mới — PASS có giới hạn / D1 HOLD

- Loại: **EXPLORATORY_FACT_CONDITIONING_DATA_VS_OBJECTIVE_CAUSAL_COMPARISON_ARCHIVE**; phán quyết **`PASS_SCOPED_EXPLORATORY_FC01_CLOSED`** sau một lượt A/B/C 256 optimizer steps/arm (tổng 768); không huấn luyện lại/đổi seed/đánh giá lại. Nguồn: parent checkpoint step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, private corpus FC01 V2 SHA256 `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3`, GO lock SHA256 `8b274e3bc976e73ad25a689e8044dda2fcb98766a8d2cdd890cb08d6f582c091`; terminal receipt `67b66ee06f6821e324c678367174d110a4620200f6f9639fb3fc0ebd1d966df1`. Ba checkpoint STEP256 đã được so SHA byte riêng trên Drive, không công khai trọng số.
- Primary EVAL64 theo `mA>0 && mB>0`: **A=4/64, B=3/64, C=38/64**. Hiệu ứng dữ liệu B−A −1,5625 điểm % (CI bootstrap 95% −9,375 đến +6,25); hiệu ứng mục tiêu C−B **+54,6875 điểm %** (CI +43,75 đến +64,0625) *trên 64 lexical family thuộc bốn shared semantic templates*, một seed. Không có bằng chứng đủ cho chuyển giao qua template cấu trúc mới hoặc suy luận tổng quát. `entity_location` C chỉ 1/16; `rule_constraint` C 16/16, không đồng đều.
- Secondary `BLIND96` đã chấm 96/96 bằng AI mù về danh tính từng output, **rubric hậu nghiệm không prereg**, không phải rater con người/fresh session hoàn toàn độc lập. SHA blind `e032e55c8f0e1e9efe87948c7fb67af5c4e648df89a32483e91a5e9d5588620f`; SHA scores `a5694690a7df8743009987bc0413c49d9951309bc00df0e670fde0cac54dae09`; score hash đã khóa ở commit `1a78ca28b64149518d61b86a55150278e2283279` **trước** khi mở mapping. Kết quả free-generation đúng đầy đủ A=4/32, B=4/32, C=8/32; toàn bộ 16 câu đúng thuộc `rule_constraint`. Không thay primary bằng thang chấm mới. Gold/outputs/mapping và EVAL private giữ riêng, không đưa lên GitHub.
- Lưu trữ cuối: `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_EXPLORATORY_FINAL_ARCHIVE_MANIFEST_AND_D1_BRIDGE_DESIGN_HOLD_20261113.json`; báo cáo lịch sử `docs/research/ttm-small4m-fact-conditioning/TTM_FC01_ABC_ONE_SHOT_INDEPENDENT_SCIENTIFIC_REVIEW_AND_SINGLE_SCOPED_ADJUDICATION_20261113.md` và `docs/research/ttm-small4m-fact-conditioning/TTM_FC01_BLIND96_AI_SCORING_FROZEN_POSTHOC_SINGLE_ADJUDICATION_20261113.md`. Báo cáo cũ trạng thái PENDING/không chấm vẫn được giữ để bảo toàn chronology; manifest này **đóng hồ sơ** chứ không xóa lịch sử âm tính/thiếu hụt.
- **Cầu nối D1 mới — DESIGN ONLY:** `docs/research/ttm-small4m-fact-conditioning/TTM_FC01_D1_BRIDGE_STRUCTURAL_OOD_FREEGEN_MULTISEED_PREREG_DESIGN_V1_20261113.md` và machine-readable `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_D1_BRIDGE_PREREG_V1_MACHINE_READABLE_DESIGN_HOLD_20261113.json`. Đề cương tách cấu trúc TRAIN/EVAL (4 category×4 skeleton OOD×16 worlds =256 paired families), **greedy free-generation** 2 điều kiện/family, 5 seed cố định ×3 arm, primary C−B với sign-flip một phía và gate theo nhóm. Đạt **26/26 source-only consistency checks tự soạn**, không phải independent scientific/power review. Chưa tạo dataset/gold, parser thực hay training mới; no GPU/TEST. Bất kỳ sửa đổi phải có amendment có nguồn gốc trước outcomes.
- Quyết định tích hợp: **`GO_FC01_ARCHIVE_AND_D1_BRIDGE_DESIGN_ONLY; HOLD_D1_SCIENCE`**. Giao thức D1 lịch sử 512 văn bản **không chỉnh sửa**, `D1_CONFIRMATORY=HOLD`, `TEST_Q1Q2=SEALED`, `FC02_CAPACITY=NOT_OPENED`, `DEV32=CLOSED`, **main chưa merge**. Bước tiếp: `TTM_SMALL4M_D1_BRIDGE_SOURCE_ONLY_INDEPENDENT_PREREG_REVIEW_AND_GO_HOLD_NO_GPU`.


## L0017 — 2026-11-14 — D1 Bridge V1 independent HOLD và gói sửa đổi V2 AM01–AM06 — HOLD thiết kế xác nhận

- Loại: **SOURCE_ONLY_INDEPENDENT_PREREG_REVIEW_RECEIPT_AND_V2_PROSPECTIVE_AMENDMENT**. Reviewer AI trong phiên mới tự nhận độc lập, không phải human/externally verified; chấm **`HOLD_REVISE_BEFORE_PREREG`** trên 6/6 trục R1–R6, 12 findings F01–F12, bắt buộc AM01–AM06. Frozen V1 scientific HEAD `25a19daea9f664e14f83d7df2cf8265ffaea4ecd`, 6 Git blob source PASS (metadata GitHub; không có independent local byte-hash ở reviewer). Hai tệp reviewer do owner bàn giao đã được kiểm SHA-256 trên byte đính kèm: report `7369882b5615785628bd93b006157423f2b8377e265e3c3098429eabd60ab97c`, JSON `21c1e07b13ce1cd39d77200247b5f1a6c9fbbd49fffa7f90821c9a429f28034b`; cả hai lưu nguyên vào `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md` và `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json`.
- Hai CRITICAL là F01 AST semantic equivalence/non-overlap chưa được hiện thực, F03 action parser và adversarial QA chưa có. F05/F06 sign-flip n=5 thiếu power/giả định, crossed seed×skeleton bootstrap; F08/F09 ACL/rights/leakage; F10–F12 resume AdamW sau moment, khả thi Free T4 và chênh compute B/C đều là MUST-FIX. **Không** ghi AST/real parser/custody/resume là PASS.
- Gói V2 **mới, không sửa V1**: `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_SINGLE_PACKET_AM01_AM06_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md` và `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_AM01_AM06_SINGLE_PACKET_PREREG_DESIGN_HOLD_20261114.json`. Đặc tả typed AST + finite-state semantic equivalence; typed action oracle + deterministic adversarial parser; exact one-sided binomial sign test trên **12 seed (k≥10/12, alpha=.05)** thay magnitude sign-flip năm seed; seed×skeleton crossed bootstrap mô tả; category guard khai báo pilot-informed; ACL custodian/rights probes; positive-moment resume QA và budget đầy đủ. Thay đổi n seed được nêu công khai là **amendment trước D1 outcomes**, không giả kết quả nghiên cứu cũ.
- Với 12 seed, **dự kiến** 36 arm-runs, 9.216 optimizer steps và 18.432 generations; **chưa thực thi**. One-sided sign-test có giả định independence của training randomness và claim có điều kiện trên **16 skeleton OOD cố định**; power và Free T4 feasibility chưa được independent review. `mean(Δ)≥10pp` chỉ là gate mô tả, không phải statistical test của ngưỡng 10pp.
- QA nguồn-only mới do **cùng tác giả V2**, 44/44 positive contract checks và 9/9 negative mutations (thiếu seed, sai p, negation, lộ gold ACL, bật GO, overlap AST, budget, resume, review verdict) PASS_SCOPED; mã `tools/pilot_t4/fc01/ttm_d1_bridge_v2_source_only_contract_qa_20261114.js`, receipt `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_SINGLE_PACKET_SOURCE_ONLY_QA_AND_HOLD_20261114.json`. Đây **không** phải QA độc lập hoặc bằng chứng AST/parser runtime; **V2 design vẫn HOLD chờ distinct independent source review**.
- Phán quyết một lần: **`D1_BRIDGE_V2_DESIGN=HOLD_PENDING_DISTINCT_V2_SOURCE_REVIEW` · `D1_BRIDGE_SCIENCE=HOLD` · `D1_EXISTING=HOLD_UNMODIFIED` · `TEST_Q1Q2=SEALED` · `FC01_EXPLORATORY=CLOSED_PASS_SCOPED` · `FC02=NOT_OPENED`**. Không tạo TRAIN/EVAL/gold, không train/GPU, không merge main, không micro-permit. Bước tiếp: `TTM_SMALL4M_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`.


## L0018 — 2026-11-14 — D1 Bridge V2 distinct HOLD → V3 một gói hợp đồng nguồn — design HOLD / science HOLD

- Reviewer AI ở chat riêng báo **`HOLD_REVISE_BEFORE_PREREG`** cho V2: 7/7 GitHub blob metadata source pins PASS tại `750533c1c2945594d827c886aaa275c49fb980d7`; 11 issues `D1V2-01…D1V2-11`, cả AM01–AM06 HOLD. AI independence self-attested, không phải human được xác minh. Bằng chứng gốc bytes đã kiểm SHA-256 và Git blob GitHub khớp: report `f482d9855b16bed2bc764e63c2d986259b8f94bd9bb1f65e30b145f5e5e23cae`, receipt `52168ae7c523d1999388e9a2de211e10a940050b15b935a856c383c62c12c04f`; lưu tại `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_DISTINCT_AI_SOURCE_REVIEW_20261114.md` và `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V2_DISTINCT_AI_REVIEW_RECEIPT_20261114.json`.
- V3 là phiên bản nguồn mới, **không sửa V1/V2**: `docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_PREREG_DESIGN_AND_OWNER_HOLD_20261114.md` + machine `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_INTEGRATED_SOURCE_CONTRACT_D1V2_01_11_DESIGN_HOLD_20261114.json`. AM01: typed reachable-state trace/bisimulation thay final-action-only; AM02: oracle A/B, parser grammar, witness không bắt sinh; AM03: **integer signed D_s** (zero nonpositive) + 12-seed sign test; AM04: integer thresholds **ΣD≥308**, category Δ≥39 và C correct≥192; AM05: isolated AST-only overlap auditor và privacy ACL/rights gates; AM06: parent/T1 source pins, nonzero-moment AdamW resume source QA và Free T4/paid $0 feasibility HOLD.
- Dự kiến **12 seed ×3 arm ×256 updates=9.216 updates và 18.432 generated outputs**, **không chạy trong operation này**. V3 chỉ source-only contract: `tools/pilot_t4/fc01/ttm_d1_bridge_v3_source_only_contract_qa_20261114.js`, kiểm chính hợp đồng cùng tác giả **PASS 57/57 + negative mutations 13/13**; biên nhận `artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_SINGLE_PACKET_SOURCE_ONLY_QA_AND_OWNER_HOLD_20261114.json`. QA này không thực thi AST checker, parser, ACL hoặc runner; không gán PASS cho actual nonoverlap, rights, independence hoặc Free T4.
- Phán quyết duy nhất cho V3: **`HOLD_PENDING_DISTINCT_V3_INDEPENDENT_SOURCE_REVIEW`** ở mức design, **`D1_BRIDGE_SCIENCE=HOLD`**, `D1_EXISTING=HOLD_UNMODIFIED`, `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`. Không tạo dữ liệu/gold, không GPU/training/reseed, không merge main, không chia micro-permit. Bước tiếp: `TTM_SMALL4M_D1_BRIDGE_V3_DISTINCT_NEW_CHAT_PREREG_SOURCE_REVIEW_SINGLE_GO_HOLD_NO_GPU`.

