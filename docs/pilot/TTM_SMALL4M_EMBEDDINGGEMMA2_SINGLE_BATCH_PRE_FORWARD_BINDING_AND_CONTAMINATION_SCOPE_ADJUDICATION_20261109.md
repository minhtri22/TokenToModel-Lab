# TTM-Small-4M × EmbeddingGemma 2 — Một đợt khóa pre-forward và phân xử nhiễm dữ liệu

**Ngày:** 09/11/2026 · **Mã công việc:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SINGLE_BATCH_PRE_FORWARD_BINDING_AND_CONTAMINATION_SCOPE_ADJUDICATION`.

**Quyết định cuối:** `HOLD_CONFIRMATORY_CPU_ONE_SHOT_UNMET_HISTORICAL_VAL_TEST_NEAR_DUPLICATE_GATE`. Cổng triển khai kỹ thuật `PASS_IMPLEMENTED_SYNTHETIC_PRE_FORWARD_BINDING`; **không cấp quyền chấm 320 truyện trong lần này**. Đây là quyết định kỹ thuật/phương pháp, không phải kết quả khoa học mới.

## 1. Nền tảng đã khóa, không thay đổi

- Nhánh gốc: `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`, parent `fa34b28db3804e17eb255d7908476dd2c2f89581`.
- Manifest `MEMBERSHIP_PRIVATE.json` có SHA-256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`; **320 truyện**, **75.798 nhãn**. Readback độc lập Windows PASS đúng phạm vi; không có ID trùng với nhóm cũ, không có thành viên thuộc bucket TEST cũ.
- Nguồn gốc `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`; original TRAIN SHA `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`; original VALID SHA `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`; BPE file SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; original split SHA `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`.
- `PASS_ORIGINAL_RUNNER_CPU_SYNTHETIC_LOGIT_PARITY` 20/20 và `PASS_SCOPED_INTEGRATED_CPU_SYNTHETIC_QA` 118/118; hai cổng đã đóng. Không tự diễn giải thành chứng minh ngoại suy.

## 2. Lớp kiểm tra trước suy luận (pre-forward binding)

**Mã nguồn được khóa:** `tools/embeddinggemma2_swap/ttm_gemma2_single_batch_pre_forward_gate_20261109.py`, SHA-256 `c92f827f7b462d42c53302b157038f0110d735ac41c4e4c2690f47356559e584`.

