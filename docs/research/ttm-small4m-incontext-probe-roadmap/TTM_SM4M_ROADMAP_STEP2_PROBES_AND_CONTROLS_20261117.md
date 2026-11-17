# Bước 2 — Probe teacher-forced, bộ chọn-ending và đối chứng

**Trạng thái:** `DESIGN_PROPOSAL_NOT_AUTHORIZED · SOURCE_ONLY · NO_MODEL_RUN · NO_TRAINING · LINEAGE_UNCHANGED`  
**Phiên bản:** v2, 2026-11-17. Thay thế v1 (commit `f88c6d1`, vẫn còn trong lịch sử git). **Repository:** `minhtri22/TokenToModel-Lab`. **Main được đối chiếu:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` (PR #27, không đổi).  
**Tác giả:** Claude (AI), soạn theo yêu cầu của chủ repo trong một phiên trò chuyện. **Review độc lập: `NOT_PERFORMED`.** Mọi ngưỡng, cỡ mẫu, thời gian và ngân sách là **đề xuất của tác giả bản nháp**, chưa dựa trên dữ liệu đo và chưa được đóng băng.  
**Quan hệ với quản trị hiện hành:** `docs/governance/ACTIVE_RESEARCH_GATE.md` ghi `NO_NEW_BRANCH_AUTHORIZED` và `TTM-SM4M-DIAG-Q001` ở `Q1_REGISTERED_SOURCE_ONLY`. Nhánh chứa tài liệu này được tạo theo yêu cầu trực tiếp của chủ repo; việc nó trở thành Question Gate, amendment của DIAG-Q001 hay bị bỏ là **quyết định của owner**. Tài liệu không cấp quyền truy cập checkpoint, không cấp quyền chạy hay huấn luyện mô hình và không thêm mục vào `lineage.md`.

**Nguồn đối chiếu bên ngoài (đã đọc) và giới hạn:** nanochat (`karpathy/nanochat`, commit `92d63d4`, 2026-07-03: README, `dev/LOG.md`, `scripts/base_train.py`, `nanochat/gpt.py`, `nanochat/optim.py`), repo autoresearch, và bài "A Recipe for Training Neural Networks". **Các video YouTube của Karpathy không xem được** (trang chặn tải), nên phần dựa vào video chỉ dựa trên mục lục, mô tả và hiểu biết nền của tác giả bản nháp, không phải trích dẫn nội dung từng clip. Kết quả của nanochat được thử ở quy mô d12–d26 trên GPU 8×H100 và **không tự chuyển** sang mô hình 3,7M tham số.

**Lộ trình v2 (mỗi bước một tài liệu):**
0. Kiểm tra nền kiểu Recipe và đối chiếu implementation tham chiếu (STEP0)
1. Đường cong scale ở horizon compute-optimal (STEP1)
2. Probe teacher-forced, bộ chọn-ending và đối chứng (STEP2)
3. Sửa thang đo cho sinh tự do (STEP3)
4. Ablation kiến trúc từng thay đổi một (STEP4)
5. Objective, dung lượng và bậc thang scale vượt Small-4M (STEP5)
6. Xác minh quyền và custody, chạy song song (STEP6)

**Thay đổi so với v1:** thêm STEP0 và STEP4; STEP1 thay Bước 4a của v1 (giữ compute, đổi độ đa dạng) bằng đường cong scale tới horizon compute-optimal; Bước 2 của v1 (đối chứng random-init, M1024, M1280) được gộp vào STEP2; v1 Bước 4b/4c chuyển thành STEP5; v1 Bước 5 thành STEP6.

---

## 1. Mục đích và câu hỏi

Đo, **không fine-tune và không sinh văn bản**, xem mô hình (A) có cơ chế sao chép trong ngữ cảnh không, (B) có dịch chuyển xác suất đúng hướng theo sự kiện gắn thực thể với đối tượng không, và (C) chọn đúng đối tượng giữa nhiều ứng viên không. Không cần gold hay rater. Kiểm toán nội bộ của repo (`SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md` §5) cũng xếp teacher-forced conditioning trước free-generation.

Vai trò trong lộ trình v2: đây là **endpoint đo** dùng dọc các bước khác (STEP1, STEP4, STEP5), không phải câu hỏi đầu tiên. Lý do hạ ưu tiên: STEP1 cho thấy mô hình mới tốt hơn bigram khoảng 12% và thiếu huấn luyện cỡ 10×, nên kết quả `A_ABSENT` trên checkpoint hiện có gần như là kỳ vọng nền; giá trị chính của giai đoạn 2a là **hiệu chuẩn probe** (random-init so với checkpoint), và làm mốc cho 2b.

## 2. Sửa so với v1: EOS không được làm token đầu chuỗi

v1 đề xuất chuỗi `[EOS=256][S][S]` kèm lưu ý "cần xác nhận cách đóng gói". Đã đọc `tools/pilot_t4/integrated/t4_data_pack.py`: mỗi truyện là `encode(text) + [EOS]`, và vì `x` là `segment[:-1]` còn `y` là `segment[1:]`, **EOS chỉ xuất hiện như nhãn ở cuối truyện, không bao giờ là đầu vào** trong huấn luyện (xác nhận lúc chạy ở STEP0 mục 0.1). Không có BOS. Hệ quả: một chuỗi bắt đầu bằng EOS là ngoài phân phối so với huấn luyện, và token EOS ở phía đầu vào chưa từng được học trực tiếp (trọng số dùng chung chỉ nhận gradient phía đầu ra). Vì vậy v2 **bỏ tiền tố EOS**: chuỗi probe bắt đầu thẳng bằng token nội dung, giống một truyện thật.

Một chi tiết liên quan: cửa sổ thứ hai trở đi của truyện dài bắt đầu giữa truyện nhưng nằm ở vị trí 0, nên "vị trí 0" trong huấn luyện không luôn là đầu truyện. Probe luôn bắt đầu ở vị trí 0 với đầu truyện thật.

## 3. Các arm và hai giai đoạn

**Giai đoạn 2a: trên checkpoint hiện có** (cần STEP6):

| Arm | Nội dung | Vai trò | Trạng thái nguồn |
|---|---|---|---|
| M1024 | Checkpoint T4 bước 1024, SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | Đối tượng chính | SHA đã ghi (lineage L0011); byte chưa kiểm lại |
| M1280 | "Step1280 exploratory continuation", SHA-256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` | So sánh theo cặp với M1024 | SHA lấy từ manifest tái lập trên nhánh `docs/ttm-small4m-model-card-dataset-rights-20261109`; **chưa kiểm byte, chưa đọc kỹ cách tạo** |
| R0a, R0b, R0c | `GPT(P02Config(2048, 256, 256, 4, 4))` khởi tạo ngẫu nhiên bằng `_init_weights` của P02, 3 seed dẫn xuất từ 20261117 | Negative control chính | Không cần quyền checkpoint |
| W1024 (tùy chọn) | M1024 với từng tensor bị xáo trộn phần tử | Kiểm tra probe có nhạy với thống kê trọng số thay vì cấu trúc học được | Cùng quyền như M1024 |
| M256, M512, M768 (tùy chọn) | Ba mốc trung gian của cùng lần train (lineage L0011) | Đường cong xuất hiện cơ chế trong một run | SHA chưa ghim |

