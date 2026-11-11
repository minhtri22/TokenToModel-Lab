# TTM-Small-4M — Rà soát GitHub/local và quyết định tích hợp AC–FRESH16 hậu CF1

**Ngày:** 2026-11-11 (Asia/Bangkok)  
**Công việc:** `TTM_SMALL4M_DATA_OBJECTIVE_EXISTING_AC_AND_FRESH16_SINGLE_INTEGRATED_SCIENCE_READINESS_GAP_REVIEW_DESIGN_ONLY`  
**Trạng thái:** `DESIGN_ONLY_SOURCE_AND_LOCAL_READONLY_AUDIT`; không thực thi khoa học.  
**Phạm vi:** mô hình TTM-Small-4M gốc O0, decoder-only P02, checkpoint step1024; không đồng nhất với EmbeddingGemma2, SIX, O1 hay T5/T6.

## 1. Phạm vi kiểm chứng và bất biến

Dùng GitHub connector đọc trực tiếp repository `minhtri22/TokenToModel-Lab`, tập hợp các nhánh và PR, báo cáo hậu CF1, thiết kế AC, biên bản tiền thực thi AC, hồ sơ FRESH16 đã khóa và kiểm toán độc lập mới nhất. Dùng RemoteDesktop **chỉ đọc** để kiểm tra thư mục gốc, Git HEAD/ref, danh sách worktree và biên nhận QA native có sẵn. Thử Git status/worktree/branch read-only bằng RemoteDesktop run_command đều bị từ chối `managed mode requires task_job_submit`, nên không giả nhận đã chạy được `git status`.

Không chạy suy luận (inference), huấn luyện (training), chấm lại TEST/Q1Q2/FRESH12/CF1, thử thách toy mới, lệnh ghi local, tự động `git fetch/pull/merge/checkout`, mở FINAL đã niêm phong, hay can thiệp vào khoá mù. Không chỉnh `main`, PR #13, `lineage.md`, các ngưỡng và checkpoint đã khóa.

## 2. GitHub và local repository — ảnh chụp chỉ đọc

| Hạng mục | Bằng chứng quan sát | Ý nghĩa |
|---|---|---|
| GitHub `main` | `5d52e32f20021e36f08f284ef9864d3ba36dbead` | Nhánh mặc định |
| Local `.git/HEAD` | `ref: refs/heads/main` | Worktree gốc đang trỏ `main` |
| Local `.git/refs/heads/main` | `b57b44e7287f842e81050c1faee337f636333dd0` | Chậm hơn GitHub 146 commit, 0 commit đi trước; GitHub compare xác nhận quan hệ tổ tiên |
| Local `.git/refs/remotes/origin/main` | `d4ec548727ba85625d1bf2684d85ec9e6867572b` | Ref theo dõi không đồng nhất với GitHub main đang quan sát |
| Local FRESH16 worktree ref | `research/ttm-small4m-prompt-adherence-continuation-design-20261111`, local SHA `6c4ba3946d6ddd3d0b4dcdc8348f7f734289d2e2` | Không giả định local đã chứa phụ lục/kiểm toán GitHub mới nhất |
| GitHub FRESH16 research head | `23dd0f73656a2882c54f8d27a0280511f06fd2ce` | Đã có commit phụ lục diễn giải và kiểm toán sau ref `1583...` |
| Local Git worktree metadata | Có CF1, FRESH16, T6, Ollama, review R2A, các worktree P00/P01 và khác | Chỉ kiểm được sự tồn tại; tình trạng file sửa/xóa/chưa commit **UNKNOWN** |
| PR mở | #13, #14, #15; đều là bản nháp (draft), chưa hợp nhất | Không tự động hợp nhất/dọn |
| PR lịch sử | 13 đã hợp nhất, #4 đã đóng nhưng không hợp nhất | Không xem trạng thái PR thay cho chất lượng khoa học |

**Cổng an toàn local:** `LOCAL_GIT_DIRTY_STATUS=NOT_VERIFIED`; cấm đồng bộ và dọn branch/worktree cho đến khi có `git status --porcelain` và `git worktree list --porcelain` chính chủ. Không đọc/di chuyển tệp khoá riêng tư.

**Quản trị lineage:** `lineage.md` local có mục kỹ thuật lịch sử. Quy tắc nghiên cứu hiện hành là chỉ nối thêm phán quyết khoa học PASS/FAIL đã được phân xử. Không sửa hồi tố sổ đã có và không append biên bản rà soát kỹ thuật này.

## 3. Ba năng lực không được gộp thành một kết luận

