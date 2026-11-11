# TTM-Small-4M — Quyết định khoa học tích hợp hậu CF1: dữ liệu, mục tiêu học và đánh giá FRESH16

**Ngày:** 2026-11-11  
**Công việc:** `TTM_SMALL4M_DATA_OBJECTIVE_EXISTING_AC_AND_FRESH16_SINGLE_INTEGRATED_SCIENCE_READINESS_GAP_REVIEW_DESIGN_ONLY`  
**Phạm vi GitHub ghi báo cáo:** `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111` (không ghi vào nhánh FRESH16/AC)  
**Trạng thái:** `DESIGN_REVIEW_GO__SUCCESSOR_SCIENCE_HOLD` · `NO_NEW_TOY` · `NO_NEW_TRAINING` · `NO_INFERENCE`.

## 1. Định vị đúng công việc và câu hỏi khoa học

Lượt rà soát này **không phải** phản biện sửa đổi rubric V2 của agent FRESH16, không phân xử quyền chạy 32 đầu ra CPU, và không đóng các lỗi thực thi native của agent AC. Chỉ tổng hợp **hai thiết kế đã tồn tại** và bằng chứng TTM-Small-4M gốc nhằm quyết định liệu có đủ cơ sở chọn hướng can thiệp dữ liệu, mục tiêu học, hay thay kiến trúc.

Ba câu hỏi khác nhau:

1. **Trạng thái năng lực:** mô hình có giữ ngữ cảnh và tạo sự kiện tiếp nối đúng dữ kiện không? — FRESH16 là phép đo chẩn đoán dự kiến (prospective diagnostic), chưa có đầu ra.
2. **Tác động mục tiêu học:** giữ nguyên dữ liệu, lịch lấy mẫu, checkpoint, cấu hình và ngân sách; thay trọng số mất mát theo vị trí có tạo cải thiện đo được không? — A/C là can thiệp đối chứng (controlled intervention), chưa chạy huấn luyện.
3. **Nguyên nhân dữ liệu so với loss:** thay lựa chọn cửa sổ dữ liệu và trọng số loss theo hai nhân tố, đồng thời đo tương tác — chỉ thiết kế 2×2 A/B/C/D mới có khả năng so sánh phù hợp ở mức can thiệp đã định, nhưng B/D chưa sẵn sàng khoa học.

Không dùng kết quả FRESH16 trên 16 prompt thay kết quả FINAL24 của AC và không gộp hai rubric thành một điểm chất lượng.

## 2. Bằng chứng gốc cần bảo toàn

| Nguồn | Kết quả / hiệu lực | Kết luận hợp lệ |
|---|---|---|
| T4 VAL bước 1.024 | NLL 3,5223388517 so với bigram TRAIN-only 3,9972314170; lợi thế 11,880537% | `T4_VAL_H1=PASS`: học dự đoán token trên TinyStories VAL |
| T4 TEST cũ | Chỉ đọc thống kê từ biên bản một lần đã tiêu thụ | Không tái chấm và không lấy TEST để chọn thay đổi |
| FRESH12 đã tiêu thụ | 35/48 đầu ra có điểm bám prompt bằng 0; người chấm AI đơn | `WEAK_ADHERENCE_SCOPED`, không phải kết luận xác nhận tổng quát |
| Bước 1.024→1.280 cũ | NLL VAL giảm, adherence ở bộ nhỏ không tăng | Không chứng minh cứ huấn luyện lâu hơn sẽ cải thiện bám ngữ cảnh |
| CF1 DEV36 đã tiêu thụ | 0/36 cặp đổi lựa chọn; có lối tắt từ vựng và nhiễu vị trí đáp án | `FAIL_SCOPED` cho phép đo CF1, không chứng minh bất lực suy luận nói chung |
| FRESH16 | Nguồn/BPE/đầu vào được QA theo biên nhận, nhưng chưa chạy mô hình | `SCIENCE_NOT_EXECUTED`; ngưỡng H1/H2 không phải kết quả |
| AC | A/C source QA, một số kiểm thử tổng hợp và public escrow có bằng chứng; thiếu điều kiện thực thi | `NO_GO_PREEXEC`, chưa có hiệu ứng loss quan sát được |

