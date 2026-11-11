# TTM-Small-4M — CF1 DEV36: kiểm toán điểm số độc lập và phân xử khoa học

**Ngày:** 2026-11-11  
**Tác vụ:** `TTM_CF1_DEV36_OWNER_LOCAL_EVIDENCE_READBACK_AND_SCIENCE_SCOPE_ADJUDICATION`  
**Nguồn:** repository `minhtri22/TokenToModel-Lab`; nhánh evidence `evidence/ttm-cf1-step1024-dev36-once-20261111` tại **commit bất biến** `cf6a37e5e9709ab0613918dc03ee70efa79f893f`. Nhánh review được tạo từ commit đó; **không sửa các tệp one-shot**.  
**Thực thi neural:** một lần duy nhất tại máy Windows chủ dự án, CPU, checkpoint bước 1024, 36 cặp DEV, 144 phép tính log-likelihood tiếp nối. Không tạo inference mới trong lượt kiểm toán này.

## 1. Bằng chứng thực thi đọc lại đúng từ GitHub

Đúng một commit thực thi `cf6a37e...` có parent `f2ce247bced65101401b3ed5c4bdca84f2f17913`, thêm đúng năm tệp: score JSON, owner adjudication JSON, SHA256 receipt, stdout và stderr. Không có file bị sửa/xóa trong commit này.

| Nguồn | Git blob | SHA256 / trạng thái |
|---|---|---|
| `artifacts/qa/ttm-narrative-cf1/dev36_owner_once_20261111/CF1_FROZEN_O0_DEV36_SCORES.json` | `462711cdc3b0bd6b8bdae33518a8518fd6f5bdd0` | `2f690fad052e4f76aec35904b665bd3135d598aca9eff12642d075c6335e2721` |
| `artifacts/qa/ttm-narrative-cf1/dev36_owner_once_20261111/CF1_DEV36_OWNER_LOCAL_ADJUDICATION.json` | `490d562ca63f59a4f68a70d685f828f92dd4b755` | `6a824e724fae0fe26aee291f5fa02d3d74d631e581adb4e6ecd4a73f741137b5` |
| `artifacts/qa/ttm-narrative-cf1/dev36_owner_once_20261111/CF1_DEV36_SOURCE_SHA256_READBACK.json` | `8156874518acc925db213b91604e47360373ec4d` | chứa các pin hiện hành |
| `artifacts/qa/ttm-narrative-cf1/CF1_DEV_MODEL_INPUT_ONLY.json` | `4fac79c16bc337926060fa21a6e22944d74259b7` | `81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed` |
| `artifacts/qa/ttm-narrative-cf1/CF1_DEV_PUBLIC_ORACLE.json` | `3f5a38069c918fd27c033ab48fce6fac9b8c5e4b` | `3a425188077f24041a02fe9675e5a503221fe5cc0247ebd53a8cc266329c046d` |

SHA256 của bốn file JSON được **tính lại trực tiếp trên nguyên nội dung đọc về từ GitHub**, so với receipt; tất cả khớp. Thuật toán SHA256 tự cài độc lập đã đối chiếu test vector chuẩn `abc` trước khi sử dụng. Script P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`, checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, BPE2048 manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` khớp receipt của tác vụ owner. Manifest/checkpoint không được đọc lại từ Windows trong lượt phân tích riêng; chỉ file **public evidence** được kiểm toán.

`ONE_SHOT_STDERR.txt` rỗng; stdout ghi `CF1_READONLY_DEV_SCORES_READY=36; NO_FINAL_OR_TRAINING`. Không có cập nhật trọng số (`optimizer_updates=0`), GPU (`GPU_calls=0`), đọc FINAL hoặc TEST/Q1Q2.

## 2. Tính lại 36 × 4 điểm số và nhãn

Mỗi hàng chứa `L_a_x, L_a_y, L_b_x, L_b_y`, đều là log-probability trung bình theo token dưới teacher forcing. Tính lại độc lập:
- `m_A = L_a_x - L_a_y`
- `m_B = L_b_y - L_b_x`
- `D = m_A + m_B`
- `PAIR_BOTH_CORRECT = (m_A > 0 && m_B > 0)`

Kiểm 36/36 hàng khớp thứ tự nội dung với oracle, công thức margin và contrast khớp chính xác (max absolute error = 0), 144 logprob hữu hạn, 36/36 cặp có hai ứng viên cùng độ dài token. **Cả 36 nhãn vàng đều theo quy ước `A=x, B=y`**, một hạn chế của thiết kế đánh giá.

| Chỉ số | Tổng | C1 (12) | C2 (12) | C3 (12) |
|---|---:|---:|---:|---:|
| Đúng cả hai ngữ cảnh | **0/36** | 0/12 | 0/12 | 0/12 |
| Đúng A | **1/36** | 0/12 | 0/12 | 1/12 |
| Đúng B | **35/36** | 12/12 | 12/12 | 11/12 |
| Thay đổi ứng viên ưu tiên giữa A/B | **0/36** | 0/12 | 0/12 | 0/12 |
| `D > 0` | 20/36 | 4/12 | 9/12 | 7/12 |

