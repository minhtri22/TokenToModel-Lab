# TTM — Quy chế nghiên cứu ưu tiên câu hỏi, lựa chọn kiến trúc, lineage khoa học và main cập nhật

**Policy ID:** `TTM-GOV-QF-20261115-V1`  
**Ngày hiệu lực:** 2026-11-15, tính từ **commit đầu tiên đưa tài liệu này vào `main`**; không hồi tố sửa các nguồn, phán quyết hay entry cũ.  
**Phạm vi:** `minhtri22/TokenToModel-Lab`; nghiên cứu, tối ưu kiến trúc, thay đổi cơ chế, thí nghiệm, kiểm toán và quyết định hợp nhất (merge).  
**Quyết định owner:** đồng ý khóa nguyên tắc trên `main` trước khi thực hiện tiếp gate kiến trúc SM4M-F0/F2, yêu cầu `lineage.md` chỉ bổ sung kết quả khoa học PASS/FAIL và implement HEAD, giới hạn cây nhánh và giữ `main` là bản chuẩn mới nhất.

## 1. Trật tự hiệu lực, không làm sai lịch sử

1. Chính sách này là **quy tắc quản trị có hiệu lực về sau** và ưu tiên khi mâu thuẫn với mô tả quy trình cũ ở `PROJECT_CHARTER.md`, `docs/GOVERNANCE.md`, `docs/PHASE_PLAN.md` và dòng mô tả mở đầu cũ của `lineage.md`. Không thay đổi khóa kết quả khoa học hoặc protocol/prereg của study đã chạy.
2. `lineage.md` là **append-only về byte và cấu trúc**: không sửa, xóa, sắp xếp, đổi ID hoặc chèn vào giữa entry lịch sử. L0010…L0029 (kể cả entry kỹ thuật/design cũ) tồn tại như bản ghi lịch sử, không tự nhiên trở thành science PASS; không tái phân loại hồi tố. Nếu cần đính chính khoa học trong tương lai, **append entry khoa học mới** trỏ entry cũ; đính chính metadata/QA không khoa học thì dùng biên bản governance riêng, không append vào lineage.
3. Từ ngày hiệu lực, **chỉ** kết quả nghiên cứu thực nghiệm đạt điều kiện phân xử khoa học, với `SCIENTIFIC_PASS_SCOPED` hoặc `SCIENTIFIC_FAIL_SCOPED`, mới được append vào `lineage.md`; trường hợp nghiên cứu thực sự FAIL là bằng chứng cần lưu, không phải thứ để sửa. `HOLD`, `NOT_EXECUTED`, `UNVERIFIED`, `DESIGN_ONLY`, `QA_PASS`, kết quả hạ tầng, run demo và metadata inventory **không được** thêm thành entry mới trong lineage. Nếu hiệu lực của kết quả khoa học chưa chứng minh, ghi trạng thái ở `docs/governance/ACTIVE_RESEARCH_GATE.md` và receipt riêng.
4. Không ghi PASS/FAIL khoa học chỉ vì `source QA`, `synthetic QA`, reviewer thiết kế hoặc chứng thực Git SHA khớp; không dùng data/checkpoint khác bằng cách đổi tên nhánh. Giữ đúng scope, one-shot và quyền dữ liệu.
5. Chính sách này không tự động thay đổi quyền thực thi, cấp phát GPU, mở TEST, hồi sinh nghiên cứu FAIL, hay cho phép merge bất kỳ nhánh khoa học nào.

## 2. Câu hỏi khoa học (Question Gate) — điều kiện vào mọi vòng

**Một nghiên cứu, một câu hỏi quyết định, một kết luận đóng.** Trước bất kỳ implement, thí nghiệm, đổi architecture, data, loss, scorer, rater, benchmark hay tạo nhánh nghiên cứu, tác giả phải ghi **một Question Gate** trên `main`, theo mẫu `templates/TTM_RESEARCH_QUESTION_GATE.md`, gồm tối thiểu:

