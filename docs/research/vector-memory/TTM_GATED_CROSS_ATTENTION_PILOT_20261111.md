# TTM — Gated Cross-Attention + Adaptive Memory Gate mini pilot

- **Ngày:** 2026-11-11
- **Nhánh nghiên cứu:** `research/ttm-vector-memory-architecture-20261111` — độc lập với P00–P12, không merge `main`.
- **Phán quyết:** `NO_SCOPED_EXPLORATORY`; đây KHÔNG phải kết luận phủ định mọi kiến trúc bộ nhớ vector.

## Giả thuyết và thiết kế

Giữ cố định checkpoint TTM-Small-4M đã huấn luyện bước 1280, tất cả token/position embeddings, 4 Transformer blocks, LayerNorm và tied output head. Chỉ huấn luyện adapter bằng TRAIN. So sánh: A GPT gốc; B bảng token embedding + output head được truy xuất chính xác từ bản sao lưu ngoài; OLD adapter MLP residual tại embedding token cuối (kiến trúc trước); C Gated Cross-Attention với **4 key/value giữ riêng**, query/key/value projections và gate học được theo từng trường hợp, residual ở hidden state trước tied output head; D adapter C với memory values bị tráo; E tắt nhánh C (bypass).

**Gated design:** `q=W_q h`, `k_i=W_k K_i`, `v_i=W_v V_i`, `a=softmax(q·k_i/sqrt(64)+cosine_i/0.05)`, `m=Σ a_i v_i`, `gate=sigmoid(MLP(h,m,confidence))`, `h'=h+gate*W_o m`. Tầng `W_o` khởi tạo đúng 0 để bước đầu tái tạo GPT gốc; đầu ra đi qua **cùng tied head**. Khóa là hidden state ngữ cảnh của frozen P02 trên TRAIN; giá trị là token embedding của nhãn tiếp theo trong TRAIN. **Không phải kiến thức ngoại sinh (external facts).**

Nguồn đầu vào pinned SHA-256: checkpoint `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`, TRAIN/VAL pack `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`, P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Mã `id_exact_trained.py` là bản toán học tương thích với P02, được tái sử dụng từ nghiên cứu cũ. Sai khác số học khi tách phép chiếu đầu ra tensor 3D thành phép chiếu theo hàng 2D đạt ~1.2e-5; các arm A/B dùng cùng đường 2D, kiểm tra bản gốc với `allclose`.

- Bộ nhớ: 512 truyện TRAIN; TRAIN khác để huấn luyện adapter: 512 truyện, không trùng bank; đánh giá nội bộ trên 256 truyện TRAIN **khác** không thuộc bank hoặc huấn luyện adapter. Số truyện VAL: 256.
- 64 bước optimizer/adapter, batch 16, learning rate 0.002, CPU FP32, seed 20261111, frozen GPT. OLD có 24.865 tham số học; C có 110.753 tham số học. Do **khác số tham số và vị trí chèn residual**, so sánh OLD–C không tách riêng được tác dụng của Cross-Attention.
- 256 truyện VAL đã được kiểm tra trong các phép thử trước. Tập 256 TRAIN đánh giá chưa được dùng làm memory hoặc fitting adapter, **nhưng đã thuộc TRAIN của checkpoint gốc**, vì vậy không thể gọi là VAL/TEST khoa học độc lập. Không dùng TEST, không công bố token windows.

## Kết quả: NLL thấp hơn là tốt hơn

| Nhánh | TRAIN holdout 256 NLL | VAL 256 NLL (đã từng xem) |
|---|---:|---:|
| A — Frozen GPT | **3.230207** | **3.534000** |
| B — Truy xuất chính xác FP32 | **3.230207** | **3.534000** |
| OLD — Adapter cũ | 3.391523 | 3.695487 |
| C — Gated Cross-Attention | 3.265487 | 3.578012 |
| D — C với giá trị memory bị tráo | 3.237048 | 3.559600 |
| E — Bypass | **3.230207** | **3.534000** |

- C tốt hơn OLD `0.126037` NLL (khoảng 3,7% NLL của OLD) trên TRAIN holdout nhưng vẫn **kém A** `+0.035280` và **kém D** `+0.028439`. Trên VAL, C cũng kém A `+0.044012` và D `+0.018412`.
- Khoảng bootstrap 95% mô tả của `(NLL_A − NLL_C)` trên TRAIN holdout `[-0.074585; -0.001147]`; trên VAL `[-0.091024; -0.001971]`. Các khoảng chỉ là mô tả pilot, không phải cổng ý nghĩa thống kê confirmatory.
- Tỷ lệ truy xuất Top-1 giá trị next-token đúng: 16,41% trên TRAIN holdout; 13,28% trên VAL. Gate trung bình: 0,23776 và 0,28596; gate có kích hoạt, nhưng thông tin từ bộ nhớ chưa đủ mang lại lợi ích tăng thêm.
- Giá trị lịch sử của adapter cũ trên đúng 128 VAL đầu (`3.739094`) được tái tạo trong runner. Exact lookup FP32 và bypass khớp logits đối chứng; model parameters frozen và SHA đầu vào bất biến.

**YES/NO rule:** C phải có NLL thấp hơn A, OLD và D cùng bộ đánh giá ít nhất `0.0001`; không đạt. **NO_SCOPED_EXPLORATORY**.

## QA, bảo toàn và quyết định

- Mã: `tools/research/vector-memory/gated_cross_attention_pilot.py` và QA `gated_cross_attention_audit.py`.
- Kết quả tổng hợp: `artifacts/research/vector-memory/TTM_GATED_CROSS_ATTENTION_MINI_20261111.json`; QA `TTM_GATED_CROSS_ATTENTION_QA_20261111.json`.
- Chạy lại CPU có JSON **trùng từng byte**; kiểm tra tổng hợp độc lập 32/32 PASS; checkpoint P02 nguyên trạng; TRAIN bank/FIT/đánh giá tách theo story; không đọc TEST. Không tải dữ liệu riêng tư lên GitHub.
- **Quyết định:** lưu FAIL khám phá, giữ nguyên nhánh và trạng thái dừng huấn luyện GPU. Nếu mở lại, cần đánh giá trên tập story-level chưa được sử dụng, thử tri thức bên ngoài và đối chứng `no-memory` tương đương tham số, để phân biệt vấn đề đọc bộ nhớ với vấn đề cung cấp dữ liệu.

## Chạy lại khi có tệp private trong workspace riêng

```powershell
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
& $py "$root\tools\research\vector-memory\gated_cross_attention_pilot.py" `
  --checkpoint "$root\<private>\checkpoint.pt" `
  --private-pack "$root\<private>\T4_PRIVATE_TRAIN_VAL_WINDOWS.npz" `
  --source "$root\tools\research\vector-memory\id_exact_trained.py" `
  --out "$root\<private>\gated_pilot_result.json"
```

Lệnh trên là mẫu; thay `<private>` bằng đường dẫn private bên trong workspace đã có, không chạy trực tiếp nếu chưa đặt đúng file. Tránh chạy lại khoa học nếu đã đủ bằng chứng một lượt.