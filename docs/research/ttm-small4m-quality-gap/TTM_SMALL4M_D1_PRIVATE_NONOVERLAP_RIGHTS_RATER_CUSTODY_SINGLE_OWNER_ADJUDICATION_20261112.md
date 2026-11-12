# TTM-Small-4M D1 — Phân xử duy nhất về không trùng nguồn, quyền dữ liệu và người chấm

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_PRIVATE_NONOVERLAP_RIGHTS_RATER_CUSTODY_SINGLE_OWNER_ADJUDICATION`  
**Nhánh:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Phương thức:** Kiểm toán nguồn và trạng thái, **chỉ đọc** (read-only); không chạy science.  
**Phán quyết:** **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`**.

## 1. Nguồn đối chiếu

Đã đọc hợp đồng D1 đóng băng tại `docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_FIXED_CHECKPOINT_FACT_CONDITIONING_VS_DECODING_FROZEN_DESIGN_20261111.md`, Git blob `a1ffb8ccbdc35ef73ec68c7e7f534aa15a2f4dc2`.

Đã kiểm tra biên nhận chấp nhận postflight ở GitHub blob `7371146306fe29cd68af3255f162ba3edfc0d2de`, cùng bản receipt riêng tư trên Windows ở `_tmp/TTM_SMALL4M_D1_V2_VERSIONED_PRIVATE_REKEY_STATIC_RECEIPT_20261111.json`. Hai nguồn thống nhất các mã sau:

| Hạng mục | SHA-256 |
| --- | --- |
| DEV V2 thô | `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8` |
| DEV V2 chuẩn hóa LF | `1553d186eb55699506b6b920153d5c7af7f0ad26a186e1d58ffef0d1e7b4eb2e` |
| Mẫu chấm mù V2 | `ae85dddbb12b299f2f9252ad3b1df426eb7bd0af6ae52fbb73b5825c646833d4` |

Đã đối chiếu metadata private V2: `source_rights=AI_AUTHORED_NEW_CONTENT_OWNER_FINAL_ATTESTATION_PENDING`, `historical_overlap=PUBLIC_TWO_FILES_SCOPED_PRIVATE_FRESH16_AC_Q1Q2_TEST_NOT_CERTIFIED`. Mẫu người chấm ghi `TEMPLATE_ONLY_RATER_UNASSIGNED_NO_OUTPUTS`, không có bản chấm thực. Giữ nguyên 16 gia đình, 128 prompt, 64 đối chứng x0 và 512 vị trí chấm mù.

GitHub default-branch search với các chuỗi `TTM_SMALL4M_D1_PRIVATE_NONOVERLAP`, `D1_OWNER_RIGHTS`, `D1_RATER_INDEPENDENCE`, `D1_BLIND_CUSTODY` không tìm ra biên nhận mới. **Đây không phải chứng minh tuyệt đối không tồn tại chứng cứ ở các nhánh khác hoặc thư mục chưa đọc**. Không truy cập nội dung TEST, Q1Q2 hoặc mapping private, không tải bản chấm mù lên GitHub.

## 2. Cổng tổng hợp và kết quả

| Cổng | Phán quyết | Thiếu bằng chứng gì |
| --- | --- | --- |
| Kỹ thuật V2 | **PASS_SCOPED** | Không cần tái khóa/QA lại |
| Trùng lặp 2 nguồn lịch sử công khai | **PASS_SCOPED** | Kiểm tra này không bao phủ dữ liệu private và tương đồng ngữ nghĩa toàn cục |
| Không trùng FRESH12/FRESH16/CF1/AC FINAL24 cùng TEST/Q1Q2 | **HOLD** | Chứng nhận từ người được phép truy cập nguồn riêng tư hoặc bằng chứng fingerprint đã có, không mở lại TEST/Q1Q2 trong thao tác này |
| Quyền dữ liệu | **HOLD** | Chủ sở hữu xác nhận và ký nhận xuất xứ, phạm vi quyền và việc dùng nội dung mới cho đánh giá |
| Người chấm và bảo quản nhãn | **HOLD** | Chỉ định người chấm mù độc lập, xác nhận không tham gia sinh dữ liệu/chạy mô hình, không truy cập seed/mapping, có người bảo quản mapping và quy tắc khóa điểm trước khi giải mù |

**Lưu ý phương pháp:** SHA-256 chỉ chứng minh tính nhất quán byte được chốt; SHA khác nhau không phải bằng chứng hai prompt khác nghĩa. Hai nguồn lịch sử công khai được kiểm tra ở phạm vi cảnh/từ ghép, không đủ loại trừ trùng lặp ngữ nghĩa với dữ liệu đã tiêu thụ. Không đổi ngưỡng khoa học D1, không xem 512 outputs là 512 mẫu gia đình độc lập.

## 3. Một quyết định cho toàn batch

`D1_V2_TECHNICAL=PASS_SCOPED` nhưng `PRIVATE_NONOVERLAP=NOT_CERTIFIED`, `OWNER_RIGHTS=NOT_ATTESTED`, `RATER_INDEPENDENCE_AND_CUSTODY=NOT_ATTESTED`.

**Owner adjudication: `HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`.** Đây là HOLD trước thực thi (pre-execution hold), **không** phải FAIL khoa học. Chưa phát 512 đầu ra, chưa chấm 384 cặp candidate, chưa huấn luyện; không cấp quyền inference/GPU/CPU. Trạng thái khoa học `NOT_EXECUTED`.

Hợp đồng thiết kế D1 `GO_DESIGN_FROZEN` vẫn giữ nguyên, checkpoint bước 1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` không đổi. `lineage.md` Git blob `9110d101601e6ebfb64d9804f3704a90cb284420` vẫn kết thúc tại L0015, `main` ở `5d52e32f20021e36f08f284ef9864d3ba36dbead`. Không merge, không mở TEST/Q1Q2, không chạy lại FRESH16.

## 4. Bước thực hiện tiếp theo

**`TTM_SMALL4M_D1_ONE_PACKET_SIGNED_NONOVERLAP_RIGHTS_INDEPENDENT_RATER_CUSTODY_OWNER_RELEASE`**.

Chỉ có **một gói chứng thực hợp nhất** cho ba cổng, không phải ba micro-permit. Gói này phải bao gồm: (i) chứng thực không trùng các nguồn private theo phạm vi được phép và nêu rõ tập nào **chưa chứng thực**; (ii) chữ ký xác nhận quyền dữ liệu của chủ dự án; (iii) văn bản người chấm độc lập chấp nhận vai trò, quyền bảo quản mapping/seed và cơ chế khóa SHA bản chấm trước khi giải mù. Nếu thiếu bất kỳ mục nào thì vẫn **HOLD**, không tái khóa V2 hay điều chỉnh protocol. Khi và chỉ khi đầy đủ bằng chứng mới phân xử GO/HOLD trong một lần cho 512 outputs, **không chạy science trong quá trình phân xử**.

Gói không được chứa secret, seed, prompt private, mapping, raw score hoặc các tệp TEST/Q1Q2 trên GitHub công khai.
