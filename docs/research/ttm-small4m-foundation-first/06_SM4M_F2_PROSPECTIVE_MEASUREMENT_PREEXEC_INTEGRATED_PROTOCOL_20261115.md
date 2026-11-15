# TTM-Small-4M — SM4M-F2: Prospective Measurement Pre-execution Integrated Protocol

**Ngày:** 2026-11-15  
**Operation:** TTM_SMALL4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_DESIGN_SINGLE_GATE  
**Phạm vi:** FOUNDATION FIRST / F2 / SOURCE+DESIGN ONLY; không sáng tác item, không rater, không forward, không GPU, không huấn luyện, không quyền merge.  
**Nguồn đóng thiết kế:** owner closure `c233dff20b9b020aefd732ce62bfa2e7aebd3985`; nguồn thiết kế MD1 `33021a421f05bb3bfa0999ad12bc3bd144366da9` (Git blob `384d077600ed864a917fdd5e74b5a5bca0ed8766`); F2 roadmap blob `d87309aea043b845fafcc805ed13b2b4466f5e46`.  
**Current state:** `AUTHOR_DESIGN_CANDIDATE · DISTINCT_QA_PENDING · F2_PREEXEC_BLOCK=TRUE · SCIENCE_HOLD`. Đây **không phải** một tiền đăng ký được owner ký cho execution.

## 1. Vấn đề khoa học, estimand và ranh giới kết luận

H-MEAS: zero scores ở H-DATA-S1 có thể do model không giữ dữ kiện, evaluator không nhận ra câu đúng, hoặc cả hai. A/C FINAL24 có điểm tuyệt đối A=C=0.6667/3 (delta=0), **khác** H-DATA H0=H1=0/3; không pooling các protocol. T4 NLL tốt hơn bigram không hàm ý giữ actor/object/goal.

**Đối tượng kiểm định duy nhất ở F2 này:** chất lượng phép đo actor, object, goal theo rubric được định nghĩa trước, không phải chất lượng checkpoint. Ngay cả rater qua mọi đối chứng mới, vẫn **không chứng minh** rater đáng tin trên phân phối đầu ra T4 hoặc nguyên nhân model FAIL. Không tạo mô hình, prompt/model output, gold, source rights attestation hay điểm mới trong gate thiết kế.

Ba tầng nằm **trong một chương trình đo lường F2**, không mở ba research phases:
- `M0-ORIGINAL` = calibration cực tính nhị phân rõ ràng theo MD1, giữ nguyên `32 cores×2 =64` items, `111/000`, thresholds và 4 strata×8.
- `M0X-AXIS` = **proposed, not frozen** factorial per-axis + same-core single-axis contrasts, nhằm phân biệt global-valence shortcut. Thiết kế bổ sung không dùng item M0 làm dữ liệu đánh giá mô hình.
- `M0U-UNKNOWN` = **proposed, not frozen** thử thách thiếu bằng chứng/ambiguous và xử lý abstention, không đưa mẫu số UNKNOWN vào M0 hoặc M0X.

Ký hiệu `1/0` trong M0X là gold đúng/sai **riêng từng trục**. `UNKNOWN` là không xác định được từ nguồn, **không phải** nhãn sai 0. Mọi biến thể cùng core phải được source/gold kiểm tra độc lập để bảo đảm chỉ trục dự định thay đổi về ngữ nghĩa.

## 2. M0-ORIGINAL — tái sử dụng MD1 bất biến, không chỉnh threshold

- 32 lõi (4 strata ×8); một positive đúng cả actor+object+goal và một negative sai cả ba mỗi core; 64 item IDs, 2 independent blind raters cùng item set.
- Mỗi rater và từng axis: `TP+FN=32`, `TN+FP=32`, `sensitivity=TP/32 ≥28/32` và `specificity=TN/32 ≥28/32`; agreement ≥0.85 từng trục giữa hai rater. F2 bản trước **đề xuất** định nghĩa raw exact agreement `matches/64` (≥55/64), chưa tuyên bố là công thức đã khóa trong MD1.
- Nếu input, gold, rubric hoặc item IDs không hợp lệ: `HOLD_INPUT_INTEGRITY` trước tính điểm; không loại bản ghi để đạt ngưỡng. M0 FAIL → `HOLD_MEASUREMENT`; không đánh FAIL model. M0 PASS → chỉ `CALIBRATION_CLEAR_POLARITY_SCOPED_PASS`, tuyệt đối không gọi `PER_AXIS_VALIDITY_PASS`.
- MD1 cũng đã thiết kế M1–M3, 16 cores/64 prompt variants và H0/H1, nhưng **ngoài phạm vi dispatch của gói này**. Không dùng FINAL24, TinyStories TRAIN/VAL, hay một checkpoint để tạo M0.

