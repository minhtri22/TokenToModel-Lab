# TTM-Small-4M D1 — Gói DEV thực tế mới, kiểm chứng nguồn và quyết định thực thi một lần

**Ngày:** 2026-11-11  
**Operation:** TTM_SMALL4M_D1_NEW_DEV_STIMULUS_AND_EXECUTABLE_PREREG_SINGLE_OWNER_GO_HOLD  
**Nhánh duy nhất:** research/ttm-small4m-prompt-adherence-continuation-design-20261111  
**Quyết định:** **HOLD_SCIENCE_EXECUTION_SINGLE_FINAL_PREEXEC**. Thiết kế D1 cũ tiếp tục **GO_DESIGN_FROZEN**. Chưa chạy train/inference/TEST.

## Bằng chứng mới đã tạo

- Đã tạo và ghi gói dữ liệu riêng tư dạng JSON trên Windows tại: D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_SMALL4M_D1_NEW_DEV_PRIVATE_20261111.json. Công cụ ghi phản hồi 259.676 ký tự.
- Nội dung gồm 16 gia đình phản thực độc lập (4 nhóm ×4), 128 prompt DEV mới (2 biến thể fact ×2 độ dài ×2 vị trí), 64 prompt trung tính x0, 32 chuỗi ứng viên, danh mục ánh xạ kín 512 đầu ra dự kiến, ba seed sampling và rubric chấm mù.
- Bản thảo ngữ nghĩa đi theo D1, nhưng câu chữ là dữ liệu mới chứ không phải tái dùng FRESH16. Đầu ra và nhãn chưa tồn tại. Tập này chưa được chấm hay đưa vào inference.
- Chỉ dấu toàn vẹn từ 39 mảnh đọc văn bản Windows, nối lại theo vị trí và chuẩn hóa xuống dòng LF, tổng 259.676 ký tự ASCII, SHA-256 **de5c0acae9a863e255922963d9644623ff6b1cbfedc0ff9edd7d8225cbac7603**. Đây là SHA của **nội dung LF chuẩn hóa**, **không được gọi là SHA của byte nguyên bản trên đĩa** khi cơ chế CRLF Windows chưa được kiểm tra.
- Bộ xác minh Python chỉ đọc (không inference/training, không ghi file) đã được đưa lên GitHub tại tools/pilot_t4/d1_static_qa/ttm_d1_private_dev_readonly_qa.py, đồng thời được ghi tại D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_D1_PRIVATE_DEV_READONLY_QA_20261111.py.
- Bộ kiểm tra dùng bộ mã hóa BPE thực từ worktree E0 và tệp T1_BPE2048_REAL_TRAIN_MANIFEST.json. Đã đọc được toàn bộ 1.791 cặp gộp trong manifest Windows; mã hóa ASCII trong bộ sinh được đối chiếu thuật toán nguồn Python. **Bộ kiểm tra Python độc lập chưa được chạy**, vì RemoteDesktop đang quản lý lệnh qua task_job_submit chứ không chấp nhận run_command/job_submit tùy ý.

## QA đạt trong phạm vi bộ sinh

| Hạng mục | Kết quả |
| --- | --- |
| Gia đình / nhóm | 16 / 4, mỗi nhóm 4 |
| Số prompt DEV | 128, phân bố đồng đều 32/nhóm |
| Đối chứng x0 | 64 |
| Ứng viên cùng độ dài BPE trên mỗi gia đình | 16/16 |
| Độ dài prompt ngắn | 74–92 BPE |
| Độ dài prompt dài | 168–186 BPE |
| Cự ly cue gần | 17–28 BPE |
| Cự ly cue xa ở ngắn | 51–62 BPE |
| Cự ly cue xa ở dài | 145–156 BPE |
| Tràn context | 0/128 |
| Trùng byte prompt nội bộ | 0/128 |
| Vi phạm kiểm tra bộ sinh | 0 |
| Quy mô giải mã tương lai, chưa chạy | 128 greedy + 384 nucleus = 512 |
| Trần sinh + teacher-forced candidate target | 37.376 token, chưa tính prompt prefill |

Hai nguồn public có prompt lịch sử đã được so sánh riêng theo 16 scene: TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json và TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json. Không thấy scene mới trùng nguyên văn với nội dung công khai đó. **Không tuyên bố không trùng gần/ngữ nghĩa toàn tập** hoặc đã kiểm tra TEST/Q1Q2/FRESH16 mù/AC FINAL24 riêng tư. TEST niêm phong và FRESH16 không bị mở hoặc chạy lại.

## Quyền dữ liệu và chấm mù

Các đoạn tình huống là văn bản được biên soạn mới trong công việc này, không trích rút chủ ý từ TinyStories hay dữ liệu lịch sử. Provenance này chỉ hỗ trợ quyền dùng trong phạm vi văn bản mới; không là chứng nhận pháp lý hay ký xác nhận quyền sử dụng của owner. Trạng thái: RIGHTS_ORIGIN=SELF_AUTHORED_SCOPED; OWNER_RIGHTS_ATTESTATION=NOT_RECORDED.

Tệp riêng tư có mapping cho 512 trường hợp và ba seed đã chọn, không đưa key/seed/prompt/mapping công khai. Người chấm tương lai phải nhận packet mới chỉ có mã mù, prompt và output, không có mapping, thông số decoder, hay nhãn fact A/B. Quy tắc chấm 0–3 và khóa điểm SHA trước giải mù giữ nguyên từ hợp đồng D1. Người chấm độc lập chưa được phân công; chưa có điểm, chưa được giải mù.

## Phán quyết duy nhất: HOLD

**HOLD_SCIENCE_EXECUTION_SINGLE_FINAL_PREEXEC**, vì (i) raw Windows SHA256 chưa tái băm trực tiếp; (ii) bộ Python QA độc lập chưa chạy; (iii) so trùng gần trên các nguồn riêng tư chưa có biên nhận an toàn, không được mở TEST/Q1Q2 đã tiêu thụ; (iv) owner rights/role custody chưa hoàn tất. Không tăng mức sẵn sàng từ chứng nhận tự tạo của bộ sinh. Đây là **HOLD về sẵn sàng thực thi**, không phải FAIL khoa học.

Giữ nguyên mọi bất biến: FRESH16 V2 FAIL scoped và lineage L0015, checkpoint bước1024, worktree E0 HEAD c05872354d892a9656f8f98642866f7eebfd0f50, main 5d52e32f20021e36f08f284ef9864d3ba36dbead, A/C NO_GO_PREEXEC, O1=DEFER. Không merge, không append lineage, không huấn luyện, không suy luận, không TEST.

## Bước thực hiện tiếp theo

**TTM_SMALL4M_D1_PRIVATE_PACK_INDEPENDENT_QA_AND_SINGLE_OWNER_RELEASE_READBACK_NO_SCIENCE** — thực hiện một lượt kiểm định read-only bằng Python 3.12 trên Windows, công bố **chỉ** SHA raw, đếm và kết quả QA; đối chiếu nguồn riêng tư bằng chỉ dấu không tiết lộ nếu có, xác nhận người chấm và quyền dữ liệu, sau đó một quyết định owner GO/HOLD toàn batch. Không tạo nhánh thí nghiệm phụ hoặc các micro-permit. Không chạy science từ lệnh QA.
