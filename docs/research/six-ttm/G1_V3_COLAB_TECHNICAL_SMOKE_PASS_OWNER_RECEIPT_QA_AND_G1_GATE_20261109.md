# G1 v3 — Colab technical smoke PASS, kiểm tra nhất quán độc lập và phân định khóa khoa học

**Ngày:** 2026-11-09  
**Dự án:** TTM × SIX (nhánh nghiên cứu, không phải TTM-Small-4M production)  
**Trạng thái:** `G1_V3_PREFLIGHT_PASS / G1_V3_TECHNICAL_SMOKE_PASS_OWNER_REPORTED / RECEIPT_CONSISTENCY_QA_11_OF_11_PASS / SCIENCE_LOCK_HOLD`  
**Nhánh:** `research/ttm-six-cross-model-representation-transfer-20261109`  
**Nguồn:** notebook Colab v3 và hai biên bản đầy đủ do chủ sở hữu gửi trực tiếp trong chat. **Chưa nhận bytes tệp receipt nguyên bản hoặc tính lại SHA-256 của receipt Colab**; biên bản được chép và đối chiếu với mã đã ghim, không giả nhận là independent Colab replay.

## 1. Provenance bất biến

- Nguồn mã đã chạy v3: `scripts/research/six_ttm/g1_qwen06_zero_science_smoke_colab_env_20261109_v3.py`, Git blob `f394293a7c43d8c726d88a1a9b9f63ab49fe3d4a`.
- Notebook v3: `notebooks/six_ttm/TTM_SIX_G1_V3_COLAB_PY313_PATCH_FLEX_PREFLIGHT_ONESHOT_SMOKE_20261109.ipynb`, Git blob `f00554c0ceda46f8c4b7f6a8b54cc7a88cb0ddfa`.
- Teacher `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca`.
- Trọng số `model.safetensors` SHA-256 đọc từ Colab: `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b`, **MATCH** với expected được đóng băng trước khi load.
- Phần tử `parent_v1_source_blob=24318de7d0196944a0a9a6d6be9851099f18b85b` và `parent_v2_source_blob=c98811e167696f86e94e3da9d01f3b9f020c3cc6` cho phép truy vết hai lần STOP trước đó. Không đổi hay xóa v1/v2.

### Mã băm các tệp teacher mà Colab báo đã tính

| File | SHA-256 |
|---|---|
| `LICENSE` | `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e` |
| `config.json` | `660db3b73d788119c04535e48cf9be5f55bc3100841a718637ae695b442f27dd` |
| `generation_config.json` | `2325da0f15bb848e018c5ae071b7943332e9f871d6b60e2ed22ca97d4cb993d2` |
| `merges.txt` | `8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5` |
| `model.safetensors` | `f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b` |
| `tokenizer.json` | `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4` |
| `tokenizer_config.json` | `d5d09f07b48c3086c508b30d1c9114bd1189145b74e982a265350c923acd8101` |
| `vocab.json` | `ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910` |

## 2. Thông số tài nguyên/runtime (Colab, owner receipt)

| Thành phần | Giá trị |
|---|---|
| Python | `3.13.16`, executable `/usr/bin/python3` |
| Torch | `2.14.1+cu130` |
| Transformers | `5.22.1` |
| Hugging Face Hub | `1.33.0` |
| Tokenizers | `0.23.3` |
| Safetensors | `0.8.0` |
| GPU | Tesla T4, compute capability `7.5` |
| Free GPU at preflight | `15,527,116,800` bytes (~14.46 GiB) |
| Peak GPU reserved in smoke | `1,310,720,000` bytes (~1.221 GiB; <=6 GiB guard) |
| Disk free at smoke preflight | `120,839,012,352` bytes (~112.54 GiB) |

`G1_V3_STATIC_COMPILE=PASS`, `G1_V3_PREFLIGHT_EXIT=0`, `G1_V3_PREFLIGHT_RECEIPT.status=PASS_PREFLIGHT_ONLY`.  
`G1_V3_SMOKE_EXIT=0`, `G1_V3_SMOKE_RECEIPT.status=PASS_TECHNICAL_ONLY`, `weight_verified_before_load=true`.

## 3. Tensor, tính lặp và giới hạn phát hiện