**Dữ liệu gốc** gồm 2.048 truyện TRAIN, 498.287 vị trí nhãn riêng, 4.194.304 lượt target presentations ở 1.024 bước (~8,417 lượt/vị trí nhãn theo phép chia), không tương đương số epoch chính xác. Đây là lý do đặt giả thuyết thiếu bao phủ dữ liệu, **không phải** bằng chứng nhân quả.

Checkpoint gốc bước 1.024 SHA-256: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Giữ nguyên kiến trúc P02, BPE gốc và phân chia dữ liệu đã khóa. Không nhập bằng chứng EmbeddingGemma2 hoặc SIX làm đối chứng trực tiếp.

## 3. Ma trận phép so sánh: cái gì thực sự nhận dạng được nguyên nhân?

| Nhánh | Can thiệp dữ liệu | Can thiệp mục tiêu học | Khả năng xác định nguyên nhân |
|---|---|---|---|
| A | Lịch lấy mẫu TRAIN gốc | Mất mát entropy chéo đều (Uniform CE) | Đối chứng huấn luyện tiếp nối cùng ngân sách |
| B | Chọn cửa sổ đầu truyện với số nhãn hợp lệ khớp | Uniform CE | `B−A`: tác động **chính sách chọn cửa sổ**, không phải tăng kích thước corpus |
| C | Cùng cửa sổ, thứ tự và số lượng như A | CE ưu tiên phần sau cửa sổ (Suffix-weighted CE) | `C−A`: tác động **trọng số loss theo vị trí** |
| D | Cùng lịch chọn cửa sổ như B | Suffix-weighted CE | `D−C`, `D−B`: tác động theo từng nhân tố; `(D−B)−(C−A)`: tương tác |

**AC hiện hành chỉ triển khai A và C**: mỗi arm tiếp nối từ **cùng parent step1024**, 128 bước × 4.096 nhãn hợp lệ/bước = **524.288 lượt nhãn/arm**; tổng hai arm **1.048.576**. C có trọng số 1 tại vị trí 0–31, trọng số 3 từ vị trí 32. Tiêu chí và tập đánh giá FINAL24 đã có; public escrow của so sánh A/C đã khóa theo biên nhận.

Giữ số lượng nhãn và số bước bằng nhau **không** đồng nghĩa cùng khối lượng tín hiệu gradient hiệu dụng: trọng số CE chủ ý làm thay đổi đóng góp gradient. Nếu C cải thiện, chỉ được nói *can thiệp loss theo vị trí trong chế độ tiếp nối này có hiệu ứng*, không được nói mô hình đã học được cấu trúc mục tiêu hoặc suy luận nhân quả.

**Thiết kế 2×2** cần toàn bộ B/D và lịch draw khớp, khôi phục optimizer/scheduler/RNG/scaler như nhau; tổng 4 arm tương ứng 2.097.152 lượt nhãn dự kiến. Hiện đây chỉ là thiết kế chưa được ủy quyền, không được tự nâng cấp AC thành bốn arm. Hơn nữa, ưu tiên cửa sổ đầu truyện làm thay đổi đồng thời **vị trí và loại ngữ cảnh**; ngay cả B−A PASS cũng không tách được ảnh hưởng độ bao phủ nội dung khỏi vị trí trong truyện, trừ khi có thiết kế riêng trong tương lai. Không tạo nghiên cứu đó lúc này.

**Checkpoint cũ step1280** không hợp lệ làm arm kiểm soát của AC/2×2 do lịch sử huấn luyện/chi phí khác, và các kết quả one-shot đã tiêu thụ.

## 4. Khả năng đo và quan hệ giữa FRESH16 với AC

**FRESH16 là đánh giá năng lực gốc (baseline diagnostic), không phải phép so sánh can thiệp:** 16 prompt (8 cặp), 32 đầu ra dự kiến từ step1024/1280, ngưỡng H1≥12/16 và H2≥6/8 có điều kiện phủ bốn nhóm. Kết quả nếu có chỉ áp dụng với rubric, prompt và điều kiện sinh của FRESH16.

