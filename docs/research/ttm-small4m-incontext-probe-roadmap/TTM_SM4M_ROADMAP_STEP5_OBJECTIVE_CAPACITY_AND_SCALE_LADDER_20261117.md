# Bước 5 — Objective, dung lượng và bậc thang scale vượt Small-4M

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

## 1. Điều kiện mở

Bước này **huấn luyện mô hình mới**. Chỉ xem xét sau STEP0 (nền sạch), STEP1 (đường cong baseline), STEP4 (cấu hình cơ sở đã chọn) và có Question Gate cùng quyết định owner theo `TTM-GOV-QF-20261115-V1`. Tài liệu này là thiết kế có điều kiện; **không phải quyền thực thi**. Nó gộp phần còn lại của Bước 4 v1 (objective, dung lượng) và thêm phần mới: bậc thang scale để đi vượt TTM-Small-4M.

## 2. Phần A: Objective (chỉ mở nếu khoảng cách còn lại sau STEP1 và STEP4)

**Câu hỏi:** Với cùng dữ liệu, kiến trúc và horizon, gói contrastive của FC01 có làm tăng chỉ số của STEP2 (đặc biệt Probe B, C) so với next-token prediction thuần không?

**Thiết kế:** cấu hình cơ sở sau STEP4, horizon T44 (STEP1), 3 seed, hai arm: NTP thuần và NTP cộng gói contrastive. Phải khai báo đúng như repo đã làm ở D1 V4/V5: đây là **gói contrastive** (loss cộng giám sát âm cộng compute thêm), **không** phải so sánh objective thuần hay ngang FLOPs; ghi riêng chi phí thêm và báo cả so sánh ngang số bước lẫn ngang compute. Dữ liệu giám sát âm dựng từ template phải **tách rời** fixture của STEP2 (tên, đối tượng, template), nếu không probe đo thuộc lòng chứ không đo khái quát. FC01 hiện chỉ có 1 seed và 64 lexical family của 4 template, nên kết quả cũ không đủ làm cơ sở.

## 3. Phần B: Bậc thang scale vượt Small-4M

**Ý tưởng cốt lõi lấy từ nanochat (đã đọc `scripts/base_train.py`):** một "núm xoay" duy nhất là `--depth`, mọi thứ khác suy ra từ đó: độ rộng bằng depth × `--aspect-ratio` (mặc định 64), số head từ `--head-dim` (mặc định 128), số token huấn luyện từ `--target-param-data-ratio` (mặc định 12) nhân số tham số scaling. Ở d4, độ rộng là 256, trùng với TTM-Small-4M.

**Bảng bậc thang (tính thô; công thức mỗi block ≈ 12·d² với MLP 4× và không tính bias; tham số scaling = L·12·d² + vocab·d, vocab 2048; FLOPs ≈ 6·N·D):**

| Depth | Độ rộng | Tham số scaling | Token ở tỉ lệ 12 | FLOPs ≈ 6·N·D | Số head nếu head-dim 128 |
|---|---|---|---|---|---|
| d4 (TTM hiện tại) | 256 | 3.670.016 | 44.040.192 | 9,7e14 | 2 (TTM đang dùng 4 head × 64) |
| d6 | 384 | 11.403.264 | 136.839.168 | 9,4e15 | 3 |
| d8 | 512 | 26.214.400 | 314.572.800 | 4,9e16 | 4 |
| d12 | 768 | 86.507.520 | 1.038.090.240 | 5,4e17 | 6 |

Chi phí tương đối so với d4: d6 ≈ 9,7×, d8 ≈ 51×, d12 ≈ 556× (theo 6·N·D, bỏ qua FLOPs attention). Thời gian thực phụ thuộc throughput đo được; không suy ra từ bộ đếm 74,25 giây của T4. Số head là một lựa chọn cần đóng băng trước (head-dim 64 như TTM hay 128 như nanochat), vì nó đổi cả chất lượng lẫn tham số.

**Dữ liệu cho từng bậc.** Với ~243 token mỗi truyện, d8 cần khoảng 1,3 triệu truyện, d12 khoảng 4,3 triệu truyện. Theo hiểu biết của tác giả bản nháp (chưa kiểm kê trong repo), TinyStories có cỡ vài triệu truyện nên có thể đủ tới khoảng d8 và **không đủ** cho d12 nếu chỉ dùng một epoch. Dùng lại dữ liệu nhiều epoch là một chế độ khác (data-constrained), không được trộn vào so sánh với các bậc dưới mà không khai báo.

