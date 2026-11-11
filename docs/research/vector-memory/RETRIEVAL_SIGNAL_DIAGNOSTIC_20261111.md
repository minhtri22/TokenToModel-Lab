# TTM Vector Memory — Retrieval Signal Diagnostic (2026-11-11)

**Phạm vi:** nhánh nghiên cứu `research/ttm-vector-memory-architecture-20261111`; không liên quan tính năng chính P00–P12, không merge `main`. **Kết quả:** `NO_INCREMENTAL_NLL_GAIN_SCOPED` / `KEY_LABEL_ASSOCIATION_POSITIVE`; tạm dừng mở rộng adapter/huấn luyện GPU.

## Dữ liệu và phương pháp

- Đúng checkpoint TTM-Small-4M đã huấn luyện ở step 1280 (SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`) và TRAIN/VAL TinyStories private window-pack (SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`). Không dùng TEST và không lưu token có thể đảo ngược lên GitHub.
- Dùng lại đúng 512 truyện TRAIN tạo bank và 128 truyện VAL đã dùng trong pilot adapter; cộng thêm **128 truyện VAL còn lại**, không trùng truyện với 128 trước. Chỉ chấm một target ở vị trí sau tiền tố tối đa 64 token/truyện.
- **Khóa (key):** hidden state của frozen P02 tại token quan sát cuối cùng, chuẩn hóa và tìm cosine Top-4. **Giá trị (value):** nhãn next-token TRAIN. So sánh với khóa chỉ dùng last-token embedding, với 1.000 lượt tráo nhãn value giữ nguyên các khóa, và với phân bố unigram của TRAIN bank.
- **Probe bổ sung, không huấn luyện:** trộn xác suất mô hình gốc và phân bố truy xuất kNN ở hệ số cố định λ=0,05, 0,10, 0,25. Phép trộn này chỉ đo thông tin tăng thêm; nó không thay thế adapter và không phải một Transformer architecture proposal đã được chấp nhận.
- Không mở gradient, không sửa weights, không tính lại tokenizer, không đọc TEST. Các kiểm tra code, nguồn và receipt chỉ dành cho experiment nhỏ.

## Kết quả chính: hidden-state content retrieval

| Nhóm VAL | Top-1 đúng | Top-1 null tráo nhãn | Top-4 có nhãn đúng | NLL baseline | NLL fusion λ=0,10 | Δ NLL fusion − baseline |
|---|---:|---:|---:|---:|---:|---:|
| 128 đã sử dụng | 14,84% | 0,76% | 32,81% | 3,63732 | 3,64059 | +0,00327 |
| **128 bổ sung** | **11,72%** | **0,88%** | **28,91%** | **3,43068** | **3,47458** | **+0,04390** |
| 256 tổng | 13,28% | 0,82% | 30,86% | 3,53400 | 3,55759 | +0,02359 |

- 128 bổ sung: permutation test Top-1 vượt null (`p=0,000999`, giới hạn bởi 1.000 permutation); nhưng **fusion λ=0,10 làm NLL tăng** `0,04390` nats/token. Khoảng bootstrap 95% của (NLL baseline − NLL fusion) `[-0,07104; -0,01091]`. Cả λ=0,05 và λ=0,25 cũng làm NLL xấu hơn trên 128 bổ sung.
- Trên 128 bổ sung, khóa chỉ dùng last-token embedding đạt Top-1 **4,69%**, kém hidden-state **11,72%**. Có tín hiệu điều kiện theo ngữ cảnh, không chỉ là nhận diện last-token.
- Fusion nhãn thực tốt hơn fusion nhãn bị tráo `0,05565` NLL trên 128 bổ sung, do đó **có thông tin truy xuất**. Tuy nhiên thông tin này **chưa vượt được mô hình gốc** và không xác nhận việc tích hợp vào Attention/MLP bằng adapter đã tốt.

## Phán quyết YES/NO

- **YES — KEY_LABEL_ASSOCIATION:** retrieval cosine trên hidden context chọn nhãn next-token TRAIN đúng nhiều hơn hẳn tráo nhãn, trên cả nhóm VAL bổ sung. Đây không phải chứng minh có tri thức ngoại sinh mới.
- **NO — INCREMENTAL_UTILITY:** chưa có cải thiện VAL NLL trước frozen baseline với fusion thử sẵn; previous learned-adapter pilot cũng FAIL. Theo quy tắc dừng khám phá, **tạm dừng nhánh mở rộng huấn luyện, không chi thêm GPU**. Không có kết luận phủ định mọi loại Vector Memory.
- **Quyết định quản trị:** nhánh GitHub vẫn được lưu độc lập, `main` và P00–P12 không thay đổi. Chỉ tiếp tục thiết kế nếu xuất hiện cơ chế truy xuất mới với lý do xác đáng và một phép đánh giá mới độc lập (ví dụ nguồn kiến thức ngoại sinh), không tune trên VAL vừa xem.

## Bằng chứng, QA và giới hạn

- Runner `tools/research/vector-memory/retrieval_signal_diagnostic.py` SHA256 `dde7b1b30de3aca63935f703f004cb0010fa19190368b70992c6570a5c049ac7` (reference model loaded from locally validated compatible P02 reimplementation; checkpoint pins original Git blob).
- Kết quả `artifacts/research/vector-memory/TTM_RETRIEVAL_SIGNAL_DIAGNOSTIC_20261111.json` SHA256 `a4d7babfa7db00ecc18b38b76812f0c0384b902f605b7ee1765b14cf9de6e5cd`.
- Byte-exact CPU replay: PASS; aggregate QA 22/22 PASS, từ `tools/research/vector-memory/retrieval_signal_audit.py` và `artifacts/research/vector-memory/TTM_RETRIEVAL_SIGNAL_AUDIT_20261111.json`.
- Hạn chế: chỉ 256 targets/256 truyện, cùng phân phối TinyStories; 128 mẫu trước đã từng dùng để đánh giá; 128 bổ sung không phải TEST sealed. Permutation chỉ chứng minh quan hệ nhãn với khóa mạnh hơn xáo trộn, **không** xác lập giá trị ngữ nghĩa hay khả năng tổng quát hóa. Chênh lệch NLL không đủ để đưa kiến trúc mới vào TTM. Không sử dụng lại VAL để chọn λ hay checkpoint.
