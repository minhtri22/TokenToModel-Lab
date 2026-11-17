# TTM PM — REAL GPT T4 vertical-slice adapter + A/C evaluation source admission

**Operation:** `TTM_PM_REAL_GPT_BASELINE_VERTICAL_SLICE_ADAPTER_AND_ABC_EVALUATION_ADMISSION_ONEPACK`  
**Ngày:** 17/11/2026 · **Nguồn khóa:** `minhtri22/TokenToModel-Lab` `main=b2e97dd3b773fc22a91618c8f034d22fda1f5908` sau PR #42.  
**Trạng thái:** `SOURCE_CONTRACT_IMPLEMENTED_QA_PENDING`; `Q4_OWNER_DECISION=HOLD_REAL_EXECUTION`, `A_I2=HOLD`, `NO_MODEL · NO_PRIVATE_BYTES · NO_GPU · NO_SCIENCE · NO_NEW_TEST`.  
**Trục phát triển:** baseline GPT có thể tái lập rồi cải thiện dữ liệu/compute/objective/capacity và ứng dụng, **không phụ thuộc Claude PR #41**; Small-4M chỉ là baseline đầu.

## 1. Phân định mối nối đã có và code mới

| Thành phần | Bằng chứng đã có | Thay đổi mới trong OnePack | Chưa được chứng minh |
|---|---|---|---|
| P02 và T4 science | P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; T4 A2 trainer `76c4d0155cd0736919f41682f240b47ad3d7c428` có schema `ttm.t4.science.checkpoint.v1`, READY-last | `src/ttm_real_baseline/typed_admission.py`: kiểm tra *khai báo* config, READY, science-lock, checkpoint SHA, train-pack SHA | **Không** mở/kiểm tensor, optimizer, RNG, model/weights hay bytes trên host |
| B synthetic E2E | PR39 B prepare→train→resume→eval→sample PASS Windows/Linux; PR42 E0 exact source graph PASS | Giữ nguyên `src/ttm_track_b/scaffold.py`, không gọi loader thực | Không suy B byte-identity = T4 BPE; không tuyên bố T4 real chạy |
| T4 tokenizer và pack | T4 BPE2048 `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`, pack builder `cdce219f2a2df27e25579f069238d4327c1d7d91` | Phân biệt **ba miền SHA**: tệp BPE raw, BPE internal manifest, TRAIN/VAL NPZ; yêu cầu quan hệ pack ↔ tokenizer ↔ checkpoint | Chưa truy xuất actual BPE, NPZ, file checkpoint từ owner; không xác nhận license/split |
| B legacy adapter | `read_historical_checkpoint(..., tokenizer_sha)` trong source `0d76d764097cd838f3fef9cb16c9da11ff778bb9` | Cấm dùng loader cũ như chứng cứ tương thích: nhánh T4 so `tokenizer_sha` với `train_pack_sha256`, một **domain mismatch**; viết typed admission độc lập, không sửa source lịch sử | B adapter cho real T4 chưa được triển khai/QA thực |
| A I1 | Frozen scorer/evidence tại `ec197b5f...` / `e3e1c802...` đã `I1_PASS_SCOPED` | Chỉ tái sử dụng yêu cầu full-vocab goldblind/negative cho source score contract, **không đọc A test/fixture** | I2 thật và output mới vẫn HOLD |
| C M4 | C registry blob `364a15d305b71e0c236a27409430f1e27e14aa70` + contract rights/splits/byte mask `PASS_DESIGN_SCOPED` | `src/ttm_real_baseline/byte_eval_contract.py` tính số học `sum(text-target NLL nats)/(ln(2) × exact raw text bytes)`, từ fixture UTF-8 tổng hợp, EOS 256 loại khỏi cả tử/mẫu | Chưa chứng minh NLL từ full-vocab logits, token→UTF8 span là thật, gold và fresh heldout |
| B/C v2 synthetic SFT | BC 7-file synthetic bridge PASS | T4 ID 257–262 là **merges TEXT**, không phải BC-v2 structural PAD/BOS/SYS/USER/ASSIST/EOT. Byte scorer xử lý token ID 262 TEXT như bình thường; chặn direct alias | External role/byte sidecar và real SFT `NOT_IMPLEMENTED` |

### Danh tính checkpoint: cố định hai loại hash KHÔNG ĐƯỢC LẪN

