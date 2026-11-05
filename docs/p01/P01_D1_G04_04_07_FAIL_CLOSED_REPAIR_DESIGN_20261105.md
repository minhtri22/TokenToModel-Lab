# P01 D1 — G04-04..07: Tái lập, quyền dữ liệu, bảo vệ tài nguyên và chứng cứ

**Phiên bản:** `TTM_P01_H04_FAIL_CLOSED_REPAIR_V1_DESIGN`  
**Chỉ thiết kế (DESIGN_ONLY):** không tạo snapshot corpus, không chạy BPE/checker, không tạo worktree, không thay máy Windows.

## G04-04 — Tái lập từ TRAIN và bảo đảm TEST không bị đọc

**Hợp đồng snapshot khi có nguồn được phép, chưa tạo snapshot tại D1:**
1. Chỉ nhận `source_id` có quyết định `ALLOW` cùng giấy phép, rà soát PII và mã băm byte nguồn khớp. `PENDING` hoặc `REJECT` đều bị từ chối.
2. Mỗi bản ghi TRAIN gồm `document_id` UTF-8 đã khóa, `source_id`, `raw_sha256`, `byte_count`, `group_id` và `split=TRAIN`. Từ chối trùng ID có byte khác nhau, bất kỳ hash thiếu hoặc sai định dạng. Mọi bản ghi của VALIDATION/TEST nằm ngoài snapshot học BPE.
3. Sắp các bản ghi theo dãy **byte UTF-8 của document_id**, sau đó `raw_sha256` 32 byte làm quy tắc phá hòa; bảo toàn ranh giới và byte từng tài liệu. Manifest định dạng chuẩn là tập dòng có độ dài/ký tự phân cách được định nghĩa trước I0, không tự dùng `repr(dict)` hay JSON với thứ tự khóa thay đổi.
4. Danh tính `TRAIN_snapshot_sha256` được tính trên **byte manifest chuẩn** cộng hash từng raw payload; cả mã nguồn, phiên bản Unicode/Python, `target_vocab_size`, quy tắc phá hòa và chính sách split phải có SHA/commit được ghim.
5. Hai tiến trình sạch với cùng snapshot đã được cấp quyền và seed/config được ghim phải sinh **byte giống hệt** của `merges.ttmbpe`; checker thứ hai băm trực tiếp byte tệp, so SHA và danh sách quy tắc đọc từ parser riêng. So log thành công hoặc số merges không đủ.
6. Cấm đọc TEST trong lúc tạo snapshot TRAIN và học BPE. Bằng chứng phải bao gồm quyền truy cập phân vùng TEST không được cấp cho tiến trình học, biên bản truy cập từ filesystem guard và negative test cố gắng đọc TEST nhưng bị từ chối. Không chỉ tin dòng `TEST_NOT_USED=true` do trainer in.

**Cổng FAIL/HOLD:** nếu TEST được đọc hoặc snapshot chứa nguồn chưa có quyền ⇒ FAIL; nếu không có trace quyền truy cập hoặc manifest chuẩn chưa khóa ⇒ HOLD; hai SHA khác nhau với đầu vào đã ghim ⇒ FAIL. F0 giả lập không đủ để khẳng định tái lập BPE với corpus thật.

## G04-05 — Ma trận quyền và bảo vệ riêng tư của nguồn

| Ca | Nguồn, bằng chứng và trạng thái | Quyết định bắt buộc |
|---|---|---|
| R01 | `admission=ALLOW`, SHA đúng, quyền học tokenizer rõ ràng, PII đã duyệt | Có thể xét tiếp ở cổng nguồn, **không** tự cho phép chạy |
| R02 | `PENDING`, `UNKNOWN`, `REJECT`, trường bắt buộc rỗng | `REJECT_OR_QUARANTINE` |
| R03 | `ALLOW` nhưng `raw_sha256` không khớp | `SOURCE_INTEGRITY_FAIL`, không tải thêm hoặc tự sửa |
| R04 | Giấy phép không cho huấn luyện/không rõ về tái sử dụng | `RIGHTS_HOLD`, không nhận TRAIN |
| R05 | `pii_status=PENDING` hay `pii_status=FAIL` | `PII_HOLD` hoặc `REJECT` |
| R06 | Giấy phép/nguồn bị thu hồi hoặc đến hạn hết hiệu lực | `RIGHTS_HOLD` cho lượt sau; giữ bằng chứng theo chính sách lưu trữ |
| R07 | 29 nhóm hợp lệ sau gom trùng | `INSUFFICIENT_GROUPS`, không tạo TEST |
| R08 | Nội dung F0 tự tạo, không có source manifest corpus | Chỉ dùng **thiết kế và oracle**, không coi là nguồn TRAIN thật |

**Ghi nhận chưa giải quyết:** chưa có một nguồn F1/F2 được duyệt cho P01, không tự chọn Wikimedia hay bất cứ nguồn internet nào. Việc có RAM/đĩa trống không cấp quyền thu thập tài liệu.

## G04-06 — Cổng tài nguyên cho toàn cây tiến trình (Process Tree)

