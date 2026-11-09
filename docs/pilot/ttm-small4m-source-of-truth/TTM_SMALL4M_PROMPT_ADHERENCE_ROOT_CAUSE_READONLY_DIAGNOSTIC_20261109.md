# TTM-Small-4M — Chẩn đoán chỉ đọc nguyên nhân bám prompt yếu

**Ngày:** 2026-11-09 · **Nhiệm vụ:** `TTM_SMALL4M_PROMPT_ADHERENCE_ROOT_CAUSE_READONLY_DIAGNOSTIC` · **Đối tượng:** hai checkpoint T4 gốc tại bước 1.024 và 1.280, 32 mẫu sinh đã khóa từ 8 prompt mới · **Trạng thái:** `DIAGNOSTIC_COMPLETED_PROMPT_SERIALIZATION_CONFOUND_FOUND`.

**Ranh giới:** không huấn luyện, không sinh thêm token, không đọc TEST hoặc bộ Q1/Q2 đã tiêu thụ, không đổi trọng số/model source, không thay đổi `main`, `lineage.md`, hoặc trạng thái merge của PR #13. Chỉ đọc các tệp đầu vào đã đóng băng; các tệp báo cáo/QA mới là hiện vật phân tích, không phải thay đổi dữ liệu nghiên cứu.

## 1. Nguồn và tính tương đương suy luận P02

- `src/p02/transformer_core.py` Git blob **`9762343e06cf800b50574c2871ae1ed58537fb18`** tại `main` đã ghim `b57b44e7287f842e81050c1faee337f636333dd0`; bản byte sử dụng có SHA-256 **`e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`** và Git blob khớp.
- Checkpoint 1.024 SHA-256 **`cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`**; checkpoint 1.280 SHA-256 **`ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`**. Cả hai ghi cùng `p02_git_blob`, cấu hình `BPE2048 / context256 / embd256 / layer4 / head4 / layernorm` và nạp PyTorch `strict=True`.
- Cùng phần cứng CPU/PyTorch 2.10.0, đối chiếu **16 chuỗi mỗi checkpoint**, gồm 8 prompt gốc và 8 cửa sổ TRAIN. Mỗi checkpoint **3.373.056 logit**; tất cả tensor canonical P02 và bộ sinh độc lập trước đây **trùng tuyệt đối** (`torch.equal=True`; `max_abs_diff=0`). Không thấy sai lệch attention mask, residual, LayerNorm hay tied embedding trong đường truyền xuôi ở phạm vi kiểm thử.
- **Giới hạn:** chưa kiểm thử parity với GGUF/Ollama, GPU FP16, mọi độ dài ngữ cảnh, hay những phép suy luận ngoài 16 chuỗi này. Đây không phải khẳng định parity toán học phổ quát.

## 2. Nguồn dữ liệu và nhãn next-token

Pack TRAIN/VAL riêng tư nguyên bản SHA-256 **`184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`**; manifest khai báo `contains_test=false` và chỉ có 8 mảng TRAIN/VAL.

| Hạng mục | Kết quả |
|---|---:|
| TRAIN stories | 2.048 |
| TRAIN windows dài tối đa 256 | 2.691 |
| Các nhãn TRAIN next-token duy nhất trong pack | 498.287 |
| Số cửa sổ đủ 256 nhãn | 652/2.691 (24,23%) |
| Số cửa sổ ngắn hơn 64 nhãn | 302 |
| Tổng budget nhãn qua 1.280 bước × 4.096 | 5.242.880 |
| Budget/nhãn TRAIN duy nhất | 10,52× (tỷ số danh nghĩa, **không phải** số epoch đều nhau) |
| Các cặp label-shift kề nhau được rà soát | 495.596, lỗi 0 |
| Nhãn EOS cuối truyện | 2.048, một/truyện |

