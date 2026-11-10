# TTM-Small-4M × EmbeddingGemma 2 — Phân xử khoa học CAUSAL6 sáu nhánh

**Ngày:** 10/11/2026. **RunID:** `ttm_small4m_gemma2_causal6_2048x4096_free_t4_20261109_v1`. **Phán quyết chính thức:** `PASS_SCOPED_DONOR_MAPPING_ALIGNMENT`. **QA độc lập:** `PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK`.

## Thiết kế đã chạy

Sáu arms `RR-F, RP-F, RR-A, RP-A, OR-F, OP-F` bắt đầu từ TTM 256 chiều checkpoint bước 1.024, huấn luyện thêm **2.048 bước × 4.096 nhãn/arm** trên một Tesla T4, cùng lịch TRAIN, tổng **50.331.648 lượt nhãn huấn luyện**. Đối chứng real/permuted trong từng cặp dùng chung phép chiếu khởi tạo; phương án F cập nhật projector và Transformer/head, phương án A chỉ cập nhật projector. H512 độc lập với các membership cũ theo kiểm tra exact: 512 truyện, 651 cửa sổ, 119.856 nhãn; không chấm lại 320 truyện L0017 hay 64 TEST.

## Kết quả trên cùng H512

| Arm | NLL (nats/token) | READY step2048 checkpoint SHA256 |
|---|---:|---|
| RR-F | 3.2825563058 | `39e38dbc401d9090234671e02613fb2b1e26b6b34c7e525fad16397d6d10a801` |
| RP-F | 3.3611221158 | `f6526a80d4b5061fcc50a841f8da26ac1630d5f257350773057fec3e817e7704` |
| RR-A | 3.6667187069 | `93698e7cf6cc9caa0f18e72248b094eba57cd911520aafd2c78e2123e2d4d15f` |
| RP-A | 3.9170144487 | `8bde54566f221d0585e425238edd8928acb709c00caa21967ad469ff0b9cc4b4` |
| OR-F | 3.3161514710 | `1314c51fe5b62d7955a275068c55736a50e1081c324f1f8e4874256e23e7396b` |
| OP-F | 3.4086149600 | `9adfa4d7de17f211cb93a03b3f697c2cdc895f878728d9ac2242591cc11dfe5e` |

**PRIMARY:** `tau_D = L(RP-F) - L(RR-F) = +0.0785658100`, CI95 `[0.0709965265, 0.0863988495]`, cận dưới **>0**: **PASS** theo hợp đồng tích hợp khóa trước CLAIM.

**SECONDARY (thăm dò):** `tau_A=-0.1717299318`, CI95 `[-0.1799432180, -0.1629692811]`; `tau_P=-0.0138976790`, CI95 `[-0.0209037707, -0.0069402524]`. Phép thử chỉ học projector cho thấy `RP-A−RR-A=0.2502957419`, lớn hơn full ridge `tau_D`: mở decoder làm cả real lẫn permuted cải thiện NLL, đồng thời thu nhỏ chênh lệch giữa chúng. Orthogonal real-perm gap `0.0924634890` lớn hơn ridge gap nhưng real ridge `RR-F` vẫn có NLL thấp nhất. **Không** dùng secondary để sửa phán quyết.

Bootstrap **2.000 lần**, NumPy seed `2026110915`, ghép cặp theo truyện, hiệu NLL được tính bằng ratio-of-sums theo nhãn (token-weighted), CI percentile 95% hai phía.

## Chứng cứ được đọc lại trực tiếp trên Drive

- CLAIM SHA256: `4ed9935821535bfee982b577c364a51eed25af496f03689ff75a0adc71c1f01b`, `claimed=true`, cùng RunID, seed, source pins, lịch TRAIN SHA256 `899afc01be5473a07a67e0d6247b0c33775f7584139c07f6680f5798eb8b1ef6`.
- RESULT SHA256: `fa692607a5f25960a1fd55a1719743b1913d11174c310e7034a1b931e66fb18c`, `COMPLETED_PENDING_INDEPENDENT_ADJUDICATION`.
- INDEPENDENT_READBACK_PUBLIC SHA256: `64b118b44848da5c3f4de381b71519918e651849e7e8ee0632427b16a45b9b96`, `PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK`, **0 model forwards** và **không train lại**.
- PER_STORY_PRIVATE SHA256: `aee961b6afd801960c15d4009d27aeea92fea1af2cb14e523a45a5d464f0840f`; chỉ kiểm tra trong môi trường riêng, **không công khai**. Tính lại cục bộ từ 512 loss-sums và target-counts: tất cả 6 NLL, 3 contrasts, 2.000 bootstrap draws cùng seed **khớp chính xác**.
- Sáu `step_2048/READY.json` và `checkpoint.pt` tồn tại trong Drive, metadata READY của tất cả khớp RunID, runner `84e1377ad526c7822bfe025f9728e91a133fee66483b4dcd8127989bb6360cd4`, lịch TRAIN, môi trường GPU và step=2048. Runner chấm H512 đã kiểm hash binary checkpoint theo READY; lần phân xử này **không tải và hash lại 6 file binary**.
- Phạm vi công khai chỉ gồm ba JSON RECEIPT, biên bản phân xử, báo cáo và L0019. Không công khai text truyện, token IDs, per-story losses, checkpoint weights, optimizer state hoặc địa chỉ Drive nội bộ.

## Phân xử khoa học và giới hạn

Bằng chứng cho thấy **gán embedding donor đúng token có lợi ích dự đoán so với donor hoán vị**, tại điều kiện Ridge và Transformer thích nghi, với cùng nguồn/dữ liệu/ngân sách. Đây là **PASS trong phạm vi ánh xạ donor (donor-mapping alignment)**, không phải chứng minh rằng lợi ích chỉ do ngữ nghĩa tiền huấn luyện của EmbeddingGemma 2. Projector đã fit từ real token pairs, chỉ một seed, dữ liệu H512 cùng họ TinyStories-valid và corpus donor pretraining chưa kiểm tra contamination. Không có arm TTM-no-donor huấn luyện ngang ngân sách trên chính H512 nên không suy ra lợi ích tuyệt đối so với baseline TTM từ CAUSAL6 này. L0017 direct-swap PASS và L0018 gate32 negative được giữ, không mâu thuẫn. Không mở GGUF/ứng dụng hoặc tự tăng seed/budget.

**Phán quyết:** `L0019=PASS_SCOPED_DONOR_MAPPING_ALIGNMENT` · `SCIENCE_ONE_SHOT=COMPLETED` · `INDEPENDENT_QA=PASS` · `APPLICATION_BACKLOG=DEFERRED`.
