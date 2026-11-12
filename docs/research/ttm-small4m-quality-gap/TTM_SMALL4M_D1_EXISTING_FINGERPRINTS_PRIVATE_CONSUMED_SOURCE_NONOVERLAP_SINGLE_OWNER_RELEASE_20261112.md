# TTM-Small-4M D1 — Bổ sung fingerprint dữ liệu đã tiêu thụ và phân xử chủ dự án một lượt

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_EXISTING_FINGERPRINTS_PRIVATE_CONSUMED_SOURCE_NONOVERLAP_ONE_OWNER_RELEASE_READBACK`  
**Phương thức:** `READ_ONLY · EXISTING_EVIDENCE · NO_TEST_Q1Q2_REOPEN · NO_INFERENCE · NO_TRAINING`  
**Phán quyết duy nhất:** **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`**.

## 1. Các neo nguồn giữ nguyên

Gói DEV V2 thô SHA-256 `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8`, SHA-256 chuẩn hóa LF `1553d186eb55699506b6b920153d5c7af7f0ad26a186e1d58ffef0d1e7b4eb2e`, mẫu chấm mù SHA-256 `ae85dddbb12b299f2f9252ad3b1df426eb7bd0af6ae52fbb73b5825c646833d4`. Không thay 16 gia đình, 128 prompt, 64 prior, 512 vị trí chấm mù, seed hoặc rubric. Kết luận kỹ thuật `V2_REKEY=PASS_SCOPED`, `POSTFLIGHT=PASS_SCOPED` không thay đổi.

## 2. Fingerprint/provenance nguồn trước đó

| Tập nguồn | Chứng cứ hiện có | Đối chiếu với D1 |
| --- | --- | --- |
| FRESH12, 24 cặp chấm mù | Packet SHA-256 `85fec5d290d6639809ca6ba437982fa8bb11cd5e7e0fbcf412d40f7bc9c3a037` từ readback receipt `_tmp/fresh12_review_20261110/TTM_FRESH12_GITHUB_READBACK_RECEIPT.md` | Khóa toàn gói; không đủ đối chiếu từng prompt |
| FRESH16 V2 S1 đã tiêu thụ | Packet SHA-256 `2dc1fd7cda1262168cbdca4ca0773327e4153642c39a9981f3462dddad9aaccb`; biên nhận offline ghi 16 SHA token của 16 prompt | Đối chiếu từ vựng trước đó 16×16=256, không trùng nguyên văn hoặc 5-gram; mức lớn nhất 0,133 |
| CF1 DEV36 đã tiêu thụ | Input SHA-256 `81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed`, Git blob nguồn `4fac79c16bc337926060fa21a6e22944d74259b7`; source trên nhánh `evidence/ttm-cf1-step1024-dev36-once-20261111` | Đã kiểm tra ngay trên nguồn DEV (không phải TEST), số liệu bên dưới |
| AC FINAL24 đã tiêu thụ | Public prompt source Git blob `f08f15c5049baf77771bed463a5119136566373b`; gồm 12 DEV + 24 FINAL, tất cả có SHA-256 từng prompt; blind packet freeze Git blob `e66c5793483d7d4f45706268a053843f613e9af3` | Đã kiểm tra 24 FINAL công khai ngay trong lượt này, số liệu bên dưới |
| Q1 + FRESH12 public | 28 prompt công khai cho phép; nguồn Git blob `6b35ec8ae377a9dbdb778766756a32e8ad4bcbc8` | Sàng lọc có giới hạn đã thực hiện |
| Candidate FRESH16 chưa dùng | 16 prompt thiết kế chưa thực thi, blob `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f` | Không dùng làm bằng chứng cho tập đã tiêu thụ |
| TEST/Q1Q2 niêm phong | Không mở lại, không băm lại, không truy xuất bản ghi riêng tư | **Chưa có index fingerprint đủ điều kiện đối chiếu toàn bộ D1** |

Hash của toàn packet hoặc SHA của tệp điểm **chỉ chứng minh danh tính byte của toàn gói**, không chứng minh các prompt riêng lẻ khác nhau. Fingerprint token cũng không trực tiếp so được với hash UTF-8 nếu hai bên không có định nghĩa chuẩn hóa/encoding và dữ liệu đầu vào cùng kiểu. Không công khai per-prompt hash mới của nguồn private đã niêm phong.

