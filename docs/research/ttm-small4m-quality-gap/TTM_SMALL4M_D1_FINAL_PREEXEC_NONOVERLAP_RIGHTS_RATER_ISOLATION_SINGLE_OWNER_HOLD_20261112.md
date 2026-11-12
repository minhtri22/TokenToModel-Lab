# TTM-Small-4M D1 — Kiểm toán cuối trước thực thi và quyết định owner GO/HOLD toàn batch

**Ngày:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_FINAL_PREEXEC_NONOVERLAP_RIGHTS_AND_RATER_CONTEXT_ISOLATION_SINGLE_OWNER_GO_HOLD`  
**Nhánh:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Phương thức:** Kiểm tra nguồn, biên nhận, quyền và quy trình chấm (source-only/read-only), **không thực thi khoa học**.  
**Quyết định duy nhất:** **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`**.

## 1. Mốc dữ liệu và khoa học đã khóa

- D1 V2 private gói dữ liệu thô SHA-256 `f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8`; nội dung LF SHA-256 `1553d186eb55699506b6b920153d5c7af7f0ad26a186e1d58ffef0d1e7b4eb2e`.
- Mẫu chấm mù riêng SHA-256 `ae85dddbb12b299f2f9252ad3b1df426eb7bd0af6ae52fbb73b5825c646833d4`. V2: 16 family, 128 DEV prompt, 64 neutral prior, 512 vị trí blind future outputs. Chưa có một văn bản sinh thực tế nào được chấm.
- Hợp đồng D1 đóng băng: Git blob `a1ffb8ccbdc35ef73ec68c7e7f534aa15a2f4dc2`; checkpoint step1024 SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Người chấm ChatGPT ở lần handoff trước đã báo `RATER_PREEXEC_READY_SCOPED`, 0/512 văn bản, nhưng cảnh báo đã từng có ngữ cảnh TTM. Không coi receipt đó là xác nhận phiên chấm độc lập.

## 2. Kiểm tra không trùng dữ liệu đã thực hiện

**Nguồn public:** Lấy 28 prompt được phép công khai Q1/FRESH12 từ `TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json` (blob `6b35ec8ae377a9dbdb778766756a32e8ad4bcbc8`); và 16 prompt thiết kế FRESH chưa từng thực thi từ `TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json` (blob `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`). Sàng lọc theo tập từ vựng content words với stopword list và Jaccard trên 16 family core: không có best-match vượt 0,18, maximum best-match 0,167. Đây là **ngưỡng sàng lọc hậu nghiệm**, không phải ngưỡng prereg khoa học.

**Nguồn private đã tiêu thụ và được phép kiểm tra:** `_tmp/ttm_fresh16_v2_e0_20261111/S1_BLIND_PACKET_PRIVATE.json`, biên nhận source SHA-256 `2dc1fd7cda1262168cbdca4ca0773327e4153642c39a9981f3462dddad9aaccb`. Tệp gồm 32 records và 16 prompt duy nhất; chỉ trường `prompt_text` được đưa vào so sánh. Tệp JSON có cả các trường generated_text nhưng không dùng chúng; **không đọc** bản đồ giải mù hoặc tệp điểm riêng. Mỗi family core D1 gồm `scene`, `fact_A`, `fact_B`, `continuation_A/B`. Thực hiện 16×16 = **256 so sánh**:

| Chỉ số | Kết quả |
| --- | ---: |
| Trùng nguyên văn giữa family core và prior prompt | 0 |
| Trùng chuỗi 5 từ liền kề | 0 |
| Jaccard từ vựng cao nhất | 0,133 |
| Family có max Jaccard ≥0,18 | 0 |

**Giới hạn khoa học:** Đây chỉ là `PASS_SCOPED_LEXICAL_SCREEN` đối với family core, không phải kiểm tra đầy đủ mọi câu trong 128 DEV prompt, 64 prior, hay chứng nhận giống/khác nghĩa từ chuyên gia. **Không** có đối chiếu private đầy đủ với CF1, AC FINAL24 và các bộ nguồn bảo vệ TEST/Q1Q2. Việc không đọc lại TEST/Q1Q2 là ràng buộc ưu tiên, không được khắc phục bằng truy cập file niêm phong. Kết luận toàn bộ cổng nonoverlap: **`HOLD_INCOMPLETE_COVERAGE`**.

## 3. Xuất xứ, quyền và giới hạn