- `question_id`, tên nghiên cứu, **câu hỏi có thể trả lời/bác bỏ cụ thể** và tại sao việc trả lời làm thay đổi quyết định; loại `SCIENCE`, `ENGINEERING`, `MEASUREMENT`, `GOVERNANCE`.
- Nguồn hiện tại: exact `main` ref, study/checkpoint/implementation HEAD, hash của bằng chứng, phân loại OBSERVED / INFERRED / UNKNOWN; các thí nghiệm/TEST đã tiêu thụ không tự tái sử dụng.
- Các giả thuyết/cơ chế cạnh tranh, đối chứng, cơ sở của kiến trúc đang dùng, điều gì không biết, các giả định cần xác nhận, khả năng bác bỏ từng giả thuyết, định nghĩa **đáp án tối thiểu** và tác động nếu câu hỏi chưa giải được.
- Lựa chọn framework **theo nhu cầu**, không tick đủ thủ tục: `5W1H` (mục đích/phạm vi), `5 Whys` + bằng chứng nguyên nhân (root-cause hypotheses, không coi chuỗi vì-sao là chứng minh), `SWOT` (trade-offs), `FMEA` (failure modes), `Pugh/MCDA` (so sánh), `falsification` (khả năng bác bỏ), hoặc tổ hợp tối thiểu. Ghi **vì sao framework được chọn**, điểm yếu và giả định của nó.
- Tối thiểu: `KEEP`, `SIMPLIFY`, `PIVOT`, `STOP` và `HOLD_EVIDENCE_INSUFFICIENT` phải được cân nhắc nếu có tính cạnh tranh. Đánh giá necessity, scientific/construct validity, discriminating power, implement fitness, chi phí/thời gian và sự đơn giản. `MCDA` nếu dùng cần trọng số khóa trước đánh giá, phân tích độ nhạy và điều kiện loại trừ cứng (hard veto) cho quyền dữ liệu, gold/construct không hợp lệ, không định danh nguyên nhân.
- Phép chứng cứ **nhỏ nhất đủ phân biệt**, tiêu chí GO/HOLD/STOP, acceptance threshold/stop rule, budget và quyền truy cập; phân biệt nguồn giấy tờ với actual science và nêu điều kiện làm thay đổi lựa chọn.
- Một người chịu trách nhiệm, một reviewer độc lập được phép, một chu kỳ kiểm tra, một hạn/sự kiện dừng hợp lý nếu có; không chia thành chuỗi micro-permit.

Nếu thiếu câu hỏi hoặc không thể nói rõ **kết quả nào sẽ thay đổi quyết định**, gate `HOLD_QUESTION_UNJUSTIFIED`; không mở branch hoặc triển khai giải pháp.

## 3. State machine và quy tắc một gate

`Q0_CLOSED_OR_NO_ACTIVE` → `Q1_QUESTION_REGISTERED` → `Q2_FRAMEWORK_AND_ALTERNATIVES_EVALUATED` → `Q3_ANSWER_REVIEWED` → `Q4_OWNER_DECIDED_AND_CLOSED` → (nếu `GO` đúng phạm vi) `I1_ONE_IMPLEMENTATION_BRANCH` → `I2_EXECUTION_AND_EVIDENCE` → `I3_INDEPENDENT_ADJUDICATION` → `I4_MERGE_OR_EVIDENCE_ONLY_CLOSURE` → `Q0`.

- Tại một thời điểm, trong TTM chỉ **một Question Gate nghiên cứu chủ động**. Không được mở gate nghiên cứu thứ hai hoặc nhánh nghiên cứu tiếp theo trong khi Q1–Q3 chưa có câu trả lời và quyết định owner ở Q4. Việc đọc/kiểm toán bảo toàn nguồn lịch sử là ngoại lệ **read-only**, không là phase mới.
- Q1–Q3 chỉ dùng `main`, tài liệu/pins hiện hữu và một hồ sơ chính sách; **chưa** tạo nhánh nghiên cứu hoặc vá kiến trúc. Nếu đánh giá được trên nguồn hiện hữu thì không tạo dữ liệu, không gọi mô hình.
- Một `HOLD` chưa được owner đóng là **chặn tiếp**. `HOLD_EVIDENCE_INSUFFICIENT` có thể được đóng hợp lệ thành `CLOSED_HOLD` nếu ghi nguồn thiếu, lý do không thể trả lời, cách xử lý và owner xác nhận; **không** tự trở thành `GO`.
- Sau Q4, chỉ khi owner xác nhận `GO_SCOPED_IMPLEMENT`, cho phép **một** nhánh implement/research lấy từ **main hiện tại**. Mỗi nhánh chỉ mang một câu hỏi và một can thiệp đã khóa; mọi sửa lỗi cần thiết nằm trong cùng nhánh/gate, không sinh nhánh con cho từng finding hoặc reviewer.
- Khi nhánh hiện tại chưa đóng I4, không mở nhánh kế nhiệm, không đổi giả thuyết, không lén đổi threshold hoặc hạt giống, không mở F3/F4. Nếu kết quả chỉ HOLD hoặc FAIL phải đóng/ghi evidence trước khi owner quyết định hướng khác.
- Mỗi gate có **một** reviewer độc lập đủ khác biệt với tác giả và phạm vi hợp lệ; tự QA là bắt buộc nhưng **không thể tự xác nhận độc lập**. Một lượt remediation tích hợp có điều kiện dừng thay cho sửa nhỏ liên tiếp vô hạn.

