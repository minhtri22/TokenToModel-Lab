# TTM — Xác minh fast-forward local, kiểm kê nhánh và chuyển sang Q1/Q2

Ngày: 2026-11-09. **Nội dung là kiểm toán kỹ thuật**, không ghi vào `lineage.md`. GitHub `main` nguồn chuẩn: `b57b44e7287f842e81050c1faee337f636333dd0`.

## 1. Đồng bộ chính thức trên Windows

- Repository: `https://github.com/minhtri22/TokenToModel-Lab.git`; local: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Windows `main` và `origin/main` đều đọc trực tiếp ở `b57b44e7287f842e81050c1faee337f636333dd0`; GitHub API `main` cùng SHA; PR #12 merged đúng merge commit. Cây nguồn `main` được đồng bộ `--ff-only`, không reset/rebase/xóa.
- Biên bản nguyên byte `evidence/governance/TTM_POSTMERGE_LOCAL_MAIN_FAST_FORWARD_20261109.json` SHA256 **`c573cdfe2eb4bf380b0ff76050d2ba900c537c8792b3927578bc825579cd7a80`**, Git blob SHA1 `d61edf634e155e224f8422d58b7c47ee976b790c`. Ghi biên bản dựa trên phiên Windows 06:34:11 UTC, readback các giá trị từ RemoteDesktop và kiểm hash độc lập; không sửa số liệu.
- Trước đồng bộ: tracked dirty = 0, untracked = **17.635** (đa số bắt đầu từ `_runtime/p07/venv_xpu_cp312`); sau đồng bộ `untracked_preserved=17635`. **Không loại bỏ các file đó**; `_runtime` chưa được bỏ qua trong `.gitignore`, đây là vấn đề hygiene riêng không chặn đồng bộ.
- `lineage.md`: SHA Git blob `971fbd8eccdf4719fee6b83a3c0f4c44b13ebaa9`, bảo toàn L0011–L0012; các worktree giữ nguyên; không dọn tệp hoặc nhánh.

## 2. Kiểm kê nhánh GitHub sau PR #12

| Nhóm | Branch | Ahead/behind so với main mới | Phân xử |
|---|---|---|---|
| Đã được bao hàm | `research/ttm-small-4m-colab-pilot-prereg-20261108` | 0/1 | `RETIREMENT_CANDIDATE` — không xóa trong lượt này |
| Đã được bao hàm | `governance/train-first-colab-and-branch-consolidation-20261108` | 0/128 | `RETIREMENT_CANDIDATE` — không xóa trong lượt này |
| P01 archive | 3 nhánh `archive/p01-*` | phân kỳ | `PRESERVE_FROZEN` |
| P07 | `feature/p07-paged-attention-kernel-design-20261107` | 9/130 | `PAUSED_PRESERVE` |
| EmbeddingGemma2 | `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` | 21/14 | `PRESERVE_SEPARATE_REVIEW` |
| Embedding2/GQA | `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` | 34/127 | `PRESERVE_SEPARATE_REVIEW` |
| SIX–TTM | `research/ttm-six-cross-model-representation-transfer-20261109` | 13/127 | `PRESERVE_SEPARATE_REVIEW` |

Quyết định: **`BRANCH_DELETE=NOT_EXECUTED`**, không thay đổi worktree. Muốn xóa hai nhánh đã chứa trong main phải kiểm tra lại đúng SHA và xác minh không có worktree/PR còn tham chiếu, rồi có phê duyệt riêng.

## 3. Q1/Q2 — một workstream ngắn hạn trên GitHub

Nguồn đầu vào gốc đã merge ở `tools/pilot_q1q2/frozen_inputs_20261109/`; giữ nguyên 16 prompt, SHA-256 manifest, 48 cấu hình Q1 và 24 phép đo Q2 + 2 warm-up. **`SCIENCE_NOT_EXECUTED`**.

- Tạo duy nhất nhánh `research/ttm-small4m-q1q2-quality-single-batch-20261109` từ `b57b44e7287f842e81050c1faee337f636333dd0` để quản lý **cả bộ chạy Q1/Q2, QA, evidence, và quyết định merge cuối**, không mở nhánh con hay PR độc lập cho mỗi kiểm tra.
- Mô hình: đã import GGUF F32 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, tên `ttm-t5-f32-compat-only-v5final:latest`; checkpoint khoa học không thay. Dùng bản sao verified model store V5, tuyệt đối không chạy lại one-shot V5, không `ollama create`.
- Runner successor ở cổng loopback **12650** dự kiến, PID và HTTP ownership kiểm chứng, root output mới `_tmp/ttm_q1q2_ollama_once_v1`. Thực thi chỉ sau static QA, quyền chạy và kiểm soát RAM/disk/time; không dùng cổng 11434.
- Dữ liệu Q1/Q2 chỉ lời dẫn mới tự biên soạn. Chấm độ lặp/đa dạng trên BPE khóa, tính nhất quán theo rubric, tốc độ từ số đo Ollama. Q2 không được gọi `TTFT` nếu không có streaming. Không sử dụng TEST 64 đã niêm phong.
- Raw output và receipt phải lưu GitHub sau sàng lọc quyền/PII; trước khi dọn tạm phải đọc lại **toàn bộ** bản công khai, còn binary model store và checkpoint chỉ được dọn nếu có bản sao thực tế verified ở kho được phép.
- `Q1Q2_NEXT`: phát triển một bộ chạy (single batch) với kiểm thử ngoại tuyến, xuất bản trên PR này, QA nguồn và thực thi đúng một lần; sau đó quyết định GO/REVISE/STOP và `MERGE_READY` hoặc `HOLD`. Từng lượt phải đánh giá khả năng merge.

**Quyết định cuối lượt:** `LOCAL_MAIN_SYNC=PASS`; `BRANCH_RETIREMENT_REVIEW=PASS_NO_DELETE`; `Q1Q2_RUNNER=DESIGN_PENDING_IMPLEMENTATION`; `MAIN_MERGE=NO_CHANGE`.
