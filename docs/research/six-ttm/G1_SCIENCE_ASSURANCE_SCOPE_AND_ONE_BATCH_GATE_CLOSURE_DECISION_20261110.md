# TTM × SIX G1 — Quyết định phạm vi bảo đảm khoa học và đóng cổng trong một đợt

**Ngày:** 2026-11-10 (Asia/Bangkok)  
**Mã công việc:** `TTM_SIX_G1_SCIENCE_ASSURANCE_SCOPE_FREEZE_AND_SINGLE_INTEGRATED_GATE_CLOSURE`  
**Loại:** `SCOPE_RECONCILIATION / ONE_BATCH_PLAN / NO_EXPERIMENT_AMENDMENT / NOT_AN_OWNER_SCIENCE_PERMIT`  
**Owner directive:** tránh lặp các micro-permit hạ tầng; xác định bảo đảm thật sự cần cho lượt khoa học; nếu đổi phạm vi thực nghiệm phải sửa hợp đồng trước; **không tự bỏ bảo vệ TEST bắt buộc**.  
**Trạng thái:** `G1_SCIENCE_LOCK=HOLD`; `OWNER_SCIENCE_PERMIT=NOT_ISSUED`.

## 1. Kết luận phạm vi (không thay đổi bài toán khoa học)

G1 theo hợp đồng ban đầu là **một thử nghiệm scoped cross-model representation-transfer feasibility**, không phải phát hành một dịch vụ khoa học production liên tục:

- RQ: Qwen3-0.6B `@c1899de289a04d12100db370d81485cdf75e47ca` → Qwen3-1.7B `@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e` trên cùng chuỗi tiền tố, tokenization riêng, `hidden_states[28]`; tám cặp continuation probes.
- G1 input lấy **chỉ** từ tập TTM pilot TRAIN, chia riêng G1 `128 TRAIN / 64 DEV / 64 TEST` theo manifest đã seal; không truy cập TTM pilot VAL/TEST; G1 TEST chỉ mở một lần sau khi selection/fitting từ TRAIN/DEV đã freeze và được chứng thực.
- Phân tích: ridge `[1,10,100]`, 1.000 pair-shuffle, 1.000 CKA permutations, 2.000 paired bootstrap; báo cáo B-direct, target-oracle, train-mean, shuffle và CKA, cùng tiêu chí đã khóa. `TEST=64` có giới hạn power, chấp nhận `INCONCLUSIVE`.
- Mục tiêu G1 chỉ là **khả năng chuyển thông tin/feasibility có giới hạn**. Không tuyên bố SIX causal mechanism, ưu thế chưng cất của TTM hoặc sức mạnh sản phẩm; G2/G3 chưa được cấp phép.
- Môi trường mục tiêu dự kiến **Colab Free T4**, giới hạn tích lũy 3.600 s / model, 7.200 s tổng, peak VRAM 12 GiB, một science run theo hợp đồng.

**Không đổi bất kỳ tham số, split, threshold, model, code pin hoặc TEST nào bằng tài liệu này.** v1e vẫn là `METHODS_CANDIDATE`, chờ reviewer. Không tái chạy 29/45/61 QA đã có evidence, hai Win32 failure-path, hoặc Qwen technical smokes đã tiêu thụ.

## 2. Bảo đảm khoa học bắt buộc, nhưng không tự nâng thành sản phẩm production

Chia rõ **security objective** bắt buộc và **implementation mechanism** cần đúng phạm vi, không nhầm một với một sản phẩm hạ tầng 24/7.

| Nhóm gate | Mục tiêu bất khả nhượng cho **G1 gốc** | Bằng chứng đủ phạm vi cho một lượt khoa học | Không đòi hỏi thêm nếu không thuộc threat model |
|---|---|---|---|
| 1. Authority / launcher | Quyền data, owner, `run_id`, Git/model/tokenizer/manifest pins và thời hạn được xác thực; worker không tự set flags cấp phép | Một owner-bound signed authorization, launcher pin chính xác, negative tamper/key/replay, QA reviewer | Hệ thống IAM doanh nghiệp, đa tenant hoặc dịch vụ quản trị chung |
| 2. TEST isolation / broker | G1 TEST **không thể đọc** bởi worker TRAIN/DEV trước `FIT_FROZEN`, kể cả alias/hardlink/junction; không phân phát TEST khi chưa witness ACK | Principal/token/ACL hoặc cơ chế tương đương chứng minh **deny thực tế** trên đúng đường dữ liệu/host của science, dùng TEST synthetic để kiểm; broker duy nhất cấp khi đạt freeze | Chứng minh mọi biến thể OS ngoài môi trường science đã khóa |
| 3. Trusted writer / ledger | Pack science gắn đúng byte đã đọc và source/run/split; worker không được giả receipt; crash không biến file nửa chừng thành valid result | Writer độc lập khỏi worker, digest trên bytes được parse, durable publish+receipt+recovery, một bộ fault injection đại diện ở ranh giới commit | Dịch vụ lưu trữ đa vùng, HA, backup nhiều năm |
| 4. One-shot / witness | TEST extraction/read duy nhất, terminal sau STOP/failure, không thể reset bằng rollback controller/worker | Một witness monotonic có chứng thực **ngoài miền rollback worker/controller**, kiểm replay/cả hai miền rollback và trạng thái khi mất ACK | Dịch vụ ledger tổng quát phục vụ nhiều nghiên cứu |
| 5. Watchdog / budget | Một lỗi load/forward không phá giới hạn hoặc để trẻ mồ côi; tổng thời gian/tài nguyên bị cưỡng chế trong môi trường science | Supervisor ngoài worker có quyền kill, cumulative budgets theo run, peak VRAM và failure cleanup trên **host/Colab T4 mục tiêu**. Win32 harmless child PASS là bằng chứng hỗ trợ nhưng **không** chứng thực GPU/T4 | Endurance 24/7, SLA, benchmark production |
| 6. Methods / review | Pre-TEST freeze v1a–v1e, near-duplicate/group leakage; null exchangeability; paired-bootstrap estimand; CKA tie; cỡ mẫu và terminal inconclusive | Reviewer độc lập phê duyệt *một* amendment chính xác, code+SHA group audit/sensitivity đã lock, power prospectively reported | Chứng minh 80% power bằng mọi giá hay mở rộng TEST hậu nghiệm |

