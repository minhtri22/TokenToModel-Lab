# TTM-Small-4M D1 — Kết thúc tra cứu fingerprint nguồn niêm phong (terminal owner closeout)

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_EXISTING_SEALED_FINGERPRINT_INDEX_OR_UNCERTIFIABLE_COVERAGE_OWNER_CLOSEOUT`  
**Phương thức:** `READ_ONLY · EXISTING_INDEX_AND_RECEIPT_ONLY · NO_SEALED_SOURCE_READ · NO_SCIENCE`  
**Phán quyết duy nhất:** **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`**  
**Đóng công việc kiểm tra trước thực thi:** `CLOSED_PREEXEC_UNCERTIFIABLE_WITHOUT_SEALED_ACCESS`.

## 1. Khóa dữ liệu D1 không thay đổi

DEV V2 raw SHA-256 `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8`; normalized LF SHA-256 `1553d186eb55699506b6b920153d5c7af7f0ad26a186e1d58ffef0d1e7b4eb2e`; blind rater template raw SHA-256 `ae85dddbb12b299f2f9252ad3b1df426eb7bd0af6ae52fbb73b5825c646833d4`. Hợp đồng D1, 16 family, 128 DEV prompt, 64 neutral prior, 512 vị trí blind, checkpoint/BPE, seed private và rubric đều giữ nguyên.

## 2. Danh mục chỉ mục đã tra cứu

Chỉ đọc danh mục đường dẫn và **metadata biên nhận có sẵn**. Không mở prompt TEST/Q1Q2, raw outputs, mapping, seed hay score để tạo chỉ mục mới.

| Nhóm nguồn | Bằng chứng đã tồn tại | Có đủ index so sánh với D1? |
| --- | --- | --- |
| Q1/Q2 | `PUBLISHED_FILES_SHA256.json` V1/V2 trên nhánh `research/ttm-small4m-q1q2-quality-single-batch-20261109`; blob `fabf5656d28c341e43f0cfe00b9989e6cf97e2eb`, `4933ea77dfe099930e1db3bf04dab1ada67cb355` | **Không**. Đó là hash các tệp RESULT/CLAIM/raw generation đã công bố, không phải index prompt niêm phong cùng chuẩn |
| FRESH12 | `TTM_FRESH12_EXECUTOR_PACKET_QA_20261110.json`, blob `02680ca1393a3e96633442259cae8883a9dfdcb8`; `TTM_FRESH12_AUTHOR_SIDE_SEPARATE_AUDIT_20261110.json`, blob `cd4576473dba4037f4a0dad83427e27d52dccab` | **Không đầy đủ**. Hash raw source, gói chấm và mapping, nhưng chưa đủ index D1↔từng prompt |
| FRESH16 | Biên nhận `_tmp/ttm_fresh16_integrated_offline_review_20261111/INTEGRATED_OFFLINE_REVIEW_RECEIPT.json` có 16 fingerprint token từng prompt | **Một phần**. Đã có lexical screen 16×16; thiếu chứng nhận ngữ nghĩa và index D1 cùng cách tuần tự hóa |
| CF1 DEV36 | Biên nhận trên nhánh `evidence/ttm-cf1-step1024-dev36-once-20261111` có toàn bộ input SHA-256 `81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed` | **Một phần**. Trước đó đã sàng lọc 1.152 lượt CF1×D1, nhưng hash packet không phải index cấp prompt |
| AC FINAL24 | Nguồn prompt public đã khóa Git blob `f08f15c5049baf77771bed463a5119136566373b`; 24 hash UTF-8 cấp prompt | **Một phần**. Đã sàng lọc 384 lượt AC×D1; không chứng nhận toàn bộ 128 prompt D1 theo cùng định dạng canonical |
| T4 private train/val | `_tmp/ttm_t4_data_pack_v1/T4_PRIVATE_PACK_MANIFEST.json` ghi `contains_test=false`; NPZ SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; QA ghi manifest SHA `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650` | **Không**. Hash TRAIN/VAL không thay thế index TEST |
| TEST/Q1Q2 protected | Đã rà danh sách tệp/biên nhận theo phạm vi dự án, không mở nội dung niêm phong | **Không tìm được index frozen đủ cùng kiểu và phủ nguồn**, ghi `UNVERIFIABLE_WITHOUT_SEALED_ACCESS` |

Chứng cứ từ lượt trước: D1 so FRESH16 256 cặp, CF1 1.152 cặp và AC FINAL24 384 cặp đều `PASS_SCOPED_LEXICAL_SCREEN`. **Không nâng những kiểm tra này thành chứng nhận trùng/khác nghĩa**. Kiểm tra mới không thực thi lại các phép so trên và không sinh dữ liệu khoa học.

**Giới hạn của kết luận tìm kiếm:** đây là tìm kiếm có phạm vi trong các nhánh/tệp biên nhận được biết, danh mục thư mục evidence và metadata trên Windows. `NOT_IDENTIFIED_IN_SCOPED_INVENTORY` **không có nghĩa** chứng minh chỉ mục không tồn tại ở bất kỳ nơi nào. Nhưng từ chứng cứ được phép đọc hiện tại, không thể phát hành giấy chứng nhận non-overlap bắt buộc.

## 3. Quyết định owner duy nhất

`V2_REKEY=PASS_SCOPED` · `POSTFLIGHT=PASS_SCOPED` · `FRESH16_CF1_AC_LEXICAL=PASS_SCOPED` · **`FULL_NONOVERLAP=UNVERIFIABLE_WITHOUT_SEALED_ACCESS`** · `RIGHTS_ORIGIN=PASS_SCOPED` · `RATER=PREEXEC_READY_SCOPED_FINAL_SESSION_STAGED`.

**`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`** cho 512 outputs và 384 candidate scores. Đây là HOLD do không đủ bằng chứng, **không phải kết quả âm tính của mô hình**.

`SCIENTIFIC_TRAINING=NO`, `INFERENCE=NO`, `TEST_Q1Q2=SEALED`, `FRESH16_RERUN=NO`, `NEW_SEEDS=NO`, `BLIND_MAPPING_LEAK=NO`, `MAIN=UNCHANGED`, `LINEAGE=UNCHANGED`.

## 4. Closeout và bước tiếp theo

**Dừng tại đây các vòng tra cứu nguồn D1 tiền thực thi**: `CLOSED_PREEXEC_UNCERTIFIABLE_WITHOUT_SEALED_ACCESS`. Không đề nghị một micro-permit hoặc một vòng kiểm tra fingerprint mới khi không có bằng chứng thực chất. Không mở niêm phong, không tự hạ tiêu chuẩn hợp đồng.

**Bước thực hiện tiếp theo (điều kiện duy nhất để mở lại):** chỉ tiếp nhận **chỉ mục fingerprint/certification canonical đã tồn tại nhưng chưa được cung cấp**, đủ bao phủ các nguồn còn thiếu, hoặc một quyết định nghiên cứu mới được tiền đăng ký riêng. Nếu không có chứng cứ mới, giữ nguyên D1 HOLD và dành nguồn lực cho hướng nghiên cứu đã đủ điều kiện thực nghiệm, không tự sinh 512 đầu ra D1.

**Biên nhận máy:** `artifacts/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXISTING_SEALED_FINGERPRINT_INDEX_UNCERTIFIABLE_OWNER_CLOSEOUT_20261112.json`.
