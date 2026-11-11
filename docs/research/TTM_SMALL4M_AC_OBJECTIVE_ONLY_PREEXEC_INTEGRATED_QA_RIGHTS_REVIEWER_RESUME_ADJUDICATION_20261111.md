# TTM Small4M — A/C Objective-only: tiền kiểm tích hợp nguồn, Resume, quyền dữ liệu và chấm mù

**Ngày:** 2026-11-11 · **Operation:** `TTM_SMALL4M_A_VS_C_OBJECTIVE_ONLY_PREEXEC_INTEGRATED_SOURCE_QA_RIGHTS_REVIEWER_RESUME_GATE`

**Phán quyết:** **`NO_GO_NOW_PREEXEC_HOLD`**, không phải FAIL khoa học. **Không** huấn luyện TTM, không inference TTM, không đọc TEST/Q1/Q2/FRESH12/OOD256 đã tiêu thụ, không tạo CLAIM hay science run. Không thay `main`, `lineage.md`, checkpoint hoặc TRAIN/VAL pack; không mở nhánh mới.

## 1. Nguồn đối chứng đã bảo toàn

Trên chính nhánh `research/ttm-small4m-prompt-conditioning-objective-design-20261110`, giữ nguyên candidate gốc 2×2 và các bằng chứng:
- Thiết kế 2×2: `artifacts/qa/ttm-small4m-prompt-conditioning/TTM_SMALL4M_EQUAL_BUDGET_2X2_DESIGN_CANDIDATE_20261110.json` và `docs/research/TTM_SMALL4M_PROMPT_CONDITIONING_TRAIN_OBJECTIVE_EQUAL_BUDGET_2X2_DESIGN_20261110.md`.
- Trạng thái owner `HOLD_FREE_T4_NOT_AUTHORIZED`: `artifacts/qa/ttm-small4m-prompt-conditioning/real_readiness/OWNER_SINGLE_GO_HOLD_DECISION_20261110.json`; 42/42 CPU QA và 34/34 kiểm toán độc lập chỉ là kết quả lịch sử, **không** được trình bày là QA runner A/C mới.
- Parent T4 checkpoint bước 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; TRAIN/VAL pack `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; P02 source SHA `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`. Các SHA này được **tham chiếu từ bằng chứng trước**, không tải lại checkpoint/private pack trong lượt này.

## 2. Triển khai mã A/C (không sửa runner lịch sử 4 arm)

Để bảo toàn nguồn gốc 2×2, giữ file `ttm_2x2_colab_runner_candidate.py` làm dependency read-only và thêm hai file nguồn A/C riêng trong **cùng thư mục và nhánh đã có**:

- `tools/pilot_t4/prompt_conditioning_2x2/ttm_ac_objective_runner_candidate.py` — chỉ arm A/C, `RUN_ID=TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1`, kiểm owner lock **trước** mở private input/model/GPU, SHA của dependency runner và READY store, cổng rights/reviewer/eval/resume-QA/T4 smoke. Chế độ mặc định `source-qa`, không model forward. Science mode là **mã ứng viên**, không được phép sử dụng cho đến khi khóa owner mới được duyệt.
- `tools/pilot_t4/prompt_conditioning_2x2/ttm_ac_resume_store.py` — checkpoint và READY marker chỉ ghi mới (exclusive create), SHA256/size, kiểm identity RunID/arm/parent/source/owner-lock, reject SHA sai, bước không liên tục, orphan marker, overwrite. Bốn mốc READY dự kiến: **1056, 1088, 1120, 1152**; nhận dạng bước thực thi chưa vào READY và **HOLD, không replay tự động**.
- `tools/pilot_t4/prompt_conditioning_2x2/test_ttm_ac_resume_synthetic.py` — kiểm thử riêng cho nguồn READY store bằng một mô hình Linear 3→2 hoàn toàn **tổng hợp**; không nạp Small4M, TRAIN/VAL/TEST, không thực hiện inference trên checkpoint thật.

**Ngân sách future candidate nếu owner phê duyệt:** 2 arm × 128 bước × 4096 target labels = **1.048.576 target-token presentations**; 2 × 2928 windows, 2 × 749568 forward token slots, cùng checkpoint, TRAIN draw schedule và optimizer/scheduler/RNG/scaler ban đầu. Điểm khác duy nhất của A/C: A dùng CE đều, C dùng CE weight 1 ở vị trí 0–31 và weight 3 từ vị trí 32; denominator theo toàn optimizer step. Không tuyên bố GPU seconds hoặc effective weighted gradient bằng nhau.

**Giới hạn Resume quan trọng:** mốc READY mỗi 32 bước giúp tránh ghi lại bằng chứng cũ, nhưng khi Colab bị ngắt **giữa** hai READY, journal của runner cố ý chặn replay để không giả định không có bước nào bị lặp. Như vậy đây là **safe fail-closed resume**, **chưa** là khả năng phục hồi không mất tiến độ từ mọi gián đoạn. Cần cân đối khoảng READY/storage và QA native T4 trước một permit khoa học.

## 3. QA đã thực hiện trong lượt này

Báo cáo máy đọc: `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_SMALL4M_AC_SOURCE_AND_SYNTHETIC_RESUME_QA_20261111.json`.

| Cổng | Kết quả | Ranh giới |
|---|---|---|
| Đọc lại chính xác 3 Git blobs nguồn A/C và fixtures | PASS | GitHub trên đúng nhánh, không xác minh private runtime |
| Đối chiếu nguồn và điều kiện khóa (23 cổng static) | **23/23 PASS** | Static review của tác giả, không phải independent code execution |
| READY store và 6 bài kiểm thử Resume CPU toy | **6/6 PASS** | Thực thi trong sandbox Linux Python 3.13.5, Torch 2.10.0+cpu; exact blob helper/test khớp GitHub |
| Khôi phục model/AdamW thực step1024 | **PASS trước đó** | 42/42 CPU QA của ứng viên 4-arm kế thừa, chưa chạy lại với code A/C |
| Python compile từ **exact GitHub A/C runner trên Windows 3.12** | **NOT_EXECUTED** | Chưa có native runner QA source chính xác trong lượt này |
| T4 FP16 smoke, interrupted READY/resume trên actual P02 | **NOT_EXECUTED** | Không có quyền GPU/huấn luyện mới |
| Full parent and 2-arm science | **NOT_EXECUTED** | Không có science lock; không dùng historical one-shot |

Không suy ra `RESUME_ACTUAL_SMALL4M=PASS` từ `TOY_RESUME=PASS`. Static checks và synthetic QA cũng **không** đủ để cấp permit.

## 4. Nguồn dữ liệu và quyền sử dụng

Nguồn `roneneldan/TinyStories` được Hugging Face công bố với metadata `license: cdla-sharing-1.0`; revision đóng băng candidate `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. Văn bản chính thức `https://cdla.dev/sharing-1-0/`:
- Mục 2: trao quyền Use/Computational Use theo các điều kiện của thỏa thuận.
- Mục 3: khi phát hành Data/Enhanced Data cần tuân thủ các điều kiện giấy phép, ghi công/notices; không suy luận quyền phát hành corpus từ quyền huấn luyện nội bộ.
- Theo thiết kế A/C, **không phát hành raw TRAIN/VAL, token windows, checkpoint, TEST, người chấm và key mù lên GitHub**.
- **`LICENSE_TEXT_REVIEW=PASS_SCOPED`**; **`OWNER_PRIVATE_PACK_USE_ATTESTATION=HOLD_NOT_SIGNED`**. Đây là rà soát văn bản giấy phép, không phải tư vấn pháp lý hay xác nhận nguồn tư nhân đã được chủ dự án phê duyệt lại.

