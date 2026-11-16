# Bước 2 — Đối chứng random-init và hai checkpoint 1024/1280

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

## 1. Mục đích

Dùng **cùng probe, cùng fixture, cùng runner** của STEP1 trên các arm đối chứng để biết (a) probe có đo đúng thứ nó định đo không (negative control), và (b) 256 bước huấn luyện thêm từ 1024 lên 1280 có làm thay đổi cơ chế sao chép/binding hay không. Quyết định bị thay đổi: nếu M1280 không khác M1024 ở cả hai probe thì không có lý do dùng thêm bước huấn luyện đơn thuần như một giả thuyết cứu vãn; nếu probe không phân biệt được random-init với M1024 thì không được dùng probe để kết luận về mô hình.

## 2. Các arm

| Arm | Nội dung | Vai trò | Trạng thái nguồn |
|---|---|---|---|
| M1024 | Checkpoint T4 bước 1024, SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | Đối tượng chính | SHA đã được kiểm lịch sử (lineage L0011); byte chưa kiểm lại trong tài liệu này |
| M1280 | "Step1280 exploratory continuation", SHA-256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` | So sánh theo cặp với M1024 | SHA lấy từ `docs/reproducibility/TTM_SMALL4M_T4_REPRODUCIBILITY_MANIFEST_20261109.md` trên nhánh `docs/ttm-small4m-model-card-dataset-rights-20261109`; **chưa kiểm byte, chưa đọc kỹ cách tạo** |
| R0a, R0b, R0c | `GPT(P02Config(2048, 256, 256, 4, 4))` khởi tạo ngẫu nhiên bằng `_init_weights` của P02 (chuẩn tắc, std 0,02), 3 seed cố định dẫn xuất từ 20261116 | Negative control chính | Không cần quyền checkpoint |
| W1024 (tùy chọn) | M1024 với từng tensor bị xáo trộn phần tử | Kiểm tra probe có nhạy với thống kê trọng số thay vì cấu trúc học được | Cần cùng quyền như M1024 |
| M256, M512, M768 (tùy chọn) | Ba mốc trung gian của cùng lần train (lineage L0011: 4 mốc, mỗi tệp 45.074.891 byte) | Đường cong xuất hiện cơ chế | SHA chưa được ghim trong tài liệu này |

**Lưu ý về M1280:** theo lineage L0015, FRESH16 không phải kết quả confirmatory của checkpoint 1280, và FRESH12 ghi VAL NLL M1280 thấp hơn (~3,498089 so với ~3,522339) nhưng `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`. Trước khi diễn giải bất kỳ so sánh M1024 và M1280 nào phải đọc nhánh nguồn `research/ttm-small4m-q1q2-quality-single-batch-20261109` để biết 256 bước đó dùng dữ liệu, optimizer và schedule nào, và có đổi cách serialize hay không. Nếu 256 bước dùng dữ liệu khác thì chênh lệch không thể quy cho "thêm bước".

## 3. Random-init: không phải mô hình thay thế

Random-init ở đây **chỉ** là negative control cho probe. Nó không phải một "scratch model" để thay checkpoint khi custody thất bại (DIAG-Q001 cấm thay thế kiểu đó). Nó không cần quyền trọng số nhưng vẫn cần cùng runner, fixture và cổng QA.

Kỳ vọng nếu probe hợp lệ: IND ≈ 0 ở mọi m, S ≈ 0 ở cả hai nhóm. Nếu random-init cho IND lệch khỏi 0 quá ±0,1 nat hoặc S có CI loại trừ 0, probe bị `HOLD_PROBE_INVALID`.

## 4. Các đối chiếu khai báo trước

| Mã | Đối chiếu | Câu hỏi |
|---|---|---|
| C1 | M1024 so với R0 (3 seed) | Huấn luyện có tạo ra tín hiệu mà probe nhìn thấy không? |
| C2 | M1280 trừ M1024, theo cặp trên cùng item | 256 bước thêm có đổi IND hoặc S không? |
| C3 | M256 → M512 → M768 → M1024 (tùy chọn) | Cơ chế xuất hiện lúc nào, có bão hòa không? |
| C4 | M1024 so với W1024 (tùy chọn) | Tín hiệu có phụ thuộc cấu trúc học được hay chỉ thống kê trọng số? |

Với C2, dùng paired bootstrap trên item và so sánh bằng **biên tương đương** thay vì chỉ kiểm tra khác 0: đề xuất biên ±0,3 nat cho IND và ±0,05 cho tỉ lệ S > 0. Kết quả "tương đương" chỉ có nghĩa nếu CI nằm trọn trong biên; CI rộng thì ghi `INCONCLUSIVE`, không ghi "không khác".

## 5. Tiêu chí quyết định (đề xuất)

| Kết quả | Diễn giải | Bước tiếp |
|---|---|---|
| C1: M1024 không tách khỏi R0 ở cả A và B | Chưa có bằng chứng cơ chế; hoặc probe thiếu độ nhạy | Kiểm tra độ nhạy bằng positive control (STEP3, mục kiểm soát dương) trước khi kết luận |
| C1 tách rõ ở A, không tách ở B | Có sao chép nhưng không có binding trên văn bản | STEP4, nhánh data/objective |
| C2 tương đương | Thêm 256 bước không đổi cơ chế | Không ưu tiên "thêm bước" như giả thuyết cứu vãn |
| C2 M1280 cao hơn rõ | Cơ chế còn đang tăng | Ủng hộ nhánh liều lượng huấn luyện ở STEP4 |
| C2 M1280 thấp hơn rõ | Quên hoặc nhiễu của đoạn tiếp tục | Đọc lại cách tạo M1280 trước khi diễn giải |
| C4 W1024 tách giống M1024 | Probe nhạy với thống kê, không hợp lệ | HOLD_PROBE_INVALID |

## 6. Số mẫu, ngân sách, dừng

Dùng đúng fixture bytes của STEP1 cho mọi arm (cùng hash) để so sánh theo cặp. Không tạo fixture riêng cho từng arm. Ngân sách và điều kiện dừng như STEP1 mục 7, nhân với số arm. Mọi arm có checkpoint đều phụ thuộc STEP5; M1280 cần được nêu rõ trong chứng nhận quyền vì DIAG-Q001 hiện chỉ ghim SHA của M1024.

## 7. Điểm yếu và giới hạn

- M1280 là một lần tiếp tục của một lần train, một seed; hai điểm không phải hai mẫu độc lập về "bước huấn luyện".
- Random-init chỉ phủ một phân phối khởi tạo; nó không loại trừ mọi nhiễu của probe.
- Khác biệt M1280 và M1024 có thể bị trộn bởi cách tiếp tục huấn luyện (optimizer state, schedule, serialization), chưa được xác minh.
- Tất cả vẫn là teacher-forced; không nói gì về sinh tự do.

## 8. Việc cần xác nhận

1. Đọc nguồn nhánh Q1/Q2 để xác định chính xác M1280 là gì, và ghim SHA M1280 sau khi kiểm byte.
2. Quyết định có đưa W1024 và các mốc 256/512/768 vào phạm vi hay không (chi phí nhỏ, nhưng thêm vào bề mặt quyền).
3. Đóng băng biên tương đương cho C2 trước khi mở checkpoint.
