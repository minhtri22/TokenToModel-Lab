# TTM P0-A Q1 — Amended Distinct Independent Source/Design Review

**Ngày:** 2026-11-15  
**Operation:** `TTM_P0A_MEASUREMENT_GOLD_INTEGRATED_REMEDIATION_EXACT_CANDIDATE_DISTINCT_REREVIEW_SINGLE_GATE`  
**Phán quyết duy nhất:** `PASS_Q1_DESIGN_SCOPE`  
**Tuyên bố giới hạn:** `BENCHMARK_GOLD=NOT_VALIDATED · Q1_NOT_REGISTERED · SCIENCE_NOT_AUTHORIZED · PR22_NO_MERGE`.

## 1. Identity, independence và nguồn

- Repo: `minhtri22/TokenToModel-Lab`.
- PR #22: https://github.com/minhtri22/TokenToModel-Lab/pull/22 · `OPEN · DRAFT · UNMERGED` tại thời điểm truy xuất.
- Chính xác ứng viên sửa đổi: `a8fd21f35d56a87f869df673b318d437ed0c8b31`; HEAD cũ `f3225f4f2cbc48ef15cdbc92cf5c050c78f4fa1a`; đối chiếu main `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`.
- GitHub compare xác nhận `ahead_by=1`, `behind_by=0`, `total_commits=1`; commit mới có parent trực tiếp là ứng viên cũ. GitHub diff đúng 5 tệp: sửa 2, thêm 3.
- Vai trò reviewer: ChatGPT, kiểm toán phân tích trong lượt làm việc chỉ đọc, không tham gia sửa commit này. **Độc lập nhân sự/tổ chức: NOT_EXTERNALLY_ATTESTED**; đây là AI source/design review, không phải người phân xử khoa học hay xác thực quyền nguồn.
- Handoff: [TTM_P0A_Q1_EXACT_AMENDED_DISTINCT_REREVIEW_HANDOFF_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/docs/governance/ttm-post-q001/TTM_P0A_Q1_EXACT_AMENDED_DISTINCT_REREVIEW_HANDOFF_20261115.md).
- Nguồn reviewer HOLD lần đầu chỉ có tường thuật của owner; Markdown/JSON reviewer gốc ở máy Windows **không được truy xuất bằng byte**. `OLD_REVIEWER_RAW_SHA256=NOT_VERIFIED`.
- Phương pháp byte: GitHub connector `fetch_file(encoding=base64)` tại exact commit; giải mã byte, tự tính SHA-1 với tiền tố Git `blob <length>\0` và SHA-256; mọi SHA-1 khớp SHA được GitHub trả về. **Không phải hashing từ bản Markdown được sao chép thủ công**.

## 2. Ba kết luận đối kháng

### F-CONSTRUCT — `PASS_DESIGN_REMEDIATED`

