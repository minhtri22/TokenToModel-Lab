# TTM — Đính chính thiết kế: ưu tiên Gemini Embedding 2 Free Tier

**Mã công việc:** `TTM_EMBEDDING2_FREE_TIER_DESIGN_CORRECTION`  
**Ngày:** 2026-11-08  
**Trạng thái:** `CORRECTION_ONLY / FREE_TIER_FIRST / DESIGN_ONLY / NO_API_EXECUTION`  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`  
**Base branch trước đính chính:** `2dd587b9adc21b04ff52a9e1dc36ca72bd05bd4a`  
**Main tại lần đọc trước đính chính:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`

## 1. Vấn đề được sửa, không thay thế hồ sơ lịch sử

Hai tài liệu trước phải được giữ nguyên, không ghi đè:
1. `docs/research/TTM_GEMINI_EMBEDDING2_GQA_PAGEDATTENTION_FEASIBILITY_DESIGN_20261108.md` (Git blob `10c4818abcf154e67244c0cc289c468f42b1fbf0`).
2. `docs/research/TTM_EMBEDDING2_FEASIBILITY_INDEPENDENT_DESIGN_REVIEW_20261108.md` (Git blob `9e6cd37cb83efdc52622aa49abf68bfbf8db1cc8`).

Các tài liệu cũ trình bày giá trả phí để ước lượng ngân sách, khiến việc sử dụng API trả phí dễ bị hiểu là mặc định. Bản đính chính này nêu rõ **`gemini-embedding-2` có Free Tier** và phải xem Free Tier như tuyến nghiên cứu ưu tiên, với mục tiêu **không phát sinh chi phí Gemini API**.

Đây là **đính chính giả định chi phí/điều kiện dịch vụ**, không phải cấp quyền cho API, không phải thay đổi giả thuyết khoa học, không phải kết luận kiến trúc đã khả thi.

## 2. Bằng chứng nhà cung cấp

**Nguồn chính thức được rà soát ngày 2026-11-08:**
- Google Gemini Developer API Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Google Gemini API Rate Limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Google Gemini API Billing: https://ai.google.dev/gemini-api/docs/billing

Bảng giá chính thức của **Gemini Embedding 2** (`gemini-embedding-2`) tại thời điểm rà soát:

| Hạng mục | Standard Free Tier | Standard Paid Tier |
|---|---|---|
| Text input | **Free of charge ($0)** | USD 0.20 / 1M tokens |
| Image input | **Free of charge ($0)** | USD 0.45 / 1M tokens |
| Audio input | **Free of charge ($0)** | USD 6.50 / 1M tokens |
| Video input | **Free of charge ($0)** | USD 12.00 / 1M tokens |
| Used to improve Google's products | **Yes** | **No** |

`Batch` của Gemini Embedding 2 **không có Free Tier**; mức giá Paid Tier cho văn bản là USD 0.10 / 1M tokens. Không coi Batch là giải pháp miễn phí.

Giá và hạn mức là thông tin nhà cung cấp có thể thay đổi; phải kiểm tra lại tại thời điểm quyết định thực thi. Việc Google công bố Free Tier **không chứng minh dự án/tài khoản cụ thể đang ở Free Tier**, cũng không có nghĩa số request hoặc token không giới hạn. Chưa truy cập Google AI Studio/API console của chủ dự án để xác nhận tier/quota/billing.

## 3. Quy tắc thiết kế ưu tiên miễn phí

- **Đường chính (`API_PLAN=FREE_TIER_FIRST`):** chỉ xem xét các gọi `gemini-embedding-2` ở `Standard Free Tier`, trong hạn mức được cấp cho project.
- **Ngân sách API (`TARGET_GEMINI_API_SPEND_USD=0`):** nếu không bảo đảm miễn phí, `HOLD_NO_API_CALL`; không âm thầm dùng Paid Tier, không tự cấp/quy đổi billing, không chuyển Batch trả phí.
- **Khi vượt giới hạn:** ghi `FREE_QUOTA_BLOCKED`; không vượt hạn bằng key/project khác, không đổi model, không kích hoạt trả phí; cân nhắc hoãn hoặc thiết kế fixture/cache dùng hợp lệ sau quyết định riêng.
- **Quyền dữ liệu:** Google công bố nội dung ở Free Tier có thể dùng để cải thiện sản phẩm. Không gửi corpus riêng tư, có PII, dữ liệu nghiên cứu chưa được phép, hay nội dung không có quyền chia sẻ; cần rà soát chính sách xử lý dữ liệu trước bước thực thi. Free Tier không đồng nghĩa với quyền sử dụng mọi dataset.
- **Tái lập:** version/model ID, cách tạo embedding, kích thước, prompt template, chunk hash, output hash, quota snapshot và timestamp vẫn là thông tin bắt buộc khi thực thi sau này; ở bước này chưa tạo bất kỳ embedding nào.
- **Chi phí khác:** mục tiêu $0 **chỉ nói đến Google Embedding API**; tài nguyên Colab, lưu trữ, CPU/GPU, thời gian và các API bổ sung nếu có phải được hạch toán riêng, không tự coi là miễn phí.

