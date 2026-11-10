# R2 semantic-state toy — Source of Truth / Reproduction

**Kết luận:** `TOY_FORMAL_FEASIBILITY=PASS_SCOPED`; **không** có bằng chứng năng lực GPT/TTM hay cải thiện kiến trúc, không training/inference, không dữ liệu TRAIN/VAL/TEST.

## Hồ sơ chính thức

- [Báo cáo định nghĩa trạng thái, giả thuyết, kết quả và giới hạn](../../../docs/research/TTM_SMALL4M_R2_SEMANTIC_STATE_GOAL_FORMAL_HYPOTHESIS_TOY_FEASIBILITY_20261110.md).
- [Báo cáo máy về 128 cặp, 256 truyện, 21 negative tests](TTM_R2_STATE_GOAL_TOY_QA_AND_OWNER_DECISION_20261110.json).
- [Mã Python **đã được thực thi và khớp Git blob**](../../../tools/research/semantic_state_r2/r2_runtime_integration_executed.py).
- [Bộ negative mutation **đã được thực thi và khớp Git blob**](../../../tools/research/semantic_state_r2/negative_test_runner.py).
- [Generator tách riêng](../../../tools/research/semantic_state_r2/r2_semantic_toy_generator.py) và [Checker độc lập chỉ đọc visible text](../../../tools/research/semantic_state_r2/r2_independent_visible_text_checker.py): **chưa chạy exact ở lượt này**; Codex cần chạy để QA chéo, phát hiện mọi bất đồng.
- [Handoff phản biện lý luận và nguồn cho Codex](../../../docs/research/TTM_R2_CODEX_ADVERSARIAL_THEORY_SOURCE_REVIEW_HANDOFF_20261110.md), trạng thái `HANDOFF_READY_NOT_REVIEWED`.

## Lệnh tái lập nội bộ (Python 3.12, stdlib)

Trong thư mục dự án `D:\WORK\RESEARCH\TokenToModel-Lab`, tạo một thư mục QA riêng **bên trong root**, sao chép đúng hai file đã thực thi `r2_runtime_integration_executed.py` và `negative_test_runner.py` vào đó, rồi:

```powershell
$ErrorActionPreference = 'Stop'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$qa = 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_r2_review_qa_20261110'
# Chạy khi hai file Python đã được sao chép vào $qa. Không chạy tại repo root.
& $py (Join-Path $qa 'r2_runtime_integration_executed.py')
& $py (Join-Path $qa 'negative_test_runner.py')
Get-FileHash (Join-Path $qa 'dataset.json') -Algorithm SHA256
```

**SHA256 kỳ vọng** `dataset.json`: `f20915ff0559b32786961b4a19fa3dce3858cb95d18beaee1fc77ab79cb3cb08`. File 200.630 byte, hoàn toàn synthetic và có thể tái tạo nguyên byte từ source pinned; không phụ thuộc file ZIP/sandbox. Mã runtime hiện **ghi đè file output cùng thư mục nếu đã tồn tại**, vì vậy chạy trong QA folder mới; Codex nên xem đây là điểm cần harden.

Negative runner ghi `negative_audit.json` với `21/21 REJECTED_AS_REQUIRED`, source_events mutation không thay kết quả checker. Cặp DEV và CHALLENGE đều công khai, không dùng như sealed TEST.

## Không nhầm trạng thái

| Lượt | Kết quả |
|---|---|
| Chạy toy bằng code Git blob byte-exact | PASS |
| 256 kết quả visible-text oracle | PASS |
| 21 trường hợp lỗi bị reject | PASS |
| Checker riêng trên GitHub: chạy chéo | **PENDING CODEX** |
| Hiệu quả phụ trợ semantic supervision trong GPT | **NOT TESTED** |
| GPU/Train/TTM inference | **NOT RUN** |
| Codex source-theory review | **HANDOFF READY, NO REVIEW YET** |

Dữ liệu và mã toy là sáng tạo nội bộ phục vụ phép đo; không đụng TinyStories/TEST/Q1Q2. **Bước thực hiện tiếp theo:** giao Codex một lượt `REVIEW_ONLY` cho R2, rồi chọn `O0_ONLY` hoặc `O0_PLUS_O1_DESIGN`, không tự mở T4.