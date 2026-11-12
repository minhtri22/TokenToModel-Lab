# TTM Small4M A/C FINAL24 — Kiểm toán hậu giải mù và phân xử chính thức

**Operation:** `TTM_AC_FINAL24_INDEPENDENT_POST_UNBLIND_SCIENCE_QA_AND_FINAL_ADJUDICATION`  
**Ngày:** 2026-11-12  
**Run:** `TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1`  
**Phạm vi:** Một lượt huấn luyện A/C đã khóa, chấm mù bởi GPT-6 trong phiên tách biệt, một seed, 24 prompt, 48 văn bản.  
**Chế độ kiểm toán:** Mã checker mới tái tính từ các bản nguồn đã khóa và escrow AES; **không** phải tổ chức độc lập thứ ba hoặc người chấm thứ hai.  

## 1. Phán quyết tách biệt

- **Tính toàn vẹn nguồn, điểm và giải mù:** `PASS_INDEPENDENT_RECOMPUTATION_SCOPED` — 107/107 phép kiểm tra độc lập đạt PASS; không thay đổi văn bản, điểm hoặc khóa.
- **Tính hợp lệ của kết quả theo tiền đăng ký:** `FAIL_CANDIDATE_EFFICACY_GATE_NO_DEMONSTRATED_C_GAIN` — C không vượt A về bám prompt trên FINAL24 theo ngưỡng đã khóa.
- **Phân loại nghiên cứu:** `EXPLORATORY_SCOPED_AI_REVIEW`, không phải chứng minh xác nhận đa seed, người chấm độc lập là con người hay kết luận hai phương pháp tương đương.
- **Quyết định đóng giai đoạn:** `CLOSE_AC_FINAL24_NEGATIVE_RESULT_IN_SCOPE`; không train lại, không chỉnh sửa rubric/threshold hậu nghiệm, không dùng lại TEST/Q1/Q2/OOD.

## 2. Chuỗi SHA-256 và nguồn gốc

| Bằng chứng | SHA-256 |
|---|---|
| Gói người chấm ZIP | `577f58ef101645febee25e959497d9d883400565ec65d4b8902516d8059daf00` |
| JSON chấm mù 24 cặp | `b325567addf4a4498c7384309281c53525e8548fc18fa35221140bbdd0901be9` |
| 48 đầu ra gốc owner | `9d158c9e8a7d590ebc9315d716e3b072f5bf94e06cf5061d63ab15e014c36570` |
| Điểm 144 số nguyên đã đóng băng | `386d455bc3768c81b0728f4b3903ecd7e73fed6d8adabf8eaf934316bd8a91be` |
| Mảng điểm chuẩn hóa trước giải mù | `f4cd13c915d2a423e21fcd74ea3fa2127ada45023292d84782614a54624f3369` |
| Biên nhận người chấm | `a0ae78a805f102a4086f7e36a81f85d95e28716589cca0192ca501a1df7a4935` |
| Escrow AES công khai nguyên byte | `519f3185d6202052ce1e5c98a7e7fa58a813d87ce9d9e2d173eb25f6a05f9f1c` |
| Ánh xạ plaintext (chỉ hash) | `68d4e303efd2c5809bf0e89f5564f70e1114349b463b5458174c1407e8deda1d` |
| Báo cáo owner giải mù chi tiết (private) | `10d1c71d46d7aa70b24ee66c304b3258b63ed0af6f73ba8be994a08da064c523` |
| Tổng hợp owner trước phân xử | `9c3e47121ef70b20d6483968bdef35015d09e2c98aaf8b47e4436937906879a9` |
| Mã kiểm toán mới (source) | `c92e7c9ab30a06c247562c327862a802c7876af7f1df51e722bdd272e3933f9f` |
| Biên nhận 107 phép kiểm toán | `27b9d6069cad1bf06b5fdba3c6def5f011fb8020e119f7818d17bd197ca22bfa` |

Khóa AES **không** được đưa vào GitHub; ánh xạ từng cặp A/C và các văn bản gốc giữ riêng phía owner. SHA của khoá file có thể dùng để đối chiếu kín nhưng không xuất trong biên bản công khai. Handoff chấm mù không có ánh xạ. Sidecar SHA gốc từ người chấm chưa được nộp; bản đối chiếu SHA phía owner được tái lập, có nhãn provenance riêng, trong khi byte tệp điểm và hash receipt khớp hoàn toàn.

## 3. Nguồn tiền đăng ký và phép tính độc lập

Tiền đăng ký: `docs/research/TTM_SMALL4M_AC_FINAL24_BLIND_EVAL_AND_RIGHTS_PREEXEC_FREEZE_20261111.json`, Git blob `ce7e3ff7297157f1f852eadd2da72e97f91ec7ff`. Tiêu chí chính: `mean_over_24_prompt_pairs(score_C_adherence-score_A_adherence)`.

