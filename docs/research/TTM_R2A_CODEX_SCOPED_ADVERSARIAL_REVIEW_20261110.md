# TTM R2A — Phản biện độc lập bằng Codex AI về lối tắt và ma trận O0/O1

**Ngày thực thi:** 2026-11-11. **Reviewer:** `CODEX_AI_INTERNAL` (phiên riêng, không đại diện cho kiểm định bên ngoài bởi con người).
**Nguồn được khóa:** `minhtri22/TokenToModel-Lab`, `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`, HEAD GitHub xác minh lúc mở review `c85b2ab504953bd667f09909f3495c4772fd1b2e`.
**Mã thực thi:** `tools/research/semantic_state_r2/r2a_codex_adversarial_qa_20261111.py`.
**Phạm vi:** nguồn R2A công khai và CPU QA. Không sử dụng checkpoint, TTM TRAIN/VAL/TEST, Q1Q2, Colab, GPU hoặc mô hình neural.

## 1. Kết luận phân xử

| Hạng mục | Phán quyết | Ý nghĩa |
| --- | --- | --- |
| 10 Git blobs/SHA-256 trong manifest nguồn | `PASS_10/10` | Đối chiếu trực tiếp tệp đã checkout từ commit được khóa. |
| Bộ kiểm thử tác giả | `PASS_36/36` | Tái chạy bằng Python 3.12.10 trên CPU. |
| Cặp phản thực, vị trí và question binding | `PASS_SCOPED` | 128 cặp A/B, 128 query-swap, 384 input được kiểm lại từ visible text. |
| Trường `story/question` ở từng record canonical | `PASS_SCOPED` | Bản đầu vào nguyên gốc không có nhãn ở cấp record. |
| Kiểm định schema cho toàn bộ model JSON | **`FAIL_SCOPED`** | Checker chấp nhận ba biến thể rò nhãn/metadata ở cấp top-level. |
| Tuyên bố nguồn oracle là `sealed FINAL` | **`FAIL_SCOPED`** | Checker chấp nhận thay trường `declaration` thành nội dung sai. |
| Nhu cầu có biểu diễn trạng thái học được | `NOT_DEMONSTRATED` | Thuật toán tìm gán cuối theo khóa giải đúng `384/384`. |
| Công bằng đối chứng O0/O1 | `HOLD_DESIGN_ONLY` | Các nhánh B/C/E chưa tương đương về giám sát, dung lượng và tính toán. |
| Lợi ích O1 so với O0 | `NOT_TESTED` | Không có huấn luyện hoặc đánh giá neural nào trong R2A. |

**Phán quyết khoa học:** `R2A_VALID_SCOPED=PASS_WITH_VALIDATOR_HARDENING_REQUIRED`, `R2A_INPUT_SCHEMA=FAIL_SCOPED`, `FAIR_SUPERVISION=HOLD_DESIGN_ONLY`, `NEURAL_GAIN=NOT_TESTED`.

R2A vẫn chứng minh được giới hạn của bag-of-words (trên từng cặp A/B, cùng multiset từ nhưng đáp án khác, tối đa đúng 128/256). Kết quả này chưa buộc mô hình cần một module trạng thái mới, vì Transformer có vị trí và một bộ giải văn bản theo quy tắc đều có thể tận dụng thứ tự cập nhật.

## 2. Phát hiện về mã và bộ kiểm định

### [HIGH] R2A-01 — Rò nhãn qua top-level model JSON được chấp nhận

Trong `r2a_independent_checker.py` dòng 77–82, checker xác minh schema, danh sách bản ghi và hai trường của **mỗi bản ghi**, nhưng bỏ qua tập khóa của chính đối tượng `model`. Đột biến độc lập ghi nhận:

| Đột biến | Checker chấp nhận? | Kết luận |
| --- | --- | --- |
| `model.answer_vector = [384 nhãn]` | **ACCEPT** | Bypass rò nhãn. |
| `model.oracle = toàn bộ oracle` | **ACCEPT** | Bypass rò nhãn/source-events. |
| `model.split = [384 split]` | **ACCEPT** | Bypass metadata. |
| `model.records[0].answer = ...` | REJECT | Phạm vi record đang được bảo vệ. |
| `model.records[0].split = ...` | REJECT | Phạm vi record đang được bảo vệ. |

Đây là lỗ hổng **checker nhận nhầm đầu vào đã bị chèn dữ liệu**. Bộ `R2A_MODEL_INPUT_ONLY.json` canonical khớp đúng projection và không có các trường trên. Không suy diễn rằng tệp canonical đã rò nhãn ở top-level.

**Điều kiện đóng:** kiểm `type(model) is dict` và `set(model) == {'schema', 'records'}` trước projection, sau đó bổ sung negative tests cho mọi trường top-level lạ. Tất cả input được chuyển cho model/trainer phải được nạp từ đúng bản projection đã hash, không từ object chứa oracle.

### [MEDIUM] R2A-02 — Tuyên bố `sealed FINAL` không được kiểm chứng