Mã `t4_data_pack.py` chia các truyện thành cửa sổ riêng, không nối chuyện, `x=tokens[:-1]`, `y=tokens[1:]`, dùng `-100` để loại nhãn đệm. Mã `t4_train_science_a2.py` lấy mẫu cửa sổ TRAIN, tính `F.cross_entropy(..., ignore_index=-100)` trên các token kế tiếp và dùng 4.096 nhãn thực mỗi bước. **Không phát hiện lỗi nhãn dịch một bước hoặc vô tình dùng TEST** trong mã và pack đã xác minh. Mục tiêu huấn luyện là dự đoán token kế tiếp (next-token objective), không phải mất mát chuyên biệt về giữ nhân vật, mục tiêu hay thực hiện chỉ dẫn.

## 3. Phát hiện chính: điều kiện dấu cách cuối prompt

Cả 8 prompt của phép thử chất lượng trước đều kết thúc bằng dấu cách ASCII. Với tokenizer gốc, dấu cách cuối trở thành BPE token **ID 32 riêng biệt**, không phải một phần của token từ tiếp theo.

**Bằng chứng từ TRAIN (chỉ số tổng hợp, không xuất bản văn bản riêng tư):**
- Token đầu vào standalone space `32` xuất hiện ở **2.101/498.287** vị trí có nhãn (**0,4216%**).
- Trong các vị trí đó, nhãn kế tiếp là xuống dòng `10` trong **1.612/2.101** trường hợp (**76,7254%**), trong khi tỷ lệ xuống dòng nói chung chỉ **8.903/498.287 = 1,7867%**. Tỷ số mô tả ≈ **42,94 lần**. Đây là phân bố điều kiện, không phải ước lượng tác động nhân quả toàn câu truyện.
- Trong **16/16 mẫu greedy gốc**, token sinh đầu là ID 10 (`\n`), tiếp đó thường rời tình huống sang mô-típ truyện chung.

**Ablation logits-only, không sinh văn bản mới:** loại đúng dấu cách cuối và tính lại phân bố dự đoán token kế tiếp trong cùng checkpoint:

| Đo theo 8 prompt | Bước 1.024 | Bước 1.280 |
|---|---:|---:|
| P(next token là `\n`) khi CÓ dấu cách cuối | 38,28% | 36,80% |
| P(next token là `\n`) khi BỎ dấu cách cuối | 2,38% | 3,05% |
| Khoảng cách phân bố total variation trung bình | **0,8303** | **0,8261** |
| Token tham lam đầu khi CÓ dấu cách | 8/8 là xuống dòng | 8/8 là xuống dòng |
| Token tham lam đầu khi BỎ dấu cách | 0/8 là xuống dòng | 0/8 là xuống dòng |

Thay đổi dấu cách làm biến đổi mạnh phân bố token kế tiếp và đảo quyết định greedy đầu tiên. Đây là **lỗi thiết kế prompt/chuẩn hóa đầu vào trong phép so sánh chất lượng**, không phải lỗi triển khai BPE hoặc P02. Chưa có phép sinh/đánh giá chất lượng nào sau khi sửa dấu cách, nên không được kết luận sửa là đủ để cải thiện mạch lạc hoặc bám prompt của toàn bộ đoạn sinh.

## 4. Mức sử dụng ngữ cảnh và độ bao phủ TRAIN

Thăm dò logits-only giữa `full prompt` và `4 BPE tokens cuối` (vẫn giữ token khoảng trắng) cho khoảng cách total variation trung bình **0,2395** tại bước 1.024 và **0,3056** tại bước 1.280. Hai checkpoint **có phản ứng với phần ngữ cảnh trước**, không phải hoàn toàn chỉ nhìn token cuối. Do phép cắt cũng thay đổi position embedding, chỉ số này **không đo riêng việc nhớ chủ thể/ngữ nghĩa**.

Kiểm tra tần suất thuật ngữ được chỉ định trong TRAIN cho thấy các tên **Nora, Lumo, Pip, June, Lina** có **0** lần; cụm `silver bell`, `blue hat` và từ `lantern` cũng **0**. Ngược lại, một số mô-típ quen thuộc xuất hiện nhiều: `Lily` **2.902**, `mom` **2.336**, `park` **629**, `tree` **486**, cụm `One day` **1.513** lần. Đây là các đếm cụm/từ không phân biệt hoa-thường trên 2.048 truyện TRAIN, không phải bằng chứng trực tiếp của memorization/overfitting.

