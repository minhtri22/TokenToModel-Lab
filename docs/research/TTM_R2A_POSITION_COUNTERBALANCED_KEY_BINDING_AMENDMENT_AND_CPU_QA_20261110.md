# TTM R2A — Counterbalanced Position & Key Binding (Amendment to R2)

**Ngày:** 2026-11-10 · **Task:** `TTM_SMALL4M_R2_POSITION_COUNTERBALANCED_KEY_BINDING_TOY_AMENDMENT_AND_SINGLE_CPU_QA`.  
**Phạm vi:** sửa đặc tả **toy grammar** sau phản biện Codex nội bộ, **không huấn luyện TTM, không inference checkpoint, không GPU**. Kết quả R2 gốc giữ nguyên, không sửa/hủy bằng chứng đã khóa.

## A. Vì sao sửa

Codex đánh giá R2 gốc tại commit `b1325d61bac07587d07ac7b48b9ad47e4284f1a9`. Báo cáo nội bộ tại `D:\WORK\RESEARCH\TokenToModel-Lab\artifacts\qa\r2\codex_adversarial_20261110_b1325d6\TTM_R2_CODEX_ADVERSARIAL_REVIEW_20261110.md` (owner-supplied SHA256 `194edaf52ee94ea9dddd8e9cba2056c0110d3612e3db771ec515642694bcf54e`). Lỗi HIGH: vị trí target có mẫu cố định `[target,distractor,target,distractor]`, nên đọc **câu 3 đạt 256/256** dù không hiểu câu hỏi. Checker gốc quá hạn chế cập nhật ở câu 4; `counts` không được đối chiếu và bộ input có thể chứa answer/source_events. H-ORDER chỉ PASS như định lý bag-of-words, **H-STATE (learned) vẫn HOLD**.

## B. Sửa thiết kế trước khi đánh giá

- Vẫn giữ **128 cặp A/B** (64 nhóm ownership, 64 goal), **256 story/question pairs**, cùng câu hỏi cho A/B, cùng **word multiset** và đáp án đối lập. Mỗi truyện vẫn **4 câu**.
- Thay pattern vị trí cố định bằng **cả 6 tổ hợp** chọn 2 trong 4 vị trí cho key được hỏi; phân bổ trong từng `family × split` để đúng **50%** số câu cuối liên quan key và **50%** là distractor. Hai lần cập nhật trái nhau cho key chính, hai lần trái nhau cho key nhiễu; A/B chỉ hoán đổi **hai cập nhật của một key**.
- Chia mỗi family 32 nhóm `DEV` và 32 nhóm `CHALLENGE`; CHALLENGE dùng khung câu khác (`has ... now`, `intends to ...`) và mẫu câu hỏi khác. Đây là kiểm tra parser có hỗ trợ thêm grammar; **CHALLENGE được công khai, không phải blind test hoặc kiểm chứng tổng quát hóa mô hình**.
- Thêm **128 query-binding probes**: dùng cùng truyện A, nhưng hỏi key khác đang được cập nhật; đáp án khác. Như vậy mỗi story đòi hỏi đọc câu hỏi, không thể luôn chọn một câu cố định.
- Tách **oracle dataset** khỏi **model-input projection**. Dữ liệu đưa vào model (nếu thực thi khoa học sau này) chứa **chính xác `story,question`**, hoàn toàn không có `answer`, `source_events`, `variant`, `split`, `family`, `id` hoặc `pair_id`. Checker đối chiếu projection exact với oracle nguồn.
- Bộ kiểm đối lập **không import generator**, phân tích cú pháp trực tiếp text thành 4 sự kiện và truy vấn key; đối chiếu tất cả fields, source_events, declared counts, 6 position patterns, nhãn split và probes. Không đọc TEST/Q1Q2/Private TRAIN/VAL.

## C. Kết quả CPU preflight (author-side, không phải neural science)

| Mục | Kết quả |
|---|---:|
| Mô tả A/B, cùng word multiset | 128/128 |
| Bản ghi đối chứng đảo sự kiện | 256 |
| Bộ kiểm văn bản độc lập xác định đúng | **256/256** |
| Bài đổi câu hỏi trên cùng truyện | **128/128** |
| Đối chứng không biết thứ tự (bag-of-words), giới hạn lý thuyết | **128/256 (50%)** |
| Đối chứng đọc câu thứ ba, bỏ qua câu hỏi | **80/256 (31,25%)** |
| Đối chứng đọc câu cuối, bỏ qua câu hỏi | **128/256 (50%)** |
| Quy tắc cập nhật *last relevant event for queried key* | **256/256 (100%)** |
| Câu cuối là target key | **128/256 (50%)** |
| CPU unit + adverse mutation suite | **36/36 PASS** (**17 kiểm tra khẳng định** và **19 ca mutation âm tính**; một số bị từ chối ở cổng đồng bộ model-input trước khi vào semantic parser, xem log) |

