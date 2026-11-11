# TTM — TEST bí mật và kiểm tra tĩnh tương thích tokenizer (2026-11-11)

**Công việc:** `TTM_VECTOR_MEMORY_EXTERNAL_FACTS_TEST_SEAL_AND_TOKENIZER_COMPATIBILITY_STATIC_QA`  
**Nhánh:** `research/ttm-vector-memory-architecture-20261111` — không merge `main`, không thay P00–P12.  
**Kết luận:** `TEST_SEAL=PASS_OWNER_PRIVATE` · `CONTRACT_AND_BYTE_BOUND_QA=PASS_18/18` · **`ACTUAL_T1_BPE_EXACT_QA=HOLD_MISSING_MANIFEST`** · `SCIENCE_NOT_EXECUTED`.

## Dữ liệu và niêm phong

- Dùng generator đã khóa `external_knowledge_fixture.py`, SHA-256 `a206bf0c1804969feea993dde0d096b730ce7fed2f79b792c334bd0a4f06609c`.
- Sinh một lần 64 TEST case bằng secret 48 byte ngẫu nhiên (`token_urlsafe(48)`), khác hoàn toàn với secret QA giả lập. TEST khác TRAIN 256 và DEV 64 về case ID và target entity; 16 nhãn TEST cân bằng đúng 4 lần mỗi nhãn.
- Sinh TEST trong bộ nhớ, kiểm tra schema và tính chống rò rỉ, niêm phong bằng AES-256-GCM, chỉ lưu **ciphertext** và **owner-only secret/key escrow**; không lưu plaintext TEST lâu dài. Không in secret, key, câu hỏi, đáp án hoặc token TEST vào GitHub.
- TEST ciphertext SHA-256: `33a43056937d424fee6407f997f9791676c2ad50af209a20f180ada154ee98e3`; plaintext commitment SHA-256: `b004b1e7b49c777fe56d20c9f586991c98843aebc83020b16cd1446d9d4f7c3e`.
- Lưu trên Google Drive của chủ dự án dưới `TTM/ttm-small-pilot/` ở hai thư mục **riêng**: `vm-external-test-sealed-v1/` (ciphertext) và `vm-external-test-owner-escrow-v1/` (private key + generation secret). Google Drive trả về `shared=false`, quyền sở hữu `owner` và readback byte-for-byte SHA trùng với bản nguồn. Không gắn public link tới hai hiện vật.
- **Giới hạn:** escrow do chủ sở hữu nắm giữ, **chưa có người giữ TEST độc lập bên ngoài**. Cả hai thư mục nằm trong cùng tài khoản Google Drive nên không tách rời về quyền truy cập; cần kỷ luật không giải mã cho tới lúc khóa cấu hình và chạy một lần.

## Kiểm tra giới hạn 256 token

Đối với nguồn T1 `ttm.gpt2.pretokenized.byte-bpe.2048.v1`, tokenization bắt đầu từ 1 token mỗi byte UTF-8, và các phép BPE chỉ **gộp**, không làm tăng số token. Với dữ liệu mới hoàn toàn ASCII, số byte là chặn trên hợp lệ của số token BPE, bất kể 1.791 cặp merge đã học.

| Chuỗi | Độ dài byte tối đa | Chặn trên số token T1 | Kết quả |
|---|---:|---:|---|
| Câu hỏi | 76 | ≤76 | PASS |
| Nhãn đáp án | 5 | ≤5 | PASS |
| Câu hỏi + một dấu cách + đáp án | 82 | ≤82 | PASS |
| Mỗi memory fact card | 52 | ≤52 | PASS |

**18/18 kiểm tra hợp đồng PASS** trên TRAIN 256, DEV 64 và TEST 64. Không dùng TEST cho tuning mô hình. Bộ nhớ truyền qua kênh reader riêng nên không tính các fact cards vào prompt GPT chính.

## Giới hạn quan trọng về tokenizer thật

Không tìm thấy file manifest **T1 TRAIN-only BPE thật** ở nguồn Drive/GitHub có thể truy cập hiện tại. SHA-256 được khóa trong nghiên cứu TTM là `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.

Vì vậy **chưa** kết luận được:

1. Token ID chính xác trên câu hỏi và từng nhãn sau 1.791 cặp merge đã học.
2. Round-trip thực tế `decode(encode(x))=x` qua manifest T1 thật.
3. Số token thực tế của 16 nhãn, và prefix alignment giữa question/answer-only teacher forcing (cần kiểm riêng vì BPE có thể gộp khác tại ranh giới).

Đã chuẩn bị runner `real_t1_bpe_compat_audit.py`: kiểm SHA manifest, kiểm Git blob mã T1, thử TRAIN/DEV theo tất cả các nhánh/fact cards. Runner **không đọc hoặc giải mã TEST**; nếu thiếu đúng manifest, trả `HOLD` với mã thoát 2. Chưa thực thi đánh giá NLL hoặc model inference.

## Bước thực hiện tiếp theo — một cổng tích hợp

`TTM_VM_REAL_T1_MANIFEST_ACQUISITION_AND_CPU_ORACLE_READER_READINESS`

Đưa manifest T1 đã khóa (SHA-256 ở trên) vào thư mục private bên trong project root; chạy đúng một lượt audit real tokenizer trên TRAIN+DEV. Chỉ khi đạt `PASS_REAL_T1_TOKENIZER`, khóa tiếp source-only frozen-bypass/oracle-reader runner và cân nhắc riêng việc huấn luyện CPU trên TRAIN. TEST ciphertext không mở trước khi chốt runner + checkpoint + lựa chọn bằng DEV.

**Lineage:** không ghi entry mới vì đây là kiểm tra tĩnh/niêm phong, chưa có PASS/FAIL khoa học. Các kết quả khoa học cũ L0015–L0019 giữ nguyên.
