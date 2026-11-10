# TTM_SMALL_4M_EMBEDDINGGEMMA2 — OOD source, quyền dữ liệu, tokenizer và hợp đồng thiết kế tiền đăng ký

**Ngày:** 2026-11-11  
**Operation:** `TTM_GEMMA2_OOD_CORPUS_SOURCE_RIGHTS_TOKENIZER_FEASIBILITY_AND_PREREG_DESIGN_ONLY`  
**Trạng thái:** `SOURCE_CANDIDATE_SELECTED_CONDITIONALLY` · `RIGHTS_DOCUMENTED_WITH_OBLIGATIONS` · `TOKENIZER_STATIC_COMPATIBLE` · `REAL_CORPUS_AND_TOKENIZER_AUDIT_NOT_EXECUTED` · `OOD_ADMISSION=HOLD` · `NO_INFERENCE_NO_TRAINING_NO_CLAIM`.

## 1. Quy tắc nhánh, KHÔNG nhắm tới TTM main

Mô hình TTM-Small-4M × EmbeddingGemma 2 là **dòng thực nghiệm**; không phải checkpoint/cấu hình TTM gốc. Đích hội tụ mặc định là **dòng thực nghiệm tương ứng**, không phải `main` của TTM. Bản thiết kế OOD nằm trên nhánh con riêng `research/ttm-small4m-embeddinggemma2-ood-design-20261111` xuất phát trực tiếp từ mốc freeze `13820a972c99c2670e8ab32ee01eb51763479aae` của `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`. Giữ nguyên nhánh gốc làm bằng chứng L0020 và tránh merge/rebase/xóa.

Nhánh pilot chung `research/ttm-small-4m-colab-pilot-prereg-20261108` **cũng đã phân kỳ**, không thể giả định là một đích fast-forward an toàn. Mọi đề xuất hội tụ mã sau này phải kiểm toán chính xác lineage của checkpoint + code; không tự chuyển các 12-arm science artifacts vào `main`. L0020 `PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE` bất biến.

## 2. Một nguồn OOD chính — dự kiến, chưa admit

- **Corpus:** Salesforce **WikiText-2 raw** (`Salesforce/wikitext`), config `wikitext-2-raw-v1`, **split `train` chỉ làm nguồn để dựng OOD_EVAL**, tuyệt đối **không huấn luyện** checkpoint trên split này. Đây là văn bản Wikipedia kiểu bách khoa tiếng Anh, khác họ TinyStories. Tên split `train` là tên trong bộ dữ liệu gốc, **không** có nghĩa được dùng cho TRAIN của TTM.
- **Pinned dataset revision:** `6231e49f19a707241d6b84d9cff60a3a86b85a85`.
- **Đường dẫn duy nhất:** `wikitext-2-raw-v1/train-00000-of-00001.parquet`; **SHA-256 được trang host công bố (chưa tự băm lại):** `49280f3dd993cbdfd322186194133d5d1935f81e1c91064c239f2a70ebb02701`. Reject byte mismatch; không ngầm thay bằng `main`, `wikitext-2-v1`, test hay validation.
- **Nguồn:** https://huggingface.co/datasets/Salesforce/wikitext/blob/6231e49f19a707241d6b84d9cff60a3a86b85a85/wikitext-2-raw-v1/train-00000-of-00001.parquet ; https://huggingface.co/datasets/Salesforce/wikitext ; bài giới thiệu https://www.salesforce.com/blog/the-wikitext-long-term-dependency-language-modeling-dataset/
- **Quy mô công bố:** WikiText-2 train khoảng 600 bài Wikipedia, file được thể hiện theo nhiều hàng văn bản; HF card ghi 36.718 hàng cho split train. **Hàng không phải đơn vị độc lập**; phải tái dựng bài viết trước khi bootstrap.
- **Quyền:** thẻ HF khai báo `cc-by-sa-3.0` và `gfdl`. Có thể nghiên cứu trên văn bản theo điều kiện giấy phép, nhưng **phải ghi công, dẫn giấy phép và xem xét nghĩa vụ ShareAlike/GFDL nếu phân phối** dữ liệu hoặc bản phái sinh. Không công bố toàn văn, token windows, private membership trên GitHub; ghi nguồn trong báo cáo. Giấy phép công bố không bảo đảm sạch PII, quyền bên thứ ba hoặc không có overlap tiền huấn luyện của donor.
- **Vì sao không chọn nguồn khác lần này:** ưu tiên một corpus có version, phép đo next-token thông dụng và giấy phép công bố rõ hơn các tập news scraped/abstract có quyền hỗn hợp. **Không được đổi corpus sau khi xem bất kỳ OOD NLL nào.**

