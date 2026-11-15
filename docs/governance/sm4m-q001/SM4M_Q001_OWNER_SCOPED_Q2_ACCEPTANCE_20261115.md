# SM4M-Q001 — Quyết định owner chấp nhận phạm vi Q2 để chuyển Q3 độc lập

**Question:** `SM4M-Q001`  
**Owner decision date:** 2026-11-15  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Policy baseline:** `main` commit `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`, `TTM-GOV-QF-20261115-V1`.  
**Owner statement:** “Tôi chấp nhận **phạm vi bằng chứng và điều kiện admission** cho independent Q3.”  
**Decision:** `ACCEPT_Q2_EVIDENCE_SCOPE_AND_ADMISSION_CRITERIA_FOR_DISTINCT_Q3_REVIEW_ONLY`.

## A. Chính xác điều được chấp nhận

1. Chấp nhận **phạm vi được phép dùng làm bằng chứng Q3**: kiến trúc Small-4M thật, T4 step1024, kết quả liên quan trực tiếp T4 VAL/TEST, FRESH12, FRESH16, CF1 DEV36, D1 EXP32, A/C FINAL24, H-DATA-S1, FC01 và D1 R1, cùng văn liệu khoa học làm **cơ sở giả thuyết**. Các chương trình EmbeddingGemma 2 và Vector Memory **nằm ngoài phạm vi**.
2. Chấp nhận **bộ tiêu chí admission AD-00 đến AD-08** làm điều kiện kiểm tra bằng chứng/thiết kế, có hard veto rõ. Chấp nhận **tiêu chí** KHÔNG đồng nghĩa **từng điều kiện đã được đáp ứng**: AD-00 mới partial public source; AD-01…AD-08 chưa xác minh/chưa thực thi/chưa được cấp phép như các giá trị gốc trong ma trận immutable.
3. Chấp nhận gói **tự QA tác giả (author QA)**: source 38/38, literature 64/64 và Q2 causal 59/59 **trong phạm vi tương ứng**; đây không là independent Q3 PASS hoặc khoa học PASS.
4. Cho phép reviewer **khác với tác giả Q2** đọc lại từ source gốc và phản biện các phân loại, các dự đoán có thể bác bỏ, tính đầy đủ của admission/veto, độ chính xác số liệu và khả năng lựa chọn phép thử tối thiểu.
5. Những gì bản source Q2 ghi là `Q3_NOT_EXECUTED` hay `PENDING_ACCEPTANCE` **đúng tại thời điểm bản nguồn được tạo**; không sửa byte hay tái viết lịch sử. Quyết định này là sự kiện owner đến sau.

## B. Không được ngầm chấp nhận

- **KHÔNG** chấp nhận `ROOT_CAUSE_IDENTIFIED`, `KEEP_BASELINE_FOR_NEW_SCIENCE`, `ADMISSION_PASS`, hoặc `SCIENCE_GO`.
- **KHÔNG** cấp phép tạo/đọc lại private checkpoint/data/gold/token IDs, giải mù, chấm điểm mới, model inference, GPU, training, TEST/FINAL replay.
- **KHÔNG** xác nhận rằng 13 bài báo chứng minh cơ chế nhân quả trên checkpoint TTM; đó chỉ là triage.
- **KHÔNG** cấp phép sửa source, architecture, rubric, F0–F2, mở thêm nhánh nghiên cứu, hoặc merge implementation đang HOLD/FAIL.
- **KHÔNG** sửa `lineage.md`: chỉ nhận khoa học PASS/FAIL đã phân xử, không nhận Q2 owner acceptance hoặc design QA.

## C. Gói tác giả đã khóa: exact Git blobs và SHA-256

Dùng nguyên byte bảy tệp, **không tóm tắt thành source thay thế**:

| Repo path | Git blob SHA-1 | Raw SHA-256 |
|---|---|---|
| `docs/governance/sm4m-q001/SM4M_Q001_INTEGRATED_ARCHITECTURE_AUDIT_20261115.md` | `b289f1056a9c0bb862a4813cbf0d2189b34c233d` | `4973ad744f5d2e2e9e89f46e7890a37833c43cd99fdb82405be2148a580bce06` |
| `artifacts/governance/sm4m-q001/SM4M_Q001_AUDIT_RECEIPT_20261115.json` | `74023311e224e552c46899a7547eb5f73deddc52` | `9fbfb2b185043685b5d24e352eb7b029b6fc36098f5a735cd699b9b5f2261f4a` |
| `docs/governance/sm4m-q001/SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_LITERATURE_TRIAGE_20261115.md` | `380582a4f1260dfda28d39e0cb56be2fc02709c5` | `34c553d10250b8403a4d2e7170ce6f0329fa14284ea5018f59de35af94622d36` |
| `artifacts/governance/sm4m-q001/SM4M_Q001_AUTHOR_ADVERSARIAL_LITERATURE_QA_RECEIPT_20261115.json` | `c984ca474c112494bfe472d4293c2da7e4a6eefb` | `5254fbb557c2074d95d7aa65e14e6c2924e8da1979e12f6fe4b1340958303a65` |
| `docs/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_ADMISSION_LOCK_20261115.md` | `d82202778fe3bc620335af18b0fa7ea1fec4094c` | `b34ad81e81e90ba5873cb1c8207592f8b078023aba60f2e57cd7ef1229376a8e` |
| `artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json` | `b7e87dbdd31c6624387f9943d7ff7db8efa8663a` | `306d32086fa1e19a910070577e0f9fbd7d0a130d792ff225e1f35768237a105b` |
| `artifacts/governance/sm4m-q001/SM4M_Q001_Q2_AUTHOR_ADVERSARIAL_QA_RECEIPT_20261115.json` | `a3a22b0cc8515979c9034d02e497ecf8f7b1fee4` | `ed0bc795c3d129cdf4c99761f96cb04888a0c9cebfb83010c0463c712be4e403` |

Bản chính thức của gói Q2 là **các byte đã pin trong bảng**, đọc bằng exact candidate commit/PR ref sau khi commit. `main` chưa tự động có các file này khi còn PR.

## D. Cổng Q3 và kết quả cho phép

Q3 reviewer độc lập phải đọc source và phản biện **có kết luận**: `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` hoặc `HOLD_Q3_REMEDIATION`. Khi HOLD, nêu finding, mức độ, exact source & amendment duy nhất, không tạo micro-permit.

Q3 PASS chỉ xác nhận tính đúng của **bản phân tích và điều kiện admission**, KHÔNG xác nhận bản thân admission đã PASS hoặc bản vá đã cần. Sau Q3, chỉ owner Q4 được đóng câu hỏi và quyết định sau này có đặt ra Q mới hay không.

**Status at owner acceptance:** `OWNER_Q2_SCOPE_ACCEPTED · Q3_AUTHORIZED_REVIEW_ONLY_NOT_EXECUTED · Q4_NOT_DECIDED · F0_F2_PAUSED · SCIENCE_HOLD · NO_NEW_RESEARCH_BRANCH · LINEAGE_UNCHANGED`.
