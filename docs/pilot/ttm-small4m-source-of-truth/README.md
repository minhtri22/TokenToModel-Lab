# TTM-Small-4M — Sổ tài liệu chính thức (GitHub Source of Truth)

Ngày cập nhật 2026-11-09. Nguồn chính thức: repository `minhtri22/TokenToModel-Lab`, nhánh PR **#13** `research/ttm-small4m-q1q2-quality-single-batch-20261109`. **GitHub** là nguồn sự thật cho protocol, tài liệu và bằng chứng có thể công bố. Các bản ZIP lưu nơi khác chỉ là bản lưu/phục vụ khôi phục, không thay thế nội dung GitHub. `main` và `lineage.md` chưa đổi.

## A. Các báo cáo đầy đủ của lượt trước (đã nhập lên GitHub)

1. [Chấm mù checkpoint 1024 vs 1280 — bản báo cáo đầy đủ](TTM_SMALL4M_1024_VS_1280_FINAL_BLIND_QUALITY_ADJUDICATION_20261109.md) — nguồn file gốc SHA256 `d6d9b46aaf5ddb1af92216efc220cd40864d11db82f65efeb3899122988dc3da`.
2. [Chẩn đoán nguyên nhân bám prompt yếu — bản đầy đủ](TTM_SMALL4M_PROMPT_ADHERENCE_ROOT_CAUSE_READONLY_DIAGNOSTIC_20261109.md) — SHA256 gốc `b68ed0b6d9e63ae38fcf2eb6a0cf6d9f7e8db6c34de10be059715db1a5f4fde5`.
3. [Ablation bỏ dấu cách cuối — bản báo cáo đầy đủ](TTM_SMALL4M_PROMPT_SERIALIZATION_ABLATION_FULL_REPORT_20261109.md) — SHA256 gốc `d49cdb970aa58614db0d021c9900c9ef836b82da0ef5a6d203aee3d89e77a075`.
4. [Chấm mù hậu nghiệm 32 cặp và quyết định TRAIN — bản đầy đủ](TTM_SMALL4M_POSTHOC_SEMANTIC_REVIEW_AND_DATA_DECISION_FULL_REPORT_20261109.md) — SHA256 gốc `8b887fdc11fe632b72bcd12a84f86a20704f1f6449e622dd3e7e15ace0895e5b`.

### Điểm chấm, rubrics và biên bản có thể công bố

- [Điểm A/B hậu nghiệm đã khóa, 32 cặp](../../../artifacts/qa/ttm-original1280/quality-scores/TTM_SMALL4M_POSTHOC_AI_BLIND_SCORES_FROZEN_20261109.csv) — SHA256 nguồn gốc `748acd55fa064f70c68af1f08fdda78b2e1c370969a8549b9da9eaf0f752037a`.
- [Điểm sau giải mù 32 cặp](../../../artifacts/qa/ttm-original1280/quality-scores/TTM_SMALL4M_POSTHOC_UNBLINDED_PAIRED_SCORES_20261109.csv) — SHA256 nguồn gốc `e6a9c5e640210e1636f7b45fa467f30db31761795587f459c491dfea12645600`.
- [Điểm sau giải mù 16 cặp checkpoint](../../../artifacts/qa/ttm-original1280/quality-scores/TTM_SMALL4M_1024_VS_1280_UNBLINDED_SCORES_20261109.csv) — SHA256 nguồn gốc `c18e0c6c09e2173c2e4435893b97e5532ad98154bf3cc64b4f5c31fb4c88e24e`.
- [Rubric 0–3 bản ghi theo GitHub](../../../artifacts/qa/ttm-original1280/quality-scores/TTM_SMALL4M_POSTHOC_SEMANTIC_RUBRIC_CANONICAL_20261109.json) — source gốc SHA256 `61705dac08df2c4458eb37e1fd9530d75a2efa11bec0a85f7f63640a5aaabad3`.
- Biên bản khoa học/chẩn đoán tóm tắt hiện có từ trước trên PR #13: `docs/pilot/TTM_SMALL4M_*QUALITY*`, `artifacts/qa/ttm-original1280/*SCOPED*`. Tất cả trạng thái **không vượt** phạm vi QA đã ghi nhận.

