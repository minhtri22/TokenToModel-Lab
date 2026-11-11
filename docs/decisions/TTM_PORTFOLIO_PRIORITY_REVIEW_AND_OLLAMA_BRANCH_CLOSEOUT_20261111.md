# TTM — Quyết định ưu tiên nghiên cứu và đóng nhánh Ollama Full Logits

**Ngày:** 2026-11-11  
**Operation:** `TTM_PORTFOLIO_PRIORITY_REVIEW_NO_SCIENCE_REPLAY`  
**Loại:** `GOVERNANCE_PORTFOLIO_DECISION_NO_NEW_SCIENCE`  
**Nguồn:** `f159cc3c52124e57a30e1236faac6a9bacb3ace6` trên `research/ttm-t5-ollama-full-logits-20261111`; main niêm phong snapshot `5d52e32f20021e36f08f284ef9864d3ba36dbead`.

## Phân xử

**Chọn số 1 — chẩn đoán chất lượng tiếp nối ngữ cảnh của TTM-Small-4M**, bằng một thiết kế mới, dùng nguồn đã khóa nhưng prompt/rubric mới nếu tương lai thực thi. Mô hình đã vượt qua VAL/TEST NLL ở phạm vi T4 và full logits Ollama CPU 4/4, **chưa** chứng minh khả năng sinh truyện hữu ích. Phép thử FRESH12 cho biết 35/48 đoạn có điểm bám prompt bằng 0 và không chứng minh cải thiện qua trimming. Từ đó, quyết định đặt câu hỏi chất lượng lên trước MoE, scaling, P07 GPU hoặc tối ưu serving.

Thứ tự tiếp: (2) cơ chế donor EmbeddingGemma2 OOD — đã có PASS_SCOPED residual nhưng chưa cô lập yếu tố semantic; (3) Attention/Dense/Paged KV và GPU numerical parity — ưu tiên sau quality; (4) memory retrieval — kết quả âm tính, tạm dừng; (5) MoE và mô hình lớn — hoãn đến khi chất lượng và đối chứng có ý nghĩa.

## Trạng thái nguồn và lưu trữ

- Duy trì kết quả khoa học `PASS_SCOPED_OLLAMA_CHILD_FULL_RAW_LOGITS_4_OF_4` tại `lineage.md` L0015; kết luận nhánh: `PASS_SCOPED_CLOSED_UNMERGED`.
- T5 L0013 FAIL strict 32/32, L0014 PASS 4/4 GELU_ERF, FRESH12 không có semantic gain, vector memory FAIL_EXPLORATORY và P07 PAUSED đều bất biến.
- Giữ nguyên bản ghi gốc và raw evidence Windows trong `_tmp/fl3` và nguồn liên quan; không dọn/xóa worktree, checkpoint, log, TEST, origin binaries, không replay inference.
- Dự kiến lưu ref `archive/ttm-ollama-full-logits-scoped-20261111` đúng final commit; archive phải được đọc lại SHA. Nhánh `research/ttm-t5-ollama-full-logits-20261111` tạm thời còn ref, không tiếp tục viết. Việc xóa ref remote cần quyền/công cụ riêng và chỉ được thực hiện sau khi verified archive, không suy diễn là đã xóa.
- Không thay đổi `main` và `lineage.md`, không merge / force push / mở PR / chạy QA source hay science.

**Quyết định cuối:** `OLLAMA_RESEARCH=STOPPED_SCOPED` · `PORTFOLIO_PRIORITY=SMALL4M_QUALITY_GAP` · `NEXT_ACTION=DESIGN_ONLY_NOT_STARTED`.

**Bước thực hiện tiếp theo:** nếu chọn triển khai một nghiên cứu mới, soạn một hợp đồng đánh giá chất lượng tiếp nối truyện có đối chứng, nguồn, tiêu chí và nguồn lực rõ ràng; không chạy trong lượt đóng nhánh này.
