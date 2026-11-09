# Q1/Q2 — Bộ chạy một lượt và QA ngoại tuyến (2026-11-09)

Nguồn chuẩn GitHub PR #13; không mở nhánh mới. **Thiết kế và mã nguồn đã tạo, thực nghiệm thật CHƯA THỰC HIỆN**.

## Nguồn đã ghim
- Python runner: `4616121dcd141c4081e2e242e91a0bcef14eaefce3a72e2ea2d0abff1a264566`.
- Unit tests: `e24ea51b34008b21f188e01c30cda16fe50beb9008dc2a4fd1831906aad0db57`.
- PowerShell wrapper: `cc2ebd4441c18830de1c5b2e52aee5d146e27363a0ebd9e704de882f55a1074c`.
- Fixed `main`: `b57b44e7287f842e81050c1faee337f636333dd0`. Nguồn V5 hash `e11e4b3a...`, native TCP `100ca442...`, GGUF `5bdc904...`, BPE source `36d66a1f...`, BPE manifest `cba18e60...`.
- Input Q1/Q2 vẫn do `tools/pilot_q1q2/frozen_inputs_20261109/Q1Q2_LOCK_MANIFEST.json` kiểm SHA, không copy hoặc sửa 16 prompt/48+24+2 matrix.

## Kiểm định đã thực hiện
`python -m py_compile` = PASS và **`unittest 10/10 PASS`** với Python 3.13.5 Linux cho kiểm thử hàm thuần (response positive/negative, run ID, cap, n-gram, chống overwrite, fixture từ chối sha và path escape). **Không gọi Ollama hay TEST/huấn luyện**.

**Chưa thực hiện:** PowerShell parse trên Windows 5.1, QA fixture thực tế trên local main, preclaim V5/BPE/GGUF Windows, 74 calls Ollama, QA metric độc lập, chấm chất lượng thủ công. Không được nâng static QA thành runtime PASS.

## Lộ trình một batch
1. Tải đúng 3 nguồn bằng raw GitHub tại SHA commit PR13 sau cập nhật; đối chiếu 3 SHA256.
2. Chạy `-Mode QA`, sau đó `-Mode Preview` với Python312, không CLAIM. Nếu FAIL, sửa cùng nhánh và không tiêu thụ science.
3. Nếu tiền kiểm PASS, một lần `-Mode Execute`: 48 Q1, 2 warmups, 24 Q2, tối đa 3.904 token, tối đa 45 phút; raw JSON và metrics sơ bộ sinh trong `_tmp/ttm_q1q2_ollama_once_v1`; cổng riêng 12650, không tạo model mới, không chạy V5 cũ.
4. Push receipts tới đúng PR13 bằng clone tạm có SHA HEAD đã ghim, re-clone và kiểm SHA toàn bộ raw + CLAIM/RESULT + manifest. Nếu HOLD, vẫn ghi kết quả từng phần và không chạy lại.
5. Không dọn dữ liệu nguồn/checkpoint/V5. Bootstrap/publish checkout chỉ xem xét dọn sau khi GitHub readback và quyết định riêng. Chấm tay rubric 0–3 trước phân xử QUALITY_GO/REVISE/STOP.

## Merge về main
`MERGE_DECISION=HOLD_PENDING_NATIVE_SCIENCE`. Chỉ merge sau có QA Windows, thực nghiệm thật, kết quả raw/metrics và adjudication rõ ràng; parity T5 `FAIL 7/8` được giữ nguyên.
