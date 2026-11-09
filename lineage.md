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

## L0017 — 2026-11-09 — TTM-Small-4M gốc: huấn luyện tiếp 1.024 → 1.280, tín hiệu VAL dương (thăm dò)

- Loại: **SCIENTIFIC_LANGUAGE_MODEL_CONTINUATION_EXPLORATORY**; kết quả **PASS_EXPLORATORY_VAL_TRAINING_SIGNAL_MATERIAL_VERIFIED**, không phải kết quả xác nhận mới và không phải QA sinh ngôn ngữ. ID L0013–L0016 đã sử dụng trong nhánh nghiên cứu độc lập EmbeddingGemma2; không sửa hoặc gộp các kết quả đó vào TTM gốc.
- RunID `ttm_small4m_step1024_to1280_exploratory_v1`, xuất phát **duy nhất** từ checkpoint T4 gốc bước 1.024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Chủ dự án cho phép Colab Free Tesla T4 2026-11-09, khóa thực thi SHA-256 `39d61f0012b41497ac5dd406dea6d0f6040c7391ff9942c254c1331d9c643730`. Khôi phục AdamW (52 trạng thái), scheduler, sampler, RNG, GradScaler; FP16 microbatch8, LR floor 3e-5. **256 optimizer steps × 4.096 TRAIN targets = 1.048.576 exposures mới**; bản ghi 1.024 bước đầu trùng hoàn toàn với log gốc.
- Đánh giá VALIDATION giữ nguyên **256 truyện/61.122 token mục tiêu**, mốc 1.152 chỉ chẩn đoán; mốc 1.280 được chọn trước. NLL gốc 1.024 **3.5223388568740495**; 1.152 **3.511285912623514**; 1.280 **3.498089026735425**; chênh `NLL1024−NLL1280=+0.024249830138624417` (giảm ~**0.6885%**). Khoảng tin cậy bootstrap theo truyện 95% **[0.02170874671893396,0.026568311029801738]**, 1.000 lượt seed20261109 theo runner đã ghim: cận dưới > 0 → `TRAINING_HELPFUL_SIGNAL` đúng tiêu chí thăm dò.
- Kiểm toán vật liệu độc lập: checkpoint bước 1.152 và 1.280 tải nguyên bản từ Drive, SHA khớp READY, progress khớp và liên tục; checkpoint 1.280 SHA-256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; optimizer state 52/52 ở step1280, scheduler step1280, LR 3e-5 và toàn bộ trạng thái hồi phục hiện diện; log 1.280 bản ghi, 256 bản ghi mới đúng ngân sách. `CLAIM` SHA `af3e5b269e2e2d306d8dab1f12d4a2be8cc5303bb6bdd36686e04e6cda39765b`; `RESULT_UNADJUDICATED` SHA `bf5e19daa017d5872750c6324913048335e3098e8d071ba0b5f94941a7dc4795`. Biên bản: `artifacts/qa/ttm-original1280/TTM_T4_ORIGINAL_1280_INDEPENDENT_MATERIAL_SCIENCE_ADJUDICATION_20261109.json`.
- **Giới hạn bắt buộc:** một lần chạy, trên VAL đã được sử dụng trong nghiên cứu trước; CI là số đã lưu từ runner đã ghim, **chưa tái tính độc lập từ loss từng truyện tại mốc 1.280**, và chưa suy luận lại đầy đủ trên CPU. TEST 64 đã tiêu thụ từ trước và **không mở lại**. Không chứng minh mạch lạc, bám prompt, khái quát hóa hoặc hiệu quả triển khai. EmbeddingGemma2 A chỉ tham khảo, B/C/D không tham gia.
- Bằng chứng/trọng số riêng tư: [thư mục Drive mốc 1.152 và 1.280](https://drive.google.com/drive/folders/137ClmIGTH4pq_peBgD-dORJbwRrz3biw). Không đưa checkpoint, per-story scores, token TRAIN/VAL hoặc TEST lên GitHub. Giữ `PR13=HOLD_FOR_MERGE_REVIEW`, `main` nguyên trạng. **Bước khoa học tiếp theo:** đánh giá chất lượng sinh nhỏ có đối chứng 1.024 vs 1.280 bằng cùng prompt/seed và cùng cấu hình suy luận, tránh mở lại Q1/Q2 V1/V2 và không dùng TEST; chỉ sau đó mới quyết định mở rộng huấn luyện hay thay đổi dữ liệu.
