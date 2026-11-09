# TTM — Quy tắc đánh giá hợp nhất `main` cuối mỗi lượt và kiểm kê nhánh

**Ngày:** 2026-11-09 · **Trạng thái:** `PROPOSED_FOR_PR12_REVIEW`; không tự sửa lịch sử P00–P12/ADR-0001. Không tạo nhánh mới để viết tài liệu này.

## 1. Bắt buộc cuối mỗi lượt công việc

Trong mỗi phản hồi kỹ thuật TTM, đưa phần `ĐÁNH GIÁ HỢP NHẤT VỀ MAIN` gồm:

| Trường | Bắt buộc |
|---|---|
| `MAIN_SHA / WORK_SHA` | SHA đã xác minh ở cuối lượt; ghi `UNKNOWN` khi chưa đọc được |
| `CHANGE_SCOPE` | Các tệp, phase, run & liên quan runtime/science |
| `QA_EVIDENCE` | PASS/FAIL/HOLD, nguồn chứng minh và kiểm định độc lập (không đồng nhất mock với native) |
| `SCIENCE_AND_LINEAGE` | Giữ FAIL khoa học, TEST một lần và `lineage.md` append-only |
| `SENSITIVE_DATA` | Không commit dữ liệu corpus, TEST, checkpoint, secrets nếu chưa xác minh quyền |
| `MERGE_DECISION` | `READY_FOR_REVIEW`, `HOLD`, `NOT_MERGEABLE`, `MERGED` và lý do cụ thể |
| `NEXT_MERGE_ACTION` | Một hành động hữu hạn để loại bỏ blocker; không mở nhánh khi chưa cần |

Hợp nhất đòi kiểm nguồn, backend parity theo scope, QA độc lập, negative tests, chứng cứ nguồn/giấy phép, diff và branch state, bảo toàn lineage, không mở phase P07/P09/P10 ngoài thẩm quyền. **`mergeable=true` là tín hiệu GitHub không có xung đột, không phải chứng nhận chất lượng.** Không bắt buộc merge khi science FAIL nếu phạm vi chỉ ghi nhận một FAIL trung thực; nhưng không được biến một chức năng lỗi thành chức năng đã đạt.

## 2. Kiểm kê thực tế (GitHub read-only ngày 2026-11-09)

- Repository `minhtri22/TokenToModel-Lab`; main `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`; **10 nhánh** tổng cộng, **1 PR mở: #12 DRAFT**.
- PR #12 HEAD trước kế hoạch `76607c212b77e217ae881b40f60b8e7e6242041e`, **116 commit, 178 tệp** so với main. Bao gồm 45 tệp `docs/pilot`, 59 `evidence/pilot`, 54 mã/vi/docs khác; **thay `lineage.md`**. `main/lineage.md` là prefix **nguyên byte** của `PR12/lineage.md`; hai entry khoa học L0011–L0012 được thêm đúng append-only.
- GitHub HEAD PR #12 **không có check-runs được báo cáo**. Trạng thái `mergeable=true` không loại bỏ cổng QA, kiểm bảo mật và scope review.
- `feature/p07-paged-attention-kernel-design-20261107`: 9 ahead, 3 behind main, **PAUSED_PRESERVE**; không merge/xóa.
- `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`: 118 ahead main nhưng phân kỳ PR12 (5 ahead/3 behind). Công việc thay tokenizer/embedding khác mục tiêu chất lượng TTM: **DEFER_SEPARATE_REVIEW**, không cherry-pick vào #12 lúc này.
- `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`: 34 ahead main, 116 behind PR12; nhánh thiết kế khác: **DEFER**.
- `research/ttm-six-cross-model-representation-transfer-20261109`: SHA **bằng main**, chưa có diff; **SAME_SHA_REVIEW_FOR_REF_RETIREMENT** (không xóa tự động).
- `governance/train-first-colab-and-branch-consolidation-20261108`: 0 ahead, 1 behind main, đã trở thành ancestor; **REDUNDANT_REF_REVIEW** (không xóa tự động).
- 3 nhánh `archive/p01-*`: **PRESERVE_FROZEN** để truy xuất; không dùng `--prune`, `--force`, không xóa local.
- `research/ttm-small-4m-colab-pilot-prereg-20261108`: tiếp tục làm head của #12; **không tạo nhánh riêng cho Q1/Q2** trong khi PR #12 đang kiểm soát.

## 3. Phân xử PR #12 lúc này

**`MERGE_DECISION=HOLD_SCOPE_AND_INDEPENDENT_QA`**, không phải FAIL khoa học. Đã có bằng chứng science T4 H1 VAL PASS, TEST descriptive PASS; T5 GGUF+Ollama import/inference PASS; strict F32 parity FAIL 7/8 được bảo toàn. PR title/body hiện mô tả trạng thái **design-only cũ** — cần cập nhật để không làm reviewer hiểu sai.

Các điều kiện đóng merge:
1. Giữ nguyên tiền tố `lineage.md`, xác minh L0011/L0012 đúng receipts, ghi rõ TEST đã tiêu thụ và không rerun.
2. Rà soát độc lập mã + 178 paths của PR #12, kiểm không có checkpoint/dataset/token/secret/thư viện nhúng bất hợp lệ; xác nhận nguồn/bản quyền TinyStories theo phạm vi thí nghiệm và quy tắc công bố.
3. Thực thi QA hồi quy hợp nhất trên cây HEAD cuối (T1–T5 source/import checks), tránh tái chạy TRAIN, sealed TEST hoặc one-shot đã tiêu thụ; báo cáo full QA thật, không chỉ mock.
4. Tách nhãn kết quả: T4 `PASS_H1_VAL`, T4 TEST `PASS_DESCRIPTIVE`, T5 Ollama `PASS_RUNTIME`, T5 strict logits `FAIL_7/8`, P07 `PAUSED`. Không sửa ngưỡng hay che FAIL.
5. Quyết định `MERGE_READY` riêng sau khi QA PASS và phạm vi PR đã duyệt. Giữ HEAD main và origin/local căn chỉnh; merge qua PR với kiểm tra HEAD mới. Không auto-merge; nếu merge thành công, đọc lại main SHA, cây tệp, lineage và các bằng chứng.
6. Nếu scope quá lớn không thể review an toàn, **đề xuất** phân đoạn tài liệu/kỹ thuật theo nhóm chức năng trong cùng PR hoặc một kế hoạch kế nhiệm hữu hạn (phải có quyết định riêng) thay vì thêm 5–10 nhánh lẻ.

## 4. Quy tắc nhánh mới

Mặc định **không tạo nhánh mới** khi PR hiện tại có thể quản lý cùng workstream. Chỉ tạo khi công việc độc lập thực sự hoặc cần tách nguồn/phase, và phải chỉ ra merge target, exit gate và thời điểm đóng. Không xóa ref, worktree hay dữ liệu của dự án khi chưa có quyết định chính xác từng tên/đường dẫn.

**Bước tiếp theo cho hợp nhất:** `TTM_PR12_INTEGRATED_READONLY_DIFF_SECURITY_LINEAGE_AND_QA_MERGE_GATE`; còn Q1/Q2 chạy sau khi khóa đánh giá theo tài liệu kế hoạch bên cạnh.