**Tokenizer.** BPE hiện tại có vocab 2048 và chỉ học trên 768 truyện (nanochat mặc định 32768 và học trên một tập lớn hơn nhiều). Cần định một **điểm đóng băng tokenizer**: sau STEP1 và STEP4 (khi so sánh còn cần tokenizer cố định), quyết định có học lại BPE trên corpus lớn hơn và/hoặc vocab lớn hơn cho các bậc cao hay không. Khi tokenizer đổi: (i) NLL theo token không còn so sánh được, chỉ dùng bits per byte; (ii) fixture của STEP2 phải dựng lại (tên, đối tượng đơn token); (iii) các checkpoint cũ không dùng chung được.

**Chuyển siêu tham số.** nanochat suy lr, weight decay và batch theo scale (chú thích trong code nói rõ việc áp dụng lý thuyết AdamW cho Muon là giả định chưa nghiên cứu kỹ). Với TTM, không giả định chuyển được: mỗi bậc chạy một quét lr ngắn (2 seed, làn thăm dò) rồi mới chạy thật.

**Quy trình mỗi bậc:**
1. STEP0 đạt trên cấu hình mới (loss khởi tạo, rò rỉ nhân quả, overfit một batch).
2. Quét lr ngắn (làn thăm dò), chọn trên VAL-TUNE.
3. Huấn luyện tới horizon tỉ lệ 12, 3 seed, trong làn xác nhận cho khẳng định.
4. Đo `val_bpb` trên VAL2 và STEP2 (probe A, B, C).
5. Chỉ sang bậc kế tiếp nếu: `val_bpb` cải thiện so với bậc dưới vượt sai số giữa seed; STEP0 đạt; chỉ số STEP2 không thoái lui.

Quy luật scale chỉ được mô tả trong khoảng đã đo (4 bậc là ít để khớp một đường); không ngoại suy ra ngoài bậc cao nhất đã chạy.

## 4. Phần C: Dữ liệu là đòn bẩy cần đo, không chỉ kiến trúc

Trong `dev/LOG.md` của nanochat, chuyển từ FineWeb-EDU 100B sang ClimbMix 400B được ghi là cải tiến đơn lẻ lớn nhất cho thời gian speedrun (từ 2 giờ 46 phút xuống 2 giờ 1 phút, giảm 27%), sau các thí nghiệm dữ liệu trước đó được ghi là âm. Bài học cho TTM: khi vượt TinyStories, chất lượng và cấu thành dữ liệu có thể quan trọng hơn thủ thuật kiến trúc. Với TTM, cần:
- Một held-out tổng quát (không chỉ TinyStories) và probe không phụ thuộc template TinyStories.
- Thí nghiệm hỗn hợp dữ liệu ở d4 hoặc d6 trước khi tăng scale.
- Chuỗi quyền cho mọi corpus mới (STEP6): TinyStories có giấy phép CDLA-Sharing-1.0 theo QA của repo; mọi corpus khác phải được kiểm riêng và chưa có kết luận nào trong tài liệu này.

## 5. Phần D: Hậu huấn luyện (SFT) chỉ sau khi base đạt cổng

nanochat có chuỗi tokenization, pretraining, finetuning, đánh giá, suy luận (README). TTM chưa có dữ liệu chỉ thị, chưa có đánh giá chat và chưa có quyền dữ liệu cho việc đó. Cổng đề xuất để bắt đầu SFT: `val_bpb` theo đường cong lành mạnh, chỉ số STEP2 đạt nhãn tối thiểu do owner đóng băng (ví dụ A_PARTIAL và B_BINDING ở d = 0), và có thang đánh giá sinh đã kiểm (STEP3). Chưa đạt thì không SFT, vì SFT trên nền chưa bám ngữ cảnh chỉ tạo giao diện, không tạo năng lực.

## 6. Đặt tên và phạm vi (quyết định của owner)

Tên các bậc (ví dụ TTM-Small-11M cho d6) chỉ để minh họa; cách đặt tên và việc có phát hành hay không là quyết định của owner. Ở thời điểm tài liệu này, quyền công bố trọng số đang `HOLD` (STEP6).

## 7. Tiêu chí quyết định (đề xuất)

