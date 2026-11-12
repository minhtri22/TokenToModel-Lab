# TTM-Small-4M — DEV32 / BLIND64: nhận điểm GPT-6, khóa SHA, đối chiếu ID, phân xử exploratory phía owner

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_EXP32_OWNER_INPUT_PROVENANCE_VERIFICATION_AND_SCOPED_POST_SCORE_UNBLIND`  
**Phạm vi:** `EXPLORATORY_SCOPED_AI_REVIEW` (người chấm GPT-6 tự khai độc lập, **không phải reviewer khoa học con người**).  
**Kết luận:** `PROVISIONAL_SCOPED_AI_RATER_ADJUDICATION_WITH_ORIGINAL_RATER_INPUT_BYTE_GAP`.

## 1. Khôi phục được tệp điểm thật, không cần tải lại

Hai tệp JSON sinh ra trong phiên chấm độc lập đã được tìm thấy trong **ChatGPT Library** rồi khôi phục byte gốc, tính lại SHA-256. Không dùng bản tóm tắt 64 điểm làm nguồn hash.

| Tài sản | Kích thước | SHA-256 tính lại |
|---|---:|---|
| `D1_EXP32_RATER_BLIND64_SCORES.json` | 19.774 byte | `d6ef3780ca72ffe5fcc7a67bcfe85abf3a87b92b4fee30bcf9b88460734885d4` |
| `D1_EXP32_RATER_BLIND64_SCORE_FREEZE_RECEIPT.json` | 1.269 byte | `97720785d460bb919be063be117f70f66fc68ebdf8cdb33abc79e368c97f8795` |

Hash tệp điểm đúng với biên nhận freeze. Schema scores hợp lệ, 64/64 ID duy nhất, có đầy đủ trường rubric, không có điểm null. Phân phối: **39 điểm 0**, **25 điểm 1**, **0 điểm 2**, **0 điểm 3**.

Biên nhận của rater ghi `input_sha256=null`, `INPUT_HASH_NOT_VERIFIED` bởi rater chỉ chấm văn bản **dán trong hội thoại**, không có byte gốc từ tệp BLIND64. Không tự điền/ghi đè trạng thái này. SHA BLIND64 do **owner generator** khóa là `4288c311f22147a85a414fd436fbeba1287464bb60d745ca64e5ce07839158f1`.

## 2. Đối chiếu danh tính và giải mù sau khóa điểm

Runner Git blob `4f7dddd52833362a52068527a3db78c2b0845578` có công thức định danh `sha256(D1_SHA256 + ':' + str(sequence_index) + ':EXP32')[:20]`, chạy sequence 0–63 theo thứ tự 32 prompt × (GREEDY, NUCLEUS). D1 V2 SHA-256 `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8`.

Đã tái tính độc lập đủ **64 opaque_id** từ công thức đã khóa và so với 64 ID của tệp điểm gốc: **64/64 khớp, 0 thiếu, 0 ID lạ**. Chỉ sau khi hash tệp điểm được xác minh mới sử dụng chỉ số thứ tự để nối nhãn greedy/nucleus phía owner. Không đọc mapping hay seed private từ gói owner; không sửa điểm.

**Giới hạn nguồn còn lại:** match 64 ID không phải chứng nhận **nội dung đầy đủ** `prompt_text` / `generated_text_only` mà rater thấy trong chat giống từng byte của BLIND64 nguyên bản. Không có bản snapshot nguyên văn 64 input đã dán cùng hash độc lập. Kết luận có nhãn **provisional**. Đây là thiếu sót nguồn của rater, **không phủ định** thực tế nó đã chấm 64/64 và kết quả vẫn hữu ích với tính chất exploratory.

## 3. Phân phối điểm sau nối nhãn

| Kết quả | GREEDY | NUCLEUS (top-p 0.9, T 0.8, 1 seed đã khóa) |
|---|---:|---:|
| Văn bản được chấm | 32 | 32 |
| Điểm 0 (không có hành động phù hợp để chấm) | 30 | 9 |
| Điểm 1 (có hành động nhưng không theo dữ kiện) | 2 | 23 |
| Điểm 2 | 0 | 0 |
| Điểm 3 | 0 | 0 |
| Trung bình điểm 0–3 | 0,0625 | 0,71875 |
| **Đạt ngưỡng tuân thủ ≥2** | **0/32** | **0/32** |
| Family pair-success (A và B cùng đạt ≥2) | **0/16** | **0/16** |

Trong 32 **cặp cùng prompt**: nucleus có điểm cao hơn greedy 22 lần; greedy cao hơn 1 lần; hòa 9 lần. Đây là thay đổi từ 0 sang 1 theo rubric chấm AI, **không** tạo ra một bản sinh nào đạt ngưỡng đúng dữ kiện.

Phân bố điểm 1 theo category (mỗi category gồm 8 bản/phương pháp):

| Category | GREEDY điểm 1 | NUCLEUS điểm 1 |
|---|---:|---:|
| `entity_location` | 0/8 | 7/8 |
| `causal_reasoning` | 2/8 | 6/8 |
| `rule_constraint` | 0/8 | 6/8 |
| `goal_persistence` | 0/8 | 4/8 |

## 4. Liên kết với kết quả chủ sở hữu đã có trước chấm mù

Teacher-forced trên đúng 16 family short/near: `S=1/16`, `S_adjusted=2/16`; đều dưới ngưỡng tín hiệu yếu khám phá `≤4/16`. Bộ sinh của owner trước chấm mù ghi 213 vs 8 cửa sổ trùng 3-token cho greedy/nucleus, 14 vs 0 EOS sớm; đây là số đếm mô tả không chuẩn hóa.

**Diễn giải hợp lệ:** nucleus giúp đầu ra thường có một hành động/diễn tiến hơn thay vì chỉ lặp/nhiễu, nhưng **không cứu được tuân thủ dữ kiện** trong DEV32 theo người chấm AI. Thiếu độ nhạy lựa chọn dữ kiện là vấn đề rõ rệt ngay ở teacher-forced; không thể quy toàn bộ thất bại cho greedy decoding. **Không** khẳng định khác biệt 22–1 có ý nghĩa thống kê độc lập vì chỉ một seed nucleus và 16 gia đình, cùng provenance rater input chưa được chứng nhận toàn văn.

## 5. Owner scoped adjudication, không mở thêm micro-gate

`SCORE_FILE_SHA256=VERIFIED`  
`SCORE_RECORDS=64_OF_64_VALID`  
`RATER_SCORE_FREEZE=VERIFIED`  
`OPAQUE_ID_SOURCE_MATCH=PASS_64_OF_64`  
`ORIGINAL_RATER_PASTED_INPUT_BYTES=NOT_VERIFIED`  
`OWNER_DECODER_UNBLIND=EXECUTED_AFTER_SCORE_SHA_FREEZE`  
`RATER_AI_REVIEW_RESULT=PROVISIONAL_EXPLORATORY_WEAK_FACT_ADHERENCE`  
`DECODER_RESCUE_FACT=NOT_SUPPORTED`  
`D1_CONFIRMATORY_512=HOLD`  
`TEST_Q1Q2=SEALED` · `TRAINING=NO` · `NEW_INFERENCE=NO` · `LINEAGE=UNCHANGED`.

**Bước thực hiện tiếp theo:** không chấm lại, không tạo seed khác hay chạy thêm DEV32 để tìm kết quả đẹp. Đóng **báo cáo exploratory** với cảnh báo input-paste provenance; nếu bắt đầu nghiên cứu mới, ưu tiên thử giả thuyết cải thiện **học điều kiện hóa dữ kiện qua training objective/data/capacity**, không tập trung chỉnh greedy/nucleus. Thiết kế nghiên cứu mới phải ghi rõ phạm vi riêng và không được nâng các điểm này thành kết quả confirmatory.

**Biên nhận máy công khai an toàn (không lộ record/seed/mapping):** `artifacts/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_EXP32_BLIND64_RECOVERED_SCORE_SHA_ID_MATCH_OWNER_PROVISIONAL_ADJUDICATION_20261112.json`.