- Ngưỡng **ứng viên**, chưa phải permit: `RSS/commit limit 4 GiB`, RAM khả dụng trước chạy `>=8 GiB`, D: trống `>=16 GiB`, D: sau dự phòng `>=12 GiB`, nguồn `<=64 MiB`, `<=2.000` tài liệu, tệp tạm+bằng chứng `<=2 GiB`, thời gian `<=1800` giây.
- Trên Windows, cần đặc tả có thể kiểm toán cho **Job Object** hoặc cơ chế tương đương bao phủ toàn bộ cây con; buộc tiến trình mới vào giới hạn **trước khi** cho phép bắt đầu công việc, không cho phép tiến trình con thoát (breakaway), xác định chính xác số đo `private bytes/commit` hay `working set/RSS`. Hai đại lượng này khác nhau, không được nhầm chúng rồi kết luận đạt 4 GiB.
- Phải ghi nhận PID, cây tiến trình, thời điểm quan sát, giới hạn đã cài, bộ đếm đo, trạng thái kết thúc, lỗi và biên bản. Nếu guard vắng, chỉ có số đo trước chạy hoặc không gắn được một tiến trình con ⇒ `HOLD_GUARD_NOT_ESTABLISHED`, không cho phép thực thi.
- Nếu vượt hoặc sắp vượt trần thời gian/RAM/đĩa, dừng toàn cây có kiểm soát, ghi `RESOURCE_LIMIT_STOP` và những tệp bằng chứng đã tạo hợp lệ; **không** tự chạy lại hoặc thay cấu hình. Khi biên bản chưa thể ghi an toàn thì kết luận `INCONCLUSIVE_EVIDENCE_FAILURE`, không PASS.
- Bắt buộc ca kiểm thử âm tính riêng: tiến trình vượt giới hạn RAM; tiến trình con cố thoát limit; ghi tệp vượt 2 GiB; hết 1800 giây; thiếu đĩa giữa chừng; bảo đảm không còn tiến trình con tồn dư và không chạm thư mục khác. Các ca âm tính chỉ được **đặc tả** tại D1, chưa được chạy.
- Không cho công cụ QA tự xóa dữ liệu gốc/worktree sau khi dừng. Mọi cleanup cần phê duyệt riêng.

**Giới hạn bằng chứng hiện có:** console Windows ngày 05/11/2026 đo `RAM_AVAILABLE_GIB=10.959`, `D_AVAILABLE_GIB=34.869` và `D_AFTER_PROPOSED_RESERVE_GIB=32.807`; chỉ cho phép `H05_RESOURCE_SNAPSHOT_PASS_CANDIDATE`, **không phải** `GUARD_QA_PASS`.

## G04-07 — Manifest và bảo toàn bằng chứng (Evidence Integrity)

**Đề xuất manifest `TTM_P01_EVIDENCE_V1`:**
- `operation_id` bất biến một lượt, `git_commit_sha`, `source_manifest_sha256`, `train_snapshot_sha256`, `config_sha256`, `fixture_spec_sha256`, `checker_source_sha256`, `tokenizer_source_sha256`, `merges_file_sha256` (khi có), `run_start_utc`, `run_end_utc`, `exit_code`, `final_status`, `resource_summary`.
- Mọi tệp phải có đường dẫn **tương đối, được phép, nằm trong** `D:\WORK\RESEARCH\TokenToModel-Lab`; từ chối `..`, ổ đĩa/UNC ngoài dự án, symlink/junction/reparse thoát root, tên tuyệt đối và tên trùng trỏ hai nội dung.
- Danh mục `file_sha256` phải xác minh **byte thực tế** từ một trình đọc độc lập với generator; việc generator tự ghi một chuỗi SHA “đúng” không phải chứng cứ. Mã nguồn checker được ghim bởi chủ thể không phải chính checker khi chạy.
- Biên bản hoàn tất dùng đường dẫn tên không trùng và chế độ **create-new**; không ghi đè, không sửa hồi tố. Nếu trùng `operation_id` hoặc tệp đã tồn tại thì fail-closed, không đổi tên ID để chạy tiếp. Tách biên bản lỗi hạ tầng khỏi kết quả khoa học.
- Đọc lại sau ghi: danh mục tệp, số byte, mã SHA và manifest phải khớp. Sai hash, thiếu file hoặc mất phần log ⇒ `EVIDENCE_INTEGRITY_FAIL` hoặc `INCONCLUSIVE`; không dùng log tự khai `PASS` để thay bằng chứng nguồn.
- Các bài kiểm tra âm tính tương lai: tệp bị đổi một byte; tệp mất; path vượt root; symlink; receipt bị ghi đè; token đặc biệt không hợp lệ; `operation_id` trùng; thay checker/oracle sau khóa.

**Dữ liệu thật/PII:** không commit corpus, raw text riêng tư hoặc bí mật vào GitHub; chỉ lưu manifest/hash và kết quả đã loại bỏ thông tin nhạy cảm theo quyền nguồn.

## Tóm tắt G04-04..07

`G04_04_DESIGN=SPECIFIED_SNAPSHOT_FORMAT_FINAL_LOCK_PENDING`  
`G04_05_DESIGN=SPECIFIED_SOURCE_ADMISSION_HOLD`  
`G04_06_DESIGN=SPECIFIED_RUNTIME_GUARD_QA_HOLD`  
`G04_07_DESIGN=SPECIFIED_EVIDENCE_FORMAT_FINAL_LOCK_PENDING`  
`P01_D1_LOCK=NOT_GRANTED`; `P01_I0_PERMIT=NOT_GRANTED`; `P01_DATA_DOWNLOAD=FORBIDDEN`; `P00_CLEANUP=FORBIDDEN`.
