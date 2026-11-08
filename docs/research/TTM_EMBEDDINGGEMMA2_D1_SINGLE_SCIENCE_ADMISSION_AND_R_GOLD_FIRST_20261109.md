# TTM EmbeddingGemma 2 D1 — One integrated science admission decision and R_gold-first run

**Ngày:** 2026-11-09. **Công việc:** `TTM_EMBEDDINGGEMMA2_D1_SINGLE_SCIENCE_ADMISSION_AND_R_GOLD_FIRST`.  
**Phán quyết khoa học có điều kiện:** **`READY_FOR_OWNER_ONE_SHOT_RGOLD_SCREENING_ONLY`**, **`R_GOLD_SCIENCE_NOT_EXECUTED`**.  
**Phạm vi:** D1 **R_gold synthetic capability screening** trên Qwen frozen; **R1/R2/R3 chưa chạy**, D2–D4 chưa mở. Kết quả kỹ thuật gốc `V1=CONSUMED_FAIL`, `V3=CONSUMED_FAIL`, `QWEN_FOLLOWUP=PASS` và `COMBINED_TECHNICAL_CORE=PASS_SCOPED` được bảo toàn, không viết lại.  
**Quyền chạy:** Người dùng yêu cầu **quyết định admission** nhưng chưa ghi rõ lệnh chấp thuận thực thi khoa học trên Colab trong cuộc trò chuyện; không thay chủ tài nguyên cấp quyền tự động. Việc người dùng chủ động bấm **Runtime → Run all** trên notebook R_gold này là một hành động quyết định chạy đúng **một** lượt khoa học trong giới hạn đã nêu; không có thêm cờ Boolean `OWNER_APPROVAL` hoặc micro-permit.  
**Mức bằng chứng:** hồ sơ đã khóa, kiểm thử tĩnh/giả lập; **không** phải xác nhận Colab giờ này đang rảnh hay đã chạy mô hình khoa học.  
**Nhánh nghiên cứu độc lập:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`.

## 1. Căn cứ admission duy nhất

- G1–G4: `LOCK_READY=YES_SCOPED_PREREG_ONLY` (không mở lại); fixture **60 group / 120 QA**, 48 group có đáp án ×2, 12 group không có đáp án ×2; Git blob `d6b23349d65724c5a7aaba41604b396facabfbe8`, exact SHA256 `0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a`.
- Model **Qwen/Qwen2.5-0.5B-Instruct** `@7ae557604adf67be50417f59c2c2f167def9a775`. Bộ chạy R_gold **không cần EmbeddingGemma 2** hay SQuAD vì câu hỏi khoa học ở đây là *frozen generator có biết sử dụng chứng cứ đúng?* Việc nạp EmbeddingGemma FP32 đã đạt kỹ thuật trước đó, nhưng không dùng làm bằng chứng cho R_gold.
- V3 xác nhận pinned Qwen tokenizer, snapshot local SHA, nguồn SQuAD, EmbeddingGemma text-only FP32 `[2,768]` finite; kiểm bổ sung Qwen xác nhận 44 prompt tokens, 1 answer token được chấm, finite NLL/shift. Technical combined `PASS_SCOPED`. Hai hậu kiểm storage/time cuối V3 chưa thực hiện => **không** nói full preflight PASS.
- Dataset sinh từ template hư cấu, chưa có reviewer người ngoài; 48 ID riêng nhưng cấu trúc lặp: chỉ sử dụng như **screening/pilot**, không dùng làm bằng chứng phân phối độc lập hoặc hiệu năng công nghiệp.

## 2. Bộ chạy chính xác đã khóa trước khoa học

**Source Python đọc được trên GitHub:** `docs/research/notebooks/TTM_EmbeddingGemma2_D1_RGold_OneShot_Science_20261109.py` Git blob `95861e30c35013a8d6a68d60fe259e4bef15a7a1`; **SHA256 bytes `221a3dde64b29a24bd86c6b8035cf501007163c5c0b458205379da0dfc89a70a`**.

**Colab notebook (full source embedded; no external .py dependency):** `docs/research/notebooks/TTM_EmbeddingGemma2_D1_RGold_Science_OneShot_20261109.ipynb` Git blob `4ba7b4dac31173624af4604ac5feeb195c9a10f9`; **SHA256 bytes `146e24e28d13701410a62193153ea5e1d754aeb00ec03f56fb62f0d85dfae8f8`**. All code cells unexecuted, no outputs.

**QA independent procedure (not external-human peer review):** `docs/research/qa/TTM_EmbeddingGemma2_D1_RGold_Science_Independent_Static_QA_20261109.py` SHA256 `d72b06017076375f3645488125e278eaab03c3add9736ac221b52e63eaf63bc9`, report `docs/research/qa/TTM_EmbeddingGemma2_D1_RGold_Science_Independent_Static_QA_20261109.json` SHA256 `6d05530e37817bba4e00e6d50c638c60cd8a36416e111d725739eec1dd049797`. **`QA=PASS_51_OF_51`**, all source/synthetic without model execution. Qwen expected file SHA/byte counts independently match **exact original V3 RESULT bytes**; four original receipt SHA pin checks PASS; synthetic logits check causal shift/mask/EOS; group bootstrap/decision controls check correct PASS/FAIL/INCONCLUSIVE branches. This QA **does not** validate Colab runtime, actual science or external human data content.

**Science RunID frozen:** `ttm_embedgemma2_d1_rgold_one_shot_20261109_v1`. Private Google Drive namespace `MyDrive/TTM_EmbeddingGemma2_D1_Science/<RUN_ID>` — distinct from original V1/V3/Qwen receipt directory. Check all four exact private receipt hashes before CLAIM. Before CLAIM, download/authenticate original fixture from pinned **Git commit `b10deb62567571dc4aa68e5aad9fe06b55d1e23b`**, and reuse/copy/verify pinned Qwen on private Drive. Do not change original FAIL/PASS.

**Implementation-level freeze before any results:**
- `R0` no evidence; `R_gold` exact corresponding gold evidence; `R_wrong` unrelated evidence. Identical frozen Qwen checkpoint, system and user prompt, reference answer token IDs across three arms; no target answer in prompt except the permitted gold evidence.
- Answer-only teacher-forced NLL uses **target answer tokens plus assistant `<|im_end|>`**, masked prompt with correct causal shift. This explicit EOS denominator definition is frozen **before** any science run; do not vary denominator after observing results.
- `d_g=mean_{two paraphrases}(NLL_R0 - NLL_Rgold)`; 48 group means; bootstrap `B=10,000`, `seed=20261108`, CI 2.5th–97.5th percentile. **PASS primary iff CI lower >0.10 nats/token.**
- Other locked guards: `EM_gold>=0.60` and `EM_gold-EM_R0>=0.10`; group-mean `NLL_wrong-NLL_gold>0`; no-answer factual-support guard `<=6/24` among 12 no-answer groups ×2. Greedy/no sampling, max24 tokens, no posthoc answer extraction, NFKC/casefold/terminal punctuation trim.
- **No-answer classification caution:** runner counts every nonexact `UNKNOWN` as a conservative upper bound of potentially unsupported output; this cannot prove all such outputs are false factual statements. If >6 with other gates PASS, set `INCONCLUSIVE_NEGATIVE_GUARD_REQUIRES_BLIND_FACTUAL_RESPONSE_REVIEW`, not a fabricated science PASS/FAIL. Independent reviewer reads the frozen raw private predictions; do not modify outputs.
- Group results persisted one original JSON per group. Each `group_id` is saved once, no overwrite; if Colab disconnects before RESULT, resume **same RUN_ID and exact source/protocol**, skip completed group files. Terminal RESULT cannot be rerun or overwritten; retain partial failure evidence.

## 3. One bounded resource admission, inside the SAME science launch

**No extra technical preflight:** actual Colab T4/GPU, memory, disk, pinned Qwen snapshot bytes, source/fixture SHA, transformer environment, original receipts and all group context tokenization are checked **before first science CLAIM** inside the same notebook. If mismatch: **STOP_PRECLAIM**, no scientific seed consumed. The runner uses a private Drive model cache because Colab ephemeral `/content` was lost earlier, copies exact-verified weights into local `/content` for torch inference, and runs only Qwen (no EmbeddingGemma/SQuAD downloads). 

Budget ceiling: **Colab Free Tesla T4**, planned download ≤5GiB, persistent project storage ≤8GiB, ≤30 minute session (timeout polled between questions/groups); paid services/API **$0**. The tool cannot programmatically guarantee a free-tier entitlement, monitor every network retry byte or ensure a hard GPU-kernel timeout. The owner must select free Colab and avoid starting the session if **TTM-Small T5** is using the same quota/resources. These limits are real runtime guards to the degree measurable, with stated limitations, **not** falsely claimed to have already passed.

## 4. Single adjudication and next step

**`SCIENTIFIC_ADMISSION_RECOMMENDATION=READY_FOR_OWNER_R_GOLD_ONCE`** based on source/rights scoped protocol and 51 static checks. **`SCIENCE_EXECUTION=NONE` at the time of this file**. No actual Qwen R_gold inference was executed by ChatGPT (no direct Colab runtime connection). Whether/when to run is decided by the owner clicking Run all on the **pinned** notebook.

If owner executes R_gold, preserve claim, all per-group outputs and raw terminal RESULT; independently recompute aggregate NLL/EM/group bootstrap and validate every earlier receipt. Record exact PASS/FAIL/INCONCLUSIVE in `lineage.md` **append only** after adjudication. If R_gold FAIL/INCONCLUSIVE, stop R1/R2/R3; if PASS, separately evaluate next phase within approved D1 boundaries, not automatically D2–D4.

**Repo changes:** this science-admission work only adds `docs/research/**` on the independent branch. No merge, no main changes, no TTM-Small PR #12 changes, no `lineage.md` mutations. TTM-Small T5 remains priority.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDINGGEMMA2_D1_RGOLD_OWNER_RUN_ONCE_THEN_INDEPENDENT_SCIENCE_QA` — on available Colab Free T4, owner clicks **Run all** once on the pinned notebook and provides Drive RESULT; no manual permit flag or micro-approval. If the owner does not execute, keep `SCIENCE_NOT_EXECUTED`.
