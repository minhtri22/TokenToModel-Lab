# G1 — One integrated admission readiness / nguồn, quyền dữ liệu, Qwen3-1.7B, độc lập và quyết định

**Ngày:** 2026-11-09  
**Thao tác:** `TTM_SIX_XMODEL_G1_INTEGRATED_ADMISSION_READINESS_DATA_RIGHTS_QWEN17_AND_INDEPENDENT_ADJUDICATION`  
**Phán quyết cuối lượt:** `G1_ADMISSION=HOLD_MATERIAL_PREREQUISITES`. **Không có science permit G1**, không chạy G1 thực nghiệm và không thay G3.  
**Quyết định machine-readable:** `G1_INTEGRATED_ADMISSION_READINESS_DECISION_20261109.json`.  
**GitHub:** `minhtri22/TokenToModel-Lab`, nhánh riêng `research/ttm-six-cross-model-representation-transfer-20261109`.  
**Biên giới:** không động `main`, PR #12, `lineage.md`, `minhtri22/CLDP` và checkpoint TTM. Bằng chứng Qwen0.6B `PASS_TECHNICAL_ONLY` được giữ, không rerun.

## I. Ma trận kết luận duy nhất

| Cổng trọng yếu | Bằng chứng đọc được | Verdict |
|---|---|---|
| SIX provenance và G0 | Sáu pin gốc, một raw REP INFO đã tái kiểm medians/hash ở G0; FAIL OW1 và INCONCLUSIVE khác bảo toàn | **PASS_SCOPED_SOURCE_ONLY** |
| Qwen3-0.6B technical | Colab T4 receipt của chủ sở hữu, Qwen weight SHA matching, 29 hidden states, 11/11 consistency | **PASS_TECHNICAL_NO_REPEAT** |
| Quyền dữ liệu TinyStories | HF dataset metadata `CDLA-Sharing-1.0`; điều khoản sử dụng/Computational Use và nghĩa vụ Publish được đọc từ CDLA chính thức | **DOCUMENTATION_PASS / OWNER_G1_SCOPE_HOLD** |
| T1 source và split provenance | T1 TRAIN SHA `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`; T1 split receipt SHA `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; QA Git blob `3b5613fdabc00f44b7524ac9dad486b1be5c3b00`. 2048 TRAIN/256 VAL/64 TEST theo biên bản T1 | **SOURCE_PROVENANCE_PASS_SCOPED** |
| Bytes manifest G1 thực tải / 256 prefix | Không tìm được bytes manifest T1 trong chứng cứ GitHub; không đọc dữ liệu riêng tư từ Windows. Chưa tạo và seal G1 128/64/64 | **HOLD_DATA_REAL_MANIFEST** |
| Qwen3-1.7B metadata | Teacher `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`, hai shard, config 28 lớp, hidden 2048, Apache-2.0 | **PASS_METADATA** |
| Qwen3-1.7B trọng số nguồn công bố | Two publisher SHA-256 (xem phần II), URL snapshot ghim; script/notebook zero-science đã commit | **EXPECTED_HASH_PINNED / ACTUAL_BYTES_HOLD** |
| Qwen3-1.7B Colab T4 smoke | Chưa được thực thi. Notebook sẵn hai cell preflight và guarded one-shot | **NOT_EXECUTED / HOLD_TECH_TARGET** |
| Hợp đồng khoa học G1 | JSON blob `de049ba00331d90f3c7ae72ab3daf943c766ec82`; method blob `9dcbf31b2835e07922b2aaf66e5895c7d2f8b03b`, QA cấu trúc 25/25 | **PASS_STRUCTURE_ONLY** |
| G1 scientific runner & anti-leakage | Chưa khóa implementation / độc lập QA TEST seal | **HOLD_IMPLEMENTATION** |
| Independent scientific adjudication | Đã có review packet đối kháng từ cùng phiên trợ lý. **Không có reviewer tách biệt chứng thực** | **NOT_PERFORMED / HOLD** |
| G1 science permission | Quyền dataset scope, manifest, Qwen1.7B, implementation, reviewer chưa đồng thời đạt | **HOLD** |

## II. Qwen3-1.7B: tài nguyên, mã băm, bộ kiểm tra đã chuẩn bị

Mô hình mục tiêu **không** được xem là PASS vì Qwen0.6B từng PASS. SHA-256 nguồn công bố cho 2 shard:

- `model-00001-of-00002.safetensors`: `169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5` (3.44GB).
- `model-00002-of-00002.safetensors`: `912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9` (622MB).
- Các file khác config/tokenizer/index/LICENSE phải tính SHA-256 khi tải đúng revision; không ghi giả giá trị thực tải.
- Nguồn công bố:
  - https://huggingface.co/Qwen/Qwen3-1.7B/tree/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e
  - https://huggingface.co/Qwen/Qwen3-1.7B/blob/8d4744f9e13072f4920c326350fa81eedb74eae9/model-00001-of-00002.safetensors
  - https://huggingface.co/Qwen/Qwen3-1.7B/blob/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/model-00002-of-00002.safetensors

**Source-only đã commit**:
- `scripts/research/six_ttm/g1_qwen17_zero_science_technical_readiness_v1.py`; Git blob `1a815a5572136a93cd9a292705b75a8a17002a97`.
- `notebooks/six_ttm/TTM_SIX_G1_QWEN17_INTEGRATED_READINESS_PREFLIGHT_ONESHOT_SMOKE_20261109.ipynb`; Git blob `3c807149ac16b1d08be3ba70ef57ff5ccf62c679`.
- **16/16 kiểm tra cấu trúc mã và notebook PASS có giới hạn**, gồm sha-before-model-load, two shard index, Colab T4/VRAM guards, preflight không tải trọng số, one-shot marker và không dùng dữ liệu khoa học. **Không phải** Colab py_compile/runtime PASS.
- Ô 1: metadata + code SHA + Python compile + preflight, không tải trọng số. Ô 2: do chủ sở hữu chủ động chạy **chỉ sau preflight PASS**, tải tổng ~4.08GB và tính SHA thực tế trước model load, một synthetic fixture, kiểm 29 hidden states shape `[1,L,2048]`, finite, repeatability, peak GPU reserved<=12GiB. Không train, không đọc TinyStories, không chạy 0.6B.
- Cổng tài nguyên ứng viên từ manifest G1: Colab Free T4, FP16, 11GiB GPU rảnh tối thiểu, 12GiB disk rảnh, 60 phút/teacher. Không được tự claim runtime theo con số 0.6B.

## III. Phân tích giấy phép và quyết định dữ liệu

Hugging Face khai báo `roneneldan/TinyStories` là `CDLA-Sharing-1.0`; các mô hình Qwen là Apache-2.0. Đọc từ nguồn license chính thức: https://cdla.dev/sharing-1-0/ và https://cdla.dev/faq-resources/faq/.

- Điều 2.1 của CDLA-Sharing-1.0 cấp quyền **Use Data** (bao gồm computational use) có điều kiện; đây là **bằng chứng khả dụng theo giấy phép**, không phải xác nhận mọi nguồn cá nhân trong truyện hoặc mọi hình thức công bố.
- Điều 3.1–3.3 có điều kiện về việc **Publish Data / Enhanced Data**, giữ ghi công và thông báo sửa đổi; **Results** được định nghĩa riêng (không chứa hơn de-minimis bản gốc) và Điều 3.5 không áp điều kiện trên Results.
- G1 dự kiến dùng private TRAIN-only extraction, giữ raw story text/rows, prefix và features **không công khai**, chỉ công bố metadata không nhạy cảm, số tổng hợp, references và license. Derived embeddings có thể tùy trường hợp là Results hay Enhanced Data; **không tự đưa ra kết luận pháp lý chung** cho toàn bộ xuất bản.
- Chủ sở hữu chưa ghi quyết định chấp nhận riêng phạm vi quyền và chính sách lưu derived representations của G1. **`DATA_G1_SCOPE_APPROVAL=NOT_RECORDED`**. Đây là một mục trong quyết định science tích hợp, không cần một chuỗi micro-permits.

**Số liệu T1 qua GitHub:** `evidence/pilot/t1-real/T1_RESULT.json`, `TTM_T1_INDEPENDENT_QA.json` và `TTM_T1_IPV4_PINNED_SOURCE_ACQUISITION.json` đã được đọc. Giới hạn near-duplicate chỉ trong tập active pilot; không suy diễn đã khử trùng lặp toàn bộ corpus. T1 manifest `T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json` có hash nhưng **không thấy raw manifest bytes trong các file t1-real vừa đọc**. Tên nguồn không đồng nghĩa đường file local đang tồn tại: trước khi G1 science cần đọc riêng đúng file manifest có hash và sinh 256 G1 prefix, kiểm zero-overlap và seal TEST G1, không mở TTM VAL/TEST.

## IV. Phản biện tích hợp và phán quyết

- Về khoa học: hợp đồng đã xác định 128/64/64, 8 functional probes, layer28, ridge, direct source→response baseline, shuffle null, positive control, permutation/bootstrap, test-only-once. Đây vẫn là **ứng viên G1 scoped feasibility**, không phải luật SIX hay G3 benefit.
- Lỗ hổng thực chất: thiếu actual manifest, thực thi target 1.7B, science runner exact source, independent reviewer. Với `n_TEST=64`, power confirmatory vẫn chưa được định lượng; các âm tính dưới điều kiện không đủ lực phải `INCONCLUSIVE`, không mặc định `FAIL`.
- Phản biện từ cùng phiên trợ lý và static QA có thể phát hiện lỗi cấu trúc, **không đáp ứng yêu cầu independent scientific adjudication**. Không tạo “chữ ký” reviewer giả. Một người/agent khác cần đọc exact blob JSON và Markdown, đánh giá corpus/rights/negative controls/stats/test-seal, phát hành verdict riêng có source SHA.
- **Kết luận thực hiện:** `SOURCE_LICENSE_REVIEW=PASS_SCOPED`, `SOURCE_MANIFEST_G1=HOLD`, `QWEN17_METADATA_AND_PUBLISHED_HASHES=PASS_DOCUMENTATION`, `QWEN17_LIVE_TECHNICAL=NOT_EXECUTED`, `INDEPENDENT_SCIENCE_REVIEW=NOT_PERFORMED`, `G1_SCIENCE_AUTHORIZATION=HOLD`, `G1_SCIENCE_NOT_EXECUTED`.

Không tự cấp quyền science sau một smoke target17; nếu 1.7B đạt, tất cả các điều kiện khoa học còn lại vẫn phải qua cùng **một** lượt adjudication cuối. G1 không đồng bộ hoặc cản trở TTM-Small-4M (ở `main` riêng; T4/T5 tiến độ riêng). Không sửa repo SIX, main, PR #12, checkpoint hay `lineage.md`.

## V. Cách hoàn tất đúng một lượt còn lại

1. Chủ sở hữu xác nhận phạm vi **private computational G1** theo CDLA-Sharing-1.0, policy lưu trữ/trích xuất và không công bố dữ liệu thô; đọc lại bytes T1 manifest, xác minh SHA, tạo/niêm phong G1 128/64/64 từ đúng 2.048 TRAIN.
2. Dùng notebook target17 đã ghim: **ô 1 trước**, nếu PASS chạy **ô 2 một lần**. Đọc receipt SHA-256 của cả hai shard và hidden tensor; giữ STOP nếu FAIL, không chạy lại Qwen0.6B.
3. Đóng băng/QA độc lập science runner theo JSON v1 và method đã pin; reviewer **khác tác giả** thẩm định cả quyền, leakage, kiểm định, power limitation, và receipts rồi chủ sở hữu quyết định **G1_SCIENCE_AUTHORIZED** hoặc **HOLD**. Không mở một loạt giấy phép kỹ thuật rời rạc.

**Bước thực hiện tiếp theo:** `TTM_SIX_XMODEL_G1_FINAL_MATERIAL_EVIDENCE_READBACK_AND_DISTINCT_SCIENCE_ADJUDICATION`. Chỉ khi tất cả điều kiện đều có bằng chứng mới quyết định G1 science one-shot. Khi chưa có bằng chứng, HOLD được ghi nhận như một kết luận có phạm vi, không phải thất bại khoa học.
