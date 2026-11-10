# TTM — TRAIN-only Lightweight Adapter vs Exact Lookup (pilot nhỏ)

- **Ngày:** 2026-11-11 · **Nhánh duy nhất:** `research/ttm-vector-memory-architecture-20261111`.
- **Phán quyết (YES/NO):** **NO trong phạm vi pilot** (`NO_SCOPED_EXPLORATORY`).
- **Loại:** nghiên cứu khám phá ngoài lộ trình P00–P12; không thay đổi `main`, không merge và chưa chấp nhận kiến trúc mới.

## Câu hỏi

Với **cùng checkpoint TTM-Small-4M đã huấn luyện**, cùng các ma trận Weights/Attention/MLP/LayerNorm/head, có thể chỉ học một adapter nhỏ từ TRAIN để đưa thông tin bộ nhớ vector ngoài vào Transformer, giúp giảm VAL negative log-likelihood (NLL) không?

## Phương pháp thực sự chạy

1. Nạp **checkpoint step 1.280** (`SHA256=ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`) và mã nguồn P02 (`Git blob=9762343e06cf800b50574c2871ae1ed58537fb18`). Mọi tham số GPT gốc bị `requires_grad_(False)` và được đối chiếu sau khi chạy.
2. Nạp bộ cửa sổ TinyStories TRAIN/VAL hợp lệ (`SHA256=184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`). Chọn theo story ID/hash, **512 truyện TRAIN riêng để xây memory bank**, **512 truyện TRAIN khác để huấn luyện adapter**, **128 truyện VAL độc lập** để chấm điểm. Không đọc TEST; không công bố raw text/token windows.
3. Tạo khóa memory bằng hidden state của **cùng frozen P02** từ tiền tố 64 token đã quan sát; cosine top-4, temperature 0.05. Giá trị là embedding của next-token trong **TRAIN bank**, không phải nhãn VAL. Tách TRAIN bank và TRAIN adapter theo story để tránh tự truy xuất nhãn khi train.
4. Adapter trainable `512→32→256`, residual được chèn vào **embedding của token quan sát cuối cùng**, **trước** 4 khối frozen Attention/MLP; đầu ra vẫn đi qua tied output head gốc. Có **24,865** tham số adapter, 64 optimizer steps, batch 16, AdamW learning rate 0.002; huấn luyện adapter từ TRAIN duy nhất.
5. Các nhánh đối chứng: A GPT gốc; B exact external embedding lookup (khớp bit-level với A); C trained memory adapter; D chính adapter C nhưng các giá trị memory bị tráo bởi permutation cố định ở lúc kiểm tra; E adapter cùng cấu trúc/cùng số tham số, được train trên cùng TRAIN nhưng đầu vào memory bằng 0.
6. Chỉ dùng **một next-token target cho mỗi truyện VAL**; NLL nats/target và Top-1 accuracy; cố định seed 20261111 và CPU PyTorch 2.10.0+cpu. Cùng một subset VAL được đánh giá trong lần chạy cuối và replay xác minh, không lựa chọn/tinh chỉnh hyperparameter theo VAL, không chạy TEST.

## Kết quả chính

| Nhánh | VAL NLL (nats/token), càng thấp càng tốt | PPL | Top-1 accuracy |
|---|---:|---:|---:|
| A — baseline | 3.637324 | 37.9901 | 28.91% |
| B — exact external lookup | 3.637324 | 37.9901 | 28.91% |
| C — TRAIN memory + learned adapter | 3.739094 | 42.0599 | 22.66% |
| D — shuffled TRAIN values | 3.715827 | 41.0926 | 28.12% |
| E — trained no-memory adapter | 3.759571 | 42.9300 | 21.88% |

- C − A = **+0.101770** nats/token (xấu hơn baseline).
- C − D = **+0.023267** nats/token (xấu hơn memory bị tráo).
- C − E = **-0.020477** nats/token (có lợi hơn adapter không memory, nhưng **không đủ** vượt A và D).
- Tỷ lệ top-1 next-token ở khóa nhớ gần nhất trùng nhãn VAL: **14.84%**; không phải bằng chứng hiểu ngữ nghĩa.
- Khoảng bootstrap phân vị mô tả 95% cho `(NLL_A − NLL_C)` trên 128 truyện: **[-0.184662, -0.013092]**; không phải kiểm định confirmatory đã tiền đăng ký.

**Quy tắc YES/NO khám phá:** C phải có NLL thấp hơn **cả A, D và E** >0,0001. Kết quả: **NO**. Không thể dùng chênh lệch C tốt hơn E đơn độc để claim memory có ích.

## Kiểm tra tái lập / bảo toàn

- SHA256 runner: `fc76d51d046aacf47ed97bb4491337128302762e1fdf3f8bc8b5606b9df84f3c`.
- SHA256 JSON kết quả chính = replay: `0c9f8b2c325e313a8bd4a0f39693b40991e003b4ae7ae7c8dc7c390325396a3b`.
- Re-run độc lập trong cùng môi trường CPU cho **JSON trùng từng byte**; QA nội bộ **16/16 PASS**.
- Checkpoint gốc không đổi, A/B bit-exact, TRAIN bank và TRAIN fit không trùng story, adapter không xem nhãn VAL hoặc TEST.
- Kết quả chỉ lưu aggregate và SHA; **không upload checkpoint, tokenizer private, TRAIN/VAL reversible windows hoặc raw story**.

## Giới hạn và định hướng

Đây là bài pilot CPU cỡ nhỏ với **128 targets/128 truyện**, một checkpoint và một thiết kế adapter/top-k, không phải đánh giá trên toàn tập VAL hoặc ngoài miền (OOD). Đường truy xuất là nearest neighbor trên hidden context, không chứng minh semantic retrieval nói chung. Không sử dụng TEST hay thay đổi cổng khoa học chính.

**Quyết định:** giữ nghiên cứu trên nhánh độc lập, `NO_SCOPED_EXPLORATORY`. Không merge vào `main`, không mở thử nghiệm lớn chỉ dựa vào pilot. Hướng tiếp theo (chỉ khi có lý do): đánh giá chất lượng khóa ngữ cảnh và giá trị truy xuất trước khi tăng kích thước adapter hoặc ngân sách huấn luyện.

## Bằng chứng trên nhánh

- `tools/research/vector-memory/adapter_train_only_pilot.py` (runner).
- `tools/research/vector-memory/adapter_pilot_qa.py` (QA nội bộ).
- `artifacts/research/vector-memory/TTM_ADAPTER_TRAIN_ONLY_PILOT_20261111.json` (số liệu aggregate).
- `artifacts/research/vector-memory/TTM_ADAPTER_TRAIN_ONLY_REPLAY_QA_20261111.json` (receipt QA/replay).
- `lineage.md` ghi bổ sung **L0017** (append-only).
