# TTM Track A — BR-I2-01/02 V2 · Hợp đồng thiết kế tích hợp F01–F06

**Ngày:** 2026-11-17 · **Chế độ:** `DESIGN_ONLY · NO_IMPLEMENTATION · NO_SCIENCE · NO_OWNER_RELEASE`  
**Operation:** `TTM_TRACK_A_BR_I2_01_02_F01_F06_INTEGRATED_DESIGN_AMENDMENT_AND_EXACT_SHA_DISTINCT_REREVIEW_SINGLE_GATE`  
**Điều phối:** [PM Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6928014536) · dưới **một gói** `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE`.  
**Design base exact commit:** `20385e71cb5d2b8f3d7725229ab7a823e1044990` · **v1 review:** `HOLD_DESIGN_AMENDMENT` (sáu phát hiện F01–F06).  
**Nguyên tắc phiên bản:** v1 `TTM_TRACK_A_BR_I2_01_02_INTEGRATED_DESIGN_CONTRACT_20261117.md` và ma trận v1 **giữ nguyên** làm lịch sử. V2 là đặc tả thay thế cho mục đích review tương lai; không ghi đè quá khứ và không tạo permit.

## 0. Phạm vi bất biến và tiêu chí bác bỏ (falsifier)

- `I1_PASS_SCOPED_MEASUREMENT` đã được PM đóng **duy nhất** cho M0 v3 tại source `ec197b5f00d3a037420390edd11ee55047e1d37f`, distinct evidence `e3e1c802815f4db1534e92d9848d6015eb9203cc`; F01/F02 **35/35**, custody **38/38**, fixture **80/80** và **5/5**. Chỉ là chứng nhận đo lường, **không phải** owner I2 GO.
- Private frozen fixture records SHA-256 `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`; manifest `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`; TRAIN BPE `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; freeze receipt `b82a7ebc29930563db581f7724d0847a725d893860b776b7cc682ec875af4c3a`.
- `owner_internal_admission.py` **vẫn** trỏ đến `I1_PASS_SCOPED_INTERNAL_RESEARCH` historical scope và runtime pins khác; `release_auth_v2.py` có ba role owner/reviewer/rights nhưng **không có trusted keys**, fail-closed. Không thay các file này; preflight lịch sử **exit 2 / HOLD_OWNER_INTERNAL_I1_NOT_PASS**. Owner release và R0–R8 đều HOLD.
- Không thay `tools/`, workflow, checkpoint, fixture, historical verdict, `main`, `lineage.md`, PR #28, Track B/C; không model forward, optimizer step, nonce claim, PR merge, không tạo micro-permit.
- Các mệnh đề dưới đây là **hợp đồng để kiểm tra trong tương lai**, không phải tính chất đã chứng minh. Bất kỳ mục nào không đạt negative QA độc lập / owner-native => `HOLD`.

## 1. Bảng sửa sáu finding của distinct reviewer

| Finding | Sửa chuẩn tắc trong V2 | Điều kiện bác bỏ |
|---|---|---|
| F01 | Receipt payload tự chứa không có staging/published SHA; sha256(payload_bytes) chỉ ở external completion envelope, không có vòng hash tự tham chiếu. | Bất kỳ ca SELF_HASH tương ứng bị chấp nhận sai => DESIGN/RELEASE HOLD |
| F02 | Chỉ chấp nhận handle-based SetFileInformationByHandle/FileRenameInfo, RootDirectory đã xác minh, relative leaf, ReplaceIfExists=FALSE; native anti-swap QA còn HOLD. | Bất kỳ ca HANDLE_RENAME tương ứng bị chấp nhận sai => DESIGN/RELEASE HOLD |
| F03 | Tên final cố định từ canonical signed logical scope; randomized staging suffix; same-transaction/same-hash retry mới idempotent, competition HOLD. | Bất kỳ ca DETERMINISTIC_KEY tương ứng bị chấp nhận sai => DESIGN/RELEASE HOLD |
| F04 | Tách receipt publish FSM khỏi immutable science nonce ledger; fail-closed khi crash/ambiguous; at-most-once dispatch, không tự cấp lượt thứ hai. | Bất kỳ ca STATE_MACHINE tương ứng bị chấp nhận sai => DESIGN/RELEASE HOLD |
| F05 | Quy trình phát hành certificate versioned có issuer signatures và principal separation; trusted roots từ reviewed source riêng; explicit I2_RUN -> run mapping, không sửa legacy. | Bất kỳ ca AUTHORITY tương ứng bị chấp nhận sai => DESIGN/RELEASE HOLD |
| F06 | Positive controls có execution/tier/evidence/oracle; thêm duplicate JSON keys, postpublish mutation, signer custody substitution và phase mapping/replay controls. | Bất kỳ ca ORACLES tương ứng bị chấp nhận sai => DESIGN/RELEASE HOLD |

## 2. F01 — Receipt byte domains: không có self-hash

### 2.1 Tập dữ liệu và thứ tự vật lý

Phân biệt **ba đối tượng độc lập, không lồng SHA của chính mình**:

1. **LogicalScopeV2** (`scope_descriptor`): object chứa `question_id`, `operation_id`, `measurement_source_commit`, `phase_intent`, `release_policy_revision`, `signed_owner_decision_ref`, `single_science_scope_id`, `fixture_records_sha256`, `fixture_manifest_sha256`, `checkpoint_sha256` (nếu áp dụng). Hai writer cho cùng operation/source/signed intent **phải** dùng object byte-identical; khác intent không được lén dùng key khác để cấp thêm science. Scope ID science có chính sách một-lần toàn chương trình độc lập với permit ID ngẫu nhiên.
2. **ReceiptPayloadV2**: object canonical chứa `schema`, `scope_key`, `transaction_id`, `source/fixture/checkpoint/tokenizer provenance`, `science_executed=false`, `I2=NOT_EXECUTED`, `public-safe file identity digests`, `created_utc` (khóa tại lần tạo transaction). **Không** chứa `payload_sha256`, `staging_sha256`, `published_sha256`, `ack_sha256` hoặc hash của chính nó.
3. **CompletionEnvelopeV2**: object riêng, tạo **sau** khi payload đã publish và xác minh, gồm `scope_key`, `transaction_id`, `payload_sha256`, `staging_file_id`, `final_file_id`, `outcome`, `verification_proof_sha256`, `source_snapshot_pins`, `I2=NOT_EXECUTED`. Envelope **không** chứa hash toàn bộ envelope. Nếu cần `envelope_sha256`, tính **ngoài** envelope và neo ở Git/PM evidence riêng; không cho phép self-reference.

### 2.2 Canonical bytes và hash domains

- Định nghĩa `C(o)`: serialize strict JSON, root/object fields **ASCII keys theo thứ tự lexicographic byte**, JSON compact separators `,` `:`, string values **ASCII only**, boolean JSON lowercase, `null` nếu schema cho phép, **integer only (không float/exponent)**, các SHA là lowercase hex dài 64; UTF-8 không BOM, **đúng một LF cuối** (`0x0A`). Reject duplicate-key JSON, unknown fields, non-canonical spacing, escaped variant, invalid Unicode, lone CR/mixed EOL; không cho reserialize semantic-equal rồi chấp nhận bytes khác.
- `scope_key = SHA256(ASCII("TTM_A_BR_I2_SCOPE_V2\\0") || C(LogicalScopeV2))`. Chuỗi `\\0` ở đây chỉ ký hiệu **một byte NUL 0x00** trong domain prefix; trong implementation sử dụng byte literal `00`, không gõ dấu backslash và số 0. `scope_key` không phụ thuộc transaction random và không phụ thuộc tên stage.
- `payload_bytes = C(ReceiptPayloadV2)`; `payload_sha256 = SHA256(payload_bytes)`. `payload_sha256` **chỉ có trong CompletionEnvelopeV2** và các external attestation. `stage_sha256` và `published_sha256` là các **phép đo độc lập trên cùng payload bytes**, phải khớp `payload_sha256`, không phải field nằm trong payload.
- `envelope_bytes = C(CompletionEnvelopeV2)` được publish như **file thứ hai với cơ chế no-replace**, sau payload; envelope SHA nếu cần được neo bên ngoài. Dữ liệu riêng tư, token/context, host path trọn vẹn không được đưa lên GitHub; evidence public chỉ chứa hash/status.

**Ordering tuyệt đối:** freeze logical scope + transaction → canonical payload → create stage → write+FlushFileBuffers+hash stage → reread/check fixture handles → handle rename no-replace payload → open final by verified handle/rehash identity → canonical completion envelope → stage+flush+rename no-replace envelope → external SHA/Git evidence. Không lấy digest envelope làm input xây payload, không sửa payload sau publish.

## 3. F02 — Parent-handle-bound atomic publication contract (Windows)

**Primitive được chọn để thiết kế:** `SetFileInformationByHandle(hStage, FileRenameInfo, &FILE_RENAME_INFO, ...)` với `RootDirectory = hVerifiedParentDir`, `FileName = <one relative leaf name, no separators/colon>`, `ReplaceIfExists = FALSE`. `MoveFileExW` nhận tên đường dẫn **không phải** cách chứng minh handle-bound ancestry và bị loại khỏi ứng viên V2. Microsoft Learn mô tả `RootDirectory` có thể là handle thư mục khi tên tương đối, và `ReplaceIfExists=FALSE` trả lỗi nếu đích tồn tại ([API](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle); [structure](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)). Tài liệu API **không** tự chứng minh tính atomic/durable/an toàn đối với mọi driver hay rename-ancestor race.

**Điều kiện native bắt buộc trước runtime admission:**

1. Trên Windows 11, chỉ local NTFS được phép ở phiên bản thử nghiệm; không UNC/SMB, exFAT, mount lạ, khác volume, ADS, tên path tuyệt đối, case alias hoặc alternate stream. Staging **trong cùng verified parent directory** với final. Verify exact volume serial+FileId qua handle của root, parent và stage; không tin `Path.resolve` / `Test-Path`.
2. Mở từng ancestor từ trusted project root và **giữ handle còn hiệu lực qua rename**; kiểm tra reparse tag, symlink/junction, đường dẫn thực, ACL and writer trust, parent FileId/volume; deny untrusted mutable ancestors. `FILE_FLAG_OPEN_REPARSE_POINT` ở final component chưa đủ cho toàn chain; chứng minh cách mở component-by-component hoặc HOLD. Kiểm tra source fixture theo stable opened handles, SHA raw và 80/5 digest; không tái sinh fixture.
3. Tạo stage `CREATE_NEW` với `DELETE` access cho rename và permissions/share modes được thiết kế/rà soát; `FILE_SHARE_*` phải đủ cho thao tác rename nhưng không mở một đường ghi ngoài trust. Không có `OPEN_ALWAYS`, `CREATE_ALWAYS`, replace/truncate.
4. `FILE_RENAME_INFO` được cấp đúng kích thước buffer, relative basename **được kiểm UTF-16 và không NUL/colon/slash**, `RootDirectory` giữ đúng validated parent handle; `ReplaceIfExists=FALSE` và **không** dùng flag POSIX replace. Failure (name collision, sharing violation, cross-volume, unsupported FS) => HOLD/reconcile, **không** fallback sang `MoveFileExW` hay copy+delete.
5. Native adversary phải chạy parent swap/junction injection **trước, giữa và sau** handle checks, trên owner-host và same volume. Mọi trường hợp phải fail-closed hoặc publication verified trong **chính directory object đã pin**, không có file nào thoát trust root. File ID, parent handle ID, volume và final SHA được re-read sau publish. Nếu driver không chứng minh được behavior => HOLD.
6. `FlushFileBuffers(hStage)` yêu cầu hoàn tất **trước rename**; flush không tự chứng minh bền vững directory entry sau power loss. Thử mất điện/durable rename là **gate riêng và chưa được chứng minh**, không gắn `DURABLE_POWERLOSS_PASS` khi chỉ crash process.

## 4. F03 — Final receipt deterministic, concurrency và idempotence

- `final_leaf = "TTM_A_BR_I2_" + scope_key + ".receipt.json"`; **bất biến**, cùng tên cho mọi transaction của một logical scope. `stage_leaf = "." + final_leaf + "." + transaction_id + ".tmp"` với transaction_id tạo ngẫu nhiên khi **khởi tạo transaction**, ghi vào **immutable transaction journal**. Random stage suffix **không** được thêm vào final.
- `transaction_id` phải được giữ nguyên qua retry: id do journal chính xác ghi lại và verify; không tạo transaction mới nếu state cũ chưa terminal. Final payload chứa transaction_id nên cùng scope nhưng writer khác tạo bytes khác, chỉ một writer được phép publish.
- **Publish WIN:** target absent, validated parent + stage, rename returns success, final file identity và SHA khớp. **COMPETITOR:** target exists, khác transaction ID **hoặc** hash mismatch => `HOLD_CONFLICT` dù cùng logical scope, không overwrite. **IDEMPOTENT_RETRY:** target exists, recovered journal proves **same transaction_id + exact payload SHA + original signer/scope** and verified final bytes/parent => return acknowledgement read-only; **không rename/write mới**, không claim science nonce. **AMBIGUOUS:** có final nhưng thiếu journal/tampered journal/không xác minh được source custody => HOLD, không đoán.
- Two writers share same stable `scope_key`; expected **exactly one** successful no-replace publish, other HOLD. Pseudocode `if not exists: WriteAllText(final)` **không hợp lệ**. Đích đã tồn tại không được unlink/delete/replace để “giải kẹt”.

## 5. F04 — Crash/replay state machine & science one-shot ledger

Hai máy trạng thái **tách biệt**; receipt publish **không tạo science permit**. Mọi state transition có snapshot SHA và journal/version monotonic append-only; ambiguous => HOLD.

### 5.1 Receipt transaction FSM

| State | Bằng chứng tối thiểu | Bước hợp lệ | Crash / retry |
|---|---|---|---|
| `ABSENT` | no trusted transaction journal, no final | create-new journal, `PREPARED` | nếu final tồn tại mà journal không có => HOLD |
| `PREPARED` | immutable journal + transaction_id + scope_key | create-new stage, `STAGED` | crash before valid stage => `NO_FINAL_AND_NO_PARTIAL_PUBLISH`; quarantine temp |
| `STAGED` | stage handle, payload hash not yet flushed | write+flush+verify, `SEALED` | no final; incomplete stage never publish |
| `SEALED` | stage hash, validated fixture handles and parent | handle-bound no-replace rename, `PUBLISHED` | crash before rename => no final, stage quarantine; if state uncertain inspect final by handle |
| `PUBLISHED` | final exact hash and file ID, same tx | build & publish separate envelope, `ACKED` | crash after rename => re-read final and journal; ack same tx **without rewrite** |
| `ACKED` | immutable external completion envelope | terminal receipt-only | retry = verify/read-only acknowledgement, no new nonce |
| `HOLD_CONFLICT/HOLD_UNKNOWN` | any inconsistent/partial artifact or uncertain result | STOP | no auto delete/retry/GO |

`ATOMIC-03` oracle **chính xác:** `NO_FINAL_AND_NO_PARTIAL_PUBLISH` (staging incomplete may exist in quarantine, but no partially visible **final** file). `ATOMIC-04`: stage sealed but no final; recover idempotently only with verified same journal, otherwise HOLD. `ATOMIC-05`: final already published but acknowledgement lost => same-transaction read-only ACK. Power-loss metadata durability **NOT_VERIFIED**.

### 5.2 Science ledger FSM (chỉ mô tả, tuyệt đối không kích hoạt)

`NO_AUTHORITY` → [**new separately signed, authenticated integrated PM owner release + all R0–R8**] `AUTHORIZED` → [append-only atomic **CREATE_NEW** claim keyed by immutable **single_science_scope_id**, shared across *all permit versions and runner revisions*, then fsync and verify] `CLAIMED_CONSUMED` → [one approved owner dispatch] `DISPATCH_ATTEMPTED` → `TERMINAL` or `HOLD_UNCERTAIN`.

- Receipt FSM **không** đi tới `AUTHORIZED`. `CLAIMED_CONSUMED` là chuyển trạng thái bất khả nghịch: crash sau claim nhưng trước/đang dispatch **không tự cấp lại khoa học**. Không đánh đồng transaction_id của staging với science nonce.
- Claim thiếu/corrupt, ledger scope đổi, hai permit mới trỏ cùng science intent, lost acknowledgement, crash không rõ có chạy model hay không => `HOLD_NONCE_AMBIGUOUS` và **không retry science**. Không có lời hứa exactly-once science; mục tiêu khả thi là **at-most-one authorized dispatch**, còn unknown thì HOLD.
- Contract phải chứng minh: một claim ghi bền trên trusted local FS trước khi forward, concurrency/process crash adversarial; rollback clock/policy/ledger đều HOLD. Nếu không chứng minh được trên máy owner thì prospective I2 **vẫn bị chặn**.

## 6. F05 — Authority, certificate issuance, identities và phase versioning

### 6.1 Issuance ceremony: chứng nhận đo lường không phải chữ ký GO

**V1 Measurement Certificate candidate** ban đầu ở trạng thái `DRAFT_UNATTESTED` được **derive only** bằng verifier độc lập đọc Git exact SHA (source `ec197b5f00d3a037420390edd11ee55047e1d37f`, distinct report/receipt SHA ở `e3e1c802815f4db1534e92d9848d6015eb9203cc`, PM closure blob, original frozen pins) và tạo canonical certificate payload. `I1_PASS_SCOPED_MEASUREMENT` gắn trên candidate **không** tạo release permission. Issuer proposal phải có một **provenance envelope độc lập**: `certificate_payload_sha256`, `evidence_commit` + exact Git blob map và sha256, `review_protocol_version`, `PM_accepted_measurement=true`, `created_utc`, `signatures`. Bản candidate chỉ thành `ISSUED_MEASUREMENT_CERT` khi **owner PM và distinct independent measurement reviewer/authorized custodial delegate** dùng key đã được root trust policy xác minh thực sự ký canonical payload và provenance envelope; ký nháy qua issue comment/Account GitHub không đủ. Nếu reviewer gốc không có key/custody hợp lệ, **không tự động chuyển** lời comment cũ thành chữ ký; state HOLD pending lawful issuance.
 
**Public trust-root policy:** policy version + reviewed immutable Git object SHA và public key fingerprints phải được bootstrap out-of-band bởi PM/owner và distinct adjudicator; approved binding `role -> verified principal identity -> verified custodian/key_id` (not just key strings), issuer validity UTC, revocation digest/list, monotonically increasing policy epoch and anti-rollback anchor. Check principal **thực sự khác nhau và kiểm soát private-key độc lập** (signer role alias, shared device/account, delegated custodian, compromised key => HOLD even if raw keys differ). Validated authentication source phải độc lập với untrusted permit; key không bao giờ lấy từ payload đang xin permit. Không tự đăng ký keys hay generate signatures trong gói này.

**ReleaseAuthorizationV1** là đối tượng **mới, riêng** và chỉ có hiệu lực sau một quyết định owner release tương lai: exact certificate/provenance SHA + integrated PM R0–R8 gate evidence + rights/resources/custody signatures, source runtime SHA map, owner host/root, checkpoint/fixture/manifest, expiry/revocation, one-shot scope+nonce. Theo legacy policy, chữ ký owner, distinct reviewer, rights custodian phải đến từ **ba principal độc lập** và key trust anchors được kiểm toán; cả ba chưa sẵn sàng = HOLD. Release authorization **không** được sinh từ owner status JSON, raw GitHub comment hay I1 certificate đơn lẻ.

### 6.2 Phase adapter explicit, fail closed, historical guard untouched

| External versioned intent | Proposed new adapter wire value | Legacy `authenticate_release(phase=...)` | Admission |
|---|---|---|---|
| `I2_RUN` | `run` | `run` | chỉ tương lai, khi signed permit supports all exact fields và integrated PM owner GO |
| `M0_V3_MEASUREMENT` | none | không gọi | `NO_RELEASE_AUTHORITY` |
| `FIXTURE_FREEZE` | none | `fixture-freeze` **không áp dụng lại cho frozen fixture** | `HOLD_REFREEZE_FORBIDDEN` |
| any unknown/downgrade | none | không gọi | `HOLD_UNKNOWN_PHASE` |

Existing `validate_verdict` còn yêu cầu `I1_PASS_SCOPED_INTERNAL_RESEARCH` của historical scope; không sửa literal, pointer, old verdict hay old SHA runtime map. **Một adapter versioned mới** (chỉ thiết kế hôm nay) phải binding signed new certificate+release decision và khai báo sự không tương thích; nếu legacy validator không thể chấp nhận new schema mà vẫn fail-closed => `HOLD`, không bypass bằng setting `I1=true` hay sửa old source.

## 7. F06 — Negative/positive QA oracles & gates

- Ma trận V2: [`BR_I2_01_02_V2_F01_F06_NEGATIVE_QA_MATRIX_20261117.json`](../../../../artifacts/ttm-abc/track-a/BR_I2_01_02_V2_F01_F06_NEGATIVE_QA_MATRIX_20261117.json); every case has `id, blocker, tier, execution, setup, stimulus/negative, expected, oracle, evidence, required`, **including POS-01/02/03**. Mọi `execution=NOT_EXECUTED_DESIGN_ONLY`, evidence fields chỉ là **planned schema**, không phải actual.
- Bổ sung đối kháng: duplicate-key JSON cả certificate/permit và receipt, private key signer custody substitution (public key khác nhưng một custodian), post-publish byte mutation (before ACK và after ACK), wrong phase adapter, global ledger two-permit collision, parent handle mutation and source final checksum.
- **Design review gate**: reviewer phiên độc lập kiểm tra exact **new commit**, toàn bộ F01–F06, từng expected/oracle, byte/alias/semantics; kết luận `DESIGN_ACCEPT_SCOPED` hoặc `HOLD_DESIGN_AMENDMENT`. Tác giả có thể tự kiểm đếm JSON/source nhưng **không ký adjudication của chính mình**.
- **Prospective implementation gate (NOT AUTHORIZED NOW)**: reviewer nguồn độc lập + owner-native Windows 11 PS 5.1/Python3.12 and native handle/NTFS fault injection, signer/key principal custody, ledger crash proofs, all mandatory negatives and positives no skips; R0–R8 one integrated owner decision. Design accept **không tự kích hoạt** implementation hay I2.
- **Global PM:** trước tất cả báo cáo về `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` và Issue #32, không phát hành Track A micro-permits.

## 8. Kết luận candidate (không tự phân xử)

`F01_F06_AMENDED_BY_AUTHOR_DESIGN_ONLY · I1_MEASUREMENT_CLOSED_PASS_SCOPED · DESIGN_STATIC_QA_EXPECTED_ONLY · DISTINCT_REREVIEW_NOT_EXECUTED · OWNER_RELEASE_HOLD · I2_NOT_EXECUTED · NO_IMPLEMENTATION · NO_MERGE`.

**Bước thực hiện tiếp theo — duy nhất:** review độc lập V2 theo exact HEAD của PR #33, sau đó PM nhận verdict **trong một gói A/B/C R0–R8**. Không cần thêm micro-permit.
