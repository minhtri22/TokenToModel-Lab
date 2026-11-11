# TTM — Phân xử độc lập thí nghiệm CPU Vector Memory External Facts (DEV)

**Operation:** `TTM_VM_EXTERNAL_FACTS_CPU_ONE_SHOT_RESULT_INDEPENDENT_QA_AND_SCIENTIFIC_ADJUDICATION`  
**Run ID:** `TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1`  
**Nguồn khoa học khóa trước thí nghiệm:** Git commit `c41b6c8bc01a4c367bf619a6df6e05e5e2fb9d47`, runner blob `13701b8768c463d845762c690768abae2040eba2`.  
**Phán quyết:** **`PASS_DEV_SCREEN_GO_CANDIDATE_SCOPED`**, *không phải PASS TEST và không cấp quyền mở TEST*.  
**Trạng thái:** huấn luyện CPU một lần hoàn tất theo receipt; không tái chạy; `main` và P00–P12 không thay đổi.

## 1. Cách tiếp nhận bằng chứng

Đọc trực tiếp hai tệp text từ máy Windows chủ dự án:

- `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1\ONE_SHOT_STARTED.json`: run ID trùng hợp đồng, `steps_planned=128`, `test_opened=false`.
- Cùng thư mục, `DEV_AGGREGATE_PUBLIC.json`: báo `status=DEV_SCREEN_GO_CANDIDATE`, 128 bước, TRAIN=256, DEV=64, TEST chưa mở, frozen checkpoint không đổi, 110.689 tham số Reader học, 200 token đáp án trong mỗi đối chứng.
- `reader_private.pt`: sự tồn tại được kiểm tra qua liệt kê thư mục; **không nạp/không công bố** trọng số riêng tư.
- SHA-256 của `DEV_AGGREGATE_PUBLIC.json` được chủ máy báo `26bec01154d5925b5c290f628a6497783e1422f5d8fc7a4911e85f475a913299`. Tính từ văn bản connector sau khôi phục CRLF Windows và dấu xuống dòng cuối cho cùng SHA. **Đây là xác minh từ readback text có tái dựng CRLF, không phải truy cập byte gốc qua một kênh đọc binary độc lập.**

## 2. Kết quả khoa học trên DEV 64 truyện

| Đối chứng | NLL trung bình trên truyện (nats/answer token) |
|---|---:|
| A — No Memory, cùng Reader bypass | **6.947507053613663** |
| B — Correct Memory, cùng Reader đã học | **3.8169478699564934** |
| C — Wrong Memory, chỉ đổi value của thực thể mục tiêu | **5.298715498298407** |

Hai hiệu số đã khai báo trước thực thi:

| Chênh lệch | Trung bình ghép cặp báo cáo | Bootstrap 95% được báo cáo |
|---|---:|---|
| `A−B` | **+3.1305591836571693** | **[2.8624527269043027, 3.4449861110188067]** |
| `C−B` | **+1.4817676283419132** | **[0.7690657899715007, 2.3000695523805907]** |

Cả hai mức tăng đạt ngưỡng tối thiểu `0.05`; cận dưới hai CI báo cáo đều lớn hơn 0. Kết luận khoa học **PASS theo sàng lọc DEV đã tiền đăng ký**, không thay ngưỡng hoặc thêm seed/epoch.

Memory sai có NLL thấp hơn không memory, nhưng **cao hơn memory đúng**: điều này không phủ định hiệu ứng thông tin của value đúng; đồng thời cho thấy Reader có thể cải thiện một phần thống kê xác suất không cần value chính xác. Không được diễn giải độ chênh như mức tăng chất lượng sinh văn bản nói chung.

## 3. Chất lượng kiểm định và giới hạn

Đối chiếu độc lập bằng chứng aggregate: **17/17 PASS** gồm nhận diện RunID, kích thước mẫu, budget, nguồn, checkpoint, TEST flag, nhất quán phép trừ, ngưỡng và đối chiếu SHA dạng text CRLF. Artifact: `artifacts/research/vector-memory/TTM_VM_EXTERNAL_FACTS_CPU_ONE_SHOT_INDEPENDENT_AGGREGATE_QA_20261111.json`.

**Giới hạn bắt buộc:** runner chỉ lưu aggregate, loại bỏ vector NLL theo từng truyện sau bootstrap. Người phân xử **không tự dựng lại được bootstrap CI từ 64 cặp per-story**; CI là số báo cáo bởi runner đã khóa, không phải CI do checker thứ hai tính lại. Không có chứng minh đọc và so sánh tensor của `reader_private.pt` bởi checker. 128 bước được xác nhận bởi metadata runner + loop nguồn khóa, chưa có log đầy đủ từng optimizer step độc lập.

**Phạm vi khoa học:** toy external facts với nhãn tưởng tượng và **Oracle tra đúng một key được ghi trực tiếp trong câu hỏi**; Query/Key projections không học xếp hạng trong Oracle mode. Đây là bằng chứng Reader học dùng thông tin từ value ngoại sinh để giảm NLL trên DEV chưa dùng cho huấn luyện; **không** chứng minh truy xuất ngữ nghĩa, Retriever Top-k, RAG tổng quát, tri thức thế giới, suy luận nhiều bước, hoặc tăng hiệu quả của mô hình trên TinyStories VAL đã khảo sát. Không được tuyên bố `TEST=PASS`, không được mở TEST chỉ vì DEV PASS.

## 4. Quyết định

- **Scientific DEV screening:** `PASS_DEV_SCREEN_GO_CANDIDATE_SCOPED`.
- **Source/result aggregate QA:** `PASS_INDEPENDENT_AGGREGATE_CONSISTENCY_17_OF_17`.
- **CPU one-shot:** `CONSUMED`. Cấm tự chạy lại, kể cả để hoàn thiện bootstrap audit.
- **TEST:** `SEALED_NOT_OPENED`; **không có release**. **GPU:** `NO`.
- **Next scientific question:** Retriever Top-k có thực sự tìm đúng bản ghi khi bỏ Oracle hay không, và giá trị đúng còn cải thiện NLL dưới cùng ngân sách thông tin? Phải thiết kế kiểm tra chỉ trên tập không phải TEST, không tái train Reader, không chấm lại DEV cũ theo nhiều cấu hình.
- **Lineage:** append `L0020` ghi kết quả khoa học dương tính có giới hạn, giữ L0015–L0019 và các kết quả âm tính nguyên trạng. `main` không merge.

**Bước thực hiện tiếp theo:** `TTM_VM_EXTERNAL_FACTS_RETRIEVED_TOPK_NONTEST_READINESS_AND_FROZEN_READER_GENERALIZATION_DESIGN` — chỉ thiết kế đối chứng Retriever Top-k/Oracle với Reader đã khóa, không chấm DEV lặp lại, không tự mở TEST, chưa cấp phép GPU.
