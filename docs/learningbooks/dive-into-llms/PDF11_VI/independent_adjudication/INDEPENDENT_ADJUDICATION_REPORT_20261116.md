# DIVE_INTO_LLMS — Independent Source–Target Language Adjudication

**Ngày kiểm tra:** 2026-11-16  
**Operation:** `DIVE_INTO_LLMS_11PDF_VI_INDEPENDENT_SOURCE_TARGET_LANGUAGE_ADJUDICATION_SINGLE_GATE`  
**Phạm vi:** 11 bài giảng / 495 trang, PDF gốc pin `Lordog/dive-into-llms@f84c04268794ef94f8949808bbc14ab8636763a0`; bản song ngữ `minhtri22/TokenToModel-Lab` tại nhánh `docs/learningbooks-dive-into-llms-vi-20261116`, HEAD kiểm tra `9544b06b9c95a319cae764957bad2c7450b11a9f`.

## Quyết định / Verdict

**`FULL_LITERAL_TRANSLATION_ADMISSION=FAIL`**, do có các phản ví dụ trực tiếp. **`OWNER_GATE=HOLD_NO_PASS_FIDELITY`**. Đây là quyết định QA tài liệu, không phải kết quả khoa học hay phủ nhận giá trị học tập của bản song ngữ. Không merge `main`; không sửa `lineage.md`; không chạy mô hình, notebook hoặc thí nghiệm.

**Ranh giới độc lập:** Lần kiểm tra này dùng đường thực thi đối chiếu riêng, đọc lại PDF nguồn và bản target đã khóa thay vì dựa vào những kết luận tự báo của chương trình tạo PDF. Tuy nhiên người phân xử là **AI trong cuộc trò chuyện này**, không phải chuyên gia ngôn ngữ độc lập được chỉ định; không nhận là `INDEPENDENT_HUMAN_LANGUAGE_QA_PASS`.

## Kết quả thực tế / Evidence boundaries

| Phép kiểm tra | Phạm vi | Kết quả | Điều không chứng minh được |
|---|---:|---|---|
| SHA-256 nguồn PDF và PDF/Markdown đích | 11+11+11 file | PASS | Không chứng minh dịch đúng |
| Bản gốc và target mở được, khớp số trang | 495 | PASS | Không chứng minh đủ bảng/hình |
| Sàng lọc kỹ thuật bằng trích xuất text, chỉ số ảnh, công thức, label | 495 | COMPLETED | Các cờ là *heuristic triage*; không phải chấm ngữ nghĩa |
| Đối chiếu source–target bằng cách đọc trích đoạn | 22 trang / 11 chương | REVIEWED_SCOPED | 473 trang chưa được adjudicate ngữ nghĩa |
| Xem ảnh nguồn + target cùng trang | 8 trang | REVIEWED_SCOPED_VISUAL | Không bao phủ tất cả ô trong sơ đồ |
| Ngôn ngữ bởi chuyên gia độc lập | 0 | NOT_EXECUTED | Không được cấp PASS_FIDELITY |

**Phân loại 22 trang đọc đối chiếu:** 8 `BLOCK_*`; 6 `PARTIAL_PARAPHRASE`; 8 `SCOPED_MEANING_MATCH`. `SCOPED_MEANING_MATCH` chỉ có nghĩa các thông tin chính đọc được tại trang đó hợp nghĩa với nguồn; không đồng nghĩa bản dịch nguyên văn của toàn trang đã được xác minh.

**Tín hiệu sàng lọc không được diễn giải thành lỗi chắc chắn:** 113 trang có nguồn >=600 ký tự và tỷ lệ độ dài ghi chú/nguồn <0.5; 34 trang rất dày có tỷ lệ <0.75; 80 trang có ít tên kỹ thuật Latin khớp nguyên dạng trong ghi chú; 75 trang chứa ít nhất 5 đối tượng ảnh trong PDF gốc; 7 trang được bộ từ khóa đánh dấu có thể chứa bảng/thuật toán. Những tập này chồng lặp và **không phải số trang bị dịch sai**. Chi tiết toàn bộ 495 dòng nằm trong `PAGE_SCREEN_495.csv`.

## Phát hiện có bằng chứng nguồn (8 blockers)

