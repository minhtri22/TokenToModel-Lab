# TTM R2A — Phân xử phản biện Codex AI nội bộ (owner-scoped)

**Ngày:** 2026-11-11 · **Quyết định:** `DESIGN_R3_BEFORE_O1` · **Phạm vi:** chứng cứ nguồn + thiết kế; không thay đổi lịch sử khoa học, không huấn luyện.  
**Nhánh lưu quyết định:** `research/ttm-r3-structural-state-tracing-design-20261111`, tạo từ **chính commit phản biện Codex** `dbf2c5389358e3989c1cb4a691bb981c32ecaf45`, không sửa nhánh Codex hoặc R2A cũ.  
**Reviewer:** Codex AI phiên riêng, người chấm **nội bộ**, không phải xác nhận độc lập từ con người/đơn vị bên ngoài.

## 1. Bằng chứng đã đọc lại (trực tiếp qua GitHub)

- [Báo cáo Codex R2A](https://github.com/minhtri22/TokenToModel-Lab/blob/dbf2c5389358e3989c1cb4a691bb981c32ecaf45/docs/research/TTM_R2A_CODEX_SCOPED_ADVERSARIAL_REVIEW_20261110.md), Git blob `41dc4153070efe2113f13d3b089208891aeec5fb`.
- [Biên nhận kiểm định](https://github.com/minhtri22/TokenToModel-Lab/blob/dbf2c5389358e3989c1cb4a691bb981c32ecaf45/artifacts/qa/ttm-r2-semantic-toy/codex-review-20261111/TTM_R2A_CODEX_ADVERSARIAL_QA_RECEIPT_20261111.json), Git blob `ebac0525be5dcff65bdd3e125229476f83d46f12`.
- [Mã adversarial QA](https://github.com/minhtri22/TokenToModel-Lab/blob/dbf2c5389358e3989c1cb4a691bb981c32ecaf45/tools/research/semantic_state_r2/r2a_codex_adversarial_qa_20261111.py), Git blob `7b622049bfd8fdb0f72866adcaf8283ef819fb65`.
- R2A gốc tại `c85b2ab504953bd667f09909f3495c4772fd1b2e`, checker Git blob `1a6edc434e30cfd66820c0d021c0b085124e1847`, bộ sinh Git blob `78d0ce42468ae4c29e44b6488feafba8b2a31215`.
- Chính report/receipt ghi `PASS_10/10` blobs, `PASS_36/36` author CPU và 11 mutation với kết quả **7 từ chối đúng + 4 nhận sai đúng kỳ vọng của phép tấn công**. **Không gọi 11/11 là 11 lần từ chối.**

## 2. Phân xử từng phát hiện — bảo toàn FAIL và phân biệt claim

| ID | Mức | Bằng chứng và phạm vi | Phán quyết | Hành động bắt buộc |
|---|---|---|---|---|
| R2A-01 | HIGH | `check(dataset, model)` chỉ kiểm `model.get('schema')`, `records` và fields từng record, **không kiểm đúng tập khóa root**. Chèn `answer_vector` / `oracle` / `split` vào model root vẫn ACCEPT | **CONFIRMED_VALIDATOR_FAIL** | `type(model) is dict and set(model)=={'schema','records'}`; negative test ba loại injection, fail-closed trước mọi inference |
| R2A-02 | MEDIUM | `dataset['declaration']` không khóa literal; declaration bịa `Sealed FINAL TEST` vẫn ACCEPT | **CONFIRMED_VALIDATOR_FAIL** | Ghim literal public-toy, `labels_public=true`, `sealed_final=false`; từ chối sự thay đổi; original public toy không trở thành FINAL kín |
| R2A-03 | MEDIUM | Thuật toán chỉ đọc visible story+question, chọn last assignment của queried key đạt **384/384** | **CONFIRMED_DISCRIMINATION_LIMIT** | R3 phải gồm chuyển trạng thái gián tiếp/đa bước và negative shortcut; **không** kỳ vọng rule engine tổng quát sẽ thất bại |
| R2A-04 | MEDIUM | A/B đi liền; 128 query-swap dùng lại story của A | **CONFIRMED_SPLIT_LEAK_RISK** | Toàn bộ nhóm phản thực phải ở cùng split; đồ thị motif graph-disjoint, dedup story và graph across splits |
| R2A-05 | MEDIUM | 2×2 thiếu B + query-swap | **CONFIRMED_FACTORIAL_COVERAGE_GAP** | Bắt buộc 4 ô: (A/B order) × (key1/key2 query), kiểm tương tác |
| R2A-06 | LOW | 36 author tests không bao phủ mọi mutation root, dù đã PASS | **CONFIRMED_QA_SCOPE_GAP** | Một bộ test mutation hợp nhất áp dụng **checker đã harden**, giữ log author/Codex riêng |
| R2A-07 | HIGH | B có nhãn state dạng text nhưng khác param/compute; E có capacity nhưng không nhãn | **CONFIRMED_CAUSAL_IDENTIFICATION_GAP** | Thêm F capacity+state-text, khóa hai sổ ngân sách; giới hạn claim nếu không match được objective/supervision/compute |

**Bảo toàn kết quả:** `R2A_TOY_FORMAL=PASS_SCOPED` không bị phủ nhận; `R2A_INPUT_SCHEMA=FAIL_SCOPED` được ghi là **FAIL thật của validator**; `NEURAL_SEMANTIC_GAIN=NOT_TESTED`; `FAIR_SUPERVISION=HOLD_DESIGN_ONLY`.

**Quan trọng:** R2A model-input JSON canonical có đúng `story/question`, SHA `72f57d704a2e4f99f06a797b8b647d93736a7093852e0c9df0f28dc59549032d`. Lỗ hổng validator chỉ cho phép **tệp bị chèn metadata** vượt gate, không phải bằng chứng file canonical đã chứa nhãn.

## 3. Phán quyết khoa học và ý nghĩa thực

- Giả thuyết `H-ORDER`: đúng với đối chứng bag-of-words khi xét cùng multiset từ và câu hỏi, một hệ quả hình thức; **không** là bằng chứng Transformer thiếu thứ tự.
- `H-KEY_BINDING`: dữ liệu yêu cầu chọn đúng khóa được hỏi, nhưng chỉ cần parser last-relevant có thể đạt 100%; không chứng minh cần thêm latent memory.
- `H-STATE_UPDATE`: R2A có state oracle đúng trong grammar giới hạn, không chứng minh tổng quát hóa sang handoff/ủy quyền/huỷ bỏ/coreference.
- `H-ARCHITECTURE_O1`: không có bất kỳ huấn luyện/inference neural R2A; **không được kết luận O1 tốt hơn hoặc kém O0**.
- *Nguyên tắc suy luận:* một bộ quy tắc ký hiệu hoàn hảo trên toy là **oracle upper bound**, không phải lỗi của bài thử; câu hỏi khoa học là mô hình học được quy tắc không, có tổng quát hóa sang motif chưa thấy, và O1 có giúp trên **ngân sách công bằng** hay không.

## 4. Quyết định duy nhất

**Quyết định:** `DESIGN_R3_BEFORE_O1`; giữ nhánh 2×2 O0 nguyên trạng HOLD. Hoàn thành thiết kế R3 tập trung ở **truy vết trạng thái nhiều bước và tham chiếu gián tiếp**, sửa checker/gate trước khi dùng dữ liệu làm nguồn cho model, thêm F vào ma trận O0/O1 và đặt giới hạn kết luận.

**Không** chuẩn thuận TRAIN, Colab, GPU, phát hành checkpoint mới, R3 FINAL mới, hay mở TEST/Q1Q2. Không tự đưa Codex reviewer vào lịch thực nghiệm hoặc làm thêm nhiều vòng phê duyệt vi mô.

**Bước tiếp:** `TTM_R3_STRICT_INPUT_VALIDATOR_AND_STRUCTURAL_GRAPH_TOY_IMPLEMENTATION_SINGLE_CPU_QA` — hiện thực validator kế nhiệm R3 và test âm tính, sinh 4-of-4 phản thực với event graph, independent oracle và split theo motif, chạy một batch CPU. Sau QA đó, trình một quyết định R3/O0/O1 duy nhất; không mở T4 nếu chưa có science prereg rõ.
