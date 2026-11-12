# TTM Vector Memory V2 — Tiền đăng ký (preregistration) nguồn PROBE NON-TEST 192 và Retriever

**Operation:** `TTM_VM_V2_NEW_NONTEST_FIXTURE_RETRIEVER_SOURCE_ONEPACKET_QA_AND_PREREG_FREEZE`  
**Ngày:** 12/11/2026 · **Nhánh:** `research/ttm-vector-memory-architecture-20261111`  
**Trạng thái:** `SOURCE_PREREG_FROZEN_PASS` / **`CPU_SCIENCE_DISPATCH=HOLD`**. Chỉ có fixture generation + source/negative QA; **không chạy NLL, Recall@k trên PROBE thật, model inference, training, TEST hoặc GPU**.  
**Quản trị:** giữ `lineage.md` đến L0021 và `main` nguyên trạng; L0021 `FAIL_RETRIEVAL_SCOPED` không bị nâng cấp hồi tố thành PASS.

## 1. Phân biệt câu hỏi nghiên cứu và phạm vi

- **S0 (64)** dùng mã thực thể `obja...` nguyên văn → `R_EXACT_ID`, kỹ thuật định danh, **Oracle-equivalent**. Không tính vào primary science.
- **S1 (64)** dùng alias `aka...`, không có key `obja...` trong câu hỏi → `R_EXACT_ALIAS` tìm trong `lookup_alias`. Đối chứng ánh xạ alias, **không** phải truy xuất ngữ nghĩa.
- **S2 (64)** chỉ có **ba thuộc tính diễn đạt lại** (color, shape, material), không chứa key hoặc alias → `R_HYBRID_LEX_FIRST` dùng char-trigram sau canonicalization **đã khóa trước** so với `retrieval_text`. Đây là **bài toán tra cứu mô tả có từ vựng đóng và bản đồ từ đồng nghĩa công khai**, chưa chứng minh semantic retrieval ngôn ngữ mở.

**Hạn chế quan trọng của R_HYBRID_LEX_FIRST:** để không đo nhầm false positive, nó chỉ chọn khi bộ ba thuộc tính chuẩn hóa trong câu hỏi khớp **duy nhất** một card; sau đó còn yêu cầu rank lexical xếp card này đầu tiên, ngược lại **ABSTAIN**. Vì vậy đây là controlled structured retrieval; điều kiện uniqueness gần với lookup cấu trúc. Fallback cosine T1/P02 chỉ dùng khi **tất cả** điểm lexical = 0 trên query hợp lệ; với các truy vấn ba thuộc tính canonicalizable của fixture, nhánh này có thể hầu như không được kích hoạt. Không diễn giải việc PASS như khả năng vector semantic retrieval.

**Bằng chứng mở thiết kế:** L0021 frozen cosine full-question mean-T1/P02 embedding vs random key chỉ đạt Recall@1 43/128, Recall@3 107/128 (tiêu chí ≥95% FAIL); lexical control 128/128 vì question chứa key literal; Reader vẫn có giá trị khi được cấp target card. Tuyệt đối không dùng per-story PROBE L0021 làm tập huấn luyện/tuning hoặc đánh giá mới.

## 2. Nguồn và byte SHA đã khóa — không tạo lại nếu nội dung thay đổi

| Nguồn | SHA / pin |
|---|---|
| Khoa học cũ, Reader source (không sửa) | Git blob `7ce728b2874284b87933237c890e54ce3d9fd651` |
| Trọng số Reader L0020 | SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f` |
| Frozen GPT step1280 | SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` |
| T1 manifest | SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| Source v2 fixture `v2_nontest_fixture.py` | Git blob **`01703d4786872a66459593d27cd7607b66c895dd`** · SHA256 `32d667f1ac95569e9bae26c2129c9b90fec37078960bd204be63bc2a4b488607` |
| Source v2 Retriever `v2_nontest_retrievers.py` | Git blob **`dc733eda42d768d695309e3a1d5df25aeabb28b7`** · SHA256 `d1596b28e63a93410c53eea22f637c5ed06cd97614b1b2552273011fcacbfac6` |
| Independent QA `v2_independent_source_qa.py` | Git blob **`a9ad31e4054cdd904174a49be2fbac14e92ee906`** · SHA256 `7039f96f1896a3904b2fc04d5f7a54ab67a12c2b5d9b61e1d05ed0aa5eafd994` |
| Fixture DATA v2 source-generated | SHA256 **`1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d`**, exactly **1.913.776 bytes**; **private file không push GitHub** |
| Fixture seed | `TTM_VM_V2_FRESH192_S0S1S2_20261112_PREREG_A1` |
| Output folder Windows | `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory` |