**35/36 cặp**: model ưu tiên `y` trong cả A và B. **1/36 cặp**: model ưu tiên `x` trong cả A và B. Vì đáp án vàng phải đảo giữa A và B, model đạt 0 cặp đúng trọn vẹn. Không có ties trong hai so sánh lựa chọn.

`mean(m_A) = −0.3069264` ; `mean(m_B) = +0.3064984` ; `mean(D)=−0.0004280`.  
`mean(|D|)=0.0123437` ; `mean` độ lớn tuyệt đối của ưu thế x/y `=0.3091527`, tức hiệu ứng ngữ cảnh tuyệt đối chỉ khoảng **4.0%** so với ưu thế giữa hai tiếp nối.

Kiểm bootstrap 10.000 lần, chọn lại các **cặp** có hoàn lại, seed `20261111`, LCG 32-bit được khai báo trong receipt JSON: CI percentile 95% của `mean(D)` là **[−0.0075893,+0.0063098]**. Bao gồm 0; đây là kiểm định thăm dò trên **DEV tự soạn, không phải xác nhận thống kê trên quần thể độc lập**. `D` dương 20/36 riêng lẻ **không** đủ để gọi giải được câu chuyện, vì phải thỏa **cả hai** dấu margin.

## 3. Nguyên nhân giới hạn kết luận

Điểm 0/36 là **kết quả neural thật trên exact public DEV**, không phải lỗi hệ thống và không phải kiến trúc O1 thất bại. Phát hiện trực tiếp là **completion preference không đảo khi thay đổi ngữ cảnh**. Chúng ta có bằng chứng rằng với checkpoint TTM O0 bước 1024, prompt và dữ liệu DEV36 này, phép thử conditional-likelihood không có tín hiệu đạt yêu cầu.

Đồng thời, độ giá trị phân biệt *state reasoning* của **chính CF1** bị giới hạn nặng:
1. Heuristic lexical nông đã đạt 36/36 trên DEV tại vòng kiểm định nguồn; không cần trạng thái động hay đồ thị.
2. Cả **36/36** nhãn có A đúng x, B đúng y. Một evaluator **được nhìn A/B và vị trí x/y** có thể đạt 36/36 bằng quy tắc vị trí cố định. Đây là *evaluation position confound*, **không phải** một mô hình hợp lệ chỉ nhìn câu chuyện và token; cần tránh đánh đồng với baseline model-only.
3. Không có kết quả trên các checkpoint/seed/model khác, không có huấn luyện nhiệm vụ trong nghiên cứu này. Không thể từ đây kết luận khả năng học, ngữ nghĩa tổng quát, hoặc O1 tốt hơn.

Do đó, **không hợp thức hóa BLIND FINAL để "cứu" kết quả DEV**, không sửa prompt/corpus/heuristic hậu nghiệm, không chạy lại checkpoint khác hoặc chọn lại seed trong cùng thử nghiệm. Phép thử nên được lưu làm **chẩn đoán thăm dò (exploratory diagnostic)** và ví dụ về thiên lệch thứ tự ứng viên/nhãn.

## 4. Phán quyết tổng hợp và điều kiện bất biến

**`OWNER_SCOPED_ADJUDICATION=NO_GO_CF1_BLIND_FINAL`**; **`FROZEN_O0_DEV36_CONTEXT_SWITCHING=FAIL_SCOPED_0_OF_36`**.

- Lượt CPU one-shot đã thực thi 36/36, receipt exact SHA được lưu; **không có lý do khoa học chạy lại**.
- BLIND FINAL 72 cặp **giữ nguyên SEALED/HOLD**, không giải mã, không chấm.
- O0 **không huấn luyện thêm**; O1 **DEFER**; GPU **NO**.
- Các nguồn public, one-shot commit, mô hình gốc, TEST/Q1Q2, `main`, PR #13 và `lineage.md` không được tác vụ phân xử này sửa.
- Review này là phân tích riêng qua ChatGPT Web trên log GitHub, **không phải độc lập external human hoặc một job Codex riêng**.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_POST_CF1_FROZEN_O0_ORIGINAL_LANGUAGE_VAL_AND_FRESH_CONTINUATION_GAP_RECONCILIATION_DESIGN_ONLY_NO_NEW_TOY`. Đối chiếu các nguồn đánh giá VAL và FRESH về mạch lạc/ngữ cảnh đã được tiêu thụ theo đúng phạm vi, chỉ nghiên cứu thiết kế và xem lại những claim thực chứng; không sinh toy khác, không dùng lại TEST/Q1Q2 và không mở neural run/GPU.

**Nguồn máy đọc:** [Báo cáo JSON chi tiết](../../artifacts/qa/ttm-narrative-cf1/reviews/CF1_DEV36_INDEPENDENT_GITHUB_SOURCE_SCORE_AUDIT_AND_ADJUDICATION_20261111.json). 
