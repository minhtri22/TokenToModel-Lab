# HANDOFF — TTM-Small-4M D1 / Independent ChatGPT Blind Rater

**Ngày thiết lập:** 12/11/2026  
**Operation:** `TTM_SMALL4M_D1_INDEPENDENT_CHATGPT_AGENT_BLIND_RATER_HANDOFF_PREEXEC`  
**Dự án:** `minhtri22/TokenToModel-Lab`  
**Nhánh lưu giao thức:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Vai trò:** AI-assisted independent blind rater (*agent chấm mù độc lập có hỗ trợ AI*).  
**Trạng thái:** **ROLE_DESIGNATED_BY_OWNER — RATER_NOT_YET_ACCEPTED / SCIENCE_HOLD**.

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

## 4. Phiếu chấp nhận nhiệm vụ (điền trước khi nhận output thật)

```text
operation=TTM_SMALL4M_D1_INDEPENDENT_CHATGPT_BLIND_RATER
rater_identity_or_agent_instance=<cung cấp bởi bên tiếp nhận>
rater_model=<mô hình thực tế tại thời điểm chấm>
accepts_scoring_only=YES/NO
has_seen_seed_decoder_mapping_answer_key=YES/NO
had_role_in_prompt_design_or_generation=YES/NO
has_access_to_private_repository_or_evaluation_history=YES/NO
rubric_and_scoring_contract_accepted=YES/NO
agrees_to_lock_scored_output_sha_before_unblind=YES/NO
accepted_at=<timestamp>
signature_or_owner_countersign=<receipt source>
```

**Điều kiện hợp lệ:** rater có thể chấm chỉ khi `accepts_scoring_only=YES`, `has_seen_seed_decoder_mapping_answer_key=NO`, `had_role_in_prompt_design_or_generation=NO`, `has_access_to_private_repository_or_evaluation_history=NO`, `rubric_and_scoring_contract_accepted=YES`, `agrees_to_lock_scored_output_sha_before_unblind=YES` và có receipt chấp nhận được owner/custodian xác minh.

## 5. Điều kiện GO/HOLD

Tài liệu này **chỉ chuẩn bị bàn giao**, không chứng minh rater đã nhận nhiệm vụ và không cấp GO science. Cần một gói chứng thực tổng hợp gồm:

1. Chủ sở hữu chứng nhận nguồn và quyền dùng văn bản D1 mới;
2. Người có thẩm quyền chứng nhận không trùng các nguồn private, trong phạm vi được phép và **không mở lại TEST/Q1Q2**;
3. ChatGPT agent độc lập ký tiếp nhận vai trò chấm mù; owner/custodian ký quy tắc bảo quản mapping/seed và khóa scores trước giải mù.

Nếu bất kỳ điều kiện nào thiếu: `HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`. Chỉ khi các điều kiện đóng cùng lúc mới xem xét phát hành 512 outputs trong một owner GO/HOLD riêng. Không micro-permit, không tái khóa seed, không chỉnh `lineage.md`, không mở lại FRESH16.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_D1_ONE_PACKET_NONOVERLAP_RIGHTS_CHATGPT_RATER_ACCEPTANCE_AND_MAPPING_CUSTODY_OWNER_RELEASE`.
