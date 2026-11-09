# Quy chuẩn tiếng Việt và thuật ngữ kỹ thuật

## Quy tắc viết

1. Tài liệu diễn giải, hướng dẫn và báo cáo mới phải viết **bằng tiếng Việt**.
2. Khi xuất hiện thuật ngữ chuyên ngành, viết khái niệm tiếng Việt trước và từ tiếng Anh sau trong ngoặc, chẳng hạn: *cơ chế chú ý (Attention)*.
3. Tên tập tin, tên hàm, câu lệnh, đường dẫn, mã Git, mã SHA-256, tên trường JSON, tên thư viện hoặc tên paper được giữ nguyên chính tả vì là định danh kỹ thuật, không phải đoạn diễn giải.
4. Giải thích mọi bảng đo: **đo cái gì → mục đích → đơn vị → giá trị đối chứng → ngưỡng → kết quả → giới hạn khẳng định**.
5. Phân biệt **kiểm thử đạt (QA PASS)**, **kết quả khoa học đạt (Experiment PASS)** và **sẵn sàng thương mại (Commercial Ready)**.
6. Những tài liệu bằng chứng đã khóa được giữ nguyên để bảo toàn nguyên văn và mã băm; nếu cần Việt hóa, tạo bản chú giải mới trỏ về bản gốc. Không sửa lịch sử `lineage.md` ngoài việc ghi bổ sung.

## Từ điển chuẩn cho dự án

| Tiếng Việt | Thuật ngữ gốc |
|---|---|
| Bộ tách token | Tokenizer |
| Mã token | Token ID |
| Chuỗi token | Token Sequence |
| Mô hình chỉ có bộ giải mã | Decoder-only Model |
| Cơ chế chú ý | Attention |
| Cơ chế tự chú ý nhiều đầu | Multi-Head Self-Attention |
| Mặt nạ nhân quả | Causal Mask |
| Biểu diễn nhúng | Embedding |
| Lan truyền ngược | Backpropagation |
| Hàm mất mát | Loss |
| Mất mát chéo | Cross-Entropy Loss |
| Bộ tối ưu | Optimizer |
| Tốc độ học | Learning Rate |
| Bộ nhớ đệm Key/Value | KV Cache |
| Bộ nhớ KV phân trang | Paged KV Cache |
| Bảng ánh xạ khối | Block Table |
| Kho khối bộ nhớ | Block Pool |
| Nhân tính toán chú ý phân trang | PagedAttention Kernel |
| Điểm lưu mô hình | Checkpoint |
| Huấn luyện | Training |
| Kiểm định | Validation |
| Kiểm thử giữ riêng | Held-out Test |
| Kiểm thử độc lập | Independent QA |
| Mốc đối chứng | Baseline |
| Độ tương đương số học | Numerical Parity |
| Sai lệch tuyệt đối lớn nhất | Maximum Absolute Difference |
| Tràn dung lượng bộ nhớ | Out of Memory |
| Số lần chạy | Run |
| Biên bản lần chạy | Run Receipt |
| Dòng lịch sử chỉ ghi bổ sung | Append-only Lineage |
| Cây làm việc Git | Git Worktree |
| Yêu cầu hợp nhất | Pull Request |
| Hợp nhất | Merge |
| Thông lượng | Throughput |
| Độ trễ | Latency |
| Thời gian tới token đầu | Time to First Token (TTFT) |
| Thời gian mỗi token đầu ra | Time per Output Token (TPOT) |
| Độ bối rối mô hình | Perplexity |
| Tính sẵn sàng thương mại | Commercial Readiness |

## Ngoại lệ cố ý

- Giữ nguyên văn các biên bản nguồn trong `artifacts/qa/`, `experiments/runs/`, nhật ký và các tài liệu QA lịch sử đã chốt.
- Không thay mã nguồn Python/PowerShell chỉ vì tuân thủ ngôn ngữ tài liệu.
- Những nhãn gốc trong tệp SVG/PNG đã tạo tại P00 có thể còn tiếng Anh; tài liệu chú giải bằng tiếng Việt nằm tại `docs/diagrams/README.md`. Việc dịch chữ trực tiếp trong hình cần một nhánh thiết kế và QA hình ảnh riêng.

## Thuật ngữ bổ sung cho tuyến huấn luyện T1–T4

