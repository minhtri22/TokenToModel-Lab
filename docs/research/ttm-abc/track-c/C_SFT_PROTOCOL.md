# C-M4/M6 — Giao thức SFT và loss mask cho tuyến B (DESIGN_ONLY)

**Status:** CANDIDATE_CONTRACT / SYNTHETIC_TESTS_ONLY / TRAINING_NOT_EXECUTED. Owner approval, B trainer integration, real data rights and independent QA are pending.

## 1. Exact pinned inspiration (not code equivalence)

nanochat @ 92d63d4e8bb4df75c3b71618f31ddde2378b2bcd:
- nanochat/tokenizer.py `render_conversation`: assistant content mask=1, assistant end token mask=1, user/header mask=0; source file blob 36880f58dc168e45d947313739b697304a4e00ed.
- scripts/chat_sft.py: BOS-aligned packing, target shift by +1, mask on **shifted target**, ignore_index=-1 and padding masking; blob 86a9e6fb766754513ec575e1d27c3155ba728e6c.
- nanochat/gpt.py: cross_entropy(..., ignore_index=-1); blob 1e89378b1ae4fcba97462960b5a11695b1fe6a8e.
- nanochat/loss_eval.py: bpb sums non-special nats / (log 2 × valid target byte count); blob 5a556e6c2c8f4409b04d3dba08f487d1fed176a5.

TTM P02 GPT.forward uses **unmasked** cross_entropy by default (src/p02/transformer_core.py); B must integrate an explicit masked loss before **any** SFT. The reference's -1 is not copied blindly: candidate uses `ignore_index=-100` (PyTorch default) and asserts the trainer uses exactly -100. This is an interface requirement, not verified B compatibility.

## 2. Candidate wire format / vocabulary (v1 ONLY)

One conversation per row until reset attention/segment-aware packing exists. Toy IDs: PAD=0, BOS=1, SYS=2, USER=3, ASSIST=4, EOT=5, EOS=6. Real tokenizer MUST reserve noncolliding special IDs and version a deterministic encoder, decoder and chat template. Synthetic content token IDs >=7 and do not encode human text; illustrative only.

`[BOS] [SYS] sys_tokens [EOT]? [USER] usr_tokens [EOT] [ASSIST] answer_tokens [EOT] [EOS]`; repeat user/assistant pairs for multi-turn. Assistant header and **all system/user content are NOT supervised**. Assistant content, its EOT turn end and EOS if the conversation ends on assistant are supervised (these are completion termination targets). Explicit generation stops: EOT for turn stop, EOS for dialogue stop; document exact stop semantics with B, disallow double-EOS emission. No answer means no training target; reject empty assistant answer or structurally invalid dialogues.

### Alignment
Given `ids[0:L]` and `mask[0:L]` with 1 marking assistant **target** positions, `x=ids[:-1]`, `y=ids[1:]`, then `y[j]=IGNORE` where `mask[j+1]=0`. Padding after EOS uses PAD=0 with mask=0 and is ignored. Count supervised tokens before averaging loss; reject all-IGNORE batches to avoid NaN. Invariant: exactly one-token shift and no system/user/header/pad targets. Forward sequence length is `max_len-1`. No silent cropping/truncation; oversize items are REJECT/resize only under a predeclared rule.

**Packing:** v1 = no inter-conversation packing. Plain concatenation with BOS separators without block-diagonal attention risks cross-conversation leakage; don't enable nanochat-style packing until attention reset is validated (including at boundaries and after padding), and verify no target attends to another conversation's tokens. B must version positional IDs when extending. Synthetic QA in `tests/ttm_track_c/` uses **no model, weights, private tokenizer, GPU or data downloads**.

### M4 Single Amendment — C-F01/C-F02: semantics và nguồn gốc mask

**C-F01 (đã sửa ở mức giao thức):** Với \(L=-\log p_\theta(a\mid s,u)\), `target[j]=-100` cho mọi vị trí đích của system/user/header/pad. Vì vậy các vị trí đó có **trọng số cross-entropy trực tiếp bằng 0**, không có term loss dự đoán token prompt. Tuy nhiên gradient của **assistant loss** vẫn được phép, và thường cần, lan truyền qua embedding prompt/context và attention; \(\partial L/\partial e_{prompt}\) **không buộc bằng 0**. Không detach/stop-gradient toàn bộ prompt. Khi tích hợp Track B, kiểm tra `per_token_loss`/unreduced CE và số supervised labels sau shift, không dùng điều kiện zero gradient của prompt embedding. Bộ kiểm thử `test_cf01_zero_direct_prompt_ce_not_zero_context_gradient` dùng chứng minh chain-rule vô hướng tổng hợp, **không chạy mô hình thực**.

