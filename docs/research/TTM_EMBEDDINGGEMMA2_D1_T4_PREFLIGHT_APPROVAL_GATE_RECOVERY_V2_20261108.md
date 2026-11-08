# TTM EmbeddingGemma 2 — D1 T4 owner-approval gate recovery V2 (technical only)

**Ngày:** 2026-11-08  
**Mã sự cố:** `TTM_EMBEDDINGGEMMA2_D1_T4_PREFLIGHT_OWNER_GATE_PERMISSIONERROR`  
**Nhánh:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**Ngữ cảnh:** Chủ dự án đã chấp thuận đúng phạm vi một lượt tiền kiểm T4 (30 phút, tải mới tối đa 5 GiB, lưu mới 8 GiB, trả phí $0; TTM-Small T5 ưu tiên). Phiên Colab báo `PermissionError` tại dòng permission guard trước khi tải mô hình và tạo one-shot claim.

## Triệu chứng và nguyên nhân

Notebook phiên LOCKED ban đầu lưu `OWNER_APPROVAL=False`, `TTM_SMALL_RESOURCE_CLEARED=False`, `SQUAD_DATA_RIGHTS_ACCEPTED_FOR_COLAB=False`, `DRIVE_RECEIPT_ROOT=None`. Permission guard yêu cầu bốn trạng thái phải đúng; do chưa cập nhật sau chấp thuận, Python raise `PermissionError`.

**Tình trạng chứng cứ:** Theo thứ tự mã nguồn notebook, permission guard nằm **trước** thao tác tạo `CLAIM.json` và bất kỳ download/model load. Với stack trace chính xác này, *lần chạy bị lỗi đó* chưa tiêu thụ one-shot. Tuy nhiên phải kiểm Drive không có CLAIM/RESULT cùng RUN_ID từ lần chạy khác trước tiếp tục; không được giả định tuyệt đối Drive rỗng.

## Bản sửa dành cho Colab — attachment V2

**Tên bản xuất cho người dùng:** `TTM_EmbeddingGemma2_D1_T4_OneShot_Preflight_OWNER_APPROVED_SETUP_V2.ipynb`.  
**SHA-256 của notebook V2 (26–27KB):** `6a8d62dbac62a54bf5cfe38d630f1da1e2eb12fdaa18e2b2a9216041287344df`.  
**SHA-256 notebook LOCKED nguyên bản:** `4baf188c42a5fc07524c344622791205a3ab41221070b7d2b64da300738f5dd2`.

Bản V2 là **artifact đính kèm trong chat**, không phải tệp ipynb được commit vào repo ở bước này. Chỉ ghi receipt và pin SHA vào GitHub; muốn lưu notebook cùng GitHub cần cung cấp bytes artifact trên đúng nguồn đã xác minh, không viết nội dung khác giả làm notebook.

### Thay đổi V2 so với bản cũ

1. `OWNER_APPROVAL=True` và `SQUAD_DATA_RIGHTS_ACCEPTED_FOR_COLAB=True` đúng với chấp thuận trong chat (chỉ SQuAD validation, không phân phối dữ liệu).
2. `TTM_SMALL_RESOURCE_CLEARED=False` mặc định và chỉ được đặt True khi **người dùng xác nhận runtime không xung đột TTM-Small T5** bằng cách nhập `TTM_SMALL_CLEAR`; không tự suy tình trạng Colab từ GitHub.
3. `DRIVE_RECEIPT_ROOT=/content/drive/MyDrive/TTM_EmbeddingGemma2_D1_Preflight`; ô SETUP mount Drive, tạo namespace riêng và kiểm không tồn tại CLAIM/RESULT.
4. Ô SETUP kiểm thiếu thư viện trước khi tạo CLAIM; lỗi về quyền, Drive, thư viện hoặc xung đột TTM-Small dừng **chưa tiêu thụ** lượt khoa học/kỹ thuật one-shot.
5. Cổng one-shot trong ô chính vẫn tạo `CLAIM.json` bằng exclusive create và không chạy lại `RUN_ID=ttm_embedgemma2_d1_t4_preflight_once_v1` khi đã CLAIM. Giới hạn 30 phút, 5 GiB tải, 8 GiB lưu giữ nguyên; không sửa exact model SHA/dataset SHA, không R_gold/R1–R3/TEST hoặc Adapter.

### Kiểm tra tĩnh

- Notebook JSON parse: `PASS`.
- Tất cả code cells Python AST: `PASS`.
- Mọi `execution_count=None`, `outputs=[]`: `PASS`.
- `RUN_ID`, `CLAIM`, budgets và các nguồn model/dataset pinned: `PRESERVED`.
- Chưa chạy setup, Colab, CUDA, model load, weights, SQuAD, Qwen, G1–G4 science: `NOT_EXECUTED`.

## Cách vận hành có hiệu lực

Trên Colab chính chủ (không dùng notebook chạy ở sandbox hoặc GPU khác), mở notebook V2 và chọn Tesla T4 nếu có. Chạy cấu hình, rồi ô SETUP; **chỉ nhập `TTM_SMALL_CLEAR` sau khi đã xác minh không ảnh hưởng TTM-Small**. SETUP kiểm Drive, CLAIM/RESULT và thư viện. Khi in `TTM_T4_SETUP_READY_NO_CLAIM=PASS`, được chạy ô one-shot **một lần**; mọi lỗi sau CLAIM phải có receipt và không được tự tạo RUN_ID khác/chạy lại. Đọc RESULT trên Drive và thực hiện independent QA trước quyết định D1 khoa học riêng.

**Không chạy ở bước recovery này.** Nếu CLAIM đã tồn tại từ bất kỳ lần chạy nào, STOP và đọc receipt; không ghi đè, không xóa.

**Bước tiếp theo:** User chạy V2 setup + one-shot trong Colab Free T4 sau kiểm tra tài nguyên; cung cấp log/RESULT. Independent QA receipt => `TECHNICAL_PREFLIGHT_PASS` hoặc `FAIL/BLOCK`, không tự mở D1. TTM-Small T5 ưu tiên.
