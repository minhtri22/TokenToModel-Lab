# TTM T5 — Thẩm định độc lập chẩn đoán sai khác số học F32 (2026-11-08)

**Phạm vi:** TTM-Small-4M trained checkpoint (step 1024); PyTorch vs llama.cpp, CPU/F32; chỉ 8 đầu vào ID tổng hợp đã khóa. Đây là kiểm định kỹ thuật (engineering QA), **không** phải thực nghiệm khoa học mới, không sử dụng TEST/TRAIN, không thay tiêu chí chính thức.

## A. Xuất xứ và kết quả kiểm định

- Báo cáo native duy nhất: `_tmp/ttm_t5_numeric_localization_v1/T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json`, do người dùng gửi lại. SHA256 tính độc lập từ tệp nhận được: `8f1ed4f8ec5846084226807cccc1455638d4d2e08957827ffa15ed765d5220ae`, đúng log Windows.
- Bộ chẩn đoán nguồn V2 ZIP SHA256 `1e33a249a7895377df069fbe4bede4247ecb3ef6b7b8a78758c1a30e502d56a3`; không sửa Python/C++ numeric so với V1.
- Checkpoint gốc SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, GGUF gốc SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5` theo native receipt; không trực tiếp tính lại SHA của hai tệp nhị phân trong lần đọc độc lập này.
- llama.cpp commit nguồn `372dc5ca157276beb6c67b2e92477e8d662e964a`; debug probe SHA256 `62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2` theo native receipt.
- FAIL gốc được ghim SHA256 `c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8`; V5B SHA256 `ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375`.
- QA độc lập đã tính lại từ tệp JSON: 8/8 fixture đúng thứ tự; 35/35 stage đúng tên mỗi fixture (280/280); kích thước hợp lệ; `max_abs`, `mean_abs`, `rmse` hữu hạn; cờ vượt ngưỡng và first-stage nhất quán; tổng thể **`PASS_SCOPED_INDEPENDENT_READBACK_NOT_PARITY_PASS`**. QA JSON SHA256 `a74bf614800dbd99000c682c9e911a0e2c414f192ed96b693a68a93a5f4e1a34`.

## B. Bảng kết quả đã tự tính lại

| Fixture | Số ID | Sai khác đầu tiên vượt 1e-5 | Điểm trung gian đầu tiên vượt 0.001 | Max abs logits cuối | T5 strict 0.001 |
|---|---:|---|---|---:|---|
| 0 | 1 | `ffn_inp-0` | `ffn_gelu-1` | 0.000936747 | PASS |
| 1 | 3 | `ffn_inp-0` | `ffn_norm-1` | 0.001599312 | FAIL |
| 2 | 5 | `ffn_inp-0` | `ffn_gelu-1` | 0.002269030 | FAIL |
| 3 | 4 | `ffn_inp-0` | `attn_norm-1` | 0.001976013 | FAIL |
| 4 | 8 | `ffn_inp-0` | `ffn_gelu-0` | 0.001823902 | FAIL |
| 5 | 16 | `ffn_inp-0` | `ffn_norm-0` | 0.001900882 | FAIL |
| 6 | 7 | `ffn_inp-0` | `attn_norm-1` | 0.002775908 | FAIL |
| 7 | 32 | `ffn_inp-0` | `ffn_norm-0` | 0.003362179 | FAIL |

**Chú ý:** `1e-5` là ngưỡng nhạy dùng để *định vị*, không phải ngưỡng PASS. `0.001` là ngưỡng chấp nhận *logits cuối* đã đóng băng, áp vào các điểm trung gian ở đây chỉ mang tính mô tả: không được diễn giải `ffn_norm-0 > 0.001` là nguyên nhân của FAIL đầu ra.

## C. Định vị và phân biệt giả thuyết

1. **Embedding+position (`inpL`) trùng tuyệt đối** ở 8/8 trường hợp; sai khác lớn nhất của `attn_norm-0` là `4.768e-7` và của `wqkv_b-0` là `9.537e-7`. Không có dấu hiệu trọng số/token/position mapping sai lớn ở đầu vào.
2. **Sai khác đáng chú ý xuất hiện đầu tiên ở `ffn_inp-0`**, là đầu ra sau khối attention cộng residual: từ `6.2287e-5` đến `2.0969e-4` trên 8 fixture. Vì không đo riêng softmax, phép nhân `attention@V`, output projection và residual, chỉ có thể kết luận **vùng attention/output-residual** là vị trí phát sinh khác biệt sớm nhất quan sát được; không quy kết một kernel cụ thể.
3. **LayerNorm sau attention có thể khuếch đại:** `ffn_norm-0` đạt sai khác lớn nhất `0.001324296`, trong khi `ffn_inp-0` tối đa `0.000209689`. Đây là đặc điểm quan sát được, chưa chứng minh LayerNorm tự thân được triển khai sai.
4. **Khác biệt GELU là đóng góp có khả năng:** P02 PyTorch dùng `nn.GELU()` mặc định (exact); nguồn llama.cpp GPT-2 được ghim dùng `LLM_FFN_GELU` qua `ggml_gelu` (khác đường `GGML_FFN_GELU_ERF`). Báo cáo có tham chiếu PyTorch GELU-tanh chẩn đoán. Đối chiếu cuối giảm max abs trong 6/8 trường hợp nhưng **vẫn 7/8 FAIL** theo 0.001; max tanh-final `0.002672329545`. Vì alternate trace dùng PyTorch-tanh trên cả chuỗi, không có phép cô lập từng toán tử, **không được tuyên bố GELU là nguyên nhân duy nhất hoặc fix hoàn chỉnh**.
5. Debug callback max abs logits cuối `0.0033621788024902344`, chênh `2.686e-12` so với V5B max abs `0.003362178805176086`, dưới giới hạn nhất quán `0.00015`. Đây là kiểm tra theo thống kê cực đại, chưa phải bitwise equivalence 8 vector 2048 logits giữa hai native probes.

## D. Phán quyết kỹ thuật và giới hạn

- `T5_NUMERIC_LOCALIZATION=PASS_SCOPED_INDEPENDENT_READBACK`: phép chẩn đoán đã hoàn tất, đọc lại nhất quán.
- `ROOT_CAUSE_REGION=ATTENTION_OUTPUT_OR_RESIDUAL_POST_QKV`, `EXACT_OPERATION=NOT_ISOLATED`, `GELU_CONTRIBUTION=POSSIBLE_SECONDARY`.
- `T5_GGUF_EXPORT=PASS_PRESERVED`, `T5_TOKENIZER_UTF8=PASS_9/9_PRESERVED`, `T5_TOP1=8/8_PRESERVED_FROM_V5B`, `T5_FULL_LOGITS=FAIL_7/8_PRESERVED`, `OLLAMA=NOT_TESTED`.
- **Quyết định:** ghi nhận giới hạn tương thích số học của backend pinned F32 với ngưỡng strict đã khóa; **không sửa llama.cpp, không re-export checkpoint, không huấn luyện hoặc kiểm tra TEST, không nâng ngưỡng chỉ để lấy PASS**. Một backend patch chỉ có cơ sở sau khi xác lập được toán tử đích và QA kiểm chứng độc lập; không tự động mở lượt chạy mới.
- Có thể kiểm tra import/inference Ollama ở phạm vi *khả năng chạy thực dụng*, nhưng kết quả chỉ mang nhãn `COMPATIBILITY_ONLY`, không sửa T5 parity FAIL và không chứng minh hiệu quả mô hình.
- Không append `lineage.md`: đây là bằng chứng QA kỹ thuật, không phải kết quả khoa học thay thế T4.

## E. Điều kiện đóng và các bằng chứng còn thiếu

Không nhận nhãn `T5_PARITY_PASS` nếu chưa có một phép đo parity mới được phê duyệt, dùng đúng 8 fixture và ngưỡng đã khóa, trên implementation version-pin sau sửa; báo cáo FAIL cũ giữ nguyên. Nếu không sửa backend, nhãn kết luận cuối là `T5_SCOPED_BACKEND_NUMERICAL_INCOMPATIBILITY_DOCUMENTED`, không phải thành công tương đương logits.

**Phạm vi độc lập:** chỉ đọc báo cáo native JSON và mã nguồn công khai tại commit ghim; chưa nhận 280 tệp tensor `.f32`, log build và xác minh binary headers/DLL trên máy Windows bằng phép kiểm độc lập mới. Không được tuyên bố kiểm định bitwise toàn bộ tensor hoặc root-cause proof.

**Bước tiếp theo:** `TTM_T5_SCOPED_BACKEND_NUMERIC_INCOMPATIBILITY_CLOSURE_AND_OLLAMA_COMPATIBILITY_PREFLIGHT_READONLY` — đóng biên bản kỹ thuật, rà soát điều kiện nạp GGUF vào Ollama, không mở lại TRAIN/TEST hoặc strict parity.
