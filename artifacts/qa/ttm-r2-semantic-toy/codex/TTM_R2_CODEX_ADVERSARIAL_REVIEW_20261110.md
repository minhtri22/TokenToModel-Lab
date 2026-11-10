# TTM-Small4M R2 — Codex adversarial theory/source review

**Ngày:** 2026-11-10. **Người rà soát:** Codex AI nội bộ.  
**Phạm vi:** đọc mã và tài liệu, chạy kiểm thử Python 3.12.10 trên nguồn công khai, đánh giá lý luận.  
**GitHub revision đã kiểm tra:** `b1325d61bac07587d07ac7b48b9ad47e4284f1a9`  
**Nhánh:** `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`.

## 1. Kết luận

- **Source/code:** `REVIEW_PASS_SCOPED`. Hai hiện thực sinh dữ liệu có kết quả bằng nhau đến từng byte. Kiểm toán dữ liệu, parser, và 21 negative mutations của mirror tái chạy thành công.
- **H-ORDER:** `R2_VALID_SCOPED` khi đầu vào chỉ gồm `story + question`, dùng bag-of-words không biết thứ tự. Chứng minh bằng đối chứng cặp là đúng.
- **H-STATE (khả năng theo dõi trạng thái tổng quát):** `HOLD_INSUFFICIENT_DISCRIMINATION`. Tất cả 256 đáp án suy được bằng một lối tắt đọc **câu thứ ba** và hoàn toàn bỏ qua câu hỏi. Bộ fixture hiện tại không phân biệt được quy tắc theo dõi trạng thái với ghi nhớ vị trí cố định.
- **H-LEARNING / cải tiến neural:** `NOT_TESTED`. Không có số đo inference/training cho O0/O1.
- **Quyết định nội bộ:** `R2_VALID_SCOPED` và `DEFER` việc triển khai khoa học O1 cho đến khi sửa thiết kế chẩn đoán. Giữ O0/2×2 làm đối chứng theo các gate riêng của nó. Không cấp quyền GPU hay mở science run.

## 2. Bằng chứng chạy lại

Đọc đúng commit và sao chép **nguyên byte** bốn script tới thư mục QA tách riêng trước khi chạy.

| Nguồn/đầu ra | SHA hoặc kết quả |
|---|---|
| Mirror runtime Git blob | `4d78819e9ee7c602b7fd461a346819abd42bda1e` |
| Negative runner Git blob | `965def98940984bb5f073aa275102336f9e2bad6` |
| Generator Git blob | `f1104bbb0a6f33833d8c5e48021d472deadc9779` |
| Separate checker Git blob | `c5b62a1ac3916ca36740e82efd4f9afbd248244a` |
| Mirror dataset và generator dataset | Cùng SHA-256 `f20915ff0559b32786961b4a19fa3dce3858cb95d18beaee1fc77ab79cb3cb08` |
| Kích thước mỗi dataset | 200.630 byte |
| Pairs, texts, independent visible parser | 128, 256, **256/256** |
| Bag-of-words order-invariant control | **128/256** |
| Exact multiset từ + cùng câu hỏi/độ dài/split | **128/128** cặp |
| Negative mutations của mirror | **21/21** bị từ chối |
| Separate checker audit SHA-256 (Windows hiện tại) | `a9f5911153f85132c916f5e657c04570ee2f73995c9f3a8e8f359237fc7c9167` |
| QA bổ sung 12 ca (9 từ chối, 3 chấp nhận đúng theo kịch bản) | SHA-256 `484358677a1ee9e6f3d6872fecaf061a99a0864b1dde8b31d10e751df6e531a9` |

**Sai khác SHA do xuống dòng Windows được phân giải.** `local_integration_qa.json` hiện có SHA `ab1a6ea044af4027751945c576caa7216eeac643d62f2d0ccc528d3c4ca0fbd1`, và `negative_audit.json` có SHA `67c28888fd02a5cf5d5c9eb9758f5d8661b5fd5d945140e8cb2f7d28c3995dd2`. Khi chuẩn hóa CRLF → LF, hai SHA lần lượt khớp chính xác SHA công bố `ba763faf7b4de3d6b0631da412f64ff15c49b8aac7ff339c01e8eff38ca3a677` và `6347fca61c27186e40f84b5dc21e0c5231c013fea656870467489f34c774b448`. Đây là khác biệt biểu diễn text, không phải sai khác kết quả logic.

## 3. Phát hiện ưu tiên

### HIGH — Lối tắt câu thứ ba đạt 100%, không cần đọc câu hỏi

