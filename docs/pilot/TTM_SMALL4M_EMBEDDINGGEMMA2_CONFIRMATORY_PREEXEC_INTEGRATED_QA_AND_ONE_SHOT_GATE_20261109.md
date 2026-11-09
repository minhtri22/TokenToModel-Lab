# TTM-Small-4M × EmbeddingGemma 2 — Kiểm định tích hợp trước thực thi và cổng one-shot

**Ngày:** 09/11/2026  
**Công việc:** `TTM_SMALL4M_EMBEDDINGGEMMA2_CONFIRMATORY_EVALUATION_PREEXECUTION_INTEGRATED_QA_AND_ONE_SHOT_GATE`  
**Nguồn:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` tại `e1a84125383174263ff39a2fb8c84b136d8d3410`.

## 1. Phán quyết

**`PASS_SCOPED_INTEGRATED_CPU_SYNTHETIC_QA` · `HOLD_ONE_SHOT_SCIENTIFIC_EVALUATION_NOT_AUTHORIZED`.**

Đã kiểm tra thực thi tích hợp trên CPU với **118/118 kiểm thử tổng hợp PASS**, bao gồm sinh cửa sổ context=256, EOS=256, mask=-100, bảo toàn số nhãn, không ghép ngữ cảnh các truyện, đối chiếu bộ chấm NLL theo token/truyện, quy tắc bootstrap ghép cặp theo truyện với 2.000 mẫu seed=2026110901 và kiểm tra các đối chứng âm.

Đồng thời đã **nạp bốn checkpoint A/B/C/D thực** trên CPU, giữ chính SHA-256 cố định, và đo hai bộ chấm gốc ↔ độc lập trên **293 nhãn token giả lập mỗi nhánh**. Sai khác NLL/token tối đa **9.87854484e-07**, nhỏ hơn ngưỡng **1e-5**. Không sử dụng GPU, không huấn luyện, không chấm 320 truyện mới, không đọc TEST.

## 2. Hợp đồng cửa sổ và phép chấm được bảo toàn

- BPE train-only 2.048 ID đã khóa, context=256, EOS_ID=256. Mỗi truyện token hóa riêng, nối đúng một EOS, tạo cặp next-token. Cửa sổ đầu tiên chứa tối đa 256 mục tiêu; cửa sổ tiếp bắt đầu từ vị trí token 256 của chính truyện, không có ngữ cảnh xuyên biên giữa truyện. Tổng số nhãn hợp lệ = len(BPE(story)); nhãn padding dùng -100, không đóng góp loss.
- Bộ sinh T4 `windows_for_ids` trong `tools/pilot_t4/integrated/t4_data_pack.py` (Git blob `cdce219f2a2df27e25579f069238d4327c1d7d91`) đối chiếu với bộ sinh oracle độc lập trên các độ dài nhạy cảm **1,2,3,4,7,31,254,255,256,257,258,511,512,513,514,515,768,769,1025** nhãn, đều PASS. Biến đổi ở biên 256 nhãn không bỏ sót hoặc nhân đôi mục tiêu.
- Hàm `val_story_sums()` trong nguồn GPU2048 nguyên bản **cố định vector kết quả 256 truyện** và là tham chiếu số học trên fixture, **không được** trực tiếp đưa vào lượt chấm 320 truyện.
- Bộ scorer riêng `ttm_gemma2_independent_cpu_scorer.py` tính loss bằng CrossEntropy FP64, cộng theo ID truyện và tổng nhãn. Vì forward P02 gốc trả `(logits, loss)` mà scorer cần tensor logits, runner đánh giá phải có wrapper cố định chỉ lấy logits đầu tiên. Không thay logic mô hình hoặc trọng số.
- Kiểm thử tổng hợp 7 truyện/1.549 nhãn so sánh scorer gốc, scorer độc lập và oracle logsumexp per-token: sai khác NLL/token nguồn gốc ↔ độc lập = **5.987753227e-08**; tất cả PASS trong 1e-5.

## 3. Hai lỗ hổng kỹ thuật đã phát hiện (blocking)

**B1 — Chưa khóa ràng buộc membership và cửa sổ trước forward.** Bộ scorer cấp thấp nhận `story_id` 64 ký tự hex được gắn nhãn `NEW_HOLDOUT` mà **không tự kiểm tra** ID đó thuộc đúng manifest riêng tư; nếu đưa lại cùng một cửa sổ thì nó cộng hai lần. Kiểm thử đối kháng đã chứng minh cả hai tình huống trên input tổng hợp. Không thể cấp quyền đánh giá one-shot khi chưa có lớp validator độc lập, kiểm đủ chính xác thứ tự 320 ID, số mục tiêu từng truyện, tổng 75.798 nhãn, không trùng cửa sổ, đúng nguồn/tập đã khóa, không mở TEST; xác minh toàn bộ trước **lần gọi model.forward đầu tiên**.

**B2 — Gần trùng với VALIDATION/TEST lịch sử chưa xác nhận.** Windows independent manifest readback PASS 320 IDs và SHA-256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`, trùng ID với pilot = 0, old TEST bucket = 0. Bộ seal đã báo quét 2.119.489 TRAIN và kiểm near với ứng viên theo 5-word Jaccard>=0.85. Tuy nhiên vẫn **không có bằng chứng** chống gần trùng nội dung với các truyện VAL/TEST pilot cũ. Không mở lại TEST cũ để lấy chứng cứ; cần bằng chứng đã được ủy quyền trước đó hoặc một quyết định về giới hạn phạm vi/ngoại lệ phương pháp rõ ràng, trước khi scoring. Không được âm thầm tự đổi manifest hoặc chọn lại dữ liệu.

