# Bước 1 — Đường cong scale ở horizon compute-optimal

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

## 1. Điều kiện mở và lý do thay thế Bước 4a của v1

Bước này **huấn luyện mô hình mới** nên chỉ được xem xét sau STEP0 và có Question Gate cùng quyết định owner. Nó thay Bước 4a của v1 (giữ 4,19M lượt tiếp xúc, chỉ đổi độ đa dạng dữ liệu), vì thiết kế đó vẫn nằm trong vùng thiếu huấn luyện.

## 2. Bằng chứng về mức thiếu huấn luyện (tính từ số liệu repo, chưa kiểm bằng runner)

nanochat đặt mặc định `--target-param-data-ratio 12` (Chinchilla là 20), tính trên các ma trận transformer cộng `lm_head` (chú thích trong `base_train.py` ghi cách đếm này cho quy luật scale gọn nhất). Với TTM:

| Đại lượng | Giá trị |
|---|---|
| Ma trận transformer: 4 layer × (196.608 + 65.536 + 262.144 + 262.144) | 3.145.728 |
| `lm_head` (dùng chung trọng số với embedding) 2048 × 256 | 524.288 |
| Tham số theo cách đếm nanochat | 3.670.016 |
| Horizon theo tỉ lệ 12 | 44.040.192 token |
| T4: lượt tiếp xúc | 4.194.304 (≈ 1,14 token/tham số) |
| T4: nhãn TRAIN độc lập | 498.287 (≈ 0,14 token/tham số) |
| Mức thiếu | ≈ 10,5× về lượt tiếp xúc; ≈ 88× về nhãn độc lập |

Thêm một bằng chứng từ chính repo: mô hình chỉ tốt hơn bigram khoảng 12% (VAL NLL ≈ 3,52 so với uniform 7,62). Nó mới ở giai đoạn đầu của đường học; bám ngữ cảnh là yêu cầu cao hơn nhiều so với thống kê cục bộ.

## 3. Câu hỏi

Với kiến trúc, tokenizer và optimizer cố định, tăng số token **độc lập** từ mức T4 tới horizon compute-optimal có làm giảm `val_bpb` và làm xuất hiện tín hiệu ngữ cảnh (IND và S, hoặc độ chính xác chọn-ending của STEP2) không? Và độ phẳng/độ dốc của đường cong nằm ở đâu?

## 4. Thiết kế

**Cố định:** kiến trúc T4 (vocab 2048, context 256, d 256, 4 layer, 4 head, LayerNorm, GELU, weight tying, vị trí học được); tokenizer BPE hiện tại (đã học trên 768 truyện TRAIN, **không học lại**); optimizer và lịch như T4, hoặc lr chọn ở STEP0 mục 0.8; 4.096 nhãn mỗi bước; mỗi arm có horizon riêng và lịch lr riêng (không dùng checkpoint trung gian của một run dài, vì lịch lr phụ thuộc horizon).

**Các arm (mỗi arm một lượt một epoch trên dữ liệu mới, trừ R0):**

| Arm | Lượt tiếp xúc | Số bước (4.096 nhãn/bước) | Dữ liệu |
|---|---|---|---|
| R0 | 4.194.304 | 1.024 | Tái lập T4: 0,5M nhãn độc lập, dùng lại ~8,4× |
| R1 | 4.194.304 | 1.024 | Cùng compute, 4,19M nhãn độc lập (một epoch) |
| T11 | 11.010.048 | 2.688 | Độc lập |
| T22 | 22.020.096 | 5.376 | Độc lập |
| T44 | 44.040.192 | 10.752 | Độc lập (≈ 12 token/tham số) |
| T88 (tùy chọn) | 88.080.384 | 21.504 | Độc lập (≈ 24 token/tham số) |

R0 so với R1 chính là phần còn lại của Bước 4a cũ: tách tác động của việc dùng lại dữ liệu ở cùng compute.

**Dữ liệu mới:** truyện TinyStories (bản đã ghim trong repo) chọn **tách rời theo hash** với VAL (256), TEST (64), VAL-TUNE (STEP0) và mọi fixture probe; được phép trùng với 2.048 truyện TRAIN cũ. Với ~243 nhãn mỗi truyện (498.287 / 2.048), T88 cần khoảng 362 nghìn truyện, T44 khoảng 181 nghìn. Theo hiểu biết của tác giả bản nháp (chưa kiểm kê trong repo), TinyStories có cỡ vài triệu truyện nên đủ; phải kiểm kê trước khi đóng băng.

