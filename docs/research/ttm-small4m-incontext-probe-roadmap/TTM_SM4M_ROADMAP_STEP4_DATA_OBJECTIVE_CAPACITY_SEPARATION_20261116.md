# Bước 4 — Tách data / objective / capacity cùng ngân sách thông tin

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

## 1. Điều kiện mở bước này

Bước 4 là **huấn luyện mô hình mới** và chỉ được xem xét khi: STEP1–STEP2 đã cho kết quả hợp lệ; STEP3 đã cho thang đủ phân biệt (hoặc endpoint teacher-forced đủ làm endpoint chính); STEP5 đã cho quyền và custody; và có Question Gate cùng quyết định owner theo `TTM-GOV-QF-20261115-V1` (Q1 → Q4, rồi I1 → I4). Tài liệu này chỉ là thiết kế điều kiện; **không phải quyền thực thi**. Kết quả của STEP1–STEP3 quyết định nhánh nào dưới đây được mở (xem bảng quyết định STEP1 mục 6).

## 2. Biến nhiễu rõ nhất chưa được kiểm

Từ chính hồ sơ repo:
- T4 chạy 1.024 bước × 4.096 nhãn mục tiêu = **4.194.304 lượt tiếp xúc**, nhưng chỉ khoảng **498.287 mục tiêu TRAIN độc lập** (từ 2.048 truyện), nên mỗi vị trí dùng lại trung bình **~8,417 lần**.
- Mô hình có **3.749.376 tham số**; số mục tiêu độc lập nhỏ hơn số tham số cỡ 7,5 lần.
- FMEA của Q001 xếp **QF-04 (độ bao phủ dữ liệu) mức MEDIUM, chưa được thử**. Kiểm toán ghi rõ "có thể gây giới hạn bao phủ, chưa chứng minh là root cause".
- Các kết quả liên quan đều lẫn biến: FC01 (objective + data + tác vụ, 1 seed), A/C FINAL24 (objective, 128 update/arm, không lợi ích), H-DATA-S1 (data, bị kẹt ở sàn 0 nên không kết luận được).

Vì vậy chưa có thí nghiệm nào tách **độ đa dạng dữ liệu** khỏi **tổng compute** và khỏi **objective**.

## 3. Câu hỏi

Với kiến trúc, tokenizer và tổng số lượt tiếp xúc cố định, thay đổi (a) độ đa dạng dữ liệu độc lập, (b) objective, (c) dung lượng, có làm tăng endpoint teacher-forced (IND, S) của STEP1 và/hoặc endpoint thang đo đã kiểm định của STEP3 không, và theo thứ tự nào thì tách được nguyên nhân?

## 4. Thiết kế theo giai đoạn (mỗi giai đoạn dừng và quyết định trước khi sang giai đoạn sau)

### 4a. Liều lượng dữ liệu ở cùng compute (ưu tiên đầu tiên)
Giữ nguyên: kiến trúc T4 (2048/256/256/4/4), tokenizer BPE hiện tại (học trên 768 truyện TRAIN, **không học lại**), optimizer (AdamW, đỉnh 3e-4, weight decay 0,1, warmup 32 + cosine, clip 1), **1.024 bước × 4.096 nhãn**, độ chính xác FP16 như T4.

Chỉ đổi số mục tiêu độc lập (hệ số dùng lại giảm tương ứng):

| Arm | Mục tiêu TRAIN độc lập (xấp xỉ) | Số lần dùng lại trung bình |
|---|---|---|
| D0 (hiện tại) | 0,5M | ~8,4 |
| D1 | 2,1M | ~2 |
| D2 | 4,2M | ~1 (một epoch) |

Ước tính số truyện cần thêm dựa trên ~243 mục tiêu mỗi truyện (498.287 / 2.048): D1 cần khoảng 8,6 nghìn truyện, D2 khoảng 17,2 nghìn truyện. Đây là phép tính thô từ số liệu repo, cần tính lại trên dữ liệu thật.

Ràng buộc dữ liệu: chọn truyện mới **tách rời theo hash** với VAL (256 truyện), TEST (64 truyện, đã tiêu thụ) và mọi truyện dùng trong probe/fixture; ghi near-duplicate; dùng đúng bản TinyStories đã ghim (`roneneldan/TinyStories`, revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, giấy phép CDLA-Sharing-1.0 theo tài liệu quyền của repo). **Quyền chọn tập con và huấn luyện từ nó là quyết định riêng của owner** (xem STEP5 mục về dữ liệu dẫn xuất).

### 4b. Objective (chỉ mở nếu 4a để lại khoảng cách)
So NTP thuần với gói contrastive của FC01 trên cùng dữ liệu. Phải khai báo đúng như repo đã làm ở D1 V4/V5: đây là **gói contrastive** (loss cộng giám sát âm cộng compute thêm), **không** phải so sánh objective thuần hay ngang FLOPs. Ghi riêng chi phí thêm.

