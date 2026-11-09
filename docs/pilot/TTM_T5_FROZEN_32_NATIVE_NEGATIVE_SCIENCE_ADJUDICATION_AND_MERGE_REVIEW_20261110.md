# TTM T5 — Phân xử kết quả 32/32 KV × Flash và đánh giá merge

**Ngày:** 2026-11-10  
**Lệnh nghiên cứu:** `TTM_T5_FROZEN_NEW_32_NATIVE_RESULT_READBACK_INDEPENDENT_ADJUDICATION_AND_MERGE_DECISION`  
**Quyết định thống nhất:** `NATIVE_EXECUTION=PASS_32_ROWS` · `STRICT_LOGIT_PARITY=FAIL_32_OF_32` · `TOP1=PASS_32_OF_32` · `ROOT_CAUSE=UNRESOLVED` · `MERGE_MAIN=HOLD_PENDING_REVIEW`.

## 1. Bằng chứng nguồn thật

Chủ sở hữu đã phê duyệt và chạy **đúng một lần** 8 fixture tổng hợp đã khóa `SYN01..SYN08` × 4 arm S0–S3, trên binary llama.cpp/P02 GGUF F32 đã pin, không train, không TEST/Q1Q2 và không dùng lại 8 fixture lịch sử. Python one-shot báo `ONE_FROZEN_32_NATIVE_BATCH_COMPLETED_UNADJUDICATED`.

