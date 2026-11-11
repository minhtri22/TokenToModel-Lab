# TTM-Small-4M × EmbeddingGemma 2 — OOD256 WikiText-2: phán quyết khoa học độc lập

**Ngày:** 2026-11-11  
**Operation:** `TTM_GEMMA2_OOD_12ARM_ONE_SHOT_INDEPENDENT_SCIENTIFIC_ADJUDICATION`  
**StudyID gốc:** `ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2`  
**Nguồn đánh giá mới:** WikiText-2 raw pinned, 256 bài ngoài miền TinyStories, 512 cửa sổ, 131.072 next-token labels.  
**Kết luận theo tiền đăng ký:** **`PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`**. Không phải PASS suy luận nhân quả thuần về semantic pretraining, không áp dụng đại diện cho mọi OOD.

## 1. Nguồn bằng chứng độc lập, đã đọc byte thực

Colab one-shot do owner được phép thực hiện đã tạo `science_one_shot` trên Google Drive riêng tư:
- `CLAIM.json` SHA256 `19c92d525d45bd5f6c72db92e8a10c2520ab18b776df113f389faadda76f7238`;
- `RESULT.json` SHA256 `5faa962919dfd56980c2b826fb341b6d90780adb2369d9c03c05d4ca42c55f9c`;
- `PER_DOCUMENT_PRIVATE.json` SHA256 `f3b4a91109054b0c4cbc45afe3f8f90845caa6bc9b8f8c8dd304b70edc9d877e`;
- `INDEPENDENT_READBACK_PUBLIC.json` SHA256 `34f8174bcd835c5d3c130dff4f82dd0a9623ada24924fddf87b2d0561bdf03f6`.

Cả bốn tệp đã được tải nguyên byte từ Drive kết nối và băm lại SHA-256 trong môi trường kiểm tra độc lập, khớp với `RESULT` và independent receipt. `RESULT.status=COMPLETED_PENDING_INDEPENDENT_ADJUDICATION` được **giữ nguyên** như biên bản science gốc; phán quyết cuối là tài liệu riêng, không sửa `RESULT` hậu nghiệm.

Có đủ **12/12** `START.json` và **12/12** `SCORE_PRIVATE.json` trên Drive. QA độc lập của notebook đã kiểm 12 receipt; lượt kiểm tra này tải riêng nguyên byte **12/12 receipt SCORE_PRIVATE** và xác minh bằng một triển khai tính toán độc lập: seed/arm, SHA-256 checkpoint trong CLAIM, SHA CLAIM, OOD membership, từng vector loss 256 phần tử khớp byte với `PER_DOCUMENT_PRIVATE.json`, SHA-256 của vector double little-endian, và NLL của cả 12 arm. **12/12 PASS**, không sai lệch. Không đọc hoặc công bố toàn văn WikiText, private membership, raw token windows hay loss theo bài trên GitHub.

Đã tải riêng từ thư mục `input_ood` trên cùng Drive và băm lại **3/3 file OOD**: public seal `0091b56b27c68f1bb724b63181097434d6c7c5922e5cc1de929423b5b0c45438`; private membership `627c99db8b39b6479fdb074a82b0ab7eea0367dde49bf0072c29ff410ecdcd5f`; private windows `3ec7655c512c5d13d4c0d04d1ddbae80b8ea0106aee82064e8dd806786d8336a`. Independent readback của NPZ: x/y shape (512,256), ID trong [0,2047], 2 cửa sổ/bài theo thứ tự, label shift trong và qua cửa sổ, counts=131.072: PASS.

12 SHA checkpoint trong `CLAIM` và `RESULT` khớp 12 SHA frozen L0020 từng key; checkpoint binary đã được băm lại 12/12 trong lượt preexec trước khi chấm, và runner ở Colab gọi preflight xác minh SHA mỗi checkpoint trước khi tạo science CLAIM. Không huấn luyện hoặc lựa chọn lại mô hình. `CLAIM` tiêu thụ một lần, không chạy lại inference trong lượt kiểm tra độc lập.

## 2. Hợp đồng khoa học đã khóa trước inference

Nguồn tiền đăng ký: `docs/pilot/TTM_GEMMA2_OOD_WIKITEXT2_SOURCE_RIGHTS_TOKENIZER_PREREG_DESIGN_20261111.md` (trước scoring), nhánh con từ freeze L0020. Dữ liệu pin: WikiText-2 raw `Salesforce/wikitext`, revision `6231e49f19a707241d6b84d9cff60a3a86b85a85`, parquet SHA `49280f3dd993cbdfd322186194133d5d1935f81e1c91064c239f2a70ebb02701`, BPE2048 T1 manifest SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.

Đúng 3 seed × 4 arm frozen tại **step 2048**, 512 nhãn/bài, 256 bài, không fit lại. Co-primary:
- `delta_PRE = NLL(PT-PERM) - NLL(PT-REAL)`;
- `delta_NULL = NLL(NULL-PERM) - NLL(NULL-REAL)`;
- `tau_residual = delta_PRE - delta_NULL`;
- `gamma_real = NLL(NULL-REAL) - NLL(PT-REAL)`.

