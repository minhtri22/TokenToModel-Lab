# TTM-Small-4M — Bộ kiểm tra tổng hợp 2×2 và quyết định đóng băng có điều kiện

**Ngày:** 2026-11-10  
**Nhiệm vụ:** `TTM_SMALL4M_2X2_EQUAL_BUDGET_TRAIN_SAMPLER_LOSS_SYNTHETIC_PREFLIGHT_AND_OWNER_FREEZE`  
**Nhánh độc lập:** `research/ttm-small4m-prompt-conditioning-objective-design-20261110`, tạo từ `main` `b57b44e7287f842e81050c1faee337f636333dd0`.  
**Phán quyết:** `SYNTHETIC_QA=PASS_SCOPED`; `SCIENCE_OWNER_FREEZE=HOLD_PENDING_COMBINED_GATES`; `NEW_TRAINING=0`. Không được coi hồ sơ này là chữ ký phê duyệt một lượt Colab T4.

## 1. Quy chiếu nguồn và kết quả khoa học đã biết

- [Thiết kế 2×2 nguyên bản](TTM_SMALL4M_PROMPT_CONDITIONING_TRAIN_OBJECTIVE_EQUAL_BUDGET_2X2_DESIGN_20261110.md); [ma trận bốn nhánh dạng JSON](../../artifacts/qa/ttm-small4m-prompt-conditioning/TTM_SMALL4M_EQUAL_BUDGET_2X2_DESIGN_CANDIDATE_20261110.json). Lưu ý JSON hiện ở mức `DESIGN_ONLY`, không phải một science lock.
- `src/p02/transformer_core.py`: Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; huấn luyện T4 source Git blob `76c4d0155cd0736919f41682f240b47ad3d7c428`; xây TRAIN windows `cdce219f2a2df27e25579f069238d4327c1d7d91`; đánh giá VAL `bef006bdff173fba6d8ba4aa0ef687a1732fd7c4`.
- Checkpoint cha step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, dữ liệu TRAIN/VAL pack riêng tư SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; các tệp này **không** được đọc trong preflight.
- Bằng chứng tiêu cực FRESH12 đã giải mù (PR #13 commit `8399406cfca7855626a20e031d1cfb3c767d606f`): 35/48 đoạn có điểm bám prompt = 0; Δ bỏ dấu cách cuối − giữ dấu cách cuối = **0,000/3**; `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED` bởi reviewer Codex AI đơn lẻ. Không dùng lại prompt FRESH12 làm bộ đánh giá xác nhận mới.

## 2. Bộ chạy đã triển khai và thực thi ngay trên CPU

GitHub source-of-truth dưới `tools/pilot_t4/prompt_conditioning_2x2/`:

- [`ttm_2x2_equal_budget_synthetic.py`](../../tools/pilot_t4/prompt_conditioning_2x2/ttm_2x2_equal_budget_synthetic.py) — tạo 40 truyện tổng hợp, 64 cửa sổ tổng hợp (40 first, 24 later), replay sampler 128 bước bằng RNG riêng, thay thế first-window có điều kiện đủ `count`, chia các arm A/B/C/D, kiểm tra ngân sách, kế hoạch lấy mẫu và cross-entropy có trọng số.
- [`test_ttm_2x2_equal_budget_synthetic.py`](../../tools/pilot_t4/prompt_conditioning_2x2/test_ttm_2x2_equal_budget_synthetic.py) — **72/72 PASS** (valid fixtures, replay, fail-closed, gradient, nhãn đệm, định mức, 4-arm integration).
- [`independent_result_audit.py`](../../tools/pilot_t4/prompt_conditioning_2x2/independent_result_audit.py) — bộ kiểm toán read-only không import mã runner, tái cộng toàn bộ 128 × 4 lịch, kiểm digest và thử **20 đột biến (negative mutants), 20/20 bị từ chối**.

**Phạm vi tuyệt đối:** Các câu chuyện/tokens đều được tạo giả định. Không mở dữ liệu TRAIN/VAL thật, không mở TEST/Q1Q2, không nạp checkpoint, không tạo mô hình/optimizer, không train, không sinh truyện. CPU Python 3.13.5 / PyTorch 2.10.0+cpu trong sandbox kỹ thuật, không phải Colab Free T4. Preflight này xác minh logic đếm ngân sách/mask/loss **trên fixture**, không chứng minh khả năng khởi tạo và chạy 3,75M params trên T4.

## 3. Kết quả đo thực tế của synthetic fixture

| Hạng mục | Arm A | Arm B | Arm C | Arm D |
|---|---:|---:|---:|---:|
| Bước logic | 128 | 128 | 128 | 128 |
| Nhãn được chấm mỗi bước | 4.096 | 4.096 | 4.096 | 4.096 |
| **Nhãn được chấm tổng** | **524.288** | **524.288** | **524.288** | **524.288** |
| Số forward windows | 3.585 | 3.585 | 3.585 | 3.585 |
| Forward token slots | 917.760 | 917.760 | 917.760 | 917.760 |
| First-story window được rút | 2.243 | 3.585 | 2.243 | 3.585 |

- Tổng cộng **2.097.152** lượt nhãn được chấm trong thiết kế cả bốn arm, **không** phải 2.097.152 nhãn TRAIN mới, không phải 2.097.152 lượt huấn luyện đã thực thi.
- **A/C khớp exact** lịch id/count/hash; **B/D khớp exact** lịch id/count/hash. Mỗi bước giữa 4 arm có đúng cùng số forward windows, 256 positions/window và số microbatch với `microbatch_windows=8`. Sau thay thế, **3.427** vị trí rút sử dụng window ID khác baseline; đây chỉ là số trên fixture giả lập.
- Kiểm loss gốc bằng PyTorch CE; weighted loss so bằng triển khai `logsumexp` độc lập; khi logits đồng nhất thì trọng số được chuẩn hóa và loss không tự bị nhân lên 3. Gradient trên `-100` bằng 0; các vị trí suffix có đạo hàm **3 lần** các vị trí prefix ở trường hợp logits đồng nhất và target bằng nhau.
- Trường hợp âm tính được từ chối: window VAL/TEST, source ID trùng, index/offset/count không hợp lệ, nhãn sai shift hoặc pad, out-of-vocab, không đủ first-window đạt count, không đủ 4.096 nhãn, sai lịch A/C hoặc B/D, sai forward/microbatch, label loss ngoài miền, NaN, batch shape sai; 20 mutations trong audit kết quả đều fail-closed.
- **Hai lần chạy synthetic được đối chiếu byte-exact**: full JSON SHA-256 `1f92b9fe5965591ce6f8292e778642081c2ad9c1557ea08b5538f536524ac409`. File nguồn/biên bản có SHA-256 riêng trong receipt.
- Trước khi đóng băng, hai *test fixtures* từng fail vì kiểm tra điều kiện đầu vào sai; đã sửa fixture, không sửa logic chạy để né lỗi; lượt cuối **72/72 PASS**, lưu log cuối. Không có lượt khoa học nào bị tiêu thụ trong bước này.

## 4. Các bất định không được tự chuyển thành PASS

1. **Chưa xác minh count-match trên 2.691 windows thật**. Candidate first-window phải có `count >= n` cho từng lượt của bản A/C, không được tự bổ sung kể cả một nhãn `-100` vào loss. Cần kiểm tra read-only trên **metadata TRAIN-only có SHA**, không đọc văn bản riêng tư hoặc tập TEST. Nếu không thể match 128 × 4.096 trong dữ liệu thật, giữ `HOLD_MATCHED_DRAW_PLAN` và sửa thiết kế trước mọi huấn luyện.
2. **Chưa có runner huấn luyện thật bốn arm** từ checkpoint cha với sao chép chính xác AdamW/RNG/scheduler/GradScaler. PyTorch loss hiện mới chạy với tensor logits tổng hợp nhỏ và không có model step / fp16 CUDA. Tránh nhận `MODEL_TRAINING_READY=PASS` từ test 72/72.
3. **Equal budget khác equal information/compute time**: cùng số nhãn và forward slots, nhưng số truyện khác nhau, sự lặp lại, gradient weighted loss, GPU thời gian/energy và AdamW trajectory có thể khác. B/D chỉ thay phân phối đầu truyện; suffix positional weighting chưa là hướng dẫn ngữ nghĩa rõ ràng.
4. **Quyền nguồn chưa được xác nhận riêng cho science mới**: dataset TinyStories trên Hugging Face khai báo `cdla-sharing-1.0` (metadata truy xuất 2026-11-10), nhưng license metadata không tự thay thế review về khai thác và phát hành; không dùng WP30/P01 F1 làm quyền huấn luyện GPT.
5. **Chưa có 12 DEV + 24 FINAL prompt mới**, rubrics/Latin-square bị khóa, người chấm độc lập chưa tiếp nhận, chưa xác nhận không trùng (Q1/Q2/TEST vẫn niêm phong). Không dùng FRESH12 cũ để chọn phương án sau kết quả.
6. **Science owner authorization không tồn tại**. `P09/P10` chưa mở, `PR13` còn draft, `main` không thay đổi.

## 5. Một quyết định tổng hợp cho chủ dự án — OWNER FREEZE

**Đề nghị có hiệu lực đối với nguồn thiết kế:** `FREEZE_SYNTHETIC_2X2_DESIGN_CANDIDATE=YES`; giữ immutable source SHA và kết quả PASS/FAIL kỹ thuật trên GitHub. Không mở PR merge tự động. Không cần nhiều micro-permits cho từng phép đo kỹ thuật.

**Quyết định thực thi khoa học:** `NO_GO_COLAB_T4_NOW / HOLD`. Các cổng chưa đủ là nguồn và quyền, matched-count TRAIN-only, readiness full checkpoint/optimizer, bộ đánh giá mới/rater, một khóa science owner cho **một** batch bốn arm. Việc đóng băng thiết kế **không** có nghĩa chủ dự án đã phê duyệt thực thi science.

**Một gate tổng hợp tiếp theo:** `TTM_SMALL4M_2X2_REAL_TRAIN_METADATA_MATCHED_DRAWS_AND_COLAB_RUNNER_QA_PLUS_EVAL_RIGHTS_SINGLE_OWNER_DECISION`:

- Xác minh theo SHA read-only pack TRAIN metadata, chứng minh count-match đủ 128 bước/arm và lưu digest schedule, không mở TEST.
- Xây runner Colab 4-arm chỉ chạy synthetic CPU QA trước, bảo toàn checkpoint/optimizer/RNG và loss denominator, một batch/4 run IDs tách riêng. Có thể tạo source/QA mà chưa huấn luyện; chưa cho GPU science.
- Kiểm tra quyền TinyStories + tạo 12 DEV/24 FINAL prompt mới được kiểm chứng và phân reviewer độc lập; đóng băng trước inference khoa học.
- Tổng hợp 3 hạng mục trên vào **một biên bản** để chủ dự án quyết định `SCIENCE_RUN_APPROVE_4_ARMS` hoặc `HOLD`, không chia các kiểm tra kỹ thuật nhỏ thành cấp phép riêng.
- Nếu được phê duyệt: checkpoint cha là **step1024**, **4 arm × 128 steps**, 4.096 target/step, cùng batch token slots, một one-shot riêng cho 4 arms; lưu checkpoint READY-last và QA. Không tái chạy historical 1024→1280. Nếu bất kỳ nguồn/budget/quality gating nào FAIL phải ghi đúng FAIL/HOLD, không tự đổi siêu tham số hoặc thêm dữ liệu.

## 6. Source of truth và bảo toàn lịch sử

Giữ source + test + audit + full per-step result + receipt trên GitHub trong **nhánh nghiên cứu độc lập**. Repository là public; không commit private TRAIN/VAL/TEST tokens, checkpoint, secret mapping hoặc dữ liệu cá nhân.

- Main SHA ban đầu: `b57b44e7287f842e81050c1faee337f636333dd0` (lineage blob `971fbd8eccdf4719fee6b83a3c0f4c44b13ebaa9`, đến **L0012**).
- PR #13 HEAD ban đầu: `8399406cfca7855626a20e031d1cfb3c767d606f` (lineage blob `15c67ada3b11c46e2d947bef8818599c7408733c`, đến **L0017**).
- Nhánh này kế thừa lineage của **main**, không phải PR #13; cả hai bản đều phải giữ nguyên byte. Không merge, không append lineage từ design-only QA.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_2X2_REAL_TRAIN_METADATA_MATCHED_DRAWS_AND_COLAB_RUNNER_QA_PLUS_EVAL_RIGHTS_SINGLE_OWNER_DECISION`.

**Trạng thái cuối:** `SYNTHETIC_PREFLIGHT=PASS_72/72` · `ARITHMETIC_AUDIT=PASS` · `NEGATIVE_MUTANTS=REJECTED_20/20` · `REPEATABILITY=PASS_EXACT` · `REAL_PACK_MATCHING=NOT_CHECKED` · `RIGHTS=HOLD` · `EVAL_FREEZE=HOLD` · `COLAB_SCIENCE=NO_GO` · `NEW_TRAINING=0` · `MAIN=UNCHANGED` · `PR13=HOLD` · `LINEAGE=UNMODIFIED`.