# Track B — B0/B1 hợp đồng và hướng dẫn chạy (2026-11-16)

**Operation:** B_B0_B1_CONTRACTS_T4_ADAPTER_AND_SYNTHETIC_E2E_SCAFFOLD
**Branch:** research/ttm-track-b-gpt-core-20261116
**Frozen main:** f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3
**Scope:** synthetic engineering only, không thực nghiệm TinyStories/Small-4M, không công bố weights hoặc merge main.

## Source pins

| File | Frozen Git blob SHA-1 | Interface |
|---|---|---|
| src/p02/transformer_core.py | 9762343e06cf800b50574c2871ae1ed58537fb18 | Original GPT; unchanged |
| src/p03/train_loop.py | 80dc004a864085e7ae2e1ab4942d1cb2d84ce742 | TrainConfig and scheduled_lr |
| src/p04/eval_checkpoints.py | f047fcd33d871d26f789f0008611c04af4579bc4 | P04 checkpoint schema |
| tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py | 76c4d0155cd0736919f41682f240b47ad3d7c428 | T4 AdamW, sampler, resume |
| tools/pilot_t4/integrated/t4_data_pack.py | cdce219f2a2df27e25579f069238d4327c1d7d91 | T4 next-token windows/EOS |
| tools/pilot_t4/integrated/t4_capacity_smoke.py | c9a6f256ba975228683ee7de2a1090e649110e97 | T4 actual model config |

PR30 được đọc ở commit 229f9dedfd82c0544cd637f8180d50017fc16777; backlog RF-04..08/12/13/21 chỉ là tài liệu phụ thuộc, không được đánh dấu đóng. nanochat 92d63d4e8bb4df75c3b71618f31ddde2378b2bcd là design comparison, không tự sao chép H100 stack.

## Contract inventory — B0

1. **Tokenizer:** Synthetic dùng byte IDs 0..255, EOS=256, vocab=2048, không dùng IDs 257..2047; định danh SYNTHETIC_BYTE_IDENTITY_V1_NOT_T4_BPE khóa SHA256. Đây không phải P01 WP30 BPE hay T4 T1 BPE; tuyệt đối không tự ghép checkpoint T4. Không có BOS, input padding ID=0 chỉ hợp lệ khi label=-100; roundtrip byte UTF-8.
2. **Data/split:** 6 TRAIN groups, 3 VAL groups, toàn byte giả lập; không có TEST. Group ID, SHA256 bytes nguồn, byte count, window ordinal, EOS, target coverage, split/group overlap và source-byte reconstruction phải xác thực. Không commit reversible private token packs.
3. **Training:** Import original P02 GPT và P03 TrainConfig/scheduled_lr; dùng AdamW betas=(.9,.95), eps=1e-8; loss=F.cross_entropy(logits.float(), targets, ignore_index=-100, reduction=sum)/valid_target_count. P02 forward loss mặc định không xử lý ignore nên adapter chỉ dùng logits. Accumulation được chuẩn hóa bằng tổng nhãn toàn optimizer step, không trung bình từng microbatch.
4. **Resume:** Lưu exact step/config hash/data hash, model, AdamW optimizer, LambdaLR scheduler, sampler RNG, Python RNG, Torch CPU RNG; torch.load(weights_only=True), strict=True, SHA trước load; READY-last và no-overwrite. Trên cùng runtime CPU FP32, so sánh 8 bước liên tục và 3+5 resume bitwise; sai số gradient accumulation predeclared max_abs 2e-6. Không khẳng định CUDA/AMP resume.
5. **Historical checkpoint schemas:** P04 ttm.p04.model_checkpoint.v1 dùng state_dict và bpe_merges_sha256. T4 ttm.t4.science.checkpoint.v1 dùng model, science_lock_sha256, train_pack_sha256 và p02_git_blob. Chỉ đọc dưới root allowlisted, no symlink, SHA trước restricted load, kiểm config/keys/shapes/dtypes/finite, load strict. T4 đúng config 2048/256/256/4/4 LayerNorm/GELU, 3,749,376 unique params. Trong T4 adapter, đối số tokenizer_sha có nghĩa expected_train_pack_sha; phải QA tokenizer thật qua manifest T1/T4 riêng, không suy diễn từ pack SHA. Bài test sử dụng fake checkpoint theo schema, không load weight lịch sử.
6. **Eval:** Full-vocab 2048 token NLL tính theo tổng valid targets bao gồm EOS; byte-bpb = tổng NLL trên các byte được dự đoán / [ln(2) × số byte UTF-8 được chấm]. Byte đầu mỗi story không có BOS nên loại; EOS cũng loại khỏi byte-bpb. Không lấy story-mean average. Top-1 tính trên full vocabulary, có independent target count và reuse factor; semantic metrics NOT_VALIDATED.
7. **Boundaries:** CLI chỉ ghi trong repo/_tmp/track_b_runs/<run_id>, chống symlink/path traversal; không network/child processes/silent retries, steps<=64, width<=64, layers<=2, windows<=16, cap thời gian kiểm giữa bước <=600 giây. Chưa có Windows Job Object hard committed memory cap.

