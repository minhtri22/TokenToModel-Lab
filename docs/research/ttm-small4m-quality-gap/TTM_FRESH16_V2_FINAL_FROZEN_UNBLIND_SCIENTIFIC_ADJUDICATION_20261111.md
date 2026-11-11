# TTM FRESH16 V2 — Phân xử khoa học cuối sau chấm mù và giải mù đã khóa

**Operation:** `TTM_FRESH16_V2_FROZEN_UNBLIND_FINAL_TALLY_AND_SCIENTIFIC_ADJUDICATION`  
**Ngày:** 2026-11-11 · **Repo:** `minhtri22/TokenToModel-Lab`  
**Nhánh:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111` · **HEAD nguồn khoa học đóng băng:** `c05872354d892a9656f8f98642866f7eebfd0f50`  
**Phán quyết nguyên bản (verbatim):** `NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED`  
**Phân loại cổng khoa học:** **`FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED`** — FAIL chỉ trong phạm vi phép kiểm thử này.

## 1. Câu hỏi và phép đo đã khóa

FRESH16 V2 hỏi liệu mô hình TTM-Small-4M có sinh tiếp nối bám dữ kiện, mục tiêu và nhạy với thay đổi dữ kiện trong prompt, thay vì chỉ nối từ/cụm hoặc lặp văn bản chung. Cổng nguyên bản (không sửa sau khi xem đầu ra): checkpoint **bước 1024 là chính**, H1 cần **ít nhất 12/16** đầu ra có `adherence_0_3 >= 2`; H2 cần **ít nhất 6/8** cặp phản thực có `h2_binary=1` và **mỗi một trong bốn nhóm** có ít nhất một cặp đạt. Checkpoint bước **1280 chỉ mô tả (descriptive-only)**. Không dùng TEST, không thêm train, không sửa prompt/rubric và không chạy lại suy luận.

Cả hai người chấm thực tế là hai cuộc trò chuyện riêng do owner cung cấp, dùng GPT-6 và nhãn phiên S1/S2 riêng; mã phiên hệ thống không được cung cấp. S1 chấm đủ 32 đầu ra ẩn danh, SHA được ghi Git **trước** khi S2 nhận cặp; S2 chấm đủ 16 cặp, khóa SHA trên Git **trước** khi giải mù. Không có kiểm định liên giám khảo lặp độc lập (inter-rater reliability) được đo ở đợt này.

## 2. Kết quả khoa học từ bộ tổng hợp (frozen tally)

| Phép đo | Điều kiện đạt | Đã quan sát | Kết luận |
| --- | ---: | ---: | --- |
| H1 tại bước 1024: adherence ≥2 | ≥12/16 | **0/16** | FAIL_SCOPED |
| H2 tại bước 1024: cặp phản thực có điều kiện | ≥6/8 | **0/8** | FAIL_SCOPED |
| Nhóm entity_location | ≥1 | **0** | FAIL_SCOPED |
| Nhóm causal_reasoning | ≥1 | **0** | FAIL_SCOPED |
| Nhóm rule_constraint | ≥1 | **0** | FAIL_SCOPED |
| Nhóm goal_persistence | ≥1 | **0** | FAIL_SCOPED |

- Tổng số đầu ra đã sinh trong lượt CPU one-shot: **32/32**. S1 chấm **32/32**; theo tệp S1 đã khóa: **28 điểm adherence=1, 4 điểm adherence=0, không có điểm ≥2**.
- S2 chấm **16/16** cặp ẩn danh; **0 cặp H2=1, 16 cặp H2=0**. H1/H2 chính chỉ tính checkpoint bước 1024, không thay mẫu số đã tiền đăng ký.
- Tệp `FINAL_TALLY_PRIVATE.json` đã được owner cung cấp và kiểm tra SHA-256 độc lập từ byte gốc **`64ec345fef6ef2f1c8b08e847047e3d3ac53f7bcca83fe39ae10d27e69b6f181`**, kích thước **839 byte**. JSON trực tiếp trên Windows trùng số liệu, SHA S1/S2 và nguồn đã khóa; bộ kiểm định gốc báo `FRESH16_FINAL_TALLY=PASS_FROZEN_GATE_EXECUTED`.
- `PASS_FROZEN_GATE_EXECUTED` là **PASS thực thi/kiểm định dữ liệu**, không phải PASS giả thuyết khoa học.

## 3. Chuỗi bằng chứng (provenance) kiểm chứng được

- CPU32 một lượt và receipt nguồn: commit `d849f010740a47fd9bcc353f6b54aedfc2096fe0`; nguồn thực nghiệm đóng băng `c05872354d892a9656f8f98642866f7eebfd0f50`; runner blob `f069f2bdaa2d9691a1ce6c9746ff8f2923beb1d8`.
- Mapping niêm phong: chỉ SHA `eb570460b1423bb4b2355ccb5b7b56862c641721d5ecf62f7136224b71ea20a8`, neo tại commit `d95b09f894dd7ef975b375a794f50a1d7905e0d6`. Nội dung mapping không đưa lên GitHub.
- Khóa S1: commit `5fd1d923de52d18709a39332400e3e98e6dfb31d`, điểm S1 SHA `d08d59a9fe9738ef798aa2e0449345cb76e5c9f24f825a37685f928052028d35`.
- Khóa S2: commit `9c02e0f3c7d3073e742de7fc75a08e5a48ec9afe`, điểm S2 SHA `517643feba73c96003334a1e8a9095ebd091aaff3e764ddd87faf91dbf78b31b`.
- Bộ phân cặp/giải mù đã đóng băng: Git blob `244c49c188c4645825af9f1bd048fbad535019d3`. Không sửa để đạt phán quyết.
- Tệp tally nguyên bản chỉ tại `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_fresh16_v2_e0_20261111\FINAL_TALLY_PRIVATE.json`; SHA `64ec345fef6ef2f1c8b08e847047e3d3ac53f7bcca83fe39ae10d27e69b6f181`. Biên bản kết quả công khai chỉ dùng hash và thống kê tổng hợp; không công khai đầu ra, điểm từng record, token IDs hoặc mapping.

## 4. Phán quyết và giới hạn

**Kết luận: `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED` / frozen verdict `NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED`.** Dưới cùng các ràng buộc nguồn/model/generation/rubric đã khóa, thử nghiệm này **không chứng minh** khả năng bám prompt và gắn kết sự kiện phản thực đạt ngưỡng định trước.

Không suy ra mô hình không bao giờ thực hiện được một tác vụ prompt, hoặc tất cả checkpoint/hyperparameter đều FAIL; checkpoint bước 1280 chỉ mô tả. Kết quả âm tính về chất lượng tiếp nối không phủ định `PASS_H1_CONFIRMATORY_VAL_SCOPE` hay `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED` trước đó vì NLL và chất lượng tiếp nối là các phép đo khác nhau. Các kết quả L0011–L0014 và các FAIL/PASS trước giữ nguyên. Không thử lại cùng 32 đầu ra, không sửa điểm S1/S2 đã khóa để “cứu” giả thuyết. Phép nghiên cứu kế nhiệm nếu có cần thiết kế độc lập, không đọc lại TEST và không mở huấn luyện mới theo biên bản này.

**Kết thúc:** Hoàn tất science adjudication trong phạm vi FRESH16 V2; cập nhật `lineage.md` bằng entry L0015 dạng append-only. Không merge/main hay triển khai mới trong lượt này.
