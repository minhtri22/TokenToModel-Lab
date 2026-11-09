# TTM T5 — caller K/V: kết quả kiểm tra nhanh chỉ đọc (2026-11-10)

**Task:** `TTM_T5_CALLER_KV_MINIMAL_READONLY_INSPECTION`  
**Phân xử:** `SOURCE_DEFAULT_F16_KV=SUPPORTED_SCOPED` · `FLASH_ATTENTION_RUNTIME=CONFIRMED` · `EXACT_CAUSAL_PROOF=HOLD` · `STRICT_LOGITS=FAIL_7/8_PRESERVED`.

## 1. Bằng chứng mới từ chủ máy

Câu lệnh PowerShell 5.1 `Select-String` chỉ đọc source C++ `C:\Users\minht\Downloads\TTM_T5_F32_NUMERIC_LOCALIZATION_PS51_PRECLAIM_RECOVERY_V2_20261108\ttm_t5_layer_probe.cpp` hoàn thành nhanh, `SOURCE_EXISTS=PASS`, **5233 bytes**. Các dòng trúng điều kiện lọc (có số dòng nguyên bản):

```text
LINE=98  auto cp=llama_context_default_params();
LINE=101 llama_context *ctx=llama_init_from_model(model,cp);
```

Không có dòng trúng bộ lọc `\.type_k\b`, `\.type_v\b`, `\.flash_attn_type\b`. Việc này **hỗ trợ** cách hiểu caller sử dụng default K/V, nhưng không có quyền tuyên bố đã thẩm định toàn bộ mã C++ và mọi biến đổi gián tiếp: công cụ remote bị giới hạn đọc thư mục Downloads. Source SHA-256 từ owner Preview trước: `8a8324a10c67c6f868fe130d6ea7c535edb6364c8d04988600163e7b4a4b828e`.

## 2. Đối chiếu nguyên bản llama.cpp pin `372dc5ca157276beb6c67b2e92477e8d662e964a`

- [src/llama-context.cpp#L4248-L4275](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-context.cpp#L4248-L4275): `llama_context_default_params` định nghĩa `type_k = GGML_TYPE_F16` (L4274), `type_v = GGML_TYPE_F16` (L4275), `flash_attn_type = LLAMA_FLASH_ATTN_TYPE_AUTO` (L4263). Git blob `a450d8257c87706655022d962d1cc846adb2fb45`.
- [src/llama-graph.cpp#L3060-L3080](https://github.com/ggml-org/llama.cpp/blob/372dc5ca157276beb6c67b2e92477e8d662e964a/src/llama-graph.cpp#L3060-L3080): đường FlashAttention có cast K/V về F16 khi cần; Git blob `9f99ba83e4d7aff29ec82c74f605df913144a021`.
- Log native gốc trong dự án `_tmp/ttm_t5_numeric_localization_v1/fixture_0/native_run.log` ghi có `FLASH_ATTN_EXT`. Cùng với thông tin default, bằng chứng này nâng giả thuyết **F16 KV + Flash ON** thành *đường thực thi có cơ sở mạnh*.

**Giới hạn:** source SHA `8a8324...` và native debug executable SHA `62fda558309502fdef9c736243b9a6194262fe0b5667949a0872fbe5c33e4de2` là hai loại hiện vật khác nhau; chưa có chuỗi chứng thực độc lập liên kết đúng tệp C++ thành binary đã chạy. Chưa đo contribution của F16 đến logits `ffn_inp-0`; chưa có bằng chứng đây là nguyên nhân duy nhất.

## 3. Phân xử chạy tiếp

- **Không chạy lại** owner Preview một-shot đã hoàn thành `HOLD_OWNER_RUN_GATE`.
- Script source-binary supplement cũ bị treo và không tạo receipt; **không chạy lại script này**. Kết quả kiểm tra nhẹ `Select-String` đã cung cấp thông tin cần thiết cho câu hỏi hiện tại, không nên kéo dài thủ tục.
- Giữ bản tiền đăng ký 2×2, **S0 F16/Flash ON**, **S1 F32/Flash OFF**, **S2 F32/Flash ON**, **S3 F16/Flash OFF**, 8 fixture tổng hợp mới, 32 suy luận dự kiến. S0 là mô phỏng cấu hình *old-like*, không phải chứng minh bitwise bằng môi trường cũ.
- **HOLD** trước khi chạy native: phải biên dịch/QA binary ứng viên đúng commit, tạo logits tham chiếu PyTorch từ checkpoint gốc 1024 với ID mới, xác minh GitHub provenance và xác nhận owner run gate. Không sửa ngưỡng `0.001`, không tái dùng 8 fixture đã tiêu thụ, không mở TEST/Q1Q2, không train, không thay model source.
- Kết quả nghiêm ngặt lịch sử vẫn `7/8 FAIL`. Không ghi kết quả kỹ thuật thăm dò này vào `lineage.md` như science PASS.

**Bằng chứng JSON mới:** `artifacts/qa/ttm-t5-parity/TTM_T5_CALLER_KV_MINIMAL_READONLY_SOURCE_INSPECTION_20261110.json`.

**Bước thực hiện tiếp theo:** `TTM_T5_F32_KV_FLASH_2X2_NEW_BINARY_REFERENCE_STATIC_QA_THEN_OWNER_RUN_DECISION` — chỉ chuẩn bị và kiểm thử công cụ mới theo hợp đồng đã khóa, rồi ra quyết định chạy một batch 32 lượt; không mở thêm vòng kiểm chứng caller bằng script nặng.
