# **Independent Review — TTM Vector Memory V4 R8 V3**

HOLD — G0 chưa đạt

DESIGN ONLY

READ ONLY

**Ngày:** 14/11/2026\
**Vai trò:** Independent AI Protocol Reviewer (người phản biện giao thức AI độc lập)\
**Commit kiểm toán:** `60c81935c44e72490f9a7a69a7e25c625c44c7ac`\
**Tài liệu:** [TTM VM V4 R8 V3 — Gold/F07/Cluster/Power Protocol](https://github.com/minhtri22/TokenToModel-Lab/blob/60c81935c44e72490f9a7a69a7e25c625c44c7ac/docs/research/vector-memory/r8/TTM_VM_V4_R8_V3_GOLD_F07_CLUSTER_POWER_PROTOCOL_CLOSURE_DESIGN_ONLY_20261114.md?utm_source=chatgpt.com)

Tôi đã đọc trực tiếp V3 qua GitHub, đối chiếu với V2, giao thức R8 ban đầu và các biên nhận phân xử R7/R8. Đây là kiểm toán nguồn tài liệu tại commit cố định, **không phải kiểm chứng dữ liệu R8, validator hoặc khả năng thực thi thực tế**.

## **1. Kết quả chấm độc lập**

| Blocker                          | Kết quả                          | Đánh giá                                                                                              |
| -------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **B01 — Gold & F07**             | **HOLD**                         | Ontology tiến bộ, nhưng chưa chứng minh được gold F07 có thể xác định độc lập và không tạo oracle mới |
| **B03 — Cluster & blind raters** | **HOLD**                         | Đúng nguyên tắc chống rò rỉ giữa folds, nhưng còn mâu thuẫn về thời điểm lập graph và phân bổ raters  |
| **B04 — Shortcut adversaries**   | **HOLD**                         | Có bộ 8 adversaries, nhưng chưa khóa đầy đủ đặc tả thực thi và còn thiếu kiểm soát target-key leakage |
| **B05 — Power & inference**      | **PASS_SCOPED_DESCRIPTIVE_ONLY** | Chấp nhận hạ phạm vi sang mô tả thăm dò; không chấp nhận chứng nhận loại bỏ shortcut                  |

PHÂN XỬ TỔNG THỂ

## **HOLD_R8_V3_G0_BLOCKERS_OPEN**

0 PASS đầy đủ · 1 PASS giới hạn · 3 HOLD · 0 FAIL cấu trúc đã xác nhận

**Kết luận khoa học:** V3 giải quyết được mâu thuẫn quan trọng về mục tiêu thống kê của V2. Tuy nhiên, V3 chưa đủ điều kiện G0 PASS vì phương án chấm mù chưa được lựa chọn chính thức, thuật toán cluster chưa thể khóa đúng trình tự và bộ kiểm tra shortcut chưa hoàn chỉnh.

Điểm quan trọng nhất: **hạ xuống exploratory descriptive là hợp lệ nếu R8 được coi là một nghiên cứu chẩn đoán mới, nhưng không hợp lệ nếu dùng kết quả đó thay cho mục tiêu chứng minh hệ thống đã khắc phục shortcut của R7.**

## **2. B01 — Gold ontology và tính khả thi F07**

**Kết quả: HOLD**

V3 đã cải thiện đáng kể cấu trúc đáp án vàng (gold ontology). Việc tách `candidate_entity_id` khỏi `card.key`, phân biệt thẻ đích (target card) với thẻ chứng cứ (proof card), và sử dụng tập chứng minh tối thiểu (minimal sufficient proof sets) là phù hợp.

Tuy nhiên, còn ba vấn đề thực chất.

**Thứ nhất — một thực thể duy nhất không đồng nghĩa với một đáp án duy nhất.**

Ví dụ: hai chứng cứ đều nói về accession X, nhưng một chứng minh địa điểm L1 và chứng cứ khác chứng minh L2. Số lượng thực thể vẫn là một, nhưng đáp án về vị trí có thể chưa xác định.

Vì vậy, không nên chỉ dùng `|E|=1`. Cần xác định tính duy nhất của *answer hypothesis* gồm thực thể, sự kiện, vị trí và thời điểm hiệu lực.

**Thứ hai — câu hỏi F07 chưa phân biệt đầy đủ phủ định và thiếu chứng cứ.**

Câu hỏi V3 là:

> Was accession X physically received, and where?

Nếu có chứng cứ xác nhận X chưa được nhận, đây có thể là đáp án phủ định hợp lệ, không nhất thiết là ABSTAIN.

Cần xác định rõ bài toán là tìm *bản ghi nhận hàng đã được xác minh* hay trả lời câu hỏi có/không. Nếu là bài toán chọn bản ghi, nên diễn đạt câu hỏi theo hướng chọn bản ghi chứng minh địa điểm nhận hàng, và ABSTAIN khi không có một bản ghi đủ căn cứ.

**Thứ ba — chứng minh F07 mới hợp lệ có điều kiện.**

Chính sách P cho phép xác nhận nhận hàng bằng biên bản đối soát kiểm kê độc lập là khả thi về logic. Nhưng chưa có chứng cứ rằng chính sách đó được chấp nhận trong miền nghiệp vụ của nghiên cứu.

Hơn nữa, SELECT có thể lại bị suy ra từ sự hiện diện của một loại biên bản cụ thể. Cần đối chứng chứa cùng từ vựng, cùng loại chứng từ nhưng khác quan hệ chứng minh.

**Điều kiện đóng B01:** Khóa định nghĩa answer hypothesis, chính sách thẩm quyền P, cách xử lý phủ định/ABSTAIN và kiểm toán ít nhất một cặp F07 có chuyển đổi chân trị thực chất. Người kiểm toán phải suy ra gold từ chứng cứ và quy tắc đã khóa, thay vì chỉ xác nhận nhãn do generator cung cấp.

## **3. B03 — Độc lập thống kê, folds và blind raters**

**Kết quả: HOLD**

### **3.1. Connected-component graph: đúng ý tưởng, chưa đúng trình tự**

V3 yêu cầu xây dựng đồ thị rò rỉ (leakage graph) trước G3, với cạnh dựa trên cặp, event graph, template và độ tương tự văn bản.

Có một mâu thuẫn triển khai: nếu văn bản 64 cases chỉ được tạo trong G3 thì không thể tính đầy đủ các cạnh dựa trên fingerprint của văn bản trước G3.

Cách sửa hợp lệ là:

- Trước G3: khóa sơ đồ event/template, quy tắc nối cạnh, ngưỡng tương tự, thuật toán folds và manifest phân bổ dự kiến.
- Sau G3, trước khi sử dụng dữ liệu để đánh giá: kiểm tra toàn bộ cạnh từ văn bản thực tế theo thuật toán đã khóa.
- Nếu xuất hiện kết nối xuyên folds: đánh dấu candidate không hợp lệ cho CV đã tiền đăng ký; không chia lại folds dựa trên kết quả để cứu candidate.

Ngoài ra, schema V3 dùng `event_graph_component` nhưng thuật toán mô tả `event_graph_id`. Phải thống nhất định danh nguồn và định danh component được suy ra.

**Bốn components chỉ đủ về mặt hình thức cho bốn folds, không bảo đảm đánh giá độc lập có ý nghĩa.**

### **3.2. Phương án phân bổ blind raters nào hợp lệ?**

Đây là điểm tôi đề nghị sửa rõ nhất trong V4.

| Phương án                                | Kết quả                                               | Tính hợp lệ                                                           |
| ---------------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------- |
| **2 raters, chia đôi twins**             | A và B mỗi người 32 cases; mỗi case được chấm một lần | Hợp lệ cho chấm mù phân tách, không đo được đồng thuận trên cùng case |
| **2 raters, mỗi người chấm cả 64**       | Mỗi case có hai điểm                                  | Không tương thích quy tắc một rater không thấy cả hai twins           |
| **4 raters, mỗi case được chấm hai lần** | Mỗi rater thấy 32 cases, chỉ một twin/cặp             | Hợp lệ cho cả chống twin exposure và đánh giá đồng thuận              |

### **Phương án được khuyến nghị: 4 blind raters**

Minh họa phân bổ một cặp phản thực

Twin 1

SELECT hoặc ABSTAIN

A

B

Hai đánh giá độc lập

Twin 2

Nhãn đối lập

C

D

Hai đánh giá độc lập

Cách ghép A/B và C/D chỉ là minh họa. Trên toàn bộ 32 cặp, cần luân phiên nhóm rater và khóa phân bổ cân bằng trước khi chấm.

Với thiết kế này:

- 64 cases × 2 lần chấm = **128 đánh giá**.
- Mỗi rater nhận 32 cases, gồm 16 SELECT và 16 ABSTAIN, đồng thời cân bằng theo relation family.
- Không rater nào nhận cả hai twins của cùng một cặp.
- Có thể đo độ đồng thuận (interrater agreement) trên từng case.

Cần tiền đăng ký phép đo đồng thuận action, key và joint, cách xử lý bất đồng, đồng thời lấy bất định thống kê theo pair/component. **128 đánh giá không biến thành 128 đơn vị khoa học độc lập.**

Nếu bốn raters đều là các phiên GPT-6 riêng biệt, có thể gọi đây là *AI-assisted blinded replication*, nhưng không được coi bốn phiên là bốn người chấm độc lập ở cấp quần thể: chúng có thể chia sẻ thiên lệch hệ thống.

Phương án hai raters phân tách vẫn hợp lệ nếu mục tiêu chỉ cần một đánh giá mù trên mỗi case và bỏ yêu cầu độ đồng thuận.

**Kết luận B03:** V3 đã phát hiện đúng xung đột nhưng chưa giải quyết. Cần owner lựa chọn và khóa thiết kế trước G0 PASS.

## **4. B04 — Kiểm toán shortcut adversaries**

**Kết quả: HOLD**

V3 có một cải thiện lớn: bộ O1–O8 được định nghĩa cụ thể hơn, với logistic regression, TF-IDF, BM25, static oracle và cơ chế held-out theo component.

Đặc biệt, giữ oracle `applicable signed record` từ R7 làm hồi quy kiểm tra (regression test) là cần thiết.

Tuy nhiên còn hai lỗ hổng lớn.

### **4.1. O5 có thể phát hiện target-key shortcut nhưng không nằm trong nhóm kiểm định chính**

B05 hiện áp dụng Holm cho O2/O3/O4/O6.

Trong khi đó, O5 trực tiếp dự đoán gold key trên các SELECT cases.

Giả sử O5 đạt 20/32 target chính xác bằng metadata/marker đơn giản, thay vì mức ngẫu nhiên 1/32. Đây là dấu hiệu rất mạnh cho thấy key có thể bị rò rỉ, mặc dù O5 không đạt 32/32 và có thể không kích hoạt quy tắc FAIL hiện tại.

Không thể để một phát hiện như vậy được bỏ qua chỉ vì O5 không nằm trong bốn kiểm định chính.

**Yêu cầu:** Precommit riêng kiểm định shortcut cho target-key, cùng quy tắc báo động/phân xử và kiểm soát đa kiểm định phù hợp. Một oracle không hoàn hảo vẫn có thể chứng minh candidate có vấn đề.

### **4.2. Bộ adversaries chưa tái lập hoàn toàn**

Những thành phần cần khóa thêm gồm phiên bản scikit-learn chính xác, SHA của regex, quy tắc tính card-level weights trong O5, ánh xạ kết quả O6 sang action/key và cách tạo truy vấn BM25/TF-IDF.

Cũng cần phân biệt một baseline sử dụng đặc trưng ngữ nghĩa thực sự hợp lệ với shortcut dựa trên chỉ dấu ngoài ý muốn. Độ chính xác cao tự nó không chứng minh đó là leakage, trừ khi đặc trưng và đường suy luận vi phạm hợp đồng thông tin đã tiền đăng ký.

**Điều kiện đóng B04:** Có source artifact và kiểm toán tĩnh độc lập bảo đảm cùng byte, cùng môi trường, cùng fold và cùng input sẽ tái tạo được bộ O1–O8 trước khi chạy R8.

## **5. B05 — Có nên chuyển thành exploratory descriptive không?**

**Kết quả: PASS_SCOPED_DESCRIPTIVE_ONLY**

Tôi chấp nhận thay đổi này về mặt phương pháp luận, nhưng phải tách rõ hai mục tiêu.

### **Mục tiêu A — Chẩn đoán thiết kế**

R8 có thể trả lời:

> Trong 32 cặp phản thực thuộc tám họ quan hệ, những loại shortcut quan sát được là gì và mô hình/chủ thể chấm phản ứng thế nào trước các thay đổi chứng cứ?

Đây là câu hỏi khoa học thăm dò hợp lệ. Có thể phân tích định tính, tỷ lệ lỗi, sự thay đổi theo từng họ quan hệ và kết quả các oracle.

### **Mục tiêu B — Chứng minh đã loại bỏ shortcut**

R8 không thể kết luận đáng tin cậy rằng shortcut đã bị loại bỏ, đặc biệt khi kích thước mẫu hữu hiệu chưa biết và các ví dụ có thể phụ thuộc lẫn nhau.

Minh họa công suất (power) trong trường hợp lạc quan

Giả sử các đơn vị Bernoulli độc lập, accuracy thật = 0,625; null = 0,5; kiểm định nhị thức chính xác hai phía ở α = 0,0125 (mức bảo thủ của bốn kiểm định).

| 8 đơn vị độc lập             | ≈ 2,4% |
| ---------------------------- | ------ |
| 32 đơn vị độc lập            | ≈ 9,8% |
| Mục tiêu nghiên cứu xác nhận | ≥ 80%  |

Đây là phép tính minh họa của một kiểm định nhị thức, không phải công suất đã được chứng minh của quy trình R8. Phụ thuộc giữa các components và việc huấn luyện oracle có thể thay đổi phân phối kiểm định.

Nói cách khác, nếu mức shortcut thật chỉ cải thiện accuracy từ 50% lên 62,5%, một nghiên cứu với 32 đơn vị độc lập có thể không phát hiện được trong khoảng 90% trường hợp theo giả định minh họa này.

Vì vậy, quy tắc của V3:

`NON_SIGNIFICANT ≠ NO_SHORTCUT`

là đúng.

Tuy nhiên, để giữ B05 PASS trong phạm vi mô tả, cần diễn giải mọi `PASS_SCOPED_DESCRIPTIVE_QA` chỉ là **hoàn thành kiểm toán và báo cáo**, không phải quyền chuyển sang CAL hoặc chứng nhận ứng viên đạt yêu cầu chống shortcut. Các kiểm định không ước lượng được phải công khai dưới trạng thái `NOT_ESTIMABLE`, không được biến thành điểm PASS thuận lợi.

### **Quyết định về mục tiêu khoa học**

Tôi đề nghị tách hai nhánh kết luận:

**R8-D — Exploratory Descriptive**

Giữ 32 cặp. Mục tiêu là khảo sát hành vi, chẩn đoán leakage và thu thập bằng chứng để thiết kế thử nghiệm tiếp theo. Được chấp nhận về nguyên tắc sau khi sửa B01/B03/B04 và hoàn tất các gate.

**R8-C — Confirmatory Anti-shortcut**

Chưa được cấp phép. Cần một giao thức tiền đăng ký riêng, nhiều components độc lập hơn, công suất đủ mạnh và kiểm soát đầy đủ các shortcut action lẫn target-key.

Không nên dùng thành công của R8-D để thay thế bằng chứng cần thiết của R8-C.

## **6. Phân xử gate và bước thực hiện tiếp theo**

| Gate                                         | Trạng thái sau review |
| -------------------------------------------- | --------------------- |
| G0 — Independent design review               | **HOLD**              |
| G1 — Owner adoption, rights, PII             | HOLD                  |
| G2 — Private custody, validator, source lock | HOLD                  |
| G3 — R8 generation                           | NOT AUTHORIZED        |
| G4 — Candidate QA                            | NOT EXECUTED          |
| G5 — Blind CAL                               | SEALED                |
| G6 — Threshold / PROBE256                    | SEALED                |

### **Bước thực hiện tiếp theo**

`TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY`

Một bản sửa đổi V4 tích hợp nên thực hiện bốn việc trong cùng một lượt: hoàn thiện answer hypothesis và F07; sửa thứ tự khóa graph/folds; bổ sung hợp đồng phát hiện target-key shortcut cho O5; và khóa phương án bốn raters nếu yêu cầu hai đánh giá trên mỗi case.

Owner cần phân xử rõ `ADOPT_R8_D_DESCRIPTIVE_ONLY` hoặc `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO`. Sau đó mới tiến hành kiểm toán độc lập V4 tại G0, không phát sinh các micro-permit.

**Quyết định cuối cùng của reviewer:**

`HOLD_R8_V3_THREE_BLOCKERS_OPEN_DESCRIPTIVE_SCOPE_CONDITIONALLY_ACCEPTABLE_NO_GENERATION`

Tôi không phát hiện lý do phải bác bỏ toàn bộ hướng nghiên cứu R8. Nhưng cũng không có căn cứ để cấp G0 PASS ở V3. Phương án khoa học hợp lý nhất là giữ R8 làm nghiên cứu chẩn đoán có kiểm soát, đồng thời bảo lưu mục tiêu chứng minh chống shortcut cho một nghiên cứu xác nhận độc lập sau này.

Phạm vi kiểm toán: tài liệu GitHub read-only; không sửa commit, không tạo candidate, không truy cập private gold và không thực thi khoa học. Kết quả này là đánh giá độc lập của AI, không thay thế xác nhận của owner hoặc kiểm toán viên con người.