## 4. Quyết định kiến trúc trước implementation

Trước khi thêm/thay thành phần `attention`, `FFN`, `embedding`, `tokenizer`, `position`, `data/objective`, `scorer/rater`, memory/retrieval, GPU kernel hoặc benchmark:
- Trả lời `WHY` chức năng bắt buộc, baseline thực tế, failure mode nào được bằng chứng chỉ ra (không quy nguyên nhân bằng cảm giác).
- Kiểm tra có **đối chứng tối thiểu** phân biệt lỗi thành phần đó với data, objective, decoding, source/rights hoặc phép đo hay không.
- So sánh giải pháp hiện tại với **phương án tối giản** và **phương án thay construct**. Phương án không có gold/construct hợp lệ, rò dữ liệu, không thể tạo đối chứng hoặc vi phạm owner scope phải bị loại (hard veto), bất kể điểm MCDA.
- Lựa chọn là `KEEP`/`SIMPLIFY`/`PIVOT`/`STOP`/`HOLD` với confidence và bằng chứng, **không** là owner science permit. Chỉ sau closure Q4 mới được phép xem xét code/experiment và phê duyệt riêng cho phép chạy.

## 5. Kỷ luật lineage khoa học (append-only)

Từ sau ngày hiệu lực, một entry mới phải có đủ:

`Lineage ID` duy nhất tăng đơn điệu trên main (xác minh ref trước append); `StudyID`; `QuestionID`; kết quả `SCIENTIFIC_PASS_SCOPED` **hoặc** `SCIENTIFIC_FAIL_SCOPED`; câu hỏi, giả thuyết, primary metric/threshold, n/đơn vị mẫu, giới hạn, baseline, **implement HEAD (Git full 40 hex; kể cả khi FAIL/không merge; nếu thí nghiệm dùng baseline trên `main` thì ghi đúng full baseline HEAD thay vì `NOT_APPLICABLE`)**, science run/checkpoint/data SHA nếu có, independent science adjudication source/ref, receipt path và hash, owner closure, `merge_decision` và `main_record_commit` tham chiếu được (không tự tham chiếu commit chưa tồn tại). Nếu thành phần không áp dụng, ghi `NOT_APPLICABLE` kèm lý do, **không bịa**.

Đường dẫn evidence và implement HEAD được **pin trước khi append**. Append **không thay thế** archive của thất bại, không chỉnh entry cũ. Không copy toàn bộ lineage theo nhánh vào main, không trùng ID `L0029` đang tồn tại trên main. Không dùng branch HEAD động thay cho exact pinned SHA.

Một `PASS` khoa học có phạm vi không tự cho phép merge code hoặc phát hành. Một `FAIL` vẫn vào lineage nếu phép đo/đối chứng/rights/science adjudication **hợp lệ**; nếu lỗi môi trường khiến không có kết quả khoa học đáng tin, phải `HOLD` ở evidence registry, **không tạo FAIL khoa học giả**.

## 6. Cổng kết thúc mỗi phần: MERGE hay EVIDENCE_ONLY

Sau Q4/I3 (tùy trường hợp), bắt buộc ghi `merge_decision` trong closure trên `main`:
- `MERGE_APPROVED`: chỉ khi implement phù hợp design đã khóa, source/rights, chức năng/negative/regression QA, independent review, không làm sai baseline, owner chấp thuận. Merge qua PR, cập nhật **main** và ghi readback exact commit; không tự đưa FAIL/experimental code vào main.
- `EVIDENCE_ONLY_NO_MERGE`: result `SCIENTIFIC_FAIL_SCOPED`, HOLD, design rejected, hoặc branch chưa đạt merge QA. Giữ nguyên implement HEAD và evidence; chỉ đưa **metadata/closure/science lineage hợp lệ** về main, không merge implementation, checkpoint, gold, TEST hay source FAIL.
- `NO_MERGE_NEEDED`: tài liệu/chứng cứ đã được lưu và không có delta có điều kiện merge; ghi rõ.
- `HOLD_MERGE_REVIEW`: chưa có quyền hoặc chứng cứ, tiếp tục lưu riêng; **không** kéo code lên main để tạo hình ảnh “up-to-date”.