## 3. M0X-AXIS — full factorial *candidate* cho phép phát hiện shortcut (F01)

**Đề xuất số lượng, cần reviewer/owner phê duyệt trước khi dữ liệu ra đời:**
- `16 new independent cores` (4 strata ×4 cores), tách hoàn toàn khỏi 32 M0 cores và future M1/FINAL cores.
- Mỗi core có 8 continuations với **đúng một gold pattern mỗi loại**: `000,001,010,011,100,101,110,111`. Tổng `16×8=128` item IDs; mỗi pattern xuất hiện 16 lần. Mỗi axis có `64 gold-positive` và `64 gold-negative`. Đây là thiết kế 2³ cân bằng, **không phải 8 ví dụ đã được sáng tác**.
- Proposed strata (chưa đóng băng trong M0): `object_custody`, `social_relation`, `causal_obstacle`, `temporal_rule` như MD1 M1. Các stratum phải được independent construct QA kiểm trước bất cứ item creation.
- Trong từng core, 3 axis đối tượng là các **mệnh đề có nguồn gốc rõ**: actor identity/role đúng, object identity/custody đúng, goal/progress đúng. Nếu mệnh đề trục này suy ra trục kia hoặc thay actor đồng thời thay ownership/goal, **core không đủ điều kiện**: `HOLD_SEMANTIC_COUPLING`, không đoán nhãn từ bit-mask.
- **Single-axis edge pairs:** với mỗi trục, mỗi core có 4 cặp đối chứng 0↔1 trong khi hai bit còn lại cố định. Kế hoạch có `16×4=64 matched edges per axis`. Reviewer phải kiểm: item chỉ khác theo gold intended axis (không làm thay đổi sự thật hai trục kia), đồng thời lexical style và narrative fluency không đánh dấu nhãn. Chứng minh tổ hợp nhãn trên giấy **không chứng minh** semantic orthogonality.
- Thẩm định independent gold *trước khi rater chấm*: checker độc lập so từng 8-pattern item trong mỗi core; nếu semantic coupling hoặc item không thể phân loại, `HOLD_GOLD_QA` toàn packet, không thay bằng item mới sau khi nhìn điểm rater.
- Gold labels phải được khóa trước blind mapping/score. Không cho LLM tạo gold tự khẳng định đúng; nguồn nhân sự phải được ghi nhận chính xác. AI-only gold chỉ là `EXPLORATORY_AI_GOLD`, không được gọi là human-attested.

### M0X candidate scoring gates (mới, **CHƯA KHÓA**, không thay ngưỡng MD1)

