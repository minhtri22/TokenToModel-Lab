# TTM-Small4M — Kiểm toán tích hợp Q1/Q2/OOD và quyết định năng lực

- Ngày: 2026-11-11 (Asia/Bangkok).
- Operation: `TTM_SMALL4M_CAPABILITY_BASELINE_Q1_Q2_OOD_INTEGRATED_ADJUDICATION`.
- Loại: `INTEGRATED_READONLY_EVIDENCE_REVIEW`; **không phải** một lần suy luận, thí nghiệm, huấn luyện hay phán quyết khoa học xác nhận mới.
- Nguồn chính: GitHub `minhtri22/TokenToModel-Lab`; `main=5d52e32f20021e36f08f284ef9864d3ba36dbead`, nhánh Q1/Q2 trước kiểm toán `8399406cfca7855626a20e031d1cfb3c767d606f`, nhánh OOD trước kiểm toán `d4550cb9c88103ccfb4ce0b3683c13f4136e4bd1`.
- Quyết định tích hợp: **`HOLD_REVISE`**. `GO_DATA_EXPANSION=NOT_AUTHORIZED`; `GO_SCALED_MODEL=NOT_AUTHORIZED`.

## 1. Bằng chứng được rà soát

1. T4 gốc, `lineage.md` L0011–L0012 trên main: Transformer P02 3.749.376 tham số, BPE2048, context256, checkpoint step1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. TRAIN 2.048 truyện/256 VAL/64 TEST, 1.024×4.096=4.194.304 target-token presentations. VAL model NLL 3.5223388517 so bigram 3.9972314170 (11.880537% giảm NLL). TEST gốc một lần model 3.48359107334 so bigram 3.97360374532 (12.3316944% mô tả). **TEST đã tiêu thụ, không chấm lại**.
2. Q1/Q2 đúng one-shot: `artifacts/qa/q1q2/TTM_Q1Q2_ONCE_V1/RESULT.json` và `...V2/RESULT.json`, tài liệu `docs/pilot/TTM_Q1Q2_V2_PARTIAL5_QUALITY_AND_HOLD_ADJUDICATION_20261109.md` trên nhánh Q1/Q2. V1: 0 request. V2: 5/74 request, 283 token từ Q1 E01/E02, lỗi `OWNERSHIP_RECHECK_HOLD_UNTRUSTED_PID` trước yêu cầu thứ sáu; Q2 0/24 measurement, warm-up 0/2. Cả hai `CLAIM` đã tiêu thụ. Không kết luận rằng socket lạ thực sự bị chiếm; bằng chứng TCP tại lúc lỗi không đủ.
3. FRESH12 là **nghiên cứu chất lượng riêng**, không thay Q1/Q2: `docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md` và `artifacts/qa/ttm-original1280/fresh12/adjudication/FRESH12_OWNER_PUBLIC_SCOPED_ADJUDICATION_20261110.json`. 12 prompt × 2 checkpoint × 2 serialization, 48 đầu ra đã thực thi và 144 điểm AI khóa trước giải mù. Có 35/48 đầu ra bám prompt 0/3; trung bình adherence baseline=0.291667 và trimmed=0.291667 (delta 0), 24 cặp; paired 12-prompt bootstrap CI mô tả [-0.208333,+0.166667]. Cổng ứng viên cải thiện bám prompt không đạt. Người chấm là Codex AI, không có đánh giá độc lập của con người; **không được ghi là khoa học xác nhận**. Kết quả phân tích trước đó cho thấy việc bỏ dấu cách cuối thay đổi token mở đầu nhưng không chứng minh cải thiện ngữ nghĩa.
4. OOD256 **đã hoàn thành**, tuyệt đối không dispatch lại: nhánh `research/ttm-small4m-embeddinggemma2-ood-design-20261111`, `docs/pilot/TTM_GEMMA2_OOD256_12ARM_FINAL_INDEPENDENT_SCIENTIFIC_ADJUDICATION_20261111.md`, biên bản `artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_OOD256_12ARM_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION_20261111.json`. 12/12 checkpoint (3 seed×4 arm, step2048), 256 bài WikiText-2, 512 cửa sổ, 131.072 labels mỗi arm; 12/12 receipt độc lập PASS. `tau_residual` trung bình +0.06836278722 (CI95 [0.06235342573,0.07423878749]); `gamma_real` +0.04798014207 (CI95 [0.04355893220,0.05222595480]); 3/3 seed dương, 2/2 co-primary đạt. `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`, ghi L0021 append-only **trên nhánh OOD**. Đây là kết quả của biến thể tích hợp EmbeddingGemma2, **không phải** thước đo chất lượng tiếp nối văn bản của checkpoint T4 gốc. Không cô lập semantic pretraining khỏi hình học embedding/động lực huấn luyện; donor overlap chưa biết.

## 2. Ma trận năng lực và giới hạn

| Câu hỏi | Bằng chứng thực tế | Phán quyết có phạm vi |
|---|---|---|
| Có học phân phối token không? | VAL/TEST NLL thấp hơn bigram, T4 một seed | `PASS_SCOPED_TOKEN_LEARNING` |
| Có sinh câu chuyện bám prompt? | Q1 partial5 yếu; FRESH12 35/48 điểm adherence=0 | `WEAK; NO_DEMONSTRATED_SEMANTIC_GAIN` |
| Có giữ thực thể và mục tiêu? | Nhiều đoạn chuyển nhân vật/đề tài trong Q1 và FRESH12 | `NOT_DEMONSTRATED`, chưa là phép đo chuyên biệt xác nhận |
| Có lợi ích OOD từ donor residual không? | OOD256 12 arm, 3 seed, 2 co-primary | `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT` cho biến thể EmbeddingGemma2 |
| Có cải thiện tốc độ/cache hay context? | Q2 0/24, 0 warm-up; T6 synthetic không thay Q2 gốc | `Q2_NOT_EXECUTED` |
| Có bằng chứng tăng tham số là lựa chọn tốt nhất? | Chưa có đối chứng same-data/same-budget scale | `NO` |
| Có bằng chứng mở rộng dữ liệu là lựa chọn tốt nhất? | TRAIN nhỏ, reuse cao, vẫn thiếu thí nghiệm dữ liệu đối chứng | `PLAUSIBLE_NOT_TESTED` |