**Giải thích được hỗ trợ:** lựa chọn prompt dùng nhiều tên/cụm hiếm trong một tập TRAIN rất nhỏ, còn mục tiêu học là next-token trên mẫu truyện ngắn. Khi decoder đi vào ngữ cảnh xuống dòng có xác suất cao, mô hình dễ chuyển sang các mô-típ câu chuyện phổ biến. **Chưa thể tách riêng** đóng góp của sự hiếm tên, ngân sách/kiến trúc 3,75M tham số, cách lấy mẫu cửa sổ và lỗi serialization lên toàn bộ chất lượng sinh.

## 5. Phân loại nguyên nhân và quyết định

| Giả thuyết | Kết quả trong phạm vi kiểm tra |
|---|---|
| Suy luận CPU viết khác P02 gốc | **Không tìm thấy**: tensor logits trùng tuyệt đối trên các probe |
| Sai lệch nhãn x/y next-token | **Không tìm thấy**: 495.596 cặp nhãn khớp, EOS đúng |
| Prompt kết thúc bằng dấu cách độc lập làm lệch token đầu | **ĐƯỢC XÁC MINH cho phân bố token đầu**; rất có khả năng gây nhiễu kết quả chất lượng |
| Tên/vật thể mới ít có trong TRAIN và mô-típ chung chiếm ưu thế | **Có bằng chứng phân bố TRAIN hỗ trợ**; chưa xác nhận hiệu ứng nhân quả đầy đủ |
| Mô hình không sử dụng ngữ cảnh trước | **Không được hỗ trợ**: phân bố đổi khi cắt ngữ cảnh, nhưng chưa xác nhận bám ngữ nghĩa |
| Huấn luyện thêm sẽ giải quyết bám prompt | **Không có bằng chứng để kết luận** |

**Phán quyết:** `READONLY_ROOT_CAUSE=PASS_SCOPED_DIAGNOSTIC` · `PRIMARY_EVALUATION_CONFOUND=TRAILING_SPACE_SERIALIZATION_FOUND` · `P02_PARITY=PASS_CPU_16_CONTEXTS_EACH` · `NEXT_TOKEN_LABEL_QA=PASS` · `SEMANTIC_PROMPT_ADHERENCE_REMEDIED=NOT_TESTED`.

Giữ nguyên phát hiện trước `QUALITY_GAIN=NOT_DEMONSTRATED_SCOPED` **chỉ trong điều kiện prompt đã dùng**. Không dùng phép chấm mù đó làm bằng chứng tổng quát rằng mô hình 1.280 không có khả năng tiếp nối prompt chuẩn; kết quả có nhiễu do định dạng đầu vào.

## 6. Giới hạn QA, quản trị và bước thực hiện tiếp theo

- QA tái tính số học/mã SHA: **22/22 PASS phạm vi kỹ thuật**. Không phải reviewer khoa học độc lập, không đo chất lượng sinh sau sửa, không dùng TEST/Q1/Q2.
- Các file PRIVATE chỉ đọc: `step_1024.pt`, `step_1280.pt`, `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz`, BPE merge private. **Không đưa nội dung checkpoint, TRAIN/VAL tokens hoặc tokenizer private lên GitHub**.
- Không ghi thêm `lineage.md`: đây là chẩn đoán kỹ thuật hậu nghiệm, không phải PASS/FAIL khoa học mới.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_PROMPT_SERIALIZATION_CONTROLLED_ABLATION_PREREG_AND_ONE_SMALL_INFERENCE_BATCH`. Thiết kế riêng một phép thử suy luận nhỏ (không train) với prompt bình thường hóa `rstrip(' ')`, cùng checkpoints, decoder, seed và tiêu chí bám nhân vật/sự kiện; đánh dấu đây là **thăm dò sửa confound hậu nghiệm**. Nếu muốn claim độc lập, phải dùng prompt mới chưa chấm và reviewer khác; không tái sử dụng Q1/Q2. Giữ main/PR HOLD cho tới quyết định riêng.