Mỗi rater chấm 128 item IDs ×3 axes (384 quyết định nhị phân). Hai raters có 768 quyết định per-axis tổng cộng. Đề xuất acceptance sẽ cần được reviewer kiểm sức mạnh và trade-offs:
- Từng axis và từng rater: `TP+FN=64`, `TN+FP=64`; candidate sensitivity ≥`56/64` và specificity ≥`56/64` (mục tiêu 87.5%, chọn **đề xuất** để tương ứng tỉ lệ M0, **không phải ngưỡng MD1**).
- Từng axis mỗi rater: matched-edge *pair correctness* ≥`56/64` edge pairs (cả hai endpoint đúng về target-axis; hai invariant axes trên cả hai endpoint không bị chấm sai). Đây là gate chống global-valence shortcut riêng; candidate threshold chưa được independent QA.
- Inter-rater exact agreement từng axis trên cùng 128 opaque item IDs ≥`109/128` (raw rate ≥0.85), **mới đề xuất**, không retrofit vào MD1.
- Balanced pattern/stratum, per-pattern confusion and cluster-by-core uncertainty bắt buộc báo. 128 items có **16 core clusters**, không là 128 observations độc lập. Không gọi confidence interval item-iid là evidence confirmatory.
- **Anti-shortcut gates:** một hoặc nhiều proxy chỉ nhìn item style/length/lexical cues/order/category/format (không dùng semantic fact) phải không đáp ứng cùng bộ sensitivity/specificity/paired-edge threshold, dưới negative-control protocol khóa trước. Nếu proxy đạt → `HOLD_SHORTCUT` dù AI rater cao điểm. Phải khóa loại proxy, extractor, negative-control threshold và leakage exclusions *trước* item authoring; hiện chưa có các giá trị nào được thực nghiệm xác nhận.
- Gate hỗn hợp: đạt M0X không suy rằng model output score 0 là đúng, chỉ rằng rater phân biệt được controlled axis errors **trên bộ đối chứng đã nhận diện hợp lệ**.

## 4. M0U-UNKNOWN — ứng viên stress test cho trường hợp không đủ bằng chứng

**Đề xuất, chưa đóng băng:**
- `24 NEW independent cores ×1 continuation` (4 strata ×6 =24), không chồng core với M0/M0X hay future M1. Trong mỗi stratum, 2 cases cho mỗi target axis actor/object/goal → trên cả tập có `8 targeted-UNKNOWN cases per axis`.
- Với mỗi item, đúng một axis ở trạng thái `UNKNOWN/UNSCORABLE` theo gold độc lập, hai axes còn lại phải có kết luận 0/1 và không làm rò target. Reviewer không được ép inference từ ngữ cảnh thiếu bằng chứng.
- Hai raters trên cùng 24 items trả một trong `{0,1,UNKNOWN}` cho từng axis; 24×3×2 =`144` quyết định ternary dự kiến. Candidate targeted abstention ≥`7/8 per axis/rater`; false-certainty, coverage và error trên hai axis còn lại phải có threshold độc lập đóng băng trước chạy. 7/8 là **đề xuất**, không phải MD1 hay kết quả đo.
- Bất kỳ gold item nào bị independent reviewer nhận định là có thể suy chắc target axis, hoặc không thể kết luận hai axes còn lại, gây `HOLD_UNKNOWN_GOLD`. Thiếu/mơ hồ không được quietly map thành 0.
- Không pooling challenge UNKNOWN vào denominator 64 M0 hoặc 128 M0X, không dùng unknown-as-wrong để làm đẹp specificity.

## 5. Tổng ngân sách thiết kế, thứ tự đánh giá và stop rules

| Set | New cores | Continuations | Raters | Output scope |
|---|---:|---:|---:|---|
| M0-ORIGINAL (MD1) | 32 | 64 | 2 | polarity `111/000`; frozen MD1 thresholds |
| M0X-AXIS (proposed) | 16 | 128 | 2 | eight patterns, 64 paired edges/axis |
| M0U-UNKNOWN (proposed) | 24 | 24 | 2 | one unknown target axis/item |
| **Tổng đề xuất, chưa tạo dữ liệu** | **72** | **216** | 2 trên từng set | 432 item-rater assignments; 1296 axis-level decisions planned |

**Đơn vị độc lập là core**, không phải mọi continuation. Candidate allocations, rates và threshold ở M0X/M0U là prospective values để độc lập QA; **chưa hề được owner freeze**, phải duy trì `EXECUTION_NOT_AUTHORIZED`. Không định nghĩa adaptive second look nếu fail.

**Thứ tự có điều kiện duy nhất khi sau này được owner GO (không được chạy nay):** admission gói tổng thể trước hết → M0 ORIGINAL → nếu source/gold/threshold/scoring PASS mới xem M0X → nếu M0X PASS mới xem M0U. FAIL/HOLD ở một cổng chặn downstream; không chuyển sang thử M1/2/3, huấn luyện hay đổi architecture. Cần prospective stop rule cho score-stage không cần mở micro-permit; một permit tổng hợp ở thời điểm thích hợp phải ghi rõ lịch chạy và fail-closed checkpoint.

