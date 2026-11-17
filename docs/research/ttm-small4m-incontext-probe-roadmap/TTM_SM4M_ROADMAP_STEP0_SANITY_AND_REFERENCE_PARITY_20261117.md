# Bước 0 — Kiểm tra nền kiểu Recipe và đối chiếu implementation tham chiếu

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

## 1. Vì sao cần bước này

Bài "A Recipe for Training Neural Networks" của Karpathy xuất phát từ hai nhận xét: huấn luyện mạng nơ-ron là một lớp trừu tượng rò rỉ, và nó **thất bại âm thầm** (lỗi cấu hình thường không ném ngoại lệ mà chỉ làm kết quả tệ hơn một chút; ví dụ mô hình tự hồi quy vô tình nhận chính thứ cần dự đoán làm đầu vào vì lệch chỉ số một vị trí). Quy trình của bài: nhìn dữ liệu trước, dựng khung huấn luyện/đánh giá đầu-cuối cùng các baseline ngốc, kiểm tra loss khởi tạo, overfit một batch nhỏ, rồi mới phức tạp hóa từng thứ một.

TTM-Small-4M có kết quả "tốt hơn bigram ~11,9% (VAL) / ~12,3% (TEST) nhưng bám ngữ cảnh 0/16". Trước khi diễn giải đó là giới hạn của mô hình hay của chế độ huấn luyện, cần loại trừ **lỗi thực thi âm thầm** bằng bằng chứng chạy thật. Kiểm toán tĩnh "không thấy lỗi" (`ROOT_CAUSE_NOT_IDENTIFIED`) không thay thế bằng chứng chạy.

**Hiện trạng các kiểm thử (đã grep, phạm vi hẹp):** `tools/pilot_t4/integrated/tests/test_t4_integrated.py` có 13 test: cửa sổ không vắt qua truyện, sampler đúng 4096 nhãn hợp lệ, baseline chỉ fit trên TRAIN, pack không chứa TEST, fail-closed, nạp/ghi checkpoint. Trong bốn tệp được grep (test, `t4_capacity_smoke.py`, `t4_trainer_synthetic_gpu_integration.py`, `t4_eval.py`) **không thấy**: test rò rỉ nhân quả, so sánh loss khởi tạo với ln 2048, overfit một batch, đối chiếu với một implementation độc lập. Tác giả bản nháp chưa đọc các tệp khác, nên mục này chỉ nói "không thấy trong phạm vi đã grep".

## 2. Những điều đã xác minh từ mã nguồn (tĩnh)

| Điều | Nguồn |
|---|---|
| Mỗi truyện được mã hóa rồi **thêm EOS ở cuối**, cắt thành cửa sổ 256 không chồng lấn; cửa sổ cuối đệm 0 ở đầu vào và `-100` ở nhãn | `t4_data_pack.py` (`windows_for_ids`, `build_pack`) |
| **EOS chỉ xuất hiện như nhãn cuối truyện, không bao giờ là token đầu vào** (suy ra từ cách tạo `x` và `y`; cần xác nhận lúc chạy ở 0.1) | cùng tệp |
| Không có BOS; cửa sổ thứ hai trở đi của truyện dài bắt đầu giữa truyện nhưng nằm ở vị trí 0 | cùng tệp |
| Trainer lấy mẫu cửa sổ **có hoàn lại** đến khi đủ đúng 4096 nhãn hợp lệ mỗi bước; 1.024 bước | `t4_train_science_a2.py` (`sample_exact_step`) |
| AdamW, lr đỉnh 3e-4, betas (0,9; 0,95), weight decay 0,1 áp lên **mọi** tham số (kể cả embedding và LayerNorm), warmup 32 bước, clip gradient 1,0 | cùng tệp |
| Loss ở bước đầu được log, nhưng không có kiểm tra tự động so với ln 2048 | cùng tệp |

Điều thứ hai có hệ quả trực tiếp cho thiết kế probe (xem STEP2 mục 2): một chuỗi bắt đầu bằng EOS là **ngoài phân phối** so với huấn luyện.

## 3. Hai làn nghiên cứu (cần owner quyết định)

autoresearch của Karpathy chạy thí nghiệm ngắn với ngân sách thời gian cố định, so bằng `val_bpb`, giữ hoặc loại thay đổi. Ý tương ứng cho TTM:

- **Làn thăm dò:** các lần chạy rẻ, cố định ngân sách, ghi **mọi** run vào một bảng (commit, cấu hình, seed, `val_bpb`, kết quả, mô tả), có hash cho dữ liệu và mã. Kết quả **không bao giờ** ghi vào `lineage.md` như PASS/FAIL và **không được dùng làm bằng chứng cho một khẳng định**. Chỉ dùng để chọn câu hỏi và loại giả thuyết.
- **Làn xác nhận:** đăng ký trước, seed và dữ liệu mới, quản trị hiện hành giữ nguyên. Mọi khẳng định khoa học phải đi qua làn này.

Rủi ro chính là lối rẽ nhiều nhánh (forking paths): chạy nhiều biến thể rồi chỉ kể biến thể thắng. Biện pháp: bảng ghi mọi run là bắt buộc, và khẳng định chỉ hợp lệ khi lặp lại ở làn xác nhận. Việc có mở làn thăm dò hay không là quyết định của owner; tài liệu này không giả định đã được phép.

## 4. Danh mục kiểm tra và tiêu chí (đề xuất)

