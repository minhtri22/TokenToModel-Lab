# RF-00 — Independent Q001 last-mile review: scorer falsification and I1 HOLD

**Ngày:** 2026-11-16 · **Operation:** `TTM_RF00_INDEPENDENT_NATIVE_EVIDENCE_READBACK_AND_NO_MODEL_REPRODUCTION_SINGLE_GATE`  
**Nguồn kiểm toán:** TTM main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`; [PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) exact reviewed HEAD `ebdc54575eed1ff60c402eecf60289f408bb38ca`, tested code `6dc04c0545b28d4a0cad21ad8be8b70461c57790`; [Issue #29](https://github.com/minhtri22/TokenToModel-Lab/issues/29).  
**Phán quyết:** `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE`. **Không** merge, không chạy I2, không tiêu thụ nonce/optimizer step, không sửa `lineage.md`, không đổi các kết quả và byte đã khóa.

## 1. Độc lập tái dựng số học: đạt đúng SHA-256 fixture

Tôi rà lại [candidate source frozen](https://github.com/minhtri22/TokenToModel-Lab/blob/6dc04c0545b28d4a0cad21ad8be8b70461c57790/tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py) và [owner-internal admission](https://github.com/minhtri22/TokenToModel-Lab/blob/6dc04c0545b28d4a0cad21ad8be8b70461c57790/tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/owner_internal_admission.py). Bằng script Python tiêu chuẩn độc lập, không import Q001 runner, không cần checkpoint/tokenizer private, tái dựng đúng 80 dòng với ID 0–2047 trừ EOS 256, seed 20261116 và thuật toán fixture.

**SHA-256 tái dựng độc lập:** `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a` = **MATCH** SHA trong [biên nhận native](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_NATIVE_20261116/native-receipt.json). Group counts: TRAIN 24, recombined 16, novel-ID 16, counterfactual 16, absent 8.

**Nguồn tái lập:** [test_q001_goldblind_control.py](test_q001_goldblind_control.py). Phép tái dựng chạy trên môi trường reviewer Linux Python 3.13.5; **không** phải native QA Windows lần thứ hai và **không** là một lượt model science.

## 2. Root cause thực sự — gold-dependent candidate leakage

Trong chính runner (khoảng dòng 159–170), `opts=[gold]` tạo danh sách 4 lựa chọn với đáp án đúng luôn nằm ở vị trí số 0; ở dòng 527–535, `max(range(4), key=...)` giữ vị trí đầu khi các logit bằng nhau. Bởi vậy **logits hằng số, hoàn toàn không học luật truy vấn, vẫn đạt 80/80 restricted**.

Một đối chứng thứ hai cấp đúng cùng vector logits trên mọi ngữ cảnh: ưu tiên token ID lớn, đưa `NO_ANSWER` xuống cuối. Kết quả tái dựng độc lập:

| Nhóm | Số trường hợp | Restricted không đọc ngữ cảnh | Full-vocabulary không đọc ngữ cảnh |
|---|---:|---:|---:|
| TRAIN | 24 | **14** | **0** |
| HELDOUT_RECOMBINED | 16 | **15** | **0** |
| HELDOUT_NOVEL_IDS | 16 | **16** | **0** |
| PAIRED_COUNTERFACTUAL | 16 | **16** | **0** |
| HELDOUT_ABSENT | 8 | **0** | **0** |

Ba nhóm 16 trường hợp đạt sẵn signpost restricted ≥12/16 và full-vocab ≤8/16 của Q001 mà **không cần model đọc prompt**. Điều đó bác bỏ khả năng dùng khoảng cách restricted/full-vocab hiện tại để quy kết decoder hoặc cạnh tranh từ vựng là nguyên nhân. **Không** suy ra T4 model chắc chắn kém: phép đo này hiện không phân biệt năng lực khỏi thủ thuật candidate.

Ngoài ra, **6/16** recombined có ít nhất một cặp key–value đã có trong TRAIN; **1/16** lặp đúng cặp được truy vấn. Không có trường hợp nào lặp toàn bộ cặp hai binding không thứ tự. Kết luận này là về tính độc lập split/construct, không phải lỗi optimizer.

## 3. Kiểm tra native và quyền sử dụng — phân định mức độc lập

Đã đối chiếu nguồn/các trường của [I1 verdict](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_I1_20261116.json), [16 native test log](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_NATIVE_20261116/native-tests.txt), [PowerShell launcher log](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_NATIVE_20261116/native-ps51-launcher.txt) và [native ABI log](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_NATIVE_20261116/native-win32-abi.txt).

| Kiểm tra | Bằng chứng / đánh giá |
|---|---|
| Windows 11 + PowerShell 5.1 + Python 3.12.10 | **PASS 16/16 theo receipt/log đã xuất bản**, không chạy lại trên Windows bởi reviewer này |
| Win32 Job Object committed memory | Test memory pressure 96 MiB: cấp phát 97 MiB và child khiến tổng vượt 96 MiB đều bị Windows từ chối (WinError 1455). Đây là **committed memory**, không đánh tráo với RSS |
| Process-tree sampled RSS / stdout / timeout | Log PowerShell cho thấy kiểm tra riêng; chỉ là sampled bound, không chứng minh OS hard RSS cap |
| Original checkpoint | Receipt xác nhận Drive→Windows SHA `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, 45.074.891 byte, step 1024, 3.749.376 phần tử tham số. Reviewer này **không** tự truy cập hoặc băm lại byte private |
| Original T1 tokenizer | Receipt báo SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, vocab 2048, loại EOS 256. Reviewer xác nhận code suy ra đúng 2.047 ID, nhưng **không** tự mở source private |
| Owner internal use | Declaration đã có. Không cần 3 vai trò Ed25519 cho owner-only engineering; không tự tuyên bố chứng nhận pháp lý bên thứ ba |
| I2 / nonce | `NOT_EXECUTED` / `UNCLAIMED` theo I1 receipt; reviewer không chạy model |

