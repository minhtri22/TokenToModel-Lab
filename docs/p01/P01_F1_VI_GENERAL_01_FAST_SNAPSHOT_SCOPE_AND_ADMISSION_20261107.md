# TTM P01 — F1-VI-GENERAL-01: một lượt snapshot có kiểm soát (Fast Track)

Ngày 07/11/2026. Mục tiêu: rút ngắn đường găng tới P02, không giảm tiêu chí khoa học. Hồ sơ này **chỉ chốt danh sách ứng viên và nguồn bộ chạy**; chưa có byte của 100 văn bản thật và chưa có quyền `E0`.

## Chỉ thị và nguồn

- **Loại toàn bộ CQG-J3 và tài liệu nội bộ nghiên cứu khỏi F1**. Giữ nguyên hồ sơ quyết định F1 tiền nhiệm để truy vết, không import hoặc chạy công cụ kiểm kê CQG-J3 cũ.
- Danh sách nguồn ứng viên cố định trước thu thập: 100 URL, gồm 70 Wikipedia tiếng Việt, 20 Wikisource tiếng Việt, 10 VBPL (mã `ItemID` nguồn chính thức). Danh sách seed máy đọc được được lưu trong tệp đính kèm conversation `TTM_P01_F1_VI_GENERAL_01_FIXED_100_CANDIDATES_20261107.json`, SHA-256 `d4f3210c229f2c1d9808bd615ec8b605a86f3312880b7e422b80f1c3f7e732bd`. **Đây là ứng viên cố định chứ chưa phải 100 trang hợp lệ.**
- Wikipedia: cố định revision ID trước trích xuất, kiểm tra giấy phép site và ngoại lệ từng trang; lưu URL lịch sử, thông tin ghi công. Wikisource: chỉ nhận tự động trang có danh mục PD `PVCC-cũ`, bản dịch/bản in thiếu bằng chứng giữ HOLD. VBPL: chỉ trích đoạn toàn văn chính thức đạt kiểm tra cấu trúc; bản hợp nhất/bài giải thích hoặc không lấy được toàn văn giữ HOLD.
- Phạm vi nghiên cứu này là xây tokenizer BPE riêng. **Không** mặc định sự phù hợp này cấp quyền tái phân phối văn bản hay công bố văn bản nguồn lên GitHub.

## Bộ chạy một lượt

| Thành phần | SHA-256 |
|---|---|
| `TTM_P01_F1_VI_GENERAL_01_SOURCE_SNAPSHOT_PS51_V1.ps1` | `50ee540eec7a946792fc1c291feb4adb21a8f2ffc7a88b68e2a8c20f38ca2b75` |
| `TTM_P01_F1_VI_GENERAL_01_SNAPSHOT_V1.py` | `9da5b25f2b8b45a62f1f88d7e6142e4cfa9d9b3b69caa513f16361c0b35bdb5b` |
| `TTM_P01_F1_VI_GENERAL_01_FIXED_100_CANDIDATES_20261107.json` | `d4f3210c229f2c1d9808bd615ec8b605a86f3312880b7e422b80f1c3f7e732bd` |
| `TTM_P01_F1_VI_GENERAL_01_FAST_SNAPSHOT_BUNDLE_20261107.zip` | `5658ced41c2721cd36412997bccdf463b7673c01c1b7f05618e7ba595dc1fa96` |

Kết quả kiểm tra ngoài Windows: Python `ast.parse/py_compile` PASS, hash hai nội dung nhúng PASS, pool đúng 70/20/10 và 100 ID PASS; zero-science unit check cho HTML parser, canonicalization, near-dup, PII regex PASS. **PowerShell 5.1 native parser/Windows execution chưa thực thi**, không tuyên bố `WINDOWS_PASS`.

Khi người dùng chạy script, chỉ dùng `D:\WORK\RESEARCH\TokenToModel-Lab`. Tạo marker một lượt mới, giữ mọi marker cũ. Raw source HTML và văn bản dẫn xuất đủ điều kiện sàng lọc tự động chỉ lưu ở `datasets/quarantine/f1_vi_general_01_20261107`; receipt không chứa nội dung văn bản tại `evidence/p01/TTM_P01_F1_VI_GENERAL_01_SOURCE_SNAPSHOT_20261107.json`. Mọi tài liệu lỗi mạng, ngoại lệ bản quyền hoặc PII đều HOLD. Không chia TRAIN/VALIDATION/TEST và không truy cập TEST.

Bộ chạy có cơ chế giới hạn 64 MiB tổng raw+derived, tài liệu <=2000, tệp HTTP tối đa 2 MiB, tệp văn bản tối đa 512 KiB, đồng thời chỉ kết nối ba host công khai định danh. Kết quả sàng lọc tự động không tự nhận là một cuộc thẩm định bản quyền/PII đầy đủ.

## Phán quyết và khóa đường găng

Trạng thái lúc phát hành: `SOURCE_POOL_FROZEN=100_CANDIDATE_URLS`, `SNAPSHOT_NOT_MATERIALIZED`, `F1_ADMISSION=HOLD`, `K1_K2=PASS_SCOPED_WINDOWS_EXISTING`, `E0=NOT_EXECUTED`, `P01=OPEN`, `P02=NOT_OPENED`.

Sau khi có receipt, chủ dự án và QA phải kiểm tra đủ >=30 nhóm độc lập, nguồn/giấy phép, PII và quyền dẫn xuất theo snapshot thật. Có thể chấp nhận **ít hơn 100 tài liệu** nếu >=30 nhóm sau dedup. Khi F1 ALLOW, một gói Docker runtime preflight + negative guard QA rồi mới được đề xuất đúng một lượt E0 TRAIN-only hai tiến trình cùng SHA. Giữ `lineage.md` append-only khoa học, không ghi việc tải và fix hạ tầng vào đó; bảo toàn P00, F0, S1 FAIL và phase P00–P12.

## Nguồn quy định API và quyền

- Wikimedia API identification: https://www.mediawiki.org/wiki/Wikimedia_APIs/Access_policy
- Revisions API: https://www.mediawiki.org/wiki/API:Revisions
- Wikimedia content reuse: https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse
- Wikisource public domain guidance: https://vi.wikisource.org/wiki/Trợ_giúp:Phạm_vi_công_cộng
- VBPL official: https://vbpl.vn
