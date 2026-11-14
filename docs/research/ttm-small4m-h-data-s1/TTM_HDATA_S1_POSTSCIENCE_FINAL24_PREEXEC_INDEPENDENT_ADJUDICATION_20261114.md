# H-DATA-S1 — Đóng băng science và kiểm toán nguồn NEW FINAL24 (không suy luận)

**Operation:** `TTM_HDATA_S1_POST_SCIENCE_INDEPENDENT_READY_LAST_VAL_FREEZE_AND_NEW_FINAL24_BLIND_GENERATION_PREEXEC_OWNER_GATE_NO_INFERENCE`  
**Date:** 2026-11-14  
**Role:** Independent scoped AI evidence/source reviewer, **not** human blind rater  
**Formal decision:** `GO_SOURCE_ONLY_PREEXEC__HOLD_NEW_FINAL24_PENDING_EXPLICIT_OWNER_ONE_SHOT_GO`

## 1. Khóa nguồn khoa học và cổng VAL

Từ biên nhận owner `READY-last` SHA-256 `e30a2281580b1f6ea33856577f0a244cd02e226dc8a3db00d207a8fe13cce4b5`, đã có kiểm toán riêng `TTM_HDATA_S1_INDEPENDENT_READY_LAST_VAL_FREEZE_20261114.json` trên nhánh nghiên cứu:

| Gate | Khóa và kết quả |
|---|---|
| Nguyên bộ dữ liệu | TRAIN pack SHA `184f68b4...`, P02 parent SHA `cb985751...` |
| Science | H0 128 update, H1 128 update; mỗi update 4096 target |
| Kết thúc | Cả hai ARM ở step 1152, đủ 8 READY, đầy đủ nhật ký BEGIN/DONE |
| Byte-custody | Hai checkpoint cuối 1152 được băm SHA độc lập; sáu checkpoint sớm được đối chiếu từ READY |
| VAL | H0 NLL `3.511285912623514`, H1 `3.5057606759493716` |
| VAL difference | H1−H0 `−0.0055252366741425085`; no-regression guardrail **PASS** |
| Ngữ nghĩa FINAL | **NOT_TESTED**; không suy diễn lợi ích từ VAL |

Không tái huấn luyện, không thay đổi optimizer, sampler, BPE, checkpoint, seed hoặc tiền đăng ký. Không sử dụng VAL để chỉnh tham số mới.

## 2. Source generator candidate và kiểm thử âm tính

**Nguồn candidate:** `tools/pilot_t4/hdata_s1/ttm_hdata_s1_new_final24_blind_generation_candidate_source_only_v1.py`  
**SHA-256:** `c66955b9ae29fda704b2bc0e94d5631e04695cb2a09e38db36f035c83a1295ee`  
**Git blob SHA-1:** `329a018c17211b73e691fad5668e96ef0f2a6558`

- Chế độ mặc định `--mode source-only`. **Không** đọc bất kỳ prompt FINAL, AES key, private TRAIN, checkpoint; không import torch và không model forward.
- `--mode generate` thiếu permit owner FINAL24 riêng phải **FAIL trước khi import torch**. Permit tương lai phải mang nguồn SHA hiện tại, run ID, đúng H0/H1 step1152, prompt SHA, ciphertext SHA, fixed output root, cấm unblind và training.
- Khi và chỉ khi owner cấp permit, runtime candidate sẽ kiểm byte SHA của checkpoint, BPE, owner FINAL và escrow ZIP, đối chiếu hash 24 prompt; giải AES map trong RAM nhưng không ghi key/mapping ra GitHub; kiểm **toàn bộ 24** prompt BPE roundtrip/context trước bất kỳ forward.
- Sau tất cả preflight mới tạo immutable run root, sinh **plain greedy argmax**, tối đa **64 BPE mới hoặc EOS=256**, context 256, không repetition penalty/temperature/sampling/tự sửa token lỗi. Gói cho người chấm có 24 cặp `R01–R24` LEFT/RIGHT, 48 continuations, **không** có nhãn H0/H1 hay owner anchor; số liệu EOS/cap64/under8 lưu **owner-only**.
- Đây là ứng viên **chưa kiểm thử inference thật trên T4**. Việc code có cổng không đồng nghĩa cổng thực tế đã PASS với 24 prompt bí mật. Nếu một cổng runtime thất bại, giữ nguyên thư mục run/sentinel và HOLD; không tạo lượt thứ hai.

**Kiểm toán độc lập nguồn:** `tools/pilot_t4/hdata_s1/independent_hdata_s1_new_final24_source_only_preexec_qa_v1.py`. GitHub Actions source-only **PASS** (run `43551858618`), bao gồm test âm tính không owner permit. Không gọi GPU hoặc mô hình.

