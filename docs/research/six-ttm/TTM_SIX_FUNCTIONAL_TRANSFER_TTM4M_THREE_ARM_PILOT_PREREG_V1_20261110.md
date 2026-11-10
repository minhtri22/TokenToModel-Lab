# TTM × SIX — TTM-Small-4M: pilot ba nhánh chuyển giao chức năng (thiết kế v1)

**Mã:** TTM_SIX_G1_EXPLORE_NO_SIGNAL_ARCHIVE_AND_TTM_FUNCTIONAL_TRANSFER_PILOT_DESIGN  
**Ngày:** 2026-11-10  
**Trạng thái:** DESIGN_ONLY / SOURCE_GROUNDED / CACHED_TEACHER_QA_PASS / STUDENT_TRAINING_NOT_EXECUTED / NO_SCIENCE_PERMIT.  
**Loại kết luận dự kiến:** exploratory engineering screening; KHÔNG phải G1 confirmatory và KHÔNG được phát hành quyết định khoa học G1 gốc.

## 1. Kết luận thí nghiệm Qwen trước và lý do sửa hướng

G1 nguyên bản: FEASIBILITY_HOLD_ARCHIVED, TEST riêng tư tiếp tục niêm phong, science lock HOLD. Phạm vi Qwen→Qwen original, frozen manifest 128/64/64, v1e adjudication và tất cả receipt giữ nguyên. Không nghiên cứu thêm witness/production broker trong pilot này; không đọc original G1 TEST, TTM original VAL/TEST, không dùng TinyStories raw hoặc chạy lại Qwen.

Pilot Qwen exploratory tại commit `a48e423c07c8205d97e832484bf959f768542af1` đã được kiểm toán số học, với MAE trên 4 nhóm DEV:
- A→P=0.0655379602073582;
- direct source→teacher probe=0.06182712847813694;
- TRAIN mean=0.06755050653737271;
- group shuffle median=0.06551105905056755.

Phán quyết `EXPLORATORY_NO_SIGNAL` chỉ cho phương pháp A→P đó. Một QA **post-hoc** mới trên cùng ZIP (KHÔNG chạy model) cho thấy **template-only** dự báo score teacher Qwen1.7B bằng trung bình từng trong 4 mẫu câu TRAIN có DEV MAE = **0.05202296104592581**: thậm chí tốt hơn direct source probe. Điều đó có thể phản ánh shortcut template; KHÔNG chứng minh tất cả phản ứng Qwen chỉ chứa template. Vì DEV 16 mẫu đã được dùng và quan sát để chọn thiết kế mới, nó không còn là một held-out confirmatory set. Pilot mới mang nhãn `REUSED_EXPLORATORY_DEV` và không báo p-value/power hay generalization claim.

## 2. Câu hỏi mới và dữ liệu

**RQ-pilot:** từ *cùng checkpoint* TTM-Small-4M đã huấn luyện, việc học thêm hai chiều phản ứng chức năng Qwen1.7B có cải thiện **DEV next-token NLL trên chính tokenizer TTM** so với tự huấn luyện trên text hay không? Và loại bỏ nuisance template bằng thống kê TRAIN-only có tạo thêm lợi ích so với distillation raw response hay không?

**Nguồn prompt:** đúng **64 câu hư cấu mới**, từ 16 tình huống × bốn template, do mã nguồn original exploratory Qwen sinh; 12 nhóm TRAIN = 48 câu, bốn nhóm DEV = 16 câu; không TEST. Chia nhóm, thứ tự, raw prompt và SHA đều bất biến. Không thêm/tái chọn câu khi thấy kết quả. Mọi teacher target đều lấy từ **ZIP Qwen đã thu**, tuyệt đối không nạp lại hai teacher. Các tensor:
- `source_features.npz` hidden `[64,1024]` (lưu chẩn đoán, KHÔNG làm teacher target của ba nhánh);
- `target_features.npz` hidden `[64,2048]` (không bắt buộc cho training); `probe` `[64,2]` là hai log-likelihood contrast của Qwen3-1.7B dùng chung cho B/C.
- ZIP SHA256 `6f98560117219cf3cecc37fb87ff562a784fe82238d9b2d831cbda7634488d9f`;
  manifest SHA256 `ae86b8e847e74c97b7f69d88a08f133902173bc4c4df104f413447c1cd6fa40d`;
  Qwen extractor SHA256 `9688deb1d1157c93fb7090e5b1c12ea4bc56ed0dedadb0597d84ceb4e68e82eb`.
- Qwen source weights and target weights were **owner-reported SHA-pinned**; assistant independently checked source/manifest/tensor/metric arithmetic, not raw Qwen weight bytes or Colab GPU transcript. No new teacher call permitted in this pilot.

