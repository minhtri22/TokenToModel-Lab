# P03 — Phán quyết QA Windows và điều kiện chuyển P04

Ngày 07/11/2026. PR #7, HEAD `3ae89a6de84ed5fd009b82842a38657c7aaa7f8f`, base P02 `dd8e83658535daad02d008d1b6a959628336cf31`.

**Phán quyết: `P03_PASS_SCOPED_SYNTHETIC_CPU_READY_FOR_MERGE`.** Đây là kiểm định chức năng vòng huấn luyện trên batch tổng hợp, không phải thực nghiệm chất lượng ngôn ngữ hoặc đánh giá held-out.

- Bản gốc biên bản Windows `TTM_P03_WINDOWS_SYNTHETIC_CPU_QA_20261107T150029Z.json` có SHA-256 `4f89c1006ad2344b10bb1d9b8ff05e11cdf6dd7c2923f43cffbbb923c1c2dc80`, Git blob exact `e71e13bea6f87f2d4725f240c18f11bb6a3bb8e1`; bản đính kèm cùng byte.
- Python 3.12.10/PyTorch 2.11.0+cpu. 6/6 unit PASS; 7/7 independent PASS, exit code 0 cả hai.
- Log Windows trực tiếp đã đọc: `evidence/p03/TTM_P03_WINDOWS_SYNTHETIC_CPU_QA_20261107T150029Z.unittest.log` và `...independent.log`; SHA theo receipt lần lượt `11606cc17f2e5c3ba9c7c4c71af0c760d23b6bf28dfda2dedca4cb54ecad3a8d`, `35bdbc1294e533a63bd209815d3ae7b379fde13b33ff3f263e188b100d478ec0`. Chưa tính lại byte-hash hai log ở lượt thẩm định này.
- Mã P03/test/independent checker và P02 dependency đối chiếu chính xác các Git blob trong biên bản.
- Loss trên cùng batch tổng hợp: `7.674461841583252` → `0.015135478228330612` (giảm ≈99,80%). Trọng số cập nhật, gradient và tham số hữu hạn, scheduler hợp lệ; **không phải held-out**.
- Không sử dụng Wikipedia F1/TEST; không sinh checkpoint, không mở P04, không có đánh giá trên GPU. Quyền WP30 trước đó chỉ cấp BPE E0, không suy ra quyền huấn luyện GPT.
- Runner xác nhận local main cũ `92facee...` không đổi và cleanup worktree PASS; local main cần đồng bộ riêng bằng fast-forward an toàn nếu cần.
- Giữ nguyên `lineage.md`, các kết quả FAIL lịch sử, kiến trúc P00–P12. Đây là kết quả QA kỹ thuật, không tuyên bố phát hiện khoa học mới.

Sau khi bổ sung hai hồ sơ và biên bản gốc vào PR #7: kiểm tra exact HEAD và diff rồi hợp nhất khi các điều kiện đạt. Chỉ sau khi `main` xác nhận merge mới mở P04 checkpoint, sampling và đánh giá synthetic trước; không tự động dùng F1 held-out.