## PowerShell 5.1 — Python 3.12

~~~powershell
Set-Location 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
& $Py -c "import sys,torch; assert sys.version_info[:2] == (3,12); print(sys.version); print(torch.__version__)"
if ($LASTEXITCODE -ne 0) { throw 'PY312_PREFLIGHT_BLOCKED' }
$Cfg = 'configs/ttm/track_b_synthetic_smoke.json'
$Out = '_tmp/track_b_runs/track_b_b0b1_one_shot_20261116'
& $Py -m unittest discover -s tests -p 'test_track_b_scaffold.py' -v
if ($LASTEXITCODE -ne 0) { throw 'TRACK_B_TEST_HOLD' }
& $Py -m src.ttm_track_b.cli prepare --config $Cfg --out $Out
if ($LASTEXITCODE -ne 0) { throw 'TRACK_B_PREPARE_HOLD' }
& $Py -m src.ttm_track_b.cli train --config $Cfg --out $Out --stop-after 3
if ($LASTEXITCODE -ne 0) { throw 'TRACK_B_PARTIAL_HOLD' }
& $Py -m src.ttm_track_b.cli train --config $Cfg --out $Out --resume-from-step 3
if ($LASTEXITCODE -ne 0) { throw 'TRACK_B_RESUME_HOLD' }
& $Py -m src.ttm_track_b.cli evaluate --config $Cfg --out $Out
if ($LASTEXITCODE -ne 0) { throw 'TRACK_B_EVAL_HOLD' }
& $Py -m src.ttm_track_b.cli sample --config $Cfg --out $Out
if ($LASTEXITCODE -ne 0) { throw 'TRACK_B_SAMPLE_HOLD' }
~~~

Out phải là tên chưa tồn tại. Không xóa evidence để chạy lại. Đây là hướng dẫn native, chưa phải receipt Python3.12/Windows đã chạy.

## Gates

| Gate | Tạm trạng | Evidence/limitation |
|---|---|---|
| B-G0 | PASS_SOURCE_INVENTORY | Handoff B, PR30/34, source pins |
| B-G1 | PASS_AUTHOR_REFERENCE | Synthetic tokenizer/split/shift/EOS/mask và negative |
| B-G2 | PASS_AUTHOR_REFERENCE | Synthetic overfit/gradient/schedule trên Linux với P02/P03 semantic copies |
| B-G3 | PASS_AUTHOR_REFERENCE | Synthetic P04/T4 adapters và resume parity; chưa mở checkpoint lịch sử |
| B-G4 | PASS_AUTHOR_REFERENCE | Full-vocab NLL, byte-bpb oracle, deterministic sample |
| B-G5 | HOLD_WINDOWS_PY312 | Windows native Py3.12/hard resource NOT_EXECUTED |
| B-G6 | HOLD_INDEPENDENT | Exact HEAD distinct independent QA NOT_EXECUTED |

Không có B_M3_PASS_ENGINEERING_BASELINE. Không kết luận cải thiện semantic. MAIN_UNCHANGED, NO_SCIENCE, NO_WEIGHT_PUBLICATION.

**Bước thực hiện tiếp theo — duy nhất:** B_B0_B1_EXACT_BRANCH_HEAD_WINDOWS_PY312_NATIVE_AND_DISTINCT_INDEPENDENT_QA_ONEPACK.
