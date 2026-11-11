# TTM-Small-4M D1 — Hợp đồng thiết kế phân biệt điều kiện hóa dữ kiện và giải mã

**Ngày:** 2026-11-11. **Operation:** TTM_SMALL4M_D1_FIXED_CHECKPOINT_FACT_CONDITIONING_VS_DECODING_NEW_DEV_SINGLE_FROZEN_DESIGN_OWNER_GO_HOLD.  
**Nhánh tiếp nhận duy nhất:** research/ttm-small4m-prompt-adherence-continuation-design-20261111.  
**Phán quyết duy nhất:** **GO_DESIGN_FROZEN** (khóa giao thức, không khóa dữ liệu byte); **SCIENCE_EXECUTION=HOLD**. Không phải khoa học PASS hay cấp phép chạy.

## 1. Đối chiếu nguồn hiện hành

| Nguồn | Giá trị đối chiếu | Phạm vi |
| --- | --- | --- |
| HEAD nhánh D1 trước tài liệu | ffbbb8c28474315cf29c72f2cd38ee2ca7056244 | Chỉ ghi D1 vào nhánh này |
| main | 5d52e32f20021e36f08f284ef9864d3ba36dbead | Không merge |
| A/C | 837289fda82b41653a61b74e476f76a0b4c4137c | Không thay đổi |
| Hậu CF1 | e2f9aca666a1f5605feebd00794d4a699a2a3475 | Có thêm 1 commit: O0 chờ AC, không có C−A thật |
| Windows worktree E0 local ref | c05872354d892a9656f8f98642866f7eebfd0f50 | Đọc ref, không checkout/fetch/reset |
| lineage.md nhánh D1 | Git blob 9110d101601e6ebfb64d9804f3704a90cb284420 | L0015 là FRESH16 FAIL |
| lineage.md main | Git blob 259adcd9fa7197c197d424ced9a7e5887e378663 | L0014 |

Đã đọc lại tài liệu quyết định hậu FRESH16 và báo cáo phân xử khoa học cuối. Các blob công khai đã kiểm tra tồn tại: runner f069f2bdaa2d9691a1ce6c9746ff8f2923beb1d8, pair gate 244c49c188c4645825af9f1bd048fbad535019d3, AC 2×2 6f8553e7054078d449bad6b2979c3b07d392eb48, AC NO-GO receipt 0c83b23c13c588a7787dd64a6c3d9ed5da22c5ce. Các commit neo mapping d95b09f894dd7ef975b375a794f50a1d7905e0d6, S1 5fd1d923de52d18709a39332400e3e98e6dfb31d, S2 9c02e0f3c7d3073e742de7fc75a08e5a48ec9afe cũng tồn tại. Windows đang online và đã liệt kê được các receipt riêng tư FRESH16; không mở mapping, raw outputs hay nhãn cá thể.

**Khóa chỉ tham chiếu:** checkpoint bước1024 SHA256 cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b; bước1280 SHA256 ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc (chỉ mô tả); mapping SHA256 eb570460b1423bb4b2355ccb5b7b56862c641721d5ecf62f7136224b71ea20a8; S1 SHA256 d08d59a9fe9738ef798aa2e0449345cb76e5c9f24f825a37685f928052028d35; S2 SHA256 517643feba73c96003334a1e8a9095ebd091aaff3e764ddd87faf91dbf78b31b; tally SHA256 64ec345fef6ef2f1c8b08e847047e3d3ac53f7bcca83fe39ae10d27e69b6f181. **Chỉ đối chiếu chéo SHA private qua biên bản, không tái băm byte private**.

**Sự thật khoa học:** T4 VAL NLL 3.5223388517 so bigram 3.9972314170 PASS theo phạm vi; FRESH16 V2 checkpoint1024 H1=0/16, H2=0/8 FAIL đã phân xử. 32/32 điểm S1 dưới 2 làm H2=0 theo cổng phụ thuộc, không thành bằng chứng nhân quả độc lập. FRESH16 dùng greedy, prompt BPE ≤192, sinh ≤64, context256, không overflow. A/C chưa có phân xử thực nghiệm, C−A NOT_ESTIMABLE. Không tái chạy FRESH16, TEST, Q1Q2 hoặc dùng checkpoint1280 như đối chứng ngân sách ngang.

## 2. Giả thuyết đối nghịch

