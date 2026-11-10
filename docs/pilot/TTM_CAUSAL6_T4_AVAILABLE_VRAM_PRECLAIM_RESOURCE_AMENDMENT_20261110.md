# CAUSAL6 — Sửa cổng VRAM của Tesla T4 trước CLAIM (2026-11-10)

**Trạng thái:** PRE-CLAIM RESOURCE AMENDMENT, **không thực thi huấn luyện**. **Thao tác:** `TTM_CAUSAL6_T4_AVAILABLE_VRAM_SCOPED_REPAIR`.

## Bằng chứng trực tiếp từ Colab của chủ dự án

- Python `3.13.16`, PyTorch `2.14.1+cu130`, `CUDA_AVAILABLE=True`, `GPU_COUNT=1`.
- Tên GPU: `Tesla T4`.
- `torch.cuda.get_device_properties(0).total_memory / 1024**3 = 14.56317138671875 GiB`.
- Google Drive free do owner xác nhận: `6.0 GiB`.
- `CUBLAS_WORKSPACE_CONFIG=:4096:8`, thư mục run **chưa tồn tại**.
- `preflight` báo **`RuntimeError: HOLD_T4_TOO_SMALL`** ở dòng `require(total >= 15*1024**3,'T4_TOO_SMALL')` trước CLAIM. Không có optimizer.step science, không dùng H512 để score.

## Định nghĩa lỗi và sửa duy nhất

Hợp đồng ban đầu ghi T4 board VRAM 16 GB đồng thời yêu cầu `>=15 GiB` theo hệ nhị phân. GPU Tesla T4 thực tế thường báo thấp hơn 15 GiB khả dụng, trong trường hợp này **14.563 GiB**. Đây là lỗi quy đổi/đặt ngưỡng kỹ thuật, không phải chủ đích thay đổi năng lực hay ngân sách mô hình.

**Đổi một biểu thức trong `gpu_preflight`:**

```diff
- require(total >= 15*1024**3,'T4_TOO_SMALL')
+ require(total >= 14*1024**3,'T4_TOO_SMALL')
```

Các điều kiện vẫn **nguyên vẹn**:
- Tesla T4 duy nhất, `CUDA=True`, Google Colab Free, Drive free owner-attested >=4 GiB.
- FP32, deterministic algorithms, CUBLAS workspace, cùng source/model/data hashes, cùng H512 niêm phong.
- **Bắt buộc** synthetic GPU smoke forward/backward và `torch.cuda.max_memory_allocated() < 12 GiB` trước CLAIM.
- Sáu arms, mỗi arm 2.048 steps × 4.096 nhãn, optimizer/seed/sampler/CI và RUN_ID **không thay đổi**.
- Không tự động thay sang GPU khác, không điều chỉnh số bước, không bỏ cổng 12 GiB.

## Mã băm đã xác minh

- Python runner gốc của private ZIP trước patch, SHA-256 `51b15ebde7587dcad9a880116ab4c2cc605132cb0ac54ea03af05c7d12bac612`.
- Python runner sau sửa một biểu thức, SHA-256 `bf1da76016e134e21c4d21eb7b972fd98cf8563deca965e50bacef457a590e32`.
- Bản sửa đã được `ast.parse`/Python compilation và `--mode fixture` chạy synthetic-only **PASS_5/5**, không chạy CUDA, không huấn luyện science.
- Commit mới cập nhật đúng file runner trên nhánh nghiên cứu; private ZIP cũ và `SOURCE_SHA256_MANIFEST.json` của ZIP vẫn là bằng chứng nguồn gốc frozen. Trên Colab, vá bản runner giải nén chỉ khi SHA gốc trùng; xác minh SHA mới **trước khi gọi preflight**.

## Quản trị khoa học

Đây là **amendment kỹ thuật pre-CLAIM** nhằm sửa tiêu chí tài nguyên để tương thích với T4 thực tế, không thay đổi bài toán khoa học. Không sửa nội dung lịch sử L0017/L0018, `lineage.md`, `main`, dữ liệu hoặc model gốc. Lưu source hash mới trong các receipt khi chạy nếu preflight thành công. Nếu smoke GPU fail, giữ nguyên HOLD và không chạy science. Không tạo CLAIM khi preflight chưa đạt đầy đủ.

**Bước kế tiếp:** chạy một ô Colab kiểm PIN (SHA old) → vá đúng một dòng → xác minh SHA new → PRE-CLAIM lại, rồi chỉ chạy ô science sau khi `PASS_NO_SCIENCE_CONSUMED` được xác nhận.