| Kết quả | Diễn giải | Bước tiếp |
|---|---|---|
| Gói contrastive tăng B/C ở d4 và d6, không tăng ở arm kiểm soát | Có lợi ích có điều kiện | Giữ làm lựa chọn; đo thêm ở d8 |
| Gói contrastive không tách khỏi NTP | Không giúp ở cấu hình này | Ghi kết quả âm; tiếp bậc thang |
| Bậc kế tiếp cải thiện `val_bpb` và chỉ số STEP2 | Giới hạn nằm ở dung lượng/compute | Tiếp tục bậc thang tới giới hạn dữ liệu hoặc ngân sách |
| Bậc kế tiếp cải thiện `val_bpb` nhưng STEP2 phẳng | Mô hình học thống kê tốt hơn nhưng không bám ngữ cảnh | Quay lại objective/dữ liệu (Phần A, C) |
| Không bậc nào rời sàn trên STEP2 | Giới hạn của nhiệm vụ, dữ liệu hoặc probe | `FLOOR_HOLD`; xem STEP2, STEP3 |
| Nguồn lực không đủ cho bậc kế | Dừng tại bậc đã đo | Báo cáo đúng phạm vi đã đo |

## 8. Ngân sách và dừng

Chi phí chưa biết. FLOPs ở bảng là ước tính thô; thời gian, bộ nhớ và chi phí tiền phải đo từ throughput thật của phần cứng được duyệt. Free T4 có thể không đủ cho d8 trở lên (các thiết kế D1 trước đây từng ghi `Free T4 feasibility HOLD`). Phải có ngân sách đã duyệt, kiểm toán custody của runner (STEP6) và điều kiện dừng trước mỗi bậc. Vượt ngân sách là `HOLD_RESOURCE_INCOMPLETE`, không phải FAIL.

## 9. Điểm yếu và giới hạn

- Các số trong bảng bậc thang là tính thô từ công thức; chưa được kiểm bằng runner và chưa tính các thành phần của STEP4 (ví dụ tách embedding thêm tham số).
- Bốn bậc không đủ để khẳng định một quy luật scale.
- TinyStories là dữ liệu tổng hợp hẹp; kết quả không nói về năng lực tổng quát.
- Đổi tokenizer phá tính so sánh theo token và phải dựng lại fixture.
- Kết quả của nanochat (d12–d26, 8×H100) không tự chuyển sang các bậc nhỏ; mỗi thành phần phải được đo lại (STEP4).
- Một người soạn; chưa có review độc lập.

## 10. Việc cần xác nhận

1. Owner: Question Gate, ngân sách, phần cứng, quyền dữ liệu và công bố, mục tiêu của "TTM nâng cấp" (bậc tối đa mong muốn).
2. Kiểm kê số truyện và token thực tế; tính lại bảng ở Phần B bằng runner.
3. Đóng băng head-dim, điểm đóng băng tokenizer và quy tắc chuyển siêu tham số.
4. Review độc lập trước khi chạy.

## 11. Ghi chú đồng bộ với `main` sau PR #39 (từ lineage L0030–L0035, chưa đọc mã)

- **Định nghĩa bpb.** Hợp đồng ABC (L0034, ALIGN-F03) dùng `val_bpb` chỉ-byte: loại token stop/protocol khỏi cả tử số NLL lẫn mẫu số byte UTF-8 hợp lệ. STEP0 mục 0.6 và STEP1 nên dùng **cùng định nghĩa** để số đo so sánh được với nhánh ABC; định nghĩa chính xác trong mã chưa được kiểm ở đây.
- **Tokenizer và SFT.** L0034 (ALIGN-F02) ghi `INCOMPATIBLE_DIRECT_T4_BC`: trong T4 các ID 257–2047 là merges BPE, còn trong B/C v2 các ID 257–262 là protocol specials; sidecar byte-span cho T4 mới ở mức thiết kế. Hệ quả cho Phần D và điểm đóng băng tokenizer: không dựng SFT trên BPE T4 hiện tại trước khi giải quyết xung đột này; khi chọn tokenizer mới phải tính cả token protocol.
- **Phạm vi quyền.** L0035 giữ `GPU/NEW_TEST=NOT_AUTHORIZED`, `REAL_SFT=HOLD_NOT_EXECUTED`. Lộ trình này vẫn là đề xuất, không phải permit.