Manifest D1 V2 ghi nguồn `AI_AUTHORED_ORIGINAL_TEST_MATERIAL_NOT_EXTRACTED_FROM_CORPUS`. Nội dung tình huống là đầu ra mới tạo cho dự án theo chỉ dẫn chủ sở hữu; đánh giá xuất xứ `PASS_SCOPED_ORIGIN`, không cần giấy ký hình thức.

OpenAI Terms of Use hiện hành (2026-01-01), https://openai.com/policies/terms-of-use/, quy định quyền sở hữu Output giữa người dùng/OpenAI theo luật hiện hành, đồng thời cảnh báo Output không chắc độc nhất và có hạn chế việc dùng Output để phát triển mô hình cạnh tranh. Vì tài liệu D1 chỉ ghi tuyên bố nguồn gốc mà chưa chứng minh đầy đủ mọi hạn chế, **không khẳng định quyền sử dụng cho mọi mục đích**. `RIGHTS_PROVENANCE=PASS_SCOPED`, `UNQUALIFIED_USE_RIGHTS_CLEARANCE=HOLD`. Chủ dự án có thể cấp biên nhận về mục đích nghiên cứu và xuất xứ ngay trong một quyết định owner, không cần ký bằng giấy.

## 4. Cô lập người chấm

Handoff đã được sửa (commit `2dbf5ca8ed7aa13bb5465cf3037a116b209c9de9`) để chấm cuối bằng **ChatGPT Temporary Chat mới ở chế độ Unpersonalized**, không đưa memory, custom instructions hoặc plugin vào phiên chấm. Theo https://help.openai.com/en/articles/8914046-temporary-chat-in-chatgpt, cần chọn Unpersonalized **trước khi gửi tin nhắn đầu tiên**. Gửi rubric và tệp 512 đầu ra mù đã khóa, **không** gửi mapping/seed/decoder. Chấm và SHA-256 điểm trước giải mù.

Vì science chưa sinh outputs và phiên mới chưa chạy, trạng thái `RATER_ISOLATION=DESIGN_READY_NOT_EXECUTED`. Không yêu cầu người chấm làm lại preexec, không ký nhận, không gọi receipt đầu là bằng chứng đã chấm.

## 5. Trạng thái runtime và phán quyết duy nhất

Device Windows `DESKTOP-4PSD0G2` đang ONLINE. Cổng RemoteDesktop báo `science_job_dispatch_gate.new_job_admission_allowed=false`, `reason=RESEARCH_ADAPTER_DISABLED`, và `run_command` trả `managed mode requires task_job_submit`. Không cố vượt cổng, không tạo job. Đây là hạn chế của đường điều phối remote; không tự biến thành lý do sửa protocol.

**Quyết định owner:** **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`** cho 512 future rollouts và 384 candidate scorings. Không có `GO` để phát hành trình sinh mô hình. `TRAINING=NO`, `INFERENCE=NO`, `TEST/Q1Q2=SEALED`, `FRESH16=NOT_RERUN`, `D1_V2_REKEY=NO_RERUN`, `MAIN=UNCHANGED`, `LINEAGE=UNCHANGED`.

Kết luận kỹ thuật V2 `PASS_SCOPED` và kiểm tra source FRESH16 `PASS_SCOPED_LEXICAL_SCREEN` **không** bị hạ thành FAIL. Cổng chưa đủ điều kiện là **HOLD trước khoa học**, không phải kết quả mô hình.

## 6. Bước thực hiện tiếp theo

`TTM_SMALL4M_D1_EXISTING_FINGERPRINTS_PRIVATE_CONSUMED_SOURCE_NONOVERLAP_ONE_OWNER_RELEASE_READBACK`

Bước chỉ nhận **một gói bằng chứng** từ fingerprint/provenance đã tồn tại của những nguồn bắt buộc còn thiếu, hoặc kết luận chính xác nguồn nào không thể chứng nhận mà không mở tập niêm phong. Xác định phạm vi sử dụng AI-authored Output của D1 bằng receipt nguồn và mục đích nghiên cứu; không ký hay micro-permit. Khi tất cả cổng của hợp đồng đã đóng, phân xử **một** lần GO/HOLD; chỉ sau GO mới thực thi 512 outputs một lượt và bàn giao cho phiên rater độc lập với mapping tách biệt. Không tạo lại V2, không tự nới ngưỡng hay chạy science theo HOLD.
