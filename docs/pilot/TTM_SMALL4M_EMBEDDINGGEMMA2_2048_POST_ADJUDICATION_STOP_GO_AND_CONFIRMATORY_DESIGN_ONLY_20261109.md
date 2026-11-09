# TTM-Small-4M × EmbeddingGemma 2 — Quyết định STOP/GO và thiết kế đánh giá xác nhận sau 2.048 bước

**Ngày:** 09/11/2026. **Mã công việc:** TTM_SMALL4M_EMBEDDINGGEMMA2_2048_POST_ADJUDICATION_STOP_GO_AND_CONFIRMATORY_DESIGN_ONLY.

**Mốc nguồn GitHub đã đọc lại:** 1f85fce1ac5cdc95caa3690b72ee2bc2b3df77fa; nhánh research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109. **Phạm vi:** chỉ nghiên cứu thiết kế và phản biện; chưa chọn dữ liệu mới, chưa mở tập TEST, chưa chạy suy luận, chưa huấn luyện CPU/GPU, không thay đổi kết quả khoa học.

**Quyết định:** GO_BLIND_HOLDOUT_FIXED_CHECKPOINT_DESIGN_ONLY · STOP_NEW_DIRECT_SWAP_TRAINING · RESIDUAL_GATED_DEFERRED_DESIGN_ONLY · CONFIRMATORY_NOT_EXECUTED.

## 1. Kết quả khoa học làm cơ sở

L0015: tại 1.024 bước thích nghi, NLL trên VALIDATION A=3,3501216608; B=3,3132221934; C=3,3604018255; D=3,4754170725, nên lợi ích C so với A/B chưa thiết lập.

L0016: tại 2.048 bước, NLL trên cùng VALIDATION A=3,3132380124; B=3,3280589053; C=3,2703167312; D=3,3920957202. Chênh lệch A−C=+0,0429212812; B−C=+0,0577421741; D−C=+0,1217789891. Ba khoảng tin cậy 95% của đối chứng theo truyện đều có cận dưới dương. Đây là **PASS thăm dò trên VALIDATION cũ**, không phải bằng chứng xác nhận. L0016 chỉ kiểm toán độc lập checkpoint và số học theo truyện; **chưa tái suy luận độc lập từng token** ở bước 2.048.

Cấu hình A: mô hình gốc với bảng đầu vào/đầu ra chia sẻ trọng số (weight tying). B: mô hình bỏ chia sẻ trọng số (untied head). C: đầu vào từ token EmbeddingGemma 2 đã ánh xạ và phép chiếu ridge. D: đối chứng hoán vị phép gán token donor. C/D chứa bộ thích nghi khác A/B; cùng ngân sách bước và nhãn không đồng nghĩa cùng số phép toán dấu phẩy động (FLOPs) hoặc số tham số.

**Hai câu hỏi cần tách riêng:**
1. Với **bốn checkpoint đã cố định**, C có lặp lại ưu thế dự đoán trên một tập truyện mới, không tham gia lựa chọn mô hình không?
2. Liệu ưu thế, nếu có, thực sự do nội dung của embedding donor, có thể lặp lại qua seed huấn luyện khác, hay do cấu trúc/độ tự do tối ưu?

Thiết kế này chỉ hướng đến câu hỏi 1. Câu hỏi 2 chưa được cấp phép thực nghiệm.

## 2. Quyết định nguồn dữ liệu — điều kiện trước thực nghiệm

**Đề xuất nguồn:** chỉ tệp nguyên bản TinyStories-valid.txt thuộc roneneldan/TinyStories, revision chính xác f54c09fd23315a6f9c86f9dc80f725de7d8f9c64; SHA-256 raw đã ghim 94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4. Không tự đổi sang TinyStoriesV2, bản Parquet hay corpus khác. Tệp TRAIN raw được ghim SHA-256 c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f. T1 split cũ SHA-256 9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9. Nguồn này được chọn vì có thể so sánh cùng miền dữ liệu với checkpoint cố định, không vì kết quả NLL.

