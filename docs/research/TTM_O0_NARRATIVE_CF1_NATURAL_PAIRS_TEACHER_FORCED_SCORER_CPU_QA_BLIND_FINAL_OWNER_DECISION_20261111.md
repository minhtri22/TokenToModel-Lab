# TTM-Small-4M / NARRATIVE-CF1 — Nguồn truyện ngôn ngữ tự nhiên, bộ chấm CPU và phân xử

**Ngày:** 2026-11-11. **Task:** `TTM_O0_NARRATIVE_CF1_NATURAL_MINIMAL_PAIRS_SOURCE_SCORER_CPU_PREFLIGHT_AND_BLIND_EVAL_READINESS`.  
**Quản trị:** nghiên cứu nội bộ owner / ChatGPT Web; Codex chưa thực hiện review CF1. **GitHub source of truth** ở nhánh `research/ttm-o0-narrative-cf1-source-scorer-blind-readiness-20261111`, tách từ `81c08f99af0dad4f163bf5f1a1a2b339f7603e91`. Không ghi main, PR13, lineage hay TEST/Q1Q2.

## 1. Câu hỏi nghiên cứu và hai lớp kết luận

NARRATIVE-CF1 hỏi: **O0-Small4M đóng băng ở step1024 có đổi *ưu tiên xác suất tiếp nối* theo sự thay đổi quan hệ/tri thức được diễn đạt trong truyện ngắn không?** Không hỏi có cần module trạng thái O1, không train, không sử dụng N1/R3A làm FINAL. Triết lý ngữ nghĩa động/khả năng duy trì trạng thái là động lực đặt câu hỏi, **không phải kết quả đã chứng minh**.

- **DEV CPU diagnostic (không mù):** có thể thăm dò một lần xem checkpoint đã học sẵn có độ nhạy ngữ cảnh không; kết quả chỉ `EXPLORATORY_CONTEXT_SENSITIVITY`, không đo năng lực suy luận trạng thái thuần.
- **FINAL confirmatory:** vẫn **HOLD** do chưa độc lập phản biện về nhãn, motif/cách diễn đạt có lối tắt, BPE FINAL owner-private chưa kiểm, và một thiết kế template không thể trở thành phép thử khẳng định nhờ mã hóa.

## 2. Corpus đã tạo thật — 108 cặp, không phải 108 motif độc lập

Ba họ truyện được **biên soạn nội bộ bằng tiếng Anh ngắn, tình huống đời thường**; không sao chép TinyStories, R2/R3/R3A/N1 rows, không dùng original Q1/Q2/TEST.

| Family | Nội dung | DEV public | FINAL ciphertext |
|---|---|---:|---:|
| `C1` | Vật phẩm/chuyển giao/quyền nhận đồ | 12 cặp | 24 cặp |
| `C2` | Trách nhiệm, cam kết và việc đang được giao | 12 cặp | 24 cặp |
| `C3` | Nhân vật đã đọc/biết thông tin cập nhật | 12 cặp | 24 cặp |
| Tổng | | **36** | **72** |

**Thiết kế thực tế:** 36 cốt truyện cơ sở tự biên soạn × 3 bộ tên nhân vật = 108 cặp. DEV dùng 12 cốt truyện, FINAL 24 cốt truyện riêng. Mỗi cặp có `context_a`, `context_b`, **chính hai chuỗi** `completion_x/y`; nhãn đúng A=x và B=y nằm trong oracle tách riêng. Bối cảnh A/B đổi quan hệ trong một câu; câu cuối giống nhau.

**Trạng thái source:** 
- [DEV oracle public](../../artifacts/qa/ttm-narrative-cf1/CF1_DEV_PUBLIC_ORACLE.json), SHA-256 `3a425188077f24041a02fe9675e5a503221fe5cc0247ebd53a8cc266329c046d`.
- [DEV model input only](../../artifacts/qa/ttm-narrative-cf1/CF1_DEV_MODEL_INPUT_ONLY.json), SHA-256 `81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed`. Mỗi record **chỉ đúng** bốn trường context/continuation; không có label/ID/split.
- [Generator DEV công khai](../../tools/research/narrative_cf1/cf1_public_dev_generator.py) tái tạo 36/36 cặp và đúng **2/2 SHA-256**, source blob `52ae20294c4a2888db9f0d35674ce38445727556`.
- [Bộ QA nội dung phía tác giả](../../artifacts/qa/ttm-narrative-cf1/CF1_CORPUS_AUTHOR_SOURCE_QA_20261111.json), schema `ttm.cf1.narrative_public_DEV_and_private_FINAL.author_content_QA.v1`.