## 3. Cổng one-shot, giới hạn truy cập và chi phí

- `Q1Q2_V1=CONSUMED_0/74`; `Q1Q2_V2=CONSUMED_5/74`; `FRESH12=CONSUMED_48/48`; `OOD256=CONSUMED_12/12`; `T4_TEST=CONSUMED`.
- Phần Q1/Q2 chưa hoàn thành theo hợp đồng cũ: 43/48 Q1, 24/24 Q2 measurement và 2/2 warm-up. Tổng còn **69 yêu cầu**, hạn mức phần còn lại tối đa **3.584 output tokens** (43×64 + 24×32 + 2×32); đây là **phép tính ngân sách chưa thực thi**, không phải quyền rerun. Không được tiếp tục bằng cùng `CLAIM` hay tự tạo V3.
- Lượt kiểm toán này: **0 training step mới; 0 forward/inference token mới; 0 TEST read; 0 lần thay checkpoint**. Chi phí compute nghiên cứu bổ sung = **0 GPU-second, 0 model-forward**; chỉ có đọc tài liệu/biên bản GitHub. Không có phép đo thực tế đáng tin để quy đổi thành thời gian hoặc USD cho một batch Q1/Q2 mới.
- Truy cập Windows RemoteDesktop `list_dir` ở cả 3 link và `device_status` trả lỗi nội bộ: **không xác nhận hiện trạng local runtime, không truy xuất lại raw local, không chạy Q2 còn thiếu**. Kiểm toán dựa trên biên bản GitHub đã lưu; không tự nhận đây là native readback mới.
- Không sửa/xóa private Drive, checkpoint, TEST, corpus, `main`, `lineage.md`, nhánh OOD hoặc các FAIL lịch sử.

## 4. Phân xử quyết định duy nhất

**`HOLD_REVISE`** là lựa chọn duy nhất hiện đủ căn cứ.

- `GO_DATA_EXPANSION=HOLD`: ưu tiên **thiết kế** một đối chứng dữ liệu huấn luyện tốt hơn, nhưng không được xem là hiệu quả đã chứng minh hay mở quyền huấn luyện mới. Nguồn/giấy phép, chống trùng, tokenizer cố định, cùng ngân sách huấn luyện và phép đo trên tập mới cần được khóa trước.
- `GO_SCALED_MODEL=HOLD`: chưa có bằng chứng mức tăng kích thước sẽ giải quyết vấn đề bám prompt. Không cấp ngân sách Colab lớn hoặc nâng architecture.
- `Q1Q2_COMPLETION=HOLD`: muốn hoàn tất phần 69 request phải có **quyết định successor riêng** với phục hồi sở hữu socket/port được chứng minh, hạn mức tài nguyên, dữ liệu mới hoặc quy tắc không tái sử dụng output, và lý do chống tái chạy. Không được trình bày như phần còn lại của V2.
- `OOD256=SCIENCE_CLOSED_PASS_SCOPED`: bảo toàn L0020/L0021; không chạy lại OOD hay mở OOD mới trong công việc này.
- Cần kết hợp giá trị NLL với chất lượng ngữ nghĩa; giảm NLL không thể coi là chứng cứ tự động của cải thiện instruction following hay coherent continuation.

## 5. Phạm vi ghi nhận GitHub và quyết định merge

Báo cáo này là **tổng hợp quản trị trên nhánh Q1/Q2 hiện hữu**, không tạo nhánh khoa học mới; không tự thêm PASS/FAIL confirmatory vào `lineage.md`. Nguồn của từng kết quả khoa học giữ tại đúng nhánh và bằng chứng riêng; đây **không phải phép QA độc lập trên binary local hiện tại**.

- `MAIN_SHA=5d52e32f20021e36f08f284ef9864d3ba36dbead` tại lượt đối chiếu.
- `CHANGE_SCOPE=DOCS_ONLY_ON_PR13`; `MERGE_DECISION=HOLD`, do PR #13 còn thiếu thẩm định phạm vi và Q1/Q2 gốc không hoàn tất.
- `SENSITIVE_DATA=NO_NEW_RAW_TRAIN_TEST_CHECKPOINT_OR_ESCROW_PUBLISHED`.
- `NEXT_MERGE_ACTION`: review report và các receipt có sẵn trên PR #13 trước bất kỳ merge nào; không đẩy L0021 từ nhánh OOD qua PR13 một cách ngầm định.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_HOLD_REVISE_DATA_OBJECTIVE_EQUAL_BUDGET_SOURCE_ONLY_REVIEW`: chỉ đọc các kế hoạch chỉnh dữ liệu/mục tiêu học đang có, xác định **một** đối chứng cùng ngân sách làm điều kiện quyết định có nên thực hiện nghiên cứu dữ liệu sau này. Chưa huấn luyện, chưa inference, không mở PR/nhánh mới, không đọc TEST hoặc OOD256 đã tiêu thụ.
