# TTM-Small-4M — Dataset Card: TinyStories pilot T1/T4 (subset, không phải upstream)

**Ngày:** 2026-11-09 · **Tập:** `TTM-TinyStories-Pilot-T1` · **Trạng thái:** `DERIVED_RESEARCH_SUBSET / NOT_PUBLISHED`.

> Card này mô tả **tập con do TTM chọn** từ TinyStories để huấn luyện mô hình gốc; không có nghĩa TTM tạo, sở hữu hoặc xuất bản lại toàn bộ dataset TinyStories. Không đưa raw text, danh tính truyện TEST hoặc token arrays lên GitHub.

## 1. Nguồn và xuất xứ

| Trường | Giá trị đã ghim |
|---|---|
| Upstream dataset | [roneneldan/TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories) |
| Revision | `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64` |
| File nguồn chính | `TinyStories-train.txt`, `TinyStories-valid.txt`; **không dùng V2 GPT4 train**, không dùng bản parquet chuyển đổi |
| SHA-256 TRAIN raw | `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f` |
| SHA-256 VALID raw | `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4` |
| Giấy phép khai báo | **CDLA-Sharing-1.0** (upstream metadata, không phải giấy phép độc lập do TTM cấp) |
| Ngôn ngữ / kiểu dữ liệu | Tiếng Anh, các truyện ngắn đơn giản, được tạo tổng hợp bằng GPT-3.5 và GPT-4 theo mô tả nguồn |
| Nghiên cứu gốc | [TinyStories, arXiv:2305.07759](https://arxiv.org/abs/2305.07759) |

Dữ liệu nguồn không phải là dữ liệu do user TTM tự quay/soạn; phải giữ attribution cho nhóm tác giả/nhà công bố TinyStories và metadata nguồn. Text nguồn khai báo `CDLA-Sharing-1.0` tại [upstream README](https://huggingface.co/datasets/roneneldan/TinyStories/blob/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64/README.md); tham khảo [license chính thức](https://cdla.dev/sharing-1-0/).

## 2. Quá trình xây tập con và nguy cơ trùng lặp

- Pipeline T1 quét nguồn TRAIN **2.119.489 truyện**; thấy **320.241 instances trùng hệt** trong TRAIN. VALID quét **21.990 truyện**, loại **6.601 collisions chính xác** so với toàn raw TRAIN.
- Sau loại trùng và chọn theo ưu tiên băm/seed trong giao thức T1, nhận **TRAIN 2.048** câu chuyện. Từ nguồn VALID còn hợp lệ, nhận **VAL 256 / TEST 64** câu chuyện, TEST có danh tính bị niêm phong.
- Kiểm tra chống trùng gần dùng Jaccard **5-gram ≥0,85** cho **bộ con đang sử dụng**; không có chứng cứ kiểm hết trùng gần giữa toàn bộ ~2M TRAIN và mọi truyện ngoài pilot.
- Tokenizer BPE huấn luyện **chỉ từ 768 truyện của TRAIN đã chọn**; vocab 2.048 IDs, bao gồm 256 byte IDs, EOS ID 256 và 1.791 merges. **Không fit tokenizer từ VAL/TEST**.
- Source/story parser dùng ranh giới truyện `<|endoftext|>`, tách cửa sổ tối đa 256 token; sau đó `x=tokens[:-1]`, `y=tokens[1:]`, padding label `-100` loại khỏi loss. **Không nối ngang hai câu chuyện**.
- Private pack T4 có **2.691 TRAIN windows/498.287 vị trí nhãn** và **328 VAL windows/61.122 nhãn**; **không chứa token TEST**. TEST 64 truyện chỉ được dùng trong một lượt kết thúc sau khoa học VAL, **không dùng để chọn mô hình hoặc tune**.

### Liên kết bằng chứng

- [T1 independent source/split/tokenizer QA](../pilot/TTM_T1_INDEPENDENT_QA_CLOSURE_AND_T3_COLAB_HANDOFF_20261108.md) (tại ngày 2026-11-08, đã có kết luận nguồn T1 thực).
- [T1/T2/T3 technical closure](../pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md).
- [Private TRAIN/VAL pack and counts](../pilot/TTM_T4_PRIVATE_PACK_PRODUCER_AND_CAPACITY_ADJUSTMENT_20261108.md).
- [T4 H1 formal science outcome](../pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md).
- [TEST one-shot report](../pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md).
- [T1 result JSON](../../evidence/pilot/t1-real/T1_RESULT.json).
- [T4 science decision JSON](../../evidence/pilot/t4-science/T4_A2_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION.json).

## 3. Cấu trúc và phân phối

| Thành phần | Lưu ở đâu | Công bố hiện tại |
|---|---|---|
| Raw TinyStories upstream TRAIN/VALID | Nguồn Hugging Face và cache riêng tư của chủ dự án | **Không sao chép/đóng gói lại** trên GitHub TTM |
| Pilot TRAIN 2.048 truyện | T1 manifest & dữ liệu lưu riêng | **Không công bố nội dung nguyên văn** |
| VAL 256 truyện | Private windows/manifest | **Không công bố nội dung nguyên văn** |
| TEST 64 truyện | Manifest niêm phong, one-shot đã tiêu thụ | **Không công bố IDs, câu chuyện hay nhãn** |
| BPE 768 TRAIN-only, merge bảng 1.791 | Private tokenizer/manifest | **HOLD bản merge**, chỉ công bố thông số + SHA |
| TRAIN/VAL `.npz` | Private Drive; SHA-256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913` | **Không công bố file** |
| Split manifest | Có dấu SHA-256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9` | Chỉ publish metadata không tiết lộ danh tính TEST |
| Kết quả QA, số lượng, băm, model metrics | GitHub TTM | **Có thể công bố theo phạm vi source card** |

Không khẳng định mọi câu chuyện sạch PII, không có bản quyền khác, không có nội dung nhạy cảm, hoặc dataset hoàn toàn không thiên lệch: hiện **chưa có** kiểm toán PII/content toàn diện từng truyện và xác nhận độc lập quyền của các nội dung do AI tạo ra.

## 4. Mục đích, chất lượng và hạn chế

**Dự kiến:** bài toán next-token language modeling, kiểm tra tokenizer TRAIN-only, huấn luyện từ đầu với ngân sách nhỏ, nghiên cứu checkpoint/resume/NLL. Chỉ phục vụ đánh giá **trong pilot subset**.

**Không dự kiến:** bộ kiểm thử ngôn ngữ tự nhiên rộng, instruction following, đối thoại, kiến thức khoa học, nội dung đa ngôn ngữ, tư vấn cho trẻ em hoặc ứng dụng sản xuất. Không dùng tập con này làm bằng chứng độ an toàn của mô hình.

**Rủi ro:** văn phong và nhân vật thường lặp, vốn từ hạn chế; nguồn synthetic không bảo đảm phản ánh người thật; split chống trùng gần chỉ trên active subsets; dự đoán token bị ảnh hưởng bởi EOS và dấu cách cuối prompt; repeated target exposure ~8,417× ở step1024 và ~10,52× ở step1280 có thể làm tăng nguy cơ ghi nhớ. Không thể dùng TEST đã tiêu thụ để chọn phương pháp xử lý mới.

## 5. Điều kiện cấp phép và công bố lại

Giấy phép upstream khai báo **CDLA-Sharing-1.0**, trong đó dữ liệu được nhận hoặc dữ liệu đã tăng cường/chỉnh sửa nếu **Publish** sẽ có điều kiện chia sẻ cùng giấy phép, giữ thông báo sửa đổi và attribution phù hợp; xem Điều 3 tại [CDLA](https://cdla.dev/sharing-1-0/). Điều 3.5 phân biệt **Results** từ Computational Use, nhưng không tự động xác định trạng thái pháp lý của mọi tệp tokenizer/weights sinh ra: cần đánh giá từng hiện vật, mức độ chứa/truy xuất lại data nguồn và quyền cụ thể.

**Quyết định hiện hành:** `DATA_PUBLICATION=HOLD`; không đưa corpus, pack, split IDs hay BPE merge bảng lên repo công khai. Điều này là **quyết định quản trị thận trọng**, không phải tuyên bố CDLA cấm tuyệt đối việc phân phối những hiện vật đó. Trước phát hành cần chủ sở hữu xác minh nghĩa vụ CDLA, attribution, notice khi sửa đổi, privacy/safety, license của mã và bên thứ ba.

## 6. Tái lập có trách nhiệm

[Manifest tái lập](../reproducibility/TTM_SMALL4M_T4_REPRODUCIBILITY_MANIFEST_20261109.md) ghi đúng commit, SHA, môi trường và giới hạn nguồn. Người tái lập phải tự lấy nguồn hợp pháp theo giấy phép, xác minh SHA, tái dựng split theo hợp đồng đã ghim và không mở lại TEST pilot đã tiêu thụ. Không có lời hứa rằng một người khác có thể khôi phục bộ dữ liệu gốc chỉ bằng file GitHub public nếu chưa có các tệp và hạt giống kín thích hợp.

**Trạng thái:** `DATASET_CARD=SOURCE_GROUNDED` · `PII_REVIEW=INCOMPLETE` · `REPUBLICATION=HOLD` · `TEST=SEALED_CONSUMED`.

**Bước thực hiện tiếp theo:** xác minh quyền xuất bản dữ liệu dẫn xuất, nội dung nhạy cảm và nhãn giấy phép trước mọi công bố; không tải dữ liệu thô lên GitHub.
