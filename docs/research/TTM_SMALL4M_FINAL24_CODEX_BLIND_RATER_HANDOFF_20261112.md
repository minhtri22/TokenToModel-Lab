# HANDOFF — TTM-Small-4M FINAL24 | Codex chấm mù độc lập

**Mục đích:** thư bàn giao riêng cho **agent Codex được owner giao chấm**.  
**Tình trạng:** `REVIEWER_NOMINATED_PENDING_ASSIGNMENT` · `BLIND_SCORE_PACKET_NOT_CREATED` · `NO_SCORES`.  
**Phạm vi định lượng:** 24 cặp, 48 đoạn tiếp nối, ba tiêu chí, mỗi điểm nguyên từ 0 đến 3: **144 điểm**, cùng 24 ghi chú.  
**Bằng chứng chấm AI:** nếu người chấm là Codex AI, giới hạn tuyên bố `EXPLORATORY_SCOPED_AI_REVIEW`, không thay cho giám khảo độc lập là con người.

## I. Điều kiện nhận nhiệm vụ — trước khi đọc đầu ra

Bạn là agent **chấm mù**, không phải người viết code trainer, thiết kế prompt hay phân xử mô hình. Trước khi thấy bất kỳ đoạn tiếp nối nào, ghi lại tên agent, nhà cung cấp, phiên bản mô hình nếu biết, phiên làm việc, UTC lúc tiếp nhận, mô tả phạm vi truy cập và một lời xác nhận:

> Tôi không truy cập checkpoint, mã huấn luyện, nhãn arm, thứ tự A/C, dữ liệu TRAIN/VAL, GitHub source, khóa AES, tài liệu giải mù, hay điểm số dự kiến. Tôi chỉ nhận 24 cặp văn bản trung lập và tiêu chí chấm cố định. Tôi không dùng dữ liệu ngoài hoặc thay đổi tiêu chí sau khi xem đầu ra.

Nếu đã tham gia huấn luyện / chọn prompt / biết ánh xạ arm→trái/phải của chính bộ này: ghi `INDEPENDENCE_CONFLICT=TRUE`, từ chối vai trò độc lập. Nếu chỉ có khả năng AI chứ không phải người, **không khai thành human rater**.

**Không tự truy cập repository hoặc tìm dữ liệu khác.** Chưa có gói neutral thì không chấm và không tạo điểm số giả.

## II. Những gì owner được giao cho reviewer

Owner chỉ gửi **gói trung lập đã niêm phong (blind packet)**, gồm đúng `R01..R24` mỗi item có:

- `pair_id`: R01..R24
- `prompt`: prompt cố định, không nêu model
- `left_text` và `right_text`: hai đoạn văn tương ứng cùng prompt, không có arm hoặc checkpoint
- `packet_sha256`: SHA-256 của gói nguyên byte; owner xác nhận trước khi gửi.

Gói reviewer **không** gồm A/C mapping, checkpoint hashes có thể dùng truy ngược arm, khóa/mã giải mù, nguồn code, log huấn luyện, cột `expected_best`, hay điểm kiểm định C−A.

## III. Chấm theo hợp đồng đã khóa, không sửa cách tính

Với từng `Rxx`, chấm **từng đoạn LEFT và RIGHT riêng biệt**, ba chiều:

1. `prompt_adherence` (bám yêu cầu/cốt truyện đưa ra)
2. `coherence` (mạch lạc)
3. `consistency` (nhất quán)

Thang là số nguyên `0,1,2,3`, không làm tròn từ điểm thập phân. Không bắt buộc phải có một bên thắng. Đánh giá độc lập từng đoạn; không điều chỉnh điểm để làm kết quả đẹp hoặc theo kỳ vọng chủ nghiên cứu. Không thêm chiều, trọng số hoặc quy tắc hòa sau khi thấy văn bản; tuân đúng `TTM_SMALL4M_AC_FINAL24_BLIND_EVAL_AND_RIGHTS_PREEXEC_FREEZE_20261111.json` **do owner cung cấp riêng phần rubric đã khóa**, không tìm vào repository.

