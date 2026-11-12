# TTM-Small-4M D1 — Kết quả thực thi DEV32 khám phá và chuyển giao BLIND64

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_POST_FINGERPRINT_EXPLORATORY_DEV32_ONE_SHOT`  
**Phạm vi khoa học:** `EXPLORATORY_SCOPED_SHORT_NEAR_ONE_NUCLEUS_SEED` — không thay thế D1 confirmatory 512.  
**Trạng thái máy Windows:** `TTM_D1_DEV32_CPU_EXPLORATORY=PASS_EXECUTED_SCOPED`, theo output PowerShell chủ sở hữu và đối chiếu trực tiếp biên nhận `D1_EXP32_SAFE_SUMMARY.json` trong `_tmp`.

## 1. Nguồn và custody đã đối chiếu

| Trường | Giá trị |
|---|---|
| Checkpoint step1024 SHA-256 | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` |
| T1 BPE manifest SHA-256 | `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| D1 V2 private raw SHA-256 | `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8` |
| Fingerprint previous 344-record private index SHA-256 | `66a987550fdeb5b6ff3711d49ab673578be68418a1978b33126f6127deed763c` |
| Runner Git blob | `4f7dddd52833362a52068527a3db78c2b0845578` |
| Owner-only raw results SHA-256 | `ebdde253504c0af94ad3fce55731220707e5420f7dd1bbec2b0084b8dde56eee` |
| Independent blind input BLIND64 SHA-256 | `4288c311f22147a85a414fd436fbeba1287464bb60d745ca64e5ce07839158f1` |
| Owner safe summary SHA-256 (PowerShell) | `7bb65aaee2d44ee2705a6911234ab980d8b02957278a547e7ffda9e90c9cb86d` |

Tệp nguồn `D1_EXP32_SAFE_SUMMARY.json` đã được đọc lại qua kết nối Windows và chép nguyên nội dung vào `artifacts/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXP32_ACTUAL_CPU_ONE_SHOT_OWNER_SAFE_SUMMARY_20261112.json` (chỉ thêm LF cuối file trên GitHub theo chuẩn truyền tải). Source run output ở `_tmp/TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112/` có ba tệp: `D1_EXP32_OWNER_PRIVATE_RAW.json`, `D1_EXP32_BLIND64_PRIVATE.json`, `D1_EXP32_SAFE_SUMMARY.json`. **Không mở raw owner hay BLIND64 trong phiên phân tích**, không công khai văn bản/mapping/seed.

## 2. Kết quả khoa học teacher-forced

Đã hoàn tất **96** candidate scores từ **16 gia đình × 2 biến thể dữ kiện** ở short/near, với **16 prior trung tính**. Score dùng mean log probability của completion cố định. Cả hai biến thể có margin đúng (>0) trong:

- **Thô `S=1/16` (6,25%).**
- **Prior-adjusted `S'=2/16` (12,5%).**

| Category | Thô | Prior-adjusted |
|---|---:|---:|
| `entity_location` | 1/4 | 1/4 |
| `causal_reasoning` | 0/4 | 0/4 |
| `rule_constraint` | 0/4 | 0/4 |
| `goal_persistence` | 0/4 | 1/4 |

Mean margin `mA=+0.1854904783331262`, `mB=-0.14583747140427547`; prior-adjusted `mA'=+0.03926357842805772`, `mB'=+0.0003894285007930154`. Ngưỡng mô tả **tín hiệu yếu khám phá** trong thiết kế D1 (cùng chính subset short/near 16 family) là `S≤4` và `S'≤4`. Cả hai đều đạt phạm vi này, nên ghi **`TEACHER_FORCED_FACT_CHOICE=WEAK_EXPLORATORY_SIGNAL`**. Đây là mô tả ở DEV, không phải bác bỏ hay xác nhận mô hình ở TEST hoặc suy luận nhân quả về nội bộ mô hình.

## 3. Kết quả sinh văn bản — descriptive only

**64/64** bản sinh mới, cùng checkpoint và 32 prompt; 32 greedy và 32 nucleus `top_p=0.9`, `temperature=0.8` với seed đầu tiên đã khóa của V2, cap 32 token.

| Metrics | GREEDY | NUCLEUS |
|---|---:|---:|
| Văn bản | 32 | 32 |
| `eos_early_count` | 14 | 0 |
| Mean new tokens | 28,875 | 32 |
| `empty_text_count` | 0 | 0 |
| `total_repeated_trigram_windows` | 213 | 8 |

Hiện tượng lặp 3-token giảm từ 213 xuống 8 trên các số đếm thô, nhưng độ dài đầu ra khác nhau; đây **không phải** kiểm định hiệu quả chuẩn hóa hoặc thước đo chất lượng nội dung. Dữ liệu trên **không nói** rằng nucleus tốt hơn về fact, nhân vật, mục tiêu, coherence, hay pair-success, vì `blind_rater_scored=0`.

14 kết thúc EOS trước cap của greedy không được quy kết là lỗi nặng hay có ích nếu thiếu chấm văn bản và phân phối vị trí EOS.

## 4. Trạng thái pháp lý khoa học và bước tiếp theo

- `EXPLORATORY_DEV32_EXECUTION=PASS_EXECUTED_SCOPED`.
- `TEACHER_FORCED_FACT_CHOICE=WEAK_EXPLORATORY_SIGNAL`.
- `DECODER_REPETITION_DIFFERENCE=DESCRIPTIVE_ONLY`.
- `BLIND64_GENERATED=YES_SHA_LOCKED`, `RATER_SCORES=0/64`, `SCIENTIFIC_FINAL_ADJUDICATION=PENDING`.
- `CONFIRMATORY_D1_512=HOLD_UNCHANGED`, `TEST_Q1Q2=SEALED`, `GPU_CALLS=0`, `TRAINING=NO`, `LINEAGE=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_EXP32_BLIND64_INDEPENDENT_GPT6_RATER_SCORE_FREEZE_AND_OWNER_SCOPED_ADJUDICATION`.

Chủ sở hữu đính kèm **duy nhất** file mù local `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112\D1_EXP32_BLIND64_PRIVATE.json` trong một phiên ChatGPT mới không có ngữ cảnh nghiên cứu, cùng rubric/handoff đã cập nhật `TTM_SMALL4M_D1_EXP32_BLIND64_CHATGPT_INDEPENDENT_RATER_HANDOFF_20261112.md`. Agent chấm 64 record, khóa điểm và SHA-256 trước giải mù. Không gửi owner raw, mapping, seed hoặc bảng tổng hợp này vào phiên chấm. Khi nhận điểm riêng tư và receipt, owner nối nhãn **sau** khi kiểm tra SHA, phân tích factual adherence và tiếp tục quyết định nghiên cứu. Không cần ký hoặc tái chạy preexec.

Không đề xuất chạy lại DEV32, chọn seed đẹp, tăng số lượt sinh hậu nghiệm, hoặc biến exploratory thành confirmatory.
