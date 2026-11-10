# TTM × SIX — Kết thúc pilot ba nhánh A/B/C (khám phá)

**Ngày ghi hồ sơ:** 2026-11-10  
**Hợp đồng:** `TTM_SIX_TTM4M_THREE_ARM_FINAL_INTEGRITY_QA_EXPLORATORY_ADJUDICATION_AND_ARCHIVE`  
**Source pin:** `d13d2d6c98cdcc32760cb86ccf0b1d3ed9acc776`  
**Experiment:** `TTM_SIX_TTM4M_FUNCTIONAL_TRANSFER_PUBLIC48_DEV16_V1`  
**Quyết định owner:** `APPROVE_TTM_SIX_TTM4M_FUNCTIONAL_PILOT_T4_V1` (một lượt T4 có điều kiện)  
**Phán quyết cuối phạm vi khám phá:** **`EXPLORATORY_NO_CLEAR_GAIN`**  
**Original G1:** `FEASIBILITY_HOLD_ARCHIVED` · **`G1_SCIENCE_LOCK=HOLD`** · **`PRIVATE_TEST=SEALED`**.

## 1. Xuất xứ và cấp độ bằng chứng

Tài liệu này ghi lại kết quả owner cung cấp từ Colab Free T4 cùng phép kiểm tra SHA-256 hậu chạy trực tiếp trên Drive. Người lập hồ sơ **không trực tiếp đọc các byte private của checkpoint/weights trên Drive hoặc tái thực thi GPU**. Do đó ghi `OWNER_REPORTED_GPU_EXECUTION` và `OWNER_REPORTED_POSTRUN_SHA_PASS`, không gọi đây là independent GPU attestation.

Preclaim owner gửi: `PRECLAIM_SOURCE_PINNED_PASS; NO_TRAINING; G1_ORIGINAL_SCIENCE_LOCK=HOLD`.  
Postrun owner gửi: `PASS_EXACT_SHA` với ba weights và `result.json`, kết thúc `TTM_SIX_POSTRUN_INTEGRITY=PASS`.  
`READY.json` có mặt (600 bytes), liệt kê hash cho bốn tệp đầu ra; **chưa có SHA độc lập của chính `READY.json`**. Không diễn giải `READY` thành chữ ký số.

Output namespace (giữ nguyên, không ghi đè):
`MyDrive/TTM/ttm-six-functional-pilot-v1/ttm_six_ttm4m_functional_transfer_public48_dev16_v1/`.

| Tệp | SHA-256 từ READY, được owner băm lại PASS |
|---|---|
| `arm_A_weights_only.pt` | `1d8673c40a9e81e96c3ad98d9c71f675739e62f23adc6612adc072c5c3c67f4d` |
| `arm_B_weights_only.pt` | `cb6af4a39a10fac150e8fd81870c6421706dde88746e8043b5648a65bc8aa648` |
| `arm_C_weights_only.pt` | `416cd18198d0dbc0a2b50f1379781ca38308153b21a5b0dd9f306d99d769bdd2` |
| `result.json` | `45da481c6591acafe5783cd35e3e9711212793a3c074c009d4046b5e2bd555dd` |

## 2. Kết quả

48 TRAIN, 16 DEV / 4 nhóm; mỗi nhánh có 72 optimizer updates từ cùng trọng số gốc step 1280 nhưng AdamW mới. DEV được dùng trong màn sàng lọc Qwen trước đó, **không phải held-out confirmatory**. Giá trị dưới đây là số liệu từ `result.json` do owner cung cấp.

| Nhánh | DEV NLL (↓) | DEV raw probe MAE (↓) | Updates |
|---|---:|---:|---:|
| Parent (chẩn đoán, không train trong pilot) | 5.290400058081509 | — | — |
| A — CE baseline | 3.5657932133037225 | — | 72 |
| B — CE + direct functional MSE | 3.6051159389127934 | 0.06855617190433794 | 72 |
| C — CE + SIX-inspired residual MSE | 3.616317542474685 | 0.06980299486229088 | 72 |
| Template-only control | — | 0.05202296104592581 | — |