- **H-A:** xác suất có điều kiện (conditional probability) ưu tiên cả hai hành động đúng khi đảo một dữ kiện, nhưng tiếp nối tự sinh (free-running rollout) mất hành động/mục tiêu. H-A1: lấy mẫu giúp cải thiện lặp lại; H-A2: lấy mẫu không cứu, cần nghiên cứu rollout chứ chưa quy lỗi cho greedy.
- **H-B:** ngay ở tình huống ngắn/gần, phân bố có điều kiện không đảo đúng ưu tiên theo fact; decoder không thể được công nhận là nguyên nhân chính từ phép đo hiện có.
- **H-C:** độ nhạy có ở ngắn/gần nhưng giảm khi context dài hoặc cue xa mà không overflow.
- **H-0:** hỗn hợp/thiên lệch từ vựng/không chắc chắn; phân loại INCONCLUSIVE.
  
Không giả định thiếu dữ liệu, thay loss, tăng capacity, MoE hay attention. D1 không thể nhận dạng nhân quả về các nguyên nhân huấn luyện này.

## 3. DEV mới: 16 gia đình độc lập, có đối chứng phản thực

Mỗi gia đình gồm fact A/B và 2 tiếp nối yA/yB; đúng **một dữ kiện quyết định** thay đổi trong từng xA↔xB. Bảng là **blueprint ngữ nghĩa đóng băng**, không phải prompt byte đã niêm phong. Viết mới tiếng Anh theo văn phong truyện ngắn; không sao chép hoặc sửa prompt đã tiêu thụ.

| Gia đình | Nhóm | Fact A ↔ fact B | Hành động yA ↔ yB |
| --- | --- | --- | --- |
| E01 | entity_location | bóng ở giỏ ↔ kệ | lấy bóng tại giỏ ↔ kệ |
| E02 | entity_location | chó ở chuồng ↔ vườn | tìm chó ở chuồng ↔ vườn |
| E03 | entity_location | thư do Mira ↔ Olin giữ | nhận thư từ Mira ↔ Olin |
| E04 | entity_location | mũ ở móc ↔ ghế | lấy mũ tại móc ↔ ghế |
| C01 | causal_reasoning | chậu khô ↔ ướt | tưới cây ↔ để cây ráo |
| C02 | causal_reasoning | cốc rỗng ↔ đầy | rót nước ↔ mang cốc đi |
| C03 | causal_reasoning | đèn hết pin ↔ tắt công tắc | thay pin ↔ bật công tắc |
| C04 | causal_reasoning | cửa khóa ↔ mở khóa | dùng chìa ↔ đẩy cửa |
| R01 | rule_constraint | quy tắc chọn đỏ ↔ xanh | đi cửa đỏ ↔ xanh |
| R02 | rule_constraint | quy tắc chọn hộp sao ↔ sọc | bỏ quà vào hộp sao ↔ sọc |
| R03 | rule_constraint | chỉ dẫn đông ↔ tây | rẽ đông ↔ tây |
| R04 | rule_constraint | chuông một ↔ hai lần | rung một ↔ hai lần |
| G01 | goal_persistence | giao thiệp Iva ↔ Nora | giao Iva ↔ Nora |
| G02 | goal_persistence | mang chậu tới sông ↔ hiên | đến sông ↔ hiên |
| G03 | goal_persistence | đồ chơi cho Ari ↔ Leo | mang Ari ↔ Leo |
| G04 | goal_persistence | đưa đèn tới nhà gỗ ↔ kho | đến nhà gỗ ↔ kho |

Cân bằng ứng viên theo từng nhóm: 2/4 gia đình yA đứng trước trong manifest, 2/4 yB đứng trước; mô hình không thấy nhãn A/B. Fact là thông tin có ý nghĩa, cả hai hành động hợp lý nếu nhận fact tương ứng. Bảo toàn actor, thời điểm, mục tiêu, vật thể và câu chốt giữa A/B. Ứng viên tương xứng hình thức, mỗi ứng viên 3–12 token BPE, **hai ứng viên bằng số token BPE**. Đánh giá độc lập tính tự nhiên, nhân quả, một-fact-only, tương đương văn phong và không có câu chữ dẫn đáp án.

Mỗi fact có bố trí độ dài (length) và vị trí (cue distance) 2×2: short 64–96 BPE, long 160–192 BPE; cue near cách điểm trả lời 16–32 BPE; cue far ở short 48–64 BPE và ở long 144–160 BPE. Chỉ hoán đổi câu fact với filler cùng số BPE, không đổi hành động đích/ý nghĩa filler. **16×2 fact×2 length×2 distance =128 prompt**; chốt toàn bộ byte/count/offset trước khi đo. Mỗi prompt ≤192 BPE, sinh ≤64; tổng không quá context256; tuyệt đối không cắt prompt. Ghi mọi sai khác token và nhiễu khó khử.