Nguồn: https://huggingface.co/datasets/roneneldan/TinyStories và https://cdla.dev/sharing-1-0/ .

## 5. Bộ đánh giá 24 prompt: nguồn khóa, ánh xạ mù còn HOLD

Dùng lại **nguồn đánh giá chưa hề chạy** thuộc candidate 2×2:
`docs/research/TTM_SMALL4M_2X2_NEW_DEV12_BLIND_FINAL24_PROMPTS_FROZEN_20261110.json`.
- 12 DEV: D01–D12; **24 FINAL: Q01–Q24**, các SHA UTF-8 từng prompt nguyên bản và BPE count 23–35, không trailing ASCII space; 36/36 distinct theo hồ sơ. Không đọc lại Q1/Q2 và TEST để kiểm overlap tuyệt đối.
- Bản rút gọn hai arm nằm tại `docs/research/TTM_SMALL4M_AC_FINAL24_BLIND_EVAL_AND_RIGHTS_PREEXEC_FREEZE_20261111.json`; 24 cặp A/C, greedy, max64 token, rubric bám prompt/mạch lạc/nhất quán 0–3.
- Primary candidate: `mean_24(score_C_adherence - score_A_adherence) >= +0.5/3`; bootstrap ghép cặp trên 24 prompt CI95 lower >0, C thắng ít nhất 16/24; guardrail VAL NLL không suy giảm >5% so A, coherence/consistency không giảm >0.25/3. Đó là ngưỡng **chưa được owner khoa học phê duyệt**, không phải thành tích.
- Lịch trình **công khai** và cân bằng được chỉ định trước: mỗi prompt một cặp, A ở vị trí trái 12/24 và C ở vị trí trái 12/24, reviewer chỉ nhận ID trung tính. **Private seed/mapping chưa được lập và khóa trong escrow**; không được giả nhận complete randomization.
- **Chưa có người chấm độc lập được định danh/chấp thuận** cho lượt A/C, chưa có attestation chống xung đột quyền lợi, chưa có khóa điểm trước giải mù. Codex AI từng chấm FRESH12 không được tự động coi là reviewer cho nghiên cứu này. Nếu reviewer AI được dùng, kết luận tối đa exploratory scoped; không gọi là chấm độc lập con người.