DEV NLL theo nhóm (A/B/C):

| Nhóm | A | B | C |
|---|---:|---:|---:|
| fiction_03 | 3.4118175906734867 | 3.4945156924374454 | 3.5155709540093696 |
| fiction_05 | 3.2786019232965287 | 3.2006931920205393 | 3.245009576120684 |
| fiction_07 | 3.9880509639810198 | 4.086793209146137 | 4.060518136053729 |
| fiction_14 | 3.4962417886864325 | 3.5271709750157707 | 3.542058245735879 |

Receipt quyết định: `relative_dev_nll_C_vs_A=-0.01416916970464244`; `relative_dev_nll_C_vs_B=-0.003107141005087875`; `relative_probe_mae_C_vs_strongest_control=-0.34177281452066677`; `DEV_groups_C_better_than_A=1`. Theo hợp đồng sàng lọc, yêu cầu C ≥1% tốt hơn A, ≥1% tốt hơn B, ≥1% tốt hơn đối chứng MAE mạnh nhất, và thắng ≥3/4 nhóm. **Cả bốn điều kiện không đạt**. Đây không phải phép kiểm định ý nghĩa thống kê hay bằng chứng phủ định phổ quát SIX.

## 3. Kỹ thuật và nguồn

Theo receipt của owner: `elapsed_wall_seconds=14.674081723999961`; `cuda_peak_reserved_gib=0.166015625` (peak CUDA reserved); `qwen_model_rerun=false`; `original_ttm_optimizer_continued=false`. Những con số này nằm dưới giới hạn 1200 giây và 12 GiB; không khẳng định watchdog bên ngoài.

Pin nguồn:
- Original TTM parent checkpoint SHA-256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`.
- BPE manifest SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Qwen ZIP SHA-256 `6f98560117219cf3cecc37fb87ff562a784fe82238d9b2d831cbda7634488d9f`.
- P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`.
- Initial model weights SHA-256 `f44dcfe887e4e0c47a1167a292becc9292483fde8d4b2d4e2ac4a8a16ae19580`.
- `READY.json`: `TEST_used=false`; `decision=EXPLORATORY_NO_CLEAR_GAIN`.

## 4. Phân xử (adjudication) và quyết định lưu trữ

- **Technical owner-evidence integrity:** `PASS_OWNER_REPORTED_4_OUTPUT_HASHES`; byte recheck độc lập bởi assistant `NOT_EXECUTED`; `READY.json` self-hash `NOT_PROVIDED`.
- **Exploratory science screening:** `EXPLORATORY_NO_CLEAR_GAIN` (4/4 thresholds fail). Không nâng thành `G1 ORIGINAL FAIL` và không kết luận cơ chế SIX không thể có ích với thiết kế khác.
- **Execution:** one-shot **consumed**, `NO_NEW_GPU_RUN_AUTHORIZED`. Không chạy lại Qwen.
- **Artifacts:** giữ A/B/C và Parent nguyên trạng, không merge C vào TTM main, không ghi đè đường dẫn xuất.
- **Privacy:** không đưa raw Qwen NPZ hoặc private tensors lên GitHub. TEST theo receipt được ghi `false`, không phải bằng chứng máy độc lập rằng mọi truy cập bên ngoài đều không xảy ra.
- **Lineage:** không sửa `lineage.md` vì đây là exploratory screen, không phải phán quyết PASS/FAIL của hợp đồng khoa học G1 nguyên bản.
- **Next focus:** quay về TTM-Small-4M evaluation, Attention, architecture, inference; mở thử nghiệm SIX tiếp theo chỉ với một hypothesis và pre-registration mới, không tự động gia hạn pilot này.

**Trạng thái cuối:** `ONE_SHOT_CONSUMED` · `OWNER_REPORTED_POSTRUN_SHA_PASS` · `EXPLORATORY_NO_CLEAR_GAIN` · `G1_ORIGINAL=FEASIBILITY_HOLD_ARCHIVED` · `G1_SCIENCE_LOCK=HOLD` · `PRIVATE_TEST=SEALED`.