Hàm `sealed_contract()` chỉ nhận manifest riêng tư có **SHA-256 toàn tệp chính xác** và biên bản công khai phù hợp; đối chiếu split lịch sử, nguồn, BPE, thứ tự 320 ID, số nhãn 75.798, quy tắc loại TEST bucket và cờ `science_executed=false`. Hàm `build_pinned_encoder()` từ chối tokenizer không đúng Git blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` hoặc manifest BPE không đúng SHA. **Không dùng bất kỳ hàm encode tùy ý nào đối với hợp đồng thực.**

Trước khi gọi bất kỳ `model.forward()` nào, `validate_complete_plan()` đối chiếu **cả 320** `Material` theo thứ tự: SHA-256 từng truyện gốc, token BPE, đếm nhãn từng truyện và toàn bộ 75.798, từng cửa sổ 256 token, EOS cuối, mặt nạ `-100`, ngữ cảnh tách riêng, x/y chính xác, không thể lặp/thiếu/thêm/đảo cửa sổ hay thay story ID. `forward_only_after_guard()` gọi callback chỉ sau khi toàn bộ plan đạt PASS. Đây là mô-đun triển khai để ghép vào runner khoa học ở **một lượt được cấp riêng về sau**; CLI của tệp chỉ có chế độ `fixture-qa`, không thể chạy đánh giá mới từ CLI này.

**Lượt chạy thật trên 320 truyện:** chưa đọc/trích xuất bản văn mới, chưa sinh cửa sổ thật hoặc forward; sau khi được phép chạy khoa học, runner phải tạo và kiểm tra toàn bộ plan trước forward đầu tiên và ghi CLAIM one-shot bất biến. Nếu kiểm tra thất bại, ghi `HOLD` mà không gọi mô hình hoặc thay danh sách.

### QA đã thực hiện — chỉ dữ liệu tổng hợp

| Bộ QA | Kết quả | Ghi chú |
|---|---:|---|
| `ttm_gemma2_single_batch_pre_forward_gate_20261109.py --mode fixture-qa` | **135/135 PASS** | Tập mô phỏng **320 truyện / 75.798 nhãn**, thử đảo ID, trùng cửa sổ, thay y, EOS, padding, thiếu nhãn; mọi input lỗi từ chối trước callback |
| `ttm_gemma2_single_batch_independent_boundary_qa_20261109.py` | **172/172 PASS** | Oracle cửa sổ T4 Git blob `cdce219f2a2df27e25579f069238d4327c1d7d91`, các biên 255/256/257/512/1025; kiểm chứng thứ tự validate rồi mới callback |

Source SHA bộ QA độc lập `f95360e71880be5a14de2a668193f9fdfc67e2c51ae562b9ee0ac684d5677ba1`. Không đọc một byte thực của tập 320 hoặc văn bản TEST, không load checkpoint, không GPU hoặc tính NLL khoa học.

## 3. Phân xử phương pháp chống trùng

| Câu hỏi | Trạng thái xác minh |
|---|---|
| Trùng ID với TRAIN/VAL/TEST cũ | PASS: 0 |
| Thuộc TEST bucket cũ | PASS: 0 |
| Gần trùng với toàn TRAIN nguyên bản | Bộ seal ghi quét **2.119.489**, loại 0; **không có lượt tái quét độc lập** |
| Gần trùng với 256 VALIDATION pilot cũ | **UNKNOWN**, không có chứng thư đủ |
| Gần trùng với 64 TEST pilot cũ | **UNKNOWN**, không có chứng thư đủ; **không mở nội dung TEST** |
| Trùng trong dữ liệu tiền huấn luyện EmbeddingGemma 2 | **UNKNOWN**, không thể suy ra từ các SHA trên |

**Căn cứ:** thiết kế tiền đăng ký yêu cầu *near-duplicate* 5-word Jaccard ≥0,85 đối với TRAIN và các nhóm pilot. Mã nguồn T1 trước kia dùng `near_dedupe` để sàng lọc **VAL cũ so với TRAIN được chọn** và **TEST cũ so với TRAIN+VAL cũ**; mã đó không chứng minh 320 truyện **mới** không gần trùng với VAL/TEST cũ. Bộ niêm phong 320 truyện hiện chỉ bảo vệ trùng ID, TEST bucket và gần trùng toàn TRAIN/nội bộ.

Đối chứng tổng hợp chứng minh hai truyện có SHA-256 khác nhau vẫn có Jaccard 5-gram **0.900990** (lớn hơn 0,85). Do đó, lập luận 'khác ID = không gần trùng' **sai về phương pháp**. Không thể chấp nhận giả định gần trùng bằng 0 chỉ vì biên bản không đo được.

**Phán quyết B2:** `HOLD_PREREG_ATTESTATION_MISSING`. Để có `GO` đúng nguyên bản phải có **bằng chứng đã được phép thu thập trước đó**, không làm lộ hoặc mở lại nội dung TEST, xác nhận near-disjointness cho danh sách đã niêm phong. Nếu không tồn tại bằng chứng như vậy, không có cách chứng minh cổng đã đạt mà vẫn giữ nguyên mọi hạn chế; không được tự sửa điều kiện tiền đăng ký hoặc thay 320 truyện. Một sửa đổi phương pháp chỉ có thể hình thành **thí nghiệm với phạm vi suy luận yếu hơn** và cần quyết định độc lập của chủ dự án trước khi chấm.

## 4. Quyền nguồn và mục tiêu khoa học không thay đổi

Thẻ [TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories) ghi `cdla-sharing-1.0`. Văn bản [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/) quy định quyền `Use` và `Computational Use` theo điều kiện thỏa thuận; các nghĩa vụ công bố dữ liệu áp dụng riêng. `INTERNAL_COMPUTATIONAL_USE=PASS_WITH_LICENSE_CONDITIONS`, nhưng chứng cứ này không phải bảo đảm nguồn gốc quyền từng truyện hoặc bảo đảm công bố sản phẩm thương mại. Chỉ công bố code/biên bản không nhạy cảm.

Bốn checkpoint A/B/C/D SHA cố định tại 2.048 bước; chỉ số chính `TOKEN_WEIGHTED_NLL`, ba đối chứng A−C/B−C/D−C; bootstrap ghép cặp 2.000 lần theo truyện, `numpy.default_rng(2026110901)`, khoảng tin cậy 95% hai phía. Điều kiện xác nhận: **tất cả ba cận dưới phải >0**. Nếu thực thi hợp lệ nhưng không thỏa, phán quyết khoa học FAIL theo đúng phạm vi; không thử lại tùy tiện. Việc đánh giá chưa xảy ra trong bước này.

## 5. Phán quyết GO/HOLD duy nhất

| Cổng | Phán quyết |
|---|---|
| B1 — Lớp kiểm tra kỹ thuật trước forward | **PASS_SCOPED_SYNTHETIC_IMPLEMENTATION** |
| B1 — Dữ liệu thật 320 truyện trước lần forward đầu | **NOT_EXECUTED_BY_DESIGN**; runner tương lai phải bắt buộc xác minh trước forward |
| B2 — Gần trùng với nhóm VAL/TEST lịch sử | **HOLD_METHOD** |
| Quyền dùng tính toán nghiên cứu nội bộ | **PASS_WITH_CONDITIONS** |
| **Quyền thực thi khoa học one-shot CPU** | **HOLD — NOT_GRANTED** |

**Không cần mở lại QA 20/20 hoặc 118/118, không chạy model, không tái niêm phong, không tạo CLAIM one-shot, không huấn luyện/GPU.** Giữ manifest và checkpoint bất biến, `lineage.md` append-only cho kết quả khoa học thực; không ghi kỹ thuật/thiết kế vào đó.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_EMBEDDINGGEMMA2_HISTORICAL_NEAR_DUPLICATE_EVIDENCE_OR_EXPLICIT_SCOPE_DECISION`. Đề nghị **một quyết định của chủ dự án** về việc có chứng thư không chứa nội dung TEST đủ điều kiện hay chấp nhận hạ phạm vi tuyên bố qua một sửa đổi tiền đăng ký minh bạch. Cho đến quyết định đó, cổng one-shot chính thức vẫn HOLD; **không** cấp quyền chạy khoa học ngầm.