## 3. Phần tương thích tokenizer phải xác minh thật

**Căn cứ nguồn TTM được kiểm:** tokenizer T1 `tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py` Git blob SHA-1 `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`; tokenizer là GPT-2 regex byte-level BPE, 2.048 ID, EOS=256, 1.791 merges, context=256. BPE thực học từ TinyStories TRAIN và private manifest T1 SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. **Không fit lại** trên WikiText; không lấy tokenizer EmbeddingGemma donor để chấm model TTM.

Hệ byte-level hỗ trợ mã hóa UTF-8 hợp lệ, không có OOV theo kiểu từ điển thông thường; **không suy ra tokenizer ngoài miền hiệu quả**. Kiểm CPU trước inference:
1. Tải đúng một parquet vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` hoặc thư mục Colab/Drive dự án, đọc SHA-256 thực và kiểm số hàng/schema; ghi receipt **không kèm toàn văn**.
2. Nạp đúng T1 private BPE manifest bằng `BPE2048.from_manifest`, kiểm cả SHA file và manifest nội tại. Tất cả corpus text phải UTF-8; mã hóa BPE `encode` và `decode` round-trip trên mọi tài liệu dự kiến; không thêm token hoặc fit tokenizer.
3. Tính tỷ lệ subword/token trên whitespace-word, phân phối token/doc, tỷ lệ ký tự không phải ASCII, các ký hiệu WikiText như `@-@`, và tỷ lệ trang đủ 513 token. Hard feasibility: **ít nhất 256 tài liệu hợp lệ**; median `len(BPE(text))/max(1,len(text.split()))` trên 256 tài liệu **không vượt 4.0**; không có lỗi UTF-8, invalid token ID hoặc round-trip.
4. SHA exact đối chiếu với các tập TRAIN/VAL/TEST/H320/H512/H768 của TTM bằng **membership hash private**; near-duplicate 5-word lowercase Jaccard `>=0.85` nội bộ OOD và so với TRAIN2048 + VAL256 khi có quyền đọc nguồn. Không giải mã TEST/H320/H512/H768 lịch sử để điều chỉnh nguồn. Donor pretraining overlap không thể chứng minh bằng các bước này: báo cáo là `UNKNOWN`, không tuyên bố không nhiễm bẩn.
5. Thiếu dữ liệu lịch sử cần kiểm, thiếu file/các SHA, độ phân mảnh không đạt, số tài liệu thiếu hoặc parsing không nhất quán → **HOLD**. Không re-rank/reselect theo NLL.

## 4. Quy tắc tạo tập OOD_EVAL đề xuất phải được khóa trước khi chấm

**Đơn vị:** bài Wikipedia, không phải hàng parquet. Nối các dòng nội dung theo thứ tự nguồn và dấu xuống dòng LF; nhận ranh giới bài bằng heading cấp trên `= TITLE =`, bỏ heading dạng markup ra khỏi `text_for_model` nhưng giữ nguyên phần văn bản khác (không sửa `@-@` hoặc punctuation). Parser cần có fixture kiểm tra section headers và các trường hợp heading lỗi; nếu cấu trúc không khớp → HOLD, **không tự vá sau khi xem kết quả**.

**Kích thước:** 256 bài, mỗi bài **chỉ chấm 512 nhãn next-token** đầu tiên dưới tokenizer T1: dùng đúng 513 input token ID ban đầu, gồm hai cửa sổ 256 vị trí, với nhãn dịch 1; **không thêm EOS giả** tại vị trí cắt 512 token. Loại bài có dưới 513 BPE token trước ranking. Tổng nhãn dự kiến `256 × 512 = 131072`, đúng cùng budget cho 12 arms. Không dùng NLL để chọn độ dài; số nhãn OOD khác H768 là **khác thiết kế miền**, không so trực tiếp absolute NLL hai miền.

**Chọn xác định:** document digest `h=SHA256(UTF8(text_for_model))`; rank `SHA256(ASCII("TTM_GEMMA2_OOD_WIKITEXT2_RAW_DOCS_V1_20261111") || NUL || lowercase_hex(h))` tăng dần, tie-break bằng `h`. Chọn 256 từ tập thỏa điều kiện pháp lý/UTF-8/BPE/chiều dài **trước inference**. Không thay thế tài liệu sau seal. Nếu bất kỳ cặp selected documents nào trùng exact hay Jaccard 5-word >=0.85, HOLD thay vì chọn tài liệu khác. Private membership chứa `h`, số token, quy tắc cắt, ordinal. Công khai chỉ `SHA256(private_manifest)`, source SHA, số lượng và tổng nhãn. Không xem NLL trước seal.

## 5. Hợp đồng khoa học dự kiến — chưa phải đăng ký thực thi

**12 checkpoint:** 3 training seed cố định S1/S2/S3 × `PT-REAL`, `PT-PERM`, `NULL-REAL`, `NULL-PERM`, step 2048; dùng SHA-256 của checkpoint cuối từ L0020 adjudication/independent readback trên Google Drive (12 SHA phải kiểm ở preflight). **Không huấn luyện lại, không chọn checkpoint theo OOD.**

Gọi `L(a,s)` là tổng next-token NLL trên **chính 256 bài và 131.072 nhãn** của arm `a`, seed `s`, chia tổng nhãn. Giữ định nghĩa gốc:
- `delta_PRE,s = L(PT-PERM,s) - L(PT-REAL,s)`
- `delta_NULL,s = L(NULL-PERM,s) - L(NULL-REAL,s)`
- `tau_residual,s = delta_PRE,s - delta_NULL,s` (co-primary 1)
- `gamma_real,s = L(NULL-REAL,s) - L(PT-REAL,s)` (co-primary 2).

Paired **document** bootstrap cùng index cho cả 12 arms, 2.000 draws, seed mới `2026111198`, 95% percentile CI của mean contrast qua ba training seed cố định. **PASS_SCOPED_OOD_RESIDUAL_TRANSPORT** chỉ khi 12/12 SHA+READY, source/legal/BPE/admission, independent scorer QA đều PASS; 3/3 seed có `tau>0` và `gamma>0`; và cận dưới CI95 của mean cả hai contrast >0. Nếu dữ liệu/scoring hợp lệ nhưng không đạt cả hai co-primary → `OOD_SIGNAL_NOT_ESTABLISHED_SCOPED_FAIL`. Không đủ source/QA/resource → `HOLD` (không tạo science FAIL). CI điều kiện trên ba seed, không suy rộng seed-quần-thể; nhiều bài cùng Wikipedia và lịch sử tiền huấn luyện donor là giới hạn độc lập.

**Giới hạn nhân quả:** OOD dương chỉ cho biết donor residual structure có lợi trên miền văn bản khác; không tách thuần ngữ nghĩa pretraining, token-morphology, row norms hay phân phối số liệu. OOD âm không làm hồi tố L0020 thành FAIL. Không hiệu chỉnh theo NLL trước đây (S3 tau gần 0), không thêm seeds, không thử nhiều corpus hậu nghiệm.

## 6. Trình tự cổng và trạng thái

| Gate | Kết quả hiện tại |
|---|---|
| Dataset metadata, mô tả miền, license card | `PASS_DOCUMENTARY_ONLY` |
| Corpus revision và SHA host được nhận diện | `PASS_METADATA_PIN`, **chưa hash bytes** |
| Quyền nghiên cứu nội bộ | `CONDITIONAL_ATTRIBUTION_SHAREALIKE` |
| BPE2048 và context=256 trong source TTM | `PASS_STATIC_SOURCE` |
| SHA parquet thực, parser/article count | `NOT_EXECUTED` |
| T1 tokenizer manifest thật, round-trip, fragmentation | `NOT_EXECUTED` |
| Cross-source duplication, 256 documents seal | `NOT_EXECUTED` |
| Checkpoint readiness và scorer independent QA cho OOD | `NOT_EXECUTED` |
| OOD inference / GPU / training / CLAIM | `NOT_EXECUTED` |
| `lineage.md` L0017–L0020 | `PRESERVED`; **không thêm L0021** |
| `main`, merge, PR | `UNCHANGED` / `NONE` |

**Quyết định cuối:** `OOD_DESIGN_PRE_REGISTERED_CONDITIONALLY` · `SOURCE_ADMISSION=HOLD_PENDING_REAL_CPU_AUDIT` · `SCORING_NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_OOD_WIKITEXT2_PINNED_CORPUS_T1_BPE_CPU_FEASIBILITY_AND_PRIVATE_MEMBERSHIP_SEAL` — kiểm SHA dataset thật và BPE gốc, dựng/audit 256 bài trong dự án, sealed private manifest, integrated independent source QA, **không nạp mô hình, không inference, không GPU, không CLAIM**. Sau kết quả đó xin quyết định khoa học riêng trước khi chấm OOD.
