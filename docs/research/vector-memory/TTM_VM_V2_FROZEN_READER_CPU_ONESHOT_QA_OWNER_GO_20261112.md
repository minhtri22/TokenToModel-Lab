# TTM Vector Memory V2 — Frozen Reader CPU one-shot: Scorer QA 78/78 và phát hành GO có điều kiện

**Operation:** `TTM_VM_V2_FROZEN_READER_CPU_SCORER_ONEPACKET_INTEGRATION_QA_OWNER_RELEASE`  
**Ngày:** 2026-11-12  
**Nhánh:** `research/ttm-vector-memory-architecture-20261111`  
**Quyết định duy nhất:** **`GO_SCOPED_ONE_CPU_ONESHOT_SUBJECT_TO_OWNER_PREEXEC`**. *GO có điều kiện*: chỉ khi owner Windows chạy gói tiền kiểm, tất cả Git blobs/SHA và QA 78/78 đạt PASS; không phải báo cáo science đã thực thi.

## 1. Bằng chứng nhận từ owner

- `V2_PRIVATE_FIXTURE_ON_D=PASS`; owner đã sinh 192 case, 32 cards/case trực tiếp trong dự án D:, SHA256 `1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d`.
- `V2_SOURCE_NEGATIVE_QA=PASS_72_72`, source pin `be3d24e6e86b7983f8882a6689a09fd6155fded7`; receipt owner SHA256 `91f199f076b30006e35e5092a9b69623b0786bf6909bb225863d048ec4081870`.
- `V2_PROBE_RETRIEVAL_OR_NLL=NOT_EXECUTED`; TRAIN/DEV/TEST/GPU không sử dụng; `lineage.md` vẫn L0021.

## 2. Scorer mới và pin không đổi

- Scorer `tools/research/vector-memory/v2_frozen_reader_cpu_one_shot.py`: blob `e9e29c35e4eeeda6ed3ad5a4481a75b51e5b4eab`, SHA256 `978dd0de1c1cec0bb686bd0a039abb85a0fb6431f8e77f1d8a97dc819835d5b4`.
- QA độc lập `v2_independent_one_shot_scorer_qa.py`: blob `06ba0bd001293f759a0783f81e3ce4cc9ae0142e`, SHA256 `c91378672914bfdc1e59faac43b2ffa9b23e527b1ab1eea8595c66ea5a82db58`.
- **Frozen source commit:** `df7865a420cbd5d58d5f24a55b85f99c9242038e`, gồm runner, QA và receipt công khai; commit tài liệu sau không làm thay đổi source này.
- Reader L0020 SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`; backbone P02 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; T1 manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Các nguồn v2 fixture/retriever vẫn pinned theo prereg: Git blobs `01703d4786872a66459593d27cd7607b66c895dd` và `dc733eda42d768d695309e3a1d5df25aeabb28b7`. **Không đọc lại hoặc tái chấm PROBE 128 L0021.**

## 3. QA đã thực hiện — chỉ trên mô hình và dữ liệu giả lập

Independent scorer QA **78/78 PASS**, local CPU torch 2.10.0, mock ASCII tokenizer, backbone/Reader ngẫu nhiên và ngân hàng 32 cards thủ công **không thuộc 192 PROBE mới**. Kiểm Answer-only NLL bằng log_softmax tham chiếu khác đường F.cross_entropy, ba Retriever S0/S1/S2, sáu arm A/O1/B1/C1/B3/C3, bản ghi đúng/sai cùng mask và key, no-memory bypass bit-exact, `ABSTAIN` là miss và bypass, 2.000 bootstrap ghép cặp 64 case S2 seeds 20261116/20261117, kiểm tra negative không có `--execute-once` và chặn output tồn tại.

Trong quá trình kiểm thử phát hiện/đã sửa lỗi NumPy truth ambiguity trong tổng hợp NLL, trước khi Git blob nguồn được khóa. **QA không chạy Retriever hoặc inference của 192 PROBE thật, không đọc trained Reader/GPT binary; không chứng minh scientific outcome.**

## 4. Gói owner PS5.1 fail-closed

Script `tools/research/vector-memory/Invoke-TTM-VM-V2-FrozenReader-OneShot-Owner-PS51.ps1`, Git blob `7ab0492d864e7e73d4dc8c5b65b3193518fa15b8`.

- Mặc định: một lượt tiền kiểm tất cả source Git blob và private SHA256, checkout detached source pin trên **worktree v2 đã có**, owner QA 78/78, main unchanged; không làm inference.
- `-ExecuteOnce`: chỉ nếu trên đã PASS, chạy **một lượt CPU FP32, 2 threads** trên 192 cases và sáu arm; song song không chạy TRAIN/DEV/TEST/GPU.
- Output `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1`, tạo `ONE_SHOT_STARTED.json` trước case đầu; không retry/overwrite/delete khi lỗi.
- Python312 executable được đọc từ C: nhưng Pycache, tempfile và chứng cứ được giữ ở project D:.
- Owner QA 78/78 **chưa chạy ở Windows tại lúc ký quyết định**. Mọi sai SHA, thiếu source, QA mismatch, thư mục output tồn tại hoặc main thay đổi = HOLD, **không vượt rào bằng sửa seed/hyperparameter**.

## 5. Tiêu chí khoa học trên S2 đã khóa, không đổi hậu nghiệm

- Chỉ 64 câu `S2_DESC_PARAPHRASE` là primary, `R_HYBRID_LEX_FIRST` Top-1 với mô tả **từ vựng đóng + kiểm duy nhất bộ ba thuộc tính**. Đây không phải kiểm chứng semantic retrieval tự do.
- Recall@1 ít nhất **58/64**; `NLL(A)-NLL(B1)` và `NLL(C1)-NLL(B1)` ≥0,05; hai cận dưới percentile bootstrap 95% >0, **2.000 lần**, seeds 20261116,20261117; control Oracle `NLL(A)-NLL(O1)` ≥0,05.
- S0 ID-literal (Oracle-equivalent), S1 alias và S2 Top3 chỉ diagnostic. `ABSTAIN` tính miss; counterfactual chỉ thay value target.
- Thứ tự phân xử: evidence invalid → HOLD; Oracle fails → HOLD; S2 Recall fails → FAIL retrieval; NLL fails → FAIL Reader transfer; tất cả PASS → `GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED`, **không phải TEST PASS**.

## 6. Quyết định và bước sau

**`SOURCE_QA=PASS_72/72` · `OWNER_V2_FIXTURE=PASS_SHA` · `SCORER_MOCK_QA=PASS_78/78` · `OWNER_SCORER_NATIVE_QA=PENDING` · `RELEASE=GO_CONDITIONAL_OWNER_PREEXEC` · `SCIENCE=NOT_EXECUTED` · `TEST=SEALED` · `GPU=NO` · `LINEAGE=L0021_UNCHANGED` · `MAIN=UNCHANGED`.**

**Bước thực hiện tiếp theo:** `TTM_VM_V2_OWNER_CPU_ONE_SHOT_192_EXACT_SOURCE_PREEXEC_AND_EXECUTE_IF_GO`. Sau khi owner đã chủ động chạy `-ExecuteOnce`, chỉ đọc lại kết quả và tính toán độc lập để phân xử; không rerun hay đổi phiên bản.