- Số hidden states: **29** (embedding/index 0 + 28 blocks).
- Hình dạng các tensor: `[2, 39, 1024]`, lengths `[17, 39]`, hai tiền tố **synthetic**; model ở `eval` và `torch.inference_mode()`, `use_cache=False`.
- Hidden tensors và logits đều được mã chạy kiểm `torch.isfinite`; đến cuối receipt `PASS_TECHNICAL_ONLY` nghĩa là các điều kiện này đã vượt theo đúng logic mã v3. Mã chỉ ghi vector-hashes của layer `0,7,14,21,28`, không lưu tensor thô.
- `repeatability=SAME_RUNTIME_EXACT_F32_HASH`: hai lần forward liên tiếp có cùng hashes của các vector được chọn. **Không chứng minh tái lập across sessions, khác GPU/version**.
- Layer 0 báo hai hashes giống nhau trên hai tiền tố: `5dd419d91214f686885516f2b603efb2baf1cdc2270a7197f2f1290bd6b8335b`. Điều này phù hợp với cả hai đầu vào cùng kết thúc bằng dấu câu và layer 0 có thể phản ánh cùng token cuối; **không quy thành lỗi hoặc bằng chứng biểu diễn bất biến**. Layer 14, 21 và 28 có các hash khác nhau theo mẫu.
- `science_data=false`, `science_executed=false`, `training=false`.
- `G1_V3_ONE_SHOT_MARKER=CONSUMED_DO_NOT_REPEAT`: **không đề xuất chạy lại** lượt đã PASS.

## 4. Kiểm tra độc lập tính nhất quán biên bản — 11/11

Đọc lại mã nguồn chính xác ở nhánh, sau đó kiểm tra theo dữ liệu từ **console/receipt do chủ sở hữu cung cấp**, không dùng trường `status` làm thẩm quyền duy nhất.

| Kiểm tra nhất quán | Phán quyết |
|---|---|
| Teacher ID + revision đúng nguồn đã pin | PASS |
| Git blob script v3 đúng mã chuẩn | PASS |
| SHA-256 trọng số từ receipt trùng expected và danh sách tệp | PASS |
| Đủ 8 tên file; mọi SHA dạng 64 ký tự hex | PASS |
| Python, Torch và 4 gói đồng bộ pin v3 | PASS |
| Tesla T4 CC7.5 và free GPU/disk đạt guards | PASS |
| Peak `1,310,720,000 <=6×2^30` bytes | PASS |
| 29 tensors, shape, lengths hợp lệ | PASS |
| Đủ 5 layer hash, mỗi layer 2 vector hash hợp lệ | PASS |
| Các vector layer 14 trên hai mẫu không trùng hash | PASS |
| Preflight PASS, smoke PASS, training/science false, marker consumed | PASS |

**Verdict về độ tin cậy:** `INTEGRATED_OWNER_RECEIPT_CONSISTENCY_QA=PASS_11_OF_11`. Đây là một phép kiểm tra thứ cấp trên **bằng chứng đã xuất**; chưa tải độc lập các tệp `G1_PREFLIGHT_RECEIPT.json`, `G1_SMOKE_RECEIPT.json` và chưa tính lại SHA-256 bytes của chúng; không tuyên bố independent GPU replay.

## 5. Adjudication kỹ thuật và ranh giới khoa học

**Đóng nhánh G1 technical feasibility (trong phạm vi đã khóa):**
`QWEN06_COLAB_T4_HIDDEN_STATE_EXTRACTION_FEASIBLE=PASS_TECHNICAL_OWNER_RECEIPT`.

Được phép chuyển sang **đánh giá khóa tiền đăng ký khoa học G1**, chưa được mở science run. Đây không phải G1 representation-transfer PASS, không phải SIX functional-transfer PASS, không phải TTM student gains. G1 prereg draft vẫn thiếu bộ dữ liệu được quyền sử dụng, probe bank/negative controls, fixed TRAIN/VAL/TEST, primary metric, ngưỡng hiệu lực, seed, ngân sách và giám sát độc lập. G3 vẫn phụ thuộc checkpoint TTM được khóa; TTM-Small-4M theo main riêng.

- `G1_TECHNICAL=PASS_SCOPED`
- `G1_SCIENCE_LOCK=HOLD`
- `G1_SCIENCE_EXECUTION=NOT_STARTED`
- `G3_TTM_DISTILLATION=NOT_STARTED`
- `LINEAGE_MD=UNCHANGED`
- `NO_REPEAT_ALREADY_CONSUMED_G1_SMOKE`

Không sửa main, PR #12 đã merge bởi tuyến riêng (không do G1). Không merge SIX × TTM, không đổi upstream SIX, không chạy lại một-shot hay huấn luyện.

**Bước thực hiện tiếp theo:** `TTM_SIX_XMODEL_G1_SINGLE_INTEGRATED_SCIENCE_PREREG_FINALIZATION_AND_INDEPENDENT_REVIEW` — kế thừa technical PASS, trong **một** lượt chốt hợp đồng khoa học G1: quyền nguồn, dữ liệu, cách tạo cùng tiền tố văn bản qua hai tokenizer, negative controls, chỉ số chức năng/CKA, seed và giới hạn GPU; thực hiện review độc lập trước khi cấp phép G1 science. Không phát sinh thêm vòng kiểm thử kỹ thuật Qwen đã đạt.
