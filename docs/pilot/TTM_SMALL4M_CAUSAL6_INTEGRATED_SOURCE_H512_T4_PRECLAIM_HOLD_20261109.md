# TTM-Small-4M × EmbeddingGemma 2 — Causal6: nguồn tích hợp và biên bản HOLD trước CLAIM

**Ngày:** 09/11/2026. **Operation:** `TTM_SMALL4M_EMBEDDINGGEMMA2_CAUSAL6_SINGLE_INTEGRATED_SOURCE_H512_SEAL_AND_FREE_T4_PREFLIGHT_THEN_ONE_SHOT`. **Nhánh:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`.

## Đã tạo một gói mã tích hợp (chưa commit mã Python trong GitHub)

- `ttm_causal6_h512_seal.py`: cố định chọn **512** truyện từ TinyStories-valid đã pin bằng SHA256, loại trừ chính xác TRAIN/VAL/TEST lịch sử và 320 truyện L0017, không giải mã TEST64; đối chiếu 5-word Jaccard >=0.85 với **2.048 TRAIN + 256 VAL** và nội bộ H512; xuất chỉ private membership, private token-window pack và biên bản SHA công khai.
- `ttm_causal6_colab_free_t4_one_shot.py`: xây 6 arms RR-F/RP-F/RR-A/RP-A/OR-F/OP-F, ridge và Procrustes, hoán vị **sau khi fit phép chiếu trên real** để giữ ma trận P chung, kiểm projected-row multiset, đối chiếu model state và logits với **mã C2048 nguyên bản**, kiểm synthetic CUDA/T4 trước CLAIM. Cùng lịch TRAIN seed `2026110914`, 2.048 bước ×4.096 nhãn/arm (50.331.648 tổng), AdamW đã khóa, FP32.
- `ttm_causal6_independent_readback.py`: tái tính NLL/paired-story bootstrap 2.000 lượt từ per-story private loss, kiểm toàn bộ 6 READY cuối, không gọi lại model.
- `RUN_WINDOWS_H512_SEAL_AND_STAGE.ps1`: một lệnh chuẩn bị trên Windows, kiểm 7 nguồn byte pin, chạy synthetic fixtures, **niêm phong H512 một lần**, CPU parity C2048, sau đó tạo private ZIP trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` để chủ dự án đưa lên Drive.
- `TTM_CAUSAL6_FREE_T4_ONE_SHOT_COLAB_20261109.ipynb`: mount Drive, kiểm ZIP, kiểm T4/Colab Free, preflight, rồi chỉ có một cell thực thi CLAIM+train+independent readback. Không tự động chạy khi thiếu dữ liệu/độ sẵn sàng.

**Gói mã nguồn tạm thời tạo ở phiên chat, chưa được ghi mã lên GitHub.** Sau khi chủ dự án chạy staging trên Windows, toàn bộ mã nguồn sẽ có thể đọc lại theo SHA và commit vào đúng nhánh. Chưa được tuyên bố GitHub đã chứa bộ chạy hoàn chỉnh. Đây là biên bản kỹ thuật, không phải phân xử khoa học.

## Kết quả QA trong phiên chat (không truy cập dữ liệu thật)

| Kiểm tra | Kết quả |
|---|---|
| Cú pháp Python của 3 script | PASS |
| H512 fixture: định hạng, shingle/Jaccard, chống near | PASS 5 |
| Training runner fixture: lịch 2048×4096 và paired bootstrap | PASS 5 |
| Independent reviewer fixture | PASS 3 |
| Notebook: cú pháp các code cells | PASS |
| Public source ZIP integrity | PASS |
| H512 real seal trên Windows | **NOT_EXECUTED** |
| C2048 real checkpoint parity trên Windows | **NOT_EXECUTED** |
| Colab Free Tesla T4 runtime và Drive quota | **NOT_VERIFIED** |
| One-shot CLAIM, training, scoring | **NOT_EXECUTED** |

## SHA của gói nguồn công khai trước staging

- Public source ZIP `TTM_GEMMA2_CAUSAL6_SOURCE_V1_20261109.zip`: SHA256 `6cd7a0dbb6e65894cdae91ff446d0d3d9c60b7ec09fec021384f7473286e0ecc`; không chứa checkpoint hoặc truyện.
- PowerShell stage script tải riêng `RUN_WINDOWS_H512_SEAL_AND_STAGE.ps1`: SHA256 `544a48032438bbba9e3f00796a05fc4f473917fd2fdcb2baa983bd5378d20d75`.
- Seal source SHA256 `698cea87cae43aea65ae66b89de74e7a317658f4d677aa7d932f956dea893e4c`.
- Runner source SHA256 `51b15ebde7587dcad9a880116ab4c2cc605132cb0ac54ea03af05c7d12bac612`.
- Reviewer source SHA256 `e47ef303deb0f30028f14cd4809d44f3dec42c338bf6b99e9c028942d0d5d5ed`.
- Notebook SHA256 `8349f5e13006ad3af5336745e34333ee0fb5a272e9a24c45b3bf6a016b1f88c7`.

**Bảo toàn nguyên hợp đồng nghiên cứu** tại commit `7aa48d8532f1297e67e83c5d39f88213aaecdc08`, `lineage.md` L0018, L0017 checkpoint PASS, L0018 gated32 FAIL, original TEST64, 320 holdout, main và backlog GGUF đều không thay.

## Quyết định trước CLAIM

**`HOLD_PRECLAIM_H512_NOT_SEALED_AND_T4_NOT_VERIFIED`**. Không ghi CLAIM hoặc huấn luyện trên CPU/GPU từ đây; không suy diễn đã có T4 trên Colab khi chưa mở phiên. Không đổi ngưỡng hoặc tự tái chọn H512 nếu near-duplicate gate HOLD.

**Bước thực hiện tiếp theo:** chạy **một script Windows** để niêm phong H512 + kiểm CPU parity, tải private pack lên Drive, chạy **một notebook Colab Free T4** preflight, và chỉ chạy cell CLAIM khi mọi điều kiện PASS. Nếu nguồn H512 hoặc CUDA FAIL, giữ HOLD và bằng chứng; không phát sinh micro-permits.
