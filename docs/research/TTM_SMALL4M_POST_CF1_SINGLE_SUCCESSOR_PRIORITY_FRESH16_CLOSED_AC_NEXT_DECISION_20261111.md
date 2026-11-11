# TTM-Small-4M — Quyết định duy nhất về ưu tiên nghiên cứu kế nhiệm hậu CF1

**Ngày:** 2026-11-11 (Asia/Bangkok)  
**Công việc:** `TTM_SMALL4M_POST_CF1_OWNER_SINGLE_SUCCESSOR_RESEARCH_PRIORITY_DECISION_ON_EXISTING_FRESH16_AND_AC`  
**Nhánh biên bản duy nhất:** `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`  
**Loại quyết định:** `PRIORITY_DECISION_DESIGN_ONLY` — **không phải giấy phép khoa học** (science execution permit).  
**Quyết định:** `PRIORITY_1_FRESH16_COMPLETE_NEGATIVE_SCOPED__PRIORITY_2_AC_READINESS_NEXT__AC_TRAINING_HOLD`.

## 1. Dữ kiện mới làm thay đổi trình tự ưu tiên

Tại thời điểm đối chiếu GitHub trong lượt này, nhánh agent FRESH16 đã tiến tới HEAD `4c3731573f3091300d3dd00dc67f4e2940aec4a3` và có phân xử kết quả thật, không còn ở trạng thái chỉ thiết kế:

- Nghiên cứu CPU **đã chạy một lần đúng 32 đầu ra** bởi agent/owner FRESH16, chấm mù cá thể S1 32/32 và đối chiếu cặp S2 16/16, SHA khóa trước khi giải mù theo báo cáo đã lưu. Lượt rà soát này **không chạy lại** hay mở raw output/khóa riêng.
- 32 đầu ra: adherence điểm 0 có **4**, điểm 1 có **28**, điểm ≥2 có **0** theo bản điểm S1 đã khóa.
- Checkpoint chính step1024: H1 = **0/16** so với điều kiện ≥12/16; H2 = **0/8** so với điều kiện ≥6/8 và yêu cầu mỗi nhóm có ít nhất một cặp đạt (thực tế cả bốn nhóm đều bằng 0).
- Phân xử khoa học chính thức của agent FRESH16: `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`, phán quyết nguyên bản `NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED`.
- Nguồn GitHub: `artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCOPED_NEGATIVE_SCIENCE_ADJUDICATION_20261111.json`, Git blob `b83fb4c45c06381b8ac2764415b5ba681d0685a6`; diễn giải `docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md`, blob `ae8ded5bb03a595f9af4f333ef96271ed3991d7d`. Nguồn science frozen của agent là `c05872354d892a9656f8f98642866f7eebfd0f50`, không phải HEAD báo cáo của nhánh hậu CF1.

**Đánh giá phạm vi:** Đây là kết quả âm tính thật trong bộ FRESH16 V2 đã tiền đăng ký, không phải FAIL phổ quát cho mọi khả năng theo prompt. S1/S2 là các phiên GPT-6 riêng do owner chỉ định; không có bằng chứng đo độ đồng thuận giữa nhiều rater độc lập (inter-rater reliability). Không dùng số liệu này để suy ra nguyên nhân dữ liệu hay loss; không phủ định T4 VAL H1 dự đoán token đã PASS.

**Quy tắc lịch sử:** Biên bản hậu CF1 trước đó ghi `FRESH16=NOT_EXECUTED` chính xác ở thời điểm biên bản ấy; báo cáo này là **bổ sung nối tiếp**, không hồi tố thay/xóa nguồn lịch sử.

## 2. Quyết định ưu tiên, kết quả và quyền hạn

