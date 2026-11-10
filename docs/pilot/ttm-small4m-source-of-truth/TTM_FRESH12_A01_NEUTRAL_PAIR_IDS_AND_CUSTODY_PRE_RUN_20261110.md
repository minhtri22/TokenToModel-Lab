# AMENDMENT A01 — FRESH12: mã cặp vô danh và phân quyền giữ khóa (trước suy luận)

**Ngày:** 2026-11-10 · **Task:** `TTM_SMALL4M_FRESH12_EXECUTOR_SINGLE_48_OUTPUT_BATCH_AND_BLINDED_PACKET_HANDOFF`.  
**Căn cứ:** [Codex reviewer attestation](https://github.com/minhtri22/TokenToModel-Lab/pull/13#issuecomment-6757097604), reviewer `ACCEPTED_SCOPED_AI`, `HOLD_PACKET_NOT_YET_AVAILABLE`.

**Giữ nguyên:** 12 prompt F01–F12 và SHA-256, hai checkpoint step1024/1280, hai điều kiện chỉ khác 1 dấu cách ASCII cuối, greedy argmax, tối đa 64 token, EOS=256, seed, phân bổ 12/12 và 6/6 trên từng checkpoint, rubric 0–3, mọi ngưỡng phân xử. **Không tạo/đọc TEST hay Q1Q2, không TRAIN, không Colab, không sửa `main`/`lineage.md`.**

## Lỗi giao diện reviewer và thay đổi đúng phạm vi

Mẫu `REVIEWER_SCORE_TEMPLATE_20261109.csv` đã đóng băng trước đó chứa `F01-C1024` và `F01-C1280`, vô tình **lộ nhãn checkpoint**. Giữ nguyên tệp cũ như bằng chứng FAIL thiết kế; tạo packet/mẫu chấm kế nhiệm với **24 mã cặp vô danh `R01`–`R24`**. Các mã không chứa `Fxx`, checkpoint, tình trạng dấu cách, bộ giải mã, hoặc thứ tự lịch công khai.

Đánh số cặp `R` sau khi xáo thứ tự 24 cặp bằng `HMAC-SHA256(seed, "PACKET_ORDER_V1|"+prompt_id+"|"+checkpoint)`, sắp tăng dần digest. `seed` là seed đã niêm phong ở [escrow AES-GCM](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_ENCRYPTED_BLIND_SEED_ESCROW_20261109.json), không tạo seed mới. Vị trí A/B điều kiện giữ nguyên từ `HMAC-SHA256(seed,"BALANCE:"+prompt_id)` và đảo theo checkpoint. Không làm mất cân bằng hay hoán đổi kết quả.

## Phân quyền hợp lý hóa escrow

Có sự bất nhất của diễn đạt trước: nếu **không một ai** giải mã seed trước chấm thì executor không thể đặt văn bản vào cột A/B theo đúng phân bổ đã khóa. Sửa ranh giới thành:
- **Executor/custodian duy nhất** được phép giải mã seed trong vùng làm việc riêng tư **để lắp gói A/B và đối chiếu cân bằng**, nhưng không chấm chất lượng hoặc công bố mapping/plaintext/key.
- **Codex reviewer** hoàn toàn không nhận/đọc seed, khóa, mapping, checkpoint IDs, raw labelled record hoặc metadata có thể giải mù. Không dùng kết quả cũ để chấm; nhận **chỉ** `pair_id, prompt_clean, output_A, output_B`, với whitespace ở **đầu** hai phần sinh được lược bỏ theo cùng một hàm `lstrip(" \\t\\r\\n")`.
- **Post-score adjudicator** chỉ đọc bảng nhãn/mapping **sau khi** 144 điểm và SHA của CSV được đóng băng trên GitHub. Phiếu điểm không được sửa sau giải mù.

## GitHub Source of Truth, bằng chứng và bảo mật

Cần commit trên đúng PR #13 **trước khi chạy**. Sau batch:
1. Niêm phong 48 raw outputs theo từng checkpoint/điều kiện, SHA-256, các bản ghi token IDs. Vì repo công khai, raw có nhãn/mapping được **mã hóa AES-256-GCM nonce mới** bằng khóa chỉ owner nắm, không commit plaintext.
2. GitHub lưu **ciphertext đầy đủ**, receipt SHA-256, nguồn runner/audit và **reviewer packet 24 cặp không nhãn**; không cần mở lại TEST hay cấp quyền phát hành checkpoint.
3. Mẫu CSV kế nhiệm 24 hàng `R01`–`R24`, chứa 144 ô điểm 0–3 trống; không dùng tệp mẫu Fxx-Cxxxx cũ cho reviewer.
4. Người chấm chỉ nhận link tới reviewer packet và score template; không gửi trực tiếp tài liệu có unblinding key hoặc raw labelled outputs.
5. QA nguồn/byte/protocol và SHA kiểm tra một lần. Nếu fail sau CLAIM thì STOP và ghi FAIL, không tự chạy lại. Không tuyên bố science PASS khi chưa có reviewer score.

**Trạng thái tại thời điểm amendment:** `RUN_NOT_CLAIMED`, `INFERENCE=0/48`, `AMENDMENT_A01=PRE_RUN_PUBLIC`; `PR13=DRAFT_HOLD`, `MAIN=UNCHANGED`, `LINEAGE=L0017_UNCHANGED`. Đây là thay đổi **giao diện và custody**, không phải sửa ngưỡng khoa học hậu nghiệm.
