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

## L0013 — 2026-11-09 — TTM-Small-4M × EmbeddingGemma 2: frozen VALIDATION A/B/C/D one-shot

- **Kết quả khoa học (trong phạm vi VAL đã dùng trước đó): `FROZEN_INITIALIZATION_BENEFIT_NOT_ESTABLISHED`**. Lượt so sánh CPU thật đã thực hiện đúng một lần: `ttm_small4m_embeddinggemma2_frozen_val_ab_cpu_once_20261109_v1`. Tiền đăng ký trước khi chấm: commit `46a37bd34299aeda16ebac7e0cf5cbf7f3772624`. QA độc lập trên receipt và loss theo từng truyện: **46/46 PASS**. Không huấn luyện, không dùng GPU, không đọc TEST; không chạy RAG.
- Cùng bộ VALIDATION TinyStories đã khóa: **328 cửa sổ / 256 truyện / 61.122 nhãn hợp lệ**, cross-entropy NLL theo token, CPU float32 và checkpoint đã huấn luyện bước 1024. **A** = TTM-Small gốc (tied), **B** = output head tách trọng số, **C** = input embedding từ EmbeddingGemma 2 thật và adapter ridge 512→256 (chưa huấn luyện), **D** = cùng 1.917 donor vector valid nhưng hoán vị gán token ngẫu nhiên seed `20261109`, đồng thời fit lại cùng ridge 0.01 và giữ cấu trúc/đối chứng.
- **NLL thực đo:** A `3.522338851682218`; B `3.522338851682218` (**A=B chính xác**); C `4.348096266099754`; D `6.443825625799108`. Bootstrap ghép cặp theo 256 truyện, 1.000 lượt, seed `20261109`: **A−C = −0.8257574144**, CI95% `[−0.8423488812,−0.8106557264]`; **D−C = +2.0957293597**, CI95% `[2.0634174828,2.1264773635]`. Điều kiện đã đăng ký yêu cầu cả hai cận dưới >0 để gọi tín hiệu tích cực; chỉ D−C đạt. **Không che hoặc thay nhãn kết quả không ủng hộ lợi ích frozen init.**
- **Coverage theo tần suất trên VALIDATION:** mapped type `1917/2048`; input token hợp lệ `61108/61122` (99.9771%); target IDs thuộc nhóm mapped `60852/61122` (99.5583%). Không nhầm lẫn coverage với chất lượng.
- **Giới hạn:** Đây là đánh giá *mô hình thay embedding nhưng chưa huấn luyện thích nghi* trên tập VAL đã từng dùng cho H1, không phải TEST chưa từng thấy. C tốt hơn D không tự chứng minh pretrained Gemma truyền ngữ nghĩa vì ánh xạ và ridge dùng hình học embedding của chính TTM gốc; kết quả C kém A cũng không bác bỏ mọi thiết kế chuyển giao embedding sau huấn luyện.
- **Bằng chứng bất biến:** checkpoint `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; candidate `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`; dữ liệu `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. CLAIM `ed63d2b72a610237728aaed0e730041f1cfc0750747b97cfa022f4e23c41e506`, RESULT `a5f1b0a0c1c81f543e181d56f0697e73c5c796cbdbf7395f935e58aa6331923e`; private 256-story sums `c0cbc7edf88aeae3fc899896272be0d6dca49606c9a643847153982b3aee77a3`, independent QA `bb3b672e2336e25397ae8095225ba688067d3526f9b0e9b88f4e7096c1dda3c2`. Báo cáo `docs/pilot/TTM_SMALL4M_EMBEDDINGGEMMA2_FROZEN_VALIDATION_AB_CPU_ONCE_ADJUDICATION_20261109.md`. Bằng chứng per-story/token riêng tư không commit công khai.
- **Next:** Không mở huấn luyện mới tự động. Nếu cần kiểm giá trị sau thích nghi, chỉ thiết kế một so sánh nhỏ cùng ngân sách TRAIN giữa A/B/C/D, không dùng TEST; TTM-Small T5 giữ ưu tiên. `D1_G4_R1_R2_R3=DEFERRED`. Bảo toàn H1 T4 PASS và kết quả TEST mô tả L0012.

## L0014 — 2026-11-09 — TTM-Small-4M × EmbeddingGemma 2: 64 bước thích nghi TRAIN ngân sách bằng nhau

