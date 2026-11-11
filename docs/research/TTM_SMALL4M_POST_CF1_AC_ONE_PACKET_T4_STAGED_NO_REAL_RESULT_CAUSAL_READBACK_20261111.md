# TTM-Small-4M O0 — Phản hồi sau tích hợp A/C T4 một gói

**Ngày:** 2026-11-11  
**Công việc:** `TTM_SMALL4M_AC_SINGLE_INTEGRATED_T4_ACTUAL_RESUME_OWNER_SCIENCE_AND_FINAL24_ADJUDICATION_THEN_O0_READBACK`  
**Nhánh phân xử O0 duy nhất:** `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`.

## 1. Kết quả kỹ thuật đã thực hiện, nguồn không đổi

Sau native Python3.12 V2 **6/6 PASS scoped** trên Windows, thực hiện rà soát nguồn và các vị trí lưu dữ liệu thực trên Drive của chủ sở hữu. Cả ba tài nguyên nguồn đã tồn tại theo Google Drive metadata: private TRAIN/VAL NPZ, manifest và parent P02 checkpoint bước 1.024. Chúng được tham chiếu theo đường dẫn Drive của owner, **không nhúng private Drive file IDs hoặc khóa riêng tư vào notebook GitHub**.

Đã tạo notebook thực thi **một gói** tại `tools/pilot_t4/prompt_conditioning_2x2/TTM_AC_2ARM_ONE_PACKET_T4_OWNER_COLAB_20261111.ipynb` trên nhánh AC, Git blob `05cc058ccbf2f502683a53ff3e99868f20f39bc7` ban đầu đã được cập nhật để dùng owner mounted Drive; **Git blob cuối** `05cc058ccbf2f502683a53ff3e99868f20f39bc7` không còn là chân lý; tham chiếu bản cuối theo HEAD của AC và biên nhận nguồn AC. (Luôn chọn notebook theo HEAD hiện tại, không dùng bản cũ trong Windows `V2`.)

Notebook giữ đúng hai arm A và C; dùng mã science nguyên bản `ttm_ac_objective_runner_candidate.py`, pin nguồn `6628401b08ea7682cf34aa5078546e1d18e4d2cc`, SHA checkpoint `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, pack `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. Có code tải đầu vào, kiểm SHA, FP16 zero-step T4, kiểm khôi phục mô hình P02 3,75M theo dữ liệu tổng hợp, thực thi khoa học khi và **chỉ khi** có exact owner science lock hợp lệ, sau đó xuất 48 đầu ra FINAL24 từ hai checkpoint thật nếu có private BPE đúng SHA.

Đã ghi bản notebook cuối trên Windows dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_AC_2ARM_ONE_PACKET_T4_OWNER_COLAB_V3_20261111.ipynb` nhưng cần dùng **bản notebook GH mới nhất** nếu có sửa sau; không thực thi lệnh nào trong Colab từ hội thoại này.

## 2. Phạm vi kiểm chứng và ranh giới khoa học

- Native V2: `PASS_SCOPED_NATIVE_PY312_SOURCE_AND_CPU_TOY_RESUME`, không chạy lại.
- Chứng cứ hiện tại: nguồn notebook và tài nguyên đầu vào trên Drive; Colab GPU **chưa được khởi chạy**; vì kết nối Google Drive chỉ hỗ trợ tệp, không cung cấp quyền điều khiển runtime Colab T4.
- Kiểm thử tải lại full P02 với token tổng hợp (synthetic) nếu chạy trên T4 chỉ được gọi `PASS_REAL_P02_T4_SYNTHETIC_RELOAD_PARITY_SCOPED`; **không tự nâng thành** `PASS_ACTUAL_AC_RESUME_PARITY`. Notebook đòi biên nhận phân xử độc lập đúng cổng đã khóa.
- Quyền dùng private pack do owner xác nhận, custody key AES owner-only, người chấm độc lập và owner science lock: chưa có biên nhận thỏa mãn tất cả. Không tự ký thay owner/reviewer.
- A/C science: **không chạy**; 128 bước/arm vẫn chỉ là hợp đồng. FINAL24: không sinh 48 outputs, không chấm mù, không giải mù, không có scores.
- Nếu có A/C sau này, đối chiếu `C−A` trên FINAL24 cùng VAL guard của AC, không dùng FRESH16 hoặc TEST/Q1Q2 thay thế; chưa có dữ liệu thì không thể phân biệt nguyên nhân data/objective/capacity.

Biên nhận AC: `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_AC_ONE_PACKET_T4_FINAL24_OWNER_INTEGRATED_EXECUTION_DECISION_20261111.json` trên nhánh AC.

## 3. Quyết định duy nhất hậu CF1

`O0_OBJECTIVE_CAUSAL_DECISION=HOLD_C_MINUS_A_NOT_ESTIMABLE`.

`T4_VAL_H1=PASS` vẫn giữ. `H_OBJECTIVE=UNDETERMINED`, `DATA_WINDOW_CAUSE=UNPROVEN`, `CAPACITY_LIMIT=UNPROVEN`; B/D, O1, MoE/Attention hoãn. **Không ghi lineage** cho việc triển khai notebook hoặc kiểm tra kỹ thuật; `main`, PR13 và `lineage.md` giữ nguyên.

Đây không phải mẫu yêu cầu micro-permit mới. Gói còn thiếu phải được owner/đối tác đánh giá hoàn tất thành **một quyết định science**; chỉ khi có kết quả A/C thật đã phân xử, nhánh này mới cập nhật kết luận nhân quả.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_AC_OWNER_ONE_PACKET_COLAB_T4_EXECUTION_AND_FROZEN_FINAL24_RESULT_RETURN_TO_POST_CF1`

Owner mở **notebook duy nhất từ GitHub HEAD AC**, dùng đúng GPU T4, hoàn thiện chứng cứ quyền/giữ mù/reviewer/actual resume và khóa khoa học duy nhất đã đóng băng, chỉ sau đó mới chạy A/C. Đọc lại hai checkpoint và FINAL24 science adjudication trước khi phân xử O0. Nếu chưa có các bằng chứng đó => HOLD, không phát minh kết quả.

**Trạng thái cuối:** `AC_NATIVE_V2=PASS_SCOPED` · `AC_COLAB_NOTEBOOK=STAGED_SOURCE_ONLY` · `AC_T4=NOT_EXECUTED` · `AC_SCIENCE=NO_GO_PREEXEC` · `FINAL24=NOT_EXECUTED` · `C_MINUS_A=NOT_ESTIMABLE` · `NEW_TRAINING=NO` · `GPU=NO` · `TEST_Q1Q2=UNTOUCHED` · `MAIN/LINEAGE=UNMODIFIED`.
