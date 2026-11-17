# Bước 3 — Sửa thang đo cho sinh tự do (ưu tiên sau STEP2)

**Trạng thái:** `DESIGN_PROPOSAL_NOT_AUTHORIZED · SOURCE_ONLY · NO_MODEL_RUN · NO_TRAINING · LINEAGE_UNCHANGED`  
**Phiên bản:** v2, 2026-11-17. Thay thế v1 (commit `f88c6d1`, vẫn còn trong lịch sử git). **Repository:** `minhtri22/TokenToModel-Lab`. **Main được đối chiếu khi soạn:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` (PR #27). Sau đó `main` tiến tới `e102d2ed3c885756b6e4354189ccbece36b75eb8` (PR #39 và #40, lineage L0030–L0035) và nhánh này đã merge `main` mới. Tác giả bản nháp **đã đọc các mục lineage L0029–L0035 nhưng chưa đọc 76 tệp mã/tài liệu ABC mới**; `ACTIVE_RESEARCH_GATE.md` không đổi giữa hai commit `main` (đã so sánh). Xem ghi chú đồng bộ ở STEP5 và STEP6.  
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

## 0. Phạm vi trong lộ trình v2

Ở v2, endpoint chính của lộ trình là likelihood-based (STEP2: Probe A, B, C) và `val_bpb` (STEP1), nên thang chấm **không còn nằm trên đường găng**. Nó cần khi muốn đánh giá **sinh tự do**, chỉ sau khi STEP1–STEP2 cho thấy có tín hiệu, hoặc khi cần bộ chấm cho các chiều (độ liền mạch, bám prompt tự nhiên) mà xác suất ứng viên không phủ. Điều này làm Bước 3 ưu tiên thấp hơn v1, nhưng nội dung kiểm định bên dưới giữ nguyên vì mọi kết quả rater đã có trong repo (FRESH16, H-DATA-S1, D1 EXP32) vẫn chưa thể diễn giải nếu thang chưa được kiểm.

## 1. Vấn đề đã quan sát trong repo

| Nguồn | Quan sát | Hệ quả cho thang đo |
|---|---|---|
| FRESH16 V2 (L0015) | Chấm mù S1: 28 điểm 1 và 4 điểm 0; không có điểm ≥ 2. S1 và S2 là hai **vai chấm khác nhau**, không phải hai rater trên cùng item | Thang không có chỗ cho mô hình thể hiện tiến bộ; không đo được độ đồng thuận |
| H-DATA-S1 FINAL24 | Cả 48 continuation bị chấm 0 ở actor, object và goal; một AI-rater | Hiệu ứng sàn: không phân biệt được mô hình yếu, nhiệm vụ khó hay thang chấm có vấn đề |
| D1 EXP32 | Greedy và nucleus đều 0/32 đạt grade ≥ 2; ghi `RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED` | Không biết chính xác rater đã nhìn thấy byte nào |
| FC01 BLIND96 | Rubric hậu nghiệm, không tiền đăng ký, AI rater | Không dùng để thay endpoint chính |
| Kiểm toán Q001 (QF-02, HIGH) | Rater/gold chưa được xác nhận cùng visible evidence ở nhiều phép đo | Hai rater cùng đồng ý vẫn có thể cùng sai |

**Kết luận của tác giả bản nháp:** trước khi huấn luyện thêm bất kỳ biến thể nào (STEP4, STEP5), cần chứng minh thang đo có thể phân biệt đúng và sai trên dữ liệu có đáp án biết trước, và không bị kẹt ở sàn 0. Nếu không, kết quả "không cải thiện" của STEP4–STEP5 không thể diễn giải.

## 2. Câu hỏi và quyết định bị thay đổi

**Câu hỏi:** Thang chấm (và bộ chấm, người hay AI hay chương trình) có phân biệt được continuation đúng với sai trên các item có sự thật đã biết, với độ tách đủ lớn và không tập trung ở sàn hay trần?

- Nếu **có**: được dùng thang này làm endpoint phụ cho STEP4–STEP5, kèm endpoint likelihood-based (STEP2) làm endpoint chính.
- Nếu **không**: dừng; sửa thang hoặc chuyển hẳn sang endpoint có thể chấm bằng chương trình. Không huấn luyện thêm chỉ để "thấy điểm lên".

**Phân biệt với `TTM-P0A-MEAS-Q001`:** Q001 hỏi liệu nhãn thật `LOCATED_AT(entity, location, time)` dựng từ nguồn có hình thành được benchmark hợp lệ không, và đã đóng ở `Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT`. Bước này không dựng ontology từ nguồn thật và không cần quyền nguồn, vì dùng item **tổng hợp có đáp án lập trình**. Nó hỏi về **độ phân biệt của thang**, không hỏi về hiệu lực của một ontology. Theo kiểm tra distinctness của `TTM_POST_P0A_Q001_EVIDENCE_GAPS...` (phản chứng: "Q001 đã đóng có trả lời câu này không?"), tác giả cho rằng câu trả lời là **không**, nhưng đây là phán đoán cần owner và reviewer xác nhận, không phải kết luận.

## 3. Thiết kế

### 3.1. Ưu tiên endpoint chấm được bằng chương trình
- **Endpoint chính, không rater:** xác suất teacher-forced và chọn trong ứng viên (STEP2, gồm Probe C).
- **Free generation, giai đoạn 1:** các slot đơn token (tên, đối tượng, địa điểm từ danh mục đóng) được chấm bằng so khớp chính xác bằng chương trình trên token ID và chuỗi đã chuẩn hóa. Không cần AI rater.
- **AI rater chỉ cho phần dư** (ví dụ mức độ liền mạch hoặc phần không thể so khớp), và chỉ sau khi vượt kiểm định ở 3.3.

### 3.2. Bộ item thang bậc có đáp án biết trước (không phải output của mô hình)
Với mỗi prompt, dựng chương trình năm lớp continuation:

| Lớp | Mô tả | Điểm kỳ vọng (cao nhất = đúng) |
|---|---|---|
| K4 | Đúng thực thể, đúng thuộc tính, câu gọn | cao nhất |
| K3 | Đúng, kèm chi tiết thừa không liên quan | cao |
| K2 | Đúng thực thể, sai thuộc tính | trung bình thấp |
| K1 | Hoán đổi gắn kết (thực thể sai) nhưng trôi chảy | thấp |
| K0 | Lạc đề, sao chép nguyên prompt, lặp suy biến | thấp nhất |

Quy mô đề xuất: 40 prompt × 5 lớp = 200 item, cộng 40 item lặp để đo test-retest = 240. Item dựng chương trình, không lấy từ TEST, FINAL24, FRESH12/16, CF1 hay output đã tiêu thụ. Không chấm lại các tập đã tiêu thụ.

### 3.3. Chỉ số kiểm định thang (đề xuất)
| Chỉ số | Ngưỡng đề xuất |
|---|---|
| AUC phân biệt {K4, K3} và {K2, K1, K0}, cận dưới CI95 (bootstrap theo prompt) | ≥ 0,90 |
| Tương quan hạng Spearman giữa lớp đã biết và điểm | ≥ 0,80 |
| Tỉ lệ K4 bị chấm điểm thấp (âm tính giả) | ≤ 10% |
| Tỉ lệ K1 (thực thể sai nhưng trôi chảy) bị chấm điểm cao (dương tính giả) | ≤ 10% |
| Tỉ lệ item ở sàn hoặc ở trần (từng đầu) | ≤ 50% mỗi đầu |
| Test-retest trên 40 item lặp (đồng thuận chính xác) | ≥ 85% |

Với nhiều rater, ghi riêng từng phiên (session) và đối chiếu; hai rater đồng ý không chứng minh đúng, nên so sánh cả với đáp án lập trình.

### 3.4. Chống hiệu ứng sàn bằng baseline và neo
Chấm thêm các baseline không phải mô hình đã train: (i) n-gram hoặc bigram TRAIN-only sinh tiếp, (ii) heuristic chép thực thể gần nhất, (iii) random-init, (iv) oracle lập trình. Thang chỉ hữu ích nếu oracle > heuristic > random-init với biên rõ rệt. Nếu baseline và mô hình cùng dính ở 0 thì ghi `FLOOR_HOLD`: thang không có thông tin ở vùng mô hình đang hoạt động.

### 3.5. Provenance của thông tin rater nhìn thấy
Ghi hash chính xác của byte mà rater nhận (prompt, continuation, rubric, thứ tự), và chứng minh rater không thấy nhãn lớp hoặc nhãn arm. Thiếu hash thì kết quả bị `RATER_INPUT_BYTE_PROVENANCE_NOT_VERIFIED`, đúng lỗi đã ghi ở D1 EXP32.

### 3.6. Kiểm soát dương
Bộ chấm phải cho K4 điểm cao trên mọi prompt. Một thang không bao giờ cho điểm cao thì không phải thang, cho dù mô hình có yếu.

## 4. Tiêu chí quyết định

| Kết quả | Diễn giải | Bước tiếp |
|---|---|---|
| Đạt toàn bộ chỉ số 3.3 và không FLOOR_HOLD | Thang có khả năng phân biệt | Dùng làm endpoint phụ ở STEP4–STEP5 |
| Đạt phân biệt nhưng sàn/trần quá nhiều | Thang đúng nhưng thiếu độ phân giải ở vùng cần đo | Thêm bậc hoặc tách thành kiểm tra nhị phân theo slot |
| Rater chấm K1 cao (thực thể sai nhưng trôi chảy) | Thang đo độ trôi chảy chứ không đo bám thực thể | Chuyển sang chấm slot bằng chương trình |
| Không đạt AUC | Thang không phân biệt đúng sai | `HOLD`; không huấn luyện thêm dựa trên thang này |
| Thiếu provenance byte | Không diễn giải được | `HOLD_PROVENANCE` |

## 5. Ràng buộc, ngân sách và dừng

- Không dùng GPU, không huấn luyện, không dùng dữ liệu nguồn ngoài, không dùng tập đã tiêu thụ. Item tổng hợp dựng từ danh mục từ đơn token của tokenizer; kiểm kê tokenizer như STEP0 (mục 0.1) và STEP2.
- Rater người hay AI phải được owner xác định; với AI rater, ghi rõ phiên mới, không có ngữ cảnh trước, và độc lập **chỉ tự khai báo**, không phải xác minh bên ngoài (đúng như cách repo gọi các review AI).
- Nếu dùng sau này cho output của mô hình, thang đã đóng băng không được sửa sau khi thấy kết quả; mọi sửa là amendment có nguồn gốc trước outcome.

## 6. Điểm yếu và giới hạn

- Item tổng hợp có thể dễ hơn hoặc khác văn bản tự nhiên mà mô hình tạo ra; AUC cao trên K0–K4 không bảo đảm thang phân biệt tốt các lỗi tinh tế của output thật.
- Lớp K1 là lớp quan trọng nhất (trôi chảy nhưng sai thực thể) và cũng khó dựng sao cho tự nhiên.
- Các ngưỡng là đề xuất, chưa dựa trên dữ liệu.
- Một người soạn; chưa có review độc lập.

## 7. Việc cần xác nhận

1. Owner xác nhận distinctness với Q001 (mục 2) và loại rater được phép dùng.
2. Reviewer thách thức ngưỡng 3.3 và cách dựng K1.
3. Quyết định slot nào chấm bằng chương trình, slot nào cần rater.
