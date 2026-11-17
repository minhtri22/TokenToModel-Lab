# TTM-Small-4M — Ma trận quyền nguồn và giới hạn công bố

**Ngày:** 2026-11-09 · **Loại:** kiểm toán tài liệu, không phải tư vấn pháp lý hoặc giấy phép phát hành.  
**Phân xử:** SOURCE_METADATA_VERIFIED_SCOPED · RELEASE_DATA_AND_WEIGHTS=HOLD_PENDING_OWNER_REVIEW.

## Nguồn đã xác minh

- [TinyStories upstream, pinned revision](https://huggingface.co/datasets/roneneldan/TinyStories/tree/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64): dataset card công bố giấy phép **CDLA-Sharing-1.0**, truyện ngắn tiếng Anh tổng hợp bằng GPT-3.5/GPT-4.
- [CDLA-Sharing-1.0, văn bản chính thức](https://cdla.dev/sharing-1-0/): khoản 1.9 định nghĩa Publish, khoản 1.11 định nghĩa Results (không gồm quá một phần dữ liệu nguồn tối thiểu), khoản 3.1–3.3 về công bố Data/Enhanced Data, attribution và thông báo sửa đổi; khoản 3.5 về Results; khoản 7.1 về luật áp dụng.
- [FAQ CDLA](https://cdla.dev/faq-resources/faq/) phân biệt Sharing với Permissive và nghĩa vụ khi công bố dữ liệu đã biến đổi.
- [Nguồn nội bộ T1](../pilot/TTM_T1_INDEPENDENT_QA_CLOSURE_AND_T3_COLAB_HANDOFF_20261108.md) ghi mã nguồn, bản ghim dữ liệu, SHA và giới hạn chống trùng. Mã nguồn TTM ở main không có tệp LICENSE khi rà soát cây Git ngày 2026-11-09.

**Diễn giải thận trọng:** giấy phép cho phép sử dụng dữ liệu theo điều khoản. Nếu phân phối Data/Enhanced Data thì áp dụng yêu cầu của mục 3. Results từ Computational Use có quy tắc khác, nhưng không tự động chứng minh mọi weight, tokenizer hay output đều được miễn nghĩa vụ; cần phân loại từng hiện vật và mức độ có thể chứa/tái tạo data nguồn. Public GitHub không tự động cấp quyền nhân bản/tái phân phối source code.

## Ma trận kiểm soát hiện vật

| Hiện vật | Quyền/nguồn | Hiện được phép đưa lên GitHub public? | Điều kiện mở |
|---|---|---|---|
| Raw TinyStories TRAIN/VALID | CDLA-Sharing-1.0 upstream | **Không** theo chính sách TTM | Xác minh attribution, notice, quyền republish, privacy |
| Các truyện TRAIN/VAL/TEST TTM được chọn | Derived Data từ TinyStories | **HOLD** | Phân loại Data/Enhanced Data; danh mục thay đổi, kiểm tra PII/copyright |
| Token pack TRAIN/VAL NPZ | Derived Data, chứa văn bản đã mã hóa | **HOLD** | Không lộ story IDs hoặc TEST; kiểm rights/PII |
| BPE2048 merge table thực tế | TRAIN-derived learned artifact | **HOLD binary**; chỉ công bố mô tả và SHA | Đánh giá khả năng tiết lộ chuỗi nguồn và quyền phát hành |
| Checkpoint PyTorch bước 1024/1280 | Trọng số TTM tự train từ đầu, không dùng pretrained checkpoint | **HOLD** | Owner chọn license cho weights, làm kiểm toán ghi nhớ/privacy và Results-vs-Data |
| GGUF F32 từ bước 1024 | Trọng số và tokenizer đã chuyển đổi | **HOLD** | Quyền weight/BPE, notices phụ thuộc, bảo toàn FAIL strict parity 7/8 |
| Mã nguồn TTM | Repository public, chưa có LICENSE ở main | Chỉ đọc theo khả năng truy cập; **không tự cấp quyền redistrib** | Owner chọn license và kiểm đóng góp/third-party notices |
| PyTorch, NumPy, regex, llama.cpp, Ollama | Các dự án bên thứ ba, license riêng | Chỉ link/ghi version; **không bundle binary** | Kiểm SBOM + license/notice theo bản đóng gói |
| Model card, dataset card, QA, SHA, số liệu tổng hợp | Báo cáo do TTM tạo | **Có, trong phạm vi đã rà soát** | Không chèn nội dung raw/private hay claim vượt bằng chứng |
| Đoạn văn bản sinh | Có thể trùng hoặc hồi tưởng đoạn dữ liệu | **Có điều kiện**, không tự phát hành hàng loạt | Similarity/PII review từng mẫu |
| Khóa giải mù AES, mapping A/B, thông tin cá nhân reviewer | Bí mật vận hành | **KHÔNG** | Chỉ escrow mã hóa và hash, giải mù sau freeze |

Các trạng thái **HOLD** là quyết định quản trị hiện tại, không phải kết luận pháp luật rằng tất cả những hiện vật trên đều bị CDLA cấm công bố.

## Các kiểm tra bắt buộc trước release

**R1 — Chain of title:** xác minh nguồn TinyStories và revision, các quyền và thông báo gắn với raw files, điều khoản nhà cung cấp phù hợp. Việc truyện do AI tạo không tự giải quyết bản quyền.

**R2 — CDLA 3.x:** nếu công bố Data/Enhanced Data, phát hành theo đúng CDLA-Sharing-1.0, bảo toàn attribution, thông báo file sửa đổi, giữ nội dung giấy phép/đường dẫn, không áp đặt các hạn chế phát hành lại trái giấy phép.

**R3 — Results classification:** đánh giá trọng số, merges, GGUF, text generation từng loại; xét khả năng tái tạo hơn mức de minimis dữ liệu nguồn và ràng buộc pháp lý liên quan.

**R4 — PII/copyright/memorization:** lập kế hoạch kiểm chứng được phép mà không tái sử dụng held-out TEST đã tiêu thụ; đánh giá chống tái tạo dữ liệu huấn luyện và khả năng tiết lộ thông tin nhạy cảm.

**R5 — Code & third-party:** chọn license cho TTM, kiểm quyền của contributions, ghi bảng version/license/notice cho third-party trong các gói phát hành (SBOM); model weights cần quyết định license riêng.

**R6 — Reproducibility:** SHA chỉ khẳng định byte-exact khi bytes đã được kiểm; chứng minh nguồn/seed/split/scheduler/RNG/READY checkpoint mà không công khai secret data.

**R7 — Scientific claims:** H1 VAL PASS-scoped, TEST 64 descriptive one-shot, step1280 exploratory NLL, semantic adherence chưa xác nhận, T5 Ollama compatible nhưng strict logits FAIL7/8 vẫn giữ nguyên.

**R8 — Owner signoff:** ký quyết định riêng cho Data, tokenizer, weights, GGUF, source code, examples. Không gộp các loại tài sản thành một phê duyệt mặc định.

## Attribution/notice mẫu (chưa có quyền release)

Original source: TinyStories, Ronen Eldan and Yuanzhi Li, https://huggingface.co/datasets/roneneldan/TinyStories , pinned revision f54c09fd... , license CDLA-Sharing-1.0: https://cdla.dev/sharing-1-0/. TTM pilot đã thực hiện subset selection, filtering và tokenization theo manifest. Nếu xuất bản Enhanced Data thì cần kèm giấy phép, attribution và dấu hiệu file thay đổi theo đúng nghĩa vụ.

Mẫu này chỉ là hướng dẫn chuẩn bị, **không tự cấp quyền**. Quyết định release sẽ được xem riêng sau khi R1–R8 có bằng chứng.

**Kết thúc:** RELEASE_DATA=HOLD · RELEASE_BPE=HOLD · RELEASE_WEIGHTS=HOLD · RELEASE_GGUF=HOLD · PUBLIC_REPORTS=SCOPED_ALLOWED · MAIN=UNCHANGED.

**Bước thực hiện tiếp theo:** reviewer quyền nguồn/chủ dự án phân xử một gói R1–R8, không động TEST hoặc rerun TRAIN.
