# TTM Q1/Q2 — Python 3.12 dataclass import HOLD trước CLAIM (2026-11-09)

## 1. Chứng cứ lỗi và phân loại

Source commit trước sửa: `dae484279e832f1d78c6ce8131de0a6fa24cf134`. Người vận hành đã chạy bootstrap lấy đúng GitHub SHA và 10/10 offline tests PASS, sau đó khi `--mode preview` chạy `preflight()`, lệnh `load_module(BPE_CODE,'ttm_q1q2_bpe')` lỗi:

```text
AttributeError: 'NoneType' object has no attribute '__dict__'
  dataclasses._is_type(...) -> sys.modules.get(cls.__module__).__dict__
NATIVE_PREVIEW_FAILED_NO_CLAIM
TTM_Q1Q2_BATCH_EXIT=1
```

Nguyên nhân kỹ thuật: `importlib.util.module_from_spec(spec)` tạo module, nhưng chưa đặt nó vào `sys.modules` trước `spec.loader.exec_module(mod)`. Khi mã BPE chứa `@dataclass(frozen=True)`, Python 3.12 cần đọc module từ `sys.modules` nên lỗi. **Không phải lỗi tokenizer, mô hình, dữ liệu hay Ollama.**

- `CLAIM` Q1/Q2: **NOT_CREATED**, `_tmp/ttm_q1q2_ollama_once_v1` chưa được tạo ở thời điểm báo lỗi; từ log, chưa có request sinh output.
- Bootstrap lỗi cũ `_tmp/TTM_Q1Q2_BOOTSTRAP_dae484279e83` và tệp launcher cũ có thể còn trên máy. **Không tự xóa**, không đụng phiên T5 V5/inference đã tiêu thụ.
- Không coi `OFFLINE_QA=PASS` là `WINDOWS_PREVIEW=PASS`. Bản sửa cần tiền kiểm native trên Windows một lần nữa; **được phép vì chưa CLAIM**.

## 2. Sửa tối thiểu trong PR #13 (không tạo nhánh khác)

Tại `tools/pilot_q1q2/single_batch_20261109/ttm_q1q2_single_batch.py`:
1. Chặn tên module không hợp lệ và trùng trong `sys.modules`.
2. `sys.modules[module_name] = mod` **trước** `spec.loader.exec_module(mod)`.
3. Nếu import thất bại, xóa đúng module chưa hoàn thiện và ném lại ngoại lệ.
4. Không thay `BPE2048`, BPE TRAIN-only manifest, Q1/Q2 frozen inputs, GGUF, model store, port, số lần đo, quyền dữ liệu hoặc source V5.

Bổ sung 3 kiểm thử trong `test_ttm_q1q2_offline.py`: mô hình `@dataclass` tổng hợp import thành công, import lỗi không làm bẩn `sys.modules`, và từ chối module name nguy hiểm. Kiểm tra offline **13/13 PASS trên Linux Python 3.13.5**, kiểm tra `py_compile` cho 2 tệp PASS. Đây là QA kỹ thuật phạm vi hẹp, **không thể thay thế Windows/Python 3.12 preview và thực nghiệm**.

## 3. Nguồn bị thay và SHA khóa

| Tệp | SHA256 sau sửa | Git blob SHA |
|---|---|---|
| `ttm_q1q2_single_batch.py` | `50c049356ceb6723c8f9ba0f8762e742b85ffe3d4c5f0572ca51c5563ad53703` | `7300f8fa264bee2b4503c10ec0206b9079881b0d` |
| `test_ttm_q1q2_offline.py` | `3dc8a9aac7f47f8baeef076da86c8bc837c306f7db843793ee0897d34fa06e20` | `4baab48fde57dd0604ef7ea8a6a41b39fd0a0e63` |
| `Invoke-TTM-Q1Q2-Single-Batch-PS51.ps1` | `361d4f6452e59d446ecc661f3520191956b61d0c407cf6b07c700f5665b93473` | `e277c1548fa5ffe08a26750c861e6b9caff09d60` (không đổi) |

## 4. Điều kiện kế nhiệm

- Xác minh HEAD mới PR #13, đúng SHA256 và Git blob của wrapper; download theo commit SHA bất biến, không dùng `main` cho runner chưa merge.
- Chạy QA offline **13/13**, sau đó preview (trước CLAIM); nếu lỗi tiếp tục thì dừng tại preclaim và giữ nguyên dữ liệu, không tự cấp quyền bỏ qua.
- Chỉ khi preview PASS mới chạy một lượt Q1/Q2 đầu tiên trên chính output `_tmp/ttm_q1q2_ollama_once_v1`; không dùng lại các `CLAIM` T5.
- Sau thực nghiệm: commit raw+receipt vào GitHub PR #13, độc lập readback, đánh giá chất lượng Q1 và hiệu năng Q2, rubric người chấm; **không** kết luận chất lượng GO trước khi chấm.
- **Merge decision:** `HOLD` cho PR #13 cho tới kết quả native + review quyền/QA; `main` không đổi.

**Bước thực hiện tiếp theo:** `TTM_Q1Q2_PY312_DATACLASS_PRECLAIM_SUCCESSOR_ONE_SHOT`.