Đối chiếu [docs/governance/ttm-post-q001/TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_QUESTION_CANDIDATE_20261115.md#L11-L17](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/docs/governance/ttm-post-q001/TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_QUESTION_CANDIDATE_20261115.md#L11-L17), [docs/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md#L9-L21](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/docs/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md#L9-L21), [JSON lines 173–224](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json#L173-L224): một họ atomic `LOCATED_AT(entity_id,location_id,reference_time_id)` với thời gian và định danh tường minh; định nghĩa `ITEM_ADMISSION_STATUS` tách `FACT_LABEL`. TRUE cần witness sau truncation; FALSE cần phủ định hoặc tiên đề loại trừ hiển thị; UNKNOWN_VALID chỉ khi miền đã khai báo đầy đủ và không entail/refute. Nhãn FALSE/TRUE do tác giả gán trước nhưng witness mất không được biến thành UNKNOWN. INVALID và conflict là reject, ngoài mẫu số.

**Ghi chú đối kháng X14:** hai địa điểm khác nhau **không tự động là mâu thuẫn** nếu ontology không có tính duy nhất; cần tiêu chí nhận diện incompatibility chứng minh được. Diễn giải N07 chỉ áp dụng cho *actually conflicting* authoritative facts; không coi đây là lỗ hổng còn chặn thiết kế vì source quy định rõ không được ngầm suy tiên đề loại trừ. Quy tắc quyết định conflict cần đóng thành assertion-level checker trước khi authoring.

### F-PARITY — `PASS_DESIGN_REMEDIATED`

Đối chiếu [remediation lines 23–33](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/docs/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md#L23-L33) và [JSON lines 227–268](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json#L227-L268): phân biệt source packet đã lưu với prefix model thực thấy sau wrapper, tokenizer và truncation. Có yêu cầu giữ witness quyết định trong cả model/rater effective views, cùng information budget; chứng cứ W bị cắt từ model nhưng rater còn W dẫn tới **hard veto trước fixture freeze**. Danh sách receipt bao gồm hash prefix đã render, hash effective prefix, tokenizer, token range/witness spans, rater payload và quyền. Tất cả vẫn chỉ là field **planned**, chưa có receipt thực.

**Ghi chú đối kháng X13/X15:** witness W khớp không đủ nếu rater còn thấy thêm fact phản bác. Trước freeze phải xác minh **toàn bộ thông tin làm thay đổi nhãn**, không chỉ duy nhất một span dương; phải định nghĩa thứ tự ghi `gate HOLD` và `item REJECT_PARITY/REJECT_MISSING_WITNESS` cho cùng lỗi truncation. Đây là điều kiện triển khai, chưa phải bằng chứng QA hiện tại thất bại.

### F-DECISION — `PASS_DESIGN_REMEDIATED`

Đối chiếu [remediation lines 35–49](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/docs/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md#L35-L49), [JSON lines 270–285](https://github.com/minhtri22/TokenToModel-Lab/blob/a8fd21f35d56a87f869df673b318d437ed0c8b31/artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json#L270-L285): năm nhánh có bằng chứng phân biệt. KEEP yêu cầu future actual prospective validations; SIMPLIFY cần hẹp phạm vi trước outcomes; PIVOT cần chứng cứ bất khả thi phạm vi cũ và oracle thay hợp pháp cùng information budget, plus Question Gate mới; STOP cần impossibility thật sự không có lawful alternative; HOLD là mặc định khi thiếu proof. Tranh chấp/hard veto không được giải quyết bằng điểm tổng hợp. `PASS_Q1_DESIGN_SCOPE` không đồng nghĩa `KEEP` hay benchmark validated.

## 3. Tái dựng 12 negative contracts (logic thủ công độc lập, không chạy dữ liệu/model)

| ID | Tình huống thách thức | Kết quả bắt buộc | Kiểm toán |
|---|---|---|---|
| N01 | Source lưu W; cửa sổ 256 token xóa W chỉ ở model; rater còn W | `HOLD_PARITY_LOST_AFTER_TRUNCATION` | PASS_LOGICAL |
| N02 | Model có W nhưng rater không có W | `HOLD_PARITY` | PASS_LOGICAL |
| N03 | Nhãn TRUE/FALSE có sẵn nhưng witness bắt buộc mất | `REJECT_MISSING_WITNESS_NOT_UNKNOWN` | PASS_LOGICAL |
| N04 | Triple hợp lệ, miền hiển thị hữu hạn/đầy đủ, không suy được TRUE/FALSE | `UNKNOWN_VALID` | PASS_LOGICAL |
| N05 | Thiếu reference_time_id hoặc referent không phân giải | `REJECT_INVALID_SCHEMA_OR_REFERENT` | PASS_LOGICAL |
| N06 | Địa điểm khác được nhắc tới nhưng không có tiên đề duy nhất/loại trừ | `UNKNOWN_VALID_IF_COMPLETE_NOT_FALSE` | PASS_LOGICAL |
| N07 | Hai chứng cứ có thẩm quyền thực sự bất tương thích tại cùng thời điểm | `REJECT_CONFLICTING_AUTHORITY` | PASS_WITH_AXIOM_CAUTION |
| N08 | Cặp phản chứng thay đổi đồng thời location và time; có yêu cầu causal contrast | `HOLD_AD06_IF_CAUSAL_CONTRAST` | PASS_LOGICAL |
| N09 | Chưa xác minh quyền nguồn trước truy cập nội dung | `HOLD_RIGHTS` | PASS_LOGICAL |
| N10 | Hai người chấm độc lập trên cùng task bất đồng chưa phân xử | `HOLD_RATER_COMPETENCE` | PASS_LOGICAL |
| N11 | Yêu cầu chạy model khi Q chưa đăng ký/owner chưa cho phép | `NO_MODEL_RUN` | PASS_LOGICAL |
| N12 | Gold chỉ có trong E_core kín; rater không thấy witness | `REJECT_MISSING_WITNESS` | PASS_LOGICAL |

**Tổng kết:** 12/12 tình huống có kỳ vọng phù hợp ở mức contract source/design; đây **không** phải 12 kiểm thử runtime hoặc kiểm định vàng.

### Phản ví dụ bổ sung ngoài QA tác giả

| ID | Câu hỏi đối kháng | Kết quả/phạm vi |
|---|---|---|
| X13 | Rater có thêm một fact phản bác nhưng model không thấy | `HOLD_EVIDENCE_PARITY`; cần mapping material facts trước freeze |
| X14 | Hai location cùng time, không có exclusivity axiom | Không tự suy FALSE/conflict; chỉ UNKNOWN nếu domain đầy đủ, nếu không HOLD |
| X15 | W mất bởi truncation sau nhãn TRUE do tác giả gán | Gate HOLD, item REJECT; **không** UNKNOWN; yêu cầu ưu tiên code khi implement |
| X16 | Q1 design coherent nhưng chưa có rights/gold/checkpoint | Được PASS_DESIGN có phạm vi; production/science và gold vẫn HOLD |

## 4. Regression và provenance

- So sánh 5 file trước/ sau ứng viên: 2 modified (`Q` và `J`), 3 added (remediation, QA, handoff). Không sửa 5 file PR còn lại; Git blob SHA-1 cũ/ mới khớp.
- `lineage.md` ở hai candidate đều là Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`; `ACTIVE_RESEARCH_GATE.md` đều là `ad01aecdde99e17653b4e111325bed0b05cc8be2`.
- Owner selection vẫn P0-A trước P0-B, P1 data/objective đồng hạng, P4 chỉ tham khảo; đối chiếu priority lock và matrix bất biến.
- Author receipt `85/85`, 85 ID độc nhất, all `pass=true`; không là distinct review hay science proof.
- Không thay main, không merge, không đăng ký Q1, không mở branch nghiên cứu, không đọc gold hoặc TEST/FINAL. Ngoài diff GitHub không chứng minh các quá trình ngoài repository; báo cáo này không đưa ra tuyên bố tuyệt đối về máy cục bộ.

## 5. Raw-byte verified manifest ở exact amended HEAD

| Repository-relative path | Git blob SHA-1, recomputed/matched | SHA-256 từ raw bytes | Bytes |
|---|---|---|---:|
| `docs/governance/ttm-post-q001/TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_QUESTION_CANDIDATE_20261115.md` | `22f7382dc7a76f3cbcbe695d700cb9111c246f60` | `8afeaddb0cb17361c4a9ab4fa90e80321551db02aaf986dbc40f8ffc9169c28d` | 14032 |
| `artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json` | `24c35ec70236fa64ff14488bf32189c81782faa6` | `9245aabb4e53a588adfb5d973ab816c25e71e0e82f67254b23d01f897f69f0a4` | 15431 |
| `docs/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_SOURCE_CONTRACT_20261115.md` | `6ab78594e1aee776cae81bba191e84d8cc39966c` | `20f4440d9ee1ab0dcb0bbffaa08b13e6a98c165c28ddde6fa9fcd0e87ced03df` | 9638 |
| `artifacts/governance/ttm-post-q001/TTM_P0A_Q1_INTEGRATED_HOLD_REMEDIATION_AUTHOR_QA_RECEIPT_20261115.json` | `b6fdbc46b2241df6203ebb62f9a2e073db090655` | `683cc8abddc743c5e856a3490eaf483d2becfe1de5100351bf26c59c07ac900d` | 10899 |
| `docs/governance/ttm-post-q001/TTM_P0A_Q1_EXACT_AMENDED_DISTINCT_REREVIEW_HANDOFF_20261115.md` | `ebb18886a9de9ae8779d08e4770662a35248e25b` | `618b2d1d07fed7b5d0a75d983db9e383903a8c6b7653497f53a3e52b492bea08` | 7777 |
| `artifacts/governance/ttm-post-q001/TTM_P0A_SELECTION_AND_DESIGN_AUTHOR_QA_RECEIPT_20261115.json` | `d5170037048a33f3353a4c61472d01f88aadfc2d` | `2daafdcecd4deb975a499fa6c6462cae6761265f9250282708e405a3ad91c8c7` | 6357 |
| `artifacts/governance/ttm-post-q001/TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_20261115.json` | `2118dbb5a2b2cf86e59285d88ff1a2b76f309f80` | `f83f43612f85d67e650215fe9c98f4e342d2abadd6aa7ee6f31ae82d88340490` | 15942 |
| `artifacts/governance/ttm-post-q001/TTM_POST_Q001_SOURCE_ONLY_AUTHOR_QA_RECEIPT_20261115.json` | `a8810baaa29a1a81b97ca8c65d6116f2c5390db0` | `47f1c2e96ebfafb4b17759a1c3d10c7576e4811cf8175fddbade3196804c1ed6` | 4267 |
| `docs/governance/ttm-post-q001/TTM_POST_Q001_P0A_OWNER_SELECTION_AND_PRIORITY_DEPENDENCY_LOCK_20261115.md` | `7ccc41b30743a44c5427368212db1e88197d3006` | `3a1eb3996f50bd6109cc94b36d0b94cadaa7ecada58eff4a29ea16a7b6b59065` | 4987 |
| `docs/governance/ttm-post-q001/TTM_POST_Q001_RESEARCH_DIRECTION_PRIORITY_MATRIX_20261115.md` | `c8da20ffa47eaebafa0c4f6cc1e710f5cdffe167` | `5f2dc6f680a7b43431c5125c3a4dc9d81b71c50fda1d7c7315ba185162c618c1` | 14290 |

## 6. Gate statuses và các giới hạn

- `OVERALL=PASS_Q1_DESIGN_SCOPE`; `F-CONSTRUCT=PASS_DESIGN_REMEDIATED`; `F-PARITY=PASS_DESIGN_REMEDIATED`; `F-DECISION=PASS_DESIGN_REMEDIATED`.
- `BENCHMARK_GOLD=NOT_VALIDATED` · `ITEM_SOURCE_RIGHTS=NOT_VERIFIED` · `VISIBLE_SOURCE_FEASIBILITY=NOT_VERIFIED` · `ITEM_LEVEL_WITNESS=NOT_VERIFIED` · `EFFECTIVE_PREFIX_RECEIPTS=NOT_CAPTURED`.
- `INDEPENDENT_SAME_TASK_RATER=NOT_CALIBRATED` · `THRESHOLD/SAMPLE_SIZE=NOT_FROZEN` · `CHECKPOINT_CUSTODY=NOT_VERIFIED` · `TEST_FINAL=SEALED` · `SCORER=NOT_AUTHORIZED`.
- `Q1_REGISTERED=false` · `GOLD_AUTHORING=false` · `SCIENCE_AUTHORIZED=false` · `PR22_MERGED=false`.
- Reviewer là AI source/design reviewer; không thay thế human independent source rights/adjudication signoff khi workflow yêu cầu.

### Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_Q1_OWNER_DESIGN_PASS_REASSESSMENT_AND_REGISTRATION_DECISION_SINGLE_GATE`

Owner xem xét **một** quyết định tiếp theo (`GO_REGISTER_Q1_SCOPED` hoặc `HOLD_Q1_REGISTRATION`), sau khi kiểm tra provenance/independence và các lưu ý X13–X15 được đưa vào điều kiện của Question Gate. **Không tự đăng ký Q1, không merge PR #22, không gold, không chạy khoa học hoặc mở micro-permit.**