Bằng chứng T1 đã quét 21.990 truyện VALID và ghi nhận 6.601 trường hợp trùng nguyên bản với toàn bộ TRAIN; 2.048 TRAIN / 256 VAL / 64 TEST là tập pilot đã chọn. QA trùng gần đúng trước kia **chỉ xác thực các tập pilot đang hoạt động**, không bảo đảm mọi truyện VALID chưa dùng đều độc lập gần đúng với toàn bộ TRAIN. Đó là **điều kiện chưa hoàn tất** của nguồn mới.

**Quy tắc tạo tập mới, phải khóa trước khi chấm:**
- Giữ nguyên bộ phân tích ranh giới truyện (story parser), phép chuẩn hóa phục vụ đối chiếu, bộ tách token (tokenizer) chỉ học trên TRAIN và quy tắc tạo cửa sổ T1/T4. Không học lại BPE, không thay EOS hay context 256.
- Đầu tiên loại theo mã băm (hash) những truyện trùng với toàn bộ TRAIN nguồn hoặc nhóm 2.048 TRAIN pilot, 256 VALIDATION pilot và 64 TEST đã dùng. Chỉ cần danh sách ID/mã băm của TEST cũ, **không mở nội dung TEST cũ**.
- Kiểm tra trùng gần đúng (near-duplicate) với TRAIN và ba tập pilot bằng quy tắc 5-gram Jaccard ≥0,85 đã mô tả trong tài liệu T1. Bản kiểm định cần ghi rõ khả năng bỏ sót của bộ sinh ứng viên; nếu không bảo đảm đủ, không tuyên bố đã loại mọi trùng gần đúng.
- Từ nguồn hợp lệ còn lại, chọn **đúng 320 truyện** theo thứ tự tăng của SHA256 trên chuỗi miền cố định 'TTM_GEMMA2_2048_NEW_HOLDOUT_V1|' ghép mã băm byte nguyên bản của truyện. Không chọn theo độ dài, NLL, độ dễ hay kết quả mô hình. Không bốc lại seed sau khi nhìn thống kê đầu ra.
- Tiêu chí dữ liệu tối thiểu đề xuất: đủ 320 truyện phân biệt, ít nhất 50.000 nhãn mục tiêu hợp lệ theo bộ token hóa gốc, không có trùng nội bộ. Nếu không đạt, trạng thái HOLD_DATA_CAPACITY, **không tự bổ sung** thêm nhóm hay nới số lượng sau khi biết kết quả.
- Manifest mới riêng tư gồm thứ tự ID, mã băm nguồn, seed miền, quy tắc loại trùng, tổng nhãn, nguồn và quyền, SHA-256 kết quả; tạo và xác minh đọc lại **trước lần suy luận nào**. Công bố lên GitHub chỉ các dấu SHA-256 và thống kê đã khử nhạy cảm, không công bố raw text, mã token, per-story loss hoặc membership TEST cũ.
- Quyền: thẻ dữ liệu ghi giấy phép CDLA-Sharing-1.0; quyền sử dụng/tính toán có điều kiện và nghĩa vụ đặc biệt khi công bố dữ liệu. Cần kiểm tra rõ sử dụng nguồn, thông báo và quyền riêng tư cho tập mới trước khi niêm phong. **Chưa tuyên bố quyền nguồn mới đã PASS** chỉ nhờ thẻ nguồn. Tham khảo: https://huggingface.co/datasets/roneneldan/TinyStories và https://cdla.dev/sharing-1-0/.

**Trạng thái thực tại thời điểm thiết kế:** NEW_HOLDOUT=NOT_SELECTED · MEMBERSHIP_AUDIT=NOT_EXECUTED · DATA_RIGHTS_GATE=HOLD · DATA_SHA_SEAL=NOT_EXECUTED. Không mô tả tập này là đã được niêm phong.

## 3. Thiết kế phép thử xác nhận có chi phí GPU bằng không

**Các hiện vật bất biến bước 2.048, không huấn luyện mới:**

| Nhánh | SHA-256 checkpoint |
|---|---|
| A | ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081 |
| B | a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c |
| C | ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d |
| D | db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e |

