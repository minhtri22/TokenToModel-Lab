# TTM EmbeddingGemma 2 — D1 V3 + Qwen targeted follow-up: combined technical receipt adjudication

**Ngày kiểm định:** 2026-11-09.  
**Mã bước:** `TTM_EMBEDDINGGEMMA2_D1_QWEN_TARGETED_TECHNICAL_COMPLETION_AND_COMBINED_RECEIPT_QA`.  
**Quyết định:** `PASS_SCOPED_TECHNICAL_CORE_WITH_POSTRUN_RESOURCE_GATES_UNMEASURED` (**không** phải full uninterrupted `PREFLIGHT_PASS`).  
**Phạm vi quyền:** `D1_D4=NOT_AUTHORIZED`; `SCIENCE=NOT_EXECUTED`; `LINEAGE_UNCHANGED`; `TTM_SMALL_T5=PRIORITY_FIRST`.  
**Đối chiếu:** tải riêng các tệp CLAIM/RESULT **gốc** từ Google Drive và kiểm SHA-256/JSON bằng một tập kiểm tra độc lập. Không chạy lại mô hình, không tạo RUN_ID, không ghi đè DRIVE hoặc TEST.

## 1. Bằng chứng nguyên bản, đọc trực tiếp từ Google Drive

Thư mục Drive: https://drive.google.com/drive/folders/1KfLnhva3SJjuF6R6ttqwGvBdPx5zixK7

| Lượt | Tệp | SHA-256 của bytes nguyên bản | Kết quả |
|---|---|---|---|
| V3 — `ttm_embedgemma2_d1_t4_preflight_st610_once_v1` | `CLAIM.json` | `2ce14ab0c890a53042862c2b376ab12e2927c15ae1c1d1d3e9075f386b4a5999` | Đã tiêu thụ |
| V3 — như trên | `RESULT.json` | `ce693326af246fdf2a3806427b46d89ce05e944a4c99e442b24004677e892427` | `FAIL_OR_BLOCKED_NO_SCIENCE` |
| Qwen bổ sung — `ttm_embedgemma2_d1_t4_qwen_tokenizer_followup_once_v1` | `CLAIM.json` | `70d36ee614990697eda18264c0c130704197fe9b28b13343cf1970fe9468b55d` | Đã tiêu thụ |
| Qwen bổ sung — như trên | `RESULT.json` | `b9f859bc639bd953893b3443b437f23182231e3297149c3cbaaa3bad2b84b2cd` | **`PASS_TARGETED_QWEN_TECHNICAL_ONLY_NO_SCIENCE`** |

- V3 RESULT: https://drive.google.com/file/d/1Mn4LmHzbgrBibB0UZIPh8TZNVGz9sTJQ/view
- V3 CLAIM: https://drive.google.com/file/d/1YUa_c7Dsk8zUOFDYeIog58YiUcpHAGam/view
- Qwen RESULT: https://drive.google.com/file/d/1wQv0UsdREqUHOLx8MRlZFswtUPM5qQw5/view
- Qwen CLAIM: https://drive.google.com/file/d/1OApb1Bb-liTJw_hGQb5L_G9B0hZfoKRI/view

**Quan hệ bằng chứng:** `qwen_followup.parent_run_id` bằng chính xác V3 `run_id`; `parent_result_sha256` bằng SHA-256 của file V3 RESULT; từng CLAIM trước RESULT tương ứng; không trùng RUN_ID; Qwen không đổi trạng thái FAIL của V3. Nguyên nhân FAIL V3 ở `qwen_tokenizer_ids` đã được chẩn đoán là kiểm tokenization/giới hạn ID không hợp với Transformers 5 và token điều khiển chat; bản mã Qwen successor có Git blob `cfd1d0558d3d61dbf1a343342bb961f8d7b17ee1` (notebook) và `a42f2d696056269e557461e45bbf29f57beaaa5b` (Python).

## 2. Kết quả kỹ thuật đo thật từ hai receipt

| Bước | V3 gốc | Qwen bổ sung | Kết luận |
|---|---|---|---|
| Colab `Tesla T4` | PASS | `Tesla T4` | PASS trong phạm vi ghi nhận |
| Thư viện ST6.1.0 và import `Normalize` | PASS | Không cần lặp | PASS |
| Kế hoạch dung lượng tải và đĩa trước chạy | PASS | Không chạy lại phần tải toàn bộ | PASS **tiền kiểm trước tải**, không phải tổng lưu trữ sau chạy |
| File SQuAD validation SHA256 nguồn | PASS exact `8c6646d36bd5a95061e076788cf3161d11f6f3e7d625dac7a83bbed0a49f69f7` | Không dùng SQuAD | PASS |
| SQuAD corpus manifest | 10.570 QA; 2.067 passage; 48 article; 144 query | Không dùng SQuAD | PASS theo thuật toán thực thi V3 |
| SHA256 tệp snapshot model | PASS **tính SHA256 cục bộ**, không phải đối chứng byte độc lập với máy chủ | Đối chiếu Qwen cache với manifest V3 trước CLAIM | PASS đúng phạm vi |
| EmbeddingGemma 2, text-only FP32 | PASS: `[2,768]`, mọi giá trị hữu hạn, norm `[1.0,1.0]` | Không chạy lại | PASS |
| Tokenization của Qwen v5 | FAIL do giả định API/token ID | PASS pre-CLAIM: 44 prefix IDs, 1 answer token | PASS **sau bản sửa** |
| Frozen Qwen answer-only teacher-forced NLL | Không đến được bước này | PASS: 1/1 scored label, NLL `5.584118843078613`, finite | PASS trong phạm vi **synthetic technical** |
| R_gold, R1/R2/R3, TEST, training | `false` | `false` | **NOT_EXECUTED** |