**Owner escrow ZIP readback (metadata only):** SHA-256 ZIP `c5c5d6...` PASS, tồn tại các member tên đúng như mã AES nguồn, không giải mã AES, không đọc bí mật trong lượt này. Public SHA/rights receipt từ science giữ nguyên.

## 3. Blind scoring freeze — không đổi hợp đồng

Nguồn hợp đồng gốc: `docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_BLIND_SCORING_AND_ADJUDICATION_CONTRACT_20261113.json`.

- Ba trục nguyên nhị phân: actor retention, object relation retention, goal/rule progress. Hai trục 0–3: coherence, consistency.
- **24 cặp × 2 phía × 5 trục = 240 điểm nguyên**, thêm **24 ghi chú có nội dung**. File mẫu `TTM_HDATA_S1_BLIND240_UNSCORED_TEMPLATE_SOURCE_ONLY_20261114.json` chỉ chứa giá trị `null`, không phải kết quả.
- Bộ validator `ttm_hdata_s1_blind240_source_only_and_score_freeze_validator_v1.py` kiểm source-only 240 ô rỗng, từ chối nhầm template trống là điểm đã đóng băng. Sau khi chấm thật, validator yêu cầu đủ điểm/ngưỡng và trả **SHA-256 tệp điểm byte thực** cùng **SHA-256 mảng điểm canonical** trước khi owner giải mù.
- Tiêu chí primary vẫn là mean `H1−H0 >= 0.5`, `>=16/24` cặp H1 thắng chặt, CI95 bootstrap paired lower `>0` với 20.000 resamples seed 20261113. Giữ đầy đủ actor/object/goal, coherence/consistency, VAL, under8 và EOS/cap64 guardrails như đã khóa.
- Reviewer AI chỉ được ghi `EXPLORATORY_SCOPED_AI_REVIEW`. Không gọi độ ổn định của judge là chuẩn vàng của con người. Trước unblind, reviewer chỉ thấy cặp trung lập, không thấy ánh xạ AES, nhánh nguồn hoặc owner anchors.

## 4. Tài liệu liên quan và contamination

Đã đọc tệp owner cung cấp `Pasted text(20261114-031629).txt` (12.444 byte, SHA-256 `e4200fe90bb2e207653700e64479ad36613d043c16354ef2588f0c81e71f4ec8`). Ghi nguồn [Farajidizaji & Raina 2026](https://aclanthology.org/2026.luhme-1.9/), [Wen et al. 2026](https://aclanthology.org/2026.acl-long.1092/), [Tiwari 2026](https://arxiv.org/abs/2609.13824) vào `TTM_HDATA_S1_RELATED_WORK_EVAL_LIMITATIONS_SOURCE_ONLY_20261114.md`.

Báo cáo liên quan chỉ giúp diễn giải: năng lực sinh văn bản khác tuân thủ chỉ dẫn; đồng thuận ban đầu khác đồng thuận sau phân xử; tính ổn định AI judge khác mức phù hợp với human judges. SHA-256/AES khẳng định byte custody và blind map, **không** chứng minh không có overlap với toàn bộ dữ liệu huấn luyện. Không bổ sung IFFR, κ hay ICC làm ngưỡng thử nghiệm.

## 5. Một quyết định owner riêng để mở NEW FINAL24

**GO nội bộ trong lượt này là GO_SOURCE_ONLY_PREEXEC, chưa phải GO_FINAL_INFERENCE.** Cơ chế gác cửa vẫn từ chối `--mode generate` nếu thiếu owner permit riêng.

Nếu owner chọn `GO_HDATA_S1_NEW_FINAL24_ONE_SHOT_OWNER_INFERENCE`, phạm vi duy nhất được đề xuất: đúng candidate SHA và run root cố định, đúng hai checkpoint step1152 và BPE, đúng 24 prompt mới SHA đã khóa, mapping AES đã tồn tại (không rekey), owner T4 `torch==2.14.1+cu130`, plain greedy64/EOS 256, **một lượt sinh 48 continuations** vào gói mù LEFT/RIGHT. Không training, không tune, không truy cập TEST/Q1/Q2/OOD, không chấm điểm/giải mù trong công đoạn generation. Sau thế hệ: QA chứng cứ/custody packet, rater riêng chấm 240 điểm+24 ghi chú, đóng băng SHA, cuối cùng mới xin owner unblind.

Nếu owner chọn `HOLD`: giữ nguyên source, AES ZIP, checkpoint và NEW FINAL niêm phong, không chạy inference.

**Overall:** `SCIENCE_EXECUTION=PASS` · `READY_LAST=PASS` · `VAL_GUARDRAIL=PASS` · `FINAL_GENERATION_SOURCE_ONLY=PASS` · `FINAL_RUNTIME=NOT_EXECUTED` · `FINAL_OWNER_PERMIT=NOT_GRANTED` · `SEMANTIC_BENEFIT=PENDING` · `NEW_FINAL=SEALED` · `UNBLIND=NOT_EXECUTED`.
