# SM4M-Q001 — Q4 Owner Closure và quyết định merge tài liệu quản trị

**Operation:** `SM4M_Q001_Q4_OWNER_CLOSURE_AND_PR21_GOVERNANCE_ONLY_MERGE_GO_HOLD_SINGLE_GATE`  
**Question:** `SM4M-Q001` · **Ngày:** 2026-11-15 · **Repo:** [minhtri22/TokenToModel-Lab](https://github.com/minhtri22/TokenToModel-Lab).  
**Draft PR cần hợp nhất:** [#21](https://github.com/minhtri22/TokenToModel-Lab/pull/21) · **Base main tại quyết định:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`.  
**Reviewer Q3 independent PASS tại exact design/source candidate:** `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`.  
**Candidate branch HEAD khi owner phát lệnh GO:** `a8718ae6c00e0521019058f50c714d829b980313`.  
**Owner statement tại cuộc hội thoại:** “GO! cho việc đóng Q001 và merge PR #21 ở phạm vi tài liệu quản trị. Đồng ý ghi nhận bài nghiên cứu chuỗi suy luận dài vào phần mở rộng.”

## 1. Quyết định chính thức của owner — Q4

- **Closure:** `SM4M-Q001=Q4_CLOSED_HOLD_NEW_SCIENCE`. Câu hỏi được đóng **trong phạm vi evidence hiện có**, không phải đã giải quyết nguyên nhân thất bại Small-4M.
- **Baseline:** `KEEP_HISTORICAL_REFERENCE_ONLY` cho checkpoint T4 step1024 và các adjudication đã khóa.
- **Admission:** `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`. Không có benchmark/gold/AI-rater mới được admission; AD-00…AD-08 không tự nâng thành PASS.
- **Root cause:** `ROOT_CAUSE_NOT_IDENTIFIED`. Không có bug source architecture T4 đã xác minh đủ để bắt buộc sửa attention, FFN, Transformer hoặc trainer.
- **Q3 independent:** `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED`, **chỉ** trên exact reviewed HEAD `c37ac0b3901eb6fd9c658d818c02e85f66b7936e`. Q3-F01…F04 đã được reviewer xác nhận trong phạm vi source/design (18/18 symbolic independent checks).
- **Merge:** `MERGE_APPROVED_GOVERNANCE_DOCS_ONLY` cho **PR #21** sau kiểm tra diff/expected HEAD. Không tự merge code khoa học, FAIL/HOLD implementation, checkpoint/private data hay experimental runner.
- **Tài liệu tham khảo mới:** `SM4M-REF-PROSPECTIVE-001=OWNER_APPROVED_REFERENCE_ONLY` — [arXiv:2601.06002v2](https://arxiv.org/abs/2601.06002) được thêm vào danh mục nghiên cứu dài hạn về Long CoT/reasoning/Mole-Syn. Đây **không** là causal evidence Small-4M hay nguồn Q2/Q3 đã được reviewer khóa.
- **No new phase/permit:** `F0_F2_PAUSED`; `SCIENCE_NOT_AUTHORIZED`; `NO_NEW_RESEARCH_BRANCH`; `NO_NEW_GOLD_DATA_SCORER`; `NO_GPU_OR_MODEL_EXECUTION`; `NO_TEST_FINAL_REPLAY`.
- **Lineage:** `NO_SCIENCE_LINEAGE_APPEND` — Q4/Q3 tài liệu/design không phải scientific PASS/FAIL. Tệp `lineage.md` phải bất biến.
- **Merge execution:** owner đã cấp GO, nhưng việc merge chỉ là **đã thực hiện** nếu GitHub PR #21 báo `merged=true`, `main` readback có merge SHA và file manifests đã được kiểm lại. Văn bản Q4 **không được thay thế** kết quả provider.

## 2. Căn cứ quyết định

1. **Q1:** [Câu hỏi back-to-basics gốc](../SM4M_Q001_BACK_TO_BASICS_ARCHITECTURE_DOC_CODE_EVIDENCE_20261115.md) trên main commit `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`.
2. **Q2:** [Gói tác giả và quyết định chấp nhận phạm vi](SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md); [ma trận Q2 gốc](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json) giữ nguyên; [V2 remediation](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json) xử lý timing AD-01/03/06.
3. **Q3:** [Báo cáo reviewer độc lập trên exact reviewed HEAD](SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_REVIEW_20261115.md) và [biên nhận JSON](../../../artifacts/governance/sm4m-q001/SM4M_Q001_Q3_AMENDED_CANDIDATE_INDEPENDENT_READBACK_RECEIPT_20261115.json), raw SHA-256 `7809d6ffb6f803d953eaa368b70241c43bc6ccfbce91a0f463bf4e06023a3e6f`. Tệp JSON gốc lần Q3 HOLD trước đó vẫn chưa được archive byte-exact; không sửa lịch sử.
4. **Nguồn ngoài:** [Prospective Literature Watchlist](SM4M_Q001_PROSPECTIVE_LITERATURE_WATCHLIST_20261115.md) về [*The Molecular Structure of Thought: Mapping the Topology of Long Chain-of-Thought Reasoning*](https://arxiv.org/abs/2601.06002), chỉ tham khảo thiết kế/giả thuyết tương lai, không hợp thức hóa một sửa code T4.
5. **Policy:** [Question-first governance](../TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) quy định owner Q4 đóng câu hỏi, quyết định merge/evidence-only, nguồn sự thật trên main; QA tác giả không thay thế kiểm toán độc lập.

## 3. Phán quyết về nhánh và khoa học

- `Q001_QUESTION_CLOSURE=Q4_CLOSED_HOLD_NEW_SCIENCE`. Q001 đã giải quyết **mức nguồn/kiến trúc và giới hạn causal evidence**, không tuyên bố đã tìm thấy cơ chế root cause.
- `IMPLEMENTATION_BRANCH_DISPOSITION=NO_NEW_IMPLEMENTATION_BRANCH; HISTORICAL_BRANCHES_UNCHANGED`.
- `MERGE_DISPOSITION=MERGE_APPROVED_GOVERNANCE_DOCS_ONLY` với PR #21; chỉ metadata, báo cáo và receipts.
- `SCIENCE_DISPOSITION=EVIDENCE_HOLD; NONE_EXECUTED`. Không thêm `lineage.md` entry.
- `NEXT_ACTIVE_RESEARCH_QUESTION=NONE`. Chỉ đề xuất đánh giá ưu tiên nghiên cứu theo dữ liệu/source hiện có; research gate kế tiếp phải được owner phê duyệt riêng và đăng ký trước bất kỳ execution nào.
- `POST_Q001_ROADMAP`: measurement/gold validity trước; data/objective sau; context/decoder/capacity theo bằng chứng; Long-CoT reference thêm vào hướng reasoning tương lai, không chen thành nguyên nhân Small-4M.

## 4. Bất biến và xác minh merge

Trước merge: kiểm provider `main` và PR head; diff **chỉ** `docs/governance/` và `artifacts/governance/`, không có `src/`, `tests/`, `tools/`, `datasets/`, `lineage.md` hay file private. Xác minh nguyên byte bảy bản Q2, Q3 reviewed source, Q3 independent report/receipt và literature watchlist.

Sau merge: GitHub PR #21 phải `merged=true`; `main` phải chứa closure Q4 và watchlist; lineage blob phải giữ `3409e036241deb1da6674619a2abc834bea8a2d6`. Báo cáo final phải trích exact merge SHA. Không bịa sẵn SHA trước khi merge.

## Bước thực hiện tiếp theo — duy nhất (sau Q4)

`TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_SOURCE_ONLY_SINGLE_GATE` — tổng hợp ma trận ưu tiên hướng nghiên cứu dựa trên `main` sau merge và `lineage.md`; không tự mở scientific Q hoặc nghiên cứu, không viết code, không sinh data/gold/scorer, không chạy model. Đề xuất hướng kế nhiệm cần owner quyết định độc lập.
