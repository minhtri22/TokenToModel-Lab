# ADR-0001 — TTM chuyển ưu tiên sang huấn luyện mô hình nhỏ và triển khai Colab → Windows

**Ngày:** 2026-11-08  
**Trạng thái:** `OWNER_DIRECTION_APPROVED_IMPLEMENTATION_GATED` — chủ dự án đồng ý điều chỉnh mục tiêu ưu tiên; tài liệu và các bước kỹ thuật mới chỉ có hiệu lực trên `main` sau review/merge PR quản trị.  
**Nguồn gốc:** `minhtri22/TokenToModel-Lab`, `main` tại `4731f75cda6aa86b1dd2929b3f10d11fbbed0812`.  
**Phạm vi:** quyết định quản trị và ưu tiên thực thi, **không** sửa hồi tố P00–P12, không thay nguyên lý Transformer/Attention/KV đã duyệt, không làm mất FAIL/PASS, không cấp quyền huấn luyện/TEST hoặc sửa corpus.

## 1. Lý do và quyết định

1. Máy dev Windows `DESKTOP-4PSD0G2` dùng Intel Core Ultra 7 258V, Intel Arc 140V và RAM 32 GB, phù hợp sửa mã, kiểm chứng GPU và suy luận nhỏ; không nên lấy một giờ GPU local làm ngân sách mặc định cho huấn luyện mô hình lớn.
2. Mục tiêu ưu tiên là **một mô hình TTM nhỏ có khả năng học chứng minh được** trên dữ liệu có giấy phép, kiểm định held-out và so sánh với baseline; loss overfit synthetic P03 và checkpoint smoke P04 **chưa đủ**.
3. Huấn luyện chính dùng GPU Colab (tài nguyên phiên không bảo đảm); checkpoint lưu Google Drive với xác minh integrity, resume không lặp bước và không xem trước TEST.
4. Checkpoint sau huấn luyện lưu về Windows, có tuyến xuất GGUF kiểm chứng cho llama.cpp/Ollama; **không** tuyên bố PyTorch checkpoint hiện tại có thể import trực tiếp. TTM P02 có positional embeddings học được và tokenizer BPE riêng, nên cần exact tensor/tokenizer mapping, parity logits/generation và QA tương thích.
5. Thử nghiệm bật/tắt kiến trúc/training phải huấn luyện các đối chứng ngang ngân sách; thử nghiệm cache/inference giữ nguyên checkpoint và token IDs/dtype/hardware để phân biệt hiệu quả với chất lượng. Báo cáo cả PASS lẫn FAIL.

## 2. Chế độ giữ nguyên và xử lý công việc đang mở

- **P00–P06**: đã merge/đóng đúng phạm vi kỹ thuật; không chạy lại khoa học hoặc sửa nguồn đã khóa.
- **P07**: **PAUSED_PRESERVE**. XPU `2.12.1+xpu` Intel Arc 140V canary = `PASS_REAL_GPU`; V1 one-shot `CONSUMED` và tổng run FAIL vì vượt ngân sách con 6 GiB (6.037 GiB), S2 compiler canary = `NOT_EXECUTED`; nhánh P07 HEAD tại thời điểm kiểm kê `06b047856a841a2213803608edfe336588857f59` không merge/xóa/rewrite. Không cài SYCL lúc thay đổi lộ trình.
- **P08**: chưa mở, không cho phép mở chỉ vì pilot PASS.
- **P09/P10**: không giả định đang mở; pilot là **tuyến xác nhận tích hợp TTM-SMALL-PILOT** bên cạnh phase, không thay số phase hoặc tạo lối tắt để tuyên bố P09/P10 đã đạt. Trước khi pilot sử dụng dữ liệu mới phải có prereg và quyền nguồn riêng.
- **P01 F1 WP30 E0**: 30 tài liệu Wikipedia tiếng Việt chỉ được phép cho BPE E0 nội bộ theo phán quyết cũ; **không** tái diễn giải thành quyền huấn luyện GPT hay thương mại.
- **lineage.md**: **chỉ append các quyết định/kết quả khoa học**, gồm cả FAIL science, **không ghi sửa hạ tầng/code/QA kỹ thuật**, giữ nguyên byte/historical entries; mọi quyết định quản trị/QA lưu tệp khác.

## 3. Tuyến pilot hữu hạn (không triển khai trước khi branch hygiene xong)