Checker bắt buộc đúng các **tên trường** của oracle tại dòng 76, nhưng không ràng buộc nội dung `dataset['declaration']`. Thay thành `Sealed FINAL TEST with hidden labels` vẫn được ACCEPT. Mã gốc tạo lời tuyên bố public-toy chính xác tại `r2a_generator.py` dòng 126.

**Điều kiện đóng:** cố định literal declaration hoặc bắt buộc manifest nguồn/receipt nêu `labels_public=true`, `sealed_final=false` và khóa SHA. Từ chối claim sai trên cùng kênh kiểm định. Vẫn giữ bằng chứng FAIL này trong lịch sử QA.

### [MEDIUM] R2A-03 — Cấu trúc bài toán vẫn có lời giải heuristic 100%

Một parser độc lập chỉ dùng **văn bản** lấy `key` từ câu hỏi, chọn sự kiện cuối cùng gán cho `key`, xuất `value`. Nó đạt **384/384**, gồm 256 truyện A/B và 128 query-swap. Không cần `source_events`, oracle, mô hình học hay bộ nhớ latent. Trên cả 384 hàng, chọn luôn câu cuối đạt 192/384, câu ba 124/384, lấy **lần gán đầu** cho khóa được hỏi đạt 0/384. Các con số sau chỉ mô tả dữ liệu hiện tại.

Ngữ pháp mỗi family có hai keys, mỗi key đúng hai phép gán trực tiếp và bốn giá trị khác nhau. Truyện gồm đúng bốn câu. `CHALLENGE` dùng template công khai theo split. Đây là một bài **tìm gán theo khóa và thứ tự** (keyed latest assignment), chưa đòi hỏi liên kết gián tiếp, trạng thái nhiều bước hoặc suy luận mục tiêu phức tạp. Không thể dùng điểm 384/384 này để quy lợi ích cho O1.

### [MEDIUM] R2A-04 — Thứ tự record và query-swap khiến phép chia ngẫu nhiên không hợp lệ

Đã xác nhận **128/128 cặp A/B nằm kế nhau**, toàn bộ 128 probe ở phần sau, và **128/128 probe dùng lại đúng story của A** (xem `r2a_generator.py` dòng 114, 129). Bản công khai chứa cùng story với hai question và có thứ tự nối oracle có nhãn. Dùng shuffle ở cấp hàng để chia TRAIN/VAL có thể đặt bản sao hoặc biến thể phản thực của cùng nhóm vào hai phía, tạo kết quả đánh giá lạc quan.

**Điều kiện đóng:** khóa split theo toàn bộ nhóm `pair_id` gồm A/B/Q, và kiểm thêm sự giao nhau của story, biến thể và đồ thị sự kiện giữa các split. R3 cần chia theo **cấu trúc đồ thị** (structural split), không chỉ theo tên key hay cách diễn đạt. `CHALLENGE` R2A công khai không thể là blind FINAL.

### [MEDIUM] R2A-05 — Thiếu ô B + query-swap

Mỗi nhóm đang có ba ô A+key1, B+key1, A+key2. Thiếu ô thứ tư B+key2, tức chưa thử đối chứng đầy đủ 2×2 của **hoán đổi cập nhật × thay câu hỏi**. Đây là thiếu sót về độ bao phủ phản thực, dù 128 probe hiện có vẫn hợp lệ. R3 nên có đủ bốn ô và các trường hợp thay một sự kiện liên quan/không liên quan.

### [LOW] R2A-06 — QA tác giả và source-independent QA có phạm vi khác nhau

36 unit tests gọi `r2a_generator.build()` trong bộ nhớ. Review bổ sung đã đọc **10 tệp chính thức có commit** và đối chiếu SHA-256, Git blob, parser từ visible text. Kết quả `PASS_36/36` của tác giả đúng với bộ test đó, nhưng tự nó chưa chứng minh validator từ chối mọi dạng chèn metadata, như R2A-01 đã chỉ ra.

## 3. Ma trận O0/O1 — những đối chứng còn thiếu

Đã đọc thiết kế 5 nhánh và JSON matrix tại HEAD được khóa.

| Nhánh | Supervision | Vấn đề nhận dạng nguyên nhân |
| --- | --- | --- |
| **A — O0-CE** | CE văn bản gốc | Mốc chuẩn, phải khóa checkpoint/seed. |
| **B — O0-STATE-TEXT** | CE + state/goal biểu diễn thành token | Thêm số token, teacher forcing, entropy và cơ hội cập nhật khác C. |
| **C — O1-TRUE** | CE + auxiliary head với nhãn đúng | Là nhánh ứng viên nhưng thắng B chưa tự cô lập hiệu ứng kiến trúc. |
| **D — O1-SHUFFLED** | CE + nhãn head hoán vị | Có thể gây gradient nhiễu và làm hại D, nên C > D là chẩn đoán, không đủ chứng minh O1. |
| **E — O0-CAPACITY** | CE + adapter hoạt động, không có state labels | Khớp tham số/FLOPs với C nhưng khác lượng thông tin TRAIN. C > E là hiệu ứng tổng hợp. |