## 4. Độ nhạy dữ kiện bắt buộc (teacher-forced fact-choice)

Trên checkpoint1024 SHA cố định, BPE2048, P02 3.749.376 tham số, không sửa weights/config, tính cho ứng viên y:
  
- L(y|x) = tổng log xác suất token ứng viên theo thứ tự (teacher forcing).
- ell(y|x) = L(y|x)/số token BPE của y.
- mA = ell(yA|xA) − ell(yB|xA).
- mB = ell(yB|xB) − ell(yA|xB).
- Switch của một gia đình = **mA>0 và mB>0**; hòa bằng 0 là chưa đạt. Báo biên raw total và length-normalized, không chỉ điểm của một ứng viên.
  
Đối chứng prior lexical: mỗi gia đình/bố trí có prompt x0 cùng slot và văn phong nhưng không nói fact quyết định (64 prompt x0); d0 = ell(yA|x0) − ell(yB|x0); biên hiệu chỉnh mA'=mA−d0, mB'=mB+d0. Báo song song prior thô và hiệu chỉnh, không chọn hậu nghiệm. Tổng **128×2+64×2=384 lượt chấm ứng viên**, mỗi ứng viên ≤12 BPE (tối đa 4.608 token ứng viên, chưa tính prefill).

Phép chính = 16 gia đình ở short/near: S đếm switch, S' đếm switch prior-adjusted, D = (mA+mB)/2. Báo 4 nhóm riêng. Khoảng tin cậy bootstrap 95% với 10.000 resample lấy **gia đình** theo tầng 4 nhóm (4 family/tầng); không dùng 128 prompt hay 32 fact variants làm 128/32 mẫu độc lập. **Tín hiệu mạnh khám phá** nếu S≥12/16, S'≥12/16, mọi nhóm ≥2/4 và cận dưới bootstrap mean(D)>0. **Yếu khám phá** nếu S≤4/16 và S'≤4/16. Các trường hợp khác hoặc điều kiện CI trái nhau = INCONCLUSIVE. Đây là chỉ báo hướng nghiên cứu, không phải PASS xác nhận.

## 5. Độ dài, vị trí cue và khác biệt rollout

Trong mỗi gia đình tính D/S/S' ở short-near, short-far, long-near, long-far. So hiệu ứng độ dài khi giữ near, hiệu ứng cue distance khi giữ length, tương tác (D_long_far−D_long_near)−(D_short_far−D_short_near). **Cảnh báo context khám phá** khi ≥8/16 gia đình mất switch từ short-near sang long-far, mean(D) giảm ≥0.05 nat/token và bootstrap cận dưới cho mức giảm >0. Filler có thể thay phân phối nên không gọi đó là lỗi kiến trúc attention.

Trong diễn tiến sinh, ghi sự kiện đầu (first actionable event), mức khớp actor/object/fact, rồi trạng thái ở mốc 8/16/32/64 token nếu có sự kiện để đo trôi mục tiêu (rollout drift). Không giả vờ teacher-forced margin ở prefix sinh tự do luôn có nghĩa: nếu ứng viên yA/yB không còn hợp cú pháp sau prefix đó thì ghi NA.

## 6. Đối chứng giải mã (decoding) cùng checkpoint và prompt

Trên 128 prompt byte đã khóa, dùng:
- Greedy argmax, EOS ID256, tối đa 64 token: **128 outputs**.
- Nucleus top-p=0.9, temperature=0.8, **3 seed độc lập khóa trong private manifest trước science**: **384 outputs**.
- Tổng **512 outputs**, tối đa **32.768 token mới**; không thêm seed, chọn mẫu đẹp, điều chỉnh top-p hoặc sinh lần hai sau khi xem kết quả.

Người chấm tách vai trò với người thiết kế/generator, chấm mù decoder/seed/fact và đảo thứ tự. Rubric: 0=không có sự kiện đủ chấm; 1=có sự kiện nhưng sai/không ràng buộc dữ kiện; 2=sự kiện đầu đúng fact, actor, đối tượng; 3=đúng và giữ mục tiêu trong diễn tiến. Thành công nếu adherence≥2 và không mâu thuẫn nghiêm trọng. Ghi thêm first event, fact consistency 0/1, goal retention 0/1, lặp 3-gram, EOS sớm, chiều dài, thời gian/cost. Điểm và SHA của bản chấm mù khóa **trước** mở mapping. Hai phiên chấm tách biệt được phép; không bắt buộc một bên thứ ba giữ nhãn.

