# Ma trận nghiên cứu TTM / CLDP từ Dive into LLMs — đánh giá source-only

**Ngày:** 2026-11-16 · **Upstream pin:** `f84c04268794ef94f8949808bbc14ab8636763a0` · **Kết luận:** `RESEARCH_IDEAS_ONLY / NO_NEW_QUESTION_REGISTERED / NO_SCIENCE_PERMIT`

## Framework đã chọn

- **5W1H:** xác định câu hỏi nào giúp thay đổi một quyết định hiện có, thay vì “học mô hình mới vì hay”.
- **Falsification + causal controls:** mỗi hướng phải có đối chứng đủ phân biệt lỗi do dữ liệu, objective, đo lường, kiến trúc và runtime.
- **Pugh/MCDA định tính:** ưu tiên theo (i) khả năng thay đổi quyết định, (ii) khả năng kiểm chứng/bác bỏ, (iii) readiness quyền dữ liệu/gold, (iv) chi phí, (v) mức độ phù hợp scope. Không biến đánh giá chủ quan thành bằng chứng thực nghiệm.
- **FMEA / hard veto:** không vượt các điều kiện quyền nguồn, privacy, source/ontology, representativeness/coverage, effective-view parity, scorer/rater, checkpoint, ngân sách hoặc owner permit. Điểm tổng không thể ghi đè hard veto.

## Ma trận lựa chọn

| Ưu tiên | Hướng / liên hệ chương | Câu hỏi thực chất | Bằng chứng phân biệt nhỏ nhất | Readiness và phán quyết |
|---|---|---|---|---|
| P1 | **CLDP Phase3F-R compact capability**; Ch.3 về locality | Có thể giảm biểu diễn/tài nguyên mà giữ hành vi Mealy8 quan sát được trên miền đã khóa? | Đối chiếu exact functional equivalence (traces, trạng thái, negative cases), resource envelope, test độc lập | **GO_SCOPED_RESEARCH_PREPARATION đã được owner định phạm vi**; chỉ source implementation/function QA/resource preexec khi qua gate riêng, không chứng nhận science |
| P2 | **TTM rights/ontology/coverage/parity/gold**; Ch.1–4 | Bằng chứng thiếu nào thực sự thay đổi quyết định KEEP/SIMPLIFY/PIVOT/STOP? | Khép kín nguồn và quyền; ontology; mẫu số/coverage; full effective-view parity; independent rater calibration; ước lượng chi phí trước model run | **HOLD empirical**; ưu tiên source/protocol evidence, không tái chạy dữ liệu hoặc sealed TEST |
| P3 | **TTM data vs objective vs capacity**; Ch.1, Ch.2, Ch.4 | Lỗi tuân thủ prompt ở Small4M đến từ data/label, objective, decoding hay giới hạn năng lực? | Thiết kế equal-budget controls, matched prompts, null/negative controls, precommitted metric; trước hết paper/source-only | Chưa đủ rights/gold/checkpoint; không cấp F0/F2 science hoặc Q mới |
| P4 | **CLDP locality & out-of-domain behavior**; Ch.3, Ch.10 | Một can thiệp chức năng có làm hỏng những hành vi ngoài đích hoặc vỡ dưới biến thể đầu vào? | Perturbation tối thiểu + target/non-target traces + OOD held-out; giữ cố định baseline/cost | Chỉ là candidate design cho gate sau; không nhập kiến trúc LLM vào CLDP |
| P5 | **TTM–CLDP adaptive compute**; Ch.2, Ch.4, Ch.11 chỉ tham khảo | Compute được điều tiết theo độ khó có tăng chất lượng trên cùng information/compute budget? | Baseline fixed-compute vs adaptive; difficulty proxy khóa trước; test phản ví dụ; cost/latency/energy | **DESIGN_ONLY**, chưa đăng ký hay thực thi |
| P6 | **RLHF/PPO trực tiếp**; Ch.11 | Có đủ dữ liệu preference/reward model để tối ưu thực sự? | Cần nguồn/rights, rater agreement, reward hacking control, causal metrics và compute | **DEFER**; không phù hợp TTM-4M hiện tại |

## Hai lưu ý chống suy diễn sai

1. Chương 4 upstream sử dụng **Qwen2.5-Math-1.5B**, DeepMath-103K; README yêu cầu **GPU ít nhất 40 GB VRAM và khoảng 50 GB dung lượng**. Không tương đương ngân sách TTM-Small-4M/Colab T4, cũng không chứng minh 4M có hoặc thiếu reasoning chỉ qua scale.
2. Chương 11 là thực hành PPO/RLHF trên mô hình và reward khác, không phải kết quả nhân quả về Transformer hoặc CLDP. Ví dụ đọc tài liệu để hình thành hypothesis, không kéo thẳng notebook vào runner TTM.

## TTM: quyết định theo 5 phương án

| Option | Điều kiện áp dụng sau khi có evidence |
|---|---|
| KEEP | Gốc lỗi đã loại trừ được, kiểm tra cho thấy baseline phù hợp mục tiêu |
| SIMPLIFY | Đối chứng cho thấy phần phức tạp không đem lại incremental benefit |
| PIVOT | Có bằng chứng đối chứng ủng hộ data/objective/architecture khác vượt baseline tại budget ngang nhau |
| STOP | Mục tiêu bất khả thi hoặc cost/rights khiến study không còn giá trị |
| HOLD_EVIDENCE_INSUFFICIENT | Hiện tại: nhiều hard veto của P0-A chưa vượt; không thể coi tutorial là bằng chứng được thay thế |

## CLDP: giới hạn khái niệm

Chuyển giao **nguyên tắc kiểm thử** từ Knowledge Editing: `reliability` (đúng hành vi đích), `generality` (đúng trên các biến thể hợp lệ), `locality` (hành vi không đích không đổi). Nhưng Mealy8 và Layered Blackboard không có cùng ontology/kiến trúc như LLM; cần định nghĩa lại trên state trace, transition, episode và invariant, tránh coi analogies là kết luận khoa học.

**Gate Phase3F-R trước khi chạy science:** source pinned, exact compact implementation, functional-equivalence positive/negative QA, resource preexec, independent source QA, owner admission. Không mở rộng phase từ ví dụ giáo trình.

## Bước thực hiện tiếp theo — duy nhất

`TTM_CLDP_DIVE_INTO_LLMS_LEARNINGBOOKS_RIGHTS_SOURCE_MAPPING_AND_DISTINCT_DOCS_QA_SINGLE_GATE`

Đánh giá việc xin quyền công bố bản dịch; đối chiếu upstream exact commit/chapters, phân loại nội dung được tham khảo so với nội dung cấm sao chép, QA độc lập bản ghi học tập và ma trận câu hỏi. Chỉ xem xét PR tài liệu sau khi có quyền và QA đúng phạm vi. Không tạo Question Gate nghiên cứu, không thực thi mô hình, không sửa `lineage.md`.