- **Ngôn ngữ dự đoán (next-token modeling):** T4 VAL 256 truyện, model NLL 3,5223388517 so với TRAIN-only bigram 3,9972314170; cải thiện 11,880537%, `PASS_H1_CONFIRMATORY_VAL_SCOPE`. TEST lịch sử đã tiêu thụ: chỉ được dẫn thống kê, không mở lại.
- **Sinh tiếp nối (free-form continuation):** FRESH12, 48 đoạn và 35/48 đoạn bám prompt mức 0; reviewer AI đơn, không có bằng chứng đáng tin về nâng chất lượng khi bỏ dấu cách cuối. Bước 1024→1280 giảm NLL VAL 3,52234→3,49809 nhưng không tăng bám prompt ở đánh giá nhỏ đã tiêu thụ.
- **Đổi ưu tiên phản thực (counterfactual preference switching):** CF1 DEV36 không có cặp đảo ưu tiên 0/36; bài thử có lối tắt từ vựng và cấu hình vị trí đáp án A=x/B=y; `FAIL_SCOPED` không được suy ra bất lực suy luận phổ quát.

Giới hạn chung: chưa xác định nguyên nhân yếu là dữ liệu, hàm mất mát, sức chứa hoặc kiến trúc. Không dùng một phép đo NLL để suy ra mạch lạc truyện.

## 4. Rà soát tính nhận dạng nhân quả (causal identifiability)

Thiết kế 2×2 **đã có** ở nhánh `research/ttm-small4m-prompt-conditioning-objective-design-20261110`:

| Arm | Lấy mẫu TRAIN | Hàm mất mát | Đối chứng nhân quả nếu cùng ngân sách |
|---|---|---|---|
| A | Gốc | Cross-Entropy đều | Chuẩn |
| B | Thay bằng cửa sổ đầu truyện đếm nhãn khớp | Cross-Entropy đều | `B−A`: lựa chọn dữ liệu |
| C | Gốc, cùng draw với A | Cross-Entropy có trọng số hậu tố | `C−A`: vị trí của loss |
| D | Cùng draw chọn dữ liệu với B | Cross-Entropy có trọng số hậu tố | `D−B`, `D−C`, tương tác `(D−B)−(C−A)` |

**Bất đồng phải giải quyết:** Kế hoạch AC đã triển khai chỉ có A/C, chung lịch draw, 128 bước/arm, 4096 target labels/bước, tổng 1.048.576 target presentations, nguồn parent step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. A dùng Cross-Entropy đều; C nhân trọng số 3 từ vị trí token 32 trở đi (trước đó weight 1). **A/C cô lập một thao tác thay trọng số loss theo vị trí, không so sánh dữ liệu khác nhau, không trực tiếp giám sát nhân vật/mục tiêu.** Dù đạt ngưỡng, claim cao nhất chỉ là hiệu ứng can thiệp loss theo vị trí trên tập đo khóa.

Ngược lại 2×2 có thể kiểm tra dữ liệu so với loss và tương tác, nhưng B/D chưa đủ điều kiện khoa học về tính khả thi của draw khớp, quyền dữ liệu, đánh giá mù và thực thi thực. Không được tự nâng AC hai nhánh thành 2×2 hoặc dùng checkpoint step1280 cũ làm đối chứng ngân sách.

**Khuyến nghị:** Giữ A/C làm can thiệp nhỏ hơn, độc lập, nếu người sở hữu chọn câu hỏi `loss có giúp bám prompt không?`; không quảng bá thành quyết định `data vs objective`. Muốn phân biệt hai nguyên nhân cần một so sánh `B−A` công bằng, và để đo tương tác cần đủ 2×2, nhưng mọi việc mở rộng đòi hỏi quyết định khoa học mới trước thực thi, không phải vòng toy chống heuristic.

## 5. FRESH16 — cổng đo năng lực trước khi suy luận

Nguồn khóa: 16 prompt/8 cặp; 32 đầu ra CPU tối đa, H1≥12/16 với adherence≥2, H2≥6/8 cặp và ít nhất một cặp/category. BPE và nguồn đã PASS theo biên nhận. Tuy nhiên kiểm toán giao thức độc lập mới nhất báo **3 PASS, 5 HOLD, 0 FAIL**; chỉ là đánh giá thiết kế, không phải kết quả neural.

Bốn trở ngại thực:
1. Dạng điền chỗ trống (cloze) có thể được tính nhầm là sinh một diễn biến mới — cảnh báo F01;
2. Cặp CP04/CP08 có thể cùng chấp nhận hành động chung, làm phép phân biệt phản thực thiếu đặc hiệu — cảnh báo F02;
3. Phụ lục diễn giải `cloze-only ≤ 1`, gắn cờ `common valid action` đã được **soạn nhưng chưa được chủ dự án/phản biện giao thức duyệt trước kết quả**; đó là thay đổi cách chấm có ý nghĩa, không phải tự động áp dụng rubric cũ;
4. Người chấm đầu ra độc lập, packet mù, quy trình khóa điểm và lệnh science một lần chưa có.