| Tiếng Việt dùng khi diễn giải | Tiếng Anh chuyên ngành |
|---|---|
| Tiền đăng ký thực nghiệm | Preregistration |
| Khóa điều kiện khoa học | Science Lock |
| Thẩm định sau kiểm thử | Adjudication |
| Đóng cổng kỹ thuật | Technical Closure |
| Tập thử nghiệm giới hạn | Bounded Pilot |
| Dữ liệu tổng hợp | Synthetic Data |
| Phiên bản nguồn dữ liệu | Dataset Revision |
| Dữ liệu gốc chưa xử lý | Raw Dataset |
| Bản kê dữ liệu/tệp | Manifest |
| Kiểm tra chuẩn bị trước thực thi | Preflight |
| Kiểm tra nhanh năng lực GPU | GPU Capacity Smoke Test |
| Thử nghiệm đúng một lượt | One-shot Experiment |
| Đọc lại bằng chứng độc lập | Independent Evidence Readback |
| Trạng thái dừng bảo toàn bằng chứng | Preserved STOP |
| Bộ chia tập dữ liệu | Dataset Splitter |
| Trùng lặp chính xác | Exact Duplicate |
| Trùng lặp gần | Near-duplicate |
| Phòng ngừa rò rỉ dữ liệu | Leakage Prevention |
| Hạt giống số ngẫu nhiên | Random Seed |
| Bộ lấy mẫu | Sampler |
| Vị trí đang đọc dữ liệu | Data Cursor |
| Trạng thái bộ sinh số ngẫu nhiên | Random Number Generator State (RNG State) |
| Bước tiền phân đoạn token | Pretokenization |
| Biểu thức chính quy của GPT-2 | GPT-2 Regular Expression (Regex) |
| Quy tắc hợp nhất BPE | Byte-pair Encoding Merge |
| Mã token đặc biệt kết thúc truyện | End-of-sequence Token (EOS) |
| Giá trị dự đoán trước chuẩn hóa xác suất | Logits |
| Giá trị lớn nhất theo xác suất dự đoán | Top-1 Prediction |
| Sai lệch tuyệt đối lớn nhất | Maximum Absolute Error |
| Tương đương sau khôi phục | Resume Parity |
| Chỉ lưu và công bố khi hoàn chỉnh | READY-last Commit Protocol |
| Độ chính xác hỗn hợp | Automatic Mixed Precision (AMP) |
| Lô dữ liệu nhỏ | Microbatch |
| Kích thước lô hiệu dụng | Effective Batch Size |
| Tích lũy gradient | Gradient Accumulation |
| Số token mục tiêu mỗi bước | Target Tokens per Step |
| Ngân sách huấn luyện | Training Budget |
| Làm nóng tốc độ học | Learning-rate Warmup |
| Đường suy giảm tốc độ học cosine | Cosine Learning-rate Schedule |
| Mất mát log âm | Negative Log-likelihood (NLL) |
| Mô hình đối chứng cặp từ | Bigram Baseline |
| Làm trơn bằng cách cộng hằng số alpha | Add-alpha Smoothing |
| Tái lấy mẫu tự trợ theo truyện | Story-level Bootstrap |
| Khoảng tin cậy | Confidence Interval |
| Kiểm thử từ chối | Negative Control |
| Tình huống kiểm thử cố định | Frozen Test Fixture |
| Mã nguồn cố định theo SHA | Pinned Source |
| Chương trình suy luận được biên dịch trực tiếp | Native Inference Backend |
| Bộ chuyển đổi trọng số | Model Export Adapter |
| Lượng tử hóa trọng số | Weight Quantization |
| Thông tin gốc của hiện vật | Artifact Provenance |

**Cách áp dụng:** Khi viết câu giải thích, dùng tiếng Việt trước và thuật ngữ tiếng Anh trong ngoặc, ví dụ **“khôi phục điểm lưu mô hình (Checkpoint Resume)”**. Trong bảng có trường máy và khi trích dẫn thông báo lỗi, có thể giữ nguyên tên `checkpoint_step10.pt`, `pass=true`, `SCIENCE_LOCK=HOLD`, SHA-256 và đường dẫn để không làm sai bằng chứng.

**Tình trạng tài liệu:** đọc [mục lục tiếng Việt toàn dự án](vi/README.md); những tài liệu lịch sử có bản dịch riêng phải dẫn chiếu văn bản gốc. Việc Việt hóa không thay đổi định nghĩa PASS/FAIL, không cấp quyền huấn luyện T4 và không ghi đè `lineage.md`.
