# TTM PM — GPT End-to-End Baseline × ABC integrated source and delivery OnePack

**Operation:** `TTM_PM_GPT_END_TO_END_BASELINE_INTEGRATION_AND_ABC_DELIVERABLE_GAP_CLOSURE_ONEPACK`  
**Ngày:** 17/11/2026 · **Trạng thái:** `SOURCE_INTEGRATION_CANDIDATE_REVIEW`; không là science/I2/SFT GO.  
**Source of truth:** `minhtri22/TokenToModel-Lab` `main=e102d2ed3c885756b6e4354189ccbece36b75eb8`.  
**Phạm vi:** một lần tích hợp các giao diện source và evidence đã đạt, không mở lại A/B/C, không chạy model, checkpoint, corpus, huấn luyện hay TEST; chỉ thực hiện QA nguồn thuần Python 3.12 và đối chiếu kỹ thuật trên GitHub.  
**Đích dài hạn:** GPT huấn luyện/tái lập/đo năng lực thật → so sánh dữ liệu/compute/objective/capacity → SFT/post-training → inference/serving → thương mại hóa; **Small-4M là baseline lịch sử, không phải giới hạn TTM**.

## 1. Quyết định thực tế: KHÔNG VIẾT LẠI TRAINER

Đã có **một chu trình end-to-end kỹ thuật synthetic** trên `main`. Track B CLI `src/ttm_track_b/cli.py` dùng `scaffold.py` và P02/P03, có lệnh `prepare → train → resume → evaluate → sample`, checkpoint lưu mới bằng SHA và READY receipt. Test `tests/test_track_b_scaffold.py::test_19_cli_end_to_end_and_no_overwrite` bảo vệ đường nối đó; `.github/workflows/track-b-b0b1-py312.yml` chạy lệnh thực trên **Python 3.12 Linux và PowerShell 5.1 Windows**.

**QA cũ đã có và tái sử dụng:** Owner-approved PR #39 merge đúng 76 tệp B/BC/C, commit `5dd6d4d5af169b0f707f872184c47ce5443513f3`; Track B workflow [#44043606469](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/44043606469), B/C [#44043606388](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/44043606388), C [#44043606424](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/44043606424), tổng **6/6 job PASS**. PM không chạy lại trainer hay checkpoint, không thay đổi source dưới `src/`/`tools/pilot_t4/` và không suy ra model thật PASS.

**Định nghĩa cẩn trọng:** `E1_SYNTHETIC_END_TO_END_PASS_SCOPED` = có một đường kỹ thuật từ fixture nhân tạo tới checkpoint synthetic rồi metric/sample. **Không** bằng `E2_REAL_T4_BASELINE_READY`, `E3_REAL_MODEL_QUALITY_PASS`, `E5_REAL_SFT_PASS`.

## 2. Source graph bất biến được PM xây dựng

Artifact máy đọc: `artifacts/ttm-gpt-e2e/TTM_PM_GPT_E2E_ABC_EXACT_SOURCE_INTEGRATION_MANIFEST_20261117.json`. Gồm **18 node code/config/tests/QA trên exact main, 2 nguồn A nằm ngoài main, 12 cạnh interface (seams)**, từng node có Git blob SHA1. PM không sửa mã đã merge, không nhập nguồn A PR28/33 HOLD vào main.

```text
         P01 BPE T4 (TRAIN-only)            C — rights / family splits / gold
             |                         [design PASS, real source HOLD]
         T4 real TRAIN/VAL pack -------------------------+
             | [rights / raw bytes HOLD]                 |
             v                                            v
P02 GPT Core  ──> P03 fixed-batch loop ──> P04 weights-only checkpoint
   |               [no train resume]       [no optimizer]
   |
   +──> B synthetic scaffold ──> B CLI
             |                    prepare → train → resume → evaluate → sample
             |                    EXISTING synthetic QA PASS (not run here)
             |
             +──> BC-v2 synthetic data/interface
                     [codec direct-to-T4 incompatible]
                            |
                            v
                     A scorer (external PASS I1) <─> C val_bpb contract
                     [one-token nats != bits/UTF8-byte, real validation HOLD]
```

### Giao diện nguồn và vấn đề còn thực sự mở

