# PM — Một phiên T4: 40 synthetic → Small-4M mới @1024 → paired VAL

**Operation:** `TTM_PM_SINGLE_SESSION_TECH40_NEW1024_HISTORIC_PAIRED_COMPARISON_ONEPACK`

**Ngày:** 17/11/2026 · **PR:** #44 · **Repository:** `minhtri22/TokenToModel-Lab` · **Base main giữ nguyên:** `59ee3f30b996405fddc087ab60102b59a021f8ea`.

## Quyết định

`GO_INTEGRATED_ONE_SESSION_SOURCE_DESIGN · Q4_REAL_TRAINING_HOLD_PENDING_EXACT_EVIDENCE`.

Thay vì hai lượt Colab tách rời, một lệnh `one-session` có thể thực hiện **A → B → C** theo đúng thứ tự:

| Giai đoạn | Hành vi | Giới hạn khẳng định |
|---|---|---|
| A · TECH40 | T4 GPT P02 **3.749.376 tham số**, 4 layers/d256/context256/vocab2048; 40 optimizer steps, mỗi bước 4.096 nhãn token uniform-random; đo worst latency/VRAM; lưu JSON | Kỹ thuật synthetic; **không phải pretraining TinyStories**, không lưu/transferred weights |
| B · NEW1024 | Tạo **đối tượng model, optimizer và RNG mới** với seed chuẩn `20261108`; train 1.024 steps × 4.096 nhãn từ pack TinyStories TRAIN đúng SHA cũ | Huấn luyện khoa học thực, nhưng chỉ sau exact Q4 tích hợp và pack/license admission |
| C · PAIRED VAL | Nạp **checkpoint gốc @1024** (SHA256 khóa) và **checkpoint mới @1024**, đánh giá cùng 256 VAL truyện, 61.122 mục tiêu BPE, paired bootstrap 2.000 | So sánh developmental VAL; không chứng minh tự động cải thiện; không mở lại TEST |

**Phân biệt:** 40 synthetic run phải dùng chính **kiến trúc Small-4M**, không còn dùng bản d128/2layers/258 byte-vocab cũ. Phần A tạo tham số ngẫu nhiên nhưng **không** chuyển bất cứ tensor/trạng thái optimizer nào sang phần B. Phần B random seed như lịch sử; nếu mọi thuật toán giống nhau thì đây là kiểm định tái lập, không phải phép chứng minh tác động kiến trúc.

## Entrypoint và đường dẫn

- Runner: `src/ttm_new_gpt_baseline/runner.py`, action `one-session`.
- Colab: `notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb`, đặt `MODE="ONE_SESSION_40_1024"` và `RUN_ID` mới dài 8–80 ký tự.
- Notebook bảo toàn `MODE="SOURCE_QA"` làm mặc định không GPU; owner tự bật session mode, không hề tự thực thi ở GitHub.
- Source P02/T4 trainer/capacity/evaluator đều ghim SHA-1 Git blob cũ; nguồn TRAIN/VAL được kiểm SHA-256 trước optimizer step đầu tiên của B. Chính checkpoint lịch sử cũng kiểm SHA-256 trước bước TRAIN.
- Theo mặc định, `SESSION_PARENT=/content/TTM_MATCHED_4M_SESSIONS`. Colab `/content` **không bền vững** khi bị reset; trước Q4 thực, nên chuyển SESSION_PARENT đến một ổ lưu trữ bền vững đã mount và có đủ dung lượng. Runner không tự mount Drive, không ghi dữ liệu riêng tư lên GitHub.
- Thư mục phiên phải là `TTM_40_1024__<run_id>`, **one-shot no-overwrite**. Run training riêng đặt tại `runs/replica_1024__<run_id>`; mỗi checkpoint lưu READY-last cùng hash metadata.

## Hành vi Q4 tích hợp

Nếu **không có** `OWNER_GO_JSON`, runner vẫn được phép A/TECH40 trên synthetic, ghi `TECHNICAL_SYNTHETIC_40.json` và `SESSION_STATUS.json` với status `TECHNICAL_40_PASS_SCIENCE_HOLD_NO_Q4`; không chạm TRAIN/VAL private, không đọc historical checkpoint, không TRAIN/COMPARE.

