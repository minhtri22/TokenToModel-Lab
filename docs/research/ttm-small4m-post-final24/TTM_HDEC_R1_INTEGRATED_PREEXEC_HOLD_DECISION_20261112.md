# TTM Small4M H-DEC-R1 — Một quyết định GO/HOLD tiền thực thi

**Operation:** `TTM_SMALL4M_H_DEC_R1_INTEGRATED_SOURCE_QA_BPE_CONTEXT_CHECK_RIGHTS_REVIEWER_AND_SINGLE_OWNER_GO_HOLD_PREEXEC_NO_INFERENCE`  
**Ngày:** 12/11/2026 · **Run ID:** `TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1`  
**Nhánh:** `research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112`  
**QUYẾT ĐỊNH DUY NHẤT:** **`HOLD_NEW_OWNER_RIGHTS_RATER_ACCEPTANCE_RUNTIME_RELEASE`**.

## Phạm vi thực hiện thật

- Khóa source decoder D0/D1: chỉ can thiệp penalty bằng dấu (dương chia 1,15; âm nhân 1,15; 0 giữ nguyên), phạt một lần cho từng token ID trong continuation, không phạt prompt; argmax tie ID thấp, EOS/64 tokens dừng. Không sampling, không huấn luyện hoặc chỉnh weights. Mã: `tools/pilot_t4/post_final24/ttm_hdec_r1_deterministic_decoder_v1.py`.
- **207/207** static QA trên synthetic logits và BPE source/manifest/checkpoint SHA. **14/14** synthetic metric QA, **4/4** cố ý làm sai source/hash bị từ chối. Đây chỉ là kiểm thử mã; không khẳng định chất lượng thực tế, không tạo model logits.
- Manifest BPE2048 TRAIN-only SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, checkpoint A-1152 45.087.641 byte SHA256 `ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b` **đã được băm lại nguyên byte**. Checkpoint ghi arm=A, step=1152, 53 model state tensors, đọc bằng `torch.load(..., weights_only=True)` chỉ trên CPU, **không model.forward**.
- Bộ private `ND01..ND12`, `NF01..NF24` 18.076 byte SHA256 `9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f`; 36/36 BPE encode→decode exact, prefix length **35–49**, prefix+64 đều <=256, EOS không nằm trong prefix, prompt không có trailing ASCII space. FINAL còn niêm phong về **model outcome**; checker xử lý text chỉ để kiểm BPE/hashes, không sinh/đọc outcomes.
- Escrow riêng **mới** AES-256-GCM giữ ánh xạ `R01–R24` với `NF01–NF24` 12/12 và 3/3 cho bốn stratum. Có ciphertext/hash public; khóa chỉ tại Drive owner-private. Không tái sử dụng private AES key hoặc mapping của A/C cũ. Tạo một lần và xác minh GCM; chạy lại create bị chặn.

## Cổng GO/HOLD (không micro-permit)

| Gate | Trạng thái | Nhận xét |
|---|---|---|
| Freeze 24 FINAL + 12 DEV | PASS | Hash/ID/stratum khớp; no prior FINAL24 reuse |
| D0/D1 exact source + synthetic negative QA | PASS_SCOPED | Không có model-forward |
| BPE exact manifest + 36 roundtrip + context | PASS | max prefix 49 BPE tokens |
| Checkpoint A-1152 actual bytes, identity | PASS_SCOPED | Không suy luận; không chứng minh production runtime trên Colab |
| Escrow mapping AES/LEFT-RIGHT | PASS_CUSTODY_STAGED | Ciphertext public; key owner-only; chưa tạo packet |
| Licenses upstream | SOURCE_DECLARED | `roneneldan/TinyStories` metadata ghi `cdla-sharing-1.0`; không phải owner release |
| Owner new-run rights scope | **HOLD** | Old `RIGHTS_OWNER_SIGNED.json` ghi `internal_A_C_only=true`, không được nhận làm consent H-DEC-R1 |
| Reviewer new-run independence | **HOLD** | Old reviewer ChatGPT GPT-6 thuộc A/C, chưa có tiếp nhận mới; không tự ký hay giả mạo |
| T4 runtime one-shot integration | HOLD_NOT_EXECUTED | Source adapter đã khóa; chưa dry-run trong owner T4 và chưa có GO; không tự bắt đầu inference |
| New evaluation | FROZEN_NOT_CONSUMED | 0 fresh model-forward |

**Một quyết định tổng hợp:** `HOLD_NEW_OWNER_RIGHTS_RATER_ACCEPTANCE_RUNTIME_RELEASE`. Không hạ ngưỡng, không mở FINAL, không phát quyền GPU. Chỉ sau khi owner cung cấp **đúng một chứng nhận phê duyệt phạm vi mới**, reviewer thực tế chấp nhận trong phiên riêng và runner Colab source pin được kiểm, mới trình quyết định release cho đúng run ID — không tái dùng giấy phép khoa học A/C.

## Cách đọc các PASS

207 checks và source sha là QA của **triển khai checker**, không phải QA độc lập bởi tổ chức bên ngoài. Bản scorer mới đóng băng mô tả 20.000 resamples `numpy==2.3.5`; nếu runtime version khác thì phải đổi môi trường trước khi phân tích, không tự sửa thuật toán. Không dùng giá trị CI hay điểm của FINAL24 cũ làm thành quả của H-DEC.

## Giới hạn tính mới

So trùng prompt mới chỉ đối với 24 FINAL24 cũ + 12 FRESH12 cũ công khai. Trong lần thiết kế trước có một lượt đọc prompt Q1 công khai (đã ghi scope deviation); ở lượt tiền kiểm này không đọc thêm Q1/Q2/TEST/OOD hay chạy model. Không khẳng định không trùng dữ liệu TRAIN/TEST chưa xem.

## Bước thực hiện tiếp theo

`TTM_H_DEC_R1_OWNER_SINGLE_NEW_RUN_CONSENT_AND_INDEPENDENT_RATER_ACCEPTANCE_THEN_ONE_SHOT_RELEASE` — không huấn luyện lại A/C, không thay decoder. Từ bằng chứng hiện tại, H-DEC mới **HOLD**.