**Giới hạn độc lập:** Đánh giá này là kiểm tra nguồn + tái dựng 80-case bằng mã độc lập + readback nhật ký native đã có, **không phải** một lượt native Windows hay private-checkpoint independent custody thứ hai. Đủ để xác nhận scorer blocker mà không lặp QA hạ tầng.

## 4. Quyết định RF-00

- **Technical source/hardware/scoped owner path:** qua các native tests được báo cáo; chưa tuyên bố Windows second-lab certification.
- **Measurement validity:** **FAIL**, do gold label leakage và context-blind control đạt signpost; không thể ký `I1_PASS`.
- **Final:** `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE`, `I2_NOT_EXECUTED`, `ONE_SHOT_UNSPENT`.
- **GitHub custody:** evidence mới ở nhánh riêng, source PR #28/QA cũ/`main`/`lineage.md` không đổi.

### Bước thực hiện tiếp theo — duy nhất

`Q001_GOLD_INDEPENDENT_CANDIDATE_SCORER_AND_HARD_NEGATIVE_PROTOCOL_AMENDMENT_NATIVE_SOURCE_QA_AND_SINGLE_I1_REREVIEW`

**Một gói chỉnh sửa kỹ thuật thay vì nhiều micro-permit:**

1. Bảo toàn byte/receipt 80 fixture cũ và phương pháp chấm cũ như **lịch sử FAIL_CONSTRUCT**; không gắn PASS lại hay xóa SHA.
2. Thiết kế scorer gold-blind: từ context xây tập giá trị `{v1, v2, NO_ANSWER}` rồi thêm một distractor xác định từ pool, không phụ thuộc `gold`; thứ tự/tie-break phải độc lập gold. Cần giải thích tính hợp lệ theo oracle và kiểm tra trường hợp `NO_ANSWER`.
3. Hard negative: equal logits, constant-token, monotone-ID, random-choice, shuffled candidate order, shuffled gold labels và matched counterfactual phải **không thể** đạt signpost theo thủ thuật vị trí. Sửa lại threshold và khả năng phân biệt restricted-vs-full bằng giả thuyết thống kê rõ ràng, không lấy threshold cũ dùng cho scorer mới.
4. Đối chiếu split leakage; nếu cần thay fixture đã khóa, dùng **versioned amendment và hash mới** trước I2, không ghi đè frozen Q001. Độc lập source/adjudication **một lần tích hợp**, tận dụng native QA/bytes đã có, chỉ retest code bị thay.
5. Chỉ khi construct hợp lệ và các gate còn lại đủ mới ghi `I1_PASS` rồi chạy **một** I2 theo owner conditional GO đã tồn tại. Nếu không thể sửa đúng phạm vi khóa, giữ `HOLD_I1` và trình một quyết định thiết kế, **không** chạy I2.

**Giới hạn:** Đây là đề xuất sửa một construct kỹ thuật chưa vận hành, không phải quyết định mở một QID mới, không tự sửa protocol frozen hoặc cấp quyền khoa học.