| Seam | Có mã và chứng cứ | Khoảng trống cần giải quyết trước khoa học thật |
|---|---|---|
| **Dữ liệu → Tokenizer** | `t4_data_pack.py`, T4 TRAIN-only BPE2048; B synthetic byte identity riêng | Quyền dữ liệu, chia family TRAIN/VAL/FRESH, source SHA và byte thật vẫn **chưa verified trong lượt này** |
| **Tokenizer → P02** | P02 `GPT(P02Config)`, config T4 `2048/256/256/4/4`, tied embedding | Exact original TRAIN BPE manifest / real T4 data pack / checkpoint identity cùng phạm vi chưa readback |
| **P02 → P03** | P03 `train_fixed_batch`, cosine LR, AdamW, accumulation có test | P03 fixed-batch source không cung cấp optimizer/scheduler/sampler checkpoint; P02 `forward(tokens,targets)` dùng CE mặc định **không ignore -100** |
| **P02 → B scaffold/CLI** | B dùng nguồn P02 và P03 schedule, có synthetic train/strict resume, VAL, sampling qua CLI, Win/Linux CI PASS | B synthetic tokenizer là **byte-identity**, không phải T4 BPE; không phải real data or real benchmark |
| **P04 checkpoint** | `save_checkpoint_new` / `load_checkpoint_verified`, weights-only, strict model keys, SHA, synthetic heldout | P04 schema **không** chứa optimizer/scheduler/RNG/sampler để resume training; không đánh đồng checkpoint B/T4/P04 |
| **B ↔ T4 checkpoint** | B có `read_historical_checkpoint` source adapter, T4 trainer có READY-last checksum/step | **HOLD** actual real weights and strict owner-host readback. Đặc biệt nhánh T4 của adapter B dùng tham số mang tên `tokenizer_sha` để so với `train_pack_sha256`, là **lẫn tên miền hash trong API**; cần tách typed `train_pack_sha` và BPE manifest pin trước khi chứng nhận adapter |
| **B ↔ BC SFT** | BC v2 7-file canonical byte bundle, source-only F05/F06 QA PASS | `weights=NOT_CREATED`; T4 BPE IDs `257..2047` trùng BC special `257..262` → **INCOMPATIBLE_DIRECT**, không alias |
| **Model → A/C evaluator** | A I1 gold-blind full-vocab NLL một token (nats) PASS scorer; C contract `val_bpb` thiết kế PASS | B `bpb_excluding_first_byte_and_eos` đang đếm **mỗi non-EOS byte-identity target = một byte**; không thể tái sử dụng cho T4 BPE nhiều byte nếu không có exact token→UTF8 span map; gold/rater/fresh VAL chưa qualified |
| **Output → serving** | P05/P06 reference CPU/KV có lịch sử scoped QA; `generate_tokens` P04 và `b.sample` synthetic | Không có runtime sản phẩm đã đủ QA an toàn/tải, kiến trúc model scale, model card/ops; P07/P08 paused |

**Đây là một gap quan trọng PM mới ghi rõ:** không chỉ là "T4-vs-BC tokenizer alias", mà ngay API `read_historical_checkpoint` của B cũng phải phân biệt rõ **hash toàn bộ train pack** với **hash tokenizer manifest**. Không sửa hoặc chạy adapter này trong operation nguồn hiện tại. Mọi thay đổi có thể ảnh hưởng checksum contract đều phải có version và negative QA.

## 3. Phân loại điều kiện đã đạt, còn thiếu và ý nghĩa

| Gate | Quyết định PM | Chứng cứ dùng / điều kiện còn thiếu |
|---|---|---|
| **E0 — ABC exact source graph** | `CANDIDATE_SOURCE_QA` trước CI của PR review | 18 exact Git blob nodes, 2 external A anchors, 12 edges, 14 negative/source tests Win/Linux; không import Torch |
| **E1 — Synthetic GPT E2E** | **`PASS_SCOPED` (đã có)** | Track B PR39 CI prepare/train/3→8 resume/eval/sample trên 2 OS; không cần chạy lại |
| **E2 — Real T4 checkpoint + data custody** | `HOLD_Q4_REAL_BYTES` | Owner-authorized exact raw rights/split/checkpoint/optimizer/tokenizer, no untrusted pickle, strict SHA and atomic custody; chưa đủ |
| **E3 — Real baseline evaluation** | `HOLD_E2_AND_R1_R2_R3` | A full-vocab, C valid UTF-8 text target byte denominator, valid gold, negative controls, fresh heldout and adversarial split QA |
| **E4 — Improvement data × compute × objective × capacity** | `NOT_EXECUTED` | Sau E3 mới tiền đăng ký giả thuyết cải thiện và measured FLOPs; không lấy Claude 44M làm hạn mức bắt buộc |
| **E5 — Real SFT** | `HOLD_REAL_DATA_CODEC_WEIGHTS` | T4/B-C versioned token policy, safe checkpoint, rights, instruction data, valid masked CE and holdout |
| **E6 — Serving / scale / product** | `DEFER` | Chất lượng đã đo, inference QA, an toàn, chi phí phục vụ, bản quyền, model card, product benchmark |

**Không coi E0–E6 là bảy giấy phép.** Đó là bảy cột đánh giá tiến độ cho **một kiến trúc và một tuyến phát triển**; chỉ khi có hành động runtime/thí nghiệm cụ thể mới hỏi một quyết định owner GO/HOLD theo Question Gate có hiệu lực. E1 không phụ thuộc STEP0 của Claude hay việc merge PR #41.

