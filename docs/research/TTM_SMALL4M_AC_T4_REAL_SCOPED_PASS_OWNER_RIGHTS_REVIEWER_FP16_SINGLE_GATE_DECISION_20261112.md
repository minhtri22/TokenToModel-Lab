# TTM Small4M A/C — T4 scoped PASS, một quyết định owner sau xử lý FP16

**Ngày:** 2026-11-12  
**Operation:** `TTM_SMALL4M_AC_SINGLE_INTEGRATED_T4_ACTUAL_RESUME_OWNER_SCIENCE_AND_FINAL24_ADJUDICATION_THEN_O0_READBACK`.  
**Nhánh:** `research/ttm-small4m-prompt-conditioning-objective-design-20261110`; readback của bản notebook V4 trên Colab và tệp gốc trong Google Drive của owner.

## 1. Chứng cứ thật đã đối chiếu (không chạy lại)

| Nguồn | SHA-256 gốc | Kết quả |
|---|---|---|
| `COLAB_ENVIRONMENT.json` | `29d5076dbc4bbac94d9b07db2e4730f677d618b4750cbf37bdc19226b35a62ae` | Tesla T4, Python 3.13.16, torch 2.14.1+cu130, 0 science steps |
| `T4_FP16_ZERO_STEP.json` | `3bea99fe32a7cb8f1e9376c5b6d8b56a18ae3660d48f3bdefefbf993970093ed` | `PASS_T4_FP16_ZERO_SCIENCE_STEP`, P02 3.749.376 tham số |
| `AC_REAL_P02_T4_FP16_RESUME_PARITY.json` | `c4fead8605dc8b5a134d8930ccdf3ef89fecdc0005cb4f621a511e2306c3de92` | `PASS_REAL_P02_T4_SYNTHETIC_RELOAD_PARITY_SCOPED`, **không** cấp quyền actual AC resume |
| `FINAL24_EVAL_SOURCE_FREEZE.json` | `cd21dd2cbcec396e0e1876136fa1d1db679212cad7ecef372f9859b545c9a7fb` | `PASS_24_PROMPT_BLIND_FREEZE`, chấm điểm NOT_EXECUTED |

Nguồn: bốn tệp ở Google Drive `ttm_small4m_ac_objective_only_v1/qa_preexec`. Metadata, mô hình nguồn, checkpoint và bộ TRAIN/VAL đồng nhất SHA đã khóa. Readback không cần tải dữ liệu TRAIN raw, không xem TEST/OOD/Q1Q2, không tái chạy native QA đã PASS.

## 2. Phát hiện FP16 và ảnh hưởng đến science

`qa_step1` ghi lần đầu tại scale `65536`: optimizer step `1024 -> 1024` (**skip**), GradScaler `65536 -> 32768`; lần 2 ở scale `32768`: `1024 -> 1025` (một update thật). `qa_step2` và `qa_resumed` đều `1025 -> 1026` với chuỗi scale/step trùng nhau. Kết quả chính xác ở phạm vi **mô hình P02 thật trên T4 với synthetic IDs**. Biên nhận khẳng định `actual_AC_resume_gate=NOT_GRANTED_BY_THIS_SYNTHETIC_QA`.

Runner khoa học V1 vẫn cố định `need(scaler.get_scale()>=oldscale, 'GRAD_SCALER_SKIPPED_STEP')` và sẽ dừng nếu tình huống ấy lặp lại trên TRAIN thực. **Không được kết luận chắc chắn** nó sẽ lặp lại trên TRAIN; đây là rủi ro kỹ thuật được quan sát trong synthetic QA, chưa là kết quả science.

Để không che lỗi hoặc thay nghiên cứu sau khi xem điểm FINAL24, đã tạo riêng nguồn **amendment candidate trước science**:
`tools/pilot_t4/prompt_conditioning_2x2/ttm_ac_objective_runner_fp16_backoff_v2_REVIEW_CANDIDATE.py`, Git blob `6bbd8b7190f843685197f6203b574a6c76977f3a`.

