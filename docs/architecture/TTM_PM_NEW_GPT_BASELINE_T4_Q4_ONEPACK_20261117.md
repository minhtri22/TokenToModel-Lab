# TTM PM — NEW GPT BASELINE Colab T4 · Implementation and Q4 OnePack

**Operation:** TTM_PM_NEW_GPT_BASELINE_END_TO_END_COLAB_T4_IMPLEMENTATION_AND_Q4_ADMISSION_ONEPACK
**Ngày:** 17/11/2026
**Base main:** 59ee3f30b996405fddc087ab60102b59a021f8ea (bảo toàn main và lineage.md)
**Candidate branch:** implementation/ttm-pm-new-gpt-baseline-colab-t4-onepack-20261117
**Lock:** Q4_HOLD · REAL_TRAIN_NOT_EXECUTED · TEST_NOT_ACCESSED · NO_MERGE.

## 1. Architecture / contract

Một GPT mới khởi tạo random seed, tái sử dụng P02 GPT core tại Git blob 9762343e06cf800b50574c2871ae1ed58537fb18. **Không nạp Small-4M checkpoint step1024, loader T4 legacy hay BC-v2 codec.**

V1 tokenizer = UTF-8 raw-byte identity (0–255 = bytes, 256 EOS, 257 BOS, vocab 258). Lựa chọn này bảo đảm trace byte exact cho bpb, tránh xung đột T4 BPE-2048 và BC-v2 role IDs. Không có tokenizer fit: tokenizer deterministic theo version; BPE train-only là phase tương lai, không tự đổi IDs.

P02 GPT: context 128, embedding 128, layers 2, heads 4, seed 20261117. AdamW 3e-4, beta .9/.95, weight decay 0.1, batch windows 4, tối đa 40 optimizer steps, clip gradient 1.0. Config canonical SHA-256:
eb9711864282e214f6e6a72970969b873549da47690a43e6a39beaae428d2e1b.

Code gồm manifest rights/split/family/custody, byte-tokenization, input-to-future target shift và -100 padding, next-token training, VAL full-vocabulary cross-entropy với TEXT targets 0..255, val_bpb = sum(TEXT NLL nats)/(ln 2 × số bytes UTF-8 gốc), checkpoint mới chứa model/optimizer/sampler/RNG, READY file SHA256, greedy sample IDs. EOS/BOS/ignore không tham gia val_bpb primary.

**Giới hạn:** checkpoint resume execution/parity chưa triển khai; A independent full-vocab/scorer/gold chưa chứng thực; val_bpb chỉ là pipeline measurement candidate. Không tự suy chất lượng ngôn ngữ hoặc release.

## 2. Notebook và thao tác owner

Notebook: notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb

Runner: src/ttm_new_gpt_baseline/runner.py, exact pinned Git blob:
cf26f931044ca549fc765109ac9cfbde6b5f21de.

- Chế độ QA (mặc định) — tải đúng Git blob rồi chạy 10 tests stdlib. Không Torch, GPU, corpus, checkpoint hay TEST.
- Chế độ PROBE — chạy đúng 3 bước optimizer trên tensor ngẫu nhiên tổng hợp; đo T4, PyTorch, free/peak VRAM và elapsed; 10 GiB free preflight, 8 GiB application-reserved guard, timeout subprocess 150 giây. Không phải hard VRAM isolation và không phải science.
- Chế độ PREFLIGHT — đọc/hash dữ liệu chỉ do owner đặt trong /content/TTM_NEW_GPT_DATA và in schema/counts. Đây là readback khai báo, chưa phải independent rights QA.
- Chế độ TRAIN_REAL — chỉ sau owner Q4 GO cho đúng one-shot, kiểm lại source+config+manifest+probe hash và run_id. Hard subprocess timeout 1020 giây, nội bộ cap 900 giây, output directory không tồn tại. Notebook không tự tạo GO, không tự mount Drive hoặc ghi GitHub.

Python3.12 là hard requirement. Notebook lấy P02 raw tại commit exact, xác minh Git blob trước import. Torch được import chỉ trong PROBE/TRAIN_REAL. Không pip install; dependency thực tế cần được xác minh bằng PROBE.

### Manifest dữ liệu có quyền sử dụng

Tệp data_manifest.json, đúng schema ttm.newgpt.data.v1, có records cho cả TRAIN và VAL. Mỗi record chứa chính xác: path, split, family, sha256, rights_basis, rights_reference, pii_reviewed. Ví dụ:

    {
      "schema":"ttm.newgpt.data.v1",
      "records":[
        {"path":"train/a.txt","split":"TRAIN","family":"group_a","sha256":"<actual_file_sha256>","rights_basis":"OWNER_AUTHORED","rights_reference":"owner-created original text","pii_reviewed":true},
        {"path":"val/b.txt","split":"VAL","family":"group_b","sha256":"<actual_file_sha256>","rights_basis":"OWNER_AUTHORED","rights_reference":"owner-created original text","pii_reviewed":true}
      ]
    }

