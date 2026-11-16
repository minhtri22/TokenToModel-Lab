# Dive into LLMs — Thư viện học tập tiếng Việt (Vietnamese study companion)

**Ngày kiểm kê:** 2026-11-16 · **Trạng thái:** `DOCS_ONLY / SOURCE_REVIEWED / FULL_TRANSLATION_HOLD_RIGHTS`  
**Nguồn:** [Lordog/dive-into-llms](https://github.com/Lordog/dive-into-llms) · **upstream exact commit:** [`f84c04268794ef94f8949808bbc14ab8636763a0`](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0)  
**Bản README đã đọc:** Git blob `933f8fae9ba3cf9fd0a3d314793749451b5bd0b2`. Git blob SHA-1 không phải SHA-256 evidence.

## Mục đích và giới hạn

Thư mục này là **bản hướng dẫn học tập và phân tích mới do TTM biên soạn bằng tiếng Việt**, không phải bản dịch/copy của sách gốc. Repository upstream chưa thấy giấy phép ở thư mục gốc (không có `LICENSE` trong listing tại ngày kiểm kê), và lời giới thiệu “miễn phí” không cấp quyền dịch/phân phối. Không chép lại nguyên văn các chương, notebook, ảnh hoặc PDF vào GitHub TTM cho đến khi có chấp thuận rõ từ người giữ bản quyền và xác minh giấy phép từng tài sản liên quan. Xem [RIGHTS_AND_PROVENANCE.md](RIGHTS_AND_PROVENANCE.md).

**Phạm vi TTM:** tài liệu học tập, không chỉnh kiến trúc, dataset, scorer, gold, scientific checkpoint, active gate, `lineage.md`.  
**Phạm vi CLDP:** tài liệu tham khảo từ xa; không thay thế các kết quả Layered Blackboard, Phase2F/2J hoặc quyết định Phase3F-R.  
**Không chạy:** notebook, API, download mô hình, đào tạo, GPU/CPU benchmark, thực nghiệm khoa học.

## Mục lục học tập (nguồn theo commit đã khóa)

| Chương upstream | Chủ đề bằng tiếng Việt | Giá trị chủ yếu | Nguồn |
|---|---|---|---|
| 1 | Tinh chỉnh mô hình và triển khai (Fine-tuning & deployment) | TTM: tách pipeline data/train/eval | [Ch.1](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter1) |
| 2 | Thiết kế prompt và chuỗi suy luận (Prompting & Chain-of-Thought) | TTM: đối chứng prompt/decoding; không nhầm với thay architecture | [Ch.2](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter2) |
| 3 | Chỉnh sửa kiến thức (Knowledge editing) | TTM/CLDP: độ tin cậy, khái quát hóa, tác động ngoài mục tiêu | [Ch.3](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter3) |
| 4 | Suy luận toán học (Mathematical reasoning) | TTM: phân biệt chất lượng dữ liệu/SFT với năng lực suy luận | [Ch.4](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter4) |
| 5 | Thủy vân văn bản (Watermarking) | Tham khảo: tính toàn vẹn đầu ra, không trực tiếp mở science gate | [Ch.5](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter5) |
| 6 | Đánh giá jailbreak (Jailbreak assessment) | An toàn và robustness; tránh đưa prompt độc hại vào pipeline thực | [Ch.6](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter6) |
| 7 | Giấu tin bằng LLM (Steganography) | Tham khảo an ninh; độ ưu tiên thấp cho TTM/CLDP | [Ch.7](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter7) |
| 8 | Mô hình đa phương thức (Multimodal LLMs) | Chưa thuộc mục tiêu TTM-4M/CLDP Phase3F hiện tại | [Ch.8](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter8) |
| 9 | Tác nhân GUI (GUI agents) | Tham khảo thiết kế điều phối, không là phép đo CLDP | [Ch.9](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter9) |
| 10 | An toàn tác nhân (Agent safety) | Học cách phân tách kiểm tra hành vi và kết luận an toàn | [Ch.10](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter10) |
| 11 | Căn chỉnh bằng phản hồi (RLHF/PPO) | TTM: hiểu reward/evaluation, không nhập runner huấn luyện | [Ch.11](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter11) |

Các liên kết trỏ trực tiếp đến bản nguồn upstream, **không** nhúng tài sản vào repository TTM.

## Lộ trình đọc hợp lý

- **TTM trước:** Ch.1 → Ch.2 → Ch.3 → Ch.4 → Ch.11. Quan sát sự khác nhau giữa xử lý dữ liệu, objective, evaluation và thay đổi khả năng mô hình.
- **CLDP trước:** Ch.3 → Ch.2 → Ch.10, dùng khái niệm về locality/generalization để *thiết kế phép đo* cho hành vi chức năng. CLDP không phải mô hình ngôn ngữ, nên đây là chuyển giao tư duy kiểm định, **không phải** bằng chứng cơ chế tương đồng.
- **Đọc song song:** [RESEARCH_DIRECTION_MATRIX.md](RESEARCH_DIRECTION_MATRIX.md) với câu hỏi bác bỏ, hard veto và chi phí.

## Thuật ngữ Việt–Anh

| Thuật ngữ | Nghĩa sử dụng trong TTM/CLDP |
|---|---|
| Tinh chỉnh có giám sát (Supervised Fine-Tuning, SFT) | Huấn luyện trên cặp đầu vào–đầu ra đã có nhãn |
| Khái quát hóa (Generalization) | Tác động đến biến thể hợp lệ ngoài mẫu huấn luyện |
| Tính cục bộ của can thiệp (Locality) | Không làm hỏng hành vi ngoài phạm vi mục tiêu |
| Đối chứng nguyên nhân (Causal control) | Tách cơ chế chính khỏi nhiễu, shortcut, đổi đánh giá |
| Tính tương đương chức năng (Functional equivalence) | Cùng hành vi quan sát trong phạm vi đã định nghĩa |
| Đăng ký trước (Preregistration) | Khóa câu hỏi, phép đo, điều kiện bác bỏ trước thực nghiệm |

## Clone upstream phục vụ đọc cục bộ

Chạy [Clone-DiveIntoLLMs-SourceReadOnly.ps1](Clone-DiveIntoLLMs-SourceReadOnly.ps1) trên PowerShell 5.1 nếu muốn lấy bản Git upstream **vào `_tmp/learningbooks` bên trong root TTM**. Script pin commit và chỉ checkout README các chương cần thiết bằng sparse-checkout; **không** tự đưa repository lồng nhau vào `docs/`, không commit tài liệu upstream, không chạy notebook. Clone thực tế cần mạng trên Windows và chưa được thực thi/xác minh trong phiên tạo nhánh này.

## Ranh giới governance

- `main` của TTM vẫn là nguồn thật cho trạng thái khoa học; nhánh tài liệu này **không được tự merge**. Các gate Q4 CLOSED_HOLD và E0–E6 HOLD giữ nguyên.
- `lineage.md` không thêm sự kiện documentation-only; QA nguồn, quyền dịch và nghiên cứu lý thuyết không phải scientific PASS/FAIL.
- Điều kiện đưa bản dịch đầy đủ lên GitHub: có quyền rõ ràng từ tác giả/chủ quyền, xác định phạm vi giấy phép tài sản, mapping file-by-file, kiểm tra bản dịch, QA độc lập và owner merge approval.
