# TTM-Small-4M × EmbeddingGemma 2 — Tiền đăng ký tích hợp 4×3 về thông tin donor ngoài Ridge projection

**Ngày:** 2026-11-10. **Operation:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SEMANTIC_FACTORIAL_4X3_INTEGRATED_PREREG_SOURCE_AND_RESOURCE_DECISION`.

**Quyết định tích hợp:** `METHOD_PREREG_FROZEN_V2` · `REAL_TENSOR_GEOMETRY_QA=PASS` · `H768_SELECTION_SOURCE_PINNED_NOT_SEALED` · `RESOURCE_HOLD` · `TRAINING_NOT_AUTHORIZED`. Không chạy inference/training khoa học, không tạo CLAIM, không sửa L0017/L0018/L0019 hoặc main.

## 1. Vì sao hợp đồng 4×3 dự thảo V1 phải thay đổi trước CLAIM

L0019 đã kết luận `PASS_SCOPED_DONOR_MAPPING_ALIGNMENT`, tau_D +0.0785658100 với CI95 [+0.0709965265,+0.0863988495], trên H512 512 truyện/119856 nhãn. Tuy nhiên projector Ridge đã được fit với 1917 token đúng rồi dùng chung ở real/perm: L0019 không cô lập thuần ngữ nghĩa tiền huấn luyện.

Dự thảo ngày 2026-11-10 tại `TTM_SMALL4M_EMBEDDINGGEMMA2_DONOR_SEMANTICS_VS_PROJECTOR_ALIGNMENT_MULTISEED_DESIGN_ONLY_20261110.md` đề nghị spectral null với **fit Ridge độc lập trên 1438 token neo**. Tôi đã kiểm định nguồn thật (donor candidate SHA `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`, TTM bước1024 SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`), **không gọi model**. Null spectral bảo toàn hiệp phương sai toàn cục (relative error ~3.41e-15) nhưng **Ridge không cân bằng**:

| Đối chứng (một diagnostic seed không phải science) | Fit 1438 normalized RMSE | Audit 479 normalized RMSE |
|---|---:|---:|
| Donor thật PT-REAL | 0.61546 | **0.96117** |
| Donor thật PT-PERM | 0.73837 | 1.13518 |
| Spectral NULL-REAL | 0.72506 | 1.14723 |
| Spectral NULL-PERM | 0.72718 | 1.13247 |

Sai khác audit này làm lợi thế downstream có thể xuất phát từ projector init. **REJECT** V1 như một phép cô lập donor semantics. V1 vẫn lưu lại như lịch sử thiết kế, không phải science FAIL, không ghi lineage. Không tiêu thụ nhãn VAL/H512/TEST/H768 trong diagnostic; chỉ dùng 1917 embedding rows và E0 bước1024.

## 2. V2: đối chứng projector- và covariance-matched null

Giữ bốn nhánh và ba seed, nhưng **thay đổi đúng cơ chế của null** và mục tiêu suy luận:

- Lấy donor thật X [1917,512], projector Ridge P [256,512] **đã khóa trong candidate gốc**; Z=XPᵀ [1917,256].
- X_parallel=Z(PPᵀ)^(-1)P; R=X−X_parallel. Dùng Q là cơ sở trực chuẩn của [1,Z] theo hàng; phân tích R=QC+UΣVᵀ, U trực giao với Q.
- Sinh U_new trực chuẩn với Q (seed khóa), tạo X_null=X_parallel+QC+U_newΣVᵀ. Nhờ đó X_null Pᵀ=XPᵀ, **trung bình hàng, hiệp phương sai cột toàn cục và phổ centered toàn cục** được giữ đến sai số số học.
- **Không refit projector riêng** theo arm; tất cả bốn nhánh dùng đúng ma trận P đã fit trên 1917 cặp thật, nhưng nay projector là một **biến số giữ cố định tại step0** giữa pretrained và null, không phải một yếu tố khác nhau.
- Các nhánh sử dụng projector trainable trong huấn luyện, cùng cơ chế forward, optimizer/seed/schedule và trainable param-count. Donor rows (real/null) frozen; 131 fallback rows giữ E0 như CAUSAL6; không đổi TTM hidden=256/vocab=2048/context=256/4 blocks/4 heads/untied head.

| Arm | Frozen row features | Assignment | P at step0 | Model adaptation |
|---|---|---|---|---|
| `PT-REAL` | X EmbeddingGemma 2 thật | Đúng token | P chung | Full |
| `PT-PERM` | X thật | π_s trên 1917 mapped rows | P chung | Full |
| `NULL-REAL` | X_null dual-matched | Đúng token | P chung | Full |
| `NULL-PERM` | X_null dual-matched | Cùng π_s | P chung | Full |

**Biên chứng minh mới, hẹp hơn và chặt hơn:** Có hay không **tín hiệu hữu ích trong phần cấu trúc donor còn lại ngoài embedding sau Ridge đã fit** giúp quá trình thích nghi? Nếu PASS, đó là bằng chứng về **donor residual structure beyond locked initial Ridge projection**, **không** phải chứng minh toàn bộ ngữ nghĩa tiền huấn luyện; phần đã được P giữ lại và thông tin E0 dùng fit P vẫn tồn tại trong cả bốn nhánh.

