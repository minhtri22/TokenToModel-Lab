# TTM R3 — Strict-input, structural state graph toy, one-shot CPU QA và phân xử nội bộ

**Ngày:** 2026-11-11 · **Task:** `TTM_R3_STRICT_INPUT_VALIDATOR_AND_STRUCTURAL_GRAPH_TOY_IMPLEMENTATION_SINGLE_CPU_QA`  
**Nhánh:** `research/ttm-r3-structural-state-tracing-design-20261111` (tiếp tục sau bản thiết kế `bf0ead9daca66be9f75522d7404469b5a8cb593a`).  
**Phạm vi:** Public synthetic toy; không gọi GPU, không train/val/test của TTM, không nạp checkpoint hay chạy inference mô hình neural; không làm thay đổi nguồn R2A đã bị Codex chỉ ra lỗi.

## 1. Nguồn GitHub nguyên vẹn — không cần tải ZIP

Mã thực thi, hai JSON dữ liệu đầy đủ và tất cả kết quả QA đều được commit trực tiếp lên GitHub:

| Nội dung | Đường dẫn trong repository | SHA-256 |
|---|---|---|
| Bộ sinh độc lập TTM | `tools/research/semantic_state_r3/r3_generator.py` | `8f8296ba2009f5b13b8c23bdb15a90519b524f39fb8c2884493b6ae63719a404` |
| Parser/checker *tách nguồn khỏi generator* | `tools/research/semantic_state_r3/r3_independent_checker.py` | `7acde2388149065e862f9561e36130747d7c597d86615d4ce0e390152d373984` |
| Bộ kiểm thử CPU tích hợp | `tools/research/semantic_state_r3/r3_single_cpu_qa.py` | `9c6bb8da606bd5df9d31d134810dcdee352e03017e241d3e67e91b2a1576c96e` |
| **Oracle JSON công khai, đầy đủ** | `artifacts/qa/ttm-r3-structural-design/runtime/R3_PUBLIC_ORACLE.json` | `bd9fb15d3f3850823e083269a61df90eaddaea3e61b8b73e9f40b4ec74c7ce47` |
| **384 đầu vào chỉ có story/question** | `artifacts/qa/ttm-r3-structural-design/runtime/R3_MODEL_INPUT_ONLY.json` | `4fa0ad45acdfecb2143a984127e6ad0c50126c203996148d60843eb1214cd50a` |
| Biên bản parser | `artifacts/qa/ttm-r3-structural-design/runtime/R3_CHECKER_REPORT.json` | `ed9c149d525b503d8cfe93b7716246797c3218ebbf420bfe852a1c8d7ebab088` |
| Log cuối 70 kiểm thử | `artifacts/qa/ttm-r3-structural-design/runtime/R3_CPU_TEST_LOG_FINAL.txt` | `0927768f7b156056d018b8df5b6180e7452ef08dbb2d73766144649ac36516e9` |
| Manifest chứa Git blob/SHA từng tệp | `artifacts/qa/ttm-r3-structural-design/runtime/R3_SOURCE_QA_MANIFEST.json` | `554dec4049421257de07230ce3821ec2ca0a1979708ba43f0f7e44723e108a1c` |
| Biên nhận quyết định & limitations | `artifacts/qa/ttm-r3-structural-design/runtime/R3_OWNER_SCOPED_CPU_QA_AND_DECISION_20261111.json` | GitHub blob đọc lại sau commit |

**Ghi chú chứng cứ:** Hai lượt sinh riêng có SHA-256 và nội dung nguyên byte giống nhau. Một ca kiểm thử đếm handoff ban đầu dùng điều kiện quá yếu nhưng vẫn PASS; đã sửa thành kiểm tra đúng 3 lần handoff và chạy lại **70/70**. Không thay đổi mã generator, checker, oracle hay model input sau sửa bài test; không có FAIL nghiên cứu bị che giấu. PASS là mức *QA phía tác giả*; Codex chưa phản biện R3.

## 2. Hệ truyện R3 và bốn ô phản thực

Ba họ, mỗi họ 32 nhóm: `T1 MULTI_HOP_HOLDER` (≥3 handoff liên tiếp, nhiều item), `T2 GOAL_DELEGATION_CANCEL` (SET/DELEGATE/CHANGE/CANCEL), `T3 ALIAS_CROSS_ENTITY` (alias được khai báo và sử dụng trong chuỗi handoff). Mỗi nhóm có **8–10 sự kiện**, đủ bốn ô:

| Ô | Trạng thái | Câu hỏi | Kiểm định |
|---|---|---|---|
| `A_T` | Graph A | Target | Đáp án ban đầu |
| `A_D` | Graph A | Distractor | Bất biến qua can thiệp |
| `B_T` | Graph B | Target | **Đổi đáp án** sau đúng một sự kiện được thay |
| `B_D` | Graph B | Distractor | **Không đổi đáp án** |