```text
[T4 TRAIN-only BPE]
    file_sha256 -------------------------> T4 pack.t1_bpe_file_sha256
    manifest_sha256 ---------------------> T4 pack.t1_bpe_internal_sha256
    token_merges_sha256       [riêng, có bằng chứng internal tokenizer]

[T4 private TRAIN/VAL pack]
    npz_sha256 --------------------------> T4 READY.train_pack_sha256
                \----------------------> T4 checkpoint.header.train_pack_sha256

[T4 checkpoint]
    checkpoint.pt file SHA256 ----------> READY.sha256
    science_lock_sha256 ----------------> READY.science_lock_sha256
    model config/P02 Git blob ----------> exact T4 source config
```

**Bằng chứng nguồn:** T4 `checkpoint_payload` có `model`, `optimizer`, `scheduler`, `sampler_state`, RNG và `science_lock_sha256`; READY có `checkpoint.pt`, sha, bytes và pack hash. T4 pack có `t1_bpe_file_sha256`, `t1_bpe_internal_sha256`, `npz_sha256`. Bộ kiểm chứng mới chỉ kiểm **khai báo quan hệ**, không xác minh chính các byte private hoặc một chữ ký owner, nên trạng thái thành công của hàm phải luôn là `PASS_DECLARED_SOURCE_RELATIONSHIPS_ONLY` và `authorizes_checkpoint_or_data_read=false`.

**Quan trọng:** cùng một chuỗi hash tình cờ được đưa vào nhiều trường không phải chứng cứ quan hệ đúng. Chỉ byte readback đúng miền trên máy được phép, schema chính xác, atomic/custody và independent QA mới cho phép nâng R3.

## 2. Hợp đồng phép đo A/C: byte-domain không phải token-domain

`byte_eval_contract.arithmetic_bpb(raw_scored_utf8, t4_rows)` là bộ kiểm thử **số học thuần** từ các gold NLL nats khai báo trên giả lập; nó không chạy scorer của Agent A và không nạp mô hình.

- Chỉ đếm **TEXT target spans** [start,end) không trùng, liên tục, phủ kín *exact scored raw UTF-8*. Byte sequences có thể chia tại vị trí giữa một codepoint UTF-8, nhưng dữ liệu toàn phần phải decode hợp lệ.
- `EOS_ID=256` không có raw text byte và không đóng góp NLL vào `val_bpb`. Prompt, cấu trúc EOT/PAD và SFT stop loss **không được nhập** vào C primary byte metric.
- Các T4 token 257–262 là BPE merge TEXT và có thể mang nhiều byte; tuyệt đối không tái diễn giải chúng thành BC-v2 specials.
- Kết quả chỉ là `PASS_SYNTHETIC_ARITHMETIC_ONLY`: giá trị `full_vocab_nll_provenance=UNVERIFIED_EXTERNAL_A_SCORER_REQUIRED`, `raw_byte_span_authenticity=UNVERIFIED_REAL_SOURCE_REQUIRED`. **Không dùng số từ bài test làm chất lượng mô hình thực**.
- Bản contract đơn giản hiện chỉ hỗ trợ **evaluation of fully scored text spans** sau khi external layer đã chọn vùng chấm. Cần một bộ truy vết source→BPE→score mask/offset độc lập để dùng real checkpoint và dataset, kể cả special handling EOT/EOS; nếu không có, gate `HOLD_BYTE_DENOM`.

## 3. Một ma trận admission R0–R8, không sinh micro-permit

| Gate | Reuse/bằng chứng đã đạt | Điều kiện còn thiếu đối với lượt real T4 | Hiện trạng |
|---|---|---|---|
| **R0** · source dependency | PR42 E0 source QA 17/17 Win & 17/17 Linux, B/C/C PR39 synthetic PASS, A I1 PASS, C M4 PASS design | New typed source/contract QA phải PASS exact branch SHA | `CANDIDATE_QA_PENDING` |
| **R1** · measurement & gold | A I1 goldblind scorer QA đã PASS | Actual checkpoint logits, independent gold/rater, fresh paired negative controls | `HOLD_REAL_GOLD` |
| **R2** · rights & split | C rights-by-operation, family split và raw SHA contract PASS design | Authenticated license/allowed operation, private TRAIN/VAL/fresh heldout byte custody, PII/copyright review | `HOLD_RIGHTS_AND_FAMILY` |
| **R3** · checkpoint tokenizer | T4 P02 source/strict template, old T4 checkpoint schema và separate SHA-domain contract code | Actual weights sha, verified BPE file/internal SHA, T4 READY header/data readback, model state tensor structure, fresh native adapter QA | `HOLD_REAL_WEIGHTS_AND_BYTES` |
| **R4** · compute/resource | B M3 synthetic and historical T4 source/capacity design | Actual resource bounds CPU/RAM/VRAM, strict Windows/GPU watchdog/time, measured throughput, atomic no-overwrite | `HOLD_NATIVE_RESOURCE` |
| **R5** · A release | A V4 design accepted, I1 scoped PASS | Trusted Ed25519 signer/epoch, Windows handle ancestry, atomic receipt, global one-shot ledger/native negative+positive QA | `HOLD_A_NATIVE_RELEASE` |
| **R6** · prereg | C science design aligned 37/26/14 | Exact real question/arms, dataset/byte denominator/gold/thresholds, TEST reader-zero, independent freeze | `HOLD_PREREG` |
| **R7** · integrated independent QA | Existing independent scoped source/synthetic QA preserved | Native real candidate + data rights and scorer source exact QA, no reusing old tests as new science | `HOLD_REAL_QA` |
| **R8** · owner decision | Owner authorized **this design/source candidate only** | Evidence R0–R7 in one packet then exact owner GO/HOLD for requested real execution | `HOLD_OWNER_Q4` |

