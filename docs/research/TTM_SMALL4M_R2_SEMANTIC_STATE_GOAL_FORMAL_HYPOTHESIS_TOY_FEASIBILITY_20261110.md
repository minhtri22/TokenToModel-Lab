# TTM-Small-4M — R2: ngữ nghĩa trạng thái/mục tiêu, toy feasibility không huấn luyện

**Nhiệm vụ:** `TTM_SMALL4M_SEMANTIC_STATE_GOAL_FORMAL_HYPOTHESIS_AND_NO_TRAINING_TOY_FEASIBILITY`  
**Ngày:** 2026-11-10 · **Source of truth:** `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`.  
**Kế thừa:** R1 commit `fe3e2851019f8ea5ed5219dcf022a4f2cb515fd3` (khảo cứu GPT-2, Llama 4, TTM và nền tảng triết học).  
**Phạm vi tuyệt đối:** chỉ truyện tổng hợp tự tạo và chương trình logic Python chuẩn, **không dùng mô hình TTM hoặc dữ liệu TinyStories**, không train, không inference LLM, không TEST/Q1Q2, không Colab, không chỉnh P02, không mở P09/P10.

## 1. Giả thuyết có thể bác bỏ

**H-ORDER:** Chỉ tập từ và tần suất từ (*bag of words*) không đủ để trả lời truy vấn khi thứ tự cập nhật trạng thái thay đổi; nếu hai văn bản có cùng multiset từ và cùng câu hỏi nhưng hai đáp án đối lập, mọi hàm quyết định chỉ phụ thuộc multiset từ sẽ phải trả lời giống nhau cho cả hai. Với các cặp đáp án cân bằng, độ chính xác tối đa cho bộ phân loại loại này là **50%**.

**H-STATE:** Có thể định nghĩa một trạng thái tối thiểu `S_t = (owner_t, goal_t)` và cập nhật xác định từ các sự kiện:
- `ASSIGN(object, person)`: `owner[object] = person` (quyền sở hữu là quan hệ ký hiệu, **không** suy diễn cơ học/định luật vật lý).
- `SET_GOAL(person, action)`: `goal[person] = action`.
- Với một khóa (object/person), lần cập nhật **sau cùng có liên quan** quyết định câu trả lời. Một sự kiện về khóa khác được xem như nhiễu, không làm thay đổi khóa đang được hỏi.

\[
S_{t+1}=U(S_t,e_t).
\]

**H-LEARNING (chưa thử):** Một đầu phụ theo dõi trạng thái hoặc bộ nhớ quan hệ có thể giúp TTM 3,75M tham số sinh tiếp nối đúng tình huống so với chỉ huấn luyện next-token CE khi được kiểm soát tổng token/compute và thông tin giám sát. **Toy này không kiểm chứng H-LEARNING**, không chứng minh TTM không thể học theo thứ tự vì GPT-2/TTM có vị trí token và attention.

## 2. Hợp đồng toy nhỏ: 128 cặp / 256 truyện

- 8 tên nhân vật, 6 vật thể, 8 mục tiêu văn bản; nguồn tự định nghĩa, không sao chép dữ liệu riêng tư.
- **64 cặp quan hệ sở hữu**, **64 cặp mục tiêu nhân vật**; mỗi cặp 2 bản A/B.
- Mỗi bản **4 sự kiện**, sự kiện thứ nhất và thứ ba cập nhật cùng đối tượng hỏi; thứ hai và thứ tư cập nhật một đối tượng/nhân vật khác. Bản B chỉ **đảo sự kiện 1 ↔ 3**; câu hỏi và hai sự kiện nhiễu giữ nguyên.
- Cùng multiset từ, cùng số token dạng regex, cùng số sự kiện và câu hỏi trong mỗi cặp. Đáp án A/B đối lập. Phân `DEV` 32 cặp và `CHALLENGE` 32 cặp **mỗi họ**. **CHALLENGE công khai, không được xem là blinded held-out TEST**. Không dùng bất kỳ bản toy nào sau này làm BLIND_FINAL nếu người đánh giá đã đọc nhãn.
- Generator lấy ground truth từ **event tuples**; checker độc lập tính đáp án từ **4 câu tiếng Anh hiển thị**, không gọi hàm `state()` của generator và không dùng trường `source_events` làm nhãn.

**Ví dụ:** A: “Minh plans to write a note. An plans to find the ball. Minh plans to help a friend. An plans to read the book.” → mục tiêu Minh = *help a friend*. B đảo hai câu về Minh → mục tiêu Minh = *write a note*. Từ xuất hiện không đổi, trạng thái cuối đổi.

## 3. Kiểm định đã thực hiện ở môi trường Python riêng

**Mã đã thực thi**, và Git blob của cả hai file đã được so nguyên byte với nguồn local:
- [r2_runtime_integration_executed.py](../../tools/research/semantic_state_r2/r2_runtime_integration_executed.py) Git blob `4d78819e9ee7c602b7fd461a346819abd42bda1e`.
- [negative_test_runner.py](../../tools/research/semantic_state_r2/negative_test_runner.py) Git blob `965def98940984bb5f073aa275102336f9e2bad6`.
- Mã generator riêng và checker độc lập đầy đủ: [generator](../../tools/research/semantic_state_r2/r2_semantic_toy_generator.py), [checker](../../tools/research/semantic_state_r2/r2_independent_visible_text_checker.py) — **được commit nhưng chưa chạy nguyên byte ở lượt này**; Codex được yêu cầu kiểm tra chéo chính hai source này.

