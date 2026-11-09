# G1 v1a — Sửa đổi vật hóa định danh, đối chứng và hợp đồng khoa học trước thực thi

**Ngày:** 2026-11-09  
**Trạng thái:** `AMENDMENT_CANDIDATE_SOURCE_PINNED / DISTINCT_REVIEW_PENDING / SCIENCE_HOLD`  
**Phạm vi:** `TTM_SIX_XMODEL_G1_SCIENCE_RUNNER_IMPLEMENTATION_INTEGRATED_QA_AND_DISTINCT_PREEXECUTION_REVIEW`.

## Quy tắc thay đổi: không sửa kín đáo hợp đồng v1

Hợp đồng gốc `docs/research/six-ttm/G1_SCIENCE_PREREG_V1_CONTRACT_CANDIDATE_20261109.json` giữ nguyên blob `de049ba00331d90f3c7ae72ab3daf943c766ec82`. Văn bản phương pháp gốc giữ nguyên blob `9dcbf31b2835e07922b2aaf66e5895c7d2f8b03b`. Biên bản này là **v1a amendment candidate**, chưa phải một science prereg được reviewer chấp thuận. Tiền đăng ký thay đổi phải được reviewer adjudicate rõ trước bất kỳ feature extraction từ G1 data.

### A. Diễn giải T1 SHA và chỉ số dòng

T1 gốc lưu content identity `SHA256(UTF8(original_story.strip()))` mà không ghi `source_row_index`. G1 v1a ánh xạ mỗi identity về **lần xuất hiện đầu tiên (first occurrence)** khi duyệt file TinyStories TRAIN gốc, dùng chỉ số truyện 0-based và xác nhận SHA tệp nguồn `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`. Không dùng TTM original VAL/TEST.

Bằng chứng đã niêm phong: manifest G1 `SHA256=6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`; 128 TRAIN / 64 DEV / 64 TEST; 29/29 metadata-QA PASS (owner console + remote READY readback). Original source rows scanned: 2,119,489. 2,048 eligible, bỏ 23 tiền tố trùng, còn 2,025 unique prefixes; 363 identities được chọn trong T1 có nhiều occurrence trên tập raw. **Không mở lại dữ liệu hoặc sinh manifest lần hai.**

### B. Ngăn trùng trước chia ba tập

v1a sắp xếp candidate bằng SHA của `TTM_SIX_G1_V1|source_row_index|normalized_story_sha`, rồi loại trùng theo SHA normalized story và SHA normalized prefix trước khi cắt 128/64/64. Giữ candidate đầu tiên theo key ổn định. Đây là thay đổi có chủ đích so với mô tả v1 chưa định nghĩa xử lý `duplicate_prefix`. Thẩm định độc lập phải quyết định liệu thay đổi quy tắc mẫu trước TEST là chấp nhận được; không giả vờ tập v1 chưa sửa.

### C. Mô hình/đối chứng được giữ nguyên

- Chỉ G1 prefix từ T1 TRAIN, hai frozen Qwen: 0.6B `c1899de…` / 1.7B `70d244…`, hidden 1024/2048, primary `hidden_states[28]`, mỗi mô hình tokenize prefix độc lập.
- Chấm đúng 8 cặp continuation gốc; tokenize prefix và continuation **riêng**, nối token IDs; đây là log-likelihood **theo token sequence**, không khẳng định bằng raw-string concatenation tokenization. Chuẩn hóa logP theo byte UTF-8 của continuation.
- A: ridge source hidden → target hidden, sau đó P: ridge target hidden → 8 scores. Lambda `[1,10,100]`, chọn theo DEV và hòa điểm lấy alpha lớn hơn.
- B-direct: source hidden → target 8 scores bằng ridge cùng grid/DEV; C-oracle: target hidden → target 8 scores; D-shuffle: 1.000 lần hoán vị **TRAIN pairs**, mỗi lần tự chọn alpha bằng DEV; E-mean: target response TRAIN mean; CKA permutation 1.000; bootstrap 2.000 nhóm story.
- **Sửa vị trí của F-random:** phép xoay trực giao toàn hạng sau chuẩn hóa giữ nguyên isotropic ridge về mặt toán học. Nó là *basis-invariance neutral diagnostic*, không được đếm như destructive null. Đối chứng tráo cặp D-shuffle là destructive null. Cơ chế `P(A(s))` vẫn là một hàm tuyến tính của `s`; so sánh với B-direct là bắt buộc, không được tuyên bố SIX-specific causal mechanism từ G1.