- Tải bốn checkpoint đã có từ Drive vào thư mục riêng của dự án khi thực thi về sau, đối chiếu SHA-256 và dấu READY; nạp lần lượt trên CPU với khả năng đọc an toàn, không đụng trạng thái AdamW.
- Dùng chung tokenizer/cửa sổ/nhãn và bộ chấm tính hao hụt log-likelihood âm theo token (token-weighted negative log-likelihood, NLL); đặt chế độ đánh giá (eval mode), không cập nhật tham số, không lấy mẫu sinh, không chọn checkpoint trung gian.
- Trước khi dùng tập mới, kiểm tra bộ chấm độc lập bằng fixture tổng hợp hoặc các chuỗi TRAIN đã cho phép, so với bộ chấm tham chiếu; đặt ngưỡng sai số số học FP32 là tối đa 1e-5 NLL trên fixture cố định. Không dùng VALIDATION cũ để chỉnh mô hình hoặc chọn bộ chấm.
- Chấm đúng **một lượt cuối** cho bốn checkpoint trên chính 320 truyện đã khóa. Mỗi truyện lưu tổng NLL và số nhãn trong vùng riêng tư; tổng NLL theo nhãn trên toàn tập là chỉ số chính. Không xem kết quả từng nhánh rồi thay số truyện/bộ lọc.

**Đối chứng chính định trước:** A−C, B−C và D−C. Dấu dương nghĩa là C tốt hơn. Lấy mẫu bootstrap ghép cặp theo **truyện**, không theo token/cửa sổ, 2.000 lần, bộ sinh số giả ngẫu nhiên NumPy default_rng với seed 2026110901; tính phân vị 2,5% và 97,5% cho khoảng tin cậy hai phía 95%, theo tỷ số giữa tổng chênh loss và tổng nhãn của mẫu truyện được chọn lại.

**Tiêu chí PASS khoa học trên tập mới:** cận dưới 95% phải **> 0 đối với cả ba** A−C, B−C, D−C, cùng lúc dữ liệu/nguồn/đánh giá hợp lệ. Đây là phép kiểm hợp (intersection–union) của một tuyên bố gồm ba điều kiện; không được chỉ báo cáo đối chứng thuận lợi rồi đổi tiêu chí. Các khoảng riêng lẻ không tự động là khoảng đồng thời (simultaneous confidence intervals).

**Tiêu chí FAIL:** dữ liệu hợp lệ, bốn checkpoint và phép chấm hợp lệ nhưng ít nhất một cận dưới không >0. Ghi FAIL khoa học đúng phạm vi, không chạy lại trên nhóm khác hoặc nới ngân sách.

**HOLD/INVALID:** nguồn, quyền, trùng lặp, tiền kiểm đánh giá, SHA hoặc kiểm tra số học không hợp lệ; không gọi là FAIL mô hình. Nếu đã có CLAIM đánh giá một lần thì phải giữ biên bản lỗi, không âm thầm sửa và tái dùng cùng nhãn xác nhận.

**Những kết quả chỉ để mô tả:** NLL tuyệt đối từng nhánh; độ lợi có ý nghĩa thực tế chẳng hạn 0,02 nats/token; phân nhóm theo tần suất token hoặc tỷ lệ token đã map; chênh lệch TRAIN→holdout và token coverage. Không biến các phân tích thứ cấp này thành điều kiện PASS mới sau khi xem số liệu.

## 4. Cây quyết định sau phép thử — chưa cấp phép chạy

| Kết quả về sau | Quyết định | Giới hạn suy luận |
|---|---|---|
| Chưa tìm đủ dữ liệu hợp lệ | HOLD_NEW_HOLDOUT | Không chấm, không suy diễn mô hình |
| Ba đối chứng đều đạt | GO_REPLICATION_DESIGN_REVIEW | Tín hiệu trên truyện mới của **một bộ checkpoint/seed cố định**; chưa xác nhận nhân quả hoặc lặp huấn luyện |
| Có đối chứng không đạt | STOP_DIRECT_SWAP_SUPERIORITY_CLAIM | C không được xác nhận vượt mọi đối chứng trên tập mới; giữ L0016 là tín hiệu thăm dò |
| Đánh giá hoặc nguồn sai | INVALID_EVALUATION | Giữ dấu lỗi; điều chỉnh hợp đồng mới trước mọi thực nghiệm lại |