### 4c. Dung lượng (chỉ mở nếu 4a và 4b để lại khoảng cách)
Tăng dung lượng ở cùng dữ liệu và objective đã chọn từ 4a/4b. Cấu hình ứng viên (số layer, độ rộng) **phải được tính số tham số bằng runner trước khi đóng băng**; tài liệu này không ghim con số nào chưa kiểm.

## 5. Endpoint và thống kê

- **Chính:** IND và S của STEP1 (teacher-forced, không rater), đo bằng cùng runner, cùng fixture bytes đã khóa. Phụ: VAL NLL (kiểm tra sức khỏe, không phải endpoint chính), và thang đã kiểm định ở STEP3 nếu qua cổng.
- **Seed:** nhiều seed độc lập (khởi tạo và thứ tự dữ liệu). Đề xuất **pilot 5 seed mỗi arm**; nếu có tín hiệu, mở rộng tới **12 seed** theo tiền lệ D1 V3–V6 của repo (kiểm định dấu chính xác một phía, k ≥ 10/12). Số seed và ngưỡng phải được đóng băng trước kết quả.
- **So sánh:** theo cặp seed trong cùng arm (cùng seed khởi tạo giữa các arm), báo hiệu ứng và CI; kiểm tra xu hướng liều–đáp ứng đơn điệu D0 < D1 < D2.
- **Tránh sàn:** nếu mọi arm cùng ở sàn trên endpoint thì ghi `FLOOR_HOLD`, không kết luận.

## 6. Biến nhiễu phải kiểm soát

- Compute: cùng số bước, cùng số nhãn mỗi bước, cùng schedule. Báo thêm tổng token duy nhất, hệ số dùng lại và thời gian thật.
- Tokenizer cố định (không học lại trên dữ liệu mới) để tách khỏi biến dữ liệu.
- Rò rỉ giữa TRAIN mới và VAL/TEST/probe; near-duplicate.
- Phân phối độ dài truyện giữa các arm.
- Thứ tự dữ liệu, seed, độ chính xác số (FP16 giống T4).
- Đo cùng checkpoint rule (bước cuối cố định, không chọn theo kết quả).

## 7. Tiêu chí quyết định (đề xuất)

| Kết quả | Diễn giải | Bước tiếp |
|---|---|---|
| IND hoặc S tăng đơn điệu theo D0 < D1 < D2 với CI loại trừ 0 | Độ đa dạng dữ liệu (ở cùng compute) là nhân tố quan trọng | Ưu tiên mở rộng dữ liệu; hoãn 4b, 4c |
| D0 ≈ D1 ≈ D2 và probe hợp lệ | Dữ liệu ở cỡ này không phải nút thắt | Mở 4b |
| 4b không tách khỏi NTP | Gói contrastive không giúp ở cấu hình này | Mở 4c |
| Không arm nào rời sàn | Giới hạn cỡ nhiệm vụ/mô hình hoặc thang chưa nhạy | `FLOOR_HOLD`; quay lại STEP3 |
| Chênh giữa các arm nhỏ hơn sai số giữa seed | Không kết luận | Tăng seed hoặc dừng |

## 8. Ngân sách và dừng

Chi phí chưa biết. Repo ghi bộ đếm GPU của lần train T4 gốc là 74,25 giây (cộng đánh giá VAL, không phải tổng thời gian phiên Colab), nhưng không suy ra được chi phí cho dữ liệu lớn hơn và nhiều seed; các thiết kế D1 trước đây từng ghi `Free T4 feasibility HOLD`. Phải có ngân sách đã duyệt, kiểm toán custody của runner, và điều kiện dừng trước khi bắt đầu. Vượt ngân sách là `HOLD_RESOURCE_INCOMPLETE`, không phải FAIL.

## 9. Điểm yếu và giới hạn

- 4a chỉ đổi số truyện độc lập trong cùng phân phối TinyStories; không nói về dữ liệu có cấu trúc bám thực thể.
- Một tokenizer đã học trên 768 truyện có thể kém trên truyện mới, tạo biến nhiễu nhỏ.
- Số seed 5 và 12 là đề xuất, chưa có phân tích độ mạnh.
- Kết quả chỉ áp dụng cho cấu hình T4 (3,75M tham số, context 256, vocab 2048).
- Một người soạn; chưa có review độc lập.

## 10. Việc cần xác nhận

1. Owner: Question Gate, ngân sách, quyền dữ liệu dẫn xuất.
2. Kiểm kê số truyện và token thực tế để tính lại bảng ở 4a.
3. Đóng băng số seed, ngưỡng và quy tắc dừng.
4. Review độc lập trước khi chạy.