Bootstrap ghép cặp theo **bài viết** với cùng chỉ số resample qua tất cả arms và 3 seed, `BOOTSTRAP_SEED=2026111198`, `BOOTSTRAP_DRAWS=2000`, CI percentile 95%, conditional on 3 fixed training seeds. Cổng PASS tiền đăng ký bắt buộc: 12 checkpoint/READY/source/scorer QA PASS, cả **3/3 seed có tau>0 và gamma>0**, đồng thời lower CI95 trên mean contrast >0 cho **cả hai**. Thất bại khoa học hợp lệ sẽ lưu FAIL, không chuyển thành lỗi QA.

**Lưu ý phân biệt nhãn:** `RESULT.candidate_verdict=PASS_SCOPED_OOD_RESIDUAL_SIGNAL` là nhãn nội bộ implementation. Hợp đồng tiền đăng ký gọi kết luận có cùng cổng `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`; biên bản này dùng **nhãn đã prereg**, không đổi ngưỡng hay chọn lại bài/arm sau khi thấy kết quả.

## 3. Kết quả khoa học

| Seed | PT-REAL NLL | PT-PERM NLL | NULL-REAL NLL | NULL-PERM NLL | τ residual | γ real |
|---|---:|---:|---:|---:|---:|---:|
| S1 | 6.7501817729 | 6.9621384340 | 6.7819574422 | 6.8972623815 | +0.0966517218 | +0.0317756693 |
| S2 | 6.6785347802 | 6.7884142972 | 6.7277494288 | 6.7695097419 | +0.0681192039 | +0.0492146486 |
| S3 | 6.7433443227 | 6.9087713730 | 6.8062944310 | 6.9314040454 | +0.0403174359 | +0.0629501083 |

| Co-primary | Mean delta NLL (nats/target) | CI95 paired-document | Seed dương | Cổng |
|---|---:|---|---|---|
| `tau_residual` | +0.06836278721978761 | [0.06235342572949934, 0.07423878749033531] | 3/3 | PASS |
| `gamma_real` | +0.0479801420718878 | [0.04355893220445865, 0.052225954797402115] | 3/3 | PASS |

Lượt QA Python hoàn toàn độc lập tải từ `PER_DOCUMENT_PRIVATE.json` (không dùng gọi model, không dùng scorer), tính lại 12 NLL, 12 delta/contrast, chỉ số bootstrap 2000×256 và hai khoảng tin cậy: **mọi chênh lệch số so với `RESULT` = 0 theo độ chính xác số lưu**. Cả hai lower CI95 >0 và cả 3/3 seed dương. Đây là **PASS khoa học có phạm vi theo pre-registered gate**.

## 4. Giới hạn và diễn giải

- Đây là evidence của **residual donor structure transfer/transport trên một miền OOD đã khóa**, không cô lập semantic pretraining hoặc chứng minh nhân quả thuần donor; có thể liên quan projected geometry, token morphology, row norms, moments cao và training dynamics.
- WikiText-2 raw source split `train` chỉ được dùng **OOD evaluation** cho TTM, không phải huấn luyện/checkpoint tuning. Phân mảnh BPE median 2.35545; BPE vẫn gốc T1.
- 256 bài cùng họ Wikipedia không đại diện mọi OOD. CI bootstrap theo bài **chỉ có điều kiện trên ba seed**; không tính bất định trên phân phối seed, miền dữ liệu, donor corpus hoặc các bài có phụ thuộc nội dung.
- Chống trùng gần đã kiểm TRAIN2048/VAL256 của TTM, không thể chứng minh vắng mọi duplicate từ tất cả TinyStories 2.1M; donor pretraining overlap **UNKNOWN**. Đó là giới hạn độc lập và contamination còn tồn tại.
- Kết quả OOD không chỉnh sửa kết luận L0020 (H768), không so trực tiếp absolute NLL qua hai miền khác nhau. Không mở GGUF, ứng dụng hay huấn luyện thêm. Nguồn CC BY-SA/GFDL giữ nghĩa vụ ghi công nếu phân phối phái sinh.

## 5. Phán quyết cuối

**`SCIENTIFIC_ADJUDICATION=PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`**.

**`INDEPENDENT_QA=PASS_12_OF_12_PRIVATE_SCORE_RECEIPTS`**; **`SHA_REAL_READBACK=PASS_CLAIM_RESULT_PRIVATE_AND_3_OOD`**; **`CO_PRIMARY=PASS_2_OF_2`**; **`SEED_SIGN=PASS_3_OF_3`**.

Science one-shot đã được tiêu thụ: `CLAIM=CONSUMED`, `OOD_SCORING=EXECUTED_12_OF_12`, `TRAINING=NOT_EXECUTED`. L0020 được bảo toàn; ghi kết quả này thành mục mới L0021 **chỉ trên nhánh OOD**, giữ bản khoa học gốc và `main` bất biến.

**Bước thực hiện tiếp theo:** Đóng hồ sơ OOD256, đóng băng CLAIM/RESULT/independent receipt và bảo toàn private Drive. Không chạy tiếp ngầm. Mọi nghiên cứu mở rộng sang OOD thứ hai hoặc cô lập semantic pretraining sẽ là hợp đồng khoa học mới, không hậu nghiệm điều chỉnh OOD256.