- V3 source receipt `elapsed_seconds=63.144`, EmbeddingGemma FP32 `peak_allocated_bytes=1097034752` (khoảng 1.02 GiB); Qwen follow-up `elapsed_seconds=26.923`, peak `max_gpu_allocated_bytes=1074050048` (khoảng 1.00 GiB). Không cộng các số peak của hai phiên để nhận định tổng tải; các phép đo không chứng minh peak khi chạy cả hai mô hình cùng lúc.
- `qwen.synthetic_answer_only_nll=5.584...` **không** là chất lượng mô hình hay bài đo R_gold. Nó chỉ chứng minh finite loss và mask/shift tính đúng **1** token mục tiêu trong bài giả lập.
- V3 `downloaded_file_manifests` cung cấp local SHA cho pinned versions: `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`; `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`. Không kết luận đã xác minh độc lập remote SHA của trọng số.

## 3. Independent QA and exact decision scope

**QA thực thi bằng chương trình (offline): `20/20 PASS`**. 20 kiểm tra bao gồm exact SHA original V3/CLAIM, V3 FAIL unchanged, source model pins, SQuAD source digest và manifest counts, FP32 finite shape, Qwen parent pointer/hash, Qwen PASS/status/mask target count/loss, GPU/version, cờ no-science/no-download, thứ tự timestamps và định danh duy nhất. Bộ QA cũng kiểm tra mã V3 nguyên bản: `final_storage_limit` và `time_budget` là hai phép kiểm **nằm sau điểm lỗi Qwen**, nên **chưa được ghi PASS** trong V3 RESULT. Không được trình bày chúng như đã thực thi.

**Một quyết định:** `TECHNICAL_CORE=PASS_SCOPED`, `FULL_END_TO_END_TECHNICAL_PREFLIGHT=NOT_ESTABLISHED` chỉ vì hai hậu kiểm nguồn gốc chưa chạy. Đây **không phải yêu cầu lặp lại V3 hoặc chạy thêm một phiên technical one-shot**; bằng chứng các phép kiểm thiết yếu về nguồn, FP32 và Qwen hiện đủ để xem xét bước khoa học tiếp theo. Hai giới hạn tài nguyên còn thiếu phải được kiểm trực tiếp **trước claim khoa học, trong cùng một lượt quyết định khoa học khi được chủ dự án cho phép**, và fail-closed nếu không đủ. Không mở thêm các micro-permit hoặc sửa tiêu chí khoa học.

**Biên bản QA JSON artifact trong cuộc trò chuyện:** `TTM_EmbeddingGemma2_D1_Combined_Technical_Receipt_QA_20261109.json`; SHA-256 `adad51da1d6ede67c1188373626e41bf5a228528e4f1d8a3be64fa7781a2b1a1`. Chỉ lưu metadata kiểm định và mã băm, không lưu dữ liệu corpus hay trọng số.

## 4. Science boundary and next integrated action

**Không sửa** `CLAIM/RESULT` V1, V3 và lượt Qwen; giữ mọi PASS/FAIL gốc. G1–G4 và `R_gold` đã khóa không thay đổi. `lineage.md` chỉ ghi kết quả khoa học nếu có chạy và phán quyết khoa học riêng; QA kỹ thuật này **không** append.

**Next:** `TTM_EMBEDDINGGEMMA2_D1_SINGLE_SCIENCE_ADMISSION_AND_R_GOLD_FIRST` — thẩm định **một** quyết định khoa học về R_gold trước, đồng thời đo/giới hạn RAM/VRAM/Drive/time trong điều kiện runtime thực tế, kiểm không ảnh hưởng TTM-Small T5. Chỉ khi được cho phép mới chạy one-shot R_gold; nếu R_gold PASS theo chuẩn đã khóa thì mới xem xét R1/R2/R3 theo điều kiện tiền đăng ký; không dùng dữ liệu đánh giá để chỉnh ngưỡng. D1 chưa tự động mở chỉ vì technical PASS.

**Final exact states:** `V1=CONSUMED_FAIL_PRESERVED` · `V3=CONSUMED_FAIL_PRESERVED` · `QWEN_FOLLOWUP=PASS_PRESERVED` · `COMBINED_TECHNICAL_CORE=PASS_SCOPED` · `FINAL_STORAGE_AND_TIMELIMIT=UNMEASURED` · `D1_D4=NOT_AUTHORIZED` · `SCIENCE_NOT_EXECUTED` · `TTM_SMALL_T5=PRIORITY_FIRST`.