**Bảo đảm khác dữ liệu cũ:** object key v2 dài 15 ký tự và có tiền tố `obja` (chữ `a` sau `obj`), trong khi khóa TRAIN/DEV/PROBE trước đều dùng `obj` + 12 phụ âm không có `a`. Không cần đọc lại dữ liệu cũ hoặc sealed TEST để khẳng định khác **không gian mã nguồn cũ đã biết**. Chưa so nội dung TEST thực tế và không được phép truy cập.

## 3. Dữ liệu và QA có thể xác minh mà không đánh giá khoa học

Dữ liệu mới được sinh deterministic trong sandbox chỉ để **kiểm tra schema/hash**, chưa sinh tệp Windows owner. Tổng 192 cases, mỗi strata 64, 16 label cân bằng đúng 4/label/strata, 32 cards (1 target + 4 near-negative đúng hai thuộc tính + 27 distractors khác), 6.144 keys và 6.144 aliases riêng, counterfactual wrong-memory chỉ đổi **value** của target. Ở S2 dùng 12 canonical words + 12 synonyms riêng cho **mỗi** color/shape/material (72 từ vựng tất cả), được khóa trong generator trước science. No-memory rỗng. Giá trị target là answer đúng duy nhất trong correct-memory và biến mất trong wrong-memory.

QA riêng `v2_independent_source_qa.py` kiểm **72/72 PASS**: AST, source boundaries, seed/byte SHA, schema/disjoint namespace, label balance, 4 hard negatives, question answer-hidden, correct/wrong invariant, missing/duplicate alias/key, missing/ambiguous description, order/value blindness, abstention masks, invalid k, malformed frozen cosine weights, và forced mock fallback. **Retriever chỉ được gọi trên một ngân hàng 32 records giả lập độc lập; không gọi trên 192 cases mới để đo hit/Recall hoặc NLL.** Fallback cosine được thử với random CPU weights; không nạp backbone hoặc trained Reader. Dữ liệu/QA không có một phát biểu hiệu năng khoa học mới nào.

## 4. Đường Reader, sáu arms cố định cho lượt khoa học tương lai

Reader/source/weights L0020 và GPT P02 giữ frozen. Retriever mới chỉ dùng `question`, `key`, `lookup_alias`, `retrieval_text` + tokenizer/embedding frozen nếu fallback; **không nhận** `answer`, `value`, `target_key`, `wrong_memory`, thông tin mục tiêu hay logits.

Sau retrieval, chuyển về Reader **đúng key/value gốc**, mã hóa T1 frozen như L0020; mask được chọn từ returned indices. Tuyệt đối không gọi lại `encode_topk_inputs` cũ vì hàm đó **tự rank cosine**, trái hợp đồng v2. Wrong-memory phải giữ key/alias/descriptor/rank/mask, chỉ thay value target. Abstain → kích hoạt 0 memory cards; tính miss trong Recall denominator, NLL B1/C1 qua bypass không memory; không loại câu khỏi thống kê.

Sáu arms: `A` no-memory (bypass bit-exact), `O1` Oracle trên **gold key chỉ bên trong positive control của scorer** (S2 không có ID trong câu hỏi), `B1` / `C1` R_HYBRID_TOP1 good/wrong, `B3` / `C3` Top3 good/wrong (diagnostic only). Trên S0/S1 dùng Retriever tương ứng, cùng Reader frozen, nhưng chỉ report controls; tiêu chí GO khoa học chỉ đo trên S2.

## 5. Tiêu chí science v2 được khóa trước đo, KHÔNG cho phép chạy ngay

Tất cả tiêu chí dưới đây đã đóng băng từ thiết kế v2 ở bước này, không được thay sau khi sinh hoặc xem kết quả:

1. **Primary strata S2 chỉ 64/192**; `R_HYBRID_LEX_FIRST Recall@1 >= 0.90`, tức **≥58/64 hit**; abstentions tính miss. Không chấp nhận false-positive trên negative cases thiếu/ambiguous key (checked separately by source QA).
2. **Answer-only teacher-forced story NLL** trên S2, trọng số mỗi story bằng nhau: `NLL(A)-NLL(B1) >= 0.05`, `NLL(C1)-NLL(B1) >= 0.05`, và cả hai lower bound của paired percentile bootstrap 95% > 0, 2.000 draws, seeds `20261116` / `20261117`, 64 stories.
3. `NLL(A)-NLL(O1) >= 0.05` trên S2, nếu không đạt → `HOLD_READER_QUERY_DOMAIN_SHIFT`, không suy ra ranker fail.
4. `B3/C3`, S0/S1, lexical/fallback share, coverage, abstain, CPU timings, conditional hit/miss đều diagnostic; **không đổi primary**.
5. Phán quyết ưu tiên: source/leak/integrity lỗi → `HOLD_INVALID_EVIDENCE`; O1 fail → `HOLD_READER_QUERY_DOMAIN_SHIFT`; S2 Recall@1 fail → `FAIL_DESCRIPTION_RETRIEVAL_SCOPED`; Recall pass nhưng NLL/bootstrap fail → `FAIL_FROZEN_READER_TRANSFER_SCOPED`; tất cả pass → `GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED` **không phải TEST PASS**.

## 6. Hợp đồng thực thi một lần — chỉ readiness, chưa dispatch

Tác vụ science dự kiến `TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1`. Khi tạo science runner phải đóng băng Git blob/SHA riêng, có independent one-shot QA và receipt Windows source/checkpoint/Reader/probe SHA trước khi cấp GO thực thi; đánh giá CPU FP32 2 threads, **0 optimizer steps**. Khởi chạy **chỉ khi explicit `--execute-once`**. Tạo marker `ONE_SHOT_STARTED.json` **trước** chấm case đầu; output dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\<RunID>`; nếu folder tồn tại bất kể PASS/FAIL phải dừng, không retry, không overwrite, không sửa nguồn/seed. Report aggregate công khai, per-story NLL private; khóa SHA và QA độc lập từ per-story rồi phân xử L0022 **chỉ sau science thật**.

**Cổng ở hiện tại:** generator+retriever+QA+protocol/seed/probe hash PASS; **one-shot science scorer v2 chưa triển khai hoặc kiểm toán**, owner Windows source/fixture readback chưa nhận. Vì vậy **`CPU_SCIENCE_RELEASE=HOLD_NOT_DISPATCHABLE`**, **không phải mở micro-permit**; bước tiếp theo phải gộp scorer integration + độc lập QA + owner one-shot GO/HOLD trong một packet. Không mở TEST, không dùng GPU, không chạy lại L0021.

## 7. Cách tạo chứng cứ owner Windows không sinh rác ổ C

Script PS5.1 `Invoke-TTM-VM-V2-Source-QA-Prereg-Freezer-PS51.ps1` source Git blob **`7280d5a11214c43f792f0982e1204aab41e38f0b`**. Chạy `-GenerateFixture` để tạo **một** tệp riêng tư D: nếu chưa có, checksum lại; nếu tồn tại đúng checksum thì tái sử dụng, nếu sai → HOLD, không ghi đè. Chạy QA 72/72 trên Windows theo đúng Git blobs, giữ worktree v2 detached pin và `main` không đổi. Python312 trên C: chỉ đọc binary, dùng `-B` và `PYTHONDONTWRITEBYTECODE` không ghi pycache lên C:.

**Bước thực hiện tiếp theo:** `TTM_VM_V2_FROZEN_READER_CPU_SCORER_ONEPACKET_INTEGRATION_QA_OWNER_RELEASE` — tích hợp scorer mới, độc lập QA, owner receipt, ra một GO/HOLD duy nhất. **Không chấm lại bất kỳ PROBE trước, không chạy science ở bước source QA hiện tại.**