**Nguồn tensor QA thực** từ private candidate, chỉ công khai số tổng hợp: projector rank256; phần dư rank256; `max_abs(X_null Pᵀ − XPᵀ) = 2.4980018e-16` (FP64) và `9.6857548e-08` (FP32); relative covariance Fro error `2.03763e-15`, mean max-abs `9.02e-17`. Loss-agnostic bước0 RMSE với E0 ở PT-REAL và NULL-REAL **giống hệt 0.02530948**. Synthetic fixture PASS. **Giới hạn:** row norms không trùng từng token (real p10/50/90 ~0.99928/0.99951/0.99973; null ~0.94695/0.99269/1.04038), các moment bậc cao vẫn khác; phải báo cáo, không nói `FULL_GEOMETRY_IDENTICAL`. Không dùng null này để chứng minh donor pretraining semantics toàn cục.

## 3. Tiền đăng ký bốn nhánh × ba seed

Cả ba seed cùng checkpoint base step1024 pinned `cb9857...71b`, donor `c9fc7...c3`, nguồn PACK T4 TRAIN `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`, manifest `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`. Mỗi arm 2048 steps × 4096 nhãn TRAIN (8.388.608 lượt nhãn/arm); 12 arms = 100.663.296 lượt nhãn. Chính xác chế độ CAUSAL6: FP32, AdamW lr1e-4, betas (0.9,0.95), eps1e-8, wd0.1, gradient clip1, micro≤8, không schedule tune, early stopping, validation chọn checkpoint; mỗi seed 4 arm **chung một lịch TRAIN** sample with replacement từ 2691 T4 TRAIN windows, mask đảm bảo 4096 target labels mỗi optimizer update.

Các seed là số đề xuất được **chốt trong bản contract V2 này**, không thay đổi sau quan sát NLL:

| Replicate | model | null U_new | token π | TRAIN schedule |
|---|---:|---:|---:|---:|
| S1 | 2026111101 | 2026111111 | 2026111112 | 2026111113 |
| S2 | 2026111102 | 2026111121 | 2026111122 | 2026111123 |
| S3 | 2026111103 | 2026111131 | 2026111132 | 2026111133 |

Hoán vị nonidentity trên 1917 mapped rows, cùng π_s trong PT-PERM/NULL-PERM; fallback bất động. Null U_new được random độc lập theo replicate. Số seed 3 là giới hạn nghiên cứu cố định; **không** cho lựa chọn lại seed theo NLL. Cùng 4 arms/mỗi seed từ cùng base, sao chép untied head, khởi tạo full model/trainer giống nhau trong seed. Sampler schedule khác nhau giữa seed và được SHA niêm phong trước CLAIM; 3 RunID phân biệt theo seed. Bảo toàn optimizer+RNG+sampler cursor trong READY 256/512/.../2048 và chính sách resume exact, không auto rerun sau CLAIM.

## 4. Ước lượng, confidence interval và PASS/FAIL

L(a,s) là NLL token-weighted trên **cùng một H768 mới** (768 truyện) của arm a và replicate s.

`delta_PRE,s = L(PT-PERM,s) − L(PT-REAL,s)`.

`delta_NULL,s = L(NULL-PERM,s) − L(NULL-REAL,s)`.

`tau_residual,s = delta_PRE,s − delta_NULL,s` (**PRIMARY interaction**).

`gamma_real,s = L(NULL-REAL,s) − L(PT-REAL,s)` (**co-primary direct check**).

Để không công bố PASS từ hiệu ứng chỉ làm nhánh hoán vị xấu đi, **PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE** đòi đồng thời: tất cả 12 arms/khoá nguồn/READY/H768/independent QA PASS; cả ba `tau_residual,s >0`, cả ba `gamma_real,s>0`; hai CI95 percentile từ **2.000 paired story bootstrap** (same H768 indices for all 12 runs) của **mean over three fixed seeds** đều có cận dưới >0. Bootstrap seed khóa `2026111199`, CI theo story **có điều kiện trên ba training seeds đã chọn**, không phải CI quần thể seed. Secondary chỉ NLL arm, delta per seed và hình học bước0; không sửa gate sau dữ liệu. Nếu complete valid but gate fails → `DONOR_RESIDUAL_SIGNAL_NOT_ESTABLISHED_SCOPED_FAIL`; nếu source/resource/READY/H768/preflight incomplete → `HOLD`, không ghi scientific FAIL.

Một PASS mới vẫn **không** chứng minh pure semantic pretraining, vì việc ngẫu nhiên hóa là phần dư ngoài P, độ lớn row norms và higher-order moments khác; có thể là hình thái/tokenization và tiến hóa gradient. Tránh gọi đó là independent multi-donor pretraining replication: vẫn chỉ một backbone và một checkpoint donor.

## 5. Nguồn H768 đã khóa cách chọn, chưa niêm phong dữ liệu thật