**Quy tắc không được hạ thấp:** 6 gate trong latest Codex `HOLD` vẫn là các **hard-gate obligations hiện hành** cho đường G1 gốc. Bảng trên tối thiểu hóa triển khai và bằng chứng, **không tự coi NOT_TESTED thành PASS**. Nếu reviewer coi một implementation cụ thể (Windows worker SID, external witness...) là bắt buộc bởi contract đã phê duyệt, không thay bằng cờ hay thư mục cùng quyền; mọi thay đổi cần amendment + independent review + owner decision **trước TEST**.

### Ranh giới quan trọng của Windows so với Colab

Windows `D:\WORK\RESEARCH\TokenToModel-Lab` là nơi seal/metadata và có QA Win32; **PASS Windows ACL/SID không tự bảo đảm** cho worker chạy trên Colab. Broker phải kiểm soát thời điểm stage/giải mã/cấp TEST sang Colab, không mount/copy toàn bộ G1 TEST vào cùng miền worker trước freeze. Kiểm soát ngăn truy cập TEST phải được chứng minh trên toàn đường truy cập thực sự dùng cho science (host, Drive/cache, process/token, broker). Nếu Colab Free không hỗ trợ ranh giới tương đương, `HOLD` thay vì suy diễn.

### Quyền dữ liệu hiện có không phải quyền khoa học

Owner approval `G1_OWNER_PRIVATE_DATA_SCOPE_ACCEPTANCE_FOR_SEAL_AND_QA_20261109.json` chỉ cấp đọc **T1 TRAIN trên Windows để seal/QA metadata/hash**, không cho phép staging raw TinyStories lên Colab, lưu teacher vectors/probe scores hoặc science TEST. Quyền mới (source/license use, staging, derived numeric outputs, retention/deletion, destination, permitted readers) phải được owner ký cùng final single-run admission, *sau* reviewer PASS. Không tự suy ra quyền từ license metadata.

## 3. Không yêu cầu cho G1 đầu tiên

Chưa cần đóng G2/G3, chạy A–E TTM-Small4M, phát hành inference server, tích hợp Ollama/llama.cpp, benchmark PagedAttention, distributed training, production high-availability, nhiều lượt replicates hoặc công nghiệp hóa một trust service. Những việc đó có thể mở ở phase sau với hợp đồng riêng.

Giữ bản chất *one-shot*; hạn chế triển khai một instance đúng `run_id`, một broker và writer phân quyền thực, một independent witness, một watchdog thật. Số thành phần dịch vụ không phải mục tiêu; **bằng chứng cổng** mới là mục tiêu. Không tạo thủ tục xin phép cho từng SID, từng đường log, từng fault test.

## 4. Một lô đóng cổng, một lần phân xử, một quyết định owner

**Tên đợt:** `TTM_SIX_G1_SINGLE_BATCH_PREEXECUTION_SCIENCE_ASSURANCE_CLOSURE`.