Nếu có một Q4 packet hợp lệ trước khi gọi notebook, runner kiểm tra **đúng source blob, recipe 1.024, SHA pack, SHA historical checkpoint, rights reference, independent review reference và ngân sách**, sau đó chạy A. Chỉ khi receipt A đạt 40/40 optimizer steps, 4.096 targets/step, ngưỡng RAM/VRAM/projection và exact hash thì runner được tiếp tục B rồi C. Không cần micro-permit giữa A/B/C. Không có định nghĩa auto-GO phát sinh từ receipt A; quyết định Q4 phải có **từ trước**.

Exact metadata schema (đây là MẪU, **KHÔNG PHẢI QUYẾT ĐỊNH GO đã được cấp**):

```json
{
  "schema": "ttm.matched_4m.integrated_q4.v1",
  "decision": "GO_CONDITIONAL_40_SYNTHETIC_1024_TRAIN_PAIRED_VAL",
  "action": "ONE_SESSION_40_THEN_1024",
  "run_id": "<8-80-character-owner-run-id>",
  "arm": "replica_1024",
  "runner_git_blob": "<runner-exact-Git-blob-SHA1-at-final-commit>",
  "original_main": "59ee3f30b996405fddc087ab60102b59a021f8ea",
  "recipe_sha256": "<canonical-sha256-of-recipe-replica_1024>",
  "private_train_val_pack_sha256": "184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913",
  "historic_left_checkpoint_sha256": "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b",
  "technical_steps": 40,
  "science_steps": 1024,
  "scored_targets_per_step": 4096,
  "gpu_seconds_cap": 5400,
  "rights_reference": "<actual-TinyStories-internal-rights-record>",
  "independent_review_reference": "<actual-independent-review-evidence>"
}
```

Lưu ý: JSON là interlock kiểm tra giá trị, **không phải chữ ký số**. Điều kiện quyền/đối chứng/nguồn và reviewer chưa được chứng minh thì Q4 vẫn HOLD.

## Output và so sánh các vấn đề Small-4M lịch sử

Mỗi session có: `SESSION_LOCK.json`, `TECHNICAL_SYNTHETIC_40.json`, `runs/replica_1024__*/RUN_LOCK.json`, checkpoints 256/512/768/1024, `FINAL.json`, `PAIRED_HISTORICAL_VAL_1024.json`, `SESSION_STATUS.json`. SHA-256 trong READY/biên nhận; source GitHub chỉ lưu **metadata không nhạy cảm**, không nộp NPZ hoặc checkpoint riêng tư.

Phép đo hiện có tính full-vocab BPE2048 NLL/token, chênh lệch ghép cặp theo truyện, CI bootstrap, wall/VRAM kỹ thuật. **Không tự phát minh** kết quả cải thiện narrative, task-following, OOD, repetition, EOS, rubric 24/32 hay benchmark chưa được cung cấp. Những khuyết điểm được ghi nhận từ Small-4M phải được đưa vào một *diagnostic failure suite* đã khóa, có thể đánh giá trên hai checkpoint sau đó, tách biệt khỏi nguồn TEST lịch sử và không suy diễn từ NLL.

## QA scope, quyết định hiện tại

- Source-only GitHub Actions Win/Linux Python3.12: source tests + adverse no-Q4/no-private-data orchestration tests (không GPU).
- Native CPU synthetic QA: serialization/READY-last/corruption and exact full P02 3.749.376-param small-target resume parity. **Không** phải Colab FP16 40-step test.
- **Còn thiếu:** hiện trường T4 40 bước, phân xử nguồn TinyStories/rights của lượt mới, độc lập QA reviewer, huấn luyện 1.024 và so sánh checkpoint thật. Không có kết quả khoa học mới.
- `main`, `lineage.md`, lịch sử Small-4M và TEST không thay đổi. PR #44 Draft, Q4 HOLD.

**Bước thực hiện tiếp theo — duy nhất:** đối chiếu exact HEAD QA + source pin; với one-session notebook đã khóa, PM đưa ra **một** Q4 tích hợp sau khi quyền nguồn và chứng cứ reviewer được xác minh, rồi owner mới chọn MODE ONE_SESSION_40_1024 trên Python3.12/T4. Nếu Q4 HOLD, có thể làm TECH40 synthetic mà không thực thi khoa học.