**Điểm thận trọng:** Bộ phân tích rule-based vẫn giải được 100% theo `last-write-wins` và câu hỏi, nên thử nghiệm **không buộc neural model học biểu diễn trạng thái nội tại**; nó chỉ loại bỏ lỗi fixed-third-sentence và kiểm tra key binding. Không nói mô hình GPT-2/P02 không thể giải bài, không tuyên bố O1 tốt hơn O0.

**Lưu ý tính toàn vẹn QA:** Lần chạy nháp đầu, ca `test_36_public_holdout_not_sealed` FAIL vì assert sai (cố tìm *không có* từ `TEST` trong dòng tuyên bố *“not sealed TEST”*). Chỉ assertion này được sửa thành kiểm tra tuyên bố `not sealed TEST`; không sửa dữ liệu sinh, parser hoặc 35 ca kiểm tra còn lại. Một lần QA cuối **36/36 PASS**. Hai log nháp/cuối có SHA riêng, không lấy lần nháp làm PASS.

### SHA-256 nguồn và hiện vật được khóa

| Hiện vật | SHA-256 |
|---|---|
| Generator `r2a_generator.py` | `e9f7df99d09a2aa449173db1358449515772b9c54778d75f775eae04f5447326` |
| Checker `r2a_independent_checker.py` | `5224707f32688d1582ab80939e844902848f896fdb52596d136904a0ec34d191` |
| Tests `r2a_single_cpu_qa.py` | `96fb5e494c75230331238f7b03361c61e9de58e197efd2dce76d17d4b229bc8e` |
| Oracle JSON uncompressed | `3243d1eaae4b8727449fe4571dc81c898414b5ba300a20e7ead0819d7953286e` |
| Model-input-only JSON | `72f57d704a2e4f99f06a797b8b647d93736a7093852e0c9df0f28dc59549032d` |
| Independent check JSON | `76920a16525b4feaa2bed9e49abbea620b91cc3982fae93d0f353a76b326a967` |
| QA log final | `6efc7fa9f1517f082b5b881942ae99a54224f8308204d496d093b648c1867159` |

Dataset nguồn **183.830 byte**, model-view **60.734 byte**. Hai tập dataset sử dụng JSON được đóng gói riêng thành **gzip deterministic mtime=0 rồi base64**; manifest ghi số byte, SHA-256 nguyên bản và hướng khôi phục. Không tuyên bố đây là TEST ẩn, không sử dụng hoặc thay đổi nội dung TTM private.

## D. Quyết định về O0 / O1

- **R2 FORMAL_TOY:** `VALID_SCOPED_WITH_POSITION_SHORTCUT_FIXED`; HIGH reviewer issue được xử lý ở cấp design fixture.
- **R2 LEARNING:** `NOT_EXECUTED`. 100% rule-based không đồng nghĩa mô hình neural đạt được.
- **O0:** Giữ thiết kế 2×2 data-sampler/loss ở HOLD và làm baseline.
- **O1:** **DEFER khoa học**. Có thể thiết kế prospective O0 vs O0-supervised-text vs O1-shuffled-label vs O1-true-label vs capacity-matched, cần kiểm soát lượng thông tin giám sát, số tham số, FLOPs, số seed, tách oracle khỏi inference; chưa có authorization mới.
- **Codex:** Đã có review R2 gốc. **Không giả nhận Codex đã review amendment R2A**; chỉ chuyển gói R2A cho một lượt source critique khi cần, không cần reviewer bên ngoài cho nghiên cứu nội bộ.

**Bảo toàn:** chỉ ghi nhánh R2 `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`; không sửa R2 cũ, P02, checkpoint, 2×2, main, PR #13, `lineage.md`. `NEW_TRAINING=0`, `GPU=0`, `TTM_INFERENCE=0`, `TEST_Q1Q2=UNTOUCHED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_R2A_INDEPENDENT_ADVERSARIAL_REVIEW_AND_O0_O1_FAIR_SUPERVISION_STUDY_DESIGN`, không cấp quyền training cho đến khi O0/O1 có đối chứng ngữ nghĩa tương xứng.
