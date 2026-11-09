# TTM — Đối chiếu kế hoạch P00–P12 gốc và đề xuất các nhánh độc lập

**Ngày rà soát:** 2026-11-09 · **Loại quyết định:** design/governance-only, không mở phase khoa học, không huấn luyện hoặc chạy inference.

**Source of truth:** `minhtri22/TokenToModel-Lab` [GitHub](https://github.com/minhtri22/TokenToModel-Lab) · `main` ghim lúc rà soát `b57b44e7287f842e81050c1faee337f636333dd0`. Tài liệu này ở nhánh quản trị riêng, **không** tự có hiệu lực khi chưa review/merge. Nguồn: [Project Charter](../../PROJECT_CHARTER.md), [PHASE_PLAN](../PHASE_PLAN.md), [ARCHITECTURE](../ARCHITECTURE.md), [TRAINING_PROTOCOL](../TRAINING_PROTOCOL.md), [GOVERNANCE](../GOVERNANCE.md), [ADR-0001](../decisions/ADR-0001_TRAIN_FIRST_COLAB_AND_BRANCH_CLEANUP_20261108.md), [Comparison Protocol](../COMPARISON_PROTOCOL.md). Các giá trị lịch sử trong tài liệu gốc chỉ được dùng theo phạm vi/thời điểm ban đầu.

## I. Quyền ưu tiên gốc không thay đổi

Mục đích từ điều lệ: xây một **GPT-like decoder-only Transformer từ đầu**, đầy đủ tokenizer, dữ liệu, huấn luyện, kiểm định, cache Dense/Paged, kernel GPU, phục vụ và phát hành; có tài liệu/sách tiếng Việt và nghiên cứu tính khả thi thương mại theo bằng chứng. Pilot Colab→Drive→Windows (T1–T7) được ưu tiên sau ADR-0001 **nhưng không thay thế** P00–P12, không tự mở P09/P10/P11/P12. Giữ ba nhóm quyết định độc lập: QA kỹ thuật, bằng chứng khoa học, và sản phẩm thương mại.

## II. Kiểm kê thực tế GitHub ngày 2026-11-09

- Ngay trước khi tạo **nhánh tài liệu quản trị này**, GitHub API trả **11 nhánh** và **01 PR open**, là **draft PR #13**. Không sử dụng kiểm kê 31 nhánh ngày 2026-11-08 trong ADR-0001 làm mô tả hiện trạng; không xóa thêm ref trong lượt này.
- Các nhánh bảo toàn lịch sử: `archive/p01-d1-prereg-draft-20261108`, `archive/p01-i0a-f0-static-side-20261108`, `archive/p01-legacy-f1-wp30-lineage-20261108`; **không xóa/merge/rewrite**.
- `feature/p07-paged-attention-kernel-design-20261107` ở `06b047856a841a2213803608edfe336588857f59`, `PAUSED_PRESERVE` theo ADR-0001. Không tiếp tục SYCL/GPU one-shot theo mặc định.
- `research/ttm-small4m-q1q2-quality-single-batch-20261109` (PR #13) có sổ GitHub Source of Truth `docs/pilot/ttm-small4m-source-of-truth/README.md`. FRESH12 đã khóa 12 prompt và 24 cặp A/B cân bằng; **chưa có reviewer độc lập**, **0/48 lượt sinh**.
- Các nhánh nghiên cứu độc lập `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`, `research/ttm-six-cross-model-representation-transfer-20261109`, `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` vẫn được tách riêng khỏi TTM model gốc; không dùng kết quả của các nhánh đó để tuyên bố T4 core tiến bộ.
- `research/ttm-small-4m-colab-pilot-prereg-20261108` và `governance/train-first-colab-and-branch-consolidation-20261108` là refs hiện có; kiểm tra exact HEAD trước mọi update, không mặc định còn active science.
- Theo tài liệu đã commit main: P00–P06 đã đạt/merge **phạm vi kỹ thuật được khóa**; T4 original huấn luyện xong đến 1280, VAL NLL có tín hiệu, nhưng chất lượng sinh bám prompt chưa được chứng minh; T5 Ollama nhập F32/sinh 32 token thật PASS kỹ thuật, **strict llama.cpp ↔ PyTorch parity vẫn FAIL 7/8**, không sửa FAIL thành PASS; PR #13/HOLD, `lineage.md` L0017 giữ nguyên.

## III. Lộ trình nguyên bản P00–P12 — phụ thuộc và phạm vi

| Phase | Kế hoạch gốc | Hiện trạng có bằng chứng | Có thể tách nhánh? |
|---|---|---|---|
| P00 | GPT-like CPU reference + Paged KV reference | Đóng/merge QA kỹ thuật | Chỉ tài liệu/đối chiếu, không chạy lại |
| P01 | Nguồn, quyền, split, tokenizer, leakage | Đóng trong phạm vi P01 đã thẩm định; pilot TinyStories T1 là tuyến riêng | Có: kiểm toán quyền phát hành/attribution **chỉ đọc** |
| P02 | Transformer embedding/norm/masked attention/MLP | Đóng synthetic CPU; source P02 blob ghim | Có: đọc mã parity/tooling, không đổi kiến trúc gốc |
| P03 | Train loop, optimizer, scheduler/overfit | Đóng synthetic; T4 là tuyến TRAIN real đã chạy | Có: thiết kế nghiên cứu tiếp theo, **không train mới** |
| P04 | Checkpoint, sampling, held-out evaluation | Đóng synthetic; T4 real VAL/TEST là hồ sơ riêng | Có: tooling đánh giá trên **prompt mới**, không mở TEST |
| P05 | Dense KV cache | Đóng QA scoped CPU | Có: benchmark fixtures ngang tải, không sửa source |
| P06 | Paged KV manager | Đóng QA scoped CPU | Có: benchmark fixtures đối chiếu P05/P02 |
| P07 | GPU direct-page PagedAttention kernel | **PAUSED_PRESERVE**, XPU canary/one-shot lịch sử | **Không mở** kernel runtime; tối đa đọc lại hợp đồng/sandbox đo |
| P08 | GPU batching/scheduler, TTFT/TPOT | Chưa mở; phụ thuộc P07 numerical parity | **Không mở triển khai**, có thể chuẩn bị schema đo |
| P09 | Model scaling | Chưa mở | Có: **design-only** cost/data/capacity, không train lớn |
| P10 | Instruction following/post-training | Chưa mở | Có: **design-only** nhãn nhiệm vụ và phản hồi, không đổi TRAIN |
| P11 | Serving API và model card | Chưa mở chính thức; T5 là pilot riêng | Có: model card/service checklist **draft-only** |
| P12 | Reproducibility, documentation/book, release | Chưa mở chính thức | Có: biên soạn tài liệu lịch sử/manifest **draft-only** |

Lưu ý: `TRAINING_PROTOCOL.md` sử dụng T0–T5 **khác** tuyến pilot T1–T7 và cũng khác số phase P00–P12. Không đồng nhất các tên T5/P05/Phase 05.

## IV. Bốn workstream độc lập đáng làm khi FRESH12 chờ reviewer

### A. T5-PARITY — tìm nguyên nhân sai khác strict logits giữa PyTorch và llama.cpp (ưu tiên 1)

- **Nhánh đề nghị chỉ tạo khi có người thực hiện:** `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109`.
- Phạm vi: static/deterministic source audit tensor QKV transpose, positional embeddings, BPE IDs, LayerNorm, GPT2-GGUF mapping và đường token-by-token; xây bộ test fixtures nhỏ OFFLINE. Nguồn đọc: `src/p02/transformer_core.py`, các scripts T2/T5 có trên `main`, biên bản `docs/pilot/TTM_T5_OLLAMA_IMPORT_AND_INFERENCE_COMPATIBILITY_FINAL_ADJUDICATION_20261109.md`.
- Kết quả dự kiến: biểu đồ discrepancy, cách tái hiện FAIL bằng fixture, mức độ ảnh hưởng, giả thuyết nguyên nhân đã phân loại; nếu thực hiện bản sửa thì **nhánh sửa riêng + QA độc lập**, không biến `T5_STRICT_PARITY=FAIL_7/8` lịch sử thành PASS.
- **Độc lập với FRESH12 và P07**, không cần T4 re-training hay Colab, không chạy lại T5/V5 one-shot đã tiêu thụ. Nếu chỉ có corpus/private checkpoint mới tái hiện được thì chặn ở READONLY_SOURCE_ONLY.

### B. T6-CACHE-AB — bộ đo tính đúng và hiệu năng Dense/Paged theo cùng tải (ưu tiên 2)

- **Nhánh đề nghị:** `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109`.
- Dùng `src/p02`, `src/p05`, `src/p06` đã merge main; xây fixture CPU ngắn, schema cache on/off vs Dense vs Paged, same tokens/checkpoint/dtype/hardware, logits parity, memory, TTFT, TPOT, tokens/s và negative tests isolation/OOM.
- Có thể QA **synthetic CPU** ngay, nhưng không tuyên bố P07/P08/GPU throughput PASS. Nếu cần chạy benchmark real checkpoint/lượt science mới thì phải có prereg/đối chứng rõ, **không dùng TEST/Q1Q2**.
- **Độc lập với FRESH12 và T5-PARITY**, miễn không chạm trọng số, dữ liệu hay lõi P02/P05/P06.

### C. T1-T5-RIGHTS-CARDS — quyền nguồn và tài liệu model/dataset card (ưu tiên 3)

- **Nhánh đề nghị:** `docs/ttm-small4m-model-card-dataset-rights-20261109`.
- Kiểm kê license/attribution nguồn TinyStories, giới hạn chia sẻ corpus/weights, dataset card, model card, model parameters/checkpoints, sha manifests, resume evidence, tính chính xác câu tuyên bố (H1 VAL, low prompt adherence, no commercial claim), reproducibility recipe; dùng metadata/manifest, **không cần đọc private token TRAIN/VAL/TEST hoặc gửi PII**.
- Đây là **T1/T5/T11/T12 supporting documentation**, **không** tự mở P11/P12 hay tuyên bố commercial-ready. Có thể làm ngay và không đụng nhánh khác.

### D. QUALITY-OBJECTIVE — chẩn đoán hướng can thiệp dữ liệu/khả năng làm theo hướng dẫn (ưu tiên 4, DESIGN ONLY)

- **Nhánh đề nghị:** `research/ttm-small4m-prompt-conditioning-objective-design-20261109`.
- Phân tích khoảng cách between next-token training và prompt-following; giả thuyết: độ bao phủ từ/nhân vật, độ dài context, loss trên continuation, giới hạn 3.75M params, sampling. Đề xuất **ít nhất 2 đối chứng**: input serialization fix vs dữ liệu/labeling khác; cùng information and compute budget nếu mở experiment.
- Dữ liệu TRAIN mới hoặc instruction-tuning bắt buộc **source/rights + prereg + separate science decision**; không mở P10, không thay checkpoint hay chạy GPU lúc design. Không dùng điểm hậu nghiệm FRESH12 làm giả thuyết xác nhận.

## V. Việc không nên phân nhánh chạy ngay

- **P07/GPU SYCL**: đang `PAUSED_PRESERVE`, one-shot cũ đã tiêu thụ và có FAIL tài nguyên; chờ quyết định owner riêng rồi mới mở, không sao chép runner để lách gate.
- **P08 GPU batching, P09 scaling thực, P10 SFT thực**: chưa qua các phase exit gates cần thiết. Chuẩn bị thiết kế hoặc công cụ kiểm định không tương đương quyền mở phase.
- **T4 step1280+ hoặc sửa TRAIN**: tạm HOLD vì 32-pair AI posthoc không thể chứng minh bám ngữ nghĩa, evaluator bị A/B imbalance; FRESH12 reviewer chưa sẵn sàng.
- **Các nhánh EmbeddingGemma2/SIX**: là nghiên cứu riêng, không được gộp vào original T4 để “cứu” chất lượng mà không có hợp đồng xuyên mô hình.
- **Không xóa/hợp nhất tự động** archive, P07, PR #13 hoặc branch nghiên cứu đang tồn tại.

## VI. Cách tạo nhánh và chống đụng độ

1. Mỗi workstream chỉ tạo **khi có tác nhân nhận việc** từ exact `main` GitHub đã xác minh; ghi `source main SHA`, branch/HEAD, danh sách paths cho phép, mã băm và output gate vào `docs/...`. Không branch từ PR #13; không tự rebase hoặc merge legacy.
2. Quy ước vùng sửa không chồng nhau: A `tools/pilot_t5/parity_diagnostic_*/`, B `tools/t6/cache_ab_*/`, C `docs/model_cards/` + `docs/data_governance/`, D `docs/research/prompt_conditioning/`. Mỗi nhánh có own QA/evidence path, PR riêng khi cần.
3. Mặc định **source/static QA hoặc synthetic CPU**; không sử dụng GPU trên dev chỉ để chuẩn bị. Không chạy Colab, không TRAIN, không TEST; tránh rerun các one-shot đã khóa.
4. Mỗi nhánh kết thúc hữu hạn trong 1 batch: `SOURCE_SHA_READBACK`, `CPU/OFFLINE_QA` phù hợp, `DISTINCT_REVIEW` nếu có, `MERGE_REVIEW`. Thiếu bằng chứng → `HOLD`, không cấp permit vi mô.
5. Giữ `lineage.md` append-only chỉ cho phán quyết khoa học PASS/FAIL. QA công cụ và tài liệu/thiết kế nằm trong branch riêng, không ghi thay science.
6. User ưu tiên Python 3.12, PowerShell 5.1; mọi worktree/cleanup chỉ trong `D:\WORK\RESEARCH\TokenToModel-Lab` với kiểm tra symlink/junction; không chạm project khác và không force-push.

## VII. Quyết định và đề nghị phân công

**Có thể làm song song ngay:** A (T5-F32 parity source diagnostic), B (T6 Cache CPU fixture), C (rights/model card). D design sau A/B không bắt buộc nhưng có thể chạy riêng mà không sử dụng dữ liệu. **Không phân công ngay P07/P08/P09/P10 thực thi.** Codex reviewer FRESH12 là một vai riêng (xem handoff PR #13) và nên tránh làm A/B/D để giảm nhiễm ngữ cảnh chất lượng.

**Đề nghị ưu tiên:** giao A cho agent kỹ thuật khi rảnh; C cho một agent tài liệu; B cho agent Python/performance. Nếu chỉ 1 agent rảnh, làm A trước vì `T5_STRICT_PARITY=FAIL_7/8` là khoảng trống tích hợp quan trọng đã đo thực tế. Không làm ảnh hưởng nhiệm vụ reviewer FRESH12 đang chờ.

**Bước thực hiện tiếp theo:** xác minh agent nào có thể nhận A/B/C và tạo đúng **một** branch khi có nhận việc; FRESH12 chỉ thực thi khi reviewer có attestation hợp lệ. **Hiện lượt này chỉ mở nhánh tài liệu governance, không mở nhánh kỹ thuật thực thi.**

`MAIN=UNCHANGED` · `PR13=HOLD` · `P07=PAUSED_PRESERVE` · `T4_TRAIN=HOLD` · `FRESH12_INFERENCE=NOT_EXECUTED` · `LINEAGE=L0017_UNCHANGED`.
