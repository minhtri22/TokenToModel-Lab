# TTM-Small-4M D1 / EXP32 — Đóng thực nghiệm khám phá và định hướng nghiên cứu mới

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_NO_RESCORE_NO_RESEED`  
**Owner decision:** `CLOSE_DEV32_NO_RESCORE_NO_RESEED_NO_NEW_SCIENCE_EXECUTION`  
**Trạng thái cuối:** **`CLOSED_EXPLORATORY_SCOPED_PROVISIONAL_INPUT_PROVENANCE`**

## 1. Bằng chứng đã khóa, không sửa lại

Lượt khoa học DEV32 short/near dùng checkpoint **step1024** SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, tokenizer SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, và dữ liệu D1 V2 SHA-256 `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8`.

Đã thực thi 96 lượt teacher-forced và 64 bản sinh (32 greedy, 32 nucleus). Kết quả chấm mù AI 64 bản được khôi phục từ hai **tệp JSON thực tế** trong Library, tính lại SHA từ byte gốc:

- Tệp điểm `D1_EXP32_RATER_BLIND64_SCORES.json` — SHA-256 `d6ef3780ca72ffe5fcc7a67bcfe85abf3a87b92b4fee30bcf9b88460734885d4` (19.774 byte).
- Tệp freeze `D1_EXP32_RATER_BLIND64_SCORE_FREEZE_RECEIPT.json` — SHA-256 `97720785d460bb919be063be117f70f66fc68ebdf8cdb33abc79e368c97f8795` (1.269 byte).
- Đã xác nhận 64/64 `opaque_id` khác nhau và khớp với thuật toán ID trong runner đã khóa; không có điểm bị thay đổi, và **owner chỉ nối nhãn sau khi hash điểm đã được xác minh**.

**Giới hạn quan trọng:** Người chấm sử dụng 64 records được dán trong cuộc trò chuyện khác và **không có byte gốc của BLIND64 ở thời điểm chấm**; do đó `RATER_INPUT_BYTE_PROVENANCE=NOT_VERIFIED`. Đối chiếu opaque ID đủ 64 **không chứng nhận** từng `prompt_text`/`generated_text_only` được dán là byte-identical. Đây là đánh giá AI `EXPLORATORY_SCOPED` và kết luận cuối giữ nhãn **provisional**; không nâng thành khoa học confirmatory.

## 2. Kết quả cuối đã phân xử

| Chỉ số | Greedy | Nucleus (1 seed V2 đã khóa) |
|---|---:|---:|
| Văn bản | 32 | 32 |
| Điểm 0 | 30 | 9 |
| Điểm 1 | 2 | 23 |
| Điểm 2/3 | 0 | 0 |
| Mean grade | 0,0625 | 0,71875 |
| **Tuân thủ dữ kiện grade ≥2** | **0/32** | **0/32** |
| Thành công cặp hai điều kiện trong 16 family | **0/16** | **0/16** |
| Cửa sổ lặp 3-token (đếm thô) | 213 | 8 |

Trong 32 cặp prompt tương ứng, nucleus đạt điểm cao hơn 22 lần; greedy cao hơn 1; hòa 9. Nucleus giảm lặp và tăng số hành động có thể nhận diện theo rubric, **nhưng 0/32 bản ở cả hai phương pháp đạt factual adherence ≥2**. Không gọi nucleus là giải pháp cứu năng lực dùng dữ kiện. Các số đếm về lặp chưa chuẩn hóa theo độ dài và chỉ mang tính mô tả.

Teacher-forced `S=1/16`, prior-adjusted `S'=2/16` cho thấy tín hiệu chọn đáp án theo fact **yếu** ngay trước giải mã sinh tự do. Đây là chỉ dấu hợp lý để chuyển trọng tâm nghiên cứu, nhưng **không xác định nguyên nhân** là data, objective hay capacity; không sử dụng nó để bác bỏ khoa học tổng quát của mô hình hoặc kết luận từ TEST.

**Phán quyết nghiên cứu:** `WEAK_FACT_CONDITIONING_EXPLORATORY` + `DECODER_RESCUE_FACT_NOT_SUPPORTED` + `RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED`.

## 3. Đóng lượt, không mở vòng thí nghiệm hậu nghiệm

Chấm điểm `64/64` được **khóa nguyên vẹn**. Không chấm lại, không thay đổi rubric, không chọn seed thuận lợi, không tạo prompt khác để làm đẹp kết quả, không chạy lại mô hình theo exploratory DEV32 và không mở TEST/Q1Q2.

`DEV32=EXECUTED` · `DEV32_CLOSEOUT=CLOSED_EXPLORATORY_SCOPED` · `RATER_SCORE_SHA=VERIFIED` · `OPAQUE_ID_MATCH=64/64` · `OWNER_UNBLIND=COMPLETED_AFTER_SCORE_FREEZE` · `FACT_ADHERENCE=0/32_BOTH` · `RATER_INPUT_BYTE_PROVENANCE=NOT_VERIFIED` · `D1_CONFIRMATORY_512=HOLD` · `TEST_Q1Q2=SEALED` · `TRAINING=NO` · `NEW_INFERENCE=NO` · `LINEAGE=UNCHANGED`.

Không append `lineage.md` vì đây là biên nhận kết thúc exploratory có giới hạn, không phải đóng một cổng confirmatory mới. Không merge `main`.

## 4. Hướng nghiên cứu tiếp theo — **đề xuất thiết kế, chưa cấp GO thí nghiệm**

Ưu tiên thay đổi khả năng **học và sử dụng dữ kiện** thay vì tinh chỉnh giải mã:

1. **Dữ liệu (training data):** một tập câu chuyện có điều kiện/đối chứng phản thực với độ phủ cân bằng A/B, thay đổi một fact mỗi cặp; chống học mẹo tên gọi/độ dài; khóa split theo family/nguồn, không lẫn D1/TEST.
2. **Mục tiêu huấn luyện (training objective):** so sánh baseline next-token loss với một mục tiêu bổ trợ **answer-choice/contrastive fact conditioning**; bảo đảm tổng token, steps, checkpoint/optimizer, ngữ cảnh và ngân sách tương đương; nếu huấn luyện bổ sung phải đăng ký riêng.
3. **Dung lượng mô hình (model capacity):** chỉ thử mô hình lớn hơn sau khi đã biết baseline và objective có tác dụng hay không, so trên cùng dữ liệu DEV mới và trần chi phí cố định.

**Thiết kế kiểm chứng tương lai đề nghị:** A/B một biến mỗi lượt, cùng thông tin đầu vào và ngân sách, đo teacher-forced fact-switch trước; rollout và blind rater làm secondary outcome. Preregistration trước khi sinh/học; không dùng dữ liệu/seed đã xem kết quả DEV32 để tối ưu hậu nghiệm. D1 confirmatory giữ nguyên HOLD, không lấy nghiên cứu mới làm cách vòng qua gate.

Lượt closeout **không khởi chạy khoa học mới** và **không yêu cầu một micro-permit khác**. Khi owner muốn nghiên cứu tiếp, mở **một** thiết kế ưu tiên duy nhất có quyết định GO/HOLD riêng.

**Biên nhận JSON:** `artifacts/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXP32_TERMINAL_EXPLORATORY_CLOSEOUT_OWNER_SINGLE_ADJUDICATION_20261112.json`.