**Lưu ý về M1280:** theo lineage L0015, FRESH16 không phải kết quả confirmatory của checkpoint 1280; FRESH12 ghi VAL NLL M1280 thấp hơn (~3,498089 so với ~3,522339) nhưng không chứng minh được lợi ích ngữ nghĩa trong phạm vi đo. Trước khi diễn giải so sánh M1024 và M1280, phải đọc nhánh nguồn `research/ttm-small4m-q1q2-quality-single-batch-20261109` để biết 256 bước đó dùng dữ liệu, optimizer và schedule nào. Nếu 256 bước dùng dữ liệu khác thì chênh lệch không thể quy cho "thêm bước".

**Giai đoạn 2b: dọc đường cong STEP1** (mỗi arm R0, R1, T11, T22, T44, T88 và mỗi seed, ở bước cuối), cùng fixture bytes.

Random-init **chỉ** là negative control cho probe; nó không phải "scratch model" thay checkpoint khi custody thất bại.

Nạp bằng `torch.load(weights_only=True)`, `strict=True`, cấu hình đúng `vocab 2048 / context 256 / d 256 / 4 layer / 4 head` và 3.749.376 tham số; không dùng `P02Config` mặc định. Sai byte, schema hoặc cấu hình thì `HOLD_CUSTODY`. FP32, CPU, `eval()`, `no_grad`, chạy hai lần và yêu cầu kết quả giống từng bit. Không dùng TEST64, FINAL24, FRESH12/16, CF1 hay bất kỳ tập đã tiêu thụ.