Quyết định `FRESH16=NO_GO_HOLD`. Không thay câu prompt, đổi ngưỡng H1/H2, loại cặp khỏi mẫu số hoặc dùng FRESH16 làm kết quả đánh giá của AC. Đây là khảo sát năng lực O0 ở một quần thể prompt riêng, không thay thế 24 FINAL prompt riêng của AC.

## 6. AC — các cổng chưa đóng, phân biệt lỗi thực với lỗi giả

AC có 24 FINAL prompt và biên nhận niêm phong (escrow) công khai cho 24 cặp, cân bằng vị trí 12/12; bộ dữ liệu TRAIN/VAL được tham chiếu SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. Tiền kiểm tổng hợp/lý thuyết và kiểm nguồn trước đây có bằng chứng PASS theo phạm vi.

Cổng khoa học còn thiếu: xác nhận phạm vi sử dụng private pack của chủ sở hữu; lưu giữ khóa escrow owner-only an toàn; reviewer có danh tính/nhận trách nhiệm; QA native Windows Python 3.12 và FP16 T4 zero-step smoke; khôi phục thực tế (actual interrupted resume parity); science lock mới.

**Bằng chứng local mới kiểm:** `_tmp/TTM_AC_NATIVE_PREEXEC_6628401b08ea/NATIVE_SOURCE_QA_RESULT.json` ghi `HOLD_NATIVE_QA_FAILED`, nhưng source Git blob, syntax compile và source QA đều `true`; test đầu tiên báo `ok`, còn `synthetic_resume_tests=false`. Biên bản GitHub phân loại incident `PS51_STDERR_REDIRECTION_WITH_ERRORACTIONPREFERENCE_STOP`; bản script sửa V2 đã stage nhưng `actual_windows_v2_executed=false`. Vì vậy **không** gọi đây là thất bại khoa học hay một lỗi của mô hình. Tuy nhiên cũng **không** gọi 6/6 kiểm thử native PASS khi stdout/stderr chưa được đọc đầy đủ. Không chạy lại trong lượt thiết kế này.

## 7. Một quyết định GO/HOLD và trật tự ưu tiên

**Quyết định hiện tại: `GO_DESIGN_REVIEW_COMPLETE__HOLD_SCIENCE_EXECUTION`.**

- **PASS phạm vi nguồn:** GitHub branch/PR, bằng chứng hậu CF1, 2×2/AC và tình trạng FRESH16 được đối chiếu; đã phân biệt đúng mối quan hệ A/C so với 2×2.
- **HOLD FRESH16:** phải khóa diễn giải rubric được phản biện chấp thuận, định danh người chấm và niêm phong quy trình trước 32 đầu ra.
- **HOLD AC:** đóng một gói điều kiện owner rights + escrow custody + reviewer + Windows V2 native readback + T4 zero-step/actual resume; rồi mới trình đúng một quyết định science A/C. Các QA nguồn đã PASS không chạy lại nếu bytes không đổi.
- **HOLD lựa chọn nguyên nhân dữ liệu:** không có B−A trong AC, chưa được phép kết luận dữ liệu tốt/xấu hơn loss.
- **DEFER O1/MoE/Attention/scale:** không mở kiến trúc thay thế trên cơ sở các tín hiệu đang nhiễu.
- **Không mở thử nghiệm toy mới**, không chấm lại tập tiêu thụ, không tạo micro-permit. Không hợp nhất hoặc xoá nhánh.

## 8. Bước thực hiện tiếp theo

`TTM_SMALL4M_ORIGINAL_FRESH16_PROTOCOL_OWNER_RATER_AND_AC_NATIVE_V2_SINGLE_READBACK_DECISION_NO_SCIENCE`

Trong **một lần**: (a) chủ sở hữu/phản biện giao thức quyết định chấp thuận hay bác bỏ phụ lục FRESH16 **trước output**; định danh reviewer chấm đầu ra và cách khóa điểm; (b) chỉ đọc và xác nhận biên nhận QA native V2 AC nếu chủ sở hữu đã thực thi, không chạy lại những kiểm nguồn PASS; (c) xác nhận bằng chứng quyền private pack/escrow owner/reviewer và T4 zero-step/resume nếu thực sự có; (d) đưa ra 2 phán quyết riêng nhưng gộp một biên bản: `FRESH16_CPU32_GO_OR_HOLD` và `AC_T4_2ARM_GO_OR_HOLD`. Nếu bất kỳ điều kiện bắt buộc nào chưa được thỏa, vẫn HOLD. Không cấp quyền khoa học trong bước này.

**Bất biến:** `TRAINING=0` · `NEW_INFERENCE=0` · `TEST_Q1Q2_FRESH12_CF1=UNTOUCHED` · `MAIN/PR13/LINEAGE=NOT_WRITTEN` · `LOCAL_WORKTREES=NOT_MODIFIED` · `GITHUB_RESEARCH_DOC_ONLY`.