| Ưu tiên | Hướng | Trạng thái quyết định | Hành động được phép từ nhánh này |
|---|---|---|---|
| 1 | Theo dõi năng lực O0 qua FRESH16 | **`COMPLETE_SCIENCE_FAIL_SCOPED`** | Ghi nhận *kết quả tổng hợp đã phân xử*; không chạy lại, không chấm lại, không thay rubric/threshold |
| 2 | AC hai arm A/C — kiểm tra hiệu ứng trọng số loss | **`NEXT_PRIORITY_READINESS_ONLY`**; `TRAINING_NO_GO_PREEXEC` | Để đúng agent AC đóng **một gói điều kiện còn thiếu** và trình quyết định GO/HOLD khoa học riêng; không huấn luyện theo quyết định này |
| Dự phòng | Thiết kế 2×2 A/B/C/D đã có | `DEFER_BD_NOT_AUTHORIZED` | Chỉ xét nếu chủ dự án chọn câu hỏi chính sách lấy mẫu dữ liệu; không mở bốn arm |
| Hoãn | O1, MoE, Attention, thay kiến trúc | `DEFER` | Không mở phát triển/huấn luyện mới dựa vào FRESH16 FAIL |

**Kết luận đơn nhất:** `GO_AC_PREEXEC_READINESS_AS_NEXT_RESEARCH_PRIORITY__HOLD_ALL_NEW_TRAINING`. Đây là **ưu tiên công việc**, không tạo thêm permit nhỏ và không cam kết kết quả huấn luyện.

## 3. Nhận dạng nguyên nhân và phép so sánh thực sự có hiệu lực

**FRESH16** đã xác lập một điểm yếu chất lượng sinh của O0 trong ngữ cảnh bộ đo, nhưng không xác định vì sao mô hình yếu. Không được so trực tiếp 16 prompt FRESH16 với 24 FINAL prompt AC như hai vế đối chứng.

**AC đang có mã ứng viên hai arm A/C**: cùng checkpoint bước 1.024, cùng draw TRAIN, optimizer state, số bước/nhãn; A là mất mát entropy chéo đều (Uniform CE); C là mất mát entropy chéo ưu tiên token phần sau (Suffix-weighted CE; hệ số 1 tại vị trí 0–31, hệ số 3 tại ≥32). Mỗi arm dự kiến 128 optimizer steps × 4.096 nhãn hợp lệ = **524.288 target presentations**. `C−A` có thể phân biệt tác động của *trọng số loss theo vị trí* nếu đầy đủ quyền dữ liệu, so khớp và đo mù; **không** kiểm nghiệm trực tiếp chất lượng tập dữ liệu, số lượng truyện, giám sát goal/entity hay cấu trúc suy luận. Kết quả AC chỉ có ý nghĩa trong các endpoint FINAL24/VAL riêng đã khóa.

**Thiết kế 2×2 có sẵn** nhưng chưa cho phép chạy: `B−A` thử lựa chọn cửa sổ đầu truyện so với sampler gốc; `D−C` thử tương tự dưới loss có trọng số; `(D−B)−(C−A)` là tương tác. Đó **không** phải so sánh tăng quy mô corpus hoặc chất lượng semantic annotation. B/D chưa đủ khả năng thực thi và không có phê duyệt khoa học; không tự đổi quy mô hai thành bốn arm.

**Ngưỡng ra quyết định khi có dữ liệu thật:** không dự đoán rằng C chắc chắn cải thiện; nếu A/C FAIL thì giữ kết luận trong đúng phạm vi can thiệp, không lấy FRESH16 FAIL làm lý do đổi tiêu chí hậu nghiệm. Nếu C có điểm tương đối cao hơn A nhưng vẫn thấp tuyệt đối, phân biệt `relative intervention effect` với `useful prompt adherence`; không tự tuyên bố mô hình đã sẵn sàng sử dụng.

## 4. Gói thiếu điều kiện AC — duy nhất, không tách micro-permit

Nguồn AC tại GitHub HEAD `837289fda82b41653a61b74e476f76a0b4c4137c`; biên bản AC `NO_GO_PREEXEC_EXTERNAL_AND_NATIVE_GATES_OPEN`, Git blob `0c83b23c13c588a7787dd64a6c3d9ed5da22c5ce`. Các kiểm nguồn đã PASS không lặp lại.

Một gói tổng hợp phải được **agent AC và chủ dự án**, không phải nhánh này, hoàn tất trước khi có thể xem xét huấn luyện A/C:

1. Xác nhận quyền của chủ dự án đối với private TRAIN/VAL pack đã khóa và xác nhận lưu giữ riêng tư khóa niêm phong AC, không gửi khóa vào GitHub.
2. Danh tính và tính độc lập của người chấm FINAL24; quy trình khóa điểm trước giải mù và quyền sử dụng dữ liệu đã xác nhận.
3. Biên nhận QA native Windows Python 3.12 V2 **thực sự chạy**; không suy từ lỗi stderr PowerShell V1 rằng mô hình FAIL hoặc từ các kiểm tổng hợp rằng native PASS.
4. Bằng chứng FP16 T4 zero-step smoke và parity khôi phục từ ngắt giữa chừng trên mô hình gốc (actual interrupted resume parity); hai phép này là kiểm **môi trường/thực thi**, không phải quyền chạy train khoa học.
5. **Một quyết định cuối duy nhất** của chủ dự án cho khoa học A/C, theo kết quả gói trên. Nếu còn thiếu => `AC_TRAINING=HOLD`.

Không yêu cầu FRESH16 PASS làm điều kiện AC; FRESH16 đã có kết quả âm tính và **không được chạy lại**. Không tạo thêm toy hoặc thí nghiệm kiểm nguồn chỉ để kéo dài chuỗi giấy phép.

## 5. Ranh giới bất biến và chứng cứ

- Chỉ commit **báo cáo quyết định và receipt công khai** trên `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`; không sửa nhánh FRESH16/AC.
- Nhánh FRESH16 đã có cập nhật `lineage.md` riêng (L0015) theo biên bản agent. **Nhánh hậu CF1 và `main` không được chỉnh `lineage.md` trong lượt này**. Không lấy kết luận thiết kế này làm entry PASS/FAIL khoa học mới.
- Giữ nguyên T4 VAL H1 PASS; FRESH12 WEAK_ADHERENCE_SCOPED; CF1 FAIL_SCOPED_PRESERVED; FRESH16 nay là FAIL_SCOPED; AC là NO_GO_PREEXEC; O1=DEFER.
- GitHub `main` quan sát `5d52e32f20021e36f08f284ef9864d3ba36dbead`; PR #13 DRAFT, NOT MERGED; không merge/fetch/sync/cleanup worktrees. Không mở hoặc chấm lại TEST, Q1/Q2, FRESH12, CF1; không xem nội dung private S1/S2/FRESH16 mapping.
- Không thực thi GPU, huấn luyện hoặc suy luận **trong lượt quyết định này**. `FRESH16_CPU32_ALREADY_EXECUTED_EXTERNALLY=TRUE` là công việc đã hoàn thành trên nhánh agent, không thuộc hành động của nhánh hậu CF1.

## 6. Bước thực hiện tiếp theo

`TTM_SMALL4M_POST_CF1_AC_TWO_ARM_SUCCESSOR_DECISION_READBACK_AFTER_OWNER_SINGLE_PREEXEC_CLOSEOUT`

Nhánh hậu CF1 **chỉ theo dõi** khi agent AC đã đóng gói duy nhất toàn bộ điều kiện rights + custody + reviewer + Windows native V2 + T4 smoke/resume và có quyết định GO/HOLD khoa học. Sau đó đối chiếu `C−A` với hợp đồng gốc; nếu chưa chạy thì tiếp tục HOLD. Không mở B/D, O1 hoặc thử nghiệm thứ ba để bù cho FRESH16 âm tính.

**Trạng thái kết thúc:** `PRIORITY_1_FRESH16=COMPLETE_FAIL_SCOPED` · `PRIORITY_2_AC=NEXT_READINESS_ONLY` · `AC_TRAINING=NO_GO_PREEXEC` · `B/D=DEFER` · `O1=DEFER` · `NEW_TRAINING_THIS_TASK=NO` · `NEW_INFERENCE_THIS_TASK=NO` · `GPU_THIS_TASK=NO` · `TEST_Q1Q2=UNTOUCHED` · `MAIN/POST_CF1_LINEAGE=UNMODIFIED` · `PR13=DRAFT_UNMERGED`.