**AC có phép đo riêng:** 24 prompt FINAL, chấm mù A/C theo rubric 0–3, mục tiêu ứng viên từ hồ sơ AC: cải thiện adherence trung bình ≥0,5/3, thắng nghiêm ngặt ≥16/24 prompt, cận dưới bootstrap ghép cặp >0; đồng thời kiểm soát VAL NLL giảm chất lượng không vượt 5% và coherence/consistency không giảm quá 0,25/3. Đây là ngưỡng ứng viên trong báo cáo gốc, không được ghi nhầm là thành tích hay tự động cấp quyền.

**Hai thiết kế không được trộn:** người chấm/niêm phong FRESH16 không tự động đáp ứng yêu cầu người chấm/niêm phong AC; FRESH16 không phải điều kiện quyền nguồn, checkpoint hay hiệu lực khôi phục native của AC. Kết quả FRESH16 nếu được thực hiện trước có thể giúp diễn giải mức baseline O0, nhưng **không phân biệt được dữ liệu với loss** và không thay thế đối chứng A/C. Nếu hai chương trình không có người chấm độc lập, cả hai vẫn HOLD theo hợp đồng riêng.

Tại thời điểm kiểm tra GitHub: nhánh FRESH16 có **ứng viên V2** với mã Git blob `27b994b3b3283b2611af21d63acc5d37abf45013`; hồ sơ trên nhánh **không ghi nhận chủ dự án đã chấp thuận/khóa vai trò đầu ra hoặc được phép chạy CPU**. Lượt này không phản biện, sửa, hay phê duyệt V2 thay agent đó; ghi nhận `FRESH16=NOT_EXECUTED`.

## 5. Điều kiện khoa học thiếu — một gói, không tách thành micro-permit

| Điều kiện cần trước thực nghiệm | FRESH16 (chỉ đánh giá) | AC (huấn luyện A/C) |
|---|---|---|
| Nguồn prompt, BPE, checkpoint, ngân sách và ngưỡng | QA nguồn đã PASS theo biên nhận, không chạy lại nếu bytes không đổi | Nguồn A/C và thiết kế/escrow đã PASS phạm vi nguồn, không chạy lại |
| Phương pháp chấm đáng tin, chống rò rỉ giải mù | Cần quyết định V2 của owner, người chấm và người phân xử cặp, giữ mù trước khi xem kết quả | Cần người chấm độc lập, custody khóa private, khóa score trước khi giải mù |
| Không dùng lại dữ liệu/đầu ra tiêu thụ | Owner/executor xác nhận chưa xem đầu ra FRESH16; không đọc TEST/Q1Q2/FRESH12/CF1 | Không dùng lại TEST/Q1Q2/FRESH12/OOD; FINAL24 chỉ dùng một lượt theo khóa |
| Quyền dữ liệu riêng tư | Không phát sinh TRAIN mới; giữ đúng phạm vi source | Xác nhận quyền dùng private TRAIN/VAL pack và không công bố raw/khóa |
| Hạ tầng và tính trung thực thực thi | Khóa mã runner CPU, custody output, một quyết định owner riêng | Native Windows Python 3.12 V2 readback, T4 FP16 zero-step smoke, actual interrupted resume parity |
| Cổng quyền chạy | `NOT_GRANTED` | `NOT_GRANTED` |

Bản QA native AC V1 lịch sử từng xuất `HOLD_NATIVE_QA_FAILED` do cách bắt stderr trong PowerShell 5.1, test đầu tiên có `ok`; script sửa V2 đã stage nhưng **chưa có biên nhận V2 hoàn tất** trong nguồn đối chiếu. Không được gọi đây là FAIL khoa học hoặc PASS của 6/6 native test. Không chạy lại kiểm tra nguồn đã PASS nếu mã byte không đổi.

Không yêu cầu kết quả FRESH16 PASS như điều kiện bắt buộc để huấn luyện AC; chỉ yêu cầu phép đo AC của chính nó đã khóa và có reviewer độc lập. Không yêu cầu AC được chạy để chấm FRESH16. Hai chương trình có quyết định thực thi riêng, nhưng báo cáo readiness có thể gộp một lần.

## 6. Quyết định của nhánh hậu CF1

**Đối với kế nhiệm có huấn luyện mới:** `HOLD_SUCCESSOR_TRAINING`.

**Đối với chuẩn bị khoa học dựa trên hai thiết kế đã có:** `GO_DESIGN_ONLY_RECONCILIATION_COMPLETE`.

