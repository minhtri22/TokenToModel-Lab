# Mã tham chiếu GPT-like và bộ nhớ KV phân trang (Paged KV Cache) — P00

Đây là mô hình GPT-like sử dụng Transformer chỉ có bộ giải mã (Decoder-only Transformer), viết bằng PyTorch để hiểu và kiểm tra tính đúng chức năng (correctness). Mô hình có cơ chế chú ý nhiều đầu và mặt nạ nhân quả (Causal Multi-Head Attention), phép dự đoán token tiếp theo (Next-token Prediction), cùng cách lưu Key/Value (KV) vào các trang bộ nhớ để suy luận từng token.

**Đây không phải nhân PagedAttention tối ưu trên GPU tương đương vLLM.** Đường suy luận phân trang của P00 vẫn gom K/V vào tensor liên tục trước khi tính Attention. Do đó có thể phát sinh sao chép bộ nhớ và thậm chí chậm hơn đường không phân trang. Chưa triển khai xử lý nhiều yêu cầu theo lô (batching), chia sẻ tiền tố (prefix sharing), sao chép khi ghi (copy-on-write), cơ chế thu hồi (eviction), chú ý theo nhóm truy vấn (GQA), mã hóa vị trí quay (RoPE) hay các nhân FlashAttention.

## Điều kiện chạy

- Python từ phiên bản 3.10 trở lên, với phiên bản PyTorch tương thích.
- Kiểm thử ban đầu có thể chạy trên CPU. Đối với Intel Arc XPU, phải dùng gói PyTorch và trình điều khiển tương thích, kiểm tra `torch.xpu.is_available()`; P00 chưa có kết quả đánh giá XPU.

Các lệnh minh họa bên dưới chạy **từ thư mục `reference/phase0`**, không phải từ bất kỳ nơi nào bên ngoài dự án. Không tạo `.venv` nếu chưa xác nhận thư mục và tài nguyên trong ranh giới workplace.

```powershell
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
Set-Location (Join-Path $root 'worktrees\p00-source-docs-diagrams-20261105\reference\phase0')
& 'C:\Users\minht\miniforge3\python.exe' -B -m unittest -v test_reference
& 'C:\Users\minht\miniforge3\python.exe' -B demo.py
```

Lệnh trên là ví dụ cho **worktree P00 đã tồn tại**; cần kiểm tra commit, nguồn Git và đường dẫn trước khi chạy lại. Không chạy lại để thay thế hoặc ghi đè lượt kiểm thử đã khóa.

## Cách chạy minh họa huấn luyện (chưa phải kết quả P00 đã thực hiện)

Hàm mất mát và lan truyền gradient (backpropagation) đã có kiểm thử. Huấn luyện thật đòi hỏi bộ dữ liệu có quyền sử dụng, phân chia huấn luyện/đánh giá, cấu hình và giao thức được phê duyệt.

```powershell
# Ví dụ cú pháp; không tự chạy trên dữ liệu chưa được duyệt:
python train.py .\corpus.txt --steps 100 --seq-len 32 --batch-size 8 --device cpu
```

Bộ từ vựng hiện gồm 256 giá trị byte để không phụ thuộc trình tách token (Tokenizer) bên ngoài. Mô hình có trọng số khởi tạo ngẫu nhiên nên việc sinh văn bản không thể hiện năng lực ngôn ngữ đã học.

## Đọc mã nguồn theo thứ tự

1. `model.py`, `CausalSelfAttention.forward`: tính chú ý nhân quả trên toàn chuỗi (Full Causal Attention).
2. `model.py`, `GPT.forward`: khối giải mã GPT và hàm mất mát chéo (Cross-Entropy Loss).
3. `paged_kv.py`: kho trang, bảng ánh xạ, đọc/ghi và giải phóng (Block Pool / Block Table / Release).
4. `model.py`, `CausalSelfAttention.step`: tính một bước suy luận với lịch sử KV.
5. `test_reference.py`: đối chiếu mọi vị trí, mặt nạ nhân quả, cách ly nhiều yêu cầu và giới hạn bộ nhớ.
6. `demo.py`: minh họa đường chạy đầu-cuối, không phải phép đo hiệu năng.

## Công việc tiếp theo chưa được P00 chứng minh

- P05: tạo đường KV liên tục (Dense Contiguous KV Cache) làm đối chứng số học, tốc độ và bộ nhớ.
- P06: đánh giá riêng hệ quản lý KV phân trang theo khối, tỷ lệ phân mảnh và nhiều yêu cầu.
- P07: xây nhân chú ý đọc bảng trang trực tiếp trên GPU, không phải gom toàn bộ K/V.
- P08: lập lịch nhiều yêu cầu, xử lý tiền tố theo đoạn (Chunked Prefill) và đo thông lượng.
- Khi tính chú ý theo đoạn, phải sử dụng mặt nạ nhân quả có độ lệch vị trí (Offset-aware Causal Mask). Không mặc định `is_causal=True` phù hợp với mọi cặp chiều dài truy vấn và KV.

## Nguồn tham khảo

- Vaswani và cộng sự (2017), *Attention Is All You Need*: https://arxiv.org/abs/1706.03762
- Mã nguồn GPT-2: https://github.com/openai/gpt-2/blob/master/src/model.py
- minGPT: https://github.com/karpathy/minGPT/blob/master/mingpt/model.py
- nanoGPT: https://github.com/karpathy/nanoGPT/blob/master/model.py
- vLLM: https://github.com/vllm-project/vllm
- Quản lý KV của vLLM: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py
- Kho trang của vLLM: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py
- Cơ chế chia sẻ tiền tố của vLLM: https://docs.vllm.ai/en/stable/design/prefix_caching/