**C-F02 (đã sửa ở mức hợp đồng toy):** `build_sft_targets(messages, max_len)` là entrypoint B-facing được đề xuất. Nó tự gọi `serialize` sau kiểm tra vai trò, sau đó gọi `shifted_padded_targets`. Hàm thấp hơn **tái dựng** mask hợp lệ từ chuỗi token có BOS, SYS tùy chọn, cặp USER/ASSIST xen kẽ, EOT và EOS; so khớp **toàn bộ** `flags` do caller cung cấp, từ chối bất cứ bit sai hay chuỗi đặc biệt sai. Phản chứng `flags[2]=1` ở token USER trả `ValueError("mask provenance/role mismatch")`. Bao gồm test giả cờ system/user EOT, tắt cờ assistant, chuỗi sai, bool flag và boundary; 1.000 hội thoại seeded xác minh nhánh đúng.

**Ranh giới tin cậy:** Đây là xác minh **cấu trúc role/mask** của toy token ID, không phải mật mã chứng nhận nguồn dữ liệu. Một tuple `(ids,flags)` tự tạo *cùng nhất quán* không chứng minh nguồn văn bản, tính đúng vai trò do uploader khai báo, tokenizer thật hay quyền dữ liệu. Track B phải dùng dữ liệu có provenance, source/split hashes, role map và versioned chat template riêng; không đưa `flags` chưa kiểm vào cross-entropy; phải tích hợp và nhận QA độc lập trước khi nhận hợp đồng.

**C-F03 (khuyến nghị):** Toy cross-split normalized duplicate hiện dùng `NFC + casefold + whitespace collapse + NFC`; byte-hash thô không đổi. Đây **không** thay thế kiểm toán near-duplicate/family/PII của corpus T4 thực.

**Exact amendment source pins:** `tests/ttm_track_c/synthetic_contract.py` Git blob `83c6d5abe0948c24c9e49375ffc2a17e3143a793`, SHA-256 `522618430f32fd0cc74da945a7bf208aad3a146c1f113a320a13e9490f9e2b88`; `tests/ttm_track_c/test_amendment_negative.py` blob `30c3ddbdbcf907d5d16ca9247c1f683d26d26150`, SHA-256 `f89f86dffaf61e92eb016f1d8fcf5b4a2075c24e4ab7f53af24413f5b08e11d4`. Giữ nguyên 14 tests gốc blob `0681c0fd6550675baa011de78d2590fc27ba604f`.

## 3. Data & outcome contract

SFT candidates: synthetic generated local instruction-answer pairs with known slot answers, formats, Vietnamese/English language tags, unknown/abstain, counterfactual attribute changes and malicious role delimiter examples. Any real training requires source rights, disjoint TRAIN/VAL/PROBE family hashing, exact tokenizer/weights baseline pin, oversampling disclosure and actual token counts. SFT must not consume historical TEST64, FRESH16 or FINAL24.

When science separately authorized: same B base checkpoint; SFT vs unchanged base or matched NTP continuation, equal training exposure or measured FLOPs (both reported), decoding controls (greedy and fixed sampler), blind heldout slot/format/stop/repetition/unknown scores, independent seeds and CIs, explicit negative controls for prompt copying and fluent wrong binding. A single low TRAIN loss or tiny synthetic overfit demonstrates only implementation sanity, not instruction gains. SFT at 4M may reveal capacity limitation.

## 4. B integration acceptance (not already achieved)

1. B exposes tokenizer/chat-template version, `encode`, special token map and frozen schema; B trainer accepts masked targets `IGNORE=-100` and per-target reduction, with no unexpected EOS/PAD behavior.
2. Paired SHA-256 of exact serialized inputs, shifted targets, target masks and training config; one-step synthetic CPU test and negative QA asserting zero **direct per-position cross-entropy weight** for system/user/headers/padding under `ignore_index=-100` after `+1` target shift, while assistant answer/EOT/EOS targets remain supervised; do **NOT** assert zero prompt-embedding or context gradients.
3. Native B train/val smoke permitted separately and independently checked (never replace historical T4 arithmetic silently).
4. Versioned checkpoint schema and non-resumable incompatibility flag for changes to embedding/token IDs, positional encoding, activation, optimizer state.

**Current handoff:** candidate template + structurally validated toy mask only; amendment author QA passed, distinct re-review pending. **C-G5=HOLD_DESIGN_INTERFACE_PENDING_REREVIEW**; **B integration = NOT_EXECUTED**. M6 real SFT remains HOLD.
