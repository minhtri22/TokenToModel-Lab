# Closure — PDF11 Vietnamese fidelity remediation and independent QA gate

**Ngày:** 16/11/2026

**Operation:** `DIVE_INTO_LLMS_11PDF_VI_FIDELITY_REMEDIATION_AND_INDEPENDENT_LANGUAGE_QA_ONEPACK`

**Nguồn:** [Lordog/dive-into-llms @ f84c04268794ef94f8949808bbc14ab8636763a0](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0).

## Đầu ra và chứng cứ GitHub

- [Workflow GitHub Actions #43857166802](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43857166802): **SUCCESS**.
- [Commit đầu ra đã ký nhận tại GitHub](https://github.com/minhtri22/TokenToModel-Lab/commit/13f2def0467cf06d456056fbd9240c953da8f5a0): 11 PDF song ngữ (495 trang), 11 Markdown chú giải sửa đổi, công cụ tạo, công cụ QA tách biệt, manifest và receipts.
- [REMEDIATION_MANIFEST_20261116.json](REMEDIATION_MANIFEST_20261116.json): đúng 11 đầu ra và SHA-256 sau sửa; không thay thế bằng SHA-256 của ZIP trước sửa.
- [REMEDIATION_STATIC_QA_20261116.json](REMEDIATION_STATIC_QA_20261116.json): `static_qa=PASS`, `total_pages=495`, `errors=[]`, `control_or_replacement_pages=[]`, `missing_note_text_pages=[]`, `upper_source_text_differences=[]`, `slide_visual_samples=33`, `slide_visual_mae_max=0`.
- Thay thế phần tiếng Việt với font DejaVu Sans hỗ trợ Unicode và ký hiệu; cỡ chữ/bố cục được chỉnh lại. Chương trình dựng/kiểm tra: [generator](remediation/remediate_pdf11.py), [separate checker](remediation/github_qa.py); [7 đoạn mở rộng](remediation/overrides.json).

## Phân xử F01–F03

| Finding/gate | Kết luận hiện tại | Bằng chứng / giới hạn |
|---|---|---|
| Source pin và phạm vi nhánh | PASS | GitHub Actions + commit source docs only |
| F01 — Unicode/ký hiệu lớp Việt | **PASS_STATIC** | 53 trang lỗi ở bản trước; 0/495 trang còn ký tự điều khiển hoặc ký tự thay thế theo chương trình QA |
| F03 — Bố cục | **PASS_STATIC_SAMPLE_33** | 495 trang được dựng lại, 33 ảnh kiểm tra phần slide gốc có MAE=0; chưa có QA đọc hiểu từng trang bởi chuyên gia |
| F02 — Độ trung thành/nguyên văn | **HOLD_FULL_LITERAL_TRANSLATION** | Đã sửa và mở rộng 7 trang (02:47, 02:57, 04:14, 05:43, 08:45, 10:28, 11:17); một số bảng, hình, đoạn dài vẫn chỉ được diễn giải |
| QA kỹ thuật tách khỏi trình tạo | **PASS** | `github_qa.py` được thi hành trong CI và có receipt |
| Independent linguistic QA (người/agent thứ hai) | **NOT_EXECUTED** | Chạy checker khác không phải thẩm định ngôn ngữ độc lập |
| Final release gate | **HOLD_FIDELITY** | Không phong PASS/FULL_TRANSLATION |

## Bất biến

- Chỉ nhánh `docs/learningbooks-dive-into-llms-vi-20261116`, không merge `main`, không thay `lineage.md`, checkpoints hoặc nghiên cứu khoa học.
- Không thực thi model; không giả định kết quả TTM/CLDP.
- Bản PDF là **tài liệu học tập song ngữ ứng viên**, chưa phải dịch nguyên văn hoàn chỉnh; quyền công bố bản dịch không được suy ra từ việc lưu GitHub.

**Bước duy nhất còn mở:** QA nội dung độc lập theo từng phần/trang đối với bảng, hình, công thức, đoạn gốc; ghi cặp chứng cứ source vs target và phân xử sau một lượt tích hợp. Không chuyển `HOLD` thành `PASS_FIDELITY` trước khi đủ chứng cứ.