### D. Ngưỡng định lượng giữ nguyên v1

`macro_R2_A >=0.10`; gain vs shuffled-null p95 `>=0.10`; permutation `p<=0.01`; paired bootstrap 95% lower `>0`; centered linear CKA permutation `p<=0.01`; oracle macro R2 `>=0.20`. Tất cả 8 chiều giữ nguyên. TRAIN target response population std bất kỳ chiều `<1e-5` thì STOP trước TEST; TEST SST bất kỳ chiều `<1e-8` thì INCONCLUSIVE sau one-shot. TEST n=64 chỉ đủ *scoped feasibility*, không có tuyên bố 80% power. Kết quả âm không đủ điều kiện kiểm soát → INCONCLUSIVE, không suy là không có chuyển giao.

### E. Scientific runtime / private staging là phạm vi mới, chưa được chấp thuận thực thi

Người dùng trước đây đã phê duyệt **đọc TinyStories TRAIN để niêm phong metadata/hash cục bộ**, không tự động cấp quyền sao chép corpus sang Colab hoặc tạo feature tensors riêng tư. Gói thực thi khoa học tương lai, nếu được chủ sở hữu + reviewer duyệt một lần, sẽ tái dựng prefix trong RAM từ source TRAIN đã ghim, nạp Qwen lần lượt, lưu các feature NPZ numeric riêng tư (`s,t,r` + 256 content-ID SHA) trong project-private workspace, không lưu raw text, không public GitHub. `private_source_staging_approved=true` trong permit riêng **là điều kiện chưa đạt**. Phải ghi rõ việc truyền/lưu nguyên bản TRAIN nếu có để reviewer đánh giá quyền dữ liệu.

## Sources pinned for review

| Artifact | Git blob |
|---|---|
| `scripts/research/six_ttm/g1_science_core_v1.py` | `b3ea8c890c45e3e2d248ad850977b53f5782552e` |
| `scripts/research/six_ttm/g1_science_private_feature_extractor_v1.py` | `f1557470ff66857e35ced71641b542685f6b3083` |
| `scripts/research/six_ttm/g1_science_adversarial_qa_v1.py` | `e6a93ac8248665de78d970ef9d237de5a45d9d8c` |
| `scripts/research/six_ttm/g1_science_preexecution_integrated_qa_v1.py` | `c022de4bdc2eae88b61d1ea2d578302c25c12445` |

**Pre-execution runtime QA:** exact sources executed in isolated assistant Linux Python `3.13.5`, NumPy `2.3.5`; `PASS_SYNTHETIC_ONLY_NO_SCIENCE`, `PASS_ADVERSARIAL_SYNTHETIC_QA_NO_SCIENCE` (14 negative/contract checks), `PASS_EXTRACTOR_SYNTHETIC_ONLY_NO_FILES_OR_GPU`, `PASS_INTEGRATED_SYNTHETIC_QA_SOURCE_PINS` (3 exact blobs, orthogonal neutrality, second marker-open rejection). Full 1,000 shuffled/1,000 CKA/2,000 bootstrap *synthetic* paths PASS, no Qwen or private TEST. These are **author-built engineering tests**, not a distinct scientific review.

**One-shot ordering:** permit/reviewer and blob pins → reconstruct G1 TRAIN numeric features → DEV features → freeze train-only scalers, P/A/B lambda grid and all 1,000 shuffled-alpha choices → *then* one TEST extraction marker → TEST numeric pack → second one-shot TEST read marker before opening TEST feature pack. `G1_SCIENCE_LOCK=HOLD` until **one** distinct reviewer adjudication and owner permit.

**Not included:** raw G1 IDs, source text, continuation outputs, teacher hidden tensors, TEST feature packs, or science results. No changes to TTM `main`, PR#12, `lineage.md`, Qwen 0.6/1.7 technical one-shots or TTM-Small-4M checkpoints.