## 6. Phân xử tổng hợp

| Hạng mục | Quyết định |
|---|---|
| Scope A/C, same-data, same-budget | **SOURCE_SCOPE_PASS** |
| New resume helper synthetic 6/6 | **PASS_SCOPED_SYNTHETIC** |
| 24 prompt/rubric public freeze | **SOURCE_FREEZE_PASS** |
| License text / rights owner | **PASS_SCOPED / HOLD_OWNER_ATTESTATION** |
| Reviewer độc lập + private mapping | **HOLD** |
| Exact Windows/Colab T4 QA + actual resume | **HOLD** |
| Science authorization | **NOT_GRANTED** |

**`FINAL_PREEXEC_DECISION=NO_GO_NOW_PREEXEC_HOLD`.** Không ban hành science owner lock/permit, không ký attestation thay chủ dự án, không đặt nhãn reviewer giả, không tạo CLAIM hay chạy huấn luyện/inference. Đây là trạng thái hạ tầng và đánh giá, **không phải** `H_OBJECTIVE=FAIL`.

**Main và lineage:** main `5d52e32f20021e36f08f284ef9864d3ba36dbead` tại lượt kiểm kê; PR #13 vẫn DRAFT; `lineage.md` nguyên vẹn. Nhánh thiết kế hiện hữu không có PR mới. **Merge = HOLD**: chỉ thêm nguồn và tài liệu staging, cần review riêng trước khi hợp nhất.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_AC_FINAL_OWNER_RIGHTS_REVIEWER_ESCROW_AND_NATIVE_RESUME_PREEXEC_CLOSEOUT`

Gộp một lượt hữu hạn cuối còn thiếu: owner xác nhận phạm vi quyền private pack; phân công reviewer và niêm phong ánh xạ mù; kiểm thử exact source trên Windows Python 3.12 và smoke/resume parity phù hợp T4 mà không thực hiện huấn luyện khoa học. Chỉ sau **tất cả** cổng PASS mới trình một quyết định duy nhất `GO/NO_GO` cho **một** batch A/C mới. Không dời ngưỡng sau kết quả, không tái sử dụng TEST/OOD/Q1Q2 hoặc run đã tiêu thụ.