**BPE:** reuse frozen TTM TRAIN-only tokenizer vocab 2048, not Qwen tokenizer. Tokenize each **full authored prompt** once using the TTM frozen BPE. Require exact tokenizer manifest and file SHA from TTM pilot receipt; fail closed if unavailable; do NOT reconstruct BPE from private corpus. Minimum 2 tokens, max 256 tokens, round-trip encoding, no truncation or resplitting, no token ID out of range. Preserve all prompt punctuation and trailing spaces exactly as in the authored source; never add end-space automatically (original TTM prompt-adherence diagnostic found this to be a confound).

## 3. Checkpoint TTM đúng dòng gốc

- Primary parent: **TTM original T4 step 1280**, not EmbeddingGemma2 A/B/C/D or step2048. Drive known folder: `MyDrive/TTM/ttm-small-pilot/ttm_small4m_step1024_to1280_exploratory_v1/checkpoints/step_1280/`.
- `checkpoint.pt` expected **SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`**, `READY.json` SHA256 `eb89d0a797451187ed20956d1f0097e9a8b9539da8eeaa92960e2a8508c9095f`; historical independent QA `PASS_29_CHECKS_SCOPED` in TTM original 1024→1280 adjudication. The assistant located the Drive folder via connected metadata but has **NOT read back checkpoint raw bytes** today. Runtime must rehash checkpoint and READY before even constructing the student.
- Exact P02 Transformer architecture: `src/p02/transformer_core.py` Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; 3,749,376 parameters, layer=4, width=256, heads=4, context=256, tied input/output embedding (read actual checkpoint config rather than using old P02 synthetic defaults). Check model `state_dict` strict load and dimensions and frozen tokenizer SHA.
- New run **forks weights only** into three experiments; this is *new dataset adaptation*, **NOT** the original T4 step 1281 continuation. Keep original checkpoint, AdamW, scheduler, RNG and READY **immutable**. Create **new** identical AdamW init and identical seeds for A/B/C; do not misrepresent original optimizer/RNG continuation. No write to PR#13, original main, old Drive checkpoint or `lineage.md`.

## 4. Ba nhánh một ngân sách

| Nhánh | Cùng input và backbone | Objective phụ |
|---|---|---|
| A — LM baseline | Original TTM step1280, 48 TRAIN prompts | `L_A=CE_next_token`; không dùng teacher |
| B — direct functional transfer | Cùng trạng thái ban đầu và lịch mẫu | `L_B=CE+0.1*MSE(head(h_last), z_train(r_teacher))` |
| C — SIX-inspired nuisance-controlled transfer | Cùng trạng thái ban đầu và lịch mẫu | `L_C=CE+0.1*MSE(head(h_last), z_train(r_teacher - mu_train_template))` |

Trong đó `h_last` là `model.final_ln` ở **token thực cuối cùng** của prompt (không phải right-padding). Một tuyến tính `Linear(256,2)` khởi tạo giống hệt cho B/C; không nạp teacher lúc train hoặc inference. Hai nhánh dùng cùng hai teacher response floats **chỉ trên TRAIN**; C trừ `mu_train_template[t,j]` tính bằng 12 nhóm TRAIN × bốn template, sau đó chia độ lệch chuẩn residual trên TRAIN. B trừ global mean TRAIN rồi chia std TRAIN. Không dùng DEV để fit normalization, template table, loss weight hay checkpoint selection. `sigma` nhỏ/hằng → STOP. C dùng **bảng 4×2** rút từ chính dữ liệu TRAIN, phải báo cáo riêng 8 số và hạn chế công bằng thông tin so với B; không được tuyên bố riêng SIX causal representation hoặc cross-domain transfer.

**Mô tả đúng mức:** C là một *SIX-inspired task-conditioned functional residual*, không phải tái triển khai phương pháp căn chỉnh SIX G1 A→P đã FAIL screening. C giữ lại thay đổi giữa các tình huống sau khi loại hiệu ứng trung bình của bốn template. Đây là một giả thuyết mới cần được thử trên TTM, không kế thừa PASS từ SIX.

**LM labels:** cho chuỗi token `ids[0:L]`, input là toàn bộ `ids`; loss label `ids[1:L]+[-100]`, bỏ vị trí cuối; cross-entropy mask `-100` trên right-pad, tính theo số token hợp lệ. Dùng `last_nonpadding_position=L-1` để lấy head. P02 attention causal cho phép right-pad mà không ảnh hưởng các vị trí trước padding; không dùng token cuối của batch padded nhầm lẫn. No chat template, no EOS insertion, no raw vocab KL.

## 5. Budget và ngăn so sánh lệch

- Một Colab Free Tesla T4 nếu được cấp; **không có quyền chạy trong nhiệm vụ thiết kế này**.
- **12 epochs × 6 batches/epoch = 72 optimizer updates/nhánh**, mỗi batch = hai *nhóm* × bốn template = tám prompt, mỗi nhóm TRAIN xuất hiện chính xác 12 lần. Tổng 576 sequence exposures/nhánh; cùng 72 batch-id và tokenized labels, không shuffle độc lập riêng theo arm.
- FP32, AdamW mới `lr=1e-4`, betas=(0.9,0.95), weight_decay=0.01, grad clip1.0, training seed `20261112`; no hyperparameter search, no early stopping theo DEV; same scheduler `none` cả ba nhánh.
- Three-arm model weights identical at update0. A has LM-only head usage; B/C add same `256→2` linear auxiliary head (514 parameters), only for training/diagnostic. Report this parameter difference and optionally strip head for teacher-free LM inference. No Qwen load or training; memory <12 GiB goal, hard stop 12GiB reserved, cumulative maximum 1,200 seconds across three arms and single one-shot session. Timeout is best-effort in Colab; no production watchdog claim.
- Exact same all-train input, same number of LM labels, group-exposure schedule, optimizer steps, seed, starting weights, dtype and compute instrumentation; capture actual time/tokens/VRAM/gradient stats per arm. A/B/C new RunIDs distinct from all original TTM scientific RunIDs; original science lock cannot authorize this transfer pilot.
- No Google Drive writes until new explicit pilot owner execution approval and a new output namespace; if enabled, it must not overlap G1 or TTM original checkpoints. Do not enumerate/scan unrelated Drive files.

## 6. DEV metrics, counterexamples và quyết định hữu hạn

One post-train evaluation at exactly step72 (also evaluate unmodified parent as read-only diagnostic). DEV groups stay 4. Report per-group & pooled token-weighted `DEV_NLL` in TTM vocabulary for A/B/C, and `gain_C_vs_A=(NLL_A-NLL_C)/NLL_A`. Report B/C probe-head raw MAE and normalized within-template residual MAE on the same 16 DEV prompts. Reconstruct C raw probe prediction by `template_mu_train + train_residual_std*head_C`; B by `train_global_mu + train_std*head_B`.

**Strong shortcut controls:**
1. Template-only teacher baseline from 12 TRAIN groups: DEV raw-probe MAE **0.05202296104592581**; no TTM/Qwen hidden input.
2. TRAIN-global mean baseline `0.06755050653737271`.
3. In evaluation, compare B/C raw teacher-score prediction to template-only 0.05202; check per-template and per-scene residual error. Do not claim semantic teacher alignment when merely reproducing four templates.
4. If C helps only on one DEV group or its auxiliary MAE does not beat template-only, report limitation; no p-value or selective resplitting. Due to observed DEV leakage from previous screening, all findings remain post-hoc exploratory.
5. Optional source-hidden/target-hidden CKA is **NOT** a training target/selection metric; avoid repeating Qwen G1 A→P.

**Finite exploratory decision (candidate, before any TTM training):**
- `EXPLORATORY_FUNCTIONAL_GAIN_CANDIDATE` only if (i) C improves token-weighted DEV NLL at least **1% relative** vs both A **and** B, (ii) C raw teacher-score MAE improves at least **1%** vs B and template-only baseline, and (iii) C improves group NLL vs A in at least **3 of 4 groups**.
- `EXPLORATORY_NO_CLEAR_GAIN` when valid run fails one of these criteria; never call G1 original FAIL.
- `TECHNICAL_STOP` when pinned source, teacher tensors, checkpoint, tokenizer, split, number of steps or memory budget fails.
These thresholds are **screening heuristics** for the new experiment, not proof of significance or transfer generalization. They must not change after results.

## 7. QA cần làm trước Colab; exit hữu hạn

**CACHED_QWEN_READONLY_QA** completed by an independent new Python preflight (not a new model run): exact source/manifests, 64 tensors shape & finite, all 16 groups, all 64 SHA, TRAIN-only template baseline and std. Actual checkpoint READY bytes, tokenizer BPE and TTM 3-arm trainer are **NOT yet material-verified/implemented**. Do not claim `READY_TO_RUN` until these are sourced, source-pinned, code audited and approved.

**Single integrated next batch, not micro-gates:** implement one student runner + Colab notebook with (1) checkpoint/READY/tokenizer exact pins, (2) no-Test paths, (3) equal-arm initialization, (4) train-only normalization, (5) negative QA for group leakage, padded last-token, wrong SHA, DEV labels in optimizer, and tensor tampering, (6) compact receipt, READY-last/no overwrite, (7) independent source QA, then one *separate* owner pilot execution approval. Nothing in this design authorizes GPU training.

**Final:** `ORIGINAL_G1=FEASIBILITY_HOLD_ARCHIVED` · `PREVIOUS_QWEN=EXPLORATORY_NO_SIGNAL` · `NEW_TTM_PILOT=DESIGN_ONLY` · `PARENT_CKPT_1280=HISTORICALLY_PINNED_NOT_REHASHED` · `CACHED_QWEN_DATA_QA=PASS` · `NEW_TTM_TRAINING=NO` · `PRIVATE_TEST=SEALED` · `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_SIX_TTM4M_THREE_ARM_RUNNER_SOURCE_IMPLEMENTATION_SINGLE_INTEGRATED_OFFLINE_QA_AND_OWNER_PILOT_APPROVAL` — source-only/CPU first, then owner decides one T4 execution, not a return to G1 production gates.