- **Kết quả khoa học thăm dò không ủng hộ lợi ích thay embedding trong phương án hiện tại:** `ADAPTED_TRANSFER_BENEFIT_NOT_ESTABLISHED`. Lượt duy nhất `ttm_small4m_gemma2_equal64_adapt_cpu_20261109_v1`; một quyết định 4 arm, không cấp phép vi mô; tiền đăng ký commit `efdc8fa8a3b71fa9e05b26821c22d39f88c3e22f` và nguồn khóa SHA256 `e423daccc678d893947f93c13b2e8a12c8dca3a4875c5546f3a80131cd0d61ca` trước CLAIM/bước tối ưu. QA độc lập **61/61 PASS** (nạp lại cả bốn checkpoint và tính lại VAL theo truyện).
- Bốn arm: A mô hình TTM-Small đã huấn luyện 1.024 bước với input/head tied; B cùng tham số ban đầu, head untied; C bảng donor EmbeddingGemma 2 ánh xạ 1.917 token + ridge adapter 512→256, donor lookup/fallback frozen; D cùng donor vectors nhưng hoán vị giữa các valid token IDs seed `20261109`, refit ridge0.01. **64 AdamW steps × chính xác 512 nhãn TRAIN/bước = 32.768 nhãn mỗi arm**, cùng lịch lấy mẫu TRAIN bất biến SHA256 `f16682b8b9cc2506753296719c8bc124103ef6a65e5fbcf98876bd8476aa82a6`, fresh optimizer và cùng LR=1e-4; số FLOPs không bằng nhau do arm C/D có adapter 512 chiều.
- NLL trên **cùng 256 truyện / 328 cửa sổ / 61.122 nhãn VALIDATION** (tập VAL đã sử dụng ở T4): **A=3.6203496575, B=3.6190452345, C=3.9190499451, D=4.2870530828**. Trước thích nghi A/B=3.5223388517, C=4.3480962661, D=6.4438256258. C cải thiện so với điểm đầu ~0.429, nhưng vẫn kém A/B. A/B xấu đi khi thích nghi theo schedule chung; bảo toàn kết quả không mong đợi này.
- Paired story-bootstrap **1.000 lượt seed 20261109**: **A−C=−0.2987002876**, CI95% `[−0.3099962949,−0.2886758762]`; **B−C=−0.3000047106**, CI95% `[−0.3115587235,−0.2899196944]`; **D−C=+0.3680031377**, CI95% `[0.3559535590,0.3803695708]`. Điều kiện đã đăng ký `CI_lower>0` cho **cả ba** so sánh; chỉ D−C đạt. Không đổi ngưỡng và không loại mẫu sau kết quả. Khác biệt lớn ban đầu của D không được diễn giải thành tốc độ học.
- **Giới hạn:** một seed, VALIDATION đã tham gia nghiên cứu trước, không đọc TEST, không kiểm tra tính tổng quát, không huấn luyện dài hay GQA/RAG; ridge dựa trên embedding TTM gốc nên không chứng minh cơ chế ngữ nghĩa donor. Đối chứng B có thể tách khỏi A sau gradient descent do weight tying khác nhau.
- **Bằng chứng riêng tư trên Drive**: [gói receipts 25.632 byte](https://drive.google.com/file/d/1bnrUq2Ty5zhbGvPo0GC94OkEeGf5OZdy/view) SHA256 `8b6051d3299fbaad43518ea53c829885e9a750298a09f1b8be04c5113eb0f963`; [bốn checkpoint mới 68.510.251 byte](https://drive.google.com/file/d/1IB_hMlnmxNR-OVSXhsP196-H0WJhvHAE/view) SHA256 `115c438f2cc1f3b3c3464b40e3eb87402d38a2c514a5edc178671e2e851927e8`. CLAIM SHA `fa9c2dce53eba66129c1d93368c257848eadc613877e8062f2fcd2a698bb93e8`; RESULT SHA `8d31f890c84a56c4f1a58293eaa2dee9d8ded3e7720599f5b6407f482f83d703`; QA SHA `6634aefb7917c792ff8398be84df0b7c5b2b8df49befda2b5bae77ff380a6405`. Không đăng dữ liệu TRAIN/VAL riêng tư và trọng số lên GitHub.
- **Bản adjudication có đủ giải thích**: `docs/pilot/TTM_SMALL4M_EMBEDDINGGEMMA2_EQUAL64_CPU_ADAPTATION_SCIENCE_ADJUDICATION_20261109.md`. T4 H1 PASS / T4 TEST L0012 và kết quả L0013 trước đó giữ bất biến. **Tiếp theo:** `TTM_SMALL4M_EMBEDDINGGEMMA2_MECHANISM_REVIEW_AND_STOP_GO_DESIGN_ONLY`; không tự chạy thêm training. D1 G4 RAG vẫn DEFERRED; TTM-Small T5 ưu tiên chính.

## L0015 — 2026-11-09 — TTM-Small-4M × EmbeddingGemma 2: GPU 1.024 bước thích nghi tiếp, không đạt lợi ích direct-swap

- **Phán quyết khoa học thăm dò:** `DIRECT_SWAP_1024_BENEFIT_NOT_ESTABLISHED`, sau khi thử đúng một lượt `ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1` trên Colab Tesla T4, `COMPLETED_UNADJUDICATED` được kiểm toán và đối chiếu độc lập CPU `PASS_INDEPENDENT_SCOPED_CPU_REPLAY`. Tiền đăng ký GPU **trước khi chạy** commit `6715c0a46aa30c3e4fee8647d4540d523d26c619` và runner nguồn SHA256 `00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b`; không sửa điều kiện sau khi biết kết quả.
- **Ngân sách xác thực:** A tied TTM, B untied, C EmbeddingGemma 2 token-mapped + ridge adapter, D donor token-association hoán vị. Mỗi nhánh **1.024 optimizer steps × 4.096 nhãn TRAIN** = **4.194.304** exposure; bốn nhánh tổng **16.777.216**. Tất cả **bắt đầu từ checkpoint TTM đã có 1.024 bước** và cùng lịch TRAIN; đây là **1.024 bước thích nghi thêm**, không phải huấn luyện từ đầu. Bốn checkpoint cuối riêng biệt đúng step1024, đầy đủ model/optimizer/loss, readback SHA256 khớp. Lượt thử 64 bước cũ L0014 không bị chạy lại hoặc chỉnh sửa.
- **NLL VALIDATION** (328 cửa sổ, 256 truyện, 61.122 nhãn): A **3.3501216607592945**; B **3.3132221934441275**; C **3.3604018255302230**; D **3.4754170724567890**. C vẫn kém A `0.0102801648` và kém B `0.0471796321`, tuy tốt hơn D `0.1150152469`.
- **Bootstrap ghép cặp theo truyện** 1.000 lần seed `20261109`: A−C `−0.01028016477`, CI95% `[−0.01772555470,−0.00299999132]`; B−C `−0.04717963209`, CI `[−0.05577709696,−0.03894225524]`; D−C `+0.11501524693`, CI `[0.10659841528,0.12345386586]`. Tiêu chí prereg yêu cầu cận dưới **cả ba** >0; chỉ D−C đạt. Không biến lợi ích so với đối chứng donor hoán vị thành tuyên bố tốt hơn TTM gốc.
- **Kiểm định độc lập:** SHA nguồn, dữ liệu, `CLAIM`, `RESULT`, per-story được đối chiếu; 256 loss-sums/truyện tái tính NLL và bootstrap chính xác. Bốn checkpoint cuối tải từ Drive, băm SHA từng tệp thực, nạp `torch.load(weights_only=True)`, kiểm step/RUN_ID/source schedule; suy luận lại trên CPU với evaluator độc lập cho bốn arm, sai khác NLL GPU/CPU lớn nhất **3.72×10⁻⁸**. Đây là re-evaluation độc lập, **không phải tái chạy huấn luyện**.
- **Bằng chứng riêng tư, không ghi dữ liệu token hoặc checkpoint lên GitHub:** [thư mục Drive của lượt chạy](https://drive.google.com/drive/folders/1JeRva6DWqT8b0ltC9R3SIz7ZhXEyuNe4); CLAIM SHA256 `d7e99b831dcb69688e4a1483732f174125f8e1a10d5e73cea5c4ef9efcfb3011`; RESULT SHA256 `46a93c888063c27711541c067d168ded31bbf22f6c46ba6efe45051cdc9c0bec`; private per-story SHA256 `3d23e6d2502060f3b7b134e6247a249dc7dd59f8dff89049764f8841a68f42da`. Checkpoint SHA256 A `95bb69de752bf051958f0d8e19a388528d2cc102f02258c88d756526a9406aa2`, B `8ecca1e181726965d4f6e76c8e725b612706d5242accd408a9386964939191d1`, C `cb77a5c2e435dd8cf1f61259f560a22964bc8c8c06889b0494cb961ed76bc9ac`, D `81003fa2fe194a7e22b30d1b3e330fc65ec0ae486a08511d17c367ec5c25f69f`. Biên bản QA SHA256 `9dc722ae8363fd325118332353396e888faef0f74715eaf976597017b9ad914e`. [Adjudication](docs/pilot/TTM_SMALL4M_GEMMA2_DIRECT_SWAP_1024_GPU_INDEPENDENT_QA_AND_SCIENCE_ADJUDICATION_20261109.md).
- **Giới hạn:** Một seed, VALIDATION đã được tham khảo trong T4 và các thí nghiệm trước, số bước/nhãn bằng nhau **không đồng nhất FLOPs**, và việc tiếp tục từ checkpoint TTM không tương đương huấn luyện độc lập từ scratch. Không đọc sealed TEST ở lượt này; không suy diễn tính tổng quát hoặc ứng dụng sản phẩm.
- **Quyết định tiếp theo của owner theo điều kiện đã định:** **STOP** thêm huấn luyện thay token embedding trực tiếp; **GO_DESIGN_ONLY** với cơ chế `E_original + tanh(a) ⊙ (WE_Gemma − E_original)` (residual/gated, zero-init) của báo cáo cơ chế đã khóa. Không tự chạy thí nghiệm gated mới. TTM-Small T5 tiếp tục ưu tiên; D1_G4_R1_R2_R3 giữ DEFERRED; L0011–L0014 và checkpoint gốc không thay đổi.

## L0016 — 2026-11-09 — TTM-Small-4M × EmbeddingGemma 2: GPU 2.048 bước, tín hiệu thăm dò dương

- **Phán quyết khoa học: `PASS_EXPLORATORY_VAL_SIGNAL_ONLY`, `CONFIRMATORY_NOT_ESTABLISHED`.** Lượt `ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1` hoàn tất trên Tesla T4; mỗi cấu hình A/B/C/D kế thừa checkpoint AdamW bước 1.024, rồi tiếp tục 1.024 bước trên lịch TRAIN chung (2.048 × 4.096 nhãn mỗi cấu hình). Không huấn luyện lại từ đầu, không đọc TEST.
- **Đối chứng VALIDATION** 256 truyện, 328 cửa sổ, 61.122 nhãn: NLL A `3.3132380124`, B `3.3280589053`, C `3.2703167312`, D `3.3920957202`. Chênh lệch A−C `+0.0429212812`, B−C `+0.0577421741`, D−C `+0.1217789891`; bootstrap ghép cặp 1.000 lượt seed `20261109`, khoảng tin cậy 95% tương ứng `[0.0327137748,0.0529380063]`, `[0.0465040707,0.0693839406]`, `[0.1105777101,0.1340138373]`. Cả ba cận dưới dương.
- **Nguồn và kiểm toán độc lập có giới hạn:** tiền đăng ký sửa đổi commit `24d0b7b1d5eea590ba1cfa0d00f74ffcbdd6f72a`, bridge commit `24492886922c7ac92c30ffa7d74f2d41b606a916`, SHA `1f3e01c6e1baf5fcab5d22e41b3c49d309b5dc5f8d2a4cf0fcf5c2fc45728ae6`. Parent CLAIM/RESULT tái băm khớp; lịch TRAIN 1.024 bước đầu trùng cũ. Bốn checkpoint thật SHA-256 A `ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081`, B `a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c`, C `ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d`, D `db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e` đều khớp READY và RESULT; nạp CPU, các bộ đếm AdamW = 2.048, loss 2.048 bước. Dữ liệu per-story SHA `8c64d166c45f03eb114400dddca7f5cf35d90bd336b8b5cc5c90708095f526c7`, NLL và CI tái tính khớp. **Chưa tái suy luận từng token bằng bộ chấm CPU thứ hai.**
- **Giới hạn:** mở rộng sau khi đã thấy kết quả ở L0015 nên không phải thử nghiệm xác nhận, một seed, VAL đã được dùng ở nhiều giai đoạn, bằng bước/nhãn nhưng không bằng FLOPs, chưa chứng minh ý nghĩa ngữ nghĩa donor hoặc khả năng tổng quát hóa. **Không xóa hay sửa phán quyết âm L0015**. Không mở TEST, không tự chạy thêm GPU.
- **Bằng chứng:** [Drive 2.048](https://drive.google.com/drive/folders/1zadSQtNsCm5jG5pMtZPaWeCgsprNS6eg), CLAIM SHA `79987e1f1cc1aefdec1aa869544f1b6e41d6ad757f6ade4e614359d7c4061626`, RESULT SHA `f0cf6edd8481197b87c1c9906a9f48664376ee5055d8994fd864126e4dcedf65`, biên bản `docs/pilot/TTM_SMALL4M_GEMMA2_GPU2048_INDEPENDENT_SCIENCE_ADJUDICATION_20261109.md`, QA `artifacts/qa/ttm-embeddinggemma2/TTM_GPU2048_INDEPENDENT_MATERIAL_STATISTICS_QA_20261109.json`. Dữ liệu/trọng số riêng tư không đưa lên GitHub. `main`, PR #12 và các mốc khoa học trước giữ nguyên.

## L0017 — 2026-11-09 — TTM-Small-4M × EmbeddingGemma 2: xác nhận một lượt CPU trên 320 truyện mới

- **Phán quyết khoa học: `PASS_FIXED_CHECKPOINT_NEW_HOLDOUT_ALL_THREE_CONTRASTS`**. Lượt CPU one-shot `ttm_small4m_gemma2_confirmatory_320_story_four_arm_cpu_once_20261109_v1` chấm đúng **320 truyện chưa dùng để chọn checkpoint, 405 cửa sổ, 75.798 nhãn token mục tiêu**, trên cùng bốn checkpoint A/B/C/D bước 2.048 đã khóa. Không huấn luyện, không GPU, không đọc lại TEST 64 truyện lịch sử; **1.620** model.forward (405 × 4).
- **Kết quả NLL theo nhãn (nats/token):** A `3.3414141970`; B `3.3581664488`; C `3.3086025043`; D `3.4265771699`. C thấp nhất. Các đối chứng đã tiền đăng ký: A−C `+0.0328116926`, CI95 `[0.0237975734, 0.0417115821]`; B−C `+0.0495639445`, CI95 `[0.0396693963, 0.0591997070]`; D−C `+0.1179746655`, CI95 `[0.1080151847, 0.1274724691]`. Ba cận dưới đều **>0**, đạt đúng cổng PASS đã khóa. Bootstrap ghép cặp theo **truyện**, 2.000 mẫu, seed `2026110901`, CI phân vị hai phía 95%; các CI riêng lẻ không phải khoảng đồng thời.
- **Bằng chứng một lượt và kiểm toán độc lập:** nguồn/checkpoint được đóng băng trước CLAIM tại commit `be7a8164cccf75dc5612731de80e8725ca5ed730`. CLAIM SHA256 `90dfa0b098897a090e0b711d15625c16d635d746e6ea46431e57d5f198ba72d0`; RESULT SHA256 `f087faad53286b57a68d64dc182d87c72c2e1934a39a00384fc50119b53f5a94`; per-story evidence riêng tư SHA256 `e79ee58524b3fcc26ea65038611e97010c753ab2daae2970066cb8b7c476bfd6`; 320-story manifest SHA256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`. `INDEPENDENT_READBACK_PUBLIC.json` đã tính lại NLL/CI và xác nhận `PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK` **không chạy lại mô hình**. Chi tiết tại `docs/pilot/TTM_SMALL4M_GEMMA2_CONFIRMATORY_320_CPU_ONE_SHOT_INDEPENDENT_SCIENCE_ADJUDICATION_20261109.md` và `artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_CONFIRMATORY_320_CPU_ONE_SHOT_PUBLIC_ADJUDICATION_20261109.json`. Dữ liệu tư (ID, text, loss theo truyện, weights) chỉ ở máy chủ dự án, không commit.
- **Phạm vi và giới hạn:** PASS về **dự đoán của bốn checkpoint cố định trên tập holdout mới**, không chứng minh do riêng ngữ nghĩa của EmbeddingGemma 2 hoặc lặp qua seed huấn luyện khác. Đã kiểm 320×256 VALIDATION cũ không trùng gần theo Jaccard 5-gram ≥0,85; không mở lại 64 TEST đã chấm ở L0012 và không khẳng định không gần trùng với chúng; dữ liệu tiền huấn luyện donor chưa kiểm chứng, các cấu hình khác số tham số/FLOPs. Giữ nguyên L0015 khoa học âm và L0016 tín hiệu thăm dò. **Không chạy lại one-shot**; không tự mở huấn luyện/triển khai mới.

## L0018 — 2026-11-09 — TTM-Small-4M × EmbeddingGemma 2: residual/gated 32 bước CPU — tín hiệu riêng của donor chưa thiết lập

- **Phán quyết khoa học `GATED_32_STEP_SIGNAL_NOT_ESTABLISHED` (FAIL theo tiêu chí thăm dò đã đăng ký, QA độc lập PASS).** RunID `ttm_small4m_gemma2_zero_gate_residual_32_cpu_probe_20261109_v1` sử dụng đúng checkpoint TTM gốc bước 1.024; B baseline untied **không huấn luyện**; G dùng donor Gemma thật, R dùng donor hoán vị (seed `20261109` và ridge refit), mỗi nhánh G/R cập nhật **chỉ 256 tham số cổng** trong **32 AdamW steps × 512 nhãn TRAIN** (16.384 exposures/nhánh), cùng lịch sampling seed `2026110902`. Step0 logits B=G=R. Không GPU, không TEST lịch sử, không đọc/chấm tập 320 truyện L0017, không huấn luyện lại backbone.
- **VALIDATION cũ 256 truyện, 328 cửa sổ, 61.122 nhãn**: NLL B `3.5223388275`; G `3.5213177127`; R `3.5205936608` (nats/token). **B−G** `+0.0010211148`, CI95 `[0.0007229702, 0.0012893495]` — cận dưới dương. **R−G** `-0.0007240519`, CI95 `[-0.0010824418, -0.0003801699]` — cận dưới âm; R tốt hơn G. Bootstrap ghép theo truyện 1.000 lượt, seed `20261109`. **Không đạt giao của hai điều kiện** tiền đăng ký, không tự tăng ngân sách hay tune theo VALIDATION.
- **Bằng chứng one-shot và độc lập:** PRE-CLAIM nguồn/hợp đồng commit `49d407554485d31abf6ef0ca2ee188b5e1e6366a`, PS51 pre-CLAIM fix commit `c6ce57fcd7fe7e2b569f3f3a0a01e22456846a57`, CLAIM SHA256 `d57c239d54cca10c448e919f36ac052ea70c20ba9c7d03620aff3832b9659fba`, RESULT SHA256 `a3eecadde88fad706411b4596aba7aa4f16ba294105cf4585c9560bf138dd3dc`, reviewer readback `PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK` (stdout SHA `9dfa8e49a515dd1c5b5924241cdb0169b00aedbb0b077b1a5139c802e5fb96a0`), loss per-story riêng tư SHA256 `5ebaa8ee9462bf5b50ae3a82639a9123a8cb0dddacd94d66611bdcee135aa187`; source runner SHA `235816631eedbe212f7f431700024f1e4ae8e470fd5b0cabcdabd78421c815bf`, schedule SHA `a460c39b176ba1ba2211bb8040821afc1bec9d41753979cf3457b00faefe430a`. Bằng chứng chi tiết tại `docs/pilot/TTM_GEMMA2_GATE32_CPU_ONE_SHOT_INDEPENDENT_SCIENCE_ADJUDICATION_20261109.md` và `artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_GATE32_CPU_ONE_SHOT_PUBLIC_ADJUDICATION_20261109.json`. Private checkpoints / per-story không công bố.
- **Diễn giải giới hạn:** G tốt hơn B rất nhỏ nhưng kém R; **chưa chứng minh** tín hiệu donor đúng token vượt đối chứng hoán vị với gate 256 chiều sau 32 bước, không chứng minh donor gây hại chung. VALIDATION đã dùng nhiều lần; refit ridge làm geometry và chuẩn nhiễu G/R khác nhau; một seed. Phán quyết **không thay đổi L0017 direct-swap C2048 PASS xác nhận checkpoint cố định**, không giải thích trực tiếp cơ chế C2048. Giữ backlog ứng dụng thực tế DEFERRED, không huấn luyện lại hoặc mở GGUF.