## 6. Scoring contract & provenance: thiết kế, không là runtime receipt

**M0 unchanged:** per axis per rater TP,FN,TN,FP; `TP+FN=32`, `TN+FP=32`; confusion×6 tổng; raw agreement proposal `matches/64≥0.85⇒≥55`. Không thay bằng Cohen κ mà không có amendment.

**M0X proposal:** per axis/per rater TP,FN,TN,FP; `TP+FN=64`, `TN+FP=64`; per-axis sensitivity/specificity, 64 matched edge results/rater/axis và invariant-axis checks, agreement matched/128; 8-pattern exact match, core-stratified logs, descriptive core-cluster bootstrap (n=16). Threshold mới phải được khóa trước gold authoring; `56/64` và `109/128` chỉ là **candidate author design**.

**M0U proposal:** 3-class confusion, targeted UNKNOWN sensitivity n=8/axis/rater; non-target binary accuracy; false certainty; NO_RELABEL. Candidate targeted ≥7/8 chưa frozen. Chặn zero denominator, missing, duplicates, invalid ID, incomplete raters, unblinded source or rubric changes.

**Gold & source rights:** owner-private human-source attestations nếu có, nếu không phải ghi AI-only exploratory. Rights/license/PII gate, new-source core/nonoverlap checks, exact tokenizer version and policy, no TRAIN/VAL/TEST/FINAL re-use, no private plaintext on GitHub. Scope SHA only once bytes exist; no fake hashes or pretend encrypted commitments are available now.

**Blinding:** owner-private distinct full manifest of core and opaque item IDs; two rater packets cùng item list nhưng independent sessions, frozen output SHA and raw responses before reveal; custodian giữ permutation map, source/gold freeze SHA before any ratings; score checker code/schema independently QA before dispatch. No post-hoc item exclusion, rater replacement based on observed scores, threshold amendment or rerun consumed tests.

## 7. Interpretation guard & read-across to existing science

| Kết quả sau này nếu hợp lệ | Điều được phép nói | Điều vẫn KHÔNG được nói |
|---|---|---|
| M0 PASS, M0X chưa PASS | Rater phân biệt cực tính rõ | Rater hiểu độc lập actor/object/goal |
| M0X PASS, M0U HOLD | Trên factorial gold hợp lệ, rater tách từng trục trong stress có phạm vi | Rater đáng tin trên output thiếu thông tin |
| M0, M0X, M0U PASS | Measurement qualification trên ba bộ thiết kế | Đã chứng minh model FAIL, measurement causality, human equivalence, hay kết quả FINAL cũ sai |
| Bất kỳ source/gold/rights/mapping fail | HOLD đúng phạm vi | Được chọn lại items, chấm lại FINAL, đổi ngưỡng hoặc train để cứu |

Không thay MD1 historical 4 FAIL (F1–F4 của H-DATA, khác `SM4M-IR-F01–F05` của Foundation First). Không lẫn với PR #20 F01–F04 governance. Không dùng FC01 exploratory là positive control của M0X.

## 8. Admission chỉ được ra một verdict, không phải chuỗi micro-permit

Các điều kiện nằm chi tiết ở tài liệu 07: exact source pin; original MD1 and owner closure unchanged; design/gold semantic isolation; sample/strata/threshold freeze; no leakage/cue-only shortcuts; rights/PII; blind rater, owner-private custody; scoring code/source QA; immutable manifests; independent reviewer; resource and checkpoint scope if a future model stage separately requested; owner science decision. **Tất cả hiện chưa đạt execution admission.**

**Current proposed verdict:** `AUTHOR_PREEXEC_DESIGN_PACKET_READY_FOR_DISTINCT_REVIEW · PREEXEC_BLOCK · NO_SCIENCE`. Reviewer distinct có thể cho `GO_DESIGN_SCOPED` hoặc `HOLD_REVISE_DESIGN` trên tài liệu, không có quyền cho `GO_EXECUTION`.

**Một bước kế tiếp:** distinct independent source & research-design review của exact candidate packet, một GO/HOLD về thiết kế. Chỉ sau owner adjudication mới được xem xét gói kiểm tra thực thi riêng; không làm tự động.
