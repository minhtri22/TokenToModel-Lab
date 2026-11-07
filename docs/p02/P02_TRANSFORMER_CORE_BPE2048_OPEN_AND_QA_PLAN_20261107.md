# TTM — P02 Transformer Core (mở từ PR #5 sau P01 closure)

Ngày 07/11/2026. Giai đoạn: **P02 OPEN — IMPLEMENTATION CANDIDATE, chưa đóng, chưa mở P03**.

## Nguồn chuẩn và bất biến

GitHub main sau hợp nhất PR #5: `848c8437cc19a5843b5286d93c246fc1762593a4`. `lineage.md` đã bổ sung `L0010` cho kết quả P01 E0. Không sửa P00, P01 hoặc `lineage.md` ở nhánh P02. Từ vựng BPE 2048 token được ràng buộc bằng SHA-256 của `merges.ttmbpe`:
`53aabcb8ac3a3c16c7cbd915b76eb82653a334c98381fad95a05eba0a9353f60`.

**Giới hạn:** P02 chỉ kiểm tra mô hình trên **ID token tổng hợp**. Không nạp 30 bài Wikipedia, không đọc TEST, không huấn luyện hay lưu checkpoint. Giấy phép nhận F1 cho E0 nội bộ không tự động cho phép P03/đóng gói công khai.

## Kiến trúc triển khai

Tệp `src/p02/transformer_core.py`: GPT decoder-only; embedding token `[2048,64]`, position `[64,64]`, 2 lớp, 4 attention heads, attention mask tam giác nhân quả, MLP GELU 4× hidden, kết nối residual, chia sẻ embedding/head. Chế độ chính: **LayerNorm**, cấu trúc và tên tham số tương thích P00 khi P00 được tạo với cùng kích thước `vocab_size=2048`; RMSNorm là lựa chọn chưa khóa cho P03.

P02 mặc định có **235264 tham số độc lập**. Không được nạp checkpoint demo P00 `vocab_size=256` như thể có cùng kích thước: token embedding và head output khác.

**Ranh giới với P00:** đã so hash đúng mã `reference/phase0/model.py` của GitHub (SHA-256 `821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea`, Git blob `fccd8d9f923b75dad04dccf51caa0a696eefb118`). P02 không tái triển khai đường KV phân trang; phần này vẫn thuộc P05–P08.

## Kiểm thử tích hợp tối thiểu (synthetic)

`tests/p02/test_transformer_core.py` gồm 6 bài:
1. Kích thước logits `[2,9,2048]`, embedding/head tied, không có NaN/Inf.
2. Gradient hữu hạn cho ID 256, 1024, 2047 và các lớp Attention/MLP.
3. Thay đổi token tương lai không đổi logits của tiền tố.
4. Tải state_dict từ mô hình P00 có cùng kích thước, đối chiếu logits/loss/gradient với `torch.testing.assert_close`.
5. RMSNorm tạo shape/gradient hợp lệ (chỉ ứng viên, không mặc định).
6. Âm tính: ID ngoài từ vựng, độ dài sai, dtype sai, cấu hình heads không hợp lệ, target shape sai.

Kết quả ngoại tuyến ở môi trường biên soạn: **6/6 PASS**, Python 3.13.5, PyTorch 2.10.0 CPU. Không phải QA trên Windows người dùng, không phải kiểm định bên thứ ba.

## Quy trình kiểm thử Windows P02, không dùng dữ liệu khoa học

Trên máy người dùng: sau khi xác minh nhánh và nguồn mới, sử dụng Python có PyTorch (ưu tiên 3.12 nếu thư viện có sẵn, nếu không dùng Miniforge3 3.13 đã có PyTorch; không cài hoặc thay base). Từ gốc worktree P02 chạy:
`& $python -B -m unittest discover -s tests/p02 -p test_*.py -v`.

Ghi log, phiên bản Python/PyTorch, HEAD, mã hash nguồn/config và verdict vào bằng chứng trong workspace; chỉ sau khi Windows QA đạt, đối chiếu độc lập/PR mới xét đóng P02. Không chạy P03 trong gói này.

## Trạng thái và bước tiếp theo

`P01=CLOSED_SCOPED_MAIN`; `P02=OPEN_IMPLEMENTATION_CANDIDATE_OFFHOST_QA_PASS_6_6`; `P02_WINDOWS_QA=NOT_EXECUTED`; `P03/P04=NOT_OPENED`; `lineage.md=UNCHANGED_ON_P02`.

**Bước thực hiện tiếp theo:** `TTM_P02_EXACT_BRANCH_WINDOWS_CPU_QA_AND_INDEPENDENT_ADJUDICATION`, rồi PR review/merge P02. Sau đó P03 mới thực hiện micro-batch overfit với điều kiện nguồn phù hợp.
