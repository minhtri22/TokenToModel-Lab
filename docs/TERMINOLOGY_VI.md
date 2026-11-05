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
