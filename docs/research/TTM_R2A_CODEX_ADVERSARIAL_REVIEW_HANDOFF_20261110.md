# HANDOFF — Codex phản biện đối kháng bản R2A (chưa thực hiện)

**Phạm vi:** đọc-only độc lập, không tự merge/huấn luyện/test TTM, không dùng checkpoint, TEST/Q1Q2. Nguồn canonical: [R2A QA index](../../artifacts/qa/ttm-r2-semantic-toy/r2a/README.md) của branch `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`. Pin commit hiện hành khi tiếp nhận từ GitHub HEAD, không dựa trên HEAD cũ của R2.

Codex cần đánh giá rằng lối tắt câu thứ ba được loại bỏ, nhưng **bất kỳ quy tắc khác không cần key-binding** còn tồn tại hay không. Đặc biệt kiểm: positional heuristics biết split/grammar, pattern of query wording, lexical-frequency cues, ID leakage, cặp phản thực cùng word-bag, 128 query-swap probes, việc checker so `counts` và không dùng `source_events` làm đáp án, model input chỉ có `story` và `question`.

Kiểm tra thêm các mutation độc lập ngoài 19 ca âm tính nội bộ; không dùng chung source oracle để làm checker; công bố bất cứ bypass nghiêm trọng nào theo **PASS/FAIL scoped**, không mặc định O1 đã có căn cứ. Đánh giá tính công bằng của prospective O0 CE vs O0 supervision bằng text vs O1 shuffled-label vs O1 true-label vs O0 capacity matched; phân biệt nhãn oracle TRAIN và thông tin ở inference.

Phản biện không có nghĩa vụ cấp quyền Colab hay quyết định thay dữ liệu huấn luyện. Nếu còn shortcut đủ để đạt 100% mà không đọc câu hỏi, `R2A_DISCRIMINATION=FAIL/HOLD` và đề nghị sửa hợp đồng trước. Nếu phép thử pass, chỉ chốt `TOY_DISCRIMINATION_READY`; `NEURAL_GAIN=NOT_TESTED`.

**Bước thực hiện tiếp theo:** phân xử duy nhất **O0-only vs thiết kế O0+O1**, không tự khởi động GPU. Reviewer AI nội bộ không được tuyên bố external independent validation.
