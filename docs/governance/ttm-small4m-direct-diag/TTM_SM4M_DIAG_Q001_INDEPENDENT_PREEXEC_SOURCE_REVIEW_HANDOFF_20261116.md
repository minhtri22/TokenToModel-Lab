# HANDOFF — TTM-SM4M-DIAG-Q001 · Independent pre-execution source review

**Operation:** `TTM_SM4M_DIAG_Q001_DISTINCT_PREEXEC_RIGHTS_CUSTODY_AND_I1_RELEASE_SINGLE_GATE`  
**Dự án:** `minhtri22/TokenToModel-Lab` · **Ngày:** 2026-11-16 · **Review mode:** `SOURCE_ONLY · READ_ONLY · NO_MODEL · NO_SCIENCE · NO_FIXTURE_FREEZE`.  
**Nhánh candidate:** `review/ttm-sm4m-diag-q001-preexec-source-candidate-20261116` · **Base main/Q1 registered:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`.  
**Candidate HEAD:** Reviewer phải lấy **full 40-hex SHA của chính Draft PR trước khi đánh giá**, không dùng tên branch động làm bằng chứng.  
**QuestionID:** `TTM-SM4M-DIAG-Q001`, **ENGINEERING** (khác `TTM-P0A-MEAS-Q001` đã CLOSED_HOLD).  
**Owner decision:** `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL` đã được chủ dự án đưa ra, ghi tại PR #27 comment ID `6910234144`. Đây là **GO có điều kiện**, không phải quyền đọc checkpoint, freeze fixture hoặc chạy mô hình tự động.

## 1. Tại sao có handoff này

ZIP trước đây đã được gửi về `Downloads` của owner mà **không đưa mã vào GitHub**. Không yêu cầu owner giải nén hay chạy gói ZIP đó. Tất cả **8 file bên trong ZIP được đưa nguyên byte** lên GitHub tại:
`tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/`.

Mục tiêu của một reviewer khác là xem diff nguồn, tải bản đã khóa và kiểm soát SHA. Không đánh đồng gói ứng viên với code đã đạt I1, không tự merge PR, không sử dụng checkpoint/private TEST/FINAL.

**Archive provenance:** ZIP `TTM_SM4M_DIAG_Q001_PREEXEC_SOURCE_CANDIDATE.zip` · SHA-256 `7d926f77fc666e95175b097f2b40022020a4a846e8493b2563ee03adb7bf5897` · 18,531 bytes · 8 tệp. GitHub lưu **source tree nguyên byte** (thích hợp cho line-by-line review), không nhất thiết lưu thêm binary ZIP. Bảy tệp payload khớp manifest SHA-256; chính `SHA256_MANIFEST.json` là tệp thứ tám.

## 2. Source custody (byte-level, not just filenames)

| Exact original filename | Git blob SHA-1 | SHA-256 (file) |
|---|---|---|
| `ttm_sm4m_diag_q001.py` | `0e34694a4733affff015305a590df1f95c659703` | `69b9b85b779c2617b5fb80d7031439189ab74ea7bb4dac856a5b903595d6055a` |
| `qa_crosscheck.py` | `7df676831e2397cf6497bc0bc47a0abcf3bbdabf` | `6aa7465a906b6669d270ab40d1fc6e6686c71f9f4a30902c616f6a519a63a099` |
| `Run-Approved-OneShot-PS51.ps1` | `d727ac512d86e105e81f4dd0d897e55e27d7a05c` | `8a59bf12f60c83f4c6c6a2f93ae2f9925058ac33a96343fb1dec4b7f290f9e0f` |
| `Run-SourceQA-PS51.ps1` | `033b77253f73ff63ec3dbf1f8bb187457ab9ae77` | `b2b48b02415ec5eaab061c4cca9f114b27241bff0e20829bccccd16c47d18e27` |
| `Invoke-TTM-SM4M-DIAG-EnvPreflight-PS51.ps1` | `9e84a07d8ded5829bc822d5db01a0f9e9cbb4fc5` | `7b3aa3e8529b2b4df38ac73140ac25f8b3e22fc9e8fd04bbdeae676bc5666e57` |
| `README.md` | `a44ef622273924bc507f055f676be0ae6e5721ec` | `b7c2863766e43a98669ab8e1578bf41c5aef21984a48ea01e4cf03ddb42e77b9` |
| `SHA256_MANIFEST.json` | `5b7975ee8f33126aca8f1e5f62d6f653e1dd1fdf` | `545a84693a148a24ddf09a762f02f16dd03db9863fcd98019b0dc1c670572988` |
| `SOURCE_QA_RECEIPT.json` | `96128a9f7de92e48ab4371fe6d9b04ebf99c6962` | `b3be272f92f535f07ac08ceb1c4d0da45f2e85637a43e2f91b7ff59777ab2e54` |

## 3. What has **actually** been tested

- ZIP SHA-256 matched expected exactly; zipfile integrity and seven SHA manifest entries matched 7/7; all eight extracted Git blob SHA-1 matched GitHub readback **8/8**.
- In an isolated ChatGPT container environment, `python -m py_compile` for both Python files **PASS 2/2**.
- `ttm_sm4m_diag_q001.py source-qa` **18/18 PASS** on **in-memory mock** token IDs; `qa_crosscheck.py` **21/21 PASS**; `ttm_sm4m_diag_q001.py run` without flags exited 2 with `HOLD_MISSING_REQUIRED_RUN_FLAGS`, proving one fail-closed path.
- This was **not Python 3.12 on the owner's Windows**, did not import/run a T4 model, did not access `CF1_STEP1024_PINNED.pt` or any private checkpoint, and did not create a real frozen fixture.
- All tests are *author-controlled*, not independent QA, not rights attestation, not proof of full resource watchdog, not science. `SOURCE_QA_RECEIPT.json` is original historical receipt and has **not been rewritten**.
- Old `README.md` still says `17/17` in its final sentence though the actual JSON/tool run is `18/18` — flag a documentary discrepancy; preserve source bytes of the reviewed candidate.

## 4. Independent review tasks (one integrated review, no micro-permits)

1. **Source exactness and protocol:** pin PR HEAD, compare 8 Git blobs against table and Q1 main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`, `src/p02/transformer_core.py` blob `9762343e06cf800b50574c2871ae1ed58537fb18` and frozen Q1 JSON. Actual model is T4 4-layer/256 emb/4 heads/vocab2048/context256; checkpoint SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` is **historical**, not re-verified. No change to P0A or `lineage.md`.
2. **Oracle/negative QA:** fixture 24 TRAIN + 56 probes; 9-token context predicting tenth token, target-not-in-next-position (target value may legitimately appear within binding); correctness of 80 oracle answers, train/holdout disjointness with 16 paired counterfactuals explicitly not independent, absent-key cases, first/second key balance; evaluate positive and mutated controls.
3. **Optimization:** only 24 items receive gradients, exactly 256 planned AdamW updates, last-context-token answer cross-entropy versus naive full-sequence loss; correct PyTorch train/eval modes; no target or probe leakage, no restarting/reseeding/hyperparam tuning based on heldout.
4. **Inference comparison:** full vocab greedy top-1 and frozen four-choice restricted argmax, target logit ranks, no false 'decoder bug' when candidate-restricted succeeds but full-vocab fails; no dependence on GGUF/T5 parity.
5. **Execution/fail-closed:** do negative QA on missing/spoofed/forged permit, invalid rights, token metadata `underlying_inventory_sha256`, missing/reforged checkpoint and P02 SHA, unsupported Python/torch, output dir reuse/path escapes and 900s/12GiB/1GiB limits. **A local JSON boolean string is not independent proof of rights**; review must tie signed/owner evidence and external attestation to exact hashes. Do not execute model during this source review.
6. **Windows integration:** `Run-SourceQA-PS51.ps1` and `Run-Approved-OneShot-PS51.ps1` default `RunnerPath` references `_tmp\ttm_sm4m_diag_q001_candidate\...`, whereas the GitHub source candidate resides under `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/`. Reviewer must explicitly adjudicate/install correction before I1 release; never make the user copy/rename scripts silently.
7. **Rights/custody:** `AD-00/AD-01C/E6=NOT_VERIFIED` for the private TinyStories-derived T4 checkpoint. Do not read the checkpoint, private tokenizer inventory or sealed TEST/FINAL to 'check it' without rights/owner scope. Host `machine-1` was seen online, zero active authoritative node jobs, but this is only environment discovery.
8. **Owner's conditional GO:** already recorded at [PR #27](https://github.com/minhtri22/TokenToModel-Lab/pull/27) comment `6910234144`. Do not request the same GO again. Source reviewer returns a separate verdict on **this exact candidate**. If SOURCE PASS but I1 rights/custody or independent runner QA incomplete, record `HOLD_I2_RUNTIME_ADMISSION` while preserving owner conditional GO.

## 5. Reviewer deliverables and merge boundaries

Return **one** verdict:
- `PASS_DIAG_Q001_CANDIDATE_SOURCE_SCOPED`, only if exact source, design and independent negative test obligations pass, with *explicit* remaining rights/runtime gates; or
- `HOLD_DIAG_Q001_CANDIDATE_SOURCE`, with concrete finding IDs and smallest scoped code remedy.

Required: a reviewer Markdown, machine JSON receipt with exact HEAD, 8 Git blobs + 7 source Q1 pins, independent negative checks, F01.. finding table, and **one** owner-facing release status `GO_I1_ONLY_WITH_RIGHTS` or `HOLD_I1`; source PASS alone does not authorize I2. Submit evidence on the PR/review branch, not a local ZIP owner must handle. No source change outside specific remedy, no PR merge or model run without clear gates and permissions.

**Do not create repeated paper-only permission cycles:** the next deliverable after an admissible I1 is **one real** 256-step CPU probe with measured train/heldout/logit results or an exact blocker with evidence, followed by independent adjudication.

**Expected post-handoff status:** `OWNER_CONDITIONAL_GO_RECORDED · I1_SOURCE_PUBLISHED_ON_GITHUB · DISTINCT_SOURCE_REVIEW_PENDING · RIGHTS_CUSTODY_NOT_VERIFIED · I2_NOT_EXECUTED · LINEAGE_UNCHANGED`.