**96/96** nhóm đạt target flip và distractor invariance, **384/384** câu được bộ parser độc lập về mã giải đúng từ văn bản hiển thị, không dùng `answer`/`source_events` cho tính đáp án. Source-events vẫn nằm trong oracle public để QA, **không** nằm trong model-input-only. Mỗi family có 16 nhóm DEV + 16 nhóm CHALLENGE; tất cả bốn ô của một nhóm ở cùng split.

**Tách theo cấu trúc (scoped):** ba dấu hiệu motif do checker định nghĩa cho DEV và ba motif CHALLENGE có **0** giao nhau; exact-story cross split **0**. Đây là kiểm tra signature được thiết kế trước, **không phải** bằng chứng mọi cấu trúc đồ thị độc lập theo mọi phép đẳng cấu hoặc độ khó DEV/CHALLENGE giống nhau. Cần đa dạng motif và split độc lập hơn trước khi khẳng định generalization khoa học.

## 3. Validator R3 kế nhiệm, giữ FAIL R2A như lịch sử

Trước khi xử lý oracle/projection, validator R3 buộc `type(model)==dict`, `set(model)=={'schema','records'}`; mỗi hàng **đúng** `{'story','question'}`, kiểm byte-length, UTF-8, khóa JSON trùng, kích thước, số hàng, thứ tự và đối chiếu projection với oracle nguồn đã ghim. Oracle chỉ được khai báo đúng là public/non-final (`labels_public=true`, `sealed_final=false`, declaration literal chuẩn). Các tiền điều kiện cần đúng theo chuỗi sự kiện visible-text.

**Kiểm thử CPU:** `70/70 PASS`; gồm **42/42 ca âm tính PASS** (nghĩa là dữ liệu sai bị từ chối), đặc biệt các lỗi R2A mà Codex xác nhận: root `answer_vector/oracle/split`, record `answer/source_events/split/id`, declaration `sealed` giả, JSON key trùng, counts sai, illegal handoff/cancel, alias chưa định nghĩa hoặc bị định nghĩa lại, group/split/motif leak, sai four-cell hay đáp án.

**Không sửa lại kết quả R2A:** `R2A_INPUT_SCHEMA=FAIL_SCOPED` vẫn là FAIL lịch sử tại code cũ. `R3_VALIDATOR=PASS_SCOPED_ON_42_CHECKED_NEGATIVES`, không suy rằng đã chống mọi kiểu attack hay một checker được chứng nhận độc lập ngoài nhóm.

## 4. Các đối chứng lối tắt và giới hạn kết luận

| Đối chứng | Kết quả trên 384 bản ghi | Diễn giải |
|---|---:|---|
| Truy xuất gán trực tiếp theo đúng khóa (không đi handoff/delegation) | **64/384** | Heuristic trực tiếp R2A không giải hết R3 |
| Đáp án **xuất hiện trong dữ liệu sự kiện cuối** | **172/384** | Chỉ là kiểm tra khả năng dùng thông tin dòng cuối, **không** phải accuracy của bộ dự đoán đã huấn luyện |
| Bộ giải ký hiệu đầy đủ về chuỗi sự kiện / alias | **384/384** | Oracle upper bound đúng kỳ vọng |
| Frozen TTM P02, O0 hay O1 neural | **NOT_EXECUTED** | Không có metric học hoặc kiến trúc |

Tính đúng của parser từ luật công khai chứng minh bài toán xác định đáp án, không chứng minh phải thêm state slot/head vào Transformer. Để suy luận hướng O1, phải đánh giá neural với dữ liệu đánh giá mới được niêm phong và nguồn supervision/compute/capacity ledger, không dùng public R3 oracle làm blind FINAL.

## 5. Quyết định tổng hợp sau QA

**`R3_PUBLIC_TOY=PASS_SCOPED_SOURCE_AND_DIAGNOSTIC`**: có thể dùng làm bộ QA, phân tích cấu trúc và phát triển baseline sau này.

**`O0=HOLD_PRESERVE` · `O1=DEFER`**: chưa mở huấn luyện/inference neural. Không có bằng chứng O1 cần thiết, cũng không có bằng chứng bác bỏ O1. Đề xuất **một** vòng Codex AI phản biện mã R3 và sơ đồ motif, cùng thiết kế O0 pilot tối thiểu trước khi cấp phép cho bất cứ lượt T4 nào. Nếu R3 chưa đủ đa dạng/anti-shortcut, sửa nguồn R3 theo amendment riêng thay vì dùng kết quả đã công khai làm TEST.

Hồ sơ R2A, Codex review, ma trận 6-arm R3 trước đó, PR #13, main và toàn bộ lineage giữ nguyên. Không thực hiện TRAIN, GPU, TEST/Q1Q2 hoặc dùng thêm nhãn oracle cho TTM.

**Bước thực hiện tiếp theo:** `TTM_R3_CODEX_SCOPED_ADVERSARIAL_QA_AND_O0_BASELINE_NEURAL_PILOT_DESIGN_SINGLE_OWNER_DECISION`. Đây là một quyết định hợp nhất, không yêu cầu cấp phép từng test nhỏ.