| Mốc | Đầu ra | Điều kiện PASS thực sự |
|---|---|---|
| T1 — Data/Tokenizer | Nguồn có snapshot, giấy phép, attribution, PII/split/dedup kiểm chứng; TinyStories là **ứng viên**, không mặc nhiên được duyệt | TRAIN/VAL/TEST khóa; cùng tokenizer cho train và decode; TEST chưa sử dụng |
| T2 — Export dry-run | Trọng số checkpoint TTM nhỏ **chưa cần train thật** và tokenizer chuyển thử GGUF | llama.cpp hỗ trợ kiến trúc/tokenizer mapping và logits/generation parity với PyTorch, nếu FAIL thì dừng trước full train |
| T3 — Colab/Drive | Notebook/script phiên bản hóa; môi trường pinned; Drive lưu checkpoint atomic verified | Resume parity: loss/step/token cursor, optimizer, scheduler, RNG, sampler; không đánh đồng retry một run khoa học |
| T4 — Small-model train | TTM ~4M là cấu hình **ứng viên**, không khóa size/token/steps chưa đo; baseline được đăng ký trước | VAL NLL/perplexity tốt hơn baseline trên cùng tokenization, mẫu sinh theo bộ prompt khóa, không dùng TEST để tune |
| T5 — Local deployment | Checkpoint SHA tải về Windows và chuyển GGUF | Chạy llama.cpp/Ollama thực sự; tokenizer và logits/outputs được so với nguồn; lưu cấu hình Modelfile |
| T6 — A/B | Ma trận cache on/off, GPU backend, quantization, norm type nếu train hai nhánh | A/B ngang dữ liệu, ngân sách, mô hình/weights thích hợp, đồng bộ GPU và nhiều repeat; log TTFT, TPOT, tokens/s, RAM/quality |
| T7 — GPU optimization | Quay lại P07 rồi P08 theo exit gates gốc | Direct-page numerical parity độc lập, benchmark same-GPU và formal merge trước P08 |

**Chỉ khởi động T1 sau khi nhánh cũ được dọn/đánh dấu hoàn thành**, tài liệu governance được merge và có một bản prereg riêng cho TTM-SMALL-PILOT. Từng bước QA kỹ thuật không cần permit riêng; chỉ các cổng nguồn khoa học, tài nguyên và các thực thi one-shot tương ứng mới cần quyết định.

## 4. GitHub cleanup là cổng trước pilot

Kiểm kê chính xác: **31 nhánh**, **10 PR** (9 merged, 1 draft PR #4 mở). Có **9 nhánh đã là ancestor của main**, **17 nhánh là ancestor của một lịch sử P01 dài**, **1 nhánh source tip của lịch sử P01**, **2 nhánh phân kỳ P01 độc lập**; cộng P07 và main = 31.

Ba `archive/` đã được tạo và read-back tại SHA nguyên bản, không force rewrite:
- `archive/p01-legacy-f1-wp30-lineage-20261108` → `a4317b3546cb5a1f3dbf71ccf7d53e2930959593`; bao trùm lịch sử của 17 nhánh P01 cũ.
- `archive/p01-d1-prereg-draft-20261108` → `b25a858cb039ea5c2a7196d7668cf4ae18eafeb7`; bảo toàn toàn bộ nhánh thiết kế PR #4.
- `archive/p01-i0a-f0-static-side-20261108` → `b793191932d794e53d88e275a45bad571750a9c3`; bảo toàn nhánh I0A lịch sử không nằm trong chain chính.

Nguồn khóa chi tiết mọi ref: `artifacts/governance/TTM_BRANCH_CLEANUP_EXACT_REF_MANIFEST_20261108.json`. **Không merge** 290 file từ nhánh P01 lịch sử vào main; 3 archive branch giữ được commits cho forensic readback. **Không xóa ref nào chưa được xác minh ancestor/same-SHA và đồng thời còn PR mở.** Sau khi đóng PR #4 không merge, có thể dọn đúng 29 tên nhánh nguồn theo manifest, với remote compare-and-swap/lease trên từng SHA. Không xóa branch `main`, `feature/p07-...`, `governance/...` hoặc 3 `archive/...`.

GitHub connector phiên này **không có API delete_ref**. Không nhận rằng đã xóa nhánh cho tới khi lệnh xóa qua Git CLI với `--force-with-lease` được thực hiện và đọc lại chính xác danh sách ref. Không tự xóa worktree, file, nguồn hay evidence trên máy Windows.

## 5. Cổng sẵn sàng

- `GOVERNANCE_DOC=PREPARED` sau khi commit; `GOVERNANCE_ADOPTED` chỉ sau review/merge.
- `BRANCH_CLEANUP=NOT_COMPLETE` cho tới khi các tên nguồn đúng manifest đã biến mất trên remote mà 3 archive và P07/main không đổi SHA.
- `TRAIN_PILOT=NOT_OPENED` và `COLAB_EXECUTION=NOT_AUTHORIZED`.
- Pilot khoa học chỉ được thực hiện sau prereg dữ liệu/config/metrics/checkpoint, không mượn quyền từ thử SYCL.

**Bước tiếp theo:** đóng draft PR #4 theo lý do superseded (bảo toàn archive), dùng manifest và script an toàn để xóa remote các ref cũ, kiểm toán lại repo; sau đó review/merge governance PR và mở pilot prereg mới.
