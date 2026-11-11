# TTM-Small4M — FRESH16 integrated offline source, rubric and science-preexec review

**Ngày:** 2026-11-11. **Operation:** `TTM_SMALL4M_PROMPT_ADHERENCE_FRESH16_PREREG_SOURCE_AND_RUBRIC_INTEGRATED_OFFLINE_REVIEW`.

**Kết quả công khai:** `PASS_PUBLIC_16_OF_16_EXACT_AND_NGRAM_DEDUP`. **Nguồn riêng tư:** `HOLD_PENDING_NATIVE_BPE_AND_CHECKPOINT_SHA`. **Rubric/H1/H2:** nguồn đã được cố định trong tệp Git, nhưng chưa cấp khóa thực thi khoa học do cần chứng thực source và reviewer độc lập. Không chạy inference, không training, không TEST.

## 1. Bộ prompt và nguồn lịch sử

- 16 prompt được tạo trong commit `c6cff9aed62bb605809dcc8f4a5cd41891d14d90`, Git blob `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`, 8 cặp minimal-pair (entity, causal, constraint, goal, 2 cặp/nhóm).
- 28 prompt lịch sử công khai gồm Q1 16 từ Git blob `0a7cb5c2125b69b062d8e5559dbbe47cb07eb788` và FRESH12 12 từ Git blob `919c43f2c919fa733b20a9be5d6b965e9649339c`, đã snapshot (chỉ các chuỗi prompt đã công khai, không output, score, TEST, TRAIN, VAL) trong `artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json`.
- Kết quả so trùng chuẩn hóa: **0 exact duplicates**. Jaccard 3-gram lớn nhất **0.017543859649122806**, 5-gram lớn nhất **0**; không vượt ngưỡng cảnh báo 0.35. Kiểm tra không gian này **không xác nhận absence** trong toàn bộ dữ liệu huấn luyện hoặc TEST đã niêm phong.
- Toàn bộ 16 văn bản ASCII tiếng Anh và **không dấu cách/linebreak ở đầu/cuối**. Có một thao tác can thiệp fact và prefix/suffix giống hệt trong mỗi cặp; không sửa nguồn sau khi score.

## 2. Khóa nguồn và rubric

Tài liệu máy-đọc được ở `artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_FROZEN_RUBRIC_AND_PREREG_CANDIDATE_20261111.json`: quy tắc byte của prompt, BPE GPT-2 TRAIN-only real, checkpoint step1024/1280, ngưỡng H1 >=12/16 và H2 >=6/8 (ít nhất 1 cặp cho mỗi trong bốn nhóm), thang 0..3 và việc **không tính điểm khi chỉ lặp lại prompt**.

- Primary: `step1024`; secondary descriptive: `step1280`.
- Reviewer chỉ xem prompt gốc và continuation; không xem checkpoint, variant, pair ID hoặc model/source label trước khi khóa phiếu chấm SHA. Reviewer độc lập phải khác executor và được ghi nhận *trước inference*. **Chưa có chứng thực reviewer** nên `REVIEWER_CUSTODY=UNASSIGNED`. Reviewer AI không thay thế mặc nhiên reviewer con người.
- H2 không được PASS nếu hai đầu ra giống nhau kiểu generic hoặc chỉ nhớ một keyword; cần hành động đúng khác nhau theo dữ kiện.
- Kết luận `QUALITY_CANDIDATE_SCOPED_STEP1024_ONLY` chỉ đạt khi cả H1, H2 và source/custody PASS; nếu không đủ dữ liệu/source thì HOLD, nếu không đạt ngưỡng sau run thì NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED, không phải lỗi toàn bộ kiến trúc.
- Nếu reviewer là duy nhất 1 AI, nhãn chỉ được cấp `SINGLE_RATER_EXPLORATORY_ONLY` mà không tuyên bố human-independent validity.

## 3. Offline native preflight (không model forward)

Mã `tools/research/ttm_small4m_quality_gap/ttm_fresh16_integrated_offline_review.py` và 8 bài QA `tools/research/ttm_small4m_quality_gap/test_fresh16_integrated_offline_review.py` thực hiện một lượt:

