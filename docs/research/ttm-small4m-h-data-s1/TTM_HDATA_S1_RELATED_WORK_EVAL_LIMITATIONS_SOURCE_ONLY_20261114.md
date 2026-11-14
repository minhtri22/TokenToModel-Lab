# TTM-Small-4M H-DATA-S1 — Tài liệu liên quan và giới hạn đánh giá (READ-ONLY)

**Ngày:** 2026-11-14 · **Phạm vi:** SOURCE-ONLY / LITERATURE-ONLY · **Science protocol:** UNCHANGED

## 1. Nguồn được tiếp nhận

Tệp owner cung cấp: `Pasted text(20261114-031629).txt`, **12.444 byte**, SHA-256 `e4200fe90bb2e207653700e64479ad36613d043c16354ef2588f0c81e71f4ec8`. Tệp là báo cáo tổng quan nghiên cứu (literature review), **không phải nguyên văn ba bài báo**. Tôi đã kiểm tra tên/tác giả/tồn tại của hai bài ACL và metadata của bản preprint năm 2026 qua các URL công bố; các con số chi tiết trong báo cáo đính kèm không được tái xem như chứng cứ QA của TTM.

- **Farajidizaji & Raina (2026)**, *Task Competence Is Not Instruction Following: Evaluating Instruction-Conflicting Behavior in Small Language Models*, LUHME 2026. https://aclanthology.org/2026.luhme-1.9/ — Phân biệt năng lực làm tác vụ (task competence) với việc thực hiện chỉ dẫn xung đột (instruction following). Không có cơ sở chuyển IFFR của Qwen sang TTM-Small-4M.
- **Wen et al. (2026)**, *IF-RewardBench: Benchmarking Judge Models for Instruction-Following Evaluation*, ACL 2026. https://aclanthology.org/2026.acl-long.1092/ — Kiểm tra ở mức ràng buộc (constraint checklist) và độ đáng tin cậy của judge. Báo cáo đính kèm trích Cohen κ 0,67 giữa annotators ban đầu và 0,87 sau cross-check, hai giai đoạn không thể đồng nhất; không thay ngưỡng rubric của TTM.
- **Tiwari (2026)**, *When Consistency Does Not Mean Reliability: Evaluating Local LLM Judges Against Human Ratings*, preprint. https://arxiv.org/abs/2609.13824 — Hai judge tự động có tính nhất quán cao nhưng tương quan thấp hơn với người chấm. Một AI reviewer (hoặc hai AI reviewers) không là gold chuẩn con người.

## 2. Ranh giới khoa học H-DATA-S1

- H-DATA-S1 đánh giá **bảo toàn ngữ nghĩa tiếp nối câu chuyện** (actor, object relation, goal/rule) trên 24 NEW FINAL prompts. Không diễn giải kết quả này thành phép đo năng lực instruction-following tổng quát.
- Điểm chính gồm `actor_retention`, `object_relation_retention`, `goal_or_rule_progress` (0/1 từng trường). Hai trục phụ `coherence` và `consistency` (0–3). **24 cặp × hai phía × năm trục = 240 điểm nguyên và 24 ghi chú**. Không thay đổi các định nghĩa này.
- Phải giữ **bản chấm gốc mù** độc lập và SHA trước giải mù. Nếu chấm bởi AI, tự khai `EXPLORATORY_SCOPED_AI_REVIEW`, không suy ra chuẩn vàng người chấm hay độ tin cậy ngoài phạm vi.
- NEW FINAL24 SHA commit và AES map chứng minh tính toàn vẹn/che danh tính theo cơ chế đã khóa. Đây **không** phải chứng cứ loại trừ contamination toàn bộ TRAIN/TEST/những bộ lịch sử không được đọc; không mở TEST/Q1/Q2/OOD để nghiên cứu contamination trong lượt này.
- Không bổ sung Cohen κ, ICC, IFFR hay human-vs-AI correlation như điều kiện PASS mới; không đổi bootstrap 20.000 lần, seed 20261113, ngưỡng trung bình +0,5/3, ≥16 cặp thắng, CI95 lower>0 và các guardrails đã khóa.
- H0/H1 science thực thi thành công và VAL không suy giảm là **cổng khả dụng (readiness)**, không phải kết quả NEW FINAL24. Trong lượt hiện tại `NEW_FINAL24_INFERENCE=NOT_EXECUTED`, `UNBLIND=NOT_EXECUTED`.

## 3. Kết luận nguồn bổ trợ

`PASS_SOURCE_ONLY_LITERATURE_COMPARISON`; **không đổi tiền đăng ký**, không cập nhật điểm, không đánh giá mù, không mở NEW FINAL hoặc TEST. Không sử dụng bài báo làm nguồn để thiết kế lại scoring sau khi đã quan sát VAL hoặc training outcome.
