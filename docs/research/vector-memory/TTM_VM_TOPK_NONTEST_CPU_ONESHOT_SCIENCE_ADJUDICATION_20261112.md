# TTM Vector Memory — Phân xử khoa học độc lập: Frozen Reader Top-k PROBE 128 (NON-TEST)

**Operation:** `TTM_VM_TOPK_NONTEST_CPU_ONESHOT_RESULT_INDEPENDENT_RECOMPUTATION_AND_SCIENTIFIC_ADJUDICATION`  
**Run ID:** `TTM_VM_TOPK_NONTEST_FROZEN_READER_PROBE_ONCE_V1`  
**Ngày:** 12/11/2026  
**Phán quyết:** **`FAIL_RETRIEVAL_SCOPED`** theo tiêu chí đã khóa trước khi đo.  
**Phạm vi:** *Một lượt CPU inference thật* trên PROBE synthetic 128 truyện, 32 memory records/truyện; Reader L0020 frozen; không TRAIN/DEV cũ/TEST/GPU.

## 1. Nguồn và tính toàn vẹn phép đo

- Nguồn science checkout khóa `9e46bb4662fcffc66f85ae7d4d479a017f69b293`; runner Git blob `d6e2cb2b087342234f8f722de70b6de429c550c3`.
- Trọng số Reader L0020 SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`, 8 tensor, bước học trước đó 128; frozen GPT step1280 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; PROBE SHA256 `88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11`.
- Tiền kiểm chủ máy `INDEPENDENT_SCORER_QA=PASS_66_66`. Runner hoàn tất `cases=128`, `TRAINING=false`, `TEST_NOT_OPENED=true`; không báo lỗi runtime và trả `FAIL_RETRIEVAL_SCOPED`. One-shot **đã tiêu thụ**, không có quyền chạy lại.
- Windows output `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_TOPK_NONTEST_FROZEN_READER_PROBE_ONCE_V1` chứa `ONE_SHOT_STARTED.json`, `PER_STORY_QA_PRIVATE.json`, `PROBE_AGGREGATE_PUBLIC.json`. Không tải lên GitHub dữ liệu NLL/gate theo từng truyện hoặc Reader/TEST.
- SHA256 aggregate do Windows xuất `c65692d19b8e48687102f664f24690c5b151a07d69f9a0a3f297b8fab06b3ffa`; trùng SHA do kiểm toán viên tái dựng byte với CRLF + final CRLF từ toàn văn bản `read_file`. **Giới hạn:** đây là readback văn bản và tái dựng newline, không phải truy cập độc lập bytes binary nguyên thủy.
- Đọc đầy đủ 128 bản ghi per-story trên Windows (3.074 dòng) theo nhiều cửa sổ; ghép được JSON hợp lệ, đủ 128 ID khác nhau, 400 answer tokens mỗi arm; tính lại Recall, NLL, paired delta và bootstrap độc lập, **22/22 QA PASS**.

## 2. Retrieval Recall@1/@3: FAIL phạm vi đã định

| Retriever | Recall@1 | Recall@3 |
|---|---:|---:|
| `R_FULL_COSINE`: cosine mean embeddings T1/P02 của toàn question với key | **43/128 = 33,59375%** | **107/128 = 83,59375%** |
| `R_LEX_TRIGRAM`: 3-gram của toàn question và key, control retrieval-only | **128/128 = 100%** | **128/128 = 100%** |

**Tiêu chí chính đã khóa** `R_FULL_COSINE Recall@3 ≥ 95%`: cần tối thiểu **122/128** hit. Thực đo chỉ **107/128**, thiếu 15 hit, có 21 miss. **`FAIL_RETRIEVAL_SCOPED`** là phán quyết đã quy định trước và có ưu tiên trước khi xét PASS chung.

Lexical trigram đạt 128/128 bởi câu hỏi **chứa literal mã thực thể**; đây là đối chứng mô tả có ích: định danh khóa chính xác có thể đáng tin hơn cosine embedding khi key là chuỗi ngẫu nhiên. Không được chuyển hậu nghiệm lexical thành primary hoặc sửa tiêu chí để gán lại kết quả là PASS. Kết quả không chứng minh semantic retrieval hay RAG tổng quát.

## 3. Reader frozen: tín hiệu value vẫn dương tính

| Arm | Mean answer-only story NLL, nats/token (nhỏ hơn là tốt hơn) |
|---|---:|
| A — No memory, bypass | **6.959491420537233** |
| O1 — Oracle top1 correct | **3.8215356841683388** |
| B1 — Cosine Top1 correct | **4.7850405015051365** |
| C1 — Cosine Top1 wrong target value | **5.208137892186642** |
| B3 — Cosine Top3 correct | **4.535291496664286** |
| C3 — Cosine Top3 wrong target value | **4.956644399091601** |

**Chênh lệch ghép cặp trên 128 truyện:**

- `A−B3 = +2.4241999238729477`; bootstrap 95% theo runner [**2.21246607969515; 2.6217374737840147**].
- `C3−B3 = +0.4213529024273157`; bootstrap 95% theo runner [**0.25030811512842777; 0.6339838543441146**].

Cả hai chênh lệch vượt 0,05 và các cận dưới CI đều >0. Kiểm toán viên lấy mẫu lại 1.000 bootstrap với **bộ sinh số ngẫu nhiên độc lập Mulberry32** (dùng seed định danh 20261114/20261115, khác NumPy PCG64 của runner) và phép phân vị tuyến tính: CI độc lập `A−B3 = [2.2311086208093913, 2.608043568301946]`, `C3−B3 = [0.2340420066844672, 0.6216202415525913]`. Chúng không phải cùng 1.000 mẫu bootstrap với runner nhưng kết luận định hướng/độ lớn nhất quán.

**Chứng cứ phân biệt:** ở 21/128 trường hợp retriever Top3 *không* đưa target vào tập chọn, đổi value target khiến `B3` và `C3` có NLL **bằng nhau bit-exact**. Ở 107 trường hợp target được chọn, trung bình `NLL(C3)-NLL(B3) = 0.5040483318756674`. Điều này hỗ trợ Reader có đáp ứng value khi card được chọn, nhưng vẫn chưa thể gọi semantic ranker là thành công. Thậm chí ở 21 miss, B3 đôi khi cải thiện so với A nhờ tác động của distractors; không được nhầm với tìm đúng fact.

## 4. QA độc lập và giới hạn khoa học

Các phần tử **22/22 PASS**: kiểm tổng số per-story, ID, 6 NLL arm finite, gates, token count, recall monotonic, rank/value invariance, miss-target swap invariance, phép cộng/trừ ghép cặp, seed-independent bootstrap sensitivity, source pins, no-TRAIN/DEV/TEST flag và logic FAIL theo tiêu chí đã khóa.

- Đây là **một số liệu khoa học âm tính có giá trị**, không phải lỗi checkpoint hoặc bug runner đã biết.
- **FAIL chỉ áp dụng** cho `R_FULL_COSINE` với mean frozen question/key embeddings, 32 records gồm 4 hard negatives, 128 PROBE synthetic, một Reader và checkpoint. Không phủ định mọi kiến trúc Vector Memory.
- Reader đã học ban đầu với singleton Oracle; Top3 nhiều records là **out-of-training-distribution**. Vì thế không gán mọi chênh lệch NLL cho duy nhất retriever; tuy nhiên **Recall@3** được đo riêng và FAIL là bằng chứng rõ ràng về bước xếp hạng đã khai báo.
- PROBE có seed công khai và đã được dùng để đánh giá. Từ nay **không được dùng chính PROBE 128 này làm heldout confirmatory mới** sau khi chọn hay điều chỉnh retriever; không thực hiện backtest lặp lại để chốt lựa chọn.
- Không mở TEST hoặc GPU. Không sửa Reader. Không chạy lại one-shot.
- Không đánh đồng với L0020: **L0020 PASS_DEV_SCREEN_GO_CANDIDATE_SCOPED** vẫn giữ nguyên (Reader với Oracle singleton trên DEV khác); thí nghiệm Top-k không Oracle tiếp theo là một câu hỏi riêng.

## 5. Phán quyết cuối và kế hoạch

**Kết luận khoa học `FAIL_RETRIEVAL_SCOPED`; `READER_VALUE_USE_SIGNAL=POSITIVE_EXPLORATORY`; `TEST=SEALED`; `ONESHOT=CONSUMED`; `TRAINING=NO`; `GPU=NO`.**

Chỉ ghi metadata công khai vào `artifacts/research/vector-memory/TTM_VM_TOPK_128_NONTEST_CPU_ONE_SHOT_INDEPENDENT_RECOMPUTATION_20261112.json`; giữ NLL/gate từng truyện và Reader binary trên owner Windows. `lineage.md` append **L0021**, không sửa L0020 hay bất kỳ kết quả cũ; `main` không đổi.

**Bước thực hiện tiếp theo:** `TTM_VM_TOPK_FAILURE_CAUSE_AND_NEW_NONTEST_RETRIEVER_REDRAFT_DESIGN_ONLY`: cân nhắc truy xuất exact-key hoặc hybrid lexical-first với Reader đã khóa trên **một tập PROBE hoàn toàn mới** và tiền đăng ký rõ giới hạn; không chạy lại PROBE 128 đã xem, không mở TEST và không cấp GPU.