| ID | Thành phần | Phát hiện đối chiếu | Phân xử |
|---|---|---|---|
| CH01/P20 | Bảng đối chiếu mô hình | Các giá trị theo hai cột về attention, training, tác vụ, khả năng nổi lên bị quy thành danh sách các trục so sánh | BLOCK_TABLE_CELLS_OMITTED |
| CH01/P43 | Bảng Llama 1–3.2 | Bỏ nhiều ô của ma trận 5 phiên bản; không thể tái tạo số liệu theo từng phiên bản từ phần Việt | BLOCK_TABLE_CELLS_OMITTED |
| CH06/P22 | Prompt dài DAN | Phần Việt nói rõ là diễn giải ý chính thay vì dịch từng câu | BLOCK_LONG_TEXT_OMITTED |
| CH06/P27 | Prompt “developer mode” giả | Tương tự: cả khối văn bản nguồn được thay bởi lời mô tả | BLOCK_LONG_TEXT_OMITTED |
| CH08/P07 | Ma trận MLLM modality × functionality | Nhiều tên mô hình và liên kết từng ô bị rút thành vài ví dụ | BLOCK_TABLE_CELLS_OMITTED |
| CH09/P14 | Bảng ba nhánh xây dựng GUI Agent | **Sai ánh xạ:** nguồn đặt OS-Atlas/Auto-GLM dưới *pretraining*, nhưng Việt lại đặt dưới *instruction tuning*; tách imitation thành nhánh thứ tư dù nguồn là ba cột | BLOCK_SEMANTIC_MISASSIGNMENT |
| CH10/P08 | Sơ đồ backdoor theo giai đoạn | Nhiều nhánh thuật toán cấy/backdoor bị quy thành 3 nhóm lớn, không có bản Việt cho nội dung kỹ thuật của sơ đồ | BLOCK_DIAGRAM_LABELS_OMITTED |
| CH11/P17 | Sơ đồ Policy Gradient | Công thức cập nhật θ có bản Việt, nhưng **công thức ước lượng gradient từ quỹ đạo và log πθ** trên hình không được dịch/giải thích | BLOCK_FORMULA_OMITTED |

## Những trang diễn giải một phần (6)

- **CH02/P57:** prompt mẫu OS-Copilot rất dài được diễn giải; chú giải đã lưu ý dấu lược có sẵn trong hình nguồn, không được tự thêm phần không hiện trong slide.
- **CH03/P05:** ba ví dụ về đầu ra không mong muốn được tóm tắt; chưa dịch từng cặp câu hỏi và đầu ra.
- **CH07/P09:** cơ chế next-token steganography hợp ý chính; chi tiết token ID theo thứ tự xác suất và cách chọn ứng viên không đầy đủ.
- **CH07/P13:** ví dụ giả thuyết về DNA và các môi trường/vật chứa được diễn giải, bỏ nhiều ví dụ cụ thể của tác giả.
- **CH08/P14:** mô tả encoder → LLM có nhưng không chuyển mọi nhãn trong sơ đồ âm thanh.
- **CH10/P28:** bảng TrojanRAG ba kịch bản tóm lược được ý chính nhưng chưa chuyển đủ từng ô và nhãn.

## Những trang khớp ý nghĩa trong phạm vi kiểm tra (8)

`CH02/P47`, `CH03/P07`, `CH04/P07`, `CH04/P14`, `CH05/P12`, `CH05/P41`, `CH09/P17`, `CH11/P22`. Giữ nhãn **scoped** vì không có kiểm toán ngôn ngữ độc lập toàn trang và không thể suy rộng sang cả chương.

## Hạn chế và hướng khắc phục

1. **F02 — FAIL admission cho bản dịch nguyên văn.** Bổ sung nội dung ở bảng, đoạn dài, công thức và sơ đồ; mỗi dòng/nhãn có chỗ neo trang và nguồn. Không thay phần Việt hiện có bằng nhận định suy đoán ngoài tài liệu.
2. **F04 — lỗi ngữ nghĩa có thể tái kiểm chứng.** Sửa phân loại của CH09/P14 theo ba cột gốc, giữ ánh xạ ví dụ của từng cột.
3. **F01/F03** giữ chứng cứ `PASS_STATIC` từ vòng trước, không tái phân xử ngầm thành PASS semantic. Nếu dựng lại PDF cần tái chạy QA Unicode, ký hiệu, tính dễ đọc và 33 ảnh/hoặc hơn.
4. **473 trang chưa được chấm ngữ nghĩa.** Ma trận kỹ thuật 495 dòng là sơ đồ ưu tiên, không thay thế đọc đối chiếu đoạn/bảng/công thức/sơ đồ bởi rater đủ độc lập. Phải kiểm đủ 495 trang hoặc quy trình chấp nhận có tiền đăng ký và nhãn chính xác trước khi xin `PASS_FIDELITY`.
5. **Giữ quyền & provenance**: tài liệu nguồn là bên thứ ba; hồ sơ QA chỉ lưu nhận xét diễn giải và hash/trang neo, không sao chép lại toàn bộ nguyên tác.

## Phân xử cuối

`BYTE_CUSTODY_PASS · STRUCTURAL_QA_PASS · MANUAL_SCOPED_REVIEW_22_OF_495 · BLOCKERS_CONFIRMED_8 · PARTIAL_6 · SCOPED_MATCH_8 · UNREVIEWED_LANGUAGE_473 · FULL_LITERAL_TRANSLATION_FAIL_ADMISSION · HUMAN_INDEPENDENT_LINGUIST_NOT_EXECUTED · OWNER_HOLD_NO_PASS_FIDELITY · MAIN_UNCHANGED · LINEAGE_UNCHANGED · SCIENCE_NOT_EXECUTED`.

**Bước thực hiện tiếp theo — duy nhất:** `DIVE_INTO_LLMS_11PDF_VI_SOURCE_ANCHORED_CONTENT_REMEDIATION_AND_EXTERNAL_RATER_FULL_COVERAGE_ONEPACK` — một lượt sửa tất cả blocker, bảng/hình/đoạn còn rút gọn, kiểm toán độ đầy đủ toàn bộ 495 trang và QA ngôn ngữ độc lập; không chia micro-permit.
