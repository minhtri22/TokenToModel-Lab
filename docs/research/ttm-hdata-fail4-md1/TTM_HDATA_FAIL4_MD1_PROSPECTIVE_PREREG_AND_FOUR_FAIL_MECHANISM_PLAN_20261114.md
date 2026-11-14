# TTM-Small-4M — MD1: Chẩn đoán tiền đăng ký bốn FAIL H-DATA-S1 bằng dữ liệu hoàn toàn mới

**Operation:** `TTM_HDATA_S1_POST_ADJUDICATION_CLOSEOUT_AND_NEW_PROSPECTIVE_MECHANISM_DIAGNOSTIC_DESIGN_ONLY`  
**Ngày:** 2026-11-14 · **Loại:** DESIGN-ONLY / SOURCE-ONLY · **Nhánh mới:** `research/ttm-hdata-s1-fail4-prospective-mechanism-design-20261114`  
**Tiền nhiệm bị đóng:** `TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1`, nguồn adjudicated HEAD `ef4cc05037f98129082cd429a75092b8cc822efb`  
**Nghiên cứu mới:** `TTM_HDATA_FAIL4_MD1_PROSPECTIVE_20261114`  
**Phán quyết mở thiết kế:** `GO_PROSPECTIVE_DESIGN_ONLY__HOLD_NEW_DATA_CUSTODY_AND_ALL_SCIENCE_UNTIL_INDEPENDENT_PREEXEC_AND_OWNER_GO`.

## A. Đóng phạm vi cũ — không đảo kết quả

H-DATA-S1 đã hoàn tất `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT`: hai nhánh H0/H1 cùng 128 cập nhật từ parent bước 1024, kết thúc bước 1152; VAL NLL H0 `3.511285912623514`, H1 `3.5057606759493716`; 24 cặp FINAL đã tiêu thụ và chấm mù độc lập với 240 điểm, 24 ghi chú, SHA khóa trước giải mù. Ánh xạ AES đã mở **một lần** theo GO và cất riêng. Kết luận khoa học của thí nghiệm cũ không thay đổi.

Các điểm **FAIL gốc cần chẩn đoán, không được đổi tên hay sửa ngưỡng**:

| ID | Điều kiện tiền đăng ký | Quan sát đã khóa | Quan hệ |
|---|---|---|---|
| **F1** | Mean H1−H0 trên điểm actor+object+goal ≥ **+0.5/3** | **0.000** | Độ lớn hiệu ứng |
| **F2** | Ít nhất **16/24** cặp H1 thắng chặt | **0/24** | Phương của hiệu ứng |
| **F3** | Cận dưới 95% CI bootstrap ghép cặp (20,000, seed 20261113) **>0** | **0.000** | Độ chắc chắn của hiệu ứng |
| **F4** | Mean delta H1−H0 của `goal_or_rule_progress` **>0** | **0.000** | Riêng tiến triển mục tiêu/quy tắc |

**Không phải bốn nguyên nhân độc lập.** F1/F2/F3 cùng suy ra từ việc tất cả **48 đoạn tiếp nối được một AI rater chấm 0 ở ba trục chính**; F4 là thành phần mục tiêu cũng bằng 0 ở hai nhánh. Giảm VAL NLL không đồng nghĩa bảo toàn ngữ nghĩa. Mức điểm mạch lạc còn thấp (0.7083/3 và 0.6667/3), trong khi 17/24 H0 và 20/24 H1 chạm trần 64 token — các chỉ báo mô tả, **không** giải thích nguyên nhân.

## B. Câu hỏi cơ chế và thứ tự ưu tiên

**Q0 — Measurement floor:** Người chấm AI có nhận diện được bằng chứng actor/object/goal rõ ràng trong các đoạn đối chứng do người thiết kế chuẩn bị trước hay đánh 0 cả khi đúng? Không thể chẩn đoán mô hình khi hệ đo chưa được hiệu chuẩn.

**Q1 — Shared model floor:** Khi cả H0 và H1 dùng câu chuyện *mới*, ít nhiễu và mục tiêu tường minh, có đạt khả năng duy trì ngữ nghĩa tuyệt đối không? Nếu cả hai vẫn ở sàn nhưng rater đạt kiểm soát, đó là **ứng viên shared-generation floor**, không phải bằng chứng phủ định mọi khả năng.

**Q2 — Context / goal accessibility:** Tăng thông tin nhiễu (semantically neutral distractor), và làm mục tiêu từ tường minh sang ngầm định, có tạo suy giảm *trong cùng lõi truyện* không? Đây là hai phép đối chứng bắt cặp; không suy từ 24 cặp lịch sử đã tiêu thụ.

**Q3 — Representation versus generation:** Ở cùng lõi truyện mới, H0/H1 có đặt xác suất chuẩn hóa cao hơn cho một tiếp diễn đúng (oracle) so với tiếp diễn sai (foil), trong khi greedy generation vẫn không thực hiện được mục tiêu? Nếu có, chỉ kết luận **ứng viên nghẽn ở sinh/chọn token**, chưa đủ chứng minh cơ chế.