Lý do quyết định:
- Không có dữ liệu can thiệp thật để xác định H_DATA hoặc H_OBJECTIVE.
- A/C chỉ thử can thiệp loss theo vị trí, không đủ để chọn giữa chiến lược dữ liệu và mục tiêu học.
- 2×2 có phép so sánh tương đối tốt hơn nhưng B/D chưa sẵn sàng và không cấp quyền thay đổi ngân sách.
- FRESH16 là đánh giá O0 chưa chạy, không cung cấp dấu hiệu thực nghiệm mới để thay đổi thứ tự ưu tiên.
- Không có bằng chứng ưu tiên thay kiến trúc O1/MoE/Attention hoặc huấn luyện nhiều bước hơn trên corpus gốc.

**Thứ tự ưu tiên được phê duyệt trong phạm vi thiết kế:** (i) giữ kết luận T4 VAL PASS đồng thời với FRESH12 và CF1 scoped weakness; (ii) tiếp tục chờ quyết định độc lập của owner/agent FRESH16 về baseline quality; (iii) AC agent tự đóng một gói điều kiện native/rights/reviewer/escrow nếu chọn chạy A/C một lần; (iv) chỉ xem lại thiết kế 2×2 sau khi có kết quả/giới hạn của can thiệp A/C và câu hỏi dữ liệu được chủ dự án lựa chọn. **Không cấp phép mới** từ nhánh báo cáo này.

## 7. Chứng cứ Git và quy tắc bảo toàn

- GitHub `main`: `5d52e32f20021e36f08f284ef9864d3ba36dbead` khi đối chiếu.
- Nhánh AC HEAD: `837289fda82b41653a61b74e476f76a0b4c4137c`.
- Nhánh FRESH16 HEAD: `202477787a14cd2c30649bb9dab8f630573479f0`.
- Nhánh hậu CF1 trước báo cáo: `e051ba06edae6af9c30bf2364b78ea8259b02aa3`.
- Nguồn đối chiếu (Git blob): hậu CF1 `d1e823818b81618b32e6d9a4f99bff2fcd0338c7`; thiết kế 2×2 `6f8553e7054078d449bad6b2979c3b07d392eb48`; AC preexec `0c83b23c13c588a7787dd64a6c3d9ed5da22c5ce`; FRESH16 V2 intake `1dd2ddd7d3ca5c054fedefa5b7ea574d98e4a660`.
- Kiểm kê Git local owner trước đó: 13 worktrees, 11 trong dự án, 8 sạch, 3 có mục trạng thái, 2 ở ngoài root bị bỏ qua; không `git clean/reset/prune`; không đụng key riêng tư.
- `main`, PR #13, `lineage.md`, tất cả nguồn/loss/checkpoint/prompt/threshold đã khóa **không viết** trong lượt này.
- Không thêm entry vào `lineage.md`: đây là thẩm định thiết kế, không phải khoa học PASS/FAIL được phân xử.

## 8. Bước thực hiện tiếp theo

`TTM_SMALL4M_POST_CF1_OWNER_SINGLE_SUCCESSOR_RESEARCH_PRIORITY_DECISION_ON_EXISTING_FRESH16_AND_AC`

Chủ dự án **chỉ chọn ưu tiên nghiên cứu kế nhiệm**, không cấp quyền chạy: hoặc chờ kết quả đánh giá O0 FRESH16 trước, hoặc ưu tiên agent AC đóng các điều kiện huấn luyện A/C hiện có. Quyết định phải giữ rõ rằng **A/C chỉ kiểm tra trọng số loss**; muốn nghiên cứu dữ liệu cần đối chứng B−A trong thiết kế 2×2 đã có và một phê duyệt khoa học riêng trước khi chạy. Không tạo thêm prompt/toy/kiểm tra nguồn, không mở O1.

**Trạng thái cuối:** `T4_VAL_H1=PASS` · `FRESH12=WEAK_ADHERENCE_SCOPED` · `CF1=FAIL_SCOPED_PRESERVED` · `FRESH16=NOT_EXECUTED` · `AC=NO_GO_PREEXEC` · `O1=DEFER` · `NEW_TRAINING=NO` · `GPU=NO` · `TEST_Q1Q2=UNTOUCHED` · `MAIN/LINEAGE=UNMODIFIED` · `PR13=DRAFT_UNMERGED`.
