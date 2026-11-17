# Bước 4 — Ablation kiến trúc từng thay đổi một

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

## 1. Điều kiện mở

Bước này **huấn luyện mô hình mới**. Chỉ xem xét sau STEP0 (nền sạch), STEP1 (có đường cong baseline) và có Question Gate cùng quyết định owner. Nó trả lời: trong các thành phần hiện đại của nanochat, thành phần nào đáng đưa vào TTM ở quy mô của TTM?

## 2. Khoảng cách kiến trúc hiện tại

| Thành phần | TTM-Small-4M (đã đọc `p02`/T4) | nanochat (đã đọc `nanochat/gpt.py`) |
|---|---|---|
| Vị trí | Embedding vị trí học được, context 256 | Rotary, không có embedding vị trí |
| Chuẩn hóa | LayerNorm (có tham số) | RMSNorm không tham số; norm sau embedding |
| Attention | Nhiều head chuẩn | QK-norm; hỗ trợ GQA; cửa sổ trượt theo mẫu |
| MLP | GELU | relu² |
| Bias | Có | Không |
| Embedding và đầu ra | Dùng chung trọng số | Tách rời |
| Optimizer | AdamW lr 3e-4, wd 0,1 mọi tham số | Muon cho ma trận, AdamW cho embedding và scalar; lr, wd, batch suy ra theo scale |
| Khác | | Value embedding xen kẽ, smear, backout, residual scalar mỗi layer, softcap logits |

Ghi chú: các thành phần sau cùng (value embedding, smear, backout, scalar mỗi layer) là tinh chỉnh dày đặc của một mã nguồn tối ưu cho tốc độ đạt GPT-2; không đề xuất đưa vào ở bước này.

## 3. Quy tắc làm việc (rút từ Recipe và LOG của nanochat)

- **Chỉ thay một thứ mỗi lần** so với baseline (lời khuyên "phức tạp hóa từng thứ một" của Recipe).
- `LOG.md` của nanochat ghi **nhiều kết quả âm** khi thử ý tưởng ở d12–d26: các mục có tiêu đề đánh dấu âm gồm SwiGLU, Mixture of Experts, DyT, quét ý tưởng parameter-golf, Hyperball/MuonH, varlen attention, hai thí nghiệm dữ liệu; quét ý tưởng modded-nanogpt được ghi là phần lớn âm; bigram hash embedding bị hoàn tác (reverted). Prior hợp lý: **phần lớn thay đổi sẽ không có tác dụng đo được** ở scale này. Không được đọc nhiễu thành tác dụng.
- Quy tắc **đề xuất của tác giả bản nháp** (không phải quy tắc đã xác minh của nanochat): chỉ nhận thay đổi nếu thắng ở cả d4 và d6, để tránh nhận một thay đổi chỉ hợp một scale.
- Ghi kết quả âm lẫn dương vào một nhật ký (như `dev/LOG.md`), kể cả khi chúng không đi vào `lineage.md`.

## 4. Thiết kế

**Baseline:** cấu hình T4 với lr đã chọn ở STEP0 (mục 0.8), huấn luyện ở horizon sàng lọc T11 (11.010.048 lượt tiếp xúc, 2.688 bước) của STEP1.

**Thứ tự ablation (mỗi cái chạy riêng so với baseline, không tích lũy):**

| Mã | Thay đổi | Ghi chú kiểm soát |
|---|---|---|
| A1 | Rotary thay embedding vị trí học được | Giả thuyết: cửa sổ T4 thứ hai trở đi bắt đầu giữa truyện ở vị trí 0, vị trí tương đối tự nhiên hơn. Đây là giả thuyết, chưa phải kết quả |
| A2 | RMSNorm không tham số thay LayerNorm | Giảm tham số nhỏ |
| A3 | QK-norm | |
| A4 | Tách embedding và đầu ra | Thêm 524.288 tham số: báo cả tổng tham số lẫn tham số theo cách đếm scaling |
| A5 | relu² thay GELU | |
| A6 | Bỏ bias | |
| A7 | Muon cho ma trận, AdamW cho phần còn lại, theo quy tắc lr của nanochat | Chú thích trong code của nanochat thừa nhận việc áp dụng lý thuyết AdamW cho Muon "chưa được nghiên cứu kỹ, là giả định"; thử **cuối cùng**, cần quét lr riêng |

**Endpoint chính:** `val_bpb` trên VAL2 ở cố định số token (nat/token và bits per byte). **Phụ:** token/giây và bộ nhớ; chỉ số của STEP2 ở bước cuối. Một thay đổi phải không làm xấu các chỉ số STEP2.

**Seed:** 3 seed ở giai đoạn sàng lọc. Thay đổi qua sàng lọc (hiệu `val_bpb` có CI loại trừ 0 theo hướng có lợi) được xác nhận ở T44 và ở d6 (STEP5) với seed mới.

**Đa phép thử:** 7 ablation tạo nguy cơ dương tính giả. Khai báo trước quy tắc điều chỉnh (đề xuất: Holm trên 7 phép thử ở giai đoạn sàng lọc) hoặc coi sàng lọc chỉ là bước chọn ứng viên, còn khẳng định chỉ đến từ giai đoạn xác nhận.

## 5. Ngân sách (ước tính thô)

Mỗi ablation ở T11 cỡ 2.688 bước × 0,0725 giây ≈ 195 giây mỗi seed; 7 ablation × 3 seed ≈ 68 phút GPU, chưa tính A7 (cần quét lr) và chi phí khác. Ước tính từ cùng bộ đếm 74,25 giây của T4; chưa kiểm, và các thành phần như rotary hay Muon có thể đổi tốc độ. Phải có ngân sách đã duyệt trước khi chạy.

## 6. Tiêu chí quyết định (đề xuất)

| Kết quả | Hệ quả |
|---|---|
| Thay đổi thắng ở sàng lọc, xác nhận ở T44 và d6, không làm xấu STEP2 | Nhận vào cấu hình cơ sở của lộ trình |
| Thắng ở d4 nhưng không ở d6 (hoặc ngược lại) | Không nhận; ghi nhật ký là phụ thuộc scale |
| Không khác baseline | Ghi kết quả âm; không nhận |
| Làm xấu `val_bpb` hoặc chỉ số STEP2 | Loại |
| Hai thay đổi riêng lẻ đều thắng | Thử kết hợp như một ablation mới, không giả định cộng tính |

## 7. Điểm yếu và giới hạn

- Kết quả của nanochat ở d12–d26 không chuyển tự động sang d4; từng thay đổi phải đo lại.
- Ablation riêng lẻ bỏ qua tương tác giữa các thành phần.
- 3 seed chỉ phát hiện hiệu ứng khá lớn; hiệu ứng nhỏ sẽ bị bỏ sót.
- lr của nanochat suy ra cho setup của nó (batch lớn, nhiều GPU); không chuyển nguyên.
- Một người soạn; chưa có review độc lập.

## 8. Việc cần xác nhận

1. Owner: Question Gate, ngân sách, quyền chạy.
2. Chọn bản triển khai tham chiếu cho từng thành phần (viết tay hay lấy từ nanochat), và ghi nguồn mã cùng giấy phép.
3. Đóng băng quy tắc đa phép thử và dung sai.
4. Review độc lập trước khi chạy.
