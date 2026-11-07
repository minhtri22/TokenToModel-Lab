# TTM P02 — Thẩm định QA Windows CPU và quyết định đóng phạm vi Transformer Core

Ngày: 07/11/2026. Nguồn: [PR #6](https://github.com/minhtri22/TokenToModel-Lab/pull/6), HEAD được kiểm tra `08e01e5c9c5749ca7da44989e528b175b32ea96e`, base `848c8437cc19a5843b5286d93c246fc1762593a4`.

## Phán quyết

**`P02_SCOPED_CPU_CORRECTNESS_PASS_READY_FOR_MERGE`** theo các tiêu chí gốc P02: shape, gradient hữu hạn, causal isolation và đối chiếu mô hình tham chiếu P00. Đủ bằng chứng để hợp nhất PR #6 sau khi kiểm tra HEAD cuối cùng; **không** tuyên bố model đã học tốt, không tuyên bố QA GPU, không mở P03 chỉ dựa vào lượt QA này.

## Đọc biên bản trên máy Windows

Biên bản gốc `TTM_P02_WINDOWS_CPU_QA_20261107T143953Z_P12672.json`, SHA-256 **`6f47174a1bd3ba34f5fb2da67bdce9e3640b2cf5180f476a4be71915875c7ae7`**, đã đối chiếu với tệp đính kèm cùng SHA. Bản lưu lên GitHub khớp byte với tệp gốc (Git blob `957083406c2b8345e9c2b30d47bc998e2f172f36`).

- Windows Python `3.12.10`, PyTorch `2.11.0+cpu`.
- 6/6 unit tests `exit_code=0`: shape/tied head; P00 LayerNorm logits-loss-gradient parity; gradient finite cho ID token lớn; causal isolation; âm tính; sanity RMSNorm.
- 4/4 independent checker `exit_code=0`: SDPA attention oracle; logits/loss/gradient P00; nhân quả giữa hai batch; shape/tied embedding/boundaries.
- Hai log trực tiếp trên máy đã được đọc, stderr của unittest chỉ là tên bài thử và `OK`, independent log in `status: PASS`.
- SHA hai log theo biên bản Windows: unit `c7d499fbd3c50b08d0984e804399ad86a79d7e0528e258f89401764ad7c2729e`; independent `7fa84c99768c0d816b31eee3f39e37a5e6433e2eb893d653d1ac2e24fa9e7d0a`. Lưu ý adjudicator đọc nội dung các log từ máy nhưng **không tái băm độc lập byte log**; giữ nguyên SHA do runner báo.
- Trạng thái máy theo runner: local main cũ `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` không đổi; worktree tạm đã cleanup PASS.
- Không đọc corpus, không TEST, không chạy optimizer/huấn luyện hoặc checkpoint; P01 one-shot E0 giữ nguyên.

## Ranh giới kết luận

- Chỉ mô hình decoder-only CPU và cấu hình ứng viên P02, vocab 2.048. `P01_E0_merges` được pin theo SHA; chưa chứng minh quy trình mã hóa BPE end-to-end với huấn luyện.
- RMSNorm chỉ tùy chọn; LayerNorm đã đối chiếu đúng toán học và tên trọng số P00 khi cùng kích thước.
- Checkpoint P00 vocab 256 không được chuyển trực tiếp sang P02 vocab 2048.
- Không có CI GitHub do workflow chưa chạy; thay bằng Windows QA local có SHA và log; không nhận là đánh giá của bên thứ ba.
- Giấy phép WP30 hiện chỉ cho E0 nội bộ; **không mở mặc nhiên** huấn luyện GPT trên WP30 ở P03. P03 được phép mở công việc triển khai loop và kiểm thử synthetic riêng; corpus cần thẩm định phạm vi khác.

## Quyết định Git

`lineage.md` không thay đổi ở P02: đây là kiểm định kỹ thuật, chưa phải kết quả khoa học của huấn luyện. QA và kết luận PASS được giữ trong `artifacts/qa/p02/`, không sửa hoặc xóa các FAIL lịch sử.

Sau khi append biên bản và tài liệu lên nhánh PR #6, kiểm tra thay đổi Git và quyết định merge. Chỉ khi GitHub main phản ánh merge mới tuyên bố `P02_CLOSED_SCOPED_CPU`; sau đó mở nhánh P03 trên main xác thực. Chưa chạy thử khoa học nào trong quyết định này.