**Ghi chú tính toàn vẹn:** Tệp chấm CSV có thể đã được bỏ cột `index` trang trí khi nhập từ bản trình đọc; Markdown có thể được chuẩn hóa xuống dòng ở cuối. Các SHA256 ở trên là **của file nguồn gốc được đóng băng**, không mặc nhiên là SHA256 byte của bản trình bày GitHub. File GitHub và Git blob trên nhánh PR #13 là bản công khai chính thức từ nay; SHA nguồn giúp tra cứu lineage.

## B. FRESH12 — hồ sơ hiện hành, chưa suy luận

- [Hợp đồng và quyết định sẵn sàng người chấm](TTM_SMALL4M_FRESH12_PREREG_AND_INDEPENDENT_REVIEW_READINESS_20261109.md)
- [12 prompt nguyên bản + 24 cặp + rubric + ngưỡng — JSON source of truth](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_PUBLIC_PREREG_GITHUB_CANONICAL_20261109.json)
- [QA tĩnh / trạng thái HOLD người chấm](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_READINESS_SCOPED_QA_20261109.json)
- [Mẫu CSV 144 điểm cho người chấm độc lập](../../../artifacts/qa/ttm-original1280/fresh12/REVIEWER_SCORE_TEMPLATE_20261109.csv)
- [Mẫu tiếp nhận và xác nhận độc lập — chưa ký](TTM_SMALL4M_FRESH12_INDEPENDENT_REVIEWER_ATTESTATION_TEMPLATE_20261109.md)
- [**Handoff dành cho Codex reviewer khi có agent rảnh**](TTM_FRESH12_CODEX_INDEPENDENT_REVIEWER_HANDOFF_20261109.md) — không chứa khóa giải mù và không tự chạy 48 mẫu nếu người chấm chưa xác nhận.
- [Escrow A/B được mã hóa AES-256-GCM](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_ENCRYPTED_BLIND_SEED_ESCROW_20261109.json); **khóa giải mã không thể đưa lên GitHub công khai** trước khi khóa điểm.

## C. Ranh giới công khai / bí mật

GitHub repo hiện tại là **public**. Không commit checkpoint, private BPE merge manifest, token TRAIN/VAL, TEST, Q1/Q2 đã tiêu thụ, A/B plaintext key chưa giải mù, hoặc ZIP cũ chứa trực tiếp A/B key và văn bản sinh riêng tư. Thay thế bằng **báo cáo, bảng điểm đã giải mù, manifest SHA256, thuật toán, escrow mã hóa** trên GitHub. Chỉ khi các quyền tương ứng được xác minh và dữ liệu vô hại mới xem xét mở rộng công khai; không coi bản ZIP làm nguồn sự thật đối với kết luận khoa học.

Trạng thái: `SOURCE_OF_TRUTH=GITHUB_PR13` · `FRESH12_PREREG=FROZEN` · `REVIEWER=HOLD_NOT_IDENTIFIED` · `INFERENCE=NOT_EXECUTED` · `TRAINING=NOT_EXECUTED` · `TEST=UNTOUCHED` · `PR13=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`.

**Bước thực hiện tiếp theo:** tiếp nhận người chấm độc lập và khóa attestation, rồi thực thi one-shot 48 continuation theo hợp đồng GitHub đã ghim.

## D. Rà soát quy hoạch nhánh song song

[Tài liệu đối chiếu toàn bộ kế hoạch P00–P12 và các workstream có thể làm song song](https://github.com/minhtri22/TokenToModel-Lab/blob/governance/ttm-parallel-workstreams-review-20261109/docs/governance/TTM_P00_P12_ORIGINAL_PLAN_VS_CURRENT_PARALLEL_WORKSTREAMS_20261109.md) nằm ở **nhánh quản trị riêng** từ `main`, không hợp nhất cùng PR #13 và không thay phase gates gốc.
