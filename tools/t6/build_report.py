"""Render a single read-only report for the frozen T6 CPU synthetic QA artifact."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[2]
a=json.loads((ROOT/'artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json').read_text())
qa=json.loads((ROOT/'artifacts/qa/t6/TTM_T6_INDEPENDENT_QA_20261109.json').read_text())
rows=[]
for w in a['workloads']:
 for mode in ('no_cache','dense','paged'):
  p=w['performance'][mode]
  diff=w['correctness'].get(mode,{}).get('max_abs_logit_error_vs_no_cache',0.0)
  rows.append(f"| {w['name']} ({w['prompt_token_count']} prompt + {w['continuation_token_count']} output) | {mode} | {p['ttft']['median_ms']:.3f} | {p['tpot_per_request_mean_ms']['median_ms']:.3f} | {p['kv_after_decode']['kv_pool_allocated_bytes']:,} | {p['kv_after_decode']['kv_request_reserved_bytes']:,} | {diff:.9g} |")
m=a['two_request_memory']
doc=f'''# TTM T6 — Bộ thử CPU No-cache / Dense KV / Paged KV (synthetic fixture)

**Ngày:** 2026-11-09 · **Đầu việc:** `TTM_T6_DENSE_PAGED_AB_BENCHMARK_FIXTURE` · **Nhánh:** `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109`.

## Phân xử kỹ thuật

**`T6_CPU_FIXTURE=PASS_SCOPED_SYNTHETIC`** dựa trên 16/16 unittest và {qa['status']}, đo trên PyTorch {a['hardware']['torch']} / Python {a['hardware']['python']} / Linux CPU / float32 / {a['hardware']['torch_threads']} luồng Torch.

**Chưa có kết luận tăng tốc:** phép thử dùng trọng số sinh bằng `torch.manual_seed(60609)` cho P02 tổng hợp (2 lớp, 4 heads, 64 embeddings, context32, 2048 token IDs). Không phải TTM-Small-4M T4 checkpoint hay chất lượng ngôn ngữ thật. Các số thời gian là snapshot từ máy thực thi ngoài Windows, không đại diện tốc độ trên thiết bị người dùng hoặc triển khai GPU.

## Khóa mã gốc và hợp đồng thử

P02/P05/P06 đều nhập **nguyên byte không sửa**, đối chiếu Git blob từ `main` gốc `b57b44e7287f842e81050c1faee337f636333dd0`:

| Mô-đun | Git blob đã khớp |
|---|---|
| P02 | `9762343e06cf800b50574c2871ae1ed58537fb18` |
| P05 | `d835e5d7bb07fea447c5a869b13c70327ab05a53` |
| P06 | `4d52188adaf55674b6965513ea1beb38ec9a8e9b` |

- Ba backend cùng model, seed, input IDs tổng hợp, dtype float32 và chiều dài đầu ra (6 token greedy/argmax). Chạy 3 tải prompt dài 4 / 11 / 16 token, không dùng tokenizer thật hoặc nguồn riêng tư.
- So sánh từng bước logits **với chính No-cache** bằng `atol=2e-5`, `rtol=2e-5`; Dense/Paged được đối chiếu trực tiếp và **chuỗi token argmax phải trùng hoàn toàn**. Giới hạn số bước và độ dài context được kiểm tra trước thực thi.
- 1 lượt warm-up/mode; 4 lượt đo/mode/tải; luân phiên thứ tự để giảm thiên lệch. `TTFT`: request start đến logits cho token sinh đầu tiên sau prefill, gồm `cache.start` nhưng **không gồm** cấp pool ban đầu. `TPOT`: trung vị thời gian trung bình mỗi request của 5 token sinh tiếp theo. Thời gian chạy thử Paged prefill theo từng token không đồng nhất với kernel GPU prefill.
- Bộ nhớ KV ghi riêng **allocated physical pool**, **active request reservation**, **used logical bytes**, **internal fragmented bytes**. Không cộng trọng số model vào KV: số byte model tổng hợp = **{a['model']['model_weight_bytes']:,}**. RSS là mẫu process-wide, **không phải peak riêng từng backend**, không lấy để quảng bá tiết kiệm RAM.

## Kết quả đo tham khảo, không phải speedup claim

| Tải | Backend | TTFT median (ms) | TPOT median/request (ms) | KV allocated (bytes) | KV reserved active (bytes) | Max logits error vs No-cache |
|---|---|---:|---:|---:|---:|---:|
{chr(10).join(rows)}

Bảng thời gian chỉ phản ánh phép thử ngắn trên môi trường trên. No-cache xử lý prompt bằng forward vectorized, còn Dense/Paged dùng append từng token; do đó sự khác nhau TTFT không chứng minh ưu thế kiến trúc.

## Bộ nhớ với hai request đồng thời

Hai stream dài 13 và 5 token được xử lý xen kẽ, cùng model:

| Chỉ số | Dense | Paged |
|---|---:|---:|
| KV pool allocated (bytes) | {m['dense']['kv_pool_allocated_bytes']:,} | {m['paged']['kv_pool_allocated_bytes']:,} |
| KV active reserved (bytes) | {m['dense']['kv_request_reserved_bytes']:,} | {m['paged']['kv_request_reserved_bytes']:,} |
| KV logical used (bytes) | {m['dense']['kv_used_logical_bytes']:,} | {m['paged']['kv_used_logical_bytes']:,} |
| KV internal fragmentation (bytes) | {m['dense']['kv_fragmented_bytes']:,} | {m['paged']['kv_fragmented_bytes']:,} |

**Quan trọng:** paged `reserved` thấp hơn vì cấp block theo nhu cầu nhưng **pool tổng vẫn 65.536 bytes, bằng Dense ở kịch bản này**; không thể gọi là tiết kiệm RAM vật lý. Hai request không trộn trang, logits khớp, và vùng page đã được xóa (zeroed) khi release.

## QA và sai lệch có ghi nhận

- **16/16 unittest PASS** sau một lần sửa kiểm thử âm tính: thử nghiệm cố tình làm hỏng tensor đã tạo trong `inference_mode` thất bại vì PyTorch cấm sửa in-place ở ngoài mode; kiểm thử được sửa để thao tác trên bản sao trong `inference_mode`, **không sửa model/cache/runner**, sau đó PASS. Giữ mô tả lỗi lần đầu trong báo cáo này, không tính là dữ liệu khoa học.
- Kiểm toán khác mã, đọc lại JSON và tái tính 33 bất biến (`{qa['status']}`): source blob, cấu hình, số lượt, ngưỡng sai số, các tổng byte và cô lập request. Đây là **independent material/arithmetic checker**, không phải reviewer khoa học/hardware thứ hai.
- QA từ chối nguồn P02/P05/P06 đã sửa blob; cấm `train()`, token sai, overflow, OOM khi thiếu page không được mutate; release scrub và bảo vệ đường output bên ngoài root.
- Số đo không có CI hiệu năng, chưa benchmark concurrency throughput, CUDA, PagedAttention GPU, TTFT/TPOT end-to-end serving, chi phí điện và CPU Windows thật.

## Tình trạng giai đoạn & bước tiếp theo

Đây chỉ là **đồ gá đo T6 pilot**; **không mở P07/P08**, không TRAIN, không TEST/Q1Q2, không sửa `lineage.md`. `main` giữ nguyên, mọi phát sinh ở nhánh riêng. Nên có lần chạy độc lập trên Windows Python3.12 với PyTorch CPU từ exact GitHub HEAD và QA SHA-256, sau đó chỉ mới so sánh mức kỹ thuật theo đúng phần cứng. Không chạy lại các one-shot lịch sử P05/P06.

**Bước thực hiện tiếp theo:** `TTM_T6_WINDOWS_EXACT_HEAD_REPLAY_AND_SCOPED_INDEPENDENT_REVIEW` — xác minh commit và hashes, chạy duy nhất fixture CPU trên Windows dev dưới root TTM, lưu JSON timing, đối chiếu QA và thẩm định trước merge; giữ P07 paused.
'''
path=ROOT/'docs/t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md'
path.write_text(doc)
print(str(path),len(doc))
