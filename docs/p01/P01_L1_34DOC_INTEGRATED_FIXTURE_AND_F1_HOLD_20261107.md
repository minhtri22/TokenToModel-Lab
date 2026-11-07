# TTM P01 — Tích hợp L1 tổng hợp và quyết định F1

Ngày 07/11/2026. Nhánh: audit/p01-l1-integrated-34doc-f1-hold-20261107.
Mốc trước: cae0ea80648954d218231ba87178307ba825dc4b.
Mốc khoa học gốc bảo toàn: f2e333df2f9ca24a8e483507c3cfc386ad9c76f0.

## QA tích hợp mới

- 7/7 PASS ngoài máy Windows trên bốn tệp mã nguồn sản phẩm đối chiếu SHA-256 chính xác.
- BPE phá hòa và không đếm cặp vượt ranh giới tài liệu; chỉ dùng byte F0 đã ghim, không lặp 10 QA F0.
- Fixture tổng hợp 34 tài liệu: nhóm bắc cầu A≈B≈C nhưng A≉C, một nhóm có raw duplicate và canonical duplicate, cùng 28 nhóm đơn: 30 nhóm độc lập.
- Thực thi classifier và assign_splits bằng một test-only scoped mock đúng hàm admission đã nhập vào classifier. Không sửa source_scope_guard.py hoặc whitelist F0.
- Chia theo nhóm TRAIN 24, VALIDATION 3, TEST 3; giao cắt group/raw/canonical SHA-256 đều 0.
- Đảo thứ tự giữ nguyên nhãn; tiêm rò rỉ vào nhãn của bản raw duplicate được kiểm toán phát hiện trên cả ba loại; 29 nhóm và PII chưa review bị chặn; source guard không patch tiếp tục từ chối fixture.

Biên bản: artifacts/qa/p01/P01_L1_34DOC_INTEGRATED_FIXTURE_OFFHOST_20261107.json.
Mã kiểm thử: qa/p01/test_l1_integrated_fixture_only.py.
Lệnh kiểm thử riêng trên checkout đã thẩm định: python -B -m unittest qa.p01.test_l1_integrated_fixture_only -v.

Kết quả giới hạn: PASS_SCOPED_FIXTURE_ALGORITHM, không phải kiểm thử production admission trên F1, không phải QA Windows native hoặc chấp thuận E0. Bộ kiểm thử dùng mock có kiểm soát và không phải QA của bên thứ ba.

## F1: HOLD vì không có snapshot được phê duyệt

Đã rà toàn bộ cây GitHub tại commit cae0ea8... (337 đường dẫn). Không thấy manifest F1 được chấp nhận với admission_decision=ALLOW. Điều này không chứng minh máy Windows không có văn bản hợp lệ.

Chưa có source_id, source_snapshot_id, original_location, owner_or_author, license_id, license_evidence_uri, permitted_uses, source_sha256, byte_count, document_count, distinct_group_count, encoding, pii_status, copyright_status, rights_reviewed_at, reviewer, và admission_decision=ALLOW cho một snapshot F1 thật.

Giữ F1_SOURCE_SELECTED=NO; F1_ADMISSION=HOLD_SOURCE_RIGHTS; F1_DOWNLOAD=NO. Không tự lấy tài liệu email, repo khác, internet, hay suy đoán quyền từ chữ 'public'.

Chủ dự án cần chỉ định một corpus F1 có quyền; sau đó rà soát thực tế giấy phép, SHA, PII và tối thiểu 30 nhóm sau dedup trước quyết định ALLOW. Runtime E0 cần chọn đúng tuyến an toàn; S1 FAIL chỉ là cổng bắt buộc nếu tuyến thực tế sử dụng cơ chế đó.

## Ma trận ngắn

| Cổng | Phán quyết |
|---|---|
| K1 B0/B1 | PASS kỹ thuật scoped; Windows QA cuối PENDING |
| K2 dedup/split | PASS tích hợp thuật toán trên fixture; F1 pipeline chưa được kiểm |
| K3 F1 | HOLD_SOURCE_RIGHTS |
| K4 runtime | HOLD_ROUTE_DECISION / NATIVE_NOT_QUALIFIED |
| K5 E0 và đóng P01 | NOT_EXECUTED / P01 OPEN |

Giữ P00, 10 F0, HEAD gốc, lineage.md, marker/receipt PASS/FAIL, SCM và thứ tự P00–P12. P02 vẫn NOT_OPENED.

Bước tiếp theo: một batch readback QA L1 trên Windows đúng mã commit; một quyết định F1 snapshot của chủ dự án; sau K1–K4 đạt mới cho phép E0 TRAIN-only và phán quyết đóng P01.