## 4. Probe A: sao chép/induction trên chuỗi ngẫu nhiên

**Cấu trúc:** `[S][S]`, trong đó S gồm m token lấy ngẫu nhiên đều từ ID 257–2047 (loại ID byte 0–255 và EOS). Không có tiền tố.

**Điều kiện:** m ∈ {8, 16, 32, 64, 128} (tổng độ dài 2m không vượt 256). Mỗi m có ba biến thể:
- **Thật:** đoạn hai lặp đúng đoạn một.
- **Shuffle:** đoạn hai là hoán vị ngẫu nhiên của S (cùng tập token).
- **Mismatch:** đoạn hai là S' độc lập, cùng vị trí tuyệt đối.

**Đại lượng:** IND = NLL trung bình trên đoạn một trừ NLL trung bình trên đoạn hai (bỏ token đầu của đoạn hai vì chưa có gì để khớp; token đầu của đoạn một không có ngữ cảnh nên cũng bỏ). Báo thêm top-1 accuracy và xác suất trung bình của token đúng ở đoạn hai. Mức chance của NLL là ln(1791) ≈ 7,49 nat. Hai biến thể kiểm soát phải cho IND gần 0, nếu không probe nhạy với vị trí hoặc thống kê bề mặt chứ không phải sao chép.

## 5. Probe B: gắn thực thể với đối tượng, teacher-forced

**Một cặp phản thực** (cùng bag-of-words, chỉ đổi cách gắn):
- Ngữ cảnh 1: `Tom has a ball. Ben has a kite. Tom plays with the` (ứng viên ` ball` và ` kite`)
- Ngữ cảnh 2: `Tom has a kite. Ben has a ball. Tom plays with the`

**Điểm số.** Lấy logits tại vị trí cuối ngữ cảnh, softmax toàn vocab, rồi LO(ngữ cảnh) = log P(o1) − log P(o2). Gọi q là thực thể được hỏi.

`S = LO(ngữ cảnh mà q gắn với o1) − LO(ngữ cảnh mà q gắn với o2)`

S > 0 nghĩa là ngữ cảnh đẩy xác suất về đối tượng gắn với q. Tần suất từ triệt tiêu theo thiết kế vì cùng cặp từ xuất hiện ở cả hai vế.

**Tách binding khỏi shortcut vị trí.** Nếu mô hình chỉ chọn đối tượng nhắc gần nhất thì S âm khi q được nhắc đầu và dương khi q được nhắc sau. Cân bằng 50/50 hai nhóm (q-first, q-last) và báo từng nhóm. Binding thật phải cho S > 0 ở cả hai.

**Ràng buộc fixture:**
- Tên và đối tượng đều là một token BPE đơn (có dấu cách đứng trước). Phải kiểm kê tokenizer trước (STEP0 mục 0.1); dưới 20 tên hoặc dưới 20 đối tượng thì `HOLD_FIXTURE`.
- Hai thực thể cùng giới tính và không dùng đại từ his/her, để đại từ không làm lộ thực thể.
- 20 template × 20 thế giới, gán tên và đối tượng theo Latin square để mỗi từ xuất hiện đều ở các vai.
- Không thay item sau khi đã thấy output; item bị loại phải ghi lý do.
- Nếu tokenizer thay đổi ở các bước sau (STEP5), fixture phải dựng lại bằng cùng quy tắc.

**Biến thể phụ:** chèn d ∈ {0, 2, 4} câu đệm trung tính giữa sự kiện và câu hỏi để đo suy giảm theo khoảng cách (rủi ro QF-05 của repo). Chỉ d = 0 là chính.

**Kiểm soát nhạy cảm bề mặt:** 100 cặp ba thực thể, hoán đổi gắn kết của hai thực thể không được hỏi. S kỳ vọng gần 0.

**Báo thêm:** P(o1) + P(o2) trên toàn vocab và hạng của hai ứng viên; phân tích độ nhạy loại item có khối lượng dưới 0,01 (khai báo trước, không phải kết quả chính).

## 6. Probe C: chọn một trong bốn ứng viên (kiểu HellaSwag, không rater)

