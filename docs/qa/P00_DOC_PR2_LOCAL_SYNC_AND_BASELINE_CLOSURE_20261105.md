# P00 — Thẩm định đồng bộ PR #2 và xác lập mốc đối chứng kỹ thuật

**Mã quyết định:** `TTM_P00_DOC_PR2_LOCAL_SYNC_AND_BASELINE_FINALIZATION`  
**Ngày:** 05/11/2026  
**Kho nguồn:** `https://github.com/minhtri22/TokenToModel-Lab.git`  
**Workspace Windows:** `D:\WORK\RESEARCH\TokenToModel-Lab`

## 1. Bằng chứng gốc được khóa

- Biên bản đồng bộ PR #2: `TTM_P00_DOC_PR2_FAST_FORWARD_20261105T081134196Z.json`.
- Nơi lưu gốc trên Windows: `evidence/p00/TTM_P00_DOC_PR2_FAST_FORWARD_20261105T081134196Z.json`.
- Bản lưu trên GitHub: `artifacts/qa/p00/TTM_P00_DOC_PR2_FAST_FORWARD_20261105T081134196Z.json`.
- **SHA-256 tệp gốc:** `9159499147c7b47b61427af6712adc33152401c1545f538ae890d4bad7305ed4`.
- Nội dung đọc lại trực tiếp qua RemoteMCP và nội dung tải lên GitHub **trùng từng ký tự**, gồm các kết thúc dòng CRLF. Các lần đọc lại không thay đổi biên bản nguồn.

## 2. Kết quả thẩm định

| Mục | Giá trị/quan sát | Kết luận |
|---|---|---|
| PR tài liệu #2 | Đã hợp nhất `2026-11-05T08:05:19Z` | PASS |
| Local `main` trước đồng bộ | `8df22f5f29e645b2becff936daccbd32ac780661` | Khớp mốc P00 trước PR #2 |
| GitHub `main` và local `main` sau đồng bộ | `c66e27a5d1e68958d42c825fd40f8a273994e0a0` | PASS tại thời điểm kiểm tra |
| Local `origin/main` | `c66e27a5d1e68958d42c825fd40f8a273994e0a0` | PASS |
| Phương thức đồng bộ | `EXACT_PIN_FAST_FORWARD_ONLY` | PASS |
| Số tệp Markdown thay đổi trong PR #2 | `25` | Tất cả thay đổi trong PR #2 là Markdown, không phải code khoa học |
| Tệp nguồn/tạm/bằng chứng được bảo vệ | `13` | **13/13 SHA-256 PASS** khi đọc lại từng tệp trực tiếp trên máy |
| Worktree P00 | `382da2c52d0fb4efe1cd9de5c92e68de79a52a20` | PASS, giữ nguyên |
| Dọn dẹp | `NONE` | Không xóa tệp hoặc worktree |
| Huấn luyện khoa học | `NOT_PERFORMED` | Chưa được phép diễn giải thành kết quả học |
| P01 | `NOT_AUTHORIZED` | Chưa mở nghiên cứu/huấn luyện mới |

Kiểm tra chương trình đồng bộ đã lưu tại `tmp/TTM_P00_PR2_FAST_FORWARD_SAFE.ps1`: mã SHA-256 `cae46bced6a34844a6564aefae4586850b1cc9db6ad05a00c60de619a3de28b9`. Chương trình kiểm tra nguồn Git, commit chính xác, tính sạch của Git, hai worktree, không phân kỳ và SHA trước/sau; thực hiện `merge --ff-only` sau khi `fetch` đúng ref. Không thực hiện `reset --hard`, `git clean` hoặc dọn worktree.

## 3. Giải thích các đại lượng

**Mã commit Git (Commit SHA):** đối chiếu chính xác 40 ký tự để chứng minh các tham chiếu cùng trỏ một phiên bản mã/tài liệu. Phép đo có tính đúng/sai tuyệt đối; không phải số đo tốc độ hay chất lượng mô hình.

**Mã băm SHA-256 (File Integrity Hash):** băm nội dung byte của từng tệp. Khi so sánh trước/sau và với biên bản cùng mã, dữ liệu không bị thay đổi ngoài ý muốn. 13/13 là số tệp được bảo vệ, **không** phải 13 bài đánh giá mô hình.

**25 tệp Markdown:** số tệp sửa trong PR #2, thể hiện phạm vi thay đổi. Không suy diễn chất lượng tài liệu, mức độ huấn luyện hay cải thiện hiệu năng từ số lượng tệp.

**Kết quả chức năng CPU P00 (CPU Correctness):** 13 bài kiểm thử cục bộ và 6 bài kiểm thử bổ sung độc lập trước đó đạt trong phạm vi nguồn `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`. Đồng bộ Git **không** chạy lại hai bộ này và không cộng chúng với các phép kiểm tra Git.

## 4. Kết luận mốc đối chứng

- **Mốc nguồn đã kiểm định:** `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- **Mốc hợp nhất nguồn P00 (PR #1):** `8df22f5f29e645b2becff936daccbd32ac780661`.
- **Mốc tài liệu/đối chứng kỹ thuật P00 hoàn chỉnh (PR #2):** `c66e27a5d1e68958d42c825fd40f8a273994e0a0`.
- **Mã cấu hình P00:** `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`, tệp vẫn ghi `PROPOSED_NOT_FROZEN`. Chỉ dùng làm mốc kỹ thuật, **không** gọi là cấu hình thí nghiệm khoa học đã khóa.
- Bộ nhớ KV phân trang (Paged KV Cache) tại P00 có phép kiểm tra tính đúng chức năng; chưa có nhân GPU đọc trang trực tiếp (PagedAttention Kernel) hay chứng cứ tăng tốc.
- Nội dung tài liệu và biên bản lịch sử đã được giữ đúng, cùng chú giải tiếng Việt ở `docs/TERMINOLOGY_VI.md`.

**Kết luận:** `P00_ENGINEERING_BASELINE_FINALIZED=PASS_SCOPED_CPU_CORRECTNESS`; `P00_PR2_LOCAL_SYNC=PASS`; `P00_WORKSPACE_PRESERVATION=PASS`; `SCIENTIFIC_TRAINING=NOT_PERFORMED`.

Việc lưu bổ sung biên bản kiểm toán trong một nhánh/PR hồ sơ riêng có thể làm GitHub `main` đi tiếp nếu được hợp nhất. Điều đó **không thay đổi mốc đối chứng đã khóa** `c66e27a5d1e68958d42c825fd40f8a273994e0a0`. Để bắt đầu nhánh mới P01 sau này, cần kiểm tra GitHub HEAD mới nhất và trạng thái local trước bất kỳ thao tác Git; không lặp vô hạn các bước đồng bộ chỉ vì thêm báo cáo lưu vết.

## 5. Điều kiện trước P01

Cổng thiết kế P01 được xem xét **riêng**, bao gồm mục tiêu bộ tách token (Tokenizer), nguồn dữ liệu có giấy phép, hợp đồng biểu diễn token, kiểm thử khứ hồi (Round-trip), đánh giá rò rỉ dữ liệu, tài nguyên và giới hạn nơi làm việc. Không tự phát lệnh huấn luyện, tải dữ liệu hoặc tạo worktree P01 ở bước này.