## 3. Đối chiếu từ vựng mới

Hai kiểm tra dưới đây so 16 **family core D1** (scene + fact A/B + continuation A/B), **không** phải toàn bộ 128 prompt D1, với nguồn đã có; không đọc seed, mapping hoặc điểm số.

| Đối chiếu | Lượt cặp | Trùng toàn chuỗi | Chung 5 từ liền nhau | Jaccard từ vựng tối đa |
| --- | ---: | ---: | ---: | ---: |
| D1 × 72 ngữ cảnh (36 cặp) CF1 DEV | **1.152** | 0 | 0 | **0,088** |
| D1 × 24 prompt FINAL của AC | **384** | 0 | 0 | **0,095** |

Đối chiếu đã hoàn tất trước đó: D1 × FRESH16 S1 = 256 cặp; 0 chuỗi nguyên văn và 0 chuỗi 5 từ chung, Jaccard tối đa 0,133. Phạm vi nguồn công khai Q1/FRESH12 và candidate chưa dùng cũng đã được sàng lọc riêng.

Phương pháp Jaccard trên tập từ tiếng Anh được loại stopword; ngưỡng rà soát `0.18` là **exploratory/posthoc**, không phải quyết định PASS/FAIL theo prereg. Kết quả này hữu ích để loại trừ trùng lặp hiển nhiên, **không** xác nhận không trùng ngữ nghĩa theo kịch bản, vai trò và mục tiêu.

## 4. Ba cổng còn lại

**Không trùng dữ liệu (non-overlap).** Có thêm bằng chứng trực tiếp cho nguồn đã tiêu thụ FRESH16/CF1/AC FINAL24. Nhưng so sánh mới chỉ ở family-core, FRESH12 riêng tư chưa có đối chiếu độc lập đủ độ bao phủ; thiếu fingerprint/certification có thể so được đối với TEST/Q1Q2 đã niêm phong. **`FULL_NONOVERLAP=HOLD`**, không được đổi thành PASS nhờ hash toàn gói.

**Quyền và xuất xứ (rights/provenance).** Metadata V2 ghi `AI_AUTHORED_ORIGINAL_TEST_MATERIAL_NOT_EXTRACTED_FROM_CORPUS`, đồng thời `AI_AUTHORED_NEW_CONTENT_OWNER_FINAL_ATTESTATION_PENDING`. Phạm vi tạo mới cho dự án đạt `ORIGIN=PASS_SCOPED`, nhưng chưa đủ làm bằng chứng về mọi quyền dùng cho thực nghiệm. Không yêu cầu ký hình thức; mọi xác nhận chỉ cần receipt nêu rõ nguồn và mục đích thực tế.

**Chấm mù độc lập (rater isolation).** Handoff đã được tiếp nhận với `RATER_PREEXEC_READY_SCOPED`. Phiên chấm 512 output thực phải tách khỏi ngữ cảnh thiết kế/người giữ seed, mapping. Hiện chưa sinh đầu ra, phiên chấm cuối chưa chạy; `RATER=STAGED_NOT_EXECUTED`. Không bắt agent ký hoặc chạy lại bước tiếp nhận.

## 5. Phán quyết owner cuối

**`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`** cho 512 rollouts và 384 candidate scores của D1. Trạng thái `SCIENCE=NOT_EXECUTED` không thay đổi. Không chạy lại FRESH16, không TEST/Q1Q2, không train, không inference, không rekey, không merge main hoặc append lineage.

Cổng remote đã quan sát `new_job_admission_allowed=false` / `RESEARCH_ADAPTER_DISABLED`; không cố gửi job hay đi đường vòng.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_EXISTING_SEALED_FINGERPRINT_INDEX_OR_UNCERTIFIABLE_COVERAGE_OWNER_CLOSEOUT`. Chỉ đối chiếu **index/biên nhận được khóa từ trước** (nếu hiện hữu) hoặc ghi rõ `UNAVAILABLE` cho phần không thể chứng nhận mà vẫn bảo toàn niêm phong. Cùng một owner closeout quyết định duy trì HOLD hay có đủ chứng cứ cấp GO, **không tạo micro-permit, không tự sửa quy tắc khoa học**.
