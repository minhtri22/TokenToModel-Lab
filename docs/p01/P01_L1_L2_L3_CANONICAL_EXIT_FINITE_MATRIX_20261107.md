# TTM P01 — Đối chiếu tiêu chí đóng L1/L2/L3 và kế hoạch QA gộp hữu hạn

**Ngày:** 07/11/2026  
**Mã công việc:** `TTM_P01_L1_L2_L3_CANONICAL_EXIT_GAP_REVIEW_AND_SINGLE_INTEGRATED_QA_PLAN`  
**Kho:** `https://github.com/minhtri22/TokenToModel-Lab`  
**Nhánh biên bản:** `audit/p01-l1-native-security-critical-fix-20261106`  
**HEAD khoa học gốc bảo toàn:** `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.

## 1. Căn cứ không đổi

Đã đối chiếu `docs/PHASE_PLAN.md`, `docs/GOVERNANCE.md`, `docs/p01/P01_LEAN_EXECUTION_PLAN_AND_REMAINING_SCOPE_REVIEW_20261106.md`, `P01_DESIGN_PREREGISTRATION.md`, `P01_METRICS_AND_QA_GATES.md`, `P01_D1_H01_DETERMINISTIC_BPE_SPEC.md`, `P01_D1_H03_DEDUP_SPLIT_SPEC.md`, `P01_D1_H02_H05_SOURCE_RESOURCE_GATE.md` và `P01_DATA_AND_SPLIT_PLAN.md`.

- **P01**: bộ tách token (Tokenizer) B0/B1, nguồn dữ liệu, quyền, chống rò rỉ, tái lập và QA.
- **P02**: lõi Transformer, không phải huấn luyện mô hình GPT.
- **P03**: vòng huấn luyện GPT.
- **P04**: checkpoint/đánh giá, tập giữ riêng.
- Không thay P00 (vocab 256), không nạp B1 ID ≥256 trực tiếp vào P00, không dùng TEST để sửa cấu hình/thuật toán.
- 10 F0 đã PASS được **tái sử dụng**, không chạy lại; toàn bộ receipt/marker PASS và FAIL của S1 giữ nguyên, S1 native vẫn FAIL. Không cấp native permit mới.
- `lineage.md` không bị sửa trong QA kỹ thuật này; khoa học/giấy phép/merge là quyết định riêng.

## 2. Bằng chứng QA mới đã thực thi

Đã chạy trên môi trường ngoài máy Windows một batch mới sử dụng **đúng 4 tệp Python có Git blob trùng GitHub** từ nhánh `implementation/p01-i0a-s-f0-static-20261106`:

| Bộ kiểm tra | PASS/Total | Chứng minh được | Không chứng minh |
|---|---:|---|---|
| K1/K2 bổ sung trên nguồn sản phẩm nguyên bản | **14/14** | BPE overlap/serialization/invalid IDs, khóa canonical, ngưỡng near-duplicate, `assign_splits` 29/30 nhóm, phân 24/3/3, từ chối F1 không phép | Học BPE trên F1, 2 tiến trình TRAIN, 30 *tài liệu* qua classifier |
| Bộ kiểm toán chia nhóm độc lập | **3/3** | Oracle split 30 nhóm, reject 29 nhóm, phát hiện 3 loại giao cắt qua biến thể âm | Không nhập dữ liệu vào pipeline sản phẩm; không chứng nhận Windows guard |
| 10 kiểm tra F0 đã khóa | **10/10 cũ** | Kết quả offhost F0 nguyên bản | Không coi là P01 closure hoặc E0 |

**SHA-256 biên bản 14/14:** `cc694293579b268a953e7b9395205ac42a62df8206ef56501c3a947659c1402d`.  
**SHA-256 biên bản 3/3:** `7582467ea4fc6edba97cf59491d6bbe4d1c402ea6451f3dad0930c802d87cb74`.  
**Gói tái lập offhost:** `TTM_P01_K1_K2_OFFHOST_REPRODUCIBLE_QA_BUNDLE_20261107.zip`, SHA-256 `59bc272e45361d708d2bb83d88d08c6cf22d92033eced02b14ef875ca7e2ed74`; gói tồn tại dưới dạng tệp đính kèm cuộc trò chuyện, **chưa upload lên GitHub**. Biên bản tổng hợp ở `artifacts/qa/p01/P01_K1_K2_OFFHOST_ADDITIVE_AND_CANONICAL_EXIT_GAP_20261107.json`.

**Giới hạn trung thực:** 30 nhóm là **30 mã băm ID tổng hợp**, không phải 30 tài liệu đã có quyền; `classify_f0_documents` từ chối mọi tài liệu không thuộc bộ F0 đã khóa. Bộ audit raw/canonical trên các bản ghi tổng hợp **không** phải cổng chống rò rỉ được tích hợp trong pipeline F1. Chuỗi A≈B≈C được kiểm tra ở mức cặp, chưa phải chứng minh union-find ba tài liệu không tương đương trực tiếp. Không được mở rộng `F0_LITERAL_SHA256` chỉ để biến kiểm thử thành PASS.

## 3. Bảng cổng đóng P01 hữu hạn

| Cổng | Điều kiện bắt buộc theo hợp đồng | Bằng chứng hiện có | Trạng thái / việc còn thiếu |
|---|---|---|---|
| **K1 / L1: B0–B1** | Byte/Text round-trip 100%; strict UTF-8; deterministic merges, golden byte, invalid ID và ranh giới tài liệu | F0 10/10 reused; 14/14 additive có overlap, serialize và âm tính | **PARTIAL_PASS_OFFHOST**: chưa đủ oracle tie/cross-document độc lập và kết luận tích hợp cuối |
| **K2 / L1: H03 chống trùng/split** | Trùng raw/canonical/near, hợp tập bắc cầu (Union-find), 30+ nhóm, split seed 20261105, 24/3/3 khi N=30, zero group/raw/canonical overlap, reject 29 nhóm | `assign_splits` trên 30 group ID và auditor âm tính PASS; near-duplicate boundary PASS | **PARTIAL_PASS_OFFHOST**: classifier transitivity chưa đủ, chưa có pipeline 30 tài liệu hoặc tuyến fixture tách biệt được thẩm định |
| **K3 / L2: Quyền dữ liệu và PII** | Ít nhất 1 F1 snapshot có manifest quyền và `admission_decision=ALLOW`, đủ 30 nhóm sau dedup; nguồn không đủ quyền bị từ chối | `P01_D1_SOURCE_RIGHTS_READONLY_REVIEW_20261105.md` xác nhận chưa có nguồn ALLOW; `source_scope_guard` hiện từ chối F1 | **HOLD_SOURCE_RIGHTS**: không có hồ sơ F1 ALLOW được xác minh trong các nhánh repo đã rà; không suy ra máy người dùng không có file |
| **K4 / L2: An toàn runtime** | Tuyến E0 có kiểm soát tài nguyên/nguồn/ghi; nếu E0 sử dụng tuyến Windows C09 thì W01–W12 native và bảo vệ liên quan phải chứng minh; không suy PASS từ mock | S1 đời đầu và kế nhiệm có FAIL đã khóa, service SCM giữ nguyên | **HOLD_ROUTE_DECISION / NATIVE_NOT_QUALIFIED**: quyết định rõ tuyến E0; không miễn an toàn nếu tuyến đó có nguy cơ |
| **K5 / L3: E0 và đóng P01** | F1 TRAIN-only BPE, 2 tiến trình sạch cùng SHA merges, byte round-trip 100%, TEST seal, metrics B0/B1, provenance, QA độc lập, PR/merge đúng cổng | Đường `learn_merges_f0_qa0_only` chỉ nhận byte F0 pinned, chưa phải F1 entrypoint | **NOT_EXECUTED**: chờ L1/L2 và tiền đăng ký/giấy phép E0 hợp lệ |

**Phán quyết chung:** `P01=OPEN`; `P02=NOT_OPENED`. QA tổng hợp mới không cho phép `E0`, không giải quyết tự động giấy phép F1 hoặc lỗi S1.

## 4. Việc còn lại — đúng 3 gói, không phát sinh chuỗi vi mô

**Gói A — Một QA tích hợp cuối L1 (K1/K2).** Tái sử dụng 10 F0 và các QA mới 14/14, 3/3. Bổ sung oracle tie/cross-document và xác minh transitivity của **chính** `classify_f0_documents` trên miền F0 có phép. Nếu cần 30 tài liệu synthetic để kiểm full classify→split thì xây **một tuyến fixture QA được review riêng** (không thay F0 pinned, không giả danh F1). Trong cùng một batch, kiểm kết quả 30 nhóm, zero group/raw/canonical overlaps, negative leak, thực thi nguồn nguyên bản trên Windows nếu môi trường đủ điều kiện, QA độc lập cuối và một phán quyết `L1_PASS_SCOPED` / `L1_FAIL` / `L1_HOLD`. Không tạo permit riêng cho từng SHA/AST.

**Gói B — Một quyết định nguồn F1 và tuyến thực thi L2.** Chủ dự án chọn ít nhất một snapshot F1 thực sự sở hữu hoặc được phép sử dụng; không dùng dữ liệu từ dự án khác, email hay web theo mặc định. Manifest tối thiểu:
`source_id`, `source_snapshot_id`, `original_location`, `owner_or_author`, `license_id`, `license_evidence_uri`, `permitted_uses` (tokenizer training, derived works, redistribution nếu cần), `source_sha256`, `byte_count`, `document_count`, `distinct_group_count`, `encoding`, `pii_status`, `copyright_status`, `reviewer`, `rights_reviewed_at`, `admission_decision`. Chỉ `ALLOW` khi đủ chứng cứ và kiểm PII; thiếu ⇒ `HOLD_SOURCE_RIGHTS`. Phân định một lần tuyến E0 Windows/khác và kiểm bảo vệ bắt buộc đúng tuyến, không biến S1 thành cổng tùy tiện cho mọi trường hợp.

**Gói C — Một E0 BPE TRAIN-only + phán quyết P01.** Chỉ sau A/B PASS và khóa snapshot/split/seed/TEST/quota. Không học từ VALIDATION/TEST; hai tiến trình sạch tạo cùng byte merges và SHA; báo round-trip, compression, token/byte, tài nguyên và bằng chứng. Checker độc lập kết luận PASS/FAIL/INCONCLUSIVE. Nếu đủ tất cả cổng đã duyệt mới xét hợp nhất và mở P02 qua PR riêng.

## 5. Ranh giới và quyết định cuối lượt rà soát

- `L1=PARTIAL_PASS_OFFHOST`; `L2=HOLD_SOURCE_RIGHTS_AND_ROUTE`; `L3=NOT_EXECUTED`.
- Chưa mở P02, không tải hay huấn luyện BPE trên F1, không chạy GPT, không truy cập TEST, không mở native S1 mới.
- Không thay đổi source P00, 10 kết quả F0, HEAD gốc, `lineage.md`, marker, receipt FAIL/PASS hay P00–P12.
- **Bước thực hiện tiếp theo:** `TTM_P01_L1_FINAL_SINGLE_INTEGRATED_QA_AND_F1_MANIFEST_OWNER_DECISION`. Tiến hành một QA L1 còn thiếu theo đúng miền F0/synthetic đã được duyệt; song song xác nhận một F1 snapshot có quyền và chọn tuyến runtime E0. Nếu F1 chưa có, chốt HOLD có lý do, không sinh thêm QA S1 theo vòng lặp.
