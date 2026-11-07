# TTM P07 — GPU PagedAttention Kernel: thiết kế kiểm định trước triển khai

Ngày: 2026-11-07. Trạng thái: **OPEN_DESIGN_ONLY**, không triển khai GPU, không mở P08.

## Phạm vi bắt buộc

Theo `docs/PHASE_PLAN.md`, P07 có mục đích: **nhân tính toán đọc các trang KV trực tiếp trên GPU** (PagedAttention Kernel); điều kiện đóng: **đối chiếu số học và đo hiệu năng với cùng tải**.

- P06 đã hợp nhất bằng [PR #10](https://github.com/minhtri22/TokenToModel-Lab/pull/10), mốc main chính xác `4731f75cda6aa86b1dd2929b3f10d11fbbed0812`.
- P06 oracle (CPU paged): `src/p06/paged_kv_manager.py`, exact Git blob `4d52188adaf55674b6965513ea1beb38ec9a8e9b`.
- P05 oracle (CPU dense): `src/p05/dense_kv_cache.py`, Git blob `d835e5d7bb07fea447c5a869b13c70327ab05a53`.
- P00 reference page table: `reference/phase0/paged_kv.py`, Git blob `ead322ff7559686cd8989264506cee6dd54c7441`.
- P02 Transformer CPU `GPT` pin giữ nguyên. Các nguồn P01–P06 và `lineage.md` bất biến; không rerun E0, không đọc F1 TEST hoặc corpus thực.

## G0: Tiền kiểm GPU Windows (read-only, không tiêu thụ lượt thực nghiệm)

Đích: máy Windows 11 với Intel Arc 140V đã được chủ dự án khai báo. **Không giả định** GPU backend khả dụng. Chỉ thu thập và lưu bằng chứng:

1. GPU/driver/device ID/driver version; tên CPU, RAM trống, dung lượng ổ đĩa dự định chứa cache; Windows build.
2. Python 3.12.10 và các môi trường đã có; `torch.__version__`, `torch.backends`, `torch.xpu.is_available()` nếu có, số GPU XPU và bộ nhớ khả dụng (chỉ đọc). Không cài, không cập nhật driver, không tải runtime.
3. Liệt kê các compiler/toolchain đã cài mà không chạy kernel; khóa chính xác phiên bản và chức năng cần thiết. Không suy đoán hỗ trợ từ tên sản phẩm GPU.
4. Đưa ra ma trận khả thi cho tối thiểu các backend GPU có sẵn thực tế; một backend được chọn **chỉ** sau khi chứng minh đọc trực tiếp paged KV và phép tính tham chiếu có thể thực hiện.
5. Nếu không có backend phù hợp: `G0=BLOCKED_CAPABILITY`, P07 giữ `DESIGN_ONLY`. Không lùi P07 thành CUDA/NVIDIA và không dùng CPU để tuyên bố GPU PASS.

## G1: Hợp đồng kernel và kiểm thử đúng số học

- Input shapes, page table `[requests, logical_blocks]`, pool KV `[layers, 2, physical_blocks, block_size, heads, head_dim]`, token count, mask và position mapping phải khớp P06; kernel đọc K/V qua table trực tiếp ở GPU, **không** thực hiện gather toàn bộ history về tensor dense trước attention.
- Chốt dtype/sai số riêng cho fp32 và nếu có fp16/bf16, không giả định tolerance chung. Kiểm tra mọi bước decode và logits với P06/P05/P02, bao gồm block boundary và requests xen kẽ.
- Âm tính: table invalid, physical block duplicate ngoài quyền, OOM, token length quá context, request release/reuse, xóa dữ liệu nhạy cảm sau tái sử dụng và không ghi sai vị trí.
- Có unit QA và một checker độc lập dùng PyTorch/reference GPU hoặc CPU float32 oracle; kiểm tra tính không rò rỉ request và determinism trong điều kiện được công bố.

## G2: Benchmark cùng tải, không tuyên bố tăng tốc tùy tiện

- So sánh P07 vs các đối chứng thích hợp trên **cùng GPU**, cùng hình dạng tensor, dtype, batch/context, quy trình warm-up và synchronization. So sánh CPU P06/P05 chỉ là tham chiếu chức năng, **không** dùng CPU/GPU chéo làm bằng chứng kernel speedup.
- Khóa trình tự đo và tối thiểu ba mức context, các block sizes, mức đồng thời 1/2/4 request nếu tài nguyên đủ; ghi latency theo distribution, VRAM peak, dữ liệu page table, overhead allocations, fragmentation và công suất/điện nếu có bằng chứng.
- Đánh giá thống kê từ nhiều repeats và ghi PASS/FAIL kể cả trường hợp P07 chậm hơn; không cần tạo một cổng cấp phép riêng cho từng test kỹ thuật.
- Không mở P08 scheduler/prefill/batching trong P07.

## Kết thúc P07

Yêu cầu: G0 capability PASS, G1 correctness/negative/independent QA PASS, G2 benchmark đồng điều kiện đủ bằng chứng, kiểm định Windows hoàn chỉnh, SHA-pin và phán quyết PASS/FAIL, review/merge trên một PR riêng. Không sửa `lineage.md` với các lỗi hạ tầng; ghi khoa học khi thật sự có kết quả khoa học được thẩm định.

**Bước thực hiện tiếp theo:** `TTM_P07_WINDOWS_GPU_READONLY_CAPABILITY_PREFLIGHT_AND_KERNEL_CONTRACT_LOCK`. Bước đó **chỉ tiền kiểm môi trường, không chạy GPU kernel**, không tự mở P08 hay dữ liệu thực.
