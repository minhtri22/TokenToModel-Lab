# HANDOFF — TTM-Small-4M D1 / Independent ChatGPT Blind Rater

**Ngày thiết lập:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_INDEPENDENT_CHATGPT_AGENT_BLIND_RATER_HANDOFF_PREEXEC`  
**Dự án:** `minhtri22/TokenToModel-Lab`  
**Nhánh lưu giao thức:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Vai trò:** AI-assisted independent blind rater (*agent chấm mù độc lập có hỗ trợ AI*).  
**Trạng thái:** **HANDOFF_READY — AUTO_START_ON_RECEIPT; SCORING_WAITING_FOR_AUTHORIZED_GENERATED_OUTPUTS / SCIENCE_HOLD**.

## 1. Phạm vi ủy nhiệm

Chủ dự án sẽ giao việc **chấm mù 512 văn bản được sinh** cho một ChatGPT agent **khác** với agent thiết kế, sinh prompt, kiểm toán V2 và giữ mapping. Đây là phân tách vai trò theo quy trình (*procedural independence*), không phải bằng chứng thống kê rằng các lần chấm của cùng nền tảng mô hình độc lập về lỗi và thiên lệch.

Agent chấm chỉ được xem **gói chấm mù riêng biệt**: mã `blind_id`, prompt cần đánh giá và văn bản sinh sau khi science GO đã chạy. Agent không được xem nhãn `A/B`, cặp candidate đúng, seed, decoder, `prompt_id`, raw mapping, checkpoint chi tiết hay phân xử FRESH16.

Trước khi có đầu ra mới, tệp mẫu riêng tư `TTM_SMALL4M_D1_BLIND_RATER_TEMPLATE_V2_20261111.json` **có 512 vị trí nhưng `generated_text=null`**. Mẫu chưa phải đầu vào có thể chấm; không suy luận, điền điểm dự đoán hoặc tự sinh tiếp nối.

## 2. Chỉ dẫn độc lập và ranh giới thông tin

- Bắt đầu trong **agent/phiên riêng**, không sử dụng ký ức/ngữ cảnh, GitHub, file private, liên kết hay cuộc trò chuyện của agent chủ nghiên cứu ngoài gói được bàn giao.
- Không tự đọc các tệp `*_PRIVATE*`, seed manifest, mapping, history FRESH16/AC hoặc sealed TEST/Q1Q2. Nếu thấy dấu hiệu tiết lộ decoder, seed, mapping, nhãn hệ thống, đáp án hoặc đánh giá trước, **dừng và báo BLINDING_COMPROMISED**, không chấm tiếp.
- Không sửa prompt, không thay văn bản do mô hình sinh, không chạy inference, không lựa chọn mẫu, không tự đổi rubric/ngưỡng, không đề xuất sửa gói DEV cho lần chạy này.
- Không gửi văn bản chấm mù, raw scores hoặc chi tiết riêng tư lên GitHub công khai. Chỉ gửi biên nhận đã che nội dung như count, SHA-256, phạm vi lỗi, tình trạng khóa điểm.
- Gói chấm mù phải được cung cấp từ custodian **sau science GO**, sau khi 512 outputs thực tế được sinh và đóng băng; owner/custodian xác nhận input SHA-256 trước khi chuyển cho rater.
- Sau khi chấm, người giữ mapping không được giải mù trước khi **bản chấm và SHA-256** được khóa; kết quả giải mù chỉ do người bảo quản và người phân xử khoa học đối chiếu.

## 3. Rubric không điều chỉnh

Chấm `adherence_0_to_3` từng văn bản:

| Điểm | Ý nghĩa |
| --- | --- |
| 0 | Không có sự kiện/hành động đủ thông tin để chấm |
| 1 | Có sự kiện nhưng sai hoặc không ràng buộc dữ kiện trong prompt |
| 2 | Sự kiện hành động đầu khớp dữ kiện, nhân vật và đối tượng |
| 3 | Đúng dữ kiện, nhân vật/đối tượng **và giữ mục tiêu** trong diễn tiến |

Ghi thêm `first_event_fact_match`, `goal_retention`, `serious_contradiction`, `notes` theo mẫu đã khóa; nếu không đủ thông tin thì ghi tình trạng **không thể chấm** thay vì đoán hoặc tự sáng tạo tình tiết. **Không** tính tỉ lệ thắng greedy/nucleus hoặc so sánh seed trước giải mù. Không tự định nghĩa science PASS/FAIL: nhiệm vụ chỉ là chấm văn bản.

Một biên nhận scoring có ít nhất: `rater_role`, `model_or_agent_identifier`, thời điểm bắt đầu/kết thúc, `blind_input_sha256`, số bản ghi nhận/đã chấm/không thể chấm, `scored_output_sha256`, xác nhận không truy cập mapping/seed/decoder và xác nhận không thay rubric. Nơi lưu điểm phải riêng tư, không ghi dữ liệu mẫu lên repo công khai.

### Cô lập ngữ cảnh chấm cuối (final rater isolation)

Biên nhận preexec ChatGPT đầu tiên chỉ đạt `RATER_PREEXEC_READY_SCOPED` và tự khai báo đã có ngữ cảnh nghiên cứu trước đó; **không dùng chính cuộc trò chuyện đó làm căn cứ chứng nhận độc lập**. Đây không phải lý do yêu cầu chấm lại preexec.

Khi **và chỉ khi** có 512 đầu ra thực được phát hành trong một science batch đã GO, chủ dự án mở **ChatGPT Temporary Chat mới, chọn Unpersonalized trước tin nhắn đầu** (không dùng memory/custom instructions/plugins cho cá nhân hóa), dán trực tiếp rubric/handoff tối thiểu và đính kèm duy nhất **gói chấm mù đã khóa**. Không đưa GitHub nghiên cứu, các bản đồ seed/decoder, keys hoặc transcript agent sinh vào phiên đó. Handoff được coi là lệnh thực hiện, không đòi hỏi chữ ký; chấm ngay 512 văn bản rồi xuất private scores và SHA trước giải mù.

Tài liệu hỗ trợ của OpenAI: https://help.openai.com/en/articles/8914046-temporary-chat-in-chatgpt — Temporary Chat có hai chế độ, chỉ **Unpersonalized** mới không tham chiếu memory, custom instructions và plugins. Cách này giảm nhiễm ngữ cảnh, không phải bằng chứng độc lập tuyệt đối về thiên lệch của cùng họ mô hình. Nếu không thể nhận tệp vì Temporary Chat thiếu plugin, đính kèm gói file trực tiếp; không bật plugin để đọc private mapping.

## 4. Lệnh thực thi ngay khi nhận handoff (auto-start on receipt)

**Không cần ký tên, phiếu chấp nhận, xác nhận riêng hoặc yêu cầu chủ dự án cấp micro-permit.** Handoff là lệnh công việc cho ChatGPT agent được giao: khi chủ dự án chuyển handoff sang phiên agent khác, agent **bắt đầu ngay** những bước đã đủ bằng chứng trong phạm vi vai trò của mình, không chờ lời mời xác nhận.

Agent phải thực hiện theo thứ tự:

1. Kiểm tra đúng phiên làm việc độc lập và gói đầu vào đã được chuyển; **không tự tìm đọc** seed, mapping, đáp án, lịch sử FRESH16/AC hoặc dữ liệu TEST/Q1Q2.
2. Nếu chỉ nhận được **mẫu V2 với `generated_text=null`**, kiểm tra cấu trúc chấm, số bản ghi và mô tả rubric; xuất **`RATER_PREEXEC_READY_SCOPED`** hoặc **`RATER_BLOCKED`** cùng lý do; **không tự sinh 512 outputs, không tự chấm văn bản chưa có**.
3. Khi một gói **512 outputs sinh thực sự đã được chủ dự án phát hành sau science GO** được bàn giao, đối chiếu SHA đầu vào, chấm mù trực tiếp 512 bản theo rubric khóa, lưu kết quả và SHA-256 **trước khi giải mù**. Không cần một cuộc ký nhận riêng.
4. Xuất biên nhận kết quả tự mô tả bằng máy: `agent_model` nếu biết, `input_sha256`, `total_records`, `scored_records`, `unscorable_records`, `score_sha256`, `blindness_integrity`, `execution_status`, `blocked_reason` nếu có. Các trường chưa thể quan sát phải ghi `NOT_VERIFIED`, không suy diễn PASS.
5. Trả kết quả về chủ dự án dưới dạng tệp private và biên nhận public đã loại dữ liệu nhạy cảm. **Không chuyển mapping hoặc nhãn hệ thống cho agent chấm**.

**Tiêu chuẩn độc lập:** một ChatGPT agent/phiên khác, không có thông tin mapping/seed/decoder hay vai trò trong việc thiết kế và sinh đầu ra. Biên nhận tự mô tả **không chứng minh được các quyền truy cập mà agent không quan sát**, nên chủ dự án vẫn cần kiểm soát quyền tệp và xác minh quy trình tách biệt. Không yêu cầu chữ ký hoặc xác nhận cá nhân, nhưng cũng không biến một lời khẳng định thiếu căn cứ thành PASS.

## 5. Điều kiện GO/HOLD ngoài phạm vi người chấm

- **Handoff không phải science GO.** Người chấm được tự động kiểm tra sẵn sàng ngay; chỉ chấm sau khi có đầu ra thực do một lượt science đã được cấp GO.
- Quyền sử dụng nội dung D1 cần **bằng chứng xuất xứ và xác nhận chủ dự án theo hình thức receipt**, không cần chữ ký riêng. Kiểm tra không trùng nguồn private cần bằng chứng từ bên được phép theo phạm vi đã đóng băng; không được tự mở lại TEST/Q1Q2.
- Kiểm soát bảo quản mapping/seed bằng **phân quyền thực tế và SHA biên nhận**, không bằng nghi thức ký nhận; chấm trước, khóa điểm, rồi mới giải mù.
- Chừng nào `PRIVATE_NONOVERLAP` hoặc `RIGHTS` chưa được xác minh, quyết định chung vẫn **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`**. Không mở micro-permit, không tái khóa seed, không sửa `lineage.md`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_AUTO_HANDOFF_RATER_READINESS_THEN_ONE_PACKET_OWNER_GO_HOLD`. Khi người dùng đưa handoff vào ChatGPT agent khác, agent thực hiện bước kiểm tra khả năng chấm ngay, trả receipt; phần science vẫn do owner GO/HOLD một lần cho batch.