**[HIGH] R2A-07 — Thiếu cặp vừa capacity-matched vừa supervision-matched.** B có nhãn nhưng khác số tham số hoạt động và ngân sách. E có dung lượng nhưng thiếu nhãn. Không tồn tại một phép so sánh duy nhất trong A–E vừa khớp **nguồn thông tin TRAIN** vừa khớp **dung lượng/tính toán** để suy ra lợi ích riêng của auxiliary state head. Thiết kế hiện đã thừa nhận rủi ro này nên phán quyết phù hợp là `FAIR_SUPERVISION=HOLD_DESIGN_ONLY`, không tự xếp O1 thắng.

**Sửa ở mức tiền đăng ký:** thêm **F — O0-CAPACITY+STATE-TEXT** nếu mục tiêu là suy luận mạnh về architecture. F dùng adapter hoạt động tương đương E nhưng nhận supervision dạng văn bản như B. C và F vẫn khác cách biểu diễn loss, vì vậy phải khóa và công bố rõ hai tầng budget: (1) số ví dụ/nhãn oracle và số text tokens nhìn thấy, (2) tổng FLOPs thực đo và thời gian GPU. Nếu chỉ đủ chi phí cho A–E, hạ giới hạn claim thành **so sánh hiệu quả có điều kiện giữa các objective/architecture**.

Trước science, tiền đăng ký chính xác nguồn TRAIN-only oracle, dữ liệu/chia nhóm, baseline O0 được chọn **trước khi nhìn kết quả**, cùng tokenizer/checkpoint P02 và trạng thái optimizer được đối chiếu, cách cân bằng gradient/loss weight, tổng/trainable/active parameters, số target tokens, FLOPs, peak VRAM, seed lặp, cùng thước đo primary và tiêu chí FAIL. `oracle_at_inference=0`. Không được dùng public R2A để lựa chọn siêu tham số rồi gọi R2A là xác nhận độc lập.

## 4. QA đã thực thi và nguồn bằng chứng

- Thực thi PowerShell 5.1 và Python 3.12.10. GitHub branch HEAD đã được đối chiếu `git ls-remote` với exact commit `c85b2ab...` trước khi tạo worktree riêng trong project root.
- Kiểm đủ **10/10** hiện vật trong `R2A_COMPLETE_GITHUB_CUSTODY_MANIFEST_20261110.json` bằng size, SHA-256 và Git blob. Canonical oracle `3243d1eaae4b8727449fe4571dc81c898414b5ba300a20e7ead0819d7953286e`, input `72f57d704a2e4f99f06a797b8b647d93736a7093852e0c9df0f28dc59549032d`.
- Chạy lại **36/36** unit tests tác giả. Checker độc lập từ visible text đạt **384/384**. Chạy **11** đột biến validator, quan sát **4 ACCEPT gây bypass** và **7 REJECT đúng kỳ vọng**.
- Receipt `artifacts/qa/ttm-r2-semantic-toy/codex-review-20261111/TTM_R2A_CODEX_ADVERSARIAL_QA_RECEIPT_20261111.json`, SHA-256 `bcc8cd8ea3a8fded307e0c6ad1b3175bbd484d4603a98b6c8fb448e48cba7326`.
- Raw original test log `original_36_stderr.txt` SHA-256 `fc820c32a2d10ee7538eb3e1d760180de4fa3e99b3637fe2869a1ea0a3720cef`, independent QA log `codex_qa_stdout.txt` SHA-256 `0f7b8c3f91c1c2f0f2bacdc5f62353d58287248191a520524c7b216f9ae6534b`, cùng thư mục receipt.
- Independent QA script SHA-256 `e622954dc1d988d270a74a716a8de6ea438df86caa6b3f4fe83d2beeb9d0a5f0`. Script không import generator cho diễn giải văn bản, chỉ import original checker để kiểm thử đột biến.

QA này chứng thực các quan sát được ghi tại commit nguồn đã khóa. Kết quả khoa học O0/O1 vẫn đang ở trạng thái `NOT_TESTED`.

## 5. Một quyết định đề xuất cho chủ dự án

**`DESIGN_R3_BEFORE_O1`**.

Giữ O0 2×2 làm baseline theo trạng thái đã khóa. Đầu tiên sửa schema của checker và ghi negative tests. Thiết kế R3 có counterfactual bốn ô, nhiều thực thể và chuyển giao quan hệ nhiều bước, coreference, sự kiện nhiễu, cập nhật/hủy mục tiêu, split theo đồ thị và FINAL kín được escrow trước science. Đặt heuristic `key-aware recency`, rule interpreter và P02/O0 dưới cùng điều kiện đánh giá. Chỉ sau khi có R3 đủ sức phân biệt và ma trận giám sát–dung lượng–compute hợp lệ mới trình một quyết định mở thực nghiệm O0/O1.

**Bước thực hiện tiếp theo:** `TTM_R2A_CODEX_REVIEW_ADJUDICATE_THEN_R3_STRUCTURAL_STATE_TRACING_SCIENCE_DESIGN_OR_KEEP_O0`.
