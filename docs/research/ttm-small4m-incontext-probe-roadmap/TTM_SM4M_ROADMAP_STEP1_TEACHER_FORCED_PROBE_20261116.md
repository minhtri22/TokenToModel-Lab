# Bước 1 — Probe teacher-forced trên checkpoint T4 nguyên bản

**Trạng thái:** `DESIGN_PROPOSAL_NOT_AUTHORIZED · SOURCE_ONLY · NO_MODEL_RUN · NO_TRAINING · LINEAGE_UNCHANGED`  
**Ngày:** 2026-11-16 · **Repository:** `minhtri22/TokenToModel-Lab` · **Main được đối chiếu:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` (PR #27).  
**Tác giả:** Claude (AI), soạn theo yêu cầu của chủ repo trong một phiên trò chuyện. **Review độc lập: `NOT_PERFORMED`.** Mọi ngưỡng, cỡ mẫu và ngân sách dưới đây là **đề xuất của tác giả bản nháp**, chưa dựa trên dữ liệu đo và chưa được đóng băng.  
**Quan hệ với quản trị hiện hành:** `docs/governance/ACTIVE_RESEARCH_GATE.md` ghi `NO_NEW_BRANCH_AUTHORIZED` và `TTM-SM4M-DIAG-Q001` ở `Q1_REGISTERED_SOURCE_ONLY`. Nhánh chứa tài liệu này được tạo theo yêu cầu trực tiếp của chủ repo; việc nó có trở thành Question Gate, amendment của DIAG-Q001 hay bị bỏ là **quyết định của owner**, không được suy ra từ sự tồn tại của nhánh. Tài liệu này không cấp quyền truy cập checkpoint, không cấp quyền chạy mô hình và không thêm mục vào `lineage.md`.

**Lộ trình 5 bước (mỗi bước một tài liệu):**
1. Probe teacher-forced trên checkpoint nguyên bản (tài liệu STEP1)
2. Đối chứng random-init và hai checkpoint 1024/1280 (STEP2)
3. Sửa thang đo trước khi train thêm (STEP3)
4. Tách data / objective / capacity (STEP4)
5. Xác minh quyền và custody checkpoint, chạy song song (STEP5)

---

## 1. Câu hỏi và quyết định mà kết quả sẽ thay đổi

**Câu hỏi:** Trên checkpoint T4 bước 1024 nguyên bản (không fine-tune), mô hình (A) có cơ chế sao chép/truy xuất trong ngữ cảnh không, và (B) khi teacher-forced trên văn bản kiểu TinyStories, xác suất của đáp án có dịch chuyển đúng hướng theo sự kiện (gắn thực thể với đối tượng) hay chỉ theo vị trí gần nhất hoặc tần suất từ?

Đây là phép đo **không cần gold, không cần rater, không sinh văn bản và không huấn luyện**. Nó nhằm tách lỗi biểu diễn của mô hình khỏi lỗi thang đo, điều mà FRESH16, D1 EXP32 và H-DATA-S1 chưa tách được (xem `docs/governance/sm4m-q001/SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md` §5, nơi chính repo xếp teacher-forced conditioning trước free-generation/rater).

## 2. Đối tượng đo và ràng buộc

- Arm chính: checkpoint T4 bước 1024, SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Các arm đối chứng nằm ở STEP2.
- Nạp bằng `torch.load(weights_only=True)`, `strict=True`, cấu hình đúng `vocab 2048 / context 256 / d 256 / 4 layer / 4 head / layernorm` và đúng 3.749.376 tham số. Không dùng `P02Config` mặc định (64/64/2).
- Sai byte, schema hoặc cấu hình thì `HOLD_CUSTODY`; không đổi sang checkpoint khác.
- FP32, CPU, `eval()`, `torch.no_grad()`, chạy hai lần và yêu cầu kết quả giống từng bit.
- Không dùng TEST64, FINAL24, FRESH12/16, CF1 hay bất kỳ tập đã tiêu thụ.
- Điều kiện tiên quyết quyền truy cập: STEP5.

## 3. Probe A — sao chép/induction trên chuỗi ngẫu nhiên

**Cấu trúc:** `[EOS=256][S][S]`, trong đó S gồm m token lấy ngẫu nhiên đều từ ID 257–2047 (loại ID byte 0–255 và EOS). Cần xác nhận trong `tools/pilot_t4/integrated/t4_data_pack.py` rằng chuỗi huấn luyện thật sự đóng gói theo kiểu EOS đầu chuỗi; tác giả bản nháp **chưa đọc chi tiết** tệp này.

**Điều kiện:** m ∈ {8, 16, 32, 64, 127} (tổng độ dài 1 + 2m không vượt 256). Mỗi m có ba biến thể:
- **Thật:** đoạn hai lặp đúng đoạn một.
- **Shuffle:** đoạn hai là hoán vị ngẫu nhiên của S (cùng tập token).
- **Mismatch:** đoạn hai là S' độc lập, cùng vị trí tuyệt đối.

**Đại lượng:** IND = NLL trung bình trên đoạn một trừ NLL trung bình trên đoạn hai (bỏ token đầu của đoạn hai vì chưa có gì để khớp). Báo thêm top-1 accuracy và xác suất trung bình của token đúng ở đoạn hai. Mức chance của NLL là ln(1791) ≈ 7,49 nat. Hai biến thể kiểm soát phải cho IND gần 0; nếu không thì probe nhạy với vị trí hoặc thống kê bề mặt chứ không phải sao chép.

## 4. Probe B — gắn thực thể với đối tượng, teacher-forced

**Một cặp phản thực** (cùng bag-of-words, chỉ đổi cách gắn):
- Ngữ cảnh 1: `Tom has a ball. Ben has a kite. Tom plays with the` (ứng viên ` ball` và ` kite`)
- Ngữ cảnh 2: `Tom has a kite. Ben has a ball. Tom plays with the`

**Điểm số.** Lấy logits tại vị trí cuối ngữ cảnh, softmax toàn vocab, rồi LO(ngữ cảnh) = log P(o1) − log P(o2). Gọi q là thực thể được hỏi.

`S = LO(ngữ cảnh mà q gắn với o1) − LO(ngữ cảnh mà q gắn với o2)`

S > 0 nghĩa là ngữ cảnh đẩy xác suất về đối tượng gắn với q. Tần suất từ triệt tiêu theo thiết kế vì cùng cặp từ xuất hiện ở cả hai vế.

**Tách binding khỏi shortcut vị trí.** Nếu mô hình chỉ chọn đối tượng nhắc gần nhất thì S sẽ âm khi q được nhắc đầu và dương khi q được nhắc sau. Vì vậy cân bằng 50/50 hai nhóm (q-first, q-last) và báo kết quả từng nhóm. Binding thật phải cho S > 0 ở cả hai.

**Ràng buộc fixture:**
- Tên và đối tượng đều là một token BPE đơn (có dấu cách đứng trước). Phải kiểm kê tokenizer trước; dưới 20 tên hoặc dưới 20 đối tượng thì `HOLD_FIXTURE`.
- Hai thực thể cùng giới tính và không dùng đại từ his/her, để đại từ không làm lộ thực thể.
- 20 template × 20 thế giới, gán tên và đối tượng theo Latin square để mỗi từ xuất hiện đều ở các vai.
- Không thay item sau khi đã thấy output; item bị loại phải ghi lý do.

**Biến thể phụ:** chèn d ∈ {0, 2, 4} câu đệm trung tính giữa sự kiện và câu hỏi để đo suy giảm theo khoảng cách (rủi ro QF-05 của repo). Chỉ d = 0 là chính.

**Kiểm soát nhạy cảm bề mặt:** 100 cặp ba thực thể, hoán đổi gắn kết của hai thực thể không được hỏi. S kỳ vọng gần 0.

**Báo thêm:** P(o1) + P(o2) trên toàn vocab và hạng của hai ứng viên, vì LO vô nghĩa nếu cả hai gần như không được cân nhắc. Phân tích độ nhạy loại item có khối lượng dưới 0,01 (khai báo trước, không phải kết quả chính).

## 5. Số mẫu

| Hạng mục | Số lượng |
|---|---|
| Probe A | 5 giá trị m × 512 chuỗi × 3 biến thể = 7.680 chuỗi mỗi arm |
| Probe B chính | 400 cặp (200 q-first, 200 q-last) × 3 mức d |
| Probe B kiểm soát | 100 cặp hoán đổi không liên quan |

Với 200 cặp mỗi nhóm, giả định độc lập và kiểm định một phía mức 0,05, độ mạnh khoảng 80% để phát hiện tỉ lệ S > 0 cỡ 0,59. Các item bị gom cụm theo template và theo cặp tên/đối tượng nên số mẫu hiệu dụng thấp hơn; dùng cluster bootstrap theo template và theo thế giới và báo cả hai khoảng tin cậy. Forward pass là tất định nên sai số chỉ đến từ lấy mẫu item; không có phương sai seed huấn luyện nào được đo ở đây.

## 6. Tiêu chí quyết định (đề xuất; đóng băng sau review độc lập, trước khi mở checkpoint)

**Cổng hợp lệ của probe** (không qua thì `HOLD_PROBE_INVALID`, không phải FAIL của mô hình):
- Random-init (STEP2): |IND| ≤ 0,1 ở cả 3 seed; khoảng tin cậy của mean S chứa 0 ở cả hai nhóm.
- Biến thể shuffle và mismatch: |IND| ≤ 0,1.
- Hoán đổi không liên quan: khoảng tin cậy của S chứa 0.
- Kết quả giống từng bit giữa hai lần chạy.
- Unit test của scorer đạt (mục 8).

**Nhãn Probe A (m = 32, chính):**

| Nhãn | Điều kiện |
|---|---|
| A_ABSENT | Cận trên CI95 của IND < 0,3 nat |
| A_PARTIAL | Cận dưới CI95 ≥ 0,3 và < 2,0 nat |
| A_STRONG | Cận dưới CI95 ≥ 2,0 nat và top-1 đoạn hai ≥ 50% |

**Nhãn Probe B (d = 0):**

| Nhãn | Điều kiện |
|---|---|
| B_BINDING | Cận dưới CI95 của mean S > 0 và tỉ lệ S > 0 ≥ 0,60, ở cả q-first lẫn q-last |
| B_RECENCY_ONLY | S dương ở q-last, âm ở q-first, cả hai CI loại trừ 0 |
| B_NONE | CI của cả hai nhóm chứa 0 |
| B_MIXED | Các trường hợp còn lại |

Các ngưỡng 0,3 nat, 2,0 nat và 0,60 chỉ có cơ sở là mức chance 7,49 nat và độ mạnh ở mục 5. Reviewer cần thách thức chúng.

**Từ kết quả đến bước tiếp theo:**

| Kết quả | Có thể diễn giải | Bước tiếp |
|---|---|---|
| A_ABSENT ở mọi checkpoint | Thiếu cơ chế sao chép trong ngữ cảnh; hợp với ít dữ liệu hoặc ít bước; chưa loại trừ capacity | STEP4, nhánh liều lượng dữ liệu, trước khi bàn objective |
| A tăng đều, chưa bão hòa ở 1024 | Có dấu hiệu chưa train đủ | STEP4: thêm bước hoặc thêm dữ liệu cùng ngân sách thông tin |
| A_PARTIAL/STRONG và B_NONE | Có cơ chế nhưng không dùng cho binding trong văn bản tự nhiên | Căn chỉnh data/objective với nhiệm vụ; mở rộng probe B |
| A có và B_RECENCY_ONLY | Shortcut vị trí gần nhất | Dữ liệu đối chứng cân bằng vị trí |
| B_BINDING suy giảm theo d | Binding mong manh theo khoảng cách | Nghiên cứu context/khoảng cách |
| B_BINDING ổn định ở mọi d | Lỗi nằm ở sinh văn bản, decoding, rater hoặc đề bài chứ không ở biểu diễn | STEP3 trước; so greedy toàn vocab với chọn trong ứng viên |
| Probe không hợp lệ | Không kết luận được | HOLD; sửa runner hoặc fixture |

## 7. Ngân sách, điều kiện dừng và bằng chứng

- Python 3.12, FP32, một process, CPU. Trần đề xuất: 600 giây, RSS 4 GiB, đầu ra 100 MB. Đây là trần đề xuất, **chưa được đo**.
- Vượt trần hoặc lỗi custody/fixture/runner thì ghi `HOLD_*`, không ghi FAIL khoa học. Không chạy lại, không đổi seed, không thay item.
- Báo cáo gồm RUN_ID, hash checkpoint, runner, fixture, tokenizer, môi trường, toàn bộ tử số và mẫu số, kết quả theo từng template. Trọng số và logits thô giữ ở máy riêng; GitHub chỉ nhận bản tóm tắt không nhạy cảm.

## 8. Kiểm thử âm tính cho runner (trước khi chạm checkpoint)

Dùng logits do tay dựng để kiểm: lệch chỉ số một vị trí giữa logits và token đích, lấy nhầm vị trí cuối, nhầm cấu hình P02 mặc định, token đích lọt vào ngữ cảnh, ứng viên đổi chỗ, tính loss trên mọi vị trí thay vì vị trí mong muốn (lưu ý `GPT.forward(tokens, targets)` mặc định tính cross-entropy trên toàn chuỗi), ID đặc biệt trùng ID ứng viên, trùng lặp giữa các ngữ cảnh. Scorer phải cho đúng kết quả đã biết trên oracle tổng hợp.

## 9. Điểm yếu của thiết kế

- Văn bản theo template bằng từ đơn token trong vocab 2048 lệch phân phối so với TinyStories và chỉ gồm từ phổ biến, nên khó khái quát sang văn bản đa dạng.
- Ưu tiên xác suất teacher-forced không đảm bảo hành vi khi sinh tự do; B_BINDING không chứng minh sinh đúng.
- Induction trên token ngẫu nhiên có thể khác cơ chế trên văn bản tự nhiên; có thể gặp A_ABSENT cùng B_BINDING và khi đó cần diễn giải riêng.
- Hạn chế ở hai ứng viên bỏ qua phần còn lại của phân phối; đã bù bằng khối lượng xác suất và hạng.
- Không có phân tích attention nên không kết luận cơ chế nhân quả.
- Người soạn là một tác giả duy nhất; cần review độc lập thách thức cả fixture lẫn ngưỡng.

## 10. Việc cần xác nhận trước khi triển khai

1. Owner: phạm vi truy cập checkpoint (STEP5) và cách đưa vào gói DIAG-Q001 hay câu hỏi riêng.
2. Đọc `t4_data_pack.py` để xác nhận định dạng chuỗi (EOS đầu chuỗi, độ dài cửa sổ).
3. Kiểm kê tokenizer: số tên và đối tượng đơn token.
4. Review độc lập về ngưỡng (mục 6) và fixture (mục 4).
5. Chạy bộ kiểm thử âm tính (mục 8) trước mọi lần mở checkpoint.