Thư mục bất biến trên Windows: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_kvflash_frozen_new_32_native_one_shot_v1_20261110`.

| Hiện vật | SHA-256 | Nguồn xác minh |
|---|---|---|
| `RUN_RECEIPT.json` | `fcaea7a629bd6dda7a4f35b60da686b73b02bc0e9e56ebe7c380d9b9e4c7db09` | Owner và đọc lại độc lập qua RemoteDesktop, khôi phục bytes CRLF đúng Windows |
| `AUDIT_FROZEN_NEW_32.json` | `8aca17561d6beca200fbc746854ab0186e5f3d75930737077111a86c475acc6c` | Auditor độc lập đã chạy return 0, trợ lý tính lại SHA từ nội dung CRLF |
| 32 dòng native `NATIVE_F32_KVFLASH_SYN01_SYN08_X_S0_S3.jsonl` | `544df628802591bcdda7ca9d6de4779d5e2872ee8b409c6710ede5bbf8ac19b8` | SHA do auditor Windows tính trực tiếp trên file gốc, liên kết receipt và audit |
| Reference PyTorch P02 F32 8×2048 | `d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c` | Reference CPU thật đã kiểm định nguồn |
| Compiled EXE native | `0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537` | Binary MSVC và recovery exact SHA |

**Giới hạn độc lập:** connector đọc file theo dòng cắt mỗi dòng dài ~20.000 ký tự, nên chưa tự đọc lại **toàn bộ 32 × 2048 logits thô** bằng kết nối. Tuy nhiên chương trình auditor có mã nguồn và Git blob đã pin **đã đọc trực tiếp đủ 32 dòng trên Windows**, tính lại metrics và SHA native. Lượt đối chiếu thứ hai đã tự kiểm `AUDIT` đủ 32 cặp fixture–arm, các trường strict, top1, Flash counters và SHA chéo. Không gọi lại model.

## 2. Kết quả đối chiếu số học với ngưỡng strict đã khóa 0,001

| Arm | Loại KV | Flash | Strict đạt | Trung bình max-abs (8 fixtures) | Max-abs tệ nhất | Top1 giữ nguyên |
|---|---|---|---:|---:|---:|---:|
| S0 | F16 | ON | **0/8** | 0,002642710 | 0,004443402 | 8/8 |
| S1 | F32 | OFF | **0/8** | 0,001828403 | 0,003038407 | 8/8 |
| S2 | F32 | ON | **0/8** | 0,002642710 | 0,004443402 | 8/8 |
| S3 | F16 | OFF | **0/8** | 0,001828922 | 0,002688889 | 8/8 |

Mọi cặp input–arm đúng cấu hình và trace: ON thấy **4** nút `FLASH_ATTN_EXT`, OFF thấy **0**, toàn bộ 32/32 top1 giữ nguyên. **Cả 32/32 vượt ngưỡng strict 0,001**, không còn arm nào PASS.

Bộ so sánh `S1=F32/Flash OFF` vẫn **FAIL 8/8**, nên việc chỉ chuyển từ F16/Flash sang F32/không Flash **không đủ** phục hồi strict parity. Đây là một kết quả bác bỏ giả thuyết `chỉ riêng KV-F16 và FlashAttention giải thích đủ 7/8 thất bại trước` **trong phạm vi 8 fixture tổng hợp mới**.

Ở cả 8 fixture, S0 và S2 có **max-abs và mean-abs thống kê giống chính xác**. Đây là bằng chứng hai cấu hình Flash ON có đầu ra đối chiếu lỗi tương đương theo hai thống kê, **không phải chứng minh từng 2048 logits giống bitwise**. Flash path có thể cast K/V sang F16; cần xem đường thực thi nếu nghiên cứu nguồn sai số tiếp.

### Lưu ý phương pháp quan trọng

Trường `descriptive_contrasts` từ auditor được tính bằng **chênh lệch giữa các trị max-abs error** của các arm. Nó **không phải** so sánh có dấu của logits từng chiều và **không đủ** để gán một hệ số nhân quả trong mô hình 2×2. Vì vậy:
- Không suy ra F16 hoặc Flash `không có tác động`, chỉ kết luận chúng **không đủ để tự chữa strict parity**.
- Không quy kết toàn bộ sai số do GELU, matmul, residual, softmax hay xuất GGUF; các khả năng này chưa được kiểm nghiệm riêng.
- Giữ nguyên 8 fixture lịch sử `FAIL_7/8` và fixed threshold `0.001`, không tái phân xử như dữ liệu mới.

### Kết luận khoa học độc lập trong phạm vi khóa

- `SCOPED_SCIENCE_RESULT=FAIL_STRICT_PARITY_32_OF_32` — **kết quả âm tính thực và hợp lệ**, không phải lỗi thực thi.
- `TECHNICAL_EXECUTION=PASS_32_OF_32` — QA giao thức, schema, Flash counters, SHA receipt/audit đạt.
- `TOP1_STABILITY=PASS_32_OF_32` — không chứng minh equivalence của logits.
- `F16_FLASH_SOLE_CAUSE_HYPOTHESIS=REJECTED_AS_SUFFICIENT`.
- `EXACT_ROOT_CAUSE=UNRESOLVED`.

Biên bản máy đọc lại: `artifacts/qa/ttm-t5-parity/TTM_T5_FROZEN_32_NATIVE_STRICT_PARITY_NEGATIVE_SCIENCE_ADJUDICATION_20261110.json`. Raw outputs vẫn giữ nguyên trong `_tmp` Windows, không upload checkpoint hoặc TEST.

## 3. Rà soát merge

`main` ban đầu `b57b44e7287f842e81050c1faee337f636333dd0`; nhánh T5 khi bắt đầu review ahead 63/behind 0 và chỉ thêm 41 file, không sửa mã hiện có. Mục L0013 trong `lineage.md` chỉ **append một FAIL khoa học** trong nhánh nghiên cứu; không sửa entry cũ.

**Kết quả FAIL không phải lý do loại bỏ nghiên cứu.** Có thể merge một phát hiện âm tính được chứng thực để khóa lại hướng chẩn đoán; tuy nhiên nhánh gồm nhiều chương trình từng lỗi hoặc bị thay thế và README trước đó mô tả chỉ DESIGN_ONLY. Cần review cách giới thiệu source thí nghiệm, trạng thái các file đã superseded, tính minh bạch raw evidence và kiểm tra quyền dữ liệu.

**Đề xuất hành động:** tạo **Draft PR T5 riêng** vào main để kiểm toán cuối; giữ `MERGE_MAIN=HOLD` trong lượt này, không trộn PR #13, không ép strict PASS. Điều kiện để merge là khoa học và QA nguồn được trình bày chính xác cùng toàn bộ FAIL, chứ không đòi giả thuyết 2×2 phải chứng minh nguyên nhân như kỳ vọng.

**Bước thực hiện tiếp theo:** một vòng review hữu hạn trên Draft PR T5 để quyết định merge kết quả âm tính hay yêu cầu một sửa tài liệu/scope nhỏ; không mở vòng huấn luyện/suy luận mới, không chạy lại 32 native.
