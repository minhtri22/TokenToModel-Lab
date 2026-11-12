# TTM-Small4M H-DEC-R1 — tích hợp quyền owner, reviewer và T4 pin trước science

**Operation:** `TTM_H_DEC_R1_OWNER_SINGLE_NEW_RUN_CONSENT_AND_INDEPENDENT_RATER_ACCEPTANCE_THEN_ONE_SHOT_RELEASE`  
**Đóng gói:** 12/11/2026; `NO_MODEL_FORWARD`, `NO_TRAINING`, `NO_FINAL_PROMPT_DISCLOSURE`.

## Nguồn kế thừa đã được khóa

- Nhánh: `research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112`; HEAD trước gói này `c784b4a0687f6b0fd840f41d3bbf93e5c31038a7`.
- A-1152 checkpoint: 45.087.641 bytes, SHA-256 `ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b`.
- BPE2048 TRAIN-only manifest SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; 36/36 prior roundtrip tests PASS, max prompt 49 tokens + 64 <256.
- Owner-private new evaluation SHA-256 `9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f`.
- Decoder D0/D1 SHA-256 `64a812a49f8d82d2c797d9150b2d3278763d411fff3e3b53424e650711092e85`; prior 207/207 CPU source, 14/14 metric and 4/4 negative mutation checks PASS.
- Reviewer position mapping is already AES-256-GCM encrypted and balanced 12/12; only ciphertext is public. No packet/score exists.

## Người sở hữu (owner) — không suy diễn quyền

Lệnh của owner trong cuộc hội thoại này chấp thuận **công tác tiền kiểm**, nhưng không chứa tuyên bố riêng cấp quyền chạy inference mới. Biên nhận quyền A/C cũ có `internal_A_C_only=true`. Không nâng quyền đó lên H-DEC-R1 và không phát một văn bản `OWNER_GO` thay owner. Cần một xác nhận GO rõ, gắn run ID, phạm vi checkpoint / D0 D1 / DEV FINAL và quy tắc không phát tán.

## Người chấm — bắt buộc có bằng chứng nhận việc thật

Tài liệu `TTM_HDEC_R1_INDEPENDENT_RATER_PRE_DATA_ACCEPTANCE_HANDOFF_20261112.md` là lời mời đối với một phiên ChatGPT mới. **Nó không phải bằng chứng đã có reviewer.** Chỉ khi phiên khác trả JSON `ACCEPTED_PRE_DATA` và owner lưu, kiểm SHA receipt, mới đánh dấu `RATER_ACCEPTANCE=PASS_SELF_ATTESTED`. Không đưa source, mapping, checkpoint, hoặc kết quả A/C cũ sang phiên người chấm.

## Colab T4 — nguồn cần pin ngay trước inference

Mã `ttm_hdec_r1_colab_t4_source_pin_no_forward_v1.py` là cell/script tiền kiểm fail-closed trên Colab owner, chỉ dùng: GPU/T4 runtime introspection, urllib tải mã GitHub theo commit cố định, Git blob+SHA verify, SHA file owner Drive, READY/FINAL metadata. Nó không nhập/khởi tạo GPT, không dùng `model.forward`, không gọi generator. Nếu tất cả PASS, nó tạo biên nhận công khai an toàn tại `public_safe/TTM_HDEC_R1_T4_NO_FORWARD_SOURCE_PIN_RECEIPT_20261112.json` bằng write-once. Việc chạy script này **chưa được thực hiện trong cuộc hội thoại này**; không nói runtime pin PASS nếu không có biên nhận thật từ Colab.

## Quyết định release một lần

| Gate | Trạng thái |
|---|---|
| FROZEN_EVAL / synthetic source QA | PASS_SCOPED_PREVIOUS |
| Actual new-owner rights/inference consent | HOLD_PENDING_EXPLICIT_NEW_RUN_GO |
| Actual independent reviewer acceptance | HOLD_PENDING_SEPARATE_SESSION_RECEIPT |
| Colab T4 pinned source readback | HOLD_NOT_EXECUTED_THIS_CHAT |
| Inference | NO |

**Quyết định:** `HOLD_PENDING_REAL_OWNER_RIGHTS_RATER_AND_COLAB_READBACK`.

Không phải tách thành các micro-permit: sau khi có đúng ba chứng cứ còn thiếu, **một** vòng phân xử release duy nhất có thể đưa ra `GO/NO_GO` trước khi chạy một inference one-shot. Không sửa FINAL24 cũ, không chạy lại huấn luyện, không sửa `lineage.md` hoặc `main` trong bước này.
