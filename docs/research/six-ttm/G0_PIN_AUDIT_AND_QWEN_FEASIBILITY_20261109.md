# G0 — Kiểm toán mốc SIX và tính khả thi trích xuất Qwen (chỉ đọc)

**Ngày kiểm toán:** 2026-11-09  
**Trạng thái:** `G0_SOURCE_PIN_AUDIT_PASS_SCOPED / QWEN_API_FEASIBLE_ON_PAPER / SCIENCE_NOT_RUN`  
**Kho đích:** `minhtri22/TokenToModel-Lab`  
**Nhánh đích:** `research/ttm-six-cross-model-representation-transfer-20261109`  
**Main nguồn TTM (snapshot ban đầu):** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`  
**Phụ thuộc:** `UPSTREAM_SIX_PINS_AND_CHARTER_20261109.md`. Văn bản này bổ sung kết quả G0, không sửa hoặc thay thế bất kỳ kết luận gốc nào của SIX.

## A. Quy trình kiểm toán và mức độ tin cậy

1. Đọc lại 6 **commit SHA đầy đủ** của `minhtri22/CLDP`, xác minh đường dẫn tệp được thay đổi và nội dung verdict trong commit diff.
2. Đối với `SIX_COMPOSITION_REPRESENTATION_INFORMATION_LOCALIZATION`, truy xuất trực tiếp Git blob raw `7ed20fcf606b7c2a21aab2016f03c2db686f5cf3` và Git blob QA `ff8018391025f7dc3b4526814c51ce1074097f05`.
3. Tính SHA-256 từ bytes UTF-8 nhận được; thuật toán SHA-256 có self-test `abc -> ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`. Đọc hàng seed-level từ raw JSON và **tự tính** trung vị, đếm seed đạt cổng, không dựa vào trường `pass`/ `summary` có sẵn.
4. Phân biệt `COMMIT_CONTENT_VERIFIED` với `RAW_RECALCULATED`: chỉ một thí nghiệm SIX-REP-INFO được kiểm tra lại trên raw JSON trong G0; không chạy lại khoa học và không tự thẩm định lại mọi họ thử nghiệm khác.
5. Không có thao tác lên repo SIX. Không kiểm tra local Windows; SHA ở đây được xác minh trên GitHub.

### A1. Ma trận các mốc đã ghim

| Mã | Commit bất biến | Tệp nguồn ở commit | Kết quả nguyên gốc | Cấp độ kiểm tra G0 |
|---|---|---|---|---|
| R0 PARENT | `32c528104c4d16eddb0d8ba094e5d117234ba524` | `research/six_open_model_r0_parent_freeze_2026_10_07/FORMAL_CONVERGENCE_CLOSURE.json` | `FORMALLY_CLOSED`, candidate BASIS15, không phải bất biến cuối | `COMMIT_CONTENT_VERIFIED` |
| REP INFO | `2fc30fba568fd3782d32fd9cb3caa172d26f7853` | `research/lineage.md` | `FUNCTIONAL_BASIS_COMPOSITION_INFORMATION_PRESERVED_UNDER_QUALIFIED_I1` | `RAW_SHA256_AND_SEED_MEDIANS_RECALCULATED` |
| ORACLE | `a9d9ceb33fbbc7ad2ed3fd495cb1e7b0917a7f02` | `research/six_composition_oracle_learner_cause_localization_confirm_recovery3/FORMAL_CLOSURE.json` | `CLOSED_PASS_ADJUDICATED`; seeds 91..95 | `COMMIT_CONTENT_VERIFIED` |
| COMP NEG | `9ef06b141bdd0fb42255f361e426b2359bb0a84e` | `research/lineage.md` | Composition learner FAIL; tổng thể `INCONCLUSIVE` | `COMMIT_CONTENT_VERIFIED` |
| BASIS QUAL | `1d9f91b6562410c4c62f90010f8cf5cb144cc15f` | `research/lineage.md` | Learner competence FAIL; tổng thể `INCONCLUSIVE` | `COMMIT_CONTENT_VERIFIED` |
| OW1 SHIFT | `9720ef5671990479db86fee7af8668d389f3bd30` | `research/six_ow1_distribution_shift_invariance/FORMAL_CLOSURE.json` | `FAIL_ALL_THREE_PRIMARY_SHIFT_AXES` | `COMMIT_CONTENT_VERIFIED` |

**R0 giới hạn:** nội dung mốc R0 nêu điều kiện riêng cho một nghiên cứu SIX × CQG. Nghiên cứu SIX × TTM mới không phải khởi tạo nghiên cứu hội tụ CQG và không được tự nhận là vượt qua điều kiện CQG hoặc được phép nâng kết luận R0.

### A2. Bằng chứng trích xuất và tái tính cho REP INFO

- Raw Git blob: `7ed20fcf606b7c2a21aab2016f03c2db686f5cf3`; UTF-8 byte count = **9040**.
- Raw SHA-256 được tính lại = `81a1ad556160b935651bc9cfc2db28533c3d4efa647d191acc828e65e82c208d` = **MATCH** với lineage.
- Independent-QA Git blob: `ff8018391025f7dc3b4526814c51ce1074097f05`; UTF-8 byte count = **3143**; SHA-256 tính lại = `b2ce666ae95a7b98ba7d75e92614370874e79f7380067ecf852c98894fb1da4b`.
- Raw seed set: `96,97,98,99,100`.
- Quan sát từ raw: cả 5/5 seed có IID NRMSE <=0.25 và cả 5/5 seed có HELDOUT NRMSE <=0.30. Đây là **số lượng đạt thực tế**, không suy diễn số seed tối thiểu của tiền đăng ký từ raw; ngưỡng và verdict nguyên gốc giữ nguyên.

| Biểu diễn | IID median tính từ 5 hàng raw | Held-out median tính từ 5 hàng raw | Số seed dưới ngưỡng IID / heldout |
|---|---:|---:|---|
| PHI8_ORACLE | 0.10472236963822018 | 0.12332361531184108 | 5/5 · 5/5 |
| FULL_RESPONSE576 | 0.1328885338512729 | 0.1576526876152328 | 5/5 · 5/5 |
| BASIS15 | 0.11782223774034631 | 0.14110009692776485 | 5/5 · 5/5 |
| IDENTITY16 (chẩn đoán) | 0.10535934078066159 | 0.12274159527574731 | kiểm chứng medians; diagnostic-only |

**Kết luận G0:** xác nhận được phép tái tính medians và SHA nguồn đã ghi. Không suy ra thành công trên biểu diễn học được của Qwen/TTM, không suy ra BASIS15 cần thiết/duy nhất. `IDENTITY16` cũng đạt; OW1 đã FAIL với chuyển thẳng subspace dưới shift. Không dùng hệ quả này để tự cấp phép thực nghiệm mới.

**Giới hạn audit:** Không tái chạy thuật toán khoa học gốc, không xác minh máy thực thi cũ, không kiểm lại tất cả 6 raw-evidence chain. Từ `RAW_RECALCULATED` chỉ áp dụng cho số liệu REP INFO, không phải các lane khác.

## B. Nguồn mô hình Qwen — revision chính xác, giấy phép, API

Thông tin từ các trang model/config của Hugging Face và tài liệu Transformers Qwen3 được đọc công khai ngày 2026-11-09; **chưa download trọng số/tokenizer**.

| Trường | Teacher ưu tiên | Teacher đối chiếu |
|---|---|---|
| Mô hình | `Qwen/Qwen3-0.6B` | `Qwen/Qwen3-1.7B` |
| Revision 40 ký tự | `c1899de289a04d12100db370d81485cdf75e47ca` | `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` |
| Cấu hình | `Qwen3ForCausalLM` | `Qwen3ForCausalLM` |
| Hidden size | 1024 | 2048 |
| Transformer layers | 28 | 28 |
| Vocab size | 151936 | 151936 |
| Checkpoint dtype | bfloat16 | bfloat16 |
| Tổng tham số theo metadata | ~751.6M | ~2031.7M |
| License metadata và tệp LICENSE | Apache 2.0 | Apache 2.0 |
| Truy xuất trạng thái ẩn | `output_hidden_states=True` → `outputs.hidden_states` | Tương tự |
| Trạng thái G0 | `API_CONFIRMED_NO_RUNTIME` | `API_CONFIRMED_NO_RUNTIME` |

Các tệp `config.json`, tokenizer và trọng số phải được lấy từ **chính revision** phía trên, không dùng `main` động. Ghim thêm SHA-256 các tệp tải thật và phiên bản `transformers`/`torch` trước khi chạy. Transformers Qwen3 cần phiên bản có hỗ trợ `qwen3` (trang model cảnh báo bản < 4.51.0).

Tài liệu API: đối tượng `Qwen3ForCausalLM` nhận `output_hidden_states=True`; output là tuple gồm embedding (nếu có) và lớp, mỗi tensor `[batch, sequence_length, hidden_size]`. Với 28 lớp, dự kiến tới 29 trạng thái; cần kiểm tra bằng runtime với revision/version đã pin. **Không phải** chứng cứ đã load model hoặc thử nghiệm extraction thực.

Tham chiếu:
- https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca
- https://huggingface.co/Qwen/Qwen3-1.7B/tree/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e
- https://huggingface.co/Qwen/Qwen3-0.6B/blob/c1899de289a04d12100db370d81485cdf75e47ca/config.json
- https://huggingface.co/Qwen/Qwen3-1.7B/blob/70d244cc86ccca08cf5af4e1e306ecf908b1ad5e/config.json
- https://huggingface.co/docs/transformers/main/model_doc/qwen3

### Quyền nguồn và giới hạn tích hợp

Apache-2.0 cho phép nghiên cứu mô hình theo điều kiện của giấy phép; vẫn phải lưu bản license, attribution/notices khi phân phối và kiểm tra quyền của corpus, teacher-generated outputs, dữ liệu trung gian trước phát hành. TinyStories của pilot TTM có đánh giá quyền riêng; **không** tự biến `CDLA-sharing-1.0` thành Apache-2.0. Không được truy cập TEST cho huấn luyện teacher adapter hoặc chọn lớp Qwen.

## C. Phương pháp lấy biểu diễn dự kiến, chưa chạy

Dự kiến `model.eval()` + `torch.inference_mode()`, chạy forward qua Transformers, `use_cache=False`, `output_hidden_states=True`, `return_dict=True`; khóa `revision`, `tokenizer`, input bytes, preprocessing, attention mask, padding, truncation, dtype, version. **Trạng thái ẩn phải lấy từ forward chứ không coi API Ollama/OpenAI tương đương khả năng truy cập tensor**.

Hai lựa chọn trình bày vector theo **cùng tiền tố văn bản**: last-valid-token state và masked mean pooling (phải quy định trước, đặc biệt với padding bên trái/phải); không ghép vị trí token giữa Qwen với TTM vì tokenizer khác nhau. Không dùng suy luận trên tập TEST niêm phong trước thời điểm đánh giá cuối.

Lưu thông tin layer index, tensor shape, finite values, PCA/CKA diagnostics, file SHA, revision, rights; không ghi hàng loạt tensor lớn vào GitHub.

**Kết luận G0 về Qwen:** `MODEL_METADATA_AND_API_FEASIBILITY=PASS_DOCUMENTATION`; `LIVE_HIDDEN_STATE_SMOKE=NOT_EXECUTED`; `MODEL_FILE_SHA256=NOT_PINNED`; `SCIENCE_PERMISSION=NOT_GRANTED`.

## D. Ràng buộc từ TTM

- `main` tại mốc đọc G0 = `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`; pilot PR #12 vẫn draft, HEAD có thể tiếp tục thay đổi.
- Đã đọc `docs/pilot/TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md` trên nhánh pilot: T1 dữ liệu/split, T2 GGUF F32, T3 Colab/Drive synthetic resume PASS có giới hạn; **T4 scientific lock HOLD**, runner chưa khoa học khóa.
- Kiến trúc ứng viên TTM 3,749,376 tham số, hidden width 256, context 256, tokenizer 2048; không được thay đổi để thuận tiện cho nghiên cứu mới. Kết quả T3 synthetic checkpoint không phải baseline huấn luyện thật.
- Giai đoạn G1/G2 có thể chuẩn bị thiết kế kiểm định trên teacher và fixture synthetic, **G3 sử dụng TTM đối chứng chỉ sau khi một checkpoint/baseline khoa học được pin và phép thử độc lập được chấp thuận**.

## E. Kết luận giới hạn G0

`SIX_PINS_EXIST_AND_CONTENT_MATCH=PASS` · `SIX_REPINFO_RAW_HASH=PASS` · `SIX_REPINFO_MEDIANS=PASS` · `OTHER_SIX_RAW_FULL_AUDIT=NOT_PERFORMED` · `QWEN_METADATA_LICENSE_API=PASS_DOCUMENTATION` · `QWEN_RUNTIME_EXTRACTION=NOT_EXECUTED` · `TTM_MAIN=UNCHANGED_BY_G0` · `TRAINING=NONE` · `PREREG=DESIGN_DRAFT_ONLY`.

**Tiếp theo:** xây bộ tiền đăng ký G1/G3, kiểm tra khả thi API với fixture không mang dữ liệu khoa học chỉ sau khi có khóa phiên bản, giấy phép và ngân sách; không tự chạy train.