**Held-out:** ngoài VAL cũ (256 truyện, nhiễu cao), dùng VAL2 lớn hơn (đề xuất ≥ 2.000 truyện, tách rời) để đo `val_bpb`. Báo cả nat/token và bits per byte (số byte mỗi token tính trên VAL2), vì tokenizer sẽ thay đổi ở các bước sau.

**Seed:** 3 seed mỗi arm cho pilot (khởi tạo và thứ tự dữ liệu độc lập).

**Đo dọc đường:** tại bước cuối của mỗi arm, chạy probe và bộ chọn-ending của STEP2 (không cần checkpoint trung gian).

## 5. Thống kê

- So sánh R0 với R1 và giữa các arm bằng hiệu `val_bpb` theo cặp seed, báo CI bootstrap.
- Khớp `L(T) = c + a·T^(−b)` chỉ để mô tả. Với 5–6 điểm và 3 tham số, **không ngoại suy ngoài khoảng đã đo** và không báo `b` như một hằng số tin cậy; báo CI.
- Tái lập: trung bình VAL NLL của R0 phải gần giá trị T4 (≈ 3,522339 ở bước 1024); dung sai đề xuất ±0,1 nat, vì T4 chỉ có một seed. Không đạt thì quay lại STEP0.
- Giữ lr cố định giữa các arm là một hạn chế đã biết (horizon dài có thể cần lr khác); nếu nguồn lực cho phép, kiểm lại ở T44 bằng một quét lr nhỏ.

## 6. Ngân sách (ước tính thô)

Từ bộ đếm 74,25 giây GPU cho 1.024 bước của T4 (gồm cả đánh giá VAL; không phải tổng thời gian phiên), tốc độ khoảng 0,0725 giây/bước. Tổng bước của mọi arm cho một seed (R0 + R1 + T11 + T22 + T44 + T88) là 41.344 + 1.024 ≈ 42.368 bước, tức cỡ 51 phút; ba seed cỡ 2,5 giờ GPU. Con số này chưa kiểm, giả định tốc độ không đổi theo horizon, và chưa tính chi phí giải mã dữ liệu, xây pack và đánh giá. Phải có ngân sách đã duyệt trước khi chạy; vượt ngân sách là `HOLD_RESOURCE_INCOMPLETE`, không phải FAIL.

## 7. Tiêu chí quyết định (đề xuất)

| Kết quả | Diễn giải | Bước tiếp |
|---|---|---|
| `val_bpb` giảm mạnh tới T44 và tín hiệu STEP2 tăng | Giới hạn bởi compute/dữ liệu | Bậc thang scale (STEP5) |
| `val_bpb` phẳng từ T11–T22, tín hiệu STEP2 ≈ 0 | Giới hạn của kiến trúc, dung lượng hoặc objective | STEP4 trước, rồi STEP5 (dung lượng) |
| `val_bpb` giảm, IND tăng nhưng S ≈ 0 | Có cơ chế sao chép, chưa có binding trên văn bản | STEP5 (objective, dữ liệu cân bằng vị trí) |
| R1 ≈ R0 | Độ đa dạng không phải nhân tố ở mức compute này | Tập trung vào compute |
| R1 tốt hơn R0 rõ | Dùng lại dữ liệu 8,4× gây hại | Ưu tiên dữ liệu độc lập |
| R0 không tái lập T4 | Lỗi pipeline hoặc khác biệt chưa nêu | Quay lại STEP0 |
| Mọi arm dính sàn trên endpoint | Endpoint thiếu độ nhạy | `FLOOR_HOLD`; xem STEP2 và STEP3 |

## 8. Điểm yếu và giới hạn

- Tokenizer học trên 768 truyện, vocab 2048, có thể kém trên dữ liệu lớn hơn; đã giữ cố định để tách biến, nhưng đó là một hạn chế (xem STEP5 về điểm đóng băng tokenizer).
- TinyStories là dữ liệu tổng hợp hẹp; kết luận chỉ áp dụng cho miền này.
- Cỡ 3,7M tham số, context 256; không nói gì về mô hình lớn hơn.
- Ba seed chỉ đủ để phát hiện hiệu ứng lớn.
- Huấn luyện từ đầu tạo trọng số dẫn xuất mới (xem STEP6).

## 9. Việc cần xác nhận

1. Owner: Question Gate, ngân sách, làn thăm dò hay xác nhận, quyền dữ liệu dẫn xuất.
2. Kiểm kê số truyện và token thực tế để tính lại bảng ở mục 4.
3. Đóng băng lr, dung sai tái lập, kích thước VAL2 và số seed.
4. Review độc lập trước khi chạy.