- TinyStories `roneneldan/TinyStories` pinned revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64` (licence provenance T1: CDLA-Sharing-1.0), `TinyStories-valid.txt` SHA256 `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4` và TRAIN SHA `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`; parser T1 Git blob `3ef500ddd8259153e7e3d4602915a51b7060a40f`, BPE blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`.
- T1 split SHA `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`, T1 BPE manifest `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Exclude exact story hash of T1 TRAIN2048, VAL256, historical TEST64, L0017 consumed 320 (membership SHA `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`) and L0019 H512 (private membership SHA `544c30b470f5e8718ba35fe016b0f52cac95e559020eae2806e1ff7291a03661`).
- Select eligible unique SHA(raw story) using immutable `DOMAIN = ASCII("TTM_GEMMA2_SEMANTIC4X3_H768_V1_20261110") || NUL`, rank `SHA256(DOMAIN || lowercase story SHA hex)`; take first exactly 768 in sorted rank, **no retry/replacement** after audit.
- Decode only selected H768 and authorized TRAIN/VAL old stories, not old TEST/H320/H512; audit 5-word-casefold shingle Jaccard >=0.85 **within H768, versus old 2048 TRAIN and 256 VAL**. Historical 320/512/64 TEST only exact hash exclusion; disclose their unaudited near-overlap and donor-pretraining contamination.
- Build new `H768_WINDOWS_PRIVATE.npz`, `H768_MEMBERSHIP_PRIVATE.json`, public seal SHA and counts in project `_tmp` only after all audits pass. Do not access H768 labels/loss until all 12 READY final exist. No model.forward during data seal. Source code fixture completed `PASS_4_CHECKS`; **actual H768 768 IDs, windows, targets and SHA not established**; the Windows managed command runtime does not permit executing the source selector here. **`H768=RULE_FROZEN_NOT_SEALED`**, no fabricated receipt.
- Data rights/contamination: in-domain only, donor pretraining overlap unknown, old consumed sources near-dup only exact exclusion.

## 6. Tài nguyên: quyết định HOLD trước CLAIM

12 arms thuộc F trainable (~3.88M parameters), each full READY checkpoint size CAUSAL6 observed **52,947,341 bytes**. Eight READY/arm means `12×8×52,947,341 = 5,082,944,736 bytes` (~**4.73 GiB**) chỉ riêng checkpoint; input ZIP trước ~61,350,758 bytes, thêm H768/metadata và headroom. Vì vậy **>=4GiB Drive cũ không đủ**. Freeze **minimum owner-verified FREE DRIVE >=6.0 GiB** ngay trước CLAIM, đồng thời preflight must project 12×8 checkpoints plus inputs/logs, require free quota > expected mandatory writes + 1GiB margin. Không xóa/chuyển dữ liệu khoa học cũ để ép điều kiện; thay vì khẳng định có 6GiB sau CAUSAL6, **DRIVE_FREE_CURRENT=UNKNOWN**, nên resource=HOLD.

Compute chỉ Colab **Free** Tesla T4 (1 GPU), CUDA, Pytorch available, VRAM thực >=14GiB theo amendment đã ghi, synthetic forward/backward memory <12GiB, FP32; không hứa T4 lúc tương lai. 24.576 optimizer updates trên 12 arms (gấp hai lượt cập nhật của CAUSAL6), checkpoint 256 steps để cho phép resume **cùng RunID với audit READY**; không tái chạy tự động nếu consumed claim. Không dùng CPU/XPU local để train, không dùng GPU trả phí, không đổi budget ngầm.

## 7. Ranh giới phê duyệt

Bản này chốt tiền đăng ký **cơ chế, seed, lịch lấy mẫu, nguồn SHA, quy tắc H768 và ngưỡng tài nguyên**, nhưng **chưa cấp quyền science run**. Null nguồn và H768 selection đều có mã source-only, cần đóng gói để chạy trước CLAIM và kiểm thử với real-source. Null real tensor QA **PASS**, H768 fixture QA **PASS**, real H768 seal NOT_EXECUTED, Free T4 GPU hiện tại UNKNOWN, Drive free UNKNOWN.

Trạng thái: `CONTRACT_V2=FROZEN_PRECLAIM_CONDITIONAL` · `SPECTRAL_NULL_V1=REJECTED_GEOMETRY_IMBALANCE` · `DUAL_MATCHED_NULL=PASS_REAL_GEOMETRY_CPU` · `H768=RULE_FROZEN_NOT_SEALED` · `RESOURCE=HOLD` · `CLAIM=NOT_CREATED` · `TRAINING=NOT_EXECUTED` · `LINEAGE=L0019_UNCHANGED`. GGUF/application vẫn backlog.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SEMANTIC4X3_H768_REAL_SEAL_AND_RESOURCE_PREFLIGHT_SINGLE_BATCH`, chỉ niêm phong H768 + kiểm source/Drive/T4 để có quyết định trước CLAIM; **không tự huấn luyện** nếu chưa có quyết định owner riêng.
