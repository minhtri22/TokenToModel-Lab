# P00 — Biên bản thẩm định QA độc lập (2026-11-05)

## Phạm vi và quyết định

- Decision ID: `TTM_P00_WINDOWS_INDEPENDENT_QA_ADJUDICATION_20261105`.
- Kết luận: **PASS — P00 CPU REFERENCE CORRECTNESS**, giới hạn đúng chức năng mô hình và bộ quản lý KV cache ở mức tham chiếu.
- Source frozen for evaluation: `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- Main trước thay đổi: `f2ed098b033431924a3cbabdc9af89d7bbd7b378`.
- Model SHA-256: `821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea`.
- Config SHA-256: `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`.
- Trạng thái config trong tệp: `PROPOSED_NOT_FROZEN`. Chỉ khóa cấu hình làm **engineering QA reference candidate** bằng hash trong biên bản này; **không** gọi là scientific training lock.

## Tiếp nhận bằng chứng

| Nguồn | Phép thử | Kết quả | SHA-256 |
|---|---|---|---|
| Windows local QA, `TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z` | 5 mô hình + 8 quản trị/script | 13/13 PASS | `6f30d4450199d471acd5e5a9c7b8264bc8fdc653bdc3b76ba5bfa8afa47034ee` |
| Windows independent QA, `TTM_P00_INDEPENDENT_QA_20261105T051340397776Z` | 6 bài test bổ sung, tách riêng từ dev tests | 6/6 PASS | `b657b40e3da40060ef6c2e2b81239c64539f93100e169dae4920135ad6f16c38` |
| Đọc lại hai receipt qua RemoteMCP | Gốc Windows và bản GitHub | CONTENT MATCH | SHA hai receipt trên |
| Bốn log của Windows local QA | File SHA và nội dung `Ran ... OK` | PASS | Chi tiết trong receipt |

- Đường dẫn local gốc: `D:\WORK\RESEARCH\TokenToModel-Lab\evidence\p00\`.
- GitHub archive: `artifacts/qa/p00/`, gồm 2 receipt, hai stderr log và mã test độc lập.
- Bản mã test bổ sung được lưu cùng repo để tái hiện; SHA-256 mã Python là `b58562f98485bd96cae5406381be004fe1844ef3bdc7116f58a7316f669bd6d8`.
- Test trên Windows: Python 3.13.12, PyTorch 2.12.0+cpu, Windows 11.
- Mô hình dùng dữ liệu fixture, không tải tập huấn luyện khoa học.

## Kết quả định lượng

- Dense vs paged logits max abs error: `2.384185791015625e-07`.
- Causal-prefix max abs error: `0.0`.
- Next-token gradient smoke loss: `5.489449977874756`; đây **không phải** chất lượng mô hình đã train.

## Giới hạn thẩm định

1. Đây là P00 correctness reference, **không phải** GPU, PagedAttention kernel trực tiếp hay tăng tốc thực tế. Đường paged vẫn gather K/V vào tensor liên tục.
2. Không có huấn luyện trên corpus hay đánh giá held-out. Không suy diễn năng lực ngôn ngữ hoặc thương mại hóa.
3. Bộ test độc lập về fixture/bộ kiểm thử so với dev test; không tuyên bố đã có một tổ chức QA bên thứ ba.
4. P00 là mốc đầu tiên nên không có predecessor tương đương để báo cáo cải thiện hiệu năng. So sánh Linux reference và Windows là kiểm tra tính tương thích, không phải benchmark.
5. Công cụ RemoteMCP project cũ `prj_7ff9a13a92022806cecf44b7` đang NON_GIT và task `tsk_fcaae8452d82e4872bc1748e` là RECOVERABLE; không động vào task hoặc sửa hạ tầng để merge GitHub.

## Kết luận và cổng hợp nhất

- `INDEPENDENT_EVIDENCE_PROVENANCE=PASS`
- `INDEPENDENT_WINDOWS_FUNCTIONAL_QA=PASS`
- `SCIENCE_TRAINING=NOT_PERFORMED`
- `P00_QA_ADJUDICATION=PASS_SCOPED_CORRECTNESS`
- `MERGE_ELIGIBILITY=PASS_CONDITIONAL`: chỉ sau khi ghi nhật ký append-only và nhận diện exact-head mới, kiểm tra trạng thái GitHub/PR, không có thay đổi runtime, source hoặc config từ commit được kiểm định; nhật ký mới chỉ bổ sung docs/evidence.
- Không tạo, xóa, di chuyển hay dọn dẹp bất kỳ Git worktree nào.

**Quyết định:** ACCEPT P00 như một baseline kỹ thuật nhỏ sau merge; các phase P01–P12 giữ các cổng riêng.