### Hợp đồng trước bất kỳ API call tương lai (chưa cấp phép)

1. Xác minh chính xác model ID, Free Tier thực tế và hạn mức/quota đang áp dụng trong dự án Google AI Studio được chọn; không suy diễn từ bảng giá chung.
2. Ghi chính sách billing của project và quy trình fail-closed (dừng nếu không xác nhận Free Tier); tuyệt đối không in/lưu API key trong GitHub.
3. Có danh mục dữ liệu được quyền gửi tới Google theo điều khoản Free Tier; đánh giá PII/quyền lưu vector, bao gồm quyền dùng embedding để huấn luyện Adapter.
4. Đăng ký trước số đoạn, số query, token và ngưỡng dừng dựa vào hạn mức thực tế. Lưu log quota/error không chứa dữ liệu nhạy cảm.
5. Chỉ khi được chủ dự án cho phép riêng và các điều kiện trên PASS mới mở bước D1; bản đính chính này không phải sự cho phép đó.

## 4. Các kết quả thẩm định KHÔNG thay đổi

**Phán quyết thẩm định độc lập thiết kế giữ nguyên:**
- `DESIGN_DISPOSITION=REVISE_REQUIRED`.
- `CAUSE_ATTRIBUTION_PROTOCOL=FAIL`: R3 (văn bản + frozen GPT) và V1 (vector + Adapter/Cross-Attention mới được huấn luyện) **không là đối chứng công bằng để quy riêng lợi ích cho embedding**, dù API miễn phí.
- `FAIRNESS_SHORT_LONG=HOLD`; phải bổ sung R4 (đối chứng text có học tương ứng), R_gold, S_SHORT/S_LONG, answer-only NLL và các negative controls.
- `MODEL_CAPABILITY=HOLD`: chưa có checkpoint T4 được phán quyết khoa học đủ năng lực trả lời câu hỏi; T1–T3 là PASS kỹ thuật, không là PASS chất lượng mô hình.
- `ADAPTER_TRAINING=NOT_AUTHORIZED`; `GQA_PAGEDATTENTION=SEPARATE_ENGINEERING`; `EXPORT_CROSS_ATTENTION=UNPROVEN`.
- `D1_D4=NOT_AUTHORIZED`; `API_CALLS=ZERO`; `TRAINING=ZERO`; `SCIENCE_LINEAGE=UNCHANGED`.

Thay đổi duy nhất trong ưu tiên chi phí: trước đây giả định dùng Paid Tier khi tính ước lượng; nay **Free Tier là mặc định được đề xuất** và Paid Tier chỉ là kịch bản tham khảo không được cấp quyền. Việc còn thiếu quyền dữ liệu, hạn mức và năng lực mô hình không bị xóa bởi đính chính.

## 5. Quy trình và bước tiếp theo

- Tệp này là phụ lục **chỉ bổ sung**, không ghi đè hai tài liệu nguồn và không sửa `lineage.md`.
- Không chạy API, dataset, huấn luyện, QA động, GPU, hay TEST; không thay mã nguồn, checkpoints, TTM P00–P12, P07 hoặc PR #12; không merge.
- Chưa có thực nghiệm khoa học, do đó không tạo một phán quyết `EXPERIMENT_PASS/FAIL`.
- Tuyến thí điểm TTM-Small T4 vẫn là ưu tiên thực thi chính.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDING2_FEASIBILITY_PROTOCOL_AMENDMENT_A1_DESIGN_ONLY` — bổ sung R4/R_gold, S_SHORT/S_LONG, answer-only NLL và đối chứng học tương đương, giữ Free Tier mục tiêu $0 trong phần chi phí; review lại trước khi mở D1. Không cần permit riêng cho từng QA kỹ thuật nhỏ; vẫn phải duy trì cổng nguồn/quyền dữ liệu, tiền đăng ký khoa học và phê duyệt thực thi one-shot có liên quan.
