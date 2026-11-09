# TTM-Small-4M × EmbeddingGemma 2 — Phân xử khoa học GATED32 CPU one-shot (B/G/R)

**Ngày:** 2026-11-09 · **Nhánh:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` · **RunID:** `ttm_small4m_gemma2_zero_gate_residual_32_cpu_probe_20261109_v1`

## 1. Phán quyết theo tiền đăng ký

**`GATED_32_STEP_SIGNAL_NOT_ESTABLISHED` — FAIL khoa học trong phạm vi giả thuyết đồng thời đã khóa.** Đây không phải FAIL QA kỹ thuật. Hai nhánh G (donor EmbeddingGemma 2 đúng token) và R (donor hoán vị) đã huấn luyện **32 bước mỗi nhánh**, mỗi bước đúng **512 nhãn TRAIN**, chỉ cập nhật **256 tham số gate**; B là đối chứng đóng băng (0 bước). Chỉ chấm cuối trên **256 truyện, 328 cửa sổ, 61.122 nhãn VALIDATION** đã sử dụng trong nghiên cứu trước đây. Không GPU, không TEST, không dùng tập 320 truyện L0017.

Tiêu chí tiền đăng ký tại commit `49d407554485d31abf6ef0ca2ee188b5e1e6366a` là đồng thời `CI95_lower(B−G)>0` **và** `CI95_lower(R−G)>0`, bootstrap ghép cặp theo truyện 1.000 lần, seed `20261109`. Chỉ điều kiện đầu đạt.

## 2. Bằng chứng định lượng

| Nhánh | VAL NLL (nats/token) | |
|---|---:|---|
| B (baseline untied đóng băng) | 3.5223388275 | |
| G (donor thật, residual gate) | 3.5213177127 | tốt hơn B rất nhỏ |
| R (donor hoán vị, residual gate) | **3.5205936608** | tốt nhất trong thăm dò này |

| Đối chứng | Delta NLL | CI95% percentile story bootstrap | Cận dưới > 0 |
|---|---:|---|---|
| B−G | +0.0010211148 | [0.0007229702, 0.0012893495] | PASS |
| R−G | -0.0007240519 | [-0.0010824418, -0.0003801699] | **FAIL** |

Giá trị R−G âm (khoảng tin cậy toàn bộ âm) cho thấy đối chứng R **có NLL thấp hơn** G trong phép thử và VALIDATION cụ thể này; **không được suy diễn** donor thật nói chung gây hại. G có lợi thế nhỏ so với B, nhưng không vượt R nên giả thuyết gate mang thông tin donor đúng token **không được thiết lập** ở ngân sách này.

## 3. Nguồn và thẩm định độc lập

- Đã đọc lại trực tiếp từ máy Windows bằng phương thức read-only các bản công khai `CLAIM.json`, `RESULT.json`, `INDEPENDENT_READBACK_PUBLIC.json`. Bằng chứng gốc giữ tại `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_small4m_gemma2_zero_gate_residual_32_cpu_probe_20261109_v1` và **không sửa hoặc chạy lại**.
- Owner console SHA256: CLAIM `d57c239d54cca10c448e919f36ac052ea70c20ba9c7d03620aff3832b9659fba`, RESULT `a3eecadde88fad706411b4596aba7aa4f16ba294105cf4585c9560bf138dd3dc`, independent readback `9dfa8e49a515dd1c5b5924241cdb0169b00aedbb0b077b1a5139c802e5fb96a0`. Per-story riêng tư chỉ lưu tại máy, SHA `5ebaa8ee9462bf5b50ae3a82639a9123a8cb0dddacd94d66611bdcee135aa187`; checkpoint gate G `718c01f00b1e924c76905473ca2fe97ed904913562c7824ec9dd974c3288829e`, R `aca5ead18b3e3cb7f38f9b95c047353eab88841a7708b36c81d9af3871ac6d9f`.
- Source runner `235816631eedbe212f7f431700024f1e4ae8e470fd5b0cabcdabd78421c815bf`, schedule `a460c39b176ba1ba2211bb8040821afc1bec9d41753979cf3457b00faefe430a`; bốn nguồn checkpoint/candidate/T4 TRAIN-VAL pack và hai mã gốc đã khớp hashes trong CLAIM–RESULT–tiền đăng ký. Fix trước CLAIM về quoting PowerShell 5.1 được commit tại `c6ce57fcd7fe7e2b569f3f3a0a01e22456846a57`; không sửa mã Python science đã dùng.
- CLAIM ghi `steps_before_claim=0`, step0 B/G/R logits bằng nhau, B frozen, mỗi gate 256 trainables. RESULT ghi `COMPLETED_PENDING_INDEPENDENT_ADJUDICATION`, reviewer `PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK`; số liệu NLL, hai contrast, CI95 và run_id đều khớp. Reviewer tính lại bootstrap từ per-story và **không chạy lại training hoặc model.forward**. Rà soát hiện tại đối chiếu công khai, không giải mã per-story data.
- Giới hạn chứng cứ: SHA256 của tệp gốc dùng dấu do owner xuất từ Windows và đối chiếu tham chiếu trong receipt; phiên đọc file văn bản từ xa này không độc lập băm lại bytes tệp nguồn. Phán quyết dùng khớp nội dung, số học, mã băm tham chiếu và reviewer độc lập đã chạy.

## 4. Giới hạn suy luận và quyết định

Đây là phép thử **exploratory** do VALIDATION cũ đã dùng nhiều lần. Phép refit ridge cho donor hoán vị có thể làm đổi chuẩn nhiễu đầu vào: mean L2 hàng delta G=`0.39382985`, R=`0.45858899`; hai nhánh có cùng 256 trainables và nhãn TRAIN, nhưng không đồng nhất tất cả cấu trúc hình học. Một seed và 32 bước không xác minh nhân quả ngữ nghĩa donor.

**Không điều chỉnh LR, không tăng 64/128 bước, không chấm lại/đổi tập.** Kết quả direct-swap L0017 `PASS_FIXED_CHECKPOINT_NEW_HOLDOUT_ALL_THREE_CONTRASTS` vẫn nguyên; đây là mô hình/giả thuyết khác. Bảo toàn backlog ứng dụng thực tế `DEFERRED`, không GGUF/Ollama/production.

**Phán quyết quản trị:** ghi `L0018` bằng append-only sau khi xác minh, không sửa L0014–L0017; giữ main và checkpoint nguồn nguyên trạng. Kết thúc one-shot GATED32 theo tiêu chí đã định.