| Tiêu chí 0–3 | A (trung bình) | C (trung bình) | C − A | C thắng / A thắng / Hòa |
|---|---:|---:|---:|---:|
| Bám sát prompt (primary) | 0,6667 | 0,6667 | **0,0000** | **1 / 1 / 22** |
| Mạch lạc | 1,2500 | 1,2500 | 0,0000 | 3 / 2 / 19 |
| Nhất quán | 1,6667 | 1,6667 | 0,0000 | 0 / 0 / 24 |

CI bootstrap 95% **mô tả hậu nghiệm** của chênh lệch C − A theo prompt: bám prompt `[−0,125; +0,125]`; mạch lạc `[−0,250; +0,2083]`; nhất quán `[0;0]`. Checker xác minh 50.000 lần lấy mẫu, seed 20261112, nhưng số lần/seed/chi tiết bootstrap **không** được khóa đầy đủ trước khoa học, nên CI chỉ được xem là mô tả, không là chứng minh confirmatory.

VAL NLL A `3,511285912623514`; C `3,512388891872789`; chênh `+0,001102979249274938`; suy giảm tương đối C so A `0,0314124%`. Guardrail 5% đạt, nhưng điểm bám prompt không cải thiện.

### Áp dụng cổng ứng viên đúng bản khóa

| Điều kiện | Kết quả |
|---|---|
| Trung bình bám prompt C − A ≥ +0,5 | **FAIL** (0,0) |
| C thắng chặt ≥16/24 cặp | **FAIL** (1/24) |
| Cận dưới bootstrap CI95 >0 | **FAIL** (−0,125; mô tả) |
| VAL NLL C không suy giảm quá 5% | PASS |
| Mạch lạc C không giảm quá 0,25/3 | PASS |
| Nhất quán C không giảm quá 0,25/3 | PASS |

Kết luận cổng ứng viên là **FAIL**, không được đổi ngưỡng hoặc tái sử dụng FINAL24 để đào tạo mô hình khác rồi tuyên bố thành công trên cùng tập.

## 4. Hợp lệ khoa học và giới hạn

- Hai nhánh A/C hoàn thành 128 optimizer update/nhánh từ parent 1024 đến checkpoint 1152, theo `READY_1152.json`, `FINAL.json`, owner science lock và readback đã lưu. Việc kiểm tra mới tập trung vào hậu giải mù và tính toán thống kê; **không** chạy lại 128 cập nhật, không chứng minh độc lập mọi FLOP hay mọi lần Colab resume.
- Người chấm GPT-6 tự khai không biết arm; chứng cứ độc lập chỉ ở mức session/rater self-attestation, không phải xác minh bằng nhà cung cấp hoặc kiểm nghiệm của con người.
- Một seed, 24 prompt và nhiều văn bản chất lượng thấp, cho nên đây là **không chứng minh lợi ích trong phạm vi thử nghiệm**, không chứng minh C luôn vô hiệu hoặc A/C tương đương trên toàn bộ tác vụ.
- TEST, Q1/Q2, OOD và nguồn TRAIN/VAL nguyên văn **không** được truy cập trong QA mới; không huấn luyện bổ sung; không thay đổi checkpoint hoặc tệp điểm đóng băng.
- Biên bản điểm và giải mù có nhãn private phải ở Drive owner; chỉ checker và aggregate không chứa bí mật được phép đưa lên GitHub.

## 5. Bằng chứng, quản trị và bước sau

Nguồn checker: `tools/pilot_t4/prompt_conditioning_2x2/qa/ttm_ac_final24_independent_postunblind_qa_v1.py`.

Biên nhận QA: `artifacts/qa/ttm-small4m-prompt-conditioning/ac_postfreeze/TTM_AC_FINAL24_INDEPENDENT_POSTUNBLIND_QA_20261112.json`.

Báo cáo này: `docs/research/TTM_AC_FINAL24_INDEPENDENT_QA_AND_FORMAL_ADJUDICATION_20261112.md`.

`lineage.md` append-only mục `L0015` trên nhánh A/C: bảo toàn `L0013–L0014` vốn đã có trên `main`. **Không sửa các mục cũ**, chưa merge nhánh, không chỉnh `main` hoặc PR/T5 khác. Trạng thái đóng nghiên cứu A/C không tự cấp quyền P02/P03 hoặc công khai checkpoint.

**Bước thực hiện tiếp theo:** Lưu kết quả âm FINAL24 làm mốc khoa học; mọi can thiệp về dữ liệu, loss hay decoding sau này phải tạo một giả thuyết và bộ prompt mới độc lập, không dùng lại FINAL24 làm bằng chứng xác nhận.