Gia đình pair-success khi **cả hai fact** có điểm≥2 với cùng decoder/seed. Đánh giá chính trên 16 gia đình short-near; so greedy với trung bình pair-success của 3 seed, bootstrap theo family; báo riêng từng seed. **Greedy rollout yếu** nếu ≤4/16 pair-success. **Tín hiệu sampling cải thiện bền** nếu gain trung bình ≥0.25, ít nhất 2/3 seed gain dương, ≥3/4 nhóm không suy giảm và bootstrap cận dưới gain >0. Không gọi một seed may mắn là decoder rescue; báo cả repetition/EOS thoái hóa.

## 7. Tiền đăng ký thực thi, quyền dữ liệu và trần chi phí

**Những việc chưa hoàn thành, phải khóa một lượt trước GO science (không phải micro-permit):** 16 family x 2 fact x 2 length x 2 cue-position thành 128 prompt byte, 64 neutral prompts x0 và 32 candidate strings (2/family); bộ manifest private; xác nhận quyền tác giả nội dung tự soạn; so trùng SHA exact và đối chiếu ngữ nghĩa với FRESH12/FRESH16/CF1/Q1Q2/TEST/AC FINAL24 bằng chủ sở hữu có quyền; QA BPE, count, candidate equality, overflow=0; checkpoint/BPE/config hashes; seeds/sample order và rubric khóa; rater/custody tách biệt; một owner GO/HOLD cho toàn batch. Chỉ công khai SHA của private manifest và thống kê được phép, không đưa text/raw outputs/scores từng bản ghi/mapping/key/seed lên GitHub.

**Ngân sách science dự kiến nhưng chưa được phép:** 512 rollouts×≤64=≤32.768 token mới; 384 candidate scores×≤12=≤4.608 token; tổng trần **≤37.376 token output/target**, chưa tính prefill. 0 optimizer steps, 0 TEST/Q1Q2, 0 rerun FRESH16, 0 API charge, 0 paid Colab, ưu tiên CPU; GPU chỉ sau owner GO riêng. Wall-clock ≤120 phút, RAM available ≥8GiB, lưu receipts trong root dự án. Sai SHA, vi phạm quyền, candidate BPE lệch, prompt overflow, checkpoint mismatch hoặc vượt ngân sách: dừng và ghi kết quả thực thi chưa hợp lệ, **không sửa rồi tái chạy trong cùng science batch**.

Trước chạy khóa SHA256 private manifest/text/tokens/seed/rubric và provenance; sau chạy khóa raw generations, blind scores, mapping, tally, verdict. Kết quả khoa học thực sự PASS/FAIL/INCONCLUSIVE đã phân xử mới ghi **nối thêm** lineage.md; review thiết kế, QA nguồn, lỗi hạ tầng không ghi lineage. L0015 không sửa/ghi lại.

## 8. Diễn giải được phép và quyết định GO/HOLD

| Quan sát khoa học tương lai | Hướng ưu tiên | Chưa được kết luận |
| --- | --- | --- |
| Preference mạnh, greedy yếu, sampling cải thiện nhiều seed | Decoder và rollout | Không phải chứng minh suy luận tổng quát |
| Preference mạnh, greedy yếu, sampling không cứu | Kiểm lỗi chuỗi sự kiện/goal | Không kết tội greedy |
| Short/near mạnh, long/far giảm | Kiểm cue distance/context | Không suy trực tiếp thiếu attention |
| Preference yếu cả short/near, rollout yếu | Cân nhắc thiết kế huấn luyện A/C rồi 2×2 **đã có** | Không tách data/loss/capacity |
| Kết quả trộn lẫn | INCONCLUSIVE, báo cả âm tính | Không sửa threshold/đẻ micro-permit |

**Phán quyết quản trị hôm nay:** **GO_DESIGN_FROZEN** — hợp đồng câu hỏi, biến, blueprint, phép đo, ngưỡng khám phá và trần đã cố định tại tài liệu này. **D1_DATA_BYTES=NOT_FROZEN; EXECUTABLE_PREREG=NOT_COMPLETED; SCIENCE_EXECUTION=HOLD; INFERENCE_EXECUTED=NO; NEW_TRAINING=HOLD; AC=NO_GO_PREEXEC; O1=DEFER; TEST=SEALED; FRESH16_RERUN=FORBIDDEN; lineage.md và main không thay đổi**. Không gọi design GO là science GO.

**Bước thực hiện tiếp theo:** TTM_SMALL4M_D1_NEW_DEV_STIMULUS_AND_EXECUTABLE_PREREG_SINGLE_OWNER_GO_HOLD — hoàn tất một gói DEV byte độc lập/quyền/QA BPE/seeds/rater và một quyết định owner GO/HOLD toàn batch, chưa thực thi trước khi có quyết định đó.
