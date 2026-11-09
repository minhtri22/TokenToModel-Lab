# TTM-Small-4M × EmbeddingGemma 2 — Phân xử khoa học độc lập, CPU 320 truyện one-shot

**Ngày:** 09/11/2026. **Nhánh:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`. **RunID:** `ttm_small4m_gemma2_confirmatory_320_story_four_arm_cpu_once_20261109_v1`.

## 1. Phán quyết

**`PASS_FIXED_CHECKPOINT_NEW_HOLDOUT_ALL_THREE_CONTRASTS`** — một lượt đánh giá xác nhận CPU one-shot trên **320 truyện mới, 405 cửa sổ, 75.798 nhãn mục tiêu mỗi cấu hình**, sử dụng bốn checkpoint A/B/C/D đã khóa ở bước 2.048. Lượt chấm đã hoàn tất, kết quả được kiểm toán độc lập từ tổng loss theo từng truyện, **không chạy lại suy luận**.

## 2. NLL đo được và ba đối chứng tiền đăng ký

| Arm | Mô tả | NLL nats/token |
|---|---|---:|
| A | Baseline tied | 3.3414141970 |
| B | Baseline untied | 3.3581664488 |
| C | EmbeddingGemma 2 token mapped + adapter | **3.3086025043** |
| D | Donor token-association permuted | 3.4265771699 |

| Contrast | Δ NLL nats/token (dương = C tốt hơn) | CI95 (bootstrap ghép cặp theo truyện) | Đạt cận dưới > 0 |
|---|---:|---|---|
| A−C | +0.0328116926 | [0.0237975734, 0.0417115821] | PASS |
| B−C | +0.0495639445 | [0.0396693963, 0.0591997070] | PASS |
| D−C | +0.1179746655 | [0.1080151847, 0.1274724691] | PASS |

Thống kê đúng tiền đăng ký: **2.000 bootstrap sample theo truyện**, `numpy.default_rng(2026110901)`, CI phân vị hai phía 95%; tiêu chí PASS là **cả ba cận dưới đều > 0**. Phán quyết về cả ba giả thuyết được xác định **trước khi xem kết quả** trong hợp đồng đã khóa. Khoảng CI riêng lẻ không tự động là khoảng bao phủ đồng thời; tiêu chí giao của ba điều kiện là phép kiểm giao (intersection–union).

## 3. Nguồn, tính toàn vẹn và QA độc lập

- Nguồn mã và bộ checkpoint trước thực thi được đóng băng trên GitHub commit `be7a8164cccf75dc5612731de80e8725ca5ed730`; source ZIP SHA256 `128f932b7e43882be1dcaac5bdca37118a78054b3c490ad3877e3838f5d6f3d3`, runner SHA256 `081115658713ef6823b5f0a2b68959235f86b2beac780f90dd451bcae6e959a5`, reviewer SHA256 `1f6fc134e7bc2a590f61b2c2c0409de701b65476bb8065ad9ad5425fc197532c`.
- Dấu CLAIM: `90dfa0b098897a090e0b711d15625c16d635d746e6ea46431e57d5f198ba72d0`; dấu RESULT: `f087faad53286b57a68d64dc182d87c72c2e1934a39a00384fc50119b53f5a94`; dữ liệu per-story riêng tư: `e79ee58524b3fcc26ea65038611e97010c753ab2daae2970066cb8b7c476bfd6`; manifest 320: `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`; dấu QA đọc lại độc lập (stdout Windows) `a6b7c52299280c480dd7d93ad09dadd86e31a89333babebaf4922a5fd831ca0b`.
- Thư mục bằng chứng gốc **trên máy chủ dự án, không đưa lên GitHub**: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_small4m_gemma2_confirmatory_320_cpu_once_20261109_v1`.
- Đọc lại các tệp `CLAIM.json`, `RESULT.json`, `INDEPENDENT_READBACK_PUBLIC.json` từ Windows qua RemoteDesktop (read-only). RunID, SHA refs, arm SHA, sự kiện chấm đúng 320 truyện/405 cửa sổ/75.798 nhãn, bốn arm và **1.620** model.forward đều khớp. `RESULT.json` vẫn ghi `COMPLETED_PENDING_INDEPENDENT_ADJUDICATION` đúng chuỗi gốc, không sửa tệp bằng chứng.
- Reviewer độc lập đã xác thực đầy đủ manifest ID/số nhãn theo truyện, checksum per-story, và tính lại NLL/bootstrap với dữ liệu riêng tư tại Windows; biên bản `PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK`. Rà soát bổ sung của phiên này chỉ đọc receipt công khai, kiểm chéo số học/tiền đăng ký/SHA, **không đọc văn bản 320 truyện, không đọc TEST, không làm thêm forward, không huấn luyện, không GPU**.
- Mã runner đã rà soát: toàn bộ source/data/model preflight xảy ra trước thao tác `out.mkdir` và `CLAIM.json` exclusive create; `CLAIM` được ghi trước lượt chấm A đầu tiên. Không thực hiện lại one-shot, dù dùng để QA.
- Biên bản kỹ thuật PREEXEC GO trước đó SHA256 `aa03c08b58aee49b46b049bceee8d735731235e19e3fed3a9725622b5d5dfdc8`. Không có kiểm tra sau kết quả để sửa chọn mẫu/seed/cổng PASS.

## 4. Giới hạn suy luận

Kết quả **xác nhận chất lượng dự đoán của bộ checkpoint C cố định trên đúng tập 320 truyện mới**, so với ba checkpoint A/B/D đã khóa. Nó **không chứng minh quan hệ nhân quả riêng của ngữ nghĩa donor**, không phải lặp độc lập training seed khác, và không khẳng định chất lượng sinh văn bản hay hiệu quả triển khai GGUF/Ollama.

Tập mới đến từ họ nguồn TinyStories VALID tương tự; kiểm toán 320×256 truyện VALIDATION lịch sử có 0 cặp gần trùng Jaccard 5-gram ≥0,85. 64 truyện TEST cũ đã được chấm ở L0012 nhưng không được mở lại; trùng gần đúng với chúng **chưa được loại trừ**. Lịch tiền huấn luyện của donor không được xác minh. A/B/C/D khác số tham số và FLOPs. Giữ nguyên L0015 FAIL và L0016 chỉ PASS thăm dò; không dùng kết quả hiện tại sửa lịch sử.

## 5. Quyết định quản trị

Đủ điều kiện ghi nối tiếp `L0017` vào `lineage.md` với phán quyết `PASS_FIXED_CHECKPOINT_NEW_HOLDOUT_ALL_THREE_CONTRASTS`. Không thay `main`, không sửa dòng cũ của lineage, không ghi data riêng tư lên GitHub. Lượt thực thi khoa học đã tiêu thụ đúng một lần; không chạy lại do đã PASS. Nếu muốn chứng minh cơ chế donor hoặc tái lập qua seed khác thì đó là nghiên cứu riêng, không được mở ngầm từ kết quả này.
