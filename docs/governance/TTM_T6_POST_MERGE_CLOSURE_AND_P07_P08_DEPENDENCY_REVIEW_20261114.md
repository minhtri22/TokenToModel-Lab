# TTM — Đóng T6 sau merge và rà soát điều kiện P07/P08 (read-only)

**Operation:** `TTM_T6_POST_MERGE_CLOSURE_AND_P07_P08_DEPENDENCY_REVIEW`  
**Ngày kiểm toán:** 14/11/2026 (Asia/Bangkok)  
**Phạm vi:** đóng hồ sơ QA kỹ thuật T6; đánh giá mức sẵn sàng và phụ thuộc của P07/P08 **chỉ từ bằng chứng có sẵn**.  
**Quyết định:** `T6=CLOSED_MERGED_SCOPED` · `P07=PAUSED_PRESERVE_HOLD` · `P08=NOT_OPENED` · `SCIENCE_EXECUTION=NONE`.

## 1. Nguồn chuẩn, trạng thái code và thẩm quyền

- Repository: [`minhtri22/TokenToModel-Lab`](https://github.com/minhtri22/TokenToModel-Lab).
- T6 [PR #15](https://github.com/minhtri22/TokenToModel-Lab/pull/15) **MERGED**; reviewed head `0ebd59755b41f68b096cde31ff4d2c9e722ed455`; merge commit GitHub và `main` lúc kiểm toán `593455c9c7472042c691e0b3c69a74433c767fc7`. Parent 1 `5d52e32f20021e36f08f284ef9864d3ba36dbead` (main cũ); parent 2 là reviewed PR head. **Merge commit**, không squash.
- `lineage.md` blob Git hiện tại `259adcd9fa7197c197d424ced9a7e5887e378663`: được bảo toàn chính xác theo parent main trước merge; không chỉnh sửa trong T6 hay trong review này.
- Ba oracles bất biến: P02 `9762343e06cf800b50574c2871ae1ed58537fb18`, P05 `d835e5d7bb07fea447c5a869b13c70327ab05a53`, P06 `4d52188adaf55674b6965513ea1beb38ec9a8e9b`.
- Kế hoạch gốc: [Phase Plan P00–P12](../PHASE_PLAN.md), [Governance](../GOVERNANCE.md), [Comparison Protocol](../COMPARISON_PROTOCOL.md), [ADR-0001](../decisions/ADR-0001_TRAIN_FIRST_COLAB_AND_BRANCH_CLEANUP_20261108.md). P07 phụ thuộc P06, P08 phụ thuộc P07. Train-first pilot T1–T7 đổi **ưu tiên**, không đổi các cổng này.
- P07 được đọc trên **nhánh riêng**, không phải `main`: `feature/p07-paged-attention-kernel-design-20261107`, HEAD `06b047856a841a2213803608edfe336588857f59`. Lúc kiểm tra compare với main: `diverged`, `ahead=9`, `behind=324`. Đây là dữ kiện quản trị, **không** tự rebase/cherry-pick/merge nhánh P07.
- Kiểm kê refs GitHub khi review: **không có nhánh P08**. Không dùng sự vắng mặt nhánh làm bằng chứng duy nhất: tài liệu/ADR cũng ghi P08 chưa mở.
- Nhánh tài liệu đóng hồ sơ này bắt nguồn từ `main` sau merge, **không thay mã nguồn hoặc cập nhật main trước khi review/merge**. Bản ghi đóng T6 cũng được phép lưu tại cuộc hội thoại của PR #15 đã merge.

## 2. T6 — kết thúc phạm vi kỹ thuật đã duyệt

| Hạng mục | Kết quả chứng thực | Giới hạn |
|---|---|---|
| GitHub PR và merge | PR #15 MERGED; merge commit `593455c9…`; post-merge readback **11/11** | Không đồng nghĩa P07/P08 được mở |
| No-cache / Dense KV / Paged KV correctness | Windows synthetic CPU: **16/16** unit tests và **33/33** material/arithmetic QA | Không dùng model T4 thật hoặc TEST |
| QA độc lập số học | **17/17** cross-file checks; 4/4 hiện vật benchmark Windows khớp nguyên byte trên GitHub | Bằng chứng cho đúng fixture, không chứng nhận hiệu năng công nghiệp |
| Windows F-01 path protection | **9/9** kiểm thử âm tính, gồm junction Windows thật không SKIP; 3/3 hiện vật SHA-256 nguyên byte; Git source 7/7 không đổi sau QA | QA tác giả + Codex owner-relayed distinct review; không giả là GitHub formal review |
| TTFT / TPOT | Có phân phối/median cho 3 tải 4/11/16 token; cache metrics | No-cache vectorized prefill vs cached sequential prefill; **không tuyên bố tăng tốc** |
| Memory accounting | 2 requests: cả Dense/Paged `physical_pool=65,536 bytes`; `request_reserved=65,536/24,576`; `logical=18,432/18,432` | RSS peak **không đo được**; reserved nhỏ hơn không đồng nghĩa tổng RAM giảm |
| Scientific, training và sản phẩm | Không có TRAIN/TEST/Q1Q2/GPU phát sinh trong fixture | Không mở P09/P10/P11 hoặc science PASS |

**T6 formal closure: `CLOSED_MERGED_SCOPED`.** Mục tiêu kỹ thuật hoàn thành trong nhánh đã merge. Không cần tái chạy one-shot benchmark hoặc QA chỉ để đóng hồ sơ. Bằng chứng gốc giữ nguyên.

Bằng chứng chuẩn trên `main`:

- [Windows T6 result report](../t6/TTM_T6_WINDOWS_CPU_AB_OWNER_SCOPED_ADJUDICATION_20261109.md).
- [Windows T6 raw/custody](../../artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_INDEPENDENT_READBACK_AND_ADJUDICATION_20261109.json).
- [Windows F-01 custody](../../artifacts/qa/t6/f01_windows_owner_20261109/TTM_T6_F01_WINDOWS_CUSTODY_AND_QA_READBACK_20261114.json).
- [16/16 and 9/9 raw logs](../../artifacts/qa/t6/f01_windows_owner_20261109/).
- [Handoff and original Codex review](../t6/reviews/TTM_T6_PR15_CODEX_DISTINCT_REVIEW_20261109.md); owner chuyển kết luận `PASS_REVIEWED_SCOPED`/`MERGE_CANDIDATE`; đây không phải review được gửi trực tiếp qua GitHub Reviews API.
- [Formal post-merge receipt trên PR #15](https://github.com/minhtri22/TokenToModel-Lab/pull/15#issuecomment-6874703114).

## 3. P07 — ma trận phụ thuộc còn thiếu

P07 theo Phase Plan là **kernel PagedAttention đọc trực tiếp các trang KV vật lý trên GPU**, khác P06/T6 vốn dùng PyTorch CPU/gather. Phải PASS thiết kế thực thi, kiểm tra số học và benchmark công bằng trước khi xem xét đóng P07.

| Gate | Chứng cứ đã lưu | Trạng thái / còn thiếu |
|---|---|---|
| P06 + T6 CPU oracle | P06 technical CPU PASS; T6 merge + Windows 16/16, 9/9 | **PASS_SCOPED_CPU_BASELINE**. Cung cấp oracle, không phải GPU implementation |
| P07 G0 inventory | Intel Arc 140V + Windows 11 Home Single Language + driver 32.0.101.8860; G0 read-only inventory PASS (08/11) | **PASS_INVENTORY_HISTORICAL**. Không thay bằng trạng thái máy hiện tại |
| P07 G0 PyTorch XPU | V1 XPU `torch 2.12.1+xpu`, GPU FP32 canary PASS, max abs `3.725290298461914e-09` | **PASS_REAL_GPU_CAPABILITY_SCOPED**. Không chứng minh custom PagedAttention |
| P07 V1 một lần đã tiêu thụ | XPU stage dùng **6.037 GiB** > hạn mức nhánh A **6 GiB** đúng 0.037 GiB; 30 wheels, V1 one-shot lock và receipt giữ nguyên | **FAIL_OR_INCONCLUSIVE_NO_AUTORERUN**. Không nâng ngân sách hồi tố; không rerun V1 |
| P07 G0 compiler / Level Zero direct-index | SYCL S2 được thiết kế và QA nguồn tĩnh 24 checks, `SOURCE_ONLY`; Windows PS5.1 parser S2 chưa chạy; compiler install & GPU direct-page canary chưa chạy | **HOLD_S2_NOT_AUTHORIZED_NOT_EXECUTED**. Việc có XPU không chứng minh SYCL compiler hoạt động trên Windows Home |
| P07 G1 numerical kernel | Hợp đồng khóa: `pool[L,2,Nblocks,B,H,D]` + bảng trang; đọc K/V trực tiếp; fp32 `atol=rtol=2e-4` cho logits; negative cases; checker độc lập | **NOT_IMPLEMENTED / NOT_EXECUTED**. Chưa có bản kernel GPU thật + output attention/logits/independent negative QA |
| P07 G2 benchmark cùng GPU | G2 yêu cầu cùng GPU, dtype, tensor shape, tải, warm-up, synchronization, repeats, peak VRAM; CPU P06/T6 chỉ là oracle correctness | **NOT_EXECUTED**. Không suy luận tốc độ từ TTFT/TPOT CPU |
| P07 formal exit / PR merge | Cần G0/G1/G2 bằng chứng, reviewer, formal decision và PR độc lập | **NOT_SATISFIED**. Branch P07 `PAUSED_PRESERVE`, không merge |

Nguồn P07 đọc nguyên văn tại frozen ref `06b047856a841a2213803608edfe336588857f59`:

- [G0/G1 interface và G2 contract](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/docs/p07/P07_GPU_KERNEL_G0_G1_INTERFACE_LOCK_AND_BACKEND_MATRIX_20261107.md).
- [P07 capability preflight & independent QA plan](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/docs/p07/P07_GPU_KERNEL_CAPABILITY_PREFLIGHT_AND_INDEPENDENT_QA_PLAN_20261107.md).
- [Windows G0 backend capability gap](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/docs/p07/P07_G0_WINDOWS_BACKEND_CAPABILITY_GAP_DISPOSITION_20261108.md).
- [V1 XPU PASS / budget BLOCK / S2 not executed](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/docs/p07/P07_ONE_SHOT_XPU_SUCCESS_SYCL_NOT_EXECUTED_RECOVERY_20261108.md).
- [V1 source receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/artifacts/qa/p07/P07_ONE_SHOT_XPU_PASS_DISK_BUDGET_BLOCK_20261108.json).
- [S2 preservation plan](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/docs/p07/P07_SYCL_S2_PRESERVED_XPU_CONTINUATION_RUNBOOK_20261108.md).
- [S2 source-only QA](https://github.com/minhtri22/TokenToModel-Lab/blob/06b047856a841a2213803608edfe336588857f59/artifacts/qa/p07/P07_SYCL_S2_SUCCESSOR_SOURCE_STATIC_QA_20261108.json).

**P07 quyết định:** `HOLD_PAUSED_PRESERVE`, `G0_XPU_CANARY=PASS_SCOPED`, `S2_SYCL=NOT_EXECUTED`, `G1=NOT_IMPLEMENTED`, `G2=NOT_EXECUTED`. Chưa có điều kiện GO triển khai/kernel/merge. Giữ V1 lock; không xóa venv/wheels; không cài SYCL, thay driver/OS hoặc chạy GPU.

## 4. P08 — phụ thuộc và tình trạng chưa mở

Theo [Phase Plan](../PHASE_PLAN.md), P08 thực hiện **GPU batching/scheduling** và prefill/decode, đo TTFT, TPOT, tokens/s và memory. Điều kiện P08 không được thay bằng T6 CPU fixture:

| Cần để xem xét mở P08 | Bằng chứng | Phán quyết |
|---|---|---|
| P07 direct-page GPU kernel đúng số học (G1) | Chưa triển khai/chưa kiểm chứng | **BLOCK_DEPENDENCY** |
| P07 same-GPU benchmark/correctness gate G2, formal review + merge | Chưa có | **BLOCK_DEPENDENCY** |
| P08 scheduler contract và request isolation trên GPU | Chưa có branch/phase/runner thực thi | **NOT_OPENED** |
| Multi-request GPU (ít nhất 1/2/4), concurrency, prefill/decode, fairness, OOM/release | Chỉ có synthetic CPU two-request / GPU XPU tiny canary | **NOT_EXECUTED** |
| Phép đo same GPU/dtype/checkpoint/token IDs, sync, đủ repeats, TTFT/TPOT, throughput, peak VRAM | Không có P08 evidence | **NOT_EXECUTED** |

**P08 quyết định:** `NOT_OPENED_DEPENDENCY_ON_P07`. Không giả lập P08 từ số liệu T6 hoặc canary XPU.

## 5. Kết luận tích hợp — duy nhất, không mở phase mới

- **`GO_T6_CLOSURE`**: hoàn thành kỹ thuật synthetic CPU, đã merge; trạng thái `CLOSED_MERGED_SCOPED`. Không cần tạo phase/permit mới.
- **`HOLD_P07`**: giữ original `PAUSED_PRESERVE` cho đến khi có quyết định owner nối lại capability SYCL S2; **chưa có quyền thực thi**. Các cổng G1/G2 giữ `NOT_EXECUTED`.
- **`NO_GO_OPEN_P08`**: vì P07 chưa đạt exit, P08 không mở.

Không có điểm nào của biên bản này sửa `lineage.md`, source P02/P05/P06, checkpoint, corpus, runner hoặc một status khoa học cũ. **Không** cấp quyền: tải/cài compiler, dùng GPU, mở TEST/Q1Q2, huấn luyện, tạo PR P07/P08 hay merge nhánh P07.

### Bước thực hiện tiếp theo — duy nhất

`TTM_P07_PAUSED_PRESERVE_S2_CAPABILITY_RESUME_READINESS_SINGLE_OWNER_DECISION` (**design/read-only**): chỉ khi chủ dự án muốn cân nhắc nối lại P07, lấy snapshot nguồn V1 đã khóa, xác minh nguyên trạng wheel/lock với read-only, đối chiếu rủi ro Windows Home, ngân sách còn lại và sự phân kỳ Git **trước khi** đưa một quyết định GO/HOLD/NO_GO cho S2. Không triển khai hoặc cài đặt trong bước review này. Nếu ưu tiên vẫn Train-first theo ADR-0001, tiếp tục HOLD P07/P08 mà không phát sinh công việc GPU.

**Trạng thái:** `T6=CLOSED_MERGED_SCOPED` · `P07=PAUSED_PRESERVE` · `P08=NOT_OPENED` · `MAIN_READONLY` · `LINEAGE_UNCHANGED`.
