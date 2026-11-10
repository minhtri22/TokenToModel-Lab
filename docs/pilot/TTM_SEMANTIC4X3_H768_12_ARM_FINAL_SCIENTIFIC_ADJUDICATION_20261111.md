# TTM-Small-4M × EmbeddingGemma 2 — SEMANTIC4X3 scientific adjudication (L0020)

**Ngày phân xử:** 11/11/2026.
**StudyID:** `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2`.
**Phán quyết khoa học:** `PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE`.
**QA độc lập:** `PASS_INDEPENDENT_12_ARM_STORY_BOOTSTRAP_READBACK`.

## 1. Phạm vi khoa học

Hoàn tất **12 nhánh** (3 seed × 4 arm: PT-REAL, PT-PERM, NULL-REAL, NULL-PERM) × **2.048 optimizer steps**/nhánh = **24.576 steps**, 4.096 next-token labels/update (100.663.296 lượt nhãn TRAIN). Cùng TTM bước 1024, frozen donor EmbeddingGemma 2, cùng projector Ridge khởi tạo, các phép can thiệp giới hạn vào phần dư donor ngoài đầu ra của Ridge. Huấn luyện tuần tự Tesla T4 FP32; chấm H768 **sau khi đủ 12 READY cuối**.

H768 mới được niêm phong theo SHA membership `0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f`: **768 truyện, 1.000 cửa sổ, 186.655 nhãn**; không chấm lại TEST lịch sử, H320 hay H512. H768 cùng miền TinyStories-valid, và tính không trùng gần với holdout lịch sử hoặc donor pretrain chưa được xác minh đầy đủ.

## 2. Kết quả trên H768

NLL nats/target (nhỏ hơn tốt hơn), đọc trực tiếp từ RESULT rồi được frozen independent reviewer tái tính qua per-story loss:

| Seed | PT-REAL | PT-PERM | NULL-REAL | NULL-PERM |
|---|---:|---:|---:|---:|
| S1 | 3.266480321 | 3.351792684 | 3.270955281 | 3.338712294 |
| S2 | 3.266318777 | 3.341063731 | 3.273992748 | 3.333333859 |
| S3 | 3.263203479 | 3.345957666 | 3.264887812 | 3.347593656 |

Định nghĩa khóa: `delta_PRE = NLL(PT-PERM)-NLL(PT-REAL)`; `delta_NULL = NLL(NULL-PERM)-NLL(NULL-REAL)`; `tau_residual=delta_PRE-delta_NULL` và `gamma_real=NLL(NULL-REAL)-NLL(PT-REAL)`.

| Seed | tau_residual | gamma_real |
|---|---:|---:|
| S1 | 0.0175553509 | 0.0044749603 |
| S2 | 0.0154038430 | 0.0076739716 |
| S3 | 0.0000483432 | 0.0016843330 |

**Hai tiêu chí co-primary đã tiền đăng ký:**

- `tau_residual = +0.0110025124`, paired story bootstrap 95% CI **[0.0080061404, 0.0142235373]**, ba seed đều dương → PASS.
- `gamma_real = +0.0046110883`, CI95 **[0.0026581795, 0.0067166239]**, ba seed đều dương → PASS.

Bootstrap **2.000 lần**, seed `2026111199`, ghép cặp cùng story indices giữa 12 nhánh, hiệu NLL token-weighted ratio-of-sums. CI percentile 95% chỉ **có điều kiện trên đúng 3 seed được khóa**; không đại diện cho quần thể training seeds.

## 3. Bằng chứng độc lập và chuỗi nguồn

- `STUDY_CLAIM.json` SHA256 `5c76c4da3d1d1c0532f04a7ff557fd0f8e46279e7e1590dd34cf7801368b47a2` — CLAIM duy nhất, runner pin `a3182549739cda848ce0f7f449b1f1455e06419d72295dcee96f0e8a7822f676`, C2048 source parity PASS.
- `RESULT.json` SHA256 `d60f8e206b20b30a5b83f324427fa0b206a9d00174661419abf2185401022610` — runner hoàn tất, `COMPLETED_PENDING_INDEPENDENT_ADJUDICATION`, kết quả ứng viên PASS.
- `PER_STORY_PRIVATE.json` SHA256 `e51f9b840cd6d9b324257efdda56b781663d488cf47cfc92ced4101de93ebcf2` — ở Drive riêng tư, **không commit**. Đã tự tính lại 12 NLL và hai co-primary với 2.000 bootstrap draws, khớp.
- `INDEPENDENT_READBACK_PUBLIC.json` SHA256 `386ec3bdab72cecc31455998951cc2afbb51bd7e3d9023cbc65027d5dd80a513`, nhận từ Google Drive, kiểm byte và mã SHA trùng owner log, reviewer không model.forward hoặc train lại.
- Frozen reviewer xác nhận **96 READY metadata**, toàn bộ nhật ký START/DONE phù hợp, **12 final binary checksum** và 12 SHA cuối trùng biên bản scoped independent trước đó. Biên bản `all_final_binary_sha256_verified=true`. Adjudicator trước đó đã tự tải/băm lại **12/12 checkpoint cuối**; không cần lặp.
- Chưa chấm lại mô hình sau kết quả, chưa tạo StudyID/CLAIM mới, không công khai dữ liệu loss từng truyện, nhãn H768, donor embeddings hay checkpoint.

## 4. Phán quyết và giới hạn

**PASS chính thức trong phạm vi xác định:** phần cấu trúc donor còn lại **ngoài thông tin ban đầu mà Ridge đã chiếu** có tín hiệu dự đoán hơn đối chứng dual-matched null tại ngân sách/nguồn/holdout đã khóa. Đây là bằng chứng cơ chế bổ sung L0019, **không chứng minh thuần ngữ nghĩa tiền huấn luyện EmbeddingGemma 2**. Đối chứng null chỉ giữ đầu ra chiếu + covariance toàn cục, không giữ row norms/higher-order moments; chưa biết donor pretraining overlap. Dữ liệu vẫn cùng miền TinyStories-valid, chưa chứng minh khả năng tổng quát OOD.

**Giới hạn seed quan trọng:** `tau_residual,S3=0.00004834318450962216` chỉ vừa dương, nên hiệu ứng khác biệt rõ theo seed. Không dùng CI bootstrap theo story để diễn giải CI quần thể seed.

**Quản trị:** giữ nguyên L0017/L0018/L0019, chỉ append L0020; các dữ liệu science private và checkpoint ở Google Drive, không merge main tự động; GGUF/ứng dụng vẫn DEFERRED. Không tự mở seed, training, inference, model serving hay nghiên cứu mới.

**Trạng thái:** `SCIENCE_12_ARM=COMPLETED` · `INDEPENDENT_96_READY_QA=PASS` · `FINAL_ADJUDICATION=PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE` · `L0020=APPENDED` · `MAIN=UNCHANGED`.