1. Kiểm branch sạch, hash Git blobs, exact prompt set, historical exact + Jaccard 3/5-gram, rubric H1/H2 và nhóm A/B.
2. Chỉ đọc manifest `_tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json` SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; dùng **đúng mã T1** Git blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` để token hóa 16 prompt và decode roundtrip; từ chối prompt >=193 tokens hoặc EOS bất thường.
3. Nếu được cung cấp hai đường dẫn checkpoint **bên trong root TTM**, đọc và xác minh step1024 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` và step1280 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`. Nếu thiếu, HOLD, không giả định checkpoint tồn tại.
4. Ghi duy nhất receipt project-local `_tmp/ttm_fresh16_integrated_offline_review_20261111/INTEGRATED_OFFLINE_REVIEW_RECEIPT.json`; không xóa, không overwrite. Nếu thiếu reviewer, vẫn chỉ `PASS_SOURCE_BYTES_PREREG_FROZEN_REVIEWER_UNASSIGNED` chứ không cấp inference.
5. Không đọc TEST, không mở Ollama, không huấn luyện và không dùng lại Q1/FRESH12 outputs.

**PowerShell:** `tools/research/ttm_small4m_quality_gap/Invoke-TTM-Fresh16-Offline-Review-PS51.ps1` có tham số tùy chọn `-Checkpoint1024`, `-Checkpoint1280`, và Python312. Tài liệu nguồn đã commit là chuẩn science prereg candidate; tệp receipt riêng tư **chưa được thực thi/kiểm chứng trên Windows** do connector RemoteDesktop trả lỗi nội bộ. Không đổi ngưỡng dựa trên byte nguồn private.

## 4. Ngân sách và hành động

Một lượt CPU nếu có quyết định riêng về sau: step1024+1280, 16 prompt mỗi checkpoint, max 64 token/response, tổng tối đa 32 response/2048 new tokens, context256, greedy. Không cần GPU/Colab, không tự retry. **Chưa có permit cấp inference.**

**Bước thực hiện tiếp theo:** chạy một lượt `FRESH16_NATIVE_BPE_CHECKPOINT_READBACK_OFFLINE_QA` trên Windows sau khi cung cấp đúng hai file checkpoint project-local. Nếu receipt nguồn PASS và reviewer custody có tên xác thực, mới lập một quyết định duy nhất cho 32 đầu ra; không áp đặt thêm micro-permits.

## 5. Đọc lại byte hai checkpoint gốc từ Google Drive kết nối

Trong cùng lượt rà soát, đã đọc nguyên byte hai checkpoint khoa học nguyên bản và băm SHA-256 độc lập bằng Python, không tải nội dung mô hình lên GitHub:

| Checkpoint | Byte gốc | SHA-256 đối chiếu | Kết quả |
|---|---:|---|---|
| T4 step1024 | 45.074.891 | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | **PASS_RAW_BYTES_SHA256** |
| T4 original step1280 | 45.075.275 | `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` | **PASS_RAW_BYTES_SHA256** |

Biên bản: `artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_ORIGINAL_T4_DRIVE_CHECKPOINT_INDEPENDENT_SHA_REHASH_20261111.json`.

**Phân biệt phạm vi:** đây là kiểm tra byte của file gốc trên Drive; *chưa* kiểm tra bản checkpoint được đặt trên Windows trong workspace hiện tại. Đường dẫn step1024 Windows từng được xác minh là `_tmp/ttm_causal6_source_h512_stage_20261109/input/checkpoint.pt`; chưa có đường dẫn step1280 nội bộ được xác nhận, nên không tự giả định nó đã nằm trên Windows. BPE manifest TRAIN-only gốc `_tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json` vẫn phải được Python 3.12 đọc và kiểm bằng byte thực trên Windows. Sau khi có cả hai tệp checkpoint trong phạm vi TTM, chỉ chạy **một lượt offline QA tích hợp**; không chạy model.