| Mã | Kiểm tra | Tiêu chí đề xuất |
|---|---|---|
| 0.1 | **Nhìn dữ liệu.** Giải mã và đọc ≥ 100 cửa sổ ngẫu nhiên (gồm cửa sổ bắt đầu giữa truyện); phân phối độ dài truyện theo token; tỉ lệ truyện > 257 token (nhiều cửa sổ); tỉ lệ cửa sổ bắt đầu giữa truyện; tỉ lệ cửa sổ có đệm; truyện trùng hoặc gần trùng trong TRAIN; round-trip tokenizer; đếm tên và danh từ đơn token (cần cho STEP2); **xác nhận EOS không bao giờ là đầu vào** | Báo cáo số liệu; EOS-as-input = 0 |
| 0.2 | **Loss khởi tạo.** NLL ở bước 0 so với ln 2048 = 7,6246 | \|loss − 7,6246\| ≤ 0,05 |
| 0.3 | **Rò rỉ nhân quả.** Đổi token ở vị trí t+1 trở đi; logits ở vị trí ≤ t không đổi | Khác biệt tối đa ≤ 1e-6 (FP32) |
| 0.4 | **Bất biến batch và đệm.** Loss của một cửa sổ không đổi khi đổi thành phần batch; vị trí nhãn `-100` không sinh gradient; chuẩn hóa theo số nhãn hợp lệ | Khác biệt ≤ 1e-6 |
| 0.5 | **Overfit một batch** (đúng 4096 nhãn như một bước T4), FP32, lr 1e-3, không weight decay; thêm: ghi nhớ 128 cửa sổ | Một batch: loss ≤ 0,05 trong ≤ 600 bước; 128 cửa sổ: loss ≤ 0,3 trong ≤ 2.000 bước |
| 0.6 | **Baseline ngốc.** Đều (7,6246 nat), unigram, bigram, trigram có back-off; báo cả nat/token và **bits per byte** (cần tính số byte mỗi token trên VAL) | Mô hình phải được đặt giữa các baseline; bpb báo cáo |
| 0.7 | **Đối chiếu implementation độc lập.** Một bản tối giản độc lập (kiểu nanoGPT: LayerNorm, GELU, weight tying, vị trí học được, cùng init) huấn luyện trên **cùng pack**, 3 seed mỗi bên. Nếu có quyền: nạp M1024 vào bản tham chiếu và so logits trên 64 cửa sổ VAL | VAL NLL trung bình lệch ≤ 2 sai số chuẩn gộp (hoặc ≤ 0,03 nat); logits lệch tối đa ≤ 1e-4 (FP32) |
| 0.8 | **Quét lr/weight decay (làn thăm dò).** lr ∈ {1e-4, 3e-4, 1e-3, 3e-3} × 2 seed ở đúng ngân sách T4 (1.024 bước); weight decay trên mọi tham số so với chỉ trên ma trận | Chọn trên một tập **VAL-TUNE** 128 truyện mới, không dùng ở nơi khác (không dùng VAL hay TEST để chọn) |
| 0.9 | **Động học mẫu sinh.** 8 prompt cố định, sinh greedy ở các bước {128, 256, …, 1024}, lưu riêng tư, owner đọc | Không chấm điểm; chỉ phát hiện suy biến bất thường |

Mục 0.7 theo tinh thần video GPT-2 124M của Karpathy, nơi bản tự dựng được kiểm bằng cách nạp trọng số tham chiếu và so kết quả. Lưu ý đây là phần tác giả bản nháp nhớ từ nội dung chung của video, không xem lại.

## 5. Quyết định

| Kết quả | Hệ quả |
|---|---|
| 0.1–0.7 đạt, 0.8 không cho thấy cải thiện đáng kể | Cấu hình T4 không bị lỗi thực thi rõ; tiếp STEP1 |
| 0.3, 0.4 hoặc 0.2 không đạt | Lỗi thực thi; sửa và loại bỏ mọi kết luận dựa trên các run đã qua đường đó |
| 0.7 lệch ngoài dung sai | Tìm lỗi ở một trong hai implementation trước khi làm gì khác |
| 0.8 cho thấy lr khác tốt hơn rõ (đề xuất: ≥ 0,15 nat VAL-TUNE) | Baseline T4 chưa được tinh chỉnh; tái lập baseline trước khi kết luận về "giới hạn mô hình" |
| 0.1 phát hiện bất thường dữ liệu (EOS làm đầu vào, trùng lặp lớn, cửa sổ rác) | Ghi nhận; ảnh hưởng đến cách thiết kế probe và pack mới |

## 6. Điểm yếu và giới hạn

- Các ngưỡng là đề xuất; chưa có hiệu chuẩn.
- Bản tham chiếu tự dựng cũng có thể có lỗi giống bản gốc nếu cùng người viết; nên do một bên độc lập viết hoặc dùng bản công khai.
- Quét lr chỉ ở một ngân sách ngắn có thể không chuyển sang horizon dài hơn.
- Một số kiểm tra (0.7 phần logits) cần quyền truy cập checkpoint (STEP6).

## 7. Việc cần xác nhận

1. Owner: có mở làn thăm dò không, và ai giữ bảng ghi mọi run.
2. Chọn bản tham chiếu (tự viết, nanoGPT hoặc nanochat cấu hình tương thích) và ai viết/độc lập.
3. Xác nhận kích thước tập VAL-TUNE và rằng nó tách rời VAL, TEST, fixture probe.
4. Đọc phần còn lại của bộ test để cập nhật mục 1.