Video GPT-2 124M và điểm CORE của nanochat đều chấm bằng so khớp xác suất của các ứng viên, không cần rater. Probe C áp dụng ý đó trên cùng fixture của Probe B: với mỗi ngữ cảnh, bốn ứng viên đơn token:
- **Đúng:** đối tượng gắn với q.
- **Hoán đổi:** đối tượng của thực thể kia.
- **Thứ ba:** một đối tượng chưa từng được nhắc, tần suất tương đương.
- **Không liên quan:** một từ hợp lý về cú pháp nhưng không phải đối tượng.

Chọn ứng viên có log-xác suất cao nhất. Báo (i) độ chính xác bốn chiều (chance 25%), (ii) độ chính xác đúng so với hoán đổi (chance 50%), (iii) **độ chính xác cặp**: item chỉ tính đúng khi mô hình ưu tiên đáp án đúng ở cả hai ngữ cảnh phản thực (chance 25% cho hai lựa chọn độc lập), vì độ chính xác đơn lẻ lẫn với tần suất từ. Baseline bắt buộc chấm cùng fixture: bigram và trigram fit trên TRAIN, random-init, heuristic "chọn đối tượng nhắc gần nhất". Mô hình phải vượt các baseline đó với biên rõ ràng mới được coi là có tín hiệu.

## 7. Số mẫu

| Hạng mục | Số lượng |
|---|---|
| Probe A | 5 giá trị m × 512 chuỗi × 3 biến thể = 7.680 chuỗi mỗi arm |
| Probe B và C chính | 400 cặp (200 q-first, 200 q-last) × 3 mức d |
| Probe B kiểm soát | 100 cặp hoán đổi không liên quan |

Với 200 cặp mỗi nhóm, giả định độc lập và kiểm định một phía mức 0,05, độ mạnh khoảng 80% để phát hiện tỉ lệ S > 0 cỡ 0,59. Các item bị gom cụm theo template và theo cặp tên/đối tượng nên số mẫu hiệu dụng thấp hơn; dùng cluster bootstrap theo template và theo thế giới, báo cả hai khoảng tin cậy. Forward pass tất định nên sai số chỉ đến từ lấy mẫu item; ở giai đoạn 2b, phương sai giữa seed huấn luyện được tính từ 3 seed mỗi arm.

## 8. Tiêu chí quyết định (đề xuất; đóng băng sau review độc lập, trước khi mở checkpoint)

**Cổng hợp lệ của probe** (không qua thì `HOLD_PROBE_INVALID`, không phải FAIL của mô hình):
- Random-init: |IND| ≤ 0,1 ở cả 3 seed; khoảng tin cậy của mean S chứa 0 ở cả hai nhóm; độ chính xác Probe C trong khoảng chance.
- Biến thể shuffle và mismatch: |IND| ≤ 0,1.
- Hoán đổi không liên quan: khoảng tin cậy của S chứa 0.
- Kết quả giống từng bit giữa hai lần chạy; unit test scorer đạt (mục 10).

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

Các ngưỡng 0,3 nat, 2,0 nat và 0,60 chỉ có cơ sở là mức chance 7,49 nat và độ mạnh ở mục 7; reviewer cần thách thức chúng.

**So sánh khai báo trước:**

| Mã | Đối chiếu | Câu hỏi |
|---|---|---|
| C1 | M1024 so với R0 (3 seed) | Huấn luyện có tạo tín hiệu mà probe nhìn thấy không? |
| C2 | M1280 trừ M1024, theo cặp trên cùng item | 256 bước thêm có đổi IND hoặc S không? (biên tương đương đề xuất ±0,3 nat cho IND, ±0,05 cho tỉ lệ S > 0; CI rộng thì `INCONCLUSIVE`, không ghi "không khác") |
| C3 | M256 → M512 → M768 → M1024 (tùy chọn) | Cơ chế xuất hiện lúc nào trong một run? |
| C4 | M1024 so với W1024 (tùy chọn) | Tín hiệu phụ thuộc cấu trúc học được hay chỉ thống kê trọng số? |
| C5 (2b) | Các arm của STEP1 | Tín hiệu tăng theo T thế nào? |

**Từ kết quả đến bước tiếp theo:**