Quy trình chặn: **M0 người chấm → M1 đầu ra mới → M2 hai tương phản yếu tố → M3 teacher-forced oracle/foil**. Một FAIL đầu vào thì HOLD tại đúng giai đoạn, không cố mở thêm để “cứu” ngưỡng.

## C. Dữ liệu hoàn toàn mới và khóa trước quan sát

### 1) M0: Bộ hiệu chuẩn thước đo (measurement calibration), độc lập với dữ liệu mô hình

Sáng tác **32 lõi đối chứng mới**, mỗi lõi một tiếp diễn **positive** bảo toàn cả actor/object/goal và một **negative** trái cả ba. Tổng **64 văn bản kiểm chuẩn** (32 pos + 32 neg); bốn strata, mỗi strata tám lõi. Khóa rubric, nhãn chuẩn và SHA riêng tư **trước** hai đợt chấm mù độc lập. Không chọn các câu từ H-DATA FINAL24, TinyStories TRAIN/VAL hoặc quá trình dò hyperparameter; không dùng đối chứng này làm prompt kiểm định mô hình.

Hai người chấm độc lập (nếu đều là AI phải ghi là `EXPLORATORY_SCOPED_AI_REVIEW`, không phải human gold). Mỗi rater, mỗi trục nhị phân phải đạt **sensitivity ≥28/32** và **specificity ≥28/32**; **agreement giữa hai rater ≥0.85 trên từng trục** với các đối chứng nhãn rõ ràng. Nếu bộ gold tự nó mơ hồ hoặc bộ kiểm định không đạt, **HOLD** và xin độc lập rà soát nhãn/thiết kế cho một phiên khảo sát tương lai, không sửa điểm cũ, không chọn rater theo kết quả FINAL. M0 không chứng minh độ phù hợp với human gold nếu không có người chấm thật.

### 2) M1: Lõi truyện mới ghép cặp 2×2, không nhập dữ liệu đã tiêu thụ

Thiết kế **16 lõi truyện mới**, gồm bốn strata × bốn lõi mỗi strata:

- `object_custody`: actor giữ/giao một vật qua bước có quy tắc.
- `social_relation`: actor nhận/trả lời một cam kết với nhân vật khác.
- `causal_obstacle`: mục tiêu chỉ tiến triển khi xử lý đúng trở ngại.
- `temporal_rule`: hành động đúng phải tuân thứ tự trước/sau.

**Mỗi lõi có đúng bốn biến thể** của cùng actor/object/goal:

| Yếu tố 1 — Context | Yếu tố 2 — Goal |
|---|---|
| `SHORT`: prefix 64–96 BPE token | `EXPLICIT`: mục tiêu nêu rõ |
| `DISTRACTOR`: prefix 144–176 BPE token | `IMPLICIT`: mục tiêu suy ra hợp lý nhưng duy nhất |

Bốn ô: SHORT+EXPLICIT, SHORT+IMPLICIT, DISTRACTOR+EXPLICIT, DISTRACTOR+IMPLICIT. Distractor phải trung tính, không thêm actor, object, goal mới và không thay sự thật nhân quả trong core; các biến thể chia sẻ core có chủ đích.

Mỗi strata: **lõi 1 cho DEV** (1 core ×4 variants) và **lõi 2–4 cho LOCKED FINAL** (3 cores ×4 variants). Toàn bộ: **4 DEV core/16 DEV prompts** và **12 FINAL core/48 FINAL prompts**; nếu sinh từ hai checkpoint thì **96 continuations FINAL**. Không sử dụng bất kỳ prompt/text/notes/ánh xạ FINAL24 cũ để tạo lõi mới. Toàn bộ prompt, nhãn bí mật và cặp oracle/foil tương lai phải có SHA-256 riêng, lưu owner-private; public GitHub **chỉ nhận SHA commitment và metadata**, không chứa văn bản FINAL.

Cổng khóa dữ liệu: 64 unique variant IDs, 16 distinct cores, DEV/FINAL tách theo **core** không theo biến thể; kiểm exact SHA so với mọi hash lịch sử đã biết; kiểm trùng bên ngoài core, phân biệt sự giống nhau có chủ ý bên trong core; kiểm quyền nội dung, PII, BPE exact roundtrip và **`len(prefix)+64<=256`** cho mọi biến thể; khóa gold/controls, rater contract và random balanced blind mapping **trước** khi nhìn thấy đầu ra. Không tuyên bố sạch toàn bộ TRAIN/TEST khi chưa thực sự kiểm nguồn.

### 3) M2: Đo trên hai checkpoint H0/H1 đã khóa, không train