## 4. Trách nhiệm A/B/C sau khi source đã merge

- **PM**: chủ sở hữu graph, runtime integration specification, source pins, công việc nối seams, final combined QA, bản chất science/engineering và source-of-truth main. Không tạo ba roadmap độc lập.
- **A — Measurement**: bảo đảm `a_gold_nll` full-vocab goldblind/negative; định nghĩa metric parity trên real BPE và quyền phát hành an toàn; **I1 PASS scoped giữ nguyên, I2 HOLD**.
- **B — Model engineering**: tái sử dụng B scaffold/CLI đã PASS; thiết kế typed adapter từ historical T4 real checkpoint/BPE/optimizer source sang runtime mới, tài nguyên được chặn và strict per-artifact readback; không dùng P04 model-only như resume snapshot.
- **C — Data and science**: quyền nguồn theo hành động, dữ liệu TRAIN/VAL/heldout mới, family overlap, byte-span deterministic, gold/measure/prereg và equal-compute; chưa cấp science claim từ synthetic E1.

**Các thành phần kỹ thuật đã đạt không bị chạy lại.** Reviewer chỉ cần xác minh **source exact** của các artifact tái sử dụng, thực hiện kiểm thử *mối nối mới* khi có patch thực sự, và đóng một chứng cứ tích hợp. Nếu node/edge chưa được chứng nhận, ghi `HOLD` rõ, không tạo micro-permit.

## 5. Ứng viên tích hợp và QA được thực hiện trong operation này

**Ứng viên:** nhánh `review/ttm-pm-gpt-e2e-abc-source-integration-20261117` từ `main` `e102d2ed...`, giữ nguyên `src/p02`, `src/p03`, `src/p04`, `src/ttm_track_b`, `tools/pilot_t4`, code C/BC, A external. Chỉ bổ sung:
1. Source manifest 18 node/12 edges + evidence R0/E0–E6;
2. OnePack kiến trúc và PM gap list này;
3. Bộ QA PM chạy bằng **stdlib Python 3.12** đọc Git blobs (không đọc checkout CRLF, không import model/torch), negative tamper/path traversal, AST parse, API signatures, CRC/metric/codec contradictions;
4. Workflow QA **Windows+Linux**, không pip install, không chạy checkpoint, dữ liệu thật, GPU, khoa học hoặc TEST;
5. Readback QA receipt lưu trên nhánh review sau khi workflow kết thúc.

**Chấp nhận E0:** đúng 18 blob đã pin; 12 seams không sai chủ; A I1/A V4 chỉ là external refs, **không có code A bị nhập ngầm**; B synthetic CI từ PR39 PASS đã có; P03/P04 contract deficiencies được đánh dấu đúng; T4 vs BC token collision và bpb byte denominator được nhận diện; không có model runtime execution trong CI; cả hai OS PASS, Git diff chỉ docs/QA.

**Điều kiện tuyệt đối chưa cấp trong operation:** mọi `torch.load` real, historical T4 checkpoint reader, real corpus access, new synthetic/model training (kể cả run thử ngoài permission), fresh TEST/Final24, owner science GO, merge main. Không tự chỉnh policy Question-First hoặc `lineage.md`.

## 6. Tiếp tục TTM như thế nào sau ứng viên E0?

**Một hướng thực thi kế tiếp hợp lý** sau khi được owner đánh giá source-only E0 là **"Unified baseline vertical slice" (mối nối thật tối thiểu)**: B dùng cấu hình có version và strict checkpoint/pack/byte tokenizer manifests; C khóa dữ liệu dùng hợp lệ và phép đo, A kiểm tra gold-blind/NLL/bytes/heldout; PM kiểm toán một lần trên exact executable candidate. Nhánh engineering/synthetic cần nằm đúng phạm vi Question Gate đã có; model / original checkpoint / thực nghiệm thật chỉ mở khi Q4 và bằng chứng R0–R8 áp dụng đủ.

Nếu có model được chứng nhận, dự án mới đo được **Small-4M yếu vì đâu**; sau đó thử các can thiệp data/compute/objective/capacity có đối chứng ở nhiều quy mô. Model lớn hơn (P09), SFT/posttraining (P10), inference/serving (P11), phát hành (P12) là mục tiêu tiếp theo theo đúng Project Charter, không phải theo kế hoạch Claude.

**Kết luận PM sau kiểm toán nguồn:** `EXISTING_B_SYNTHETIC_E2E_PASS_REUSED · EXACT_SOURCE_GRAPH_CANDIDATE_READY_FOR_QA · REAL_T4_RUNTIME_HOLD · REAL_DATA_RIGHTS_HOLD · A_I2_HOLD · REAL_SFT_HOLD · NO_NEW_SCIENCE`.