**Leakage:** DEV/FINAL không chung pair-id, motif-id đã đặt, không chung nguyên văn ngữ cảnh; không có cặp crossing 5-gram Jaccard≥0,85. **Nhưng 0 overlap ở motif IDs không chứng minh hai tập độc lập về dependency pattern.** Định dạng cấu trúc thay tên/quan hệ ở một câu vẫn lặp across all families; có nguy cơ học mẹo.

### Phát hiện shortcut mới, không vá sau khi xem

Đối chứng chỉ chọn **tên người đầu tiên xuất hiện trong mệnh đề thông tin** đúng **36/36 DEV** và **72/72 FINAL (chỉ audit tại khâu biên soạn, không chạy neural)**. Các cặp đảo chỗ hai tên rất đồng dạng. Điều này cho thấy corpus **không phân biệt được** thuật toán nông với trạng thái/tri thức nhiều bước. `SCIENCE_STATE_SPECIFIC_DISCRIMINATION=FAIL_SCOPED`. Không sửa text để đánh bại heuristic rồi gọi là FINAL khoa học. NARRATIVE-CF1 có thể là **bài chẩn đoán độ nhạy ngữ cảnh** ở DEV, không phải science benchmark chứng minh O1.

## 3. BPE2048 exact DEV, giới hạn context