Đây là **đề xuất triển khai sau này, KHÔNG chạy trong lượt DESIGN-ONLY**. Nếu owner GO riêng, dùng checkpoint H0 step1152 `a7cdade3...` và H1 step1152 `31d9365a...` như mẫu đã khóa, P02 3,749,376 params/BPE2048/context256, **plain greedy 64 token hoặc EOS256**, không penalty, sampling, re-rank hoặc tune.

Tạo blind map AES **mới cho nghiên cứu MD1**, không dùng lại AES H-DATA cũ; mỗi core bốn ô có LEFT H0 hai lần, LEFT H1 hai lần; mỗi điều kiện 2×2 trên 12 FINAL cores có **6/6**; mỗi strata có **6/6**. Map được khóa/kiểm SHA trước forward. Hai fresh-chat raters chấm các 48 cặp, mỗi người **480 điểm nguyên, 48 notes**, freeze SHA trước giải mù. Không sửa hoặc ghi đè điểm sau freeze. Đơn vị suy luận/bootstrap là **12 lõi truyện độc lập**, không phải 48 biến thể hay 96 văn bản.

### 4) M3: Các chỉ báo cơ chế đã đăng ký trước

- **Absolute short-explicit floor:** với 12 FINAL cores, cả hai nhánh có `goal_progress <0.25` trung bình ở điều kiện SHORT+EXPLICIT, trong khi M0 đạt → `SHARED_GOAL_GENERATION_FLOOR_CANDIDATE`. Không suy thành nguyên nhân kiến trúc.
- **Context interference:** within-core mean `SHORT−DISTRACTOR` trên ba trục ngữ nghĩa ≥**0.25** và lower 95% cluster-bootstrap >0 → `CONTEXT_INTERFERENCE_CANDIDATE`; còn lại `INCONCLUSIVE`.
- **Goal explicitness:** within-core mean `EXPLICIT−IMPLICIT` của goal-progress ≥**0.25**, lower 95% cluster-bootstrap >0 → `GOAL_SIGNAL_EXTRACTION_CANDIDATE`; còn lại `INCONCLUSIVE`.
- **Oracle vs foil:** với 12 FINAL cores, cặp tiếp diễn đúng/sai được khóa **trước** mô hình, chênh BPE token-length ≤2 **và** ≤5%, không chỉnh sau khi xem đầu ra. Nếu normalized teacher-forced log-likelihood oracle > foil trên ít nhất **9/12 cores** ở một nhánh trong khi tiến triển mục tiêu khi greedy sinh vẫn kém, báo `GENERATION_SELECTION_GAP_CANDIDATE`. Nếu điều kiện độ dài không đạt, HOLD M3, không làm “matched foil” hậu nghiệm.

Khoảng tin cậy cho hai tương phản cơ chế dùng **20,000 bootstrap resamples seed 20261114 trên 12 cores**; với nhiều phép thử và cỡ mẫu nhỏ, đây là tiêu chí *ứng viên chẩn đoán khám phá*, **không phải chứng minh nhân quả/độ tin cậy family-wise**. Báo cả effect size, CI, tỷ lệ zero, coherence, consistency, EOS/cap64, thất bại từng strata và phân bố disagreement. Các nguồn lỗi có thể cùng tồn tại.

## D. Điều kiện GO/HOLD; chống lặp và thiên lệch hậu nghiệm

**Được thực hiện trong lượt này:** soạn hợp đồng tiền đăng ký, thiết kế dữ liệu mới, chỉ đọc kết quả công khai đã adjudicated, viết/kiểm nguồn tĩnh, commit evidence SHA và append-only lineage trên **nhánh mới**.

**Chưa được phép:** sinh/lộ dữ liệu LOCKED FINAL mới, đọc/gỡ niêm phong old FINAL24 hoặc điểm cũ để chấm lại, truy cập TEST/Q1/Q2/OOD, dựng mới ánh xạ AES, forward H0/H1, huấn luyện, lựa chọn prompt sau quan sát hoặc chạy GPU. Mọi phép đo trên 64 prompts/2 mô hình/2 người chấm là **kế hoạch**, không có kết quả.

**Cổng tiếp theo tích hợp duy nhất** cần độc lập QA cả thiết kế, bộ tạo dữ liệu/rights, nguồn đối chứng, lịch khóa SHA và gold, đầy đủ 2×2 và 16/48 core split, rater calibration độc lập và quyền sử dụng H0/H1/Colab. Chỉ khi PASS mới trình **một quyết định owner GO/HOLD**, không mở micro-permit. Nếu FAIL, `HOLD_SOURCE_OR_MEASUREMENT`; không gọi đó là khoa học.

**Final design decision:** `GO_PROSPECTIVE_DESIGN_ONLY__HOLD_NEW_DATA_CUSTODY_AND_ALL_SCIENCE_UNTIL_INDEPENDENT_PREEXEC_AND_OWNER_GO`. Old H-DATA scientific outcome remains immutable. `lineage.md` append-only; branch `main` unchanged.