| Kết quả | Có thể diễn giải | Bước tiếp |
|---|---|---|
| C1: M1024 không tách khỏi R0 ở A, B, C | Chưa có bằng chứng cơ chế, hoặc probe thiếu độ nhạy | Dùng probe ở 2b (đường cong) trước khi kết luận; không kết luận "mô hình không thể" |
| A có, B/C không | Có sao chép nhưng không binding trên văn bản | STEP5 (objective, dữ liệu cân bằng vị trí) |
| A_ABSENT ở mọi arm kể cả T44 | Chưa có cơ chế sao chép ở d4 | STEP5 (dung lượng d6) và STEP4 |
| B_RECENCY_ONLY | Shortcut vị trí gần nhất | Dữ liệu đối chứng cân bằng vị trí |
| B_BINDING giảm theo d | Binding mong manh theo khoảng cách | Nghiên cứu context/khoảng cách |
| B_BINDING ổn định mọi d | Lỗi nằm ở sinh văn bản, decoding, rater hoặc đề bài | STEP3; so greedy toàn vocab với chọn trong ứng viên |
| C4: W1024 tách giống M1024 | Probe nhạy với thống kê | `HOLD_PROBE_INVALID` |
| Probe không hợp lệ | Không kết luận được | HOLD; sửa runner hoặc fixture |

## 9. Ngân sách, điều kiện dừng và bằng chứng

- Python 3.12, FP32, một process, CPU. Trần đề xuất mỗi arm: 600 giây, RSS 4 GiB, đầu ra 100 MB. Đây là trần đề xuất, **chưa được đo**.
- Vượt trần hoặc lỗi custody, fixture, runner thì ghi `HOLD_*`, không ghi FAIL khoa học. Không chạy lại, không đổi seed, không thay item.
- Báo cáo gồm RUN_ID, hash checkpoint, runner, fixture, tokenizer, môi trường, toàn bộ tử số và mẫu số, kết quả theo từng template. Trọng số và logits thô giữ ở máy riêng; GitHub chỉ nhận bản tóm tắt không nhạy cảm.

## 10. Kiểm thử âm tính cho runner (trước khi chạm checkpoint)

Dùng logits do tay dựng để kiểm: lệch chỉ số một vị trí giữa logits và token đích, lấy nhầm vị trí cuối, nhầm cấu hình P02 mặc định, token đích lọt vào ngữ cảnh, ứng viên đổi chỗ, tính loss trên mọi vị trí thay vì vị trí mong muốn (`GPT.forward(tokens, targets)` mặc định tính cross-entropy trên toàn chuỗi), ID đặc biệt trùng ID ứng viên, trùng lặp giữa các ngữ cảnh. Scorer phải cho đúng kết quả đã biết trên oracle tổng hợp. Các kiểm tra này trùng một phần với STEP0 mục 0.3–0.4 và nên dùng chung mã.

## 11. Điểm yếu của thiết kế

- Văn bản theo template bằng từ đơn token trong vocab 2048 lệch phân phối so với TinyStories và chỉ gồm từ phổ biến, nên khó khái quát.
- Ưu tiên xác suất teacher-forced không đảm bảo hành vi khi sinh tự do; B_BINDING hay Probe C cao không chứng minh sinh đúng.
- Induction trên token ngẫu nhiên có thể khác cơ chế trên văn bản tự nhiên; có thể gặp A_ABSENT cùng B_BINDING, cần diễn giải riêng.
- Hạn chế ở vài ứng viên đơn token bỏ qua phần còn lại của phân phối; đã bù bằng khối lượng xác suất và hạng.
- Không có phân tích attention nên không kết luận cơ chế nhân quả.
- M256–M1024 và M1280 đều từ một lần train, một seed; không phải mẫu độc lập.
- Người soạn là một tác giả duy nhất; cần review độc lập thách thức cả fixture lẫn ngưỡng.

## 12. Việc cần xác nhận trước khi triển khai

1. Owner: phạm vi truy cập checkpoint (STEP6) và cách đưa vào DIAG-Q001 hay câu hỏi riêng.
2. Kiểm kê tokenizer: số tên và đối tượng đơn token, loại token đặc biệt (kết quả của STEP0 mục 0.1).
3. Đọc nhánh nguồn của M1280 trước khi dùng nó làm đối chiếu.
4. Review độc lập về ngưỡng (mục 8) và fixture (mục 5, 6).
5. Chạy bộ kiểm thử âm tính (mục 10) trước mọi lần mở checkpoint.
