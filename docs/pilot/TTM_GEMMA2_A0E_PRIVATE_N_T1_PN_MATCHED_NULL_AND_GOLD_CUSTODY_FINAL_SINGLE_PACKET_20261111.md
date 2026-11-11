# TTM GEMMA2 A0E — Private N/T1 3-seed, P/N matched-null và Gold Custody

**Operation:** `TTM_GEMMA2_A0E_OWNER_PRIVATE_N_T1_3SEED_PN_MATCHED_NULL_AND_GOLD_CUSTODY_FINAL_ONE_PACKET`  
**Ngày:** 2026-11-11 · **Nhánh:** `research/ttm-gemma2-token-alignment-pretraining-causality-20261111`  
**Phạm vi:** CPU / source-control QA **không** model.forward, training, GPU, TEST, H768, OOD256 hay gold-score.  
**Quyết định duy nhất:** `NO_GO_HOLD`; `T4_2X2=HOLD`. Không thay đổi tiền đăng ký ban đầu.

## 1. Đã thực hiện mới

Từ file nguồn PRIVATE gắn trong môi trường xử lý của ChatGPT (không phải readback Windows owner), sử dụng đúng bản donor `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`, `transformers==5.19.0`, `torch==2.10.0+cpu`. Không tải trọng số pretrained mới. Thực hiện official **random untrained** full text-model initialization cho ba seed khóa sẵn, kiểm full table 262144×512 SHA trùng CI source-only `43019314812`. Ánh xạ T1 theo hàm mean donor-ID gốc của TTM với tokenizer official pinned; `1.917 mapped / 50 multi ID / 130 incomplete UTF-8 / 1 EOS / 0 invalid`.

Cùng dùng projector `256×512` đúng SHA `9fdd433da0e728f969278cd89242a9df36b3e3e6b155821c9968b5e6d661c2b1`; P pretrained source `2048×512` SHA `b6b0d3cb9d4f33b8d7d63269d296d2001e946706948d71cb4f357ab7cf5b2122`. Dữ liệu tần suất chỉ đọc TRAIN trong package cũ.

| N seed | N-A T1 source SHA256 | N-C null SHA256 | P-C null SHA256 |
|---|---|---|---|
| `61031` | `9fd58fb914e1ffccebbc735ef8d633feecf965ba99efcd96c5b7a2503aeaf9e6` | `004be5fa5611291ef806a0b2de0e91de4a25d25fc490e85547233c40d6ccbf64` | `e96f2d55ed1e02003c06012fd0345da260aab1fb3864f844155621e4d6ee2fd1` |
| `61032` | `6d9c535397aef5fee11a7ceee4a562b10f1ad78b947fbb7cdc8dfc349a822a43` | `85d671f32d4f16e4a898f1369dfc6056d7b3fad6d68e4147764b7a843f911c12` | `30ad3136a00f9e26f8469a6dab5509289b8f258a7a8681d28ca1bdc18ac3b053` |
| `61033` | `e6746ab9766c820e64ebb7bfbe78507fad1aeb91e0111ab6324ec0d8c5cfe02f` | `bfc63f5bf39563dbc5fb6ca0b638bbd54456f43a9511e34878f3f9e67838bc13` | `6c7d8f6fac478be11b0f57c94976ab438f61911f929aabafe5609df3d0a052fb` |

P-C/N-C dùng các null seed `51031,51032,51033`. Cả **6/6 source transforms đạt trong-nhánh**: covariance relative Fro ≈ `2.6e-15`, projection drift FP32 tối đa `1.2e-7`, row norm drift tối đa `1.2e-7`; residual top-10 overlap thấp hơn `0.036`. Cả hai nguồn dùng cùng projector ban đầu. Phần biến đổi A0B được tái xây dựng độc lập, **chưa chứng minh chính xác từng byte giống source A0B cũ**. Không tuyên bố thay đổi semantic labels đã được xác nhận.

**Độc lập QA:** 16/16 receipt checks PASS, negative altered-covariance rejected fail-closed. Mã private SHA256 `07ea6ff2111ca36e964c51a4a04c208bd041ac02cc6578c81ba4f25c4fbf7c29`; receipt SHA256 `a8f7a1d232f8edf579af52cd4e73959b3b8a51cbd3bd1beaf628b6f56b4f1cd5`; checker SHA256 `5f3630ec300670818a18b6efa6ebcd82459b3d6d471d50a308d09cd73334d78d`. Chỉ công khai aggregate và hash.