Trước đóng mỗi nhánh, có owner/reviewer status, evidence manifest (HEAD, blob hashes, file paths), link parent question, lineage ID nếu có, quyết định merge và lý do. Không kết thúc ở “QA PASS” mà thiếu quyết định xử lý nhánh.

## 7. Main là hiện trạng quản trị chuẩn mới nhất — không phải nơi gom mọi code branch

- `main` là **source of truth cho quyết định đã đóng, policy hiện hành, active-question status, science lineage đã đủ điều kiện và implementation đã MERGE_APPROVED**. Không có nghĩa mọi exploratory/HOLD/FAIL branches phải được merge. `docs/governance/ACTIVE_RESEARCH_GATE.md` là bảng trạng thái **có thể cập nhật**; `lineage.md` không dùng làm bảng task/QA.
- Sau **mỗi gate closure**, phải cập nhật active register + merge/evidence-only decision trên main (cùng PR/đợt governance được owner phê duyệt) **trước khi tạo gate nghiên cứu kế tiếp**. Không duy trì kết quả mới nhất chỉ trong hội thoại hoặc nhánh riêng.
- Quy mô target: **tối đa một nhánh nghiên cứu/implementation đang hoạt động trong TTM**, không có chùm branch cho review, remediation, evidence. Những nhánh lịch sử (snapshot hiện quan sát 68 refs) không được gọi ACTIVE chỉ vì còn trên GitHub. Cần phân loại `ACTIVE / CLOSED_EVIDENCE_ONLY / MERGED / ARCHIVED / UNVERIFIED` bằng kiểm toán exact HEAD, **không tự xóa**, không tự thay nhánh khi còn việc đang mở.
- Việc dọn nhánh phải có manifest hash/owner authorization theo đúng đường dẫn/custody; nhánh HOLD/FAIL có thể được giữ read-only/archived, xóa ref sau khi đã chứng minh preservation và được owner cho phép. Không xóa worktree hoặc evidence tự động.
- PR đang Draft không trở thành PASS/mergeable vì đổi tên. Prior statuses trên main chỉ là snapshot, cập nhật bằng gate kế tiếp, không tự tuyên bố mọi nhánh đã kiểm toán khoa học.

## 8. Quy tắc khóa chính sách và thay đổi tương lai

- Policy thay đổi bằng câu hỏi `GOVERNANCE` đã ghi rõ, diff giới hạn, author adversarial QA, independent source QA khi phù hợp, owner quyết định; ưu tiên PR. Không sửa hồi tố lịch sử, không nới scientific gate vì tiến độ.
- **Một ngoại lệ khởi tạo duy nhất tại chính commit ban hành policy này:** chủ sở hữu yêu cầu đưa policy trước nghiên cứu mới trực tiếp vào `main`; cho phép commit **chỉ tài liệu quản trị/mẫu/receipt**, sau QA đối kháng và đối chiếu diff, với chính quyết định owner trong cuộc trò chuyện là nguồn phê duyệt. Ngoại lệ không trao quyền cho thay đổi source/code, khoa học, merge nhánh cũ hay bỏ qua independent QA của nghiên cứu. Ghi rõ rằng author QA không phải independent QA. Từ commit tiếp theo, tuân quy tắc PR/independent/owner của chính sách.
- Bất kỳ mâu thuẫn hiện hành nào với mô tả “mỗi sửa lỗi một nhánh”, “lineage ghi mọi QA”, “main là nơi nhập mọi branch” được giải thích theo thứ tự: **policy này → amendment trong `PROJECT_CHARTER.md` và `docs/GOVERNANCE.md` → văn bản cũ theo phạm vi lịch sử**.

**Terminal governance scope:** `GOVERNANCE_POLICY_LOCK_ONLY · NO_SCIENCE_EXECUTION · NO_NEW_RESEARCH_BRANCH · NO_LINEAGE_REWRITE · NO_IMPL_MERGE`.