[Kiểm BPE read-only](../../artifacts/qa/ttm-narrative-cf1/CF1_EXACT_T1_BPE2048_DEV_READONLY_QA_20261111.json): đọc trọn **1.791 merge pair** từ **T1 private original manifest** của owner trên máy Windows, chạy rank merge GPT2 với văn bản ASCII. Kiểm prefix `encode(context+completion)` có tiền tố `encode(context)` cho cả bốn tổ hợp; zero mismatch. Kết quả trên 36 DEV cặp:
- Context 83–129 token (≤224), completion 5–12 token (≤16), tổng tối đa 138/256; **0 overflow**.
- 36/36 cặp có hai tiếp nối x/y cùng số token trong mỗi context.
- Source internal manifest SHA `6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6`, số merges 1791. SHA file manifest chuẩn từ thiết kế `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; **không tự nhận đã SHA-readback cả file Windows này**, chỉ đọc đủ pair_ids và đối chiếu con số/pin.
- [Exact T1 BPE adapter](../../tools/research/narrative_cf1/cf1_exact_t1_bpe.py) sẽ khóa SHA file, internal SHA và reconstructed merge tokens SHA trước eval thật; source adapter chưa thực thi với manifest thật trong runtime Linux hiện tại.
- **BPE FINAL chưa kiểm owner-private**, có sẵn [auditor không phát hành plaintext](../../tools/research/narrative_cf1/cf1_private_final_bpe_audit.py). Không tự cho FINAL vượt context khi mới kiểm DEV.

## 4. Frozen P02 scoring engine: đã QA trên fixture, chưa chấm DEV/FINAL

Mã trên GitHub:
- [Teacher forcing scorer](../../tools/research/narrative_cf1/cf1_teacher_forced_scorer.py), Git blob `d7214a4514ecb52e98c0abccd3cecb7180c705e8`, chỉ nhận `context_a,b` và `completion_x,y`, raw JSON fail-closed, từ chối duplicate key/unknown root/field, nonfinite và vượt length. CPU + `torch.no_grad`; không có optimizer/training.
- [25 bài QA scorer](../../tools/research/narrative_cf1/cf1_cpu_scorer_unit_qa.py) và [receipt](../../artifacts/qa/ttm-narrative-cf1/CF1_CPU_SCORER_UNIT_QA_20261111.json) **PASS_25/25**, kiểm 4 logprobs/pair, margin signs, prefix alignment, off-by-one và 16 loại mutated inputs (tính trong tổng 25), không dùng truyện DEV/FINAL.
- [CPU frozen parent fixture](../../tools/research/narrative_cf1/cf1_parent_cpu_fixture_smoke.py) và [receipt](../../artifacts/qa/ttm-narrative-cf1/CF1_PARENT_CPU_FIXTURE_QA_20261111.json) **PASS_8/8**, checkpoint gốc step1024 vật lý SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; 3.749.376 tham số, strict state dict, xác suất hữu hạn/repeat được, không đổi weights.
- **Giới hạn smoke:** CPU dùng triển khai P02 *tương đương toán học từ N1* và tokenizer stub ASCII, **không phải chính Git blob P02 và T1 manifest**. Không gọi đây là exact end-to-end P02 readiness.
- [Runner đọc-only DEV](../../tools/research/narrative_cf1/cf1_dev_once_readonly.py) dùng **chính mã P02 exact blob `9762343e06cf800b50574c2871ae1ed58537fb18`**, exact parent checkpoint SHA, exact BPE/manifest SHA và DEV model input SHA; mặc định HOLD, chỉ chấm khi có cờ scope `--allow-frozen-o0-dev-only`. Không có đường dẫn đọc FINAL hoặc Q1Q2. **Runner chưa được thực thi trên DEV.**

Cho mỗi ngữ cảnh c và hai tiếp nối x/y, `L(c,t)` là mean teacher-forced log-prob của các token t, đọc logits ở vị trí trước token cần dự đoán (không nhầm off-by-one). `m_A=L(A,x)-L(A,y)`, `m_B=L(B,y)-L(B,x)`, `both_correct=(m_A>0 && m_B>0)`; D=m_A+m_B là thứ cấp. Đối chứng prior context-blind không thể đúng cả hai nếu chỉ ưu tiên một tên. Nhưng đối chứng first-mentioned-name đạt 100% nên **không claim suy luận ngữ nghĩa chuyên biệt** khi neural đạt điểm cao.

## 5. FINAL escrow an toàn về mật mã, chưa qua science QA

[Envelope AES-256-GCM trên GitHub](../../artifacts/qa/ttm-narrative-cf1/CF1_FINAL_ENCRYPTED_ENVELOPE.json), Git blob `b3266d8c4eccbb7fe203de66e9af8d2f75547673`. Bao gồm:
- 72 cặp FINAL + nhãn **trong ciphertext**, không có plaintext oracle trên GitHub.
- **Mã biên soạn FINAL riêng cũng là ciphertext** với nonce/AAD khác, cùng owner key; không đưa 24 mẫu gốc FINAL lên repo.
- Public SHA256 ciphertext FINAL `28c1670a609b80214f1ec852cd04df622bc210fb17f3ddccea5300f086218365`, ciphertext source `8acb265b77a84edcfe43da7cded1020f9d09821f3ec523ac482c7db824a813df`.
- Khóa owner ghi/readback thành công tại **`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_CF1_FINAL_OWNER_PRIVATE_KEY_DO_NOT_GITHUB_20261111.json`**, **không trên GitHub**. Khóa chưa được dùng để chấm mô hình.
- [Auditor giải mã read-only](../../tools/research/narrative_cf1/cf1_owner_escrow_verify.py) đã chạy trên CPU: **PASS** hai lượt AES-GCM decrypt, SHA, 72 pairs cân 24/24/24 và private source. [Receipt](../../artifacts/qa/ttm-narrative-cf1/CF1_OWNER_ESCROW_VERIFY_QA_20261111.json) chỉ có metadata/hashes, không có khóa/nhãn.

**HOLD FINAL:** missing independent internal semantic adjudication, query-conditioned structural overlap test, exact owner-private BPE lengths, và prespecified anti-shortcut validity; external reviewer không bắt buộc theo governance owner+Web+Codex. Cryptographic escrow PASS không tự làm science pass.

## 6. Một quyết định tổng hợp

**`GO_SCOPED_READONLY_CPU_DEV_36_PAIRS_ONLY`; `BLIND_FINAL_HOLD`; `O0_TRAIN/T4=HOLD`; `O1=DEFER`.**

Cho phép **một thí nghiệm chẩn đoán DEV 36 cặp** bằng frozen O0, CPU, không train/no GPU/no TEST, với metric đã ghi trước và mọi heuristic audit. Không cho phép chấm FINAL, không kết luận O1 cần thiết hoặc mạnh hơn. Đây là **quyết định phạm vi nghiên cứu nội bộ**, không phải việc runner đã được chạy hay giấy phép inference mới ngầm từ owner. Người chủ có thể cho phép bước tiếp bằng lệnh cụ thể; không thêm micro-permits.

Nếu mục tiêu là **science confirmatory**, quyết định vẫn **HOLD**. Khi đánh giá DEV, giữ cả thành công/thất bại thành exploratory và không tinh chỉnh test hậu nghiệm. FINAL có thể dùng trong nghiên cứu sau nếu giải quyết tính độc lập; không mở trong lượt hiện tại.

**Bước tiếp:** `TTM_O0_CF1_FROZEN_STEP1024_DEV_ONLY_ONESHOT_CPU_TEACHER_FORCED_EVAL_AND_OWNER_ADJUDICATION`. Chạy đúng runner `cf1_dev_once_readonly.py` với owner private T1 manifest, exact P02 Git blob, cp step1024, input DEV SHA, lưu bốn log-probs/pair và receipt SHA vào **GitHub**. Tiền đề là cờ explicit scoped DEV và CPU capacity; nếu không có, dừng FAIL-CLOSED. Nếu có shortcut khác, báo cáo chứ không vá.

**Bảo toàn:** `N1/R3A=DEMO_ONLY`; `MAIN=NOT_WRITTEN`; `PR13=DRAFT_HOLD`; `LINEAGE=UNMODIFIED`; `O1=DEFER`; `TRAIN=NO`; `GPU=NO`; `TTM_TEST_Q1Q2=UNTOUCHED`; `DEV_NEURAL_SCORES=NOT_EXECUTED`.