## 2. Nút thắt khoa học phải giữ HOLD

**P và N KHÔNG matched cross-origin:** tỷ lệ norm trung vị P/N = `2.2103–2.2129`; tỷ lệ tổng trace covariance P/N = `4.7741–4.7801`. A/C trong mỗi nguồn MATCHED không chứng minh P/N có cùng scale hay training dynamics. Không hợp thức hóa việc sửa scale/khối lượng nguồn sau khi xem outcome; thiết kế cần owner reviewer quyết định amend trước khi quan sát NLL.

**Frozen-projector negative:** các source A/C giữ `XP₀ᵀ` bằng nhau tại khởi tạo khi chiếu cố định; với trainable projector gradient có thể khác. Đây là PASS về kiểm tuyến tính nguồn, không phải thử nghiệm frozen-projector có forward/NLL hoặc bằng chứng semantic causality.

**Independent gold custody:** Cambridge original score publicly available, không có người giữ nhãn độc lập được bổ nhiệm hoặc chữ ký; mẫu `A0E_GOLD_CUSTODY_UNSIGNED_NOT_VALID_FOR_T4.json` vẫn `UNSIGNED`. Niêm phong hiện tại không loại trừ việc donor có thể thấy benchmark SimVerb-3500 từ trước.

**TRAIN/VAL rights:** TinyStories khai báo CDLA-Sharing-1.0; quyền owner đối với raw source, full near-duplicate và nguyên gốc story membership chưa hoàn thành. Full official pretrained safetensors mới đối chiếu metadata, không rehash raw weights và raw-row extraction trong lượt này.

**Runner/scorer:** Đã khóa mã nguồn scorer `ttm_a0e_fourarm_independent_scorer_v1.py` Git blob `88ea6af212b2ebaab60e4c208390113882611f34`; runner **chỉ là preexecution contract** blob `5ffc150238c7c9f0058d940b4637456c5c5bcc79`, chưa có full training implementation, checkpoint/optimizer/sampler/VAL roster approved. GitHub Actions [43046304992](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43046304992) PASS two synthetic positive/negative source-only fixtures; không chạy NLL thật, không đọc VAL.

## 3. Gói evidence duy nhất

Private ZIP `TTM_GEMMA2_A0E_PRIVATE_N_T1_PN_MATCHED_NULL_FINAL_ONE_PACKET_20261111.zip`, SHA256 `2c38e3d70ed302f11973247818a7cc5841adc03ed28e8b5bc8619902c464ba31`, gồm 8 tài liệu/script và manifest SHA. Không chứa trọng số, raw T1, TRAIN/VAL hoặc gold scores. Kèm script PowerShell 5.1 **read-only** để owner tự kiểm ZIP và từng thành phần; mã PS chưa được kiểm parser Windows CI.

Biên bản đỏ/gọn: [A0E source-only integrated adjudication](../../artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_A0E_PRIVATE_N_T1_THREE_SEED_PN_NULL_AND_GOLD_CUSTODY_SINGLE_PACKET_ADJUDICATION_20261111.json).

## 4. Final

`A0D=PASS` · `A0E_SOURCE=PASS` · `N_OFFICIAL_3_OF_3=PASS` · `N_TO_T1_3_OF_3=PASS_SCOPED` · `P_C_N_C_6_OF_6_INTERNAL_NULL=PASS_SCOPED` · `P_VS_N_CROSS_SOURCE_SCALE=MISMATCH_HOLD` · `INDEPENDENT_GOLD=UNSIGNED_HOLD` · `RUNNER_SCORER=SOURCE_FIXTURE_ONLY` · `SCIENCE_ADMISSION=NO_GO_HOLD` · `T4=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_A0E_OWNER_CROSS_ORIGIN_SOURCE_MATCHING_AMENDMENT_CUSTODIAN_SIGNED_RUNNER_FINAL_ONE_GO_NO_GO`. Chỉ **một** quyết định hậu kiểm độc lập về cross-origin normalization hoặc matched-init strategy (trước khi xem outcomes), chữ ký custody thật, raw rights và full runner binding. Nếu thiếu bất kỳ điều kiện bắt buộc nào, giữ HOLD và **không chạy GPU**.

Không merge vào `main`, không thêm `lineage.md` cho source QA, bảo toàn L0020/L0021, không tạo L0022.