Thay đổi duy nhất được dự kiến: nếu GradScaler giảm và AdamW **không** cập nhật, thử lại tối đa 12 lần với đúng batch/plan đã khóa; scheduler và bước nghiên cứu chỉ tăng khi AdamW thực sự tăng một; ghi mỗi lần thay đổi scale vào history. Giữ A/C (không B/D), cùng source data, checkpoint, CE A/C, 128 **successful optimizer steps**/arm. Candidate vẫn `NOT_INDEPENDENTLY_EXECUTED/NOT_ACCEPTED`, không thay runner V1 đã khóa, bắt buộc một owner lock mới có cờ `fp16_backoff_amendment` xác nhận chính xác.

**Khác biệt khoa học cần được quyết định trước khi train:** Nếu chấp thuận amendment V2, kết quả sẽ áp dụng chính sách backoff tối đa 12 lần; không hồi tố kết quả cho runner V1. Nếu chọn V1 không sửa, huấn luyện phải fail-closed khi có skip. Không tự chuyển V1 sang V2 trong phiên huấn luyện.

## 3. Một gói GO/HOLD còn thiếu

Bộ Cell3 hiện từ chối vì ba tệp owner-controlled chưa có:
- `RIGHTS_OWNER_SIGNED.json`: owner thực sự xác nhận private pack SHA `184f68b4...` từ nguồn TinyStories được phép nghiên cứu nội bộ và không tái phân phối raw.
- `REVIEWER_INDEPENDENCE_SIGNED.json`: người chấm/đơn vị độc lập **thực sự được giao và chấp nhận**, chấm 48 output theo FINAL24 mù, đóng băng điểm trước giải mù. Không được tự điền tên/chữ ký reviewer.
- `OWNER_AC_SCIENCE_LOCK.json`: chỉ được owner xác nhận sau khi có quyền/custody key owner-only, reviewer, exact checksum 5 receipt (rights/reviewer/final24/actual resume/T4 smoke), source runner pinned và một quyết định owner duy nhất.

**Ba tệp chưa đủ:** còn phải xác minh custody AES key chỉ owner đọc được; biên nhận độc lập `PASS_ACTUAL_AC_RESUME_PARITY` chưa có. Receipt synthetic hiện tại **không đủ điều kiện thay thế**. Không được sinh giấy phép/QA PASS giả để vượt gate. Không đặt khóa AES hoặc raw prompts/checkpoints private lên GitHub công khai.

Cũng cần kiểm tra BPE manifest TRAIN-only SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` trong thư mục owner để sau huấn luyện không vướng khâu sinh FINAL24. Chưa xác minh hiện diện.

## 4. Một quyết định hiện thời

`AC_T4_SCOPED_TECH_QA=PASS`.  
`AC_SCIENCE_GO=HOLD_UNSIGNED_OWNER_RIGHTS_UNASSIGNED_REVIEWER_UNVERIFIED_ACTUAL_RESUME_AND_FP16_SCIENCE_RUNNER_POLICY`.  
`C_MINUS_A=NOT_ESTIMABLE`.

Không đào tạo lại O0, không mở B/D/O1, không chạy lại native hoặc synthetic QA đã PASS. Không sửa `main`, `lineage.md` hoặc nhánh FRESH16.

## Bước thực hiện tiếp theo

`TTM_AC_SINGLE_OWNER_RIGHTS_REVIEWER_CUSTODY_FP16_AMENDMENT_ACTUAL_RESUME_INTEGRATED_GO_HOLD`

Một lần owner xác nhận nguồn quyền và người chấm độc lập (không giả mạo), owner-only escrow ACL và chấp thuận/chối bỏ amendment trước science; độc lập thẩm định candidate/source runner, xác nhận actual T4 resume. Nếu gói được đóng đầy đủ, owner ký **một science lock duy nhất**, chạy A/C trên T4; sau khi thực hiện FINAL24 và chấm mù thật, mới phân xử C−A rồi cập nhật nhánh hậu CF1.