1. **Chốt hồ sơ trước khi thi công:** một trang threat model G1 + quyền dữ liệu + thiết bị thực tế + các pin hiện có + phương pháp v1e và TEST protection. Reviewer và owner lựa chọn: **A. Giữ G1 original**, hoặc **B. Thay đổi phạm vi bằng amendment được ký/duyệt trước**, không đồng nhất A với B.
2. **Triển khai đúng một reference instance, không hệ thống tổng quát:** owner launcher/signature; cách ly broker/TEST trên đường Windows→Colab; trusted writer và ledger; external rollback-domain witness; watchdog có quyền dừng + budget. Provision các principal/khóa một lần theo danh sách finite được owner duyệt; không cấp science permit tại bước này.
3. **Một bộ kiểm thử liên thông end-to-end với synthetic TEST:** phủ quyền deny từ worker và aliases, freeze→witness ACK→TEST release, writer receipt/crash recovery, rollback/replay, kill/cumulative budget và hạn chế dữ liệu/log. Chỉ kiểm phần chưa chứng minh; tái sử dụng chứng cứ v1c, Windows 45/45, v1e CPU 61/61 và Windows fault paths 2/2.
4. **Một báo cáo kiểm định độc lập cho cả 6 gate:** mỗi gate `PASS/FAIL/NOT_TESTED`, SHA source, môi trường, quyền, side effects, data rights, phương pháp; kết luận duy nhất `PASS_DISTINCT_REVIEWER/HOLD/FAIL`. Nếu blocker không thể đóng với Colab Free, dừng vòng production, không triển khai micro-permit tiếp.
5. **Một owner admission khoa học tách biệt:** chỉ sau reviewer PASS và quyền data hợp lệ, owner mới có thể ký one-shot run và quyết định mở sealed TEST đúng quy trình. PASS reviewer **không tự cấp phép**.

**Exit / stop policy:** một integrated batch → một adjudication. Nếu `HOLD`, phát hành **một** bản định lượng blocker/cost/feasibility + lựa chọn scope, không nối tiếp chuỗi QA nhỏ vô hạn. `FAIL` ghi đúng bằng chứng; không xóa lịch sử. Không cấp quyền science qua việc sửa status JSON.

## 5. Nếu phải đổi phạm vi để có kết quả sớm hơn

Không chuyển dữ liệu TEST G1 gốc sang pilot hoặc hạ khóa TEST vì tiện. Nếu six-gate assurance vượt tài nguyên Colab Free, **tạo một hợp đồng khám phá tách biệt trước khi chạy** (ví dụ `G1_EXPLORATORY_TRAIN_DEV_ONLY`) với:

- Chỉ synthetic/public material đã được owner cấp quyền, hoặc TRAIN/DEV source sau khi quyền khoa học/derived data được phê duyệt; **không đọc, vận chuyển, suy diễn từ G1 private TEST**.
- Hợp đồng mới phải ghi `experiment_id`, mục tiêu suy giảm thành feasibility diagnostics / engineering learning, dataset, permissions, model/equipment pin, metrics, controls, retention, no confirmatory claims và no shared TEST.
- Kết quả này **không** được gọi `G1 original PASS` hay mang sang G3; không sử dụng như bằng chứng để tune rồi mở TEST G1 không amendment.
- Một amendment khác nếu vẫn muốn chạy G1 original sau pilot: review leakage và tất cả selection mới trước khi TEST.

**Không có scope-change hay new pilot permit nào được phát hành bởi tài liệu này.** Mặc định vẫn chọn **A: giữ nguyên G1 original**, trừ khi owner có quyết định sửa hợp đồng cụ thể.

## 6. Bằng chứng / đối chiếu nguồn

- Original scope draft: `docs/research/six-ttm/G1_G3_CROSS_MODEL_REPRESENTATION_PREREG_DRAFT_20261109.md` @ `d5d0c5346a595557a76349f900d09be50bce289c`.
- Original quantitative prereg: `G1_SCIENCE_PREREG_V1_METHODS_AND_THRESHOLDS_20261109.md` and `G1_SCIENCE_PREREG_V1_CONTRACT_CANDIDATE_20261109.json` at the same research HEAD.
- Existing owner scope: `G1_OWNER_PRIVATE_DATA_SCOPE_ACCEPTANCE_FOR_SEAL_AND_QA_20261109.json` (metadata/hash only).
- Independent prior adjudication: `G1_WINDOWS_REAL_QA_CODEX_DISTINCT_ADJUDICATION_20261110.md` @ `efbbc1fddfd61e775d30a0481622312f8fb93c51`, verdict `HOLD`.
- New methods v1e candidate: `G1_METHODS_V1E_PRETEST_FROZEN_AMENDMENT_CANDIDATE_20261110.md` on the implementation branch, still `REVIEW_HOLD`.
- Previously completed evidence: `V1C_CRITICAL=PASS_SYNTHETIC`; `WINDOWS_45/45=PASS_AUTHOR_LOG`; `V1E_CPU_61/61=PASS_AUTHOR`; `WIN32_FAILURE_PATH_2/2=PASS_OWNER_SCOPED`. None is a science result or full Colab assurance.

**Current state:** `ASSURANCE_SCOPE_G1_ORIGINAL=UNCHANGED` · `ONE_BATCH_CLOSURE_PLAN=RECORDED` · `PRODUCTION_HARD_GATES=HOLD` · `METHODS_V1E=REVIEW_HOLD` · `OWNER_SCIENCE_PERMIT=NOT_ISSUED` · `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_SIX_G1_SINGLE_BATCH_PREEXECUTION_SCIENCE_ASSURANCE_CLOSURE` — reviewer and owner scope signoff before any TEST, implement the minimal trusted boundary + methods freeze in one batch, then one independent integrated QA/adjudication; if impossible under Colab Free, formally amend/split exploratory scope before science.