Nếu đạt: khi chủ dự án thật sự cần kết luận về cơ chế, mới cân nhắc lượt huấn luyện lặp với seed mới trên cùng thiết kế A/B/C/D và nguồn TRAIN khác biệt hoặc lịch độc lập, có đối chứng đủ để phân biệt donor với chi phí FLOPs/untie. **Không tự mở GPU**.

Nếu không đạt: không huấn luyện kéo dài direct-swap để cứu kết quả. Có thể trở lại **thiết kế** cổng dư (residual/gated), nhưng chỉ dưới giả thuyết riêng, bắt đầu bằng kiểm tra trạng thái cổng 0 cho logits bằng baseline B, đối chứng donor đúng vs hoán vị và một tập đánh giá phù hợp; không tự động triển khai.

## 5. Phản biện bắt buộc

1. **Khác truyện không đồng nghĩa khác miền:** dùng TinyStories-valid.txt chưa dùng giúp xác nhận ngoài nhóm VAL trước, nhưng vẫn là cùng họ nguồn và không chứng minh hiệu quả trong sản phẩm thực tế.
2. **Rò rỉ gần trùng:** T1 đã loại trùng exact với toàn bộ TRAIN, nhưng xác thực near-duplicate lịch sử chỉ trên tập pilot. Phải xử lý lỗ hổng này cho 320 truyện mới trước khi dán nhãn độc lập.
3. **Một seed và lựa chọn hậu nghiệm:** tín hiệu 2.048 được chọn vì đã thấy L0015. Tập mới có thể xác nhận chất lượng dự đoán của checkpoint đã chọn, không làm lịch sử quyết định trở thành một thử nghiệm huấn luyện đăng ký trước.
4. **C/D không cô lập ngữ nghĩa:** phép chiếu ridge được fit theo embedding gốc; D hoán vị giúp đối chứng gán token nhưng không kiểm tra riêng tất cả ưu thế thống kê/dung lượng hay việc donor có từng gặp văn bản nguồn.
5. **NLL không thay thế sản phẩm:** không có bằng chứng về chất lượng sinh truyện, tốc độ suy luận, yêu cầu RAM, độ ổn định vận hành hoặc khả năng xuất Ollama của cấu hình C.

## 6. Ràng buộc quản trị và kết luận

- Đây là **bản thiết kế dự thảo**, chưa phải tiền đăng ký thực nghiệm đầy đủ có niêm phong dữ liệu, không phải quyền thực thi và không phải khoa học mới.
- Không sử dụng TEST 64 truyện đã tiêu thụ; chỉ đọc danh sách mã băm thành viên nếu cần kiểm tra loại trùng, không giải mã/nạp nội dung TEST.
- Không tạo checkpoint, không train, không mở CPU scorer, không tải corpus ở bước này, không sửa mã thí nghiệm đã khóa, không sửa main hoặc PR #12.
- `lineage.md` chỉ ghi bổ sung (append-only) khi **sau này** có kết quả khoa học thực PASS/FAIL; tuyệt đối không ghi quyết định thiết kế hoặc QA kỹ thuật vào đó.
- TTM-Small T5 giữ ưu tiên theo lộ trình. Đường D1 G4 vẫn hoãn (DEFERRED).
- Mọi tài liệu mới bằng tiếng Việt, thuật ngữ chuyên ngành tiếng Anh trong ngoặc đơn.

**Bước thực hiện tiếp theo đề xuất:** TTM_SMALL4M_EMBEDDINGGEMMA2_NEW_HOLDOUT_SOURCE_RIGHTS_MEMBERSHIP_AND_EVALUATOR_CONTRACT_SEAL. Trong bước đó chỉ kiểm tra nguồn/quyền, chống trùng và khóa manifest, tiền kiểm mã chấm trên fixture; chưa chấm tập mới, chưa chạy GPU. Sau khi hợp đồng tích hợp PASS và được phê duyệt mới xin một lượt CPU đánh giá duy nhất.