Rights basis được nhận: OWNER_AUTHORED, LICENSED_TRAINING, PUBLIC_DOMAIN. Chứng cứ tham chiếu do owner cung cấp không tự chứng minh license thật; reviewer phải kiểm tra độc lập. R2 vẫn HOLD nếu thiếu nguồn/QA. Chặn nhãn TEST, traversal/symlink, family leakage, trùng source bytes TRAIN-VAL, SHA sai, UTF-8 lỗi (real training), không attested PII/rights, >2 MB/file hoặc >16 MB/tổng. Chưa có near-duplicate independent QA.

### Exact owner Q4 file — chỉ tạo sau quyết định thật

Tệp OWNER_GO_FILE phải đúng schema sau và có SHA thực của dữ liệu/probe (mẫu không phải GO được cấp):

    {
      "schema":"ttm.newgpt.owner_q4.v1",
      "decision":"Q4_GO_NEW_GPT_SINGLE_RUN",
      "run_id":"<future_unique_run_id>",
      "runner_git_blob":"cf26f931044ca549fc765109ac9cfbde6b5f21de",
      "p02_git_blob":"9762343e06cf800b50574c2871ae1ed58537fb18",
      "config_sha256":"eb9711864282e214f6e6a72970969b873549da47690a43e6a39beaae428d2e1b",
      "manifest_sha256":"<actual_manifest_sha256>",
      "probe_sha256":"<actual_probe_json_sha256>"
    }

Đây là interlock bằng giá trị, **không xác thực chữ ký/authority độc lập**. Mọi Q4 GO phải được owner xét sau R1–R7 trong cùng một quyết định. Không suy GO từ việc tự viết JSON.

## 3. QA và F01 sửa có chứng cứ

Author runner QA: 10 source tests (UTF8, byte denominator, final-window shift, split leakage, rights, SHA, path, TEST blocking). Separate source test module: 7 kiểm tra notebook JSON/AST, exact Git object pin, default QA, refusal Q4, no-overwrite. Tất cả stdlib/không model trên Python3.12. CI hai OS Windows/Linux, không GPU/Torch.

**Negative history:** CI #44089466115 FAILED ở lỗi final shifted window length. Sửa source bằng n=min(context,len(ids)-1-i) cho cả x/y; cập nhật notebook pin. CI #44089674035 tiếp tục FAILED Windows vì test so file checkout CRLF với Git blob LF; source test sửa sang git rev-parse HEAD:src/... thay vì hash file worktree. Các FAIL lịch sử giữ nguyên; quyết định acceptance chỉ dựa CI exact FINAL HEAD.

Các test này do cùng assistant soạn, không được gắn nhãn human independent QA. Colab native probe, real training, independent A/C gold, rights verification và người dùng Q4 đều **NOT_EXECUTED/HOLD**.

## 4. R1–R7 và Q4

| Gate | Current outcome |
|---|---|
| R0 | New-source candidate, cần exact HEAD QA Win/Linux |
| R1 | HOLD_NEW_ACTION_A_C_REAL_GOLD_AND_UTF8_SCORE_PROVENANCE |
| R2 | HOLD_REAL_DATA_RIGHTS_FAMILY_AND_INDEPENDENT_SOURCE_QA |
| R3 | NEW_CHECKPOINT_OLD_T4_NOT_APPLICABLE; HOLD_REAL_DATA_AND_NEW_WEIGHT_CUSTODY |
| R4 | GPU_DETECTED_BUT_SYNTHETIC_PROBE_NOT_EXECUTED |
| R5 | N/A FOR NEW_GPT_BASELINE; historical A-I2 HOLD |
| R6 | CONFIG/STEP CONTRACT VERSIONED; HOLD_FRESH_ACTION_PREREG_DATA_GOLD_THRESHOLD |
| R7 | AUTHOR_SOURCE_QA_ONLY; HOLD_DISTINCT_REAL_QA |
| Q4 | HOLD_NO_AUTOMATIC_GO; NO_REAL_TRAIN |

**Bước thực hiện tiếp theo — duy nhất:** sau exact source CI PASS, owner chạy Colab notebook ở MODE=QA rồi tùy chọn MODE=PROBE để tạo biên nhận T4 mới. Sau đó PM xét đồng thời rights/gold/split/resource/QA và lập đúng một owner Q4 GO/HOLD cho một lượt TRAIN_REAL. Không tạo micro-permits hoặc mở TEST.
