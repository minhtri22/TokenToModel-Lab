# TTM T5 — GELU_ERF strict parity: phán quyết khoa học xác nhận độc lập C01–C04

Ngày: **10/11/2026**. Đối tượng: TTM-Small4M GPT-2 trên checkpoint bước 1.024. **Không huấn luyện lại, không truy cập TEST/Q1Q2 và không chạy lại bất kỳ phép suy luận cũ nào.**

## 1. Kết quả đã kiểm chứng trên Windows

**Phán quyết khoa học:** `PASS_HELDOUT_STRICT_LOGIT_PARITY_4_OF_4_SCOPED_GELU_ERF`.

Các lượt C01–C04 được định nghĩa **trước** thí nghiệm khám phá D01/D02 trong prereg Git blob `82fdd9fe716579181db648caa69170fb63d115a6`. Đối chứng sử dụng GGUF F32 gốc SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, checkpoint nguồn bước 1.024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, CPU, `KV=F32`, `Flash=OFF`, `threads=1`. Bản sửa có phạm vi **thay đúng lựa chọn GELU thành `GELU_ERF` tại khối GPT-2 FFN**.

| Fixture | Token | max-abs logits: GGML − PyTorch P02 | strict 0,001 | Top-1 |
|---|---:|---:|---|---|
| C01 | 2 | 0,000002811279296466296 | PASS | Cùng |
| C02 | 4 | 0,00000476921142578135 | PASS | Cùng |
| C03 | 11 | 0,000003819118651549047 | PASS | Cùng |
| C04 | 17 | 0,000005725019530444797 | PASS | Cùng |

**4/4 PASS**, mỗi fixture so sánh **đủ 2.048 logits**, tổng 8.192 giá trị. Sai số lớn nhất `5,72501953044e-6`, nhỏ hơn `0.001` **174,67 lần**. 4/4 node `ffn_gelu_erf-0` thật được ghi trong trace, không chỉ thay nhãn tên. Không thay ngưỡng, nguồn P02, GGUF hoặc fixture.

Log Windows đã được đọc trực tiếp:

- 12/12 bài kiểm thử nguồn và âm tính PASS hai lần (V2 bootstrap và runner), không chạy model ở bước này.
- MSVC configure/build probe C PASS; `--self-check` PASS, không tải model.
- Một lô duy nhất bốn phép suy luận native: `04_confirmatory_four_native_once.log`, `RETURN_CODE=0`, marker `T5_GELU_ERF_CONFIRMATORY_COMPLETE_ROWS_4`.
- Checker riêng `05_independent_strict_2048_audit.log`, `RETURN_CODE=0`, `CONFIRMATORY_STATUS=STRICT_PASS_4_OF_4`; checker chỉ đọc raw native và reference ZIP, không tự sinh lại đáp án.

### Chuỗi provenance bất biến

- Receipt Windows: `_tmp/ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110/CONFIRMATORY_ONCE_RECEIPT.json`, SHA256 **`95ed3c419e42df493dc314abeb42e47afa1bf72fcb90d2c7246ff4c55d645e88`**.
- Audit JSON: `C01_C04_INDEPENDENT_STRICT_AUDIT.json`, SHA256 `1d5e050e9aefbeb5720a5f86986ecbcffe2a51a8c7605d07c85467553b8b8887`.
- Native logits JSONL: SHA256 `9b674719010eb04ce14865104613de953030fed6febb653faa9b6bdc52f02027`.
- Native graph trace JSONL: SHA256 `2df54a8340db5272f4144372266c090c24f74d04ac063b149516cd4b01affe99`.
- Binary mới: SHA256 `aa55f398617e8160013e3d1d8494986160d150f5052e44b39c8885f6f47a5df4`. Bản GELU source GPT2: SHA256 `59d1685da8f44ed420af8852c987a6c72e0d028c8304931f05a9e90a5c03f06e`.
- Reference P02 ZIP: SHA256 `e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996`; raw JSONL SHA256 `dbebd9e5261ad4857b72ff16cf9383ce243dab9ca72ade5332e8325ea2c48e25`.
- Checker Git blob **`cef0e214bb178f7e5059c5ada0200e75b3970936`**, runner Git blob `aca05ce2791385a69fcd7d933fd5079e4088358b`. Nguồn gốc checkout lỗi cú pháp V1 được giữ nguyên; sửa đúng một dấu ngoặc trước khi native, đã QA và PIN.