**Scope nuance:** A-I2 không phải cổng bắt buộc cho mọi thay đổi nguồn. Nếu một hành động dùng đúng lượt chẩn đoán Q001 I2 đã khóa thì phải xử lý R5/A-I2, no replay/no new TEST. Nếu là nghiên cứu pretraining mới, bắt buộc có gate khoa học tương ứng; **không tái sử dụng release I2 như giấy phép tổng quát**.

**Một quyết định Q4 duy nhất cho real vertical slice:** `HOLD_Q4_REAL_VERTICAL_SLICE_UNTIL_R0_R8_EXACT_EVIDENCE`. Owner không được suy ra GO từ việc mã typed admission PASS, từ run source-only CI hay từ một SHA do ứng viên tự khai báo.

## 4. Candidate và QA kỹ thuật thực sự trong OnePack

Nhánh `implementation/ttm-pm-real-gpt-vertical-slice-admission-contract-20261117` từ `b2e97dd3...`, **không thay đổi** `src/p02`, P03/P04, B Core, B/C, C, A hoặc T4 frozen source. Các tệp mới:

1. `src/ttm_real_baseline/typed_admission.py`: typed SHA-domain/source relationship validator, strict schema/config, fail-closed owner HOLD.
2. `src/ttm_real_baseline/byte_eval_contract.py`: C UTF-8 bpb arithmetic bridge for fake values; EOS exclusion, T4-BPE no alias, rejected invalid bytes/spans/NLL.
3. `tests/ttm_real_baseline/test_t4_contract_source_only.py`: 25 unittest gồm negative tampering, owner forged GO, alias, schema, byte denominators; dùng synthetic-only fixture generated in memory.
4. `.github/workflows/ttm-real-baseline-source-contract-py312.yml`: Python3.12 Windows/Linux stdlib source-only QA, không pip/Torch/dataset.
5. `artifacts/ttm-real-baseline/TTM_PM_T4_ABC_R0_R8_ADMISSION_LEDGER_20261117.json`: ledger scope and exact source pins, current HOLD, no GO.
6. Tài liệu OnePack này + receipt QA sau khi có CI.

### Tiêu chí chấp nhận candidate kỹ thuật

- [ ] CI Windows/Linux Python 3.12 **24/24** test mỗi hệ, 0 skip, 0 model/weight/real dataset load.
- [ ] Negative tests thử sai BPE file/internal SHA, pack vs checkpoint SHA, ready file bytes, checkpoint schema/config, code provenance, BC alias, UTF-8 và forged authority; không khai PASS thực nghiệm.
- [ ] QA source kiểm lại Git blob P02/T4/B/C đã có, giữ bất biến và không sửa A/B/C đã PASS.
- [ ] Git diff chỉ tệp mới kể trên; không sửa `lineage.md`, `main`, PR41 Claude hay Question Gate.
- [ ] Reviewer nêu rõ source-only PASS **không** phải actual checkpoint readback. Không giải phóng Q4, I2, SFT.

**Bước thực hiện tiếp theo — duy nhất sau khi source QA/PR đã được phân xử:** PM đánh giá ứng viên này để merge **đúng phạm vi source/QA** nếu PASS; chuẩn bị **một** owner R0–R8 witness cho real T4 action (nếu có exact checkpoint/corpus private và quyền), không tạo chuỗi micro-permit. Nếu owner chưa có quyền hoặc byte gốc, tiếp tục HOLD real runtime nhưng hướng phát triển TTM vẫn mở.

**Trạng thái khóa hiện tại:** `T4_TYPED_ADAPTER_DESIGN_SOURCE_ONLY · UTF8_BPB_ARITHMETIC_SYNTHETIC_ONLY · R0_CANDIDATE_PENDING_QA · R1_R8_HOLD · A_I2_HOLD · REAL_MODEL_NOT_EXECUTED · MAIN_UNCHANGED · NO_NEW_SCIENCE`.
