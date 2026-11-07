# TTM — P01: tiêu chí đóng tinh gọn và đường chuyển sang P02

Ngày: 2026-11-07. Đối chiếu `docs/PHASE_PLAN.md`, `docs/p01/P01_LEAN_EXECUTION_PLAN_AND_REMAINING_SCOPE_REVIEW_20261106.md` và các nhánh GitHub. Đây là rà soát điều phối, không thay đổi tiêu chí đã duyệt và không tự đóng phase.

## 1. Kết luận về thời điểm mở P02

**P01 chưa thể đóng chỉ bằng S1 native PASS.** P01 gốc yêu cầu Tokenizer B0/B1, dữ liệu có quyền, round-trip, leakage, SHA-256, tái lập hai tiến trình, đo lường và QA độc lập. Theo lộ trình, P02 mới phát triển Transformer Core; P03 mới huấn luyện GPT; P04 đánh giá và lưu checkpoint.

Bản rà soát Lean ngày 06/11 ghi rõ:
- `F0_10_OF_10_PASS` là QA offhost cho fixture, **không phải** P01 closure.
- `L1`: các gap còn thiếu cho B0/B1 oracle, dedup transitivity/ngưỡng, split 30+ nhóm synthetic và cross-split 0.
- `L2`: F1 source/rights `HOLD` đến khi có manifest cho phép thật; đường nạp F1 và runtime guard phải phù hợp. **Không** nạp F1/TEST trái quyền.
- `L3`: E0 trên TRAIN-only được khóa, B1 hai tiến trình sạch có cùng SHA, round-trip 100%, leakage 0, metrics B0/B1 và QA độc lập.
- `K4` C09 Windows native W01–W12 là bắt buộc **nếu E0 sử dụng tuyến Windows cần kiểm soát bảo mật đã xác định**; không biến mỗi thao tác kiểm tra kỹ thuật nhỏ thành một giấy phép riêng.

**Không có bằng chứng trong hai tài liệu đó buộc mọi thử nghiệm S1–S5, bất kể rủi ro và đường E0, phải hoàn tất trước P02.** Trường hợp S1 có liên quan đến K4 phải giải quyết trong một gói QA native có giới hạn, chứ không được tự động thay thế các mục tiêu Tokenizer/dữ liệu. Không tự bỏ cổng K4 khi có nguy cơ thực.

## 2. Bảng đường găng thực tế

| Nhóm | Điều kiện kết luận | Tình trạng theo tài liệu Lean 06/11 và đọc lại 07/11 |
|---|---|---|
| K1 B0/B1 | Byte/Unicode round-trip 100%, oracle và tái lập deterministic | F0 10/10 đã PASS, còn bài tích hợp bổ sung và E0 |
| K2 H03 | Dedup/transitivity, split >=30 nhóm, 0 raw/canonical/group overlap | Chưa có PASS đầy đủ, cần batch tích hợp |
| K3 H02 | F1 rights manifest ALLOW và PII admission | HOLD, chưa xác minh được nguồn đủ quyền |
| K4 H05 | Guard theo tuyến E0, native W01–W12 nếu thực thi Windows E0 theo hợp đồng | Chưa đủ bằng chứng native; không được claim PASS |
| K5 E0/B1 | TRAIN-only BPE hai tiến trình SHA trùng, metrics B0/B1, TEST niêm phong, QA độc lập | Chưa thực hiện |

Đây là **trạng thái theo bằng chứng đã đọc**, không phải tuyên bố toàn bộ môi trường Windows hiện tại đã được kiểm toán mới. Không suy đoán ngày chắc chắn mở P02.

## 3. Chặn vòng QA dư thừa

Một gói công việc kỹ thuật sử dụng ba bước `Preflight → Implementation/Integrated Test → Independent QA/Adjudication` theo kế hoạch đã phê duyệt. Không tự cấp giấy phép riêng cho AST, SHA, đọc receipt, biến thể âm khi cùng phạm vi.

- Giữ tất cả receipt FAIL, PASS và marker đã khóa, không overwrite; `lineage.md` append-only kết quả khoa học.
- S1 tiền nhiệm: permit và marker `CONSUMED_FAIL` do lỗi chuyển tiếp `$args`, host/S1 chưa chạy.
- S1 kế nhiệm: Host/runner nguồn mới gắn ID permit/marker/output root riêng; source-only independent QA 47/47, 10/10; **không** suy ra Win32 native PASS.
- Nếu có quyết định native kế nhiệm, một lượt duy nhất được điều kiện hóa bởi xác minh SHA/PS51 parser/SCM/permit/preflight và marker CreateNew; lỗi dừng, giữ receipt, không retry.

## 4. Bước dự án ưu tiên để tiến sang P02

`TTM_P01_CANONICAL_L1_L2_L3_EXIT_GAP_CLOSE_AND_P02_OPEN_DECISION`

1. Chốt K1/K2 trong một batch QA trên synthetic, tái sử dụng 10 F0 PASS; không làm lại những bài không thay đổi.
2. Nhận/kiểm chứng F1 có quyền sử dụng hợp lệ cùng manifest, split >=30 nhóm, và cổng runtime phù hợp trước E0. Khi thiếu nguồn, ghi `HOLD_SOURCE_RIGHTS`; không tuyên bố P01 đóng.
3. Khi L1/L2 PASS, tiến hành E0 BPE TRAIN-only có khóa, QA độc lập và một phán quyết P01 cuối. Sau merge/closure hợp lệ mới mở P02, rồi P03 huấn luyện và P04 đánh giá.

Chỉ thay đổi **thứ tự ưu tiên công việc**, không thay đổi kiến trúc, hợp đồng B0/B1, tiêu chí khoa học, lịch sử hoặc lộ trình P00–P12.