Ở [generator dòng 86](https://github.com/minhtri22/TokenToModel-Lab/blob/b1325d61bac07587d07ac7b48b9ad47e4284f1a9/tools/research/semantic_state_r2/r2_semantic_toy_generator.py#L86), hai biến thể luôn có dạng `[target, distractor, target, distractor]`. Trong cả 256 truyện, câu 3 là cập nhật cuối cùng của đúng khóa được hỏi. Kiểm định trực tiếp bằng `third_sentence_answer(story)` không đọc question hay source_events đạt **256/256**. Quy tắc chọn câu 4 đạt 0/256 vì nó luôn là sự kiện nhiễu khác khóa.

Vì vậy, nhãn `independent_visible_text_oracle_correct=256` là bằng chứng tính nhất quán fixture/parser, chưa chứng minh có bài toán *key-binding* khó cho kiến trúc học. Thử các cấu hình ngôn ngữ vẫn gồm bốn câu đúng cú pháp nhưng chuyển cập nhật mục tiêu tới câu 4 hoặc hỏi khóa nhiễu ở câu 4 đều bị [checker dòng 81–83](https://github.com/minhtri22/TokenToModel-Lab/blob/b1325d61bac07587d07ac7b48b9ad47e4284f1a9/tools/research/semantic_state_r2/r2_independent_visible_text_checker.py#L81-L83) từ chối với `QUERY_VS_DISTRACTOR_POSITIONS`.

**Tác động:** H-ORDER vẫn đúng về bất khả phân biệt theo bag-of-words. Tuy nhiên, thí nghiệm hiện tại không nhận diện được liệu hệ thống thực sự học `S_t = (owner, goal)` hay chỉ học quy luật vị trí.

### MEDIUM — Phạm vi formalization hẹp hơn ngữ nghĩa diễn ngôn

Các câu `The X belongs to Y` và `P plans to G` là cú pháp hoàn toàn cố định. Quy tắc last-write-wins không xử lý phủ định, chuyển giao nhiều bước, đồng sở hữu, đại từ, tham chiếu đồng nhất, mục tiêu bị hủy bỏ, điều kiện, sự kiện gián tiếp hay suy luận từ trạng thái. Bộ 12 ca thêm đã xác nhận các biến thể ấy bị từ chối đúng như giới hạn grammar, không được chấm thành lỗi mô hình.

H-STATE có một hiện thực ký hiệu đúng cho ontology đã định. Điều này chưa kiểm tra giả thuyết mạnh của Wittgenstein về *meaning as use*, cơ chế tham chiếu diễn ngôn của Kamp/Heim, hay *plans/scripts* của Schank/Abelson. R2 đặt ra một khái niệm kỹ thuật nhỏ lấy cảm hứng từ các công trình đó.

### MEDIUM — Metadata trực tiếp chứa nhãn, cần khóa đường input ở thử nghiệm sau

Mỗi record hiện có `answer`, `source_events`, `variant`, `id`, `pair_id`, và `split`. Checker cố tình không dùng `source_events` để suy đáp án, điều này được kiểm tra. Chứng minh giới hạn 50% cho bag-of-words chỉ áp dụng với `story + question`. Nếu future training/inference nạp cả JSON record hoặc tiết lộ nhãn oracle, mệnh đề không còn là kiểm định công bằng. Không có bằng chứng R2 đã thực hiện neural training với metadata này.

### LOW — Declared counts không được đối chiếu với nội dung

Sửa `data['counts']['goal_DEV'] = 0` vẫn khiến `r2_independent_visible_text_checker.verify()` báo PASS, dù checker tự tính composition đúng 64. Mirror `check()` cũng không đối chiếu `counts` với records. Đây là thiếu kiểm định metadata, không ảnh hưởng SHA dataset gốc đã ghim. Nên harden trước khi dùng checker như validator của giao thức mở rộng.

### LOW — Negative QA 21/21 kiểm bản mirror, không tự chạy separate checker

[`negative_test_runner.py`](https://github.com/minhtri22/TokenToModel-Lab/blob/b1325d61bac07587d07ac7b48b9ad47e4284f1a9/tools/research/semantic_state_r2/negative_test_runner.py#L3) import `check` từ mirror runtime. Nó bắt một tập ngoại lệ rộng để tính một mutation là bị từ chối. Kết quả 21/21 là đúng cho **mirror**. Separate checker đã chạy thành công trên data gốc và chịu 12 case bổ sung, nhưng chưa có kiểm toán 21 mutation cùng bộ đối với `verify()`. Có thể hợp nhất test suite chéo trước khi khóa phiên bản R2 tiếp theo.

### MEDIUM — CHALLENGE thiếu dịch chuyển cấu trúc và không mù

Phép chia dựa trên `i < 32`, rồi sinh bằng cùng grammar, vocab và vị trí target. Do đó CHALLENGE không kiểm định tổng quát hóa sang vị trí sự kiện, cú pháp, tên thực thể mới hoặc quy tắc cập nhật mới. Tài liệu gốc đã ghi rõ đây là tập công khai, không phải BLIND_FINAL. Rủi ro xuất hiện nếu dùng nó để chọn O1 và sau đó báo kết quả như held-out confirmation.

## 4. Kết luận đối với từng giả thuyết

**H-ORDER:** PASS ở mức định lý trên cặp cân bằng. Đặt `φ(story, question) = (multiset(words(story)), question)`. Với mỗi cặp `φ(A)=φ(B)` nhưng `answer(A)≠answer(B)`, mọi hàm dự đoán chỉ phụ thuộc `φ` nhận cùng đầu vào trên A/B và tối đa đúng một trong hai. Điều này dẫn tới accuracy tối đa **50%** trên tập hai biến thể cân bằng. Phép chứng minh không áp dụng cho Transformer có positional embeddings, attention hoặc các cột metadata.

**H-STATE:** PASS đối với định nghĩa chương trình `U(S_t,e_t)` và khả năng diễn giải chuỗi sự kiện theo luật đã biết. HOLD với phát biểu mạnh hơn rằng các fixture buộc mô hình phải xây dựng biểu diễn trạng thái hay liên kết thực thể.

**H-LEARNING:** chưa đo. Điều kiện bác bỏ thực nghiệm trong tương lai cần preregister trước khi chạy, gồm hiệu quả O1 so với đối chứng cùng thông tin, tham số, FLOPs, tokens, seeds và checkpoint. O1 chỉ có tín hiệu thực chất khi thắng trên nhóm đã khóa trước gồm thay đổi vị trí cập nhật, nhiễu cuối, cập nhật chéo khóa, tham chiếu/tên chưa gặp. Nếu chênh lệch không tái lập, biến mất khi kiểm soát oracle supervision, hoặc chỉ xuất hiện trên template quen, không xác nhận lợi thế kiến trúc.

## 5. Thiết kế O0/O1 prospective ablation

Đề nghị thiết kế các nhánh dưới cùng checkpoint/tokenizer/story split, có thể đo chi phí thực và không cấp nhãn oracle làm input khi inference.

| Arm | Kiểm soát |
|---|---|
| A — O0-CE | Text-only next-token CE theo lịch gốc. |
| B — O0-SUPERVISED-TEXT | Cùng nhãn state/goal oracle ở TRAIN được mã hóa thành mục tiêu huấn luyện text phụ, cắt cân bằng tổng supervised targets và FLOPs. Tách tác dụng **thêm thông tin nhãn** khỏi đầu phụ. |
| C — O1-SHUFFLED | Cùng kiến trúc/head/compute với O1, nhưng nhãn state/goal được hoán vị có kiểm soát trong TRAIN. Ước lượng tác dụng head/regularization khi thiếu quan hệ đúng. |
| D — O1-TRUE | Cùng head và cùng ngân sách với C, nhãn state/goal đúng. |
| E — O0-CAPACITY | O0 có số tham số và FLOPs hiệu dụng được matching với O1. Kiểm tra tác dụng tăng dung lượng/compute, với cùng nguồn supervision được chỉ định. |

Đo riêng `VAL NLL`, `entity accuracy`, `goal consistency`, đáp án trên bộ vị trí đối kháng, extrapolation theo template/key, chi phí huấn luyện thực tế và độ ổn định giữa seeds. Công bố số mục tiêu supervised, FLOPs, total/active params và sự hiện diện của oracle labels **trong TRAIN**. Tất cả arms phải có `oracle_at_inference=0`. Bộ thử mới cần khóa trước, và dùng nguồn test mới chưa nhìn nhãn sau quyết định chính thức.

## 6. Danh sách bằng chứng và lệnh tái hiện

Các script sao chép nguyên byte nằm cạnh file này. Dưới Python 3.12:

```powershell
$qa = 'D:\WORK\RESEARCH\TokenToModel-Lab\artifacts\qa\r2\codex_adversarial_20261110_b1325d6'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
# Chạy lại kiểm toán bổ sung cần output riêng hoặc xóa chỉ file được tạo ở vòng mới.
& $py (Join-Path $qa 'r2_codex_adversarial_checks.py')
```

Phần kiểm toán bổ sung ghi `codex_adversarial_audit.json`, gồm 12 ca. 9 ca bị từ chối theo grammar/label, 3 ca chấp nhận có chủ đích (người sở hữu trùng giữa hai vật khác nhau, declared counts bị sửa, `source_events` bị sửa). Nếu chạy đúng script thêm lần nữa trong cùng QA dir, guard `REFUSE_OVERWRITE` sẽ bảo vệ bằng chứng đã tạo. Muốn tái chạy riêng, sao chép mã và dataset sang một **thư mục QA mới** dưới cùng project root.

Không dùng checkpoint, dataset TRAIN/VAL/TEST, Q1Q2, Ollama, Colab hoặc science inference. Không sửa source branch, không merge PR, không commit/push GitHub.

## 7. Bước thực hiện tiếp theo

`TTM_SMALL4M_R2_POSITION_COUNTERBALANCED_KEY_BINDING_TOY_AMENDMENT_AND_SINGLE_CPU_QA`

Tạo bản fixture **mới** trong phạm vi nghiên cứu R2, cân bằng vị trí cập nhật có liên quan trên cả bốn câu, cho phép sự kiện cuối là target hoặc distractor, đổi vị trí câu hỏi hợp lệ, giữ 128 A/B word-bag pairs, và thêm một held-out grammar/template split. Đặt một đối chứng rẻ `position-only` và `last-relevant-event` trước khi quyết định O1. Sau khi phần kiểm định đủ khả năng phân biệt shortcut mới trình owner chọn O0-only hoặc O0+O1 prospective ablation. Không tự mở huấn luyện.