**Phương pháp đọc lại:** nhận trực tiếp receipt, report JSON, log build, log native và log checker, đối chiếu GitHub prereg/source SHA và bảng metric từng fixture. Connector đọc tệp raw JSONL có giới hạn độ dài nên lần kiểm toán hiện tại **không tái tính độc lập thêm 8.192 phép trừ từ raw**; phép kiểm 8.192 logit đã được checker độc lập đóng băng và thực thi trên Windows. Không thổi phồng mức độc lập của lớp readback này.

## 2. Giải thích nguyên nhân

Ở D01/D02 trước khi mở tập xác nhận, can thiệp **chỉ đổi phép toán `LLM_FFN_GELU → LLM_FFN_GELU_ERF`** trong mã nguồn GGML (các tensor trước GELU có cùng thống kê chênh lệch giữa A/B). `ffn_gelu-0` là bước đầu tiên vượt độ nhạy chẩn đoán `1e-5` ở baseline A. Sau bản sửa B, sai số tại GELU và logits giảm mạnh; D01/D02 strict PASS 2/2. Các C01–C04 mới chưa dùng đạt strict PASS 4/4 bằng chính sửa đổi đó.

**Kết luận nguyên nhân có điều kiện:** sự không tương thích biến thể GELU giữa mã PyTorch P02 và nhánh GPT2 GGML gốc **là cơ chế chính đã được xác định và kiểm tra độc lập trên sáu fixture mới này**. Không suy ra mọi sai khác trên CPU/GPU, ở kích thước chuỗi bất kỳ, Flash ON, KV F16 hoặc các fixture lịch sử đều được giải quyết.

## 3. Giữ nguyên kết quả khoa học âm tính

- L0013 nguyên bản: **`FAIL_STRICT_LOGITS_32_OF_32_SCOPED_SYNTHETIC`**; bốn cấu hình F16/F32 × Flash ON/OFF vẫn FAIL trên bộ cũ, không được đổi nhãn.
- Bộ fixture gốc 8: **FAIL 7/8** vẫn giữ nguyên.
- `G1_ORIGINAL`, các kết quả TEST và những nghiên cứu độc lập không bị tác động.
- Các receipt lỗi kỹ thuật (Windows loader, V1 auditor shape, V1 Python checker syntax) giữ nguyên trong lịch sử; các lỗi này **không phải FAIL khoa học mới**.

## 4. Phán quyết merge riêng PR #16

PR #16 có **83 tệp thay đổi** trong `artifacts/qa/ttm-t5-parity`, `docs/pilot`, `tools/pilot_t5` và `lineage.md`. Một số công cụ chỉ dành cho chẩn đoán lịch sử hoặc đã được thay thế (bao gồm checker lỗi V1), được lưu để bảo toàn chứng cứ. Không phải mọi tệp trong PR đều là code production sẽ đưa vào sử dụng.

- **Cổng khoa học mới:** PASS. C01–C04 được đánh giá trên nguồn và reference đã khóa, không sửa threshold hay fixture.
- **Cổng nguồn/merge:** cần rà soát danh mục 83 tệp, đánh dấu rõ runner lỗi/được thay thế/khuyến nghị sử dụng; kiểm tra source SHA và trạng thái nhánh cập nhật; chủ dự án quyết định merge sau rà soát.
- **Tình trạng GitHub tại lúc phân xử:** `PR16=DRAFT_HOLD`, `MERGED=false`, `main=b57b44e7287f842e81050c1faee337f636333dd0`. Không merge tự động.

**Quyết định:** `SCIENCE=PASS_HELDOUT_4_OF_4` · `ROOT_CAUSE=GELU_IMPLEMENTATION_MISMATCH_SUPPORTED_SCOPED` · `MERGE=HOLD_OWNER_FINAL_SOURCE_HYGIENE_AND_APPROVAL` · `TEST=UNCHANGED`.

## 5. Bước thực hiện tiếp theo

`TTM_T5_PR16_SCIENTIFIC_PASS_LINEAGE_APPEND_AND_83_FILE_FINAL_MERGE_HYGIENE_REVIEW`: ghi nối tiếp L0014 cho khoa học PASS có giới hạn; giữ L0013 FAIL; hoàn tất review 83 tệp và trình quyết định merge cho chủ dự án. Không inference hoặc train lại.
