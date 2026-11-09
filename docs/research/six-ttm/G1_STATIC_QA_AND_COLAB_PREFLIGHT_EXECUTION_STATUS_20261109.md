# G1 — Biên bản QA cú pháp, trường hợp từ chối, và trạng thái Colab preflight

**Ngày:** 2026-11-09  
**Phạm vi công việc:** `TTM_SIX_XMODEL_G1_STATIC_QA_AND_COLAB_TECHNICAL_PREFLIGHT_EXECUTION`  
**Kho:** `minhtri22/TokenToModel-Lab`  
**Nhánh:** `research/ttm-six-cross-model-representation-transfer-20261109`  
**Trạng thái kết luận:** `STATIC_QA_PASS_SCOPED / COLAB_PREFLIGHT_NOT_EXECUTED / G1_SCIENCE_LOCK_HOLD`

## Nguồn được kiểm tra

- Python source: `scripts/research/six_ttm/g1_qwen06_zero_science_smoke.py`
- Exact Git blob SHA-1: `24318de7d0196944a0a9a6d6be9851099f18b85b`
- Exact SHA-256 của bytes nguồn: `cb875f0d6ec3e6d80afbe84b92c11ff632687ec5f270bfe713852772a103e90d`
- Kích thước nguồn: **7021 bytes**.
- Nguồn được đọc từ GitHub qua GitHub connector, tạo bản làm việc tạm trong sandbox QA độc lập và xác minh lại bằng `git hash-object`; mã băm Git blob **MATCH**. Sandbox QA không phải máy Windows của chủ sở hữu và không phải Colab.

## Kết quả QA thực thi

| Kiểm tra | Bằng chứng thực hiện | Kết luận |
|---|---|---|
| Exact source identity | `git hash-object` = `24318de7d0196944a0a9a6d6be9851099f18b85b` | PASS |
| Python AST parse | `ast.parse` trên chính bytes nguồn | PASS |
| Python compile | `py_compile.compile(..., doraise=True)` trên chính bytes nguồn | PASS |
| Môi trường QA độc lập | Python **3.13.5**, không phải Python 3.12.10 đã pin cho Colab | Ghi nhận giới hạn |
| Non-Colab negative probe | Chạy `python ... --phase preflight` ngoài Colab; exit code = **1**; stdout `G1_STATUS=STOP_FAIL_CLOSED`, `G1_REASON=GOOGLE_COLAB_REQUIRED_NO_WRITES`; stderr rỗng | PASS (từ chối đúng) |
| Non-Colab filesystem boundary | Trước/sau negative probe không tạo `/content/ttm_six_g1` | PASS |
| Kiểm tra không gọi huấn luyện | AST không có call `fit/train/backward/step`; code gọi `torch.inference_mode()` cho forward | PASS_SCOPED (static) |
| Notebook preflight metadata/source | `nbformat=4`, 2 cells (1 Markdown/1 Code), execution_count=null, outputs=[]; đọc lại GitHub và xác minh pin | PASS_SCOPED (notebook structural QA) |
| Google Colab T4 runtime | **Không có phiên Google Colab được kết nối trong cuộc trò chuyện / không có tool điều khiển Colab** | NOT_EXECUTED |
| Python 3.12.10, Torch 2.14.1+cu130, GPU/T4 RAM & disk thực tế | Chưa có receipt từ Colab | NOT_VERIFIED |
| Trọng số Qwen tải thật & hidden states | Không được chạy ở pha preflight | NOT_EXECUTED |

**Không dùng PASS cú pháp để suy ra runtime PASS.** Không yêu cầu đổi lock, không tự cài package, không tải Qwen, không train.

## Notebook dành cho đúng một preflight trong Colab

- Path: `notebooks/six_ttm/TTM_SIX_G1_COLAB_PREFLIGHT_ONLY_20261109.ipynb`.
- Exact notebook Git blob (đọc lại): `055ef8064634f444432b3e6fc1a0c7e4e3a3c939`.
- Notebook chỉ đọc các phiên bản thư viện, GPU, dung lượng và tải **file script nhỏ (~7 KB)** từ commit `016609c3465c768e749b351e4f7ec4088f2a1a5a`. Tính lại Git blob `24318de7d0196944a0a9a6d6be9851099f18b85b`, dừng nếu lệch; sau đó gọi `--phase preflight`.
- Notebook **không** chạy `--phase smoke`, không tải trọng số mô hình, không huấn luyện và không tự pip install.
- File receipt dự kiến chỉ có sau thực thi Colab: `/content/ttm_six_g1/G1_PREFLIGHT_RECEIPT.json`.
- Các phiên bản ứng viên hiện tại: Python `3.12.10`; torch `2.14.1+cu130`; transformers `4.57.6`; huggingface-hub `0.36.0`; tokenizers `0.22.1`; safetensors `0.6.2`; GPU T4 CC `7.5`; GPU free >=8 GiB, disk free >=6 GiB.
- **Nếu runtime Colab không trùng pin:** `STOP_FAIL_CLOSED` (không phải lỗi khoa học). Dùng inventory thực tế để thẩm định một thay đổi phiên bản trong một lượt; không sửa hậu nghiệm, không nhảy sang smoke.

## Giới hạn và quyết định

Đã thực hiện đúng QA độc lập bằng công cụ local sandbox, kiểm âm tính ngoài Colab và tạo notebook preflight có mã nguồn exact. **Không thể điều khiển một phiên Google Colab thực tế thông qua các công cụ hiện có trong phiên chat; vì vậy chưa chạy preflight Colab và không có biên bản GPU.**

`STATIC_SYNTAX=PASS` · `EXACT_GIT_BLOB=PASS` · `NONCOLAB_NEGATIVE=PASS` · `NOTEBOOK_STRUCTURE=PASS_SCOPED` · `COLAB_PREFLIGHT=NOT_EXECUTED` · `MODEL_DOWNLOAD=NO` · `LIVE_SMOKE=NOT_EXECUTED` · `SCIENCE_LOCK=HOLD`.

Không sửa `main`, PR #12, `research/lineage.md`, TTM checkpoint hoặc kho SIX; không tạo worktree trong máy chủ sở hữu; không merge.

**Bước thực hiện tiếp theo:** chủ sở hữu mở notebook trên Google Colab, chọn GPU T4 nếu có, chạy ô preflight đúng một lần và cung cấp `G1_PREFLIGHT_RECEIPT.json` hoặc kết quả console. Tiếp đó thẩm định tích hợp (giữ PIN hoặc sửa manifest có phiên bản), rồi mới xét đúng một smoke Qwen3 zero-science và khóa G1 khoa học.