**Kết quả thực thi:** `256/256` đoạn được visible-text parser tính đúng theo nhãn event generator; đối chứng lexical không đọc thứ tự trả lời đúng `128/256 = 50%`. `128/128` cặp đối lập và có multiset từ chính xác như nhau. `21/21` ca mutate/negative bị checker từ chối. Thử sửa `source_events` mà không sửa văn bản **không làm thay đổi kết quả**, chứng minh checker được viết để chỉ đọc text/question khi xác định đáp án.

- File dataset JSON 200.630 byte; SHA-256 **`f20915ff0559b32786961b4a19fa3dce3858cb95d18beaee1fc77ab79cb3cb08`**. Có thể tái dựng bằng `python tools/research/semantic_state_r2/r2_runtime_integration_executed.py` trong một thư mục làm việc mới; mã mặc định ghi `dataset.json` và `local_integration_qa.json` cùng nơi mã. Tránh ghi đè hiện vật gốc; clone checkout ở vị trí kiểm tra riêng bên trong project workspace.
- QA runtime JSON SHA-256 `ba763faf7b4de3d6b0631da412f64ff15c49b8aac7ff339c01e8eff38ca3a677`.
- Negative QA JSON SHA-256 `6347fca61c27186e40f84b5dc21e0c5231c013fea656870467489f34c774b448`.

**Lưu ý mức độc lập:** checker so văn bản là code độc lập với hàm oracle structured, nhưng cùng tác giả và cùng đặc tả công khai. Không được gọi “external independent scientific verification”. Một số mutation bất thường ở bản test runtime hiện được từ chối bằng exception gốc thay vì một loại lỗi xác định; Codex có thể đề xuất hardening nhưng không được xóa FAIL lịch sử.

## 4. Diễn giải khoa học và ranh giới triết học

**PASS_TOY_FORMAL_FEASIBILITY:** phép đo có thể mô tả bằng quan hệ trạng thái động và có thể phân biệt thông tin có thứ tự với mô hình chỉ dựa trên thống kê từ; ngữ pháp, parser và bộ tạo cặp có thể kiểm tra bằng chương trình.

**KHÔNG PASS semantic architecture:** chương trình giải đúng vì luật và nhãn được thiết kế trước; một quy tắc đơn giản “lấy cập nhật gần nhất về thực thể được hỏi” đã đủ giải bài. GPT-2/TTM **không phải bag-of-words**; không có lần chạy inference TTM nào ở R2. Vòng này **không chứng minh** tăng accuracy, NLL, hay năng lực suy luận của GPT, và không đòi hỏi giả thiết về vật lý, consciousness hay intrinsic grounding.

Hai việc chưa giải quyết: (a) các câu grammar quá khuôn mẫu, chưa có đại từ/quan hệ nhiều bước/chuyển giao sở hữu phức tạp; (b) labels và chương trình update là nguồn thông tin giám sát mới nếu dùng làm auxiliary loss. Nếu không điều chỉnh ngân sách supervision, việc O1 thắng O0 sẽ không được quy cho kiến trúc.

## 5. Phương án kế tiếp và tiêu chí quyết định

| Phương án | Điều kiện | Quyết định R2 |
|---|---|---|
| O0: giữ P02, 2×2 data-sampler × suffix CE | Runner/rights/reviewer từ nhánh 2×2 chưa mở science | **BẢO TOÀN HOLD**; là baseline |
| O1: P02 + entity/goal auxiliary objective | Cần nhãn từ oracle, đối chứng supervision công bằng, param/compute audit | **Ứng viên để thiết kế đối chứng tiếp**, chưa train |
| O2: thêm state slots/bộ nhớ quan hệ | Phức tạp hơn, không có bằng chứng cần thiết hơn O1 | Tạm hoãn sau O1 |

**Đề nghị:** gửi Codex một vòng **phản biện lý luận và audit code R2 chỉ đọc**, không chấm mù và không đổi kết quả; khi có đánh giá, quyết định cùng chủ dự án chọn **O0-only** hoặc **O0+O1 với đối chứng supervision/compute**. Không mở GPU, không cấp phép vi mô.

## 6. Bảo toàn governance

R2 được tách nhánh từ R1 `fe3e285…`, không dựa trên HEAD main mới; khi kiểm tra trước khi tạo nhánh, `main` đã **tiến tới `df126b2d4beaee865faa24d8a7e9720bb59693aa`** (khác main lịch sử `b57b…`). **Không được khẳng định `main` vẫn ở `b57b…`; chỉ khẳng định R2 không ghi main**. PR #13 draft `8399406…`, nhánh 2×2 `ed2cfcd…` được giữ nguyên tại lúc bắt đầu R2; cần đọc lại exact HEAD khi ra quyết định tiếp theo. `lineage.md` main/PR13 có thể khác lịch sử; R2 không chạm lineage.

**Kết thúc R2:** `TOY_FORMAL_FEASIBILITY=PASS_SCOPED` · `NEGATIVE_QA=PASS_21/21` · `NEURAL_SEMANTIC_GAIN=NOT_TESTED` · `NEW_TRAINING=0` · `NEW_INFERENCE=0` · `TEST_Q1Q2=UNTOUCHED` · `CODEX=REVIEW_HANDOFF_READY_NOT_REVIEWED` · `2X2=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_R2_CODEX_ADVERSARIAL_THEORY_AND_SOURCE_REVIEW_THEN_O0_VS_O1_DECISION` (không Codex science-run).