## 4. Cổng quyền và những giới hạn không thể xóa chỉ bằng QA

- `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, mã nguồn TRAIN `c5cf5e22...`, VALID `94e43181...`. Dataset card: https://huggingface.co/datasets/roneneldan/TinyStories — giấy phép CDLA-Sharing-1.0. Điều 2 cho phép dùng dữ liệu/tính toán theo Điều 3. Nguồn: https://cdla.dev/sharing-1-0/ . **`INTERNAL_COMPUTATIONAL_USE=PASS_WITH_CONDITIONS`**; không công bố văn bản, token đảo ngược, thành viên private, checkpoints hay kết quả từng truyện. Quyền phát hành sản phẩm/artefact khác là cổng riêng. Thẻ nguồn không chứng minh mọi quyền sở hữu nội dung của từng truyện.
- Không có bằng chứng chắc chắn rằng donor EmbeddingGemma 2 chưa học nguồn TinyStories. Một bộ checkpoint được chọn sau VALIDATION không trở thành lặp huấn luyện độc lập chỉ nhờ chấm dữ liệu mới. Kết quả tương lai, nếu có, chỉ chứng minh tín hiệu của **bốn checkpoint cố định trên đúng miền holdout này**, không chứng minh nguyên nhân hoặc khả năng ứng dụng thực tế.

## 5. Hợp đồng one-shot bất biến — CHƯA cấp quyền thực thi

- **Pin:** manifest private SHA256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`; 320 ID riêng tư; 75.798 target; nguồn gốc và T1 BPE đã ghim; source original core SHA256 `0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e`; scorer `de6ab9652bb690a6e967e752b9367f5755674a23a6c4b2fcb45941274612dfe1`.
- **Checkpoints 2048:** A `ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081`; B `a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c`; C `ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d`; D `db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e`.
- **Một lần duy nhất:** bộ đánh giá CPU phải ghi CLAIM độc quyền trước khi bất kỳ forward nào xảy ra; nguồn, danh sách thành viên, thứ tự cửa sổ, masks, counts, checkpoint hashes và đầu ra phải qua kiểm toán; chấm đủ bốn model trước khi báo cáo thống kê; lỗi hoặc chạy dở phải lưu biên bản, **không âm thầm chạy lại**, không tự dùng GPU.
- **Quy tắc thống kê:** NLL theo token = tổng per-story token loss / 75.798; hiệu số A−C, B−C, D−C; paired-story bootstrap 2.000 lần bằng `numpy.default_rng(2026110901)`, lấy phân vị 2,5/97,5%; cả 3 cận dưới >0 = PASS tín hiệu trên checkpoint cố định. Có một cận dưới ≤0 khi toàn bộ evaluation hợp lệ = FAIL tín hiệu. QA/nguồn thất bại = INVALID/HOLD, không tính FAIL mô hình. Không thay tiêu chí sau khi nhìn kết quả.

**Quyết định tích hợp:** `HOLD_ONE_SHOT_DISPATCH` cho đến khi **B1** được đóng bằng mã và QA fixture độc lập, **B2** được phán quyết phương pháp mà không mở TEST hoặc thay tập niêm phong. Hãy gộp hai việc trong **một lượt review**, không phân thành các cổng cấp phép nhỏ. Khi không có block mới và được chủ dự án phê chuẩn, mới có thể thực thi một lượt CPU riêng. Lượt này **không** cấp quyền tự động.

## 6. Bằng chứng và quản trị

- `tools/embeddinggemma2_swap/ttm_gemma2_confirmatory_preexec_integrated_qa_20261109.py`: SHA256 `786b002cb16139eb033c0b25c5b98b11135bf58baa144d03f8b48be4b30f2263`, 118/118 synthetic PASS.
- `tools/embeddinggemma2_swap/ttm_gemma2_preexec_four_arm_cpu_synthetic_scorer_qa_20261109.py`: SHA256 `ae506a6da2bd674812b6a63a104e245a1f1ff679d407e0127c2f24287c7a30c6`, 4/4 arm PASS trên dữ liệu tổng hợp.
- `tools/embeddinggemma2_swap/ttm_gemma2_preexec_scorer_adversarial_contract_probe_20261109.py`: SHA256 `e859334c02501b5132f2dff6cd003aab86d1e2117b9f1c541b036fae3754241c`, xác minh B1 trên fixture.
- Báo cáo JSON: `artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_CONFIRMATORY_INTEGRATED_PREEXEC_AND_ONE_SHOT_GATE_20261109.json`.

Không merge; không sửa `main`, không chấm new holdout, không chạy TRAIN/TEST, không dùng GPU, không ghi `lineage.md` (science outcome cũ kết thúc ở L0016).

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SINGLE_BATCH_PRE_FORWARD_BINDING_AND_CONTAMINATION_SCOPE_ADJUDICATION` — khóa validator trước forward và ra một quyết định độc lập về giới hạn gần trùng với OLD VAL/TEST mà không mở TEST; sau đó quyết định GO/HOLD cuối cho một lượt CPU.