Mỗi cặp có đúng **sáu số nguyên** và một ghi chú trung lập chỉ giải thích chất lượng văn bản, không đoán arm.

### Định dạng trả về bắt buộc (ví dụ chỉ cho một R01, KHÔNG PHẢI điểm thực)

```json
{
  "schema": "ttm.small4m.ac.codex.blind_final24.ratings.v1",
  "status": "FROZEN_BEFORE_UNBLIND",
  "reviewer": {
    "agent": "Codex",
    "model_version": "<owner/reviewer supplies>",
    "session_reference": "<owner/reviewer supplies>",
    "received_utc": "<ISO8601>",
    "score_frozen_utc": "<ISO8601>",
    "human_rater": false,
    "independence_conflict": false,
    "no_arm_mapping_access": true,
    "no_unblind_key_access": true
  },
  "blind_packet_sha256": "<64 lowercase hex chars>",
  "rows": [
    {
      "pair_id": "R01",
      "left": {
        "prompt_adherence": null,
        "coherence": null,
        "consistency": null
      },
      "right": {
        "prompt_adherence": null,
        "coherence": null,
        "consistency": null
      },
      "note": "<objective, no-arm note>"
    }
  ],
  "pair_count": 24,
  "integer_score_count": 144,
  "test_q1q2_ood_access": false,
  "arm_mapping_or_key_received": false
}
```

Trong **kết quả nộp thật**, `rows` phải chứa đủ 24 `R01..R24` duy nhất, không có null, đủ 144 số nguyên từ 0 đến 3, 24 ghi chú; phải ghi nhận biên bản tiếp nhận trước khi xem dữ liệu. Chấm không đủ, tự điền thiếu, tự suy đoán kết quả, hoặc bị lộ nhãn là `HOLD_REVIEWER_PROTOCOL`.

## IV. Khóa điểm trước khi giải mù

1. Agent hoàn thành đầy đủ `rows`, ghi metadata và thời điểm đóng băng.
2. Owner lưu **nguyên byte JSON** và tính SHA-256, ghi biên nhận `REVIEWER_SCORE_FROZEN_BEFORE_UNBLIND`. Nếu cần sửa lỗi cấu trúc, phải thực hiện **trước** bất kỳ lần mở ánh xạ và ghi lại vết phiên bản.
3. Agent không được tự giải mù, xem khóa AES, hoặc tính `score_C−score_A`.
4. **Sau khi điểm đã khóa**, một người khác (owner/independent auditor) mới dùng private map để phân biệt A/C và phân xử tiêu chí đã đăng ký.

Ngưỡng phân xử thuộc tài liệu source đã khóa và phần hậu giải mù; không gửi ngưỡng dự đoán thắng-thua cho reviewer trước khi họ chấm.

## V. Kết quả cần giao lại cho owner

Chỉ giao: biên bản chấp nhận vai trò, gói `blind_packet_sha256` đã nhận, tệp chấm 24 cặp với 144 điểm/24 ghi chú, SHA-256 tệp chấm, biên bản đóng băng trước giải mù. Reviewer không chuyển checkpoint/khóa lên GitHub hoặc hệ thống công khai. **Nếu owner chưa chạy A/C và chưa gửi neutral packet thì chỉ xác nhận vai trò, chưa có kết quả chấm.**

## Trạng thái lúc lập handoff

`OWNER_CHAT_CONSENT=AFFIRMATIVE` · `REVIEWER_CODEX=PLANNED_NOT_ACCEPTED` · `AC_T4_SCOPED_QA=PASS` · `AC_TRAINING=NOT_EXECUTED` · `BLIND_PACKET=NOT_CREATED` · `FINAL24=NOT_SCORED` · `NO_GPU_EXECUTION_FROM_THIS_HANDOFF`.
