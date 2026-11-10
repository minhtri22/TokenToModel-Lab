# TTM — Kiến trúc GPT-2 / Llama 4 / TTM và giả thuyết ý nghĩa-trạng thái (R1)

**Ngày nghiên cứu:** 2026-11-10. **Phạm vi:** một vòng khảo cứu nguồn và phát biểu giả thuyết, **DESK_RESEARCH_ONLY**, chưa inference hay training. **Đối tượng:** GPT-2 gốc, TTM P02-Small4M thực tế và Llama 4 Scout/Maverick; khảo sát hướng thay thế có nền tảng triết học/ngữ nghĩa, không lấy định luật vật lý làm tiền đề.  
**Source of truth:** GitHub nhánh `research/ttm-gpt2-llama4-philosophy-architecture-round1-20261110` từ `main` SHA `b57b44e7287f842e81050c1faee337f636333dd0`. Nhánh 2×2 ở `ed2cfcd3b8676e1a6a959d2f90aade35269ee117`, PR #13 ở `8399406cfca7855626a20e031d1cfb3c767d606f`; không sửa. Main lineage L0012 và PR13 lineage L0017 không hợp nhất.

## I. Nguồn được đọc và cấp độ bằng chứng

**Nguồn mã gốc (đọc trực tiếp qua GitHub):**
1. OpenAI `openai/gpt-2/src/model.py`, Git blob `230b83cc2ac7582b4a22e9db3c2d8916dfe2ea9a` ([nguồn](https://github.com/openai/gpt-2/blob/master/src/model.py)): cấu hình nhỏ chuẩn `n_ctx=1024, n_embd=768, n_head=12, n_layer=12`; causal self-attention, pre-LN, GELU MLP, learned positions. Bản nhỏ 124M tham số; bản GPT-2 tối đa 1.5B.
2. TTM `src/p02/transformer_core.py`, Git blob `9762343e06cf800b50574c2871ae1ed58537fb18` ([nguồn](https://github.com/minhtri22/TokenToModel-Lab/blob/b57b44e7287f842e81050c1faee337f636333dd0/src/p02/transformer_core.py)); T4 thực tế dùng 3.749.376 tham số, vocab2048, context256, d_model256, layer4, head4, LayerNorm; learned position + token embeddings, causal MHA, pre-LN, GELU 4× MLP, tied output head. Không có lớp trạng thái thực thể/ý định tường minh.
3. TTM `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py`, Git blob `76c4d0155cd0736919f41682f240b47ad3d7c428` ([nguồn](https://github.com/minhtri22/TokenToModel-Lab/blob/b57b44e7287f842e81050c1faee337f636333dd0/tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py)): next-token CE `ignore_index=-100`, 4096 valid targets/step, nguồn TRAIN đã khóa; không có objective dành riêng cho entity/goal continuity.
4. Meta `meta-llama/llama-models/models/llama4/MODEL_CARD.md`, Git blob `80e624a8f7415bd533070277cc6b9f3c5215625b` ([nguồn](https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md)); license Git blob `ce807287a1cd38e1ed0f8e5eaaa925292e3f6903` ([nguồn](https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE)). Scout/Maverick là open-weight dưới **giấy phép cộng đồng tùy chỉnh**, không tự đồng nhất với open-source unrestricted. Không tải/trộn/copy trọng số Llama 4 vào TTM.
5. TTM FRESH12 phân xử scope ([nguồn](https://github.com/minhtri22/TokenToModel-Lab/blob/8399406cfca7855626a20e031d1cfb3c767d606f/docs/pilot/ttm-small4m-source-of-truth/TTM_FRESH12_OWNER_CONTROLLED_UNBLIND_AND_SCOPED_QUALITY_ADJUDICATION_20261110.md)): 35/48 đoạn adherence 0, Δ trimmed−baseline 0,000/3, reviewer Codex AI một phiên; **NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED**. Đây không chứng minh kiến trúc GPT-2 bất khả thi.

**Nguồn lý luận/công trình:** OpenAI GPT-2 (2019) https://openai.com/index/better-language-models/ ; Meta Llama 4 (2025) https://ai.meta.com/blog/llama-4-multimodal-intelligence/ ; Eldan & Li, *TinyStories* (2023) https://arxiv.org/abs/2305.07759 ; Wittgenstein (Stanford Encyclopedia) https://plato.stanford.edu/entries/wittgenstein/ ; Discourse Representation Theory, Hans Kamp/Heim (Stanford Encyclopedia) https://plato.stanford.edu/entries/discourse-representation-theory/ ; Schank & Abelson, *Scripts, Plans, Goals, and Understanding* (1977) https://www.routledge.com/Scripts-Plans-Goals-and-Understanding-An-Inquiry-Into-Human-Knowledge-Structures/Schank-Abelson/p/book/9780203781036 ; Harnad, *The Symbol Grounding Problem* (1990) https://www.southampton.ac.uk/~harnad/Papers/Harnad/harnad90.sgproblem.html ; Kim & Schuster (ACL 2023) https://aclanthology.org/2023.acl-long.213/.

**Phân biệt:** kiến trúc và kết quả TTM = nguồn thực; chi tiết Llama 4/GPT-2 = tài liệu và mã nhà phát triển; ý tưởng ý nghĩa-trạng thái và xếp ưu tiên bên dưới = **suy luận/giả thuyết mới**, chưa được kiểm nghiệm trên TTM.

## II. So sánh bản chất, không đánh đồng kích thước

| Chiều | GPT-2 nhỏ 124M | TTM-Small4M hiện có | Llama 4 Scout/Maverick |
|---|---|---|---|
| Lõi | Decoder-only dense Transformer | Decoder-only dense Transformer tương tự GPT-2 | Decoder-only MoE Transformer + multimodal |
| Tham số | 124M | **3,749,376** | **17B active**; Scout **109B total**, Maverick **400B total** |
| Vị trí | Learned absolute | Learned absolute | iRoPE: RoPE xen kẽ lớp attention không positional embedding |
| Chú ý | Causal MHA | Causal MHA 4 head | Attention tối ưu cho ngữ cảnh dài; kiến trúc kết hợp MoE |
| Feed-forward | Dense GELU | Dense GELU | Xen kẽ dense/MoE, chuyên gia được định tuyến |
| Tri thức tình huống | Ngầm định trong hidden states | Ngầm định trong hidden states | Ngầm định trong hidden states, không mặc nhiên có sổ trạng thái logic |
| Dữ liệu/mục tiêu | Next-token, nguồn đa dạng khổng lồ | Next-token, 2.048 truyện TRAIN gốc | Pretraining cực lớn, mid/post training, nhiều nguồn |
| Khả thi với free T4 16GB | Từ đầu tốn kém trong ngân sách hiện có | **Đã thực thi** | **Không chạy quy mô gốc**: 109B trọng số ở 4 bit lý tưởng đã ~54,5 GB chỉ cho giá trị weights |

**Không suy ra** GPT-2/MHA/CE là nguyên nhân tất yếu của tình trạng bám prompt yếu. *TinyStories* báo cáo các LM dưới 10M tham số có thể tạo truyện mạch lạc với điều kiện dữ liệu/huấn luyện riêng. Ở chiều ngược lại, biến TTM thành MoE 4M sẽ khiến mỗi expert nhận ít tham số và có thể làm chất lượng giảm; **chưa có bằng chứng TTM riêng** rằng MoE tốt hơn dense. Mạnh ở ngữ cảnh dài/multimodal không chứng minh bám nhân vật/mục tiêu ở 64-token continuation tốt hơn cùng ngân sách.

## III. Nền tảng triết học có thể chuyển thành toán và phép thử

### P1 — Ý nghĩa gắn với sử dụng (*meaning as use*, Wittgenstein)

Một câu chuyện không chỉ là chuỗi từ đúng xác suất: lời nói có tác dụng thông báo, hứa, hỏi, nhờ, đáp lại; ý nghĩa được thể hiện trong hoàn cảnh sử dụng. **Giả thuyết kỹ thuật**: một chương trình học có nhiệm vụ nhỏ/đối chứng hành động rõ ràng có thể học tiếp nối đúng mục tiêu hiệu quả hơn chỉ thay CE theo vị trí token. **Đo**: tình huống giống nhau nhưng mục tiêu khác nhau có khiến continuation thay đổi phù hợp không?

### P2 — Nghĩa là cập nhật ngữ cảnh theo thời gian (*dynamic/discourse semantics*, Kamp/Heim)

Thay vì lưu chỉ token, duy trì trạng thái trừu tượng `S_t` gồm thực thể, đồ vật, vị trí, sở hữu, mục tiêu, sự kiện, tình trạng còn hiệu lực. Mỗi sự kiện `e_t` cập nhật: `S_(t+1) = U(S_t, e_t)`; xác suất sinh có điều kiện `P(token_(t+1) | tokens_<=t, S_t, goal_t)`. Đây là **một mô hình giả thuyết** rút cảm hứng từ DRT, không phải thuật toán trực tiếp đã được DRT bảo chứng. **Đo**: giữ referent/pronoun, actor-object ownership, goal pursuit và cập nhật trạng thái sau hành động.

### P3 — Hiểu hành động thông qua kế hoạch và mục tiêu (*scripts, plans, goals*, Schank/Abelson)

Hành động được đánh giá bằng việc nó có tương thích với điều nhân vật muốn đạt hay không, không chỉ tần suất token. **Giả thuyết**: dự đoán `goal`/action-consistency hoặc trạng thái hậu sự kiện như mục tiêu phụ (auxiliary objective) có thể làm giảm việc đánh mất tuyến truyện. **Đo**: can thiệp đảo mục tiêu, đảo chủ sở hữu, đảo kết quả sự kiện rồi kiểm tra mô hình có phản ứng hợp logic.

### P4 — Ranh giới của ngữ nghĩa chỉ từ chữ (*symbol grounding*, Harnad)

Một bảng trạng thái do người nghiên cứu gắn nhãn **không tự chứng minh** máy hiểu ý nghĩa nội tại hay đã được grounded vào thế giới. Các thử nghiệm toy/text đo **năng lực giữ và sử dụng quan hệ trong văn bản**, không giải quyết bài toán nhận thức triết học đầy đủ. Không khẳng định mô hình có ý thức, hiểu biết theo nghĩa chủ quan, hay suy luận logic phổ quát.

**Kết luận triết học → phép thử:** ý nghĩa là việc giữ/biến đổi đúng trạng thái và mục tiêu trong hoàn cảnh, một tiêu chí có thể sai và kiểm định. Không cần dựng phương trình vật lý; vẫn cần toán, dữ liệu và bác bỏ thực nghiệm.

## IV. Năm phương án đáng cân nhắc trước khi gửi Codex

| Mã | Phương án | Độ khó tương đối | Khả thi T4 | Thông tin mới đem lại | Đánh giá R1 |
|---|---|---|---|---|---|
| O0 | Giữ P02, thử 2×2 data selection × position-weighted CE đã thiết kế | Thấp/vừa | Có thể khi resume/rights PASS | Nguyên nhân data-vs-loss | **Giữ làm đối chứng**, chưa GO |
| O1 | Giữ P02 + *entity/goal auxiliary state objective* ở lớp/đầu phụ, cân bằng params/compute | Vừa | Có khả năng | Kiểm tra liệu giám sát quan hệ trực tiếp có giúp hơn suffix CE | **Ưu tiên khảo cứu R2** |
| O2 | P02 + số nhỏ *relational/state slots* có update có kiểm soát | Vừa/cao | Có thể với thiết kế nhỏ | Kiểm tra memory/representation thực thể riêng khỏi token | R2 sau O1 |
| O3 | GPT-2-lite cải tiến RoPE/RMSNorm/SwiGLU/GQA (mỗi lần một yếu tố) | Vừa | Có thể | Hiệu quả tối ưu vị trí/cache/FFN | Phụ, chưa chứng minh semantic gain |
| O4 | Tiny MoE dựa ý tưởng Llama 4, 2–4 experts, giữ ~4M params | Cao | Chưa chứng minh hiệu quả | Kiểm tra specialization/router | **Không ưu tiên** ở 4M |

**Cảnh báo công bằng:** O1 thêm head, nhãn hoặc token cấu trúc không phải cải tiến “miễn phí”. So cùng checkpoint, cùng tokenizer/vocabulary, **tổng tham số nằm trong sai số thiết kế khóa**, cùng số valid target/optimizer steps, cùng số token và FLOPs đo thực; nếu thêm thông tin oracle trong prompt thì phải tách riêng thử nghiệm `EXTRA_INFORMATION` chứ không gán thắng lợi cho kiến trúc. Không dùng các prompt FRESH12 và Q1Q2/TEST đã tiêu thụ để chọn phương án.

## V. Thí nghiệm khả thi nhất từ triết học — chưa chạy

**R2A: kiểm tra giả thuyết trạng thái trước GPU, trên bộ truyện tự sinh nhỏ**

1. Xây một ngữ pháp toy story với vài nhân vật, vật thể, vị trí, mục tiêu, động tác và kết quả; oracle state `S_t` tự tính từ các quy tắc được đóng băng; dữ liệu tự tạo, không đụng corpus private. Sử dụng **bộ kiểm logic độc lập** xác nhận truyện/trạng thái/sự kiện.
2. Sinh các cặp phảnfactual chỉ khác **một** mục tiêu hoặc quan hệ sở hữu, giữ từ vựng và độ dài tương đương. Phân TRAIN/DEV/FUTURE BLIND_FINAL theo **mẫu cấu trúc/quan hệ** để tránh học thuộc khuôn; kiểm train-test near duplicate.
3. Thử rẻ nhất: **diagnostic không huấn luyện** để kiểm liệu frozen P02 phản ứng ra sao với `same-length factual context` so với `same-length shuffled state context`. Hai prompt có cùng số token thông tin và vị trí, tránh đưa đáp án vô tình vào câu hỏi. Kết quả có thể không phân biệt do P02 chưa từng học cú pháp nhãn.
4. Chỉ nếu có tín hiệu đáng tin và owner freeze, so O0 với O1 theo **cùng data/supervision budget**, nêu rõ nhãn phụ được tạo bằng oracle và coi đó là **nguồn thông tin huấn luyện mới**. Đo riêng `entity accuracy`, `goal-consistency`, `event transition`, `adherence`, `VAL NLL`, bộ nhớ, thời gian.
5. Kiểm định bác bỏ: nếu chỉ thắng trên tên nhân vật quen/truyện giống TRAIN, hoặc thắng nhờ oracle rò đáp án, hoặc tăng token/compute/params mà không điều chỉnh đối chứng, **không gọi semantic gain**.

**Ví dụ quan hệ trừu tượng** (không phải prompt khoa học đã tiêu thụ): “Lan giữ chiếc chìa khóa. Lan đưa khóa cho Minh. Minh muốn mở cửa.” Trạng thái cuối có `holder(key)=Minh`, `goal(Minh)=open(door)`. Câu tiếp nối hợp lý phải không tự nói Lan vẫn cầm khóa nếu không có sự kiện chuyển ngược. Đây là kiểm tra tính nhất quán nhân quả của truyện, **không** chứng minh hiểu thế giới vật lý.

## VI. Quyết định R1 — điều gì nên làm và không nên làm

**R1_RESEARCH_COMPLETED_DESK_ONLY**, chưa có science result. Chưa nên gửi Codex handoff review 2×2 cho mục tiêu chạy GPU hoặc phát hành science lock, vì khảo cứu cho thấy **một yếu tố chưa được đối chiếu**: bám prompt có thể cần trạng thái/mục tiêu tường minh thay vì chỉ thay phân phối cửa sổ và vị trí loss. Tuy nhiên, O1/O2 **chưa được chứng minh ưu việt**; giữ 2×2 làm baseline khả dụng, không xóa.

**Khuyến nghị vòng kế tiếp:** R2A `TTM_SMALL4M_SEMANTIC_STATE_GOAL_FORMAL_HYPOTHESIS_AND_NO_TRAINING_TOY_FEASIBILITY`. Chỉ khóa ontology tối thiểu, oracle/test negative, so sánh cùng information budget và đường dữ liệu/supervision; không mở T4 hay thay mô hình đã khóa. Cuối R2 trình một lựa chọn **O0-only vs O0+O1 prospective ablation** trước khi làm handoff Codex. Người nghiên cứu nội bộ chỉ gồm owner, ChatGPT Web và Codex nếu cần — **không yêu cầu reviewer tổ chức/human bên ngoài cho vòng khám phá**, nhưng biên bản phải ghi rõ không có external validation.

**Bảo toàn:** `2X2_COLAB=HOLD`, `PR13=DRAFT_HOLD`, `MAIN=UNCHANGED`, `MAIN_LINEAGE=L0012_UNCHANGED`, `PR13_LINEAGE=L0017_UNCHANGED`, `CHECKPOINTS=UNCHANGED`, `TRAIN/VAL/TEST=UNTOUCHED`, `Q1Q2=UNTOUCHED`. Không có thay đổi nào lên hai nhánh cũ.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_SEMANTIC_STATE_GOAL_FORMAL_HYPOTHESIS_AND_NO_TRAINING_TOY_FEASIBILITY`. Sau đó mới cân nhắc handoff Codex cho phê bình lý luận và kiểm thử độc lập, không phải reviewer điểm mù sớm.
