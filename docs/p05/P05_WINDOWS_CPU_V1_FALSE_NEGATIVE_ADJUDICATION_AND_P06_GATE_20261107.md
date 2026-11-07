# TTM P05 — Đối chiếu độc lập báo cáo QA Windows; bảo toàn FAIL V1 và phán quyết scoped PASS

Ngày 07/11/2026. [PR #9](https://github.com/minhtri22/TokenToModel-Lab/pull/9), HEAD mã P05 được Windows kiểm thử `9afbdcdbd5c39da0ae5d92da327498cb3ad866d9`; base P04 `88bde037705607730cfc24e36875aa865d3a380c`.

## Kết luận có phân tách rõ ràng

- Bộ chạy PowerShell V1 **đã ghi** `FAIL_OR_INCONCLUSIVE` / `INDEPENDENT_QA_REPORT_SCOPE_OR_STATUS_MISMATCH`; bản ghi này **được giữ nguyên**, tuyệt đối không sửa thành PASS.
- Bằng chứng gốc của cùng một lượt Windows: 6/6 unittest PASS, independent Python **exit=0**, JSON `status=PASS`, bốn phép kiểm tra đều `true`. Tất cả điều kiện phạm vi và số đo đã được tính lại **ngoài** biểu thức đếm của PowerShell V1 và đều khớp.
- **Phán quyết độc lập:** `PASS_SCOPED_CPU_WITH_RUNNER_V1_FALSE_NEGATIVE` cho thuật toán Dense KV trong phạm vi synthetic CPU, kèm chú thích lỗi ở bộ phán quyết kỹ thuật V1. **Không có lượt QA Windows mới, không chạy lại P01–P04/E0.**

## Đường dẫn và SHA

- Receipt nguyên gốc `evidence/p05/TTM_P05_WINDOWS_CPU_QA_20261107T161218Z_P34804.json`, SHA-256 `b8dc243e194e121bda7bd1cd164e375e535239978a2e60b3362230dae77127fb`; Git blob chính xác `9a18fbfb37e830c6d803e822280f114d5d39e3c3`. Nội dung FAIL, `independent_tests.pass=false/count=0`, cùng cleanup PASS được bảo toàn.
- Script chạy V1 SHA-256 `547a22e11cd59b01ace78cf0d8a20e534d8faeec4e65f53550b4323a5f7fad71`, Git blob `3b4da49ef341db08eac3e4feb5619df65ef7c608`, lưu dưới `scripts/p05/`.
- Log unittest nguyên gốc `evidence/p05/TTM_P05_WINDOWS_CPU_QA_20261107T161218Z_P34804.unittest.log`, SHA theo receipt `b41f6618a9e6fa5fa36323e58b0f245b7b6ffc3e923a5189fda76abd5ba7712b`: `EXIT=0`, sáu test `ok`, `Ran 6 tests in 0.083s`, `OK`.
- Log độc lập `evidence/p05/TTM_P05_WINDOWS_CPU_QA_20261107T161218Z_P34804.independent.log`, SHA theo receipt `91363e4149628a9ceaa6939bcfb81b69b621b85cbc8ae805b4612eb5e3790dc8`: `EXIT=0`, `status=PASS`, torch `2.11.0+cpu`.
- Đã đọc trực tiếp log Windows; **chưa tái băm độc lập hai tệp log nhị phân**. GitHub lưu receipt exact-byte và biên bản phán quyết, không tự xưng lưu hai log nguyên byte.

## 4 phép đối chiếu độc lập PASS

1. `explicit_sdpa_incremental_oracle`: logits Dense KV khớp Attention tham chiếu PyTorch.
2. `interleaved_dense_vs_uncached`: các request xen kẽ khớp mô hình không cache và không rò trạng thái.
3. `independent_kv_byte_accounting`: bộ nhớ theo số byte đúng, giải phóng sau sử dụng.
4. `cpu_wall_time_measured_no_speedup_claim`: đo thời gian CPU, **không** tuyên bố tăng tốc.

JSON có đúng bốn tên trên, tất cả `true`, `P01_TEST=NOT_READ`, `P03_TRAINING=NOT_EXECUTED`, `no_real_corpus=true`.

Số đo: chiều dài 6, hai lần lặp; `allocated_kv_bytes=65536`, `logical_kv_bytes=6144`; dense CPU `[6.5546,6.3465]` ms, đường tính lại `[5.3252,5.6924]` ms. Mẫu rất nhỏ, **không đủ chứng minh cải thiện hiệu năng**.

## Vấn đề trong công cụ PS5.1

Trong V1, dòng 208–210 chặn tại biểu thức `$report.checks.PSObject.Properties.Count -ne 4`, cùng các điều kiện dữ liệu khác. Khi đọc lại báo cáo JSON trực tiếp, toàn bộ điều kiện dữ liệu và đo lường đều đúng, nên biểu thức đếm thuộc tính là nghi phạm còn lại. **Giá trị thực sự mà PowerShell 5.1 trả về cho `PSObject.Properties.Count` chưa được đo ở lần chạy**, vì vậy không tuyên bố đã tái hiện nguyên nhân đến từng giá trị runtime.

Đề nghị sửa **chỉ công cụ QA cho lần sử dụng về sau**: lấy `@($report.checks.PSObject.Properties | ForEach-Object { $_.Name })`, kiểm tra `.Count -eq 4`, tập tên chính xác và bốn giá trị `true`. Không đổi nguồn `src/p05`, `tests/p05`, `tools/p05`, không rerun để thay biên bản FAIL V1.

## Phạm vi phán quyết

`P05_TECHNICAL_EXIT=PASS_SCOPED_CPU_WITH_RUNNER_FALSE_NEGATIVE`. Bộ nhớ KV CPU Dense hoạt động đúng theo các bài synthetic. Không có bằng chứng lợi ích hiệu năng, tính tổng quát trên workload thực, GPU hoặc dữ liệu F1. Không mở P06 trước khi PR #9 merge. Các phase P01–P04, `lineage.md` và E0 giữ nguyên.

Bước tiếp theo: rà soát exact diff, receipt và HEAD, hợp nhất PR #9 khi GitHub báo clean; sau đó mở nhánh P06 từ đúng commit `main` sau merge.
