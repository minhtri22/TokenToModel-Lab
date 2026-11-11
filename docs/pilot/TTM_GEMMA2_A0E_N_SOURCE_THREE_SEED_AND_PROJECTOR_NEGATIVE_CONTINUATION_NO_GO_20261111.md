# A0E — Báo cáo tiếp tục: official N 3 seed và projector negative control

**Operation:** `TTM_GEMMA2_A0E_FINAL_OWNER_CUSTODY_SIGNATURE_AND_N_SOURCE_MATCHED_NULL_EVIDENCE_SINGLE_READBACK`  
**Ngày:** 2026-11-11 · **Mode:** SOURCE-ONLY CPU / NO MODEL FORWARD / NO TRAIN / NO GPU  
**Phán quyết:** `NO_GO_HOLD` · `T4_2X2=HOLD`.

## 1. Các cổng PASS đã đóng — KHÔNG chạy lại

A0D official source, 1.917/50 mapping, A0E SimVerb Cambridge publisher-byte parity và lexical roster 138/37 đã PASS. Bản input SHA audit 20/20 và negative T1 fail-closed trước đó giữ nguyên. `main`, `lineage.md`, L0020/L0021 không thay đổi. Không dùng lại TEST/H768/OOD256.

## 2. Kết quả mới: official nonpretrained N source — PASS có phạm vi

GitHub Actions [run 43019314812](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43019314812) thành công trên CPU, với `torch=2.10.0+cpu`, `transformers=5.19.0`, official `EmbeddingGemma2TextModel`, `config.json` SHA b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3. Khởi tạo độc lập toàn bộ text model bằng seed 61031/61032/61033. Kiểm shape `262144×512`, pad row zero và fingerprint kiến trúc 413 tensors. Hash **chỉ** input weight `float32le`, không lưu checkpoint hoặc weights:

| Seed | SHA256 full official input source |
|---|---|
| 61031 | `4a5553ee294a08d4dc03a552169930998827b6d16a23ccd80dfc128ae82fe826` |
| 61032 | `edbb8c89304eb35722f78efe186626341a25147bb5fd457079060443d326ca3c` |
| 61033 | `a78c59a1fe0584e67c3011be71975e11048a3a5904a49bd23a05d0aae0fc6aaf` |

Artifact ID `13853569172`, ZIP SHA `e3485fc38ea6fe79ae9ed24d95277fed95ede549524d8df2946f4a9f3d4950d4`, receipt JSON SHA `6dcc578ab812ec2884a1ec9c372fcfe5b70ec4c3233e9605b77afa9e7212f115`; kiểm lại ZIP và JSON từ artifact. **PASS nguồn N-CPU, chưa phải PASS N-A/N-C bốn nhánh**: actual 1.917 T1 mean-pooled N rows, matched projection và tensor N-C per-seed chưa được đóng băng. CPU owner với torch 2.11 có thể cho SHA khác 2.10; không tự cho qua mismatch.

## 3. Kết quả mới: cơ chế gradient không phụ thuộc phá cấu trúc cặp từ

Phép thử toán học đọc đúng candidate P donor SHA `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`, 1.917 hàng đầu vào, projector 256×512, lấy 120 hàng đại diện không dùng nhãn. Thực hiện **phản xạ trực giao toàn cục** trên nullspace của projector (P_0) để tạo (X'). Điều này giữ nguyên pairwise Gram (XX^T) và projected input (XP_0^T), nhưng với một upstream gradient cố định:

`dL/dP = G^T X` trong khi `dL'/dP = G^T X'`.

Sai số initial projected output `2.3592239273e-16`, Gram relative `8.8376391266e-16`. Relative projector-gradient difference `1.5336064`. Một perturbation giả định `0.0005` làm output divergence tương đối `0.0262439`. **Không optimizer step, không model forward và không NLL**.

Quan trọng: phép phản xạ giữ nguyên quan hệ cosine / Gram giữa cặp từ, **không hủy ngữ nghĩa**. Kết quả chứng minh chênh gradient có thể xảy ra chỉ do biểu diễn tọa độ mà projector trainable nhìn thấy. Không được coi đây là đối chứng null P-C/N-C hoặc bằng chứng nhân quả ngữ nghĩa. Kết quả củng cố nhu cầu khóa frozen-projector negative control trước khi giải thích `D_origin`.

## 4. Manifest và người giữ nhãn

Người giữ nhãn độc lập chưa được bổ nhiệm/ký; public gold SimVerb vốn có thể đã nằm trong dữ liệu pretraining donor. Mẫu custody vẫn `UNSIGNED_HOLD`, không tự ký.

Runner CAUSAL6 hiện hữu SHA `51b15ebde7587dcad9a880116ab4c2cc605132cb0ac54ea03af05c7d12bac612` có arms `RR-F/RP-F/RR-A/RP-A/OR-F/OP-F`, không phải `P-A/P-C/N-A/N-C`. Chưa có A0E runner, optimizer/sampler/scorer pin và A0E checkpoint admission. Không gọi CAUSAL6 là runner A0E.

Đã tạo gói readback fail-closed `TTM_GEMMA2_A0E_N_SOURCE_CUSTODY_NULL_SINGLE_READBACK_20261111.zip` SHA `3d539bb7408f58bfdfb4f7b6d3c7740c9f41613630eee8745a4629385a50ba21`. Checker PASS ở kiểm nguồn N/negative toán học nhưng **giữ `NO_GO_HOLD` cho khoa học**. Không chứa raw TRAIN, donor tensors hoặc SimVerb labels.

## 5. Một phán quyết duy nhất

`A0D=PASS` · `A0E_SOURCE=PASS` · `A0E_INPUT_QA_20_OF_20=PASS_PRESERVED` · `N_OFFICIAL_SOURCE_3_OF_3=PASS_SCOPED` · `PROJECTOR_ALGEBRAIC_NEGATIVE=PASS_SCOPED` · `N_MAPPED_AND_P_N_NULL=HOLD` · `GOLD_CUSTODY=HOLD` · `RUNNER_SCORER=HOLD` · `SCIENCE_ADMISSION=NO_GO_HOLD` · `T4=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_A0E_OWNER_PRIVATE_N_T1_3SEED_PN_MATCHED_NULL_AND_GOLD_CUSTODY_FINAL_ONE_PACKET`.

Một gói duy nhất cần hoàn tất: người giữ nhãn độc lập ký + giới hạn truy cập; xác minh quyền raw TRAIN/VAL; official 3 N mapped rows (giữ version/seed đúng pin); kiểm P-C/N-C geometry và morphology/frequency cùng projector; đối chứng frozen-projector; khóa four-arm runner/scorer/optimizer/checkpoint. Sau đó mới có thể ra GO/NO-GO riêng cho GPU. Không chạy GPU lúc này.
