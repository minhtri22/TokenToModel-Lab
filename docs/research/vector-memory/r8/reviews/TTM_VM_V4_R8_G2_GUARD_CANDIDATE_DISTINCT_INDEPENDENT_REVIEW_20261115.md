# TTM VM V4 R8 — Kiểm toán độc lập pre-G3 admission guard

**Operation** `TTM_VM_V4_R8_G2_GUARD_CANDIDATE_INDEPENDENT_REVIEW_AND_TRUST_BOUNDARY_ADMISSION_SINGLE_GATE`

**Ngày** 15/11/2026 (Asia/Saigon). **Reviewer** Codex trong phiên review hiện tại, tách khỏi agent triển khai candidate. Reviewer này đã soạn đề xuất retention `b1231fa` ở lượt trước. Kết quả QA candidate dưới đây do reviewer trực tiếp thực hiện. Hồ sơ không cấp independent acceptance cho chính đề xuất retention.

| Phân xử | Kết quả |
| --- | --- |
| `RETENTION_AMENDMENT_REVIEW` | `HOLD` |
| `GUARD_SOURCE_INDEPENDENT_QA` | `HOLD` |
| `PRODUCTION_TRUST_BOUNDARY_READINESS` | `NOT_ATTESTED` |
| `G2_INTEGRATED_DECISION` | `G2_HOLD · HOLD_INTEGRATED` |

## Git pins và provenance

- Candidate `9d210f1392e81a17f1c35cea12230bf7ff74fb02`, frozen scientific source `84d9d5c95e9962ccfe294852570e261b145fe403`, retention proposal `b1231faef1b2a4166016ee78a9de6617800efeff`, handoff `d47656dbd5af27e26fa18d61089956eaac6e0df8` và commit thêm ZIP `63e45126625cd99064f9d476affe39c5d347e21d`. [Candidate](https://github.com/minhtri22/TokenToModel-Lab/commit/9d210f1392e81a17f1c35cea12230bf7ff74fb02), [handoff](https://github.com/minhtri22/TokenToModel-Lab/blob/d47656dbd5af27e26fa18d61089956eaac6e0df8/docs/research/vector-memory/r8/handoffs/TTM_VM_V4_R8_G2_GUARD_CANDIDATE_DISTINCT_INDEPENDENT_REVIEW_HANDOFF_20261115.md), [amendment](https://github.com/minhtri22/TokenToModel-Lab/blob/b1231faef1b2a4166016ee78a9de6617800efeff/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md).
- Đã lấy blobs bằng GitHub Git Data API, tái tính Git blob ID từ bytes, so với object trong exact commits và tính SHA-256. ZIP 30.727 bytes có Git blob `34dc0d5abc32799df96449c8c00714bc3adbfe61` và SHA-256 `d1bf1b43f2cd9d482c989173ab1736594eb4593d5931094df285f8c95c174b77`. CRC hợp lệ, đúng ba entry ZIP_STORED, mỗi entry khớp byte với candidate và SHA-256 manifest. [ZIP](https://github.com/minhtri22/TokenToModel-Lab/blob/d47656dbd5af27e26fa18d61089956eaac6e0df8/docs/research/vector-memory/r8/reviews/artifacts/TTM_VM_V4_R8_G2_PRE_G3_GUARD_SOURCE_QA_20261115.zip), [SHA-256 manifest](https://github.com/minhtri22/TokenToModel-Lab/blob/d47656dbd5af27e26fa18d61089956eaac6e0df8/docs/research/vector-memory/r8/reviews/artifacts/TTM_VM_V4_R8_G2_PRE_G3_GUARD_SOURCE_QA_20261115.sha256.txt).
- So với `b1231fa`, candidate thêm đúng hai tệp Python và một báo cáo. Các commit sau candidate chỉ thêm ZIP, manifest và handoff. Năm blob khoa học đã khóa khớp Git blob và SHA-256 ở frozen pin, candidate và handoff. Kế thừa `G0=PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` tại `12d66bcff86a6cf435998a98a14afd254924fa5d`. Runtime và custody trước đó được viện dẫn theo phạm vi lịch sử. [G0 adjudication](https://github.com/minhtri22/TokenToModel-Lab/commit/12d66bcff86a6cf435998a98a14afd254924fa5d).

| ZIP member | Git blob | SHA-256 |
| --- | --- | --- |
| `pre_g3_admission_guard.py` | `b35da231742d5bcf01f8d4ab48069afbfad37eea` | `6bf5150b65718ad594dec4fc66f42a9dc6e29cf004828f265752af1d9e603a31` |
| `test_pre_g3_admission_guard.py` | `9534a2d32e8cf53208634efe47ded4f02b9e9743` | `64d4b6bf4929373cd1a553c5b1e22cb5fa55ed915ea10ae5c0465b91ec744318` |
| `TTM_VM_V4_R8_G2_PRE_G3_ADMISSION_GUARD_IMPLEMENTATION_AND_SOURCE_QA_20261115.md` | `d07c0972422fe6f68284b97cc46f1210c3feb40f` | `ab719a0e5a9d371a014a244c1c2c1767c7f806f2ea3d76ecd1ddca5e6e4be696` |

## Retention amendment

Quyết định owner về backup độc lập chỉ áp dụng R8-D exploratory, 32 cặp/64 ca synthetic. `RECOVERY_NOT_VERIFIED` được bảo toàn. Frozen V4 yêu cầu khóa G_pre trước khi có case text và giữ quy tắc `FOLD_LEAK_CV_INVALID` nếu G_post nối hai fold. Một thời hạn retention chống xóa cố định chưa được xác định trong những đoạn frozen design và independent adjudication đã đối chiếu. Tính toàn vẹn, thứ tự prospective và khả năng đối chiếu khi sử dụng kết quả vẫn bắt buộc. [Frozen §B03](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md#L33-L40), [independent G2 requirement](https://github.com/minhtri22/TokenToModel-Lab/blob/12d66bcff86a6cf435998a98a14afd254924fa5d/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_GPRE_V2_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md#L94-L96).

Reviewer tải lại asset sentinel và đối chiếu SHA-256 `f589347fc615f73826104a0121fd46e842ea210414df8c26f75c0c13c2ffc54f`. GitHub báo `immutable=true`, tag trỏ exact commit `3ca8d7993bc6921adc507cd4c9cf7d839e92141e`, thời điểm publish `2026-11-15T08:16:24Z`. `gh release verify-asset` kiểm được attestation bind repo/tag/commit/asset và timestamp authority `2026-11-15T08:16:25Z`. Asset ghi rõ đây là mẫu. Quyền xóa cả release vẫn tồn tại; không có retention tối thiểu đã được nghiệm thu. [Sentinel release](https://github.com/minhtri22/TokenToModel-Lab/releases/tag/ttm-vm-v4-r8-g2-commitment-sentinel-20261115), [GitHub immutable releases](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).

`HOLD`. Ở mức thiết kế, quy tắc dừng và hạ kết quả mất bằng chứng xuống hồ sơ forensic có thể bảo toàn giá trị khoa học nếu nó được áp dụng trước mọi bước phụ thuộc. Cần một reviewer khác với tác giả chấp nhận bản prospective theo scope R8-D, cùng bằng chứng xác nhận riêng rủi ro retention và đường thực thi dừng thật khi mất anchor, signed bundle hoặc custody. Nếu mất khả năng đối chiếu, khóa bước tiếp theo và phân loại kết quả phụ thuộc là không hợp lệ. Giữ evidence còn lại và cấm sửa hồi tố, đổi seed/key/fold/commitment hoặc sinh lại để thay bằng chứng. [Đề xuất prospective](https://github.com/minhtri22/TokenToModel-Lab/blob/b1231faef1b2a4166016ee78a9de6617800efeff/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md#L35-L53).

## Independent source-only QA

Windows `win32`, CPython `3.12.10`, SQLite `3.49.1`. Python source được materialize từ exact GitHub blobs, kiểm byte với Git trước khi chạy. Tất cả database thử được tạo dưới thư mục scratch riêng, callback chỉ tăng bộ đếm. Không dựng key, fold allocation, blueprint thật hoặc G_pre thật. Dùng `python -B -W error::ResourceWarning test_pre_g3_admission_guard.py` với temp riêng và không ghi bytecode.

- **22/22** method test của candidate đạt khi reviewer chạy lại độc lập. Bao gồm 8 threads cho 1 callback và 7 replay denial, 2 process Windows qua `spawn` cho 1 callback và 1 replay denial, callback lỗi vẫn consume và default deny trước callback. Kết quả 22/22 Linux của implementation là hồ sơ lịch sử riêng.
- Harness riêng `reviewer-probes.py` chỉ import guard exact, không dùng fixture code của implementation. 23 probe ghi nhận **12 control**, **9 trường hợp nhận/ghi ngoài giả định an toàn**, **2 exception sai contract với 0 callback**. Con số 23 là số quan sát được ghi nhận, không phải điểm PASS. `P13` phản ánh fixture được thiết kế cho fake verifier, với giới hạn trust boundary nêu ở F01–F04. SHA-256 harness `2d3e069749a5888d8c2adf7d43b9d1bb17dcc6c732d05f66f9d8e6ff3ba36f32`.
- P01–P12 kiểm default deny, lỗi byte/UTF-8, duplicate lock JSON, nonce, digest, schema, runtime và asset binding, receipt thiếu hoặc muộn, cùng commit trước callback và replay sau khi consume. Receipt JSON lưu từng kết quả, error code và số lần gọi callback.

## Findings

### F01 · HIGH · Fixture dispatcher nhận verifier và callback do caller cấp

Default trả lỗi trước verifier và callback. Trong fixture, hai fake verifier cùng callback tùy ý được nhận. Chuỗi `"false"` cũng kích hoạt fixture vì dùng truthiness. Tìm tham chiếu ở code và workflow của exact tree chỉ thấy định nghĩa guard và hai hàm của caller cũ ngoài test. Caller cũ tạo lock và hậu kiểm; chưa có generator R8 production đăng ký hoặc launch path bắt buộc qua guard.

**Ảnh hưởng** Giữ `PRODUCTION_TRUST_BOUNDARY_READINESS=NOT_ATTESTED`. Callback giả đã chạy trong fixture. Khả năng một tích hợp tương lai đi vòng guard là rủi ro từ call graph chưa khóa.

**Probe** `P01`, `P13`, `P14`. [pre_g3_admission_guard.py L163–189](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L163-L189), [pre_g3_admission_guard.py L242–247](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L242-L247), [r8_production_caller.py L1–26](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/integrated_closure/r8_production_caller.py#L1-L26).

### F02 · HIGH · Attestation và independent acceptance là dữ liệu do caller tự dựng

`AnchorProof` và `AcceptedReceipt` là dataclass công khai. Code so chuỗi, kiểm 64 hex và dựa vào truthiness của `immutable`, `signature_verified`, `accepted`. Commit review chỉ qua regex 40 hex. Commit toàn số 0, digest asset/bundle tự khai và cả ba cờ chuỗi `"false"` đều đi đến callback trong fixture. Candidate thiếu adapter kiểm exact remote bytes, signature/trust root, repository/release/asset identity và signer được ủy quyền chấp nhận đúng amendment lẫn G_pre.

**Ảnh hưởng** Production HOLD. Tải lại sentinel thật xác minh được đường công bố mẫu ở bên ngoài guard.

**Probe** `P13`, `P14`. [pre_g3_admission_guard.py L119–160](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L119-L160), [pre_g3_admission_guard.py L188–226](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L188-L226).

### F03 · HIGH · Exact bytes được bind nhưng HMAC V2 chưa được xác thực

SHA-256 khóa exact blueprint/lock bytes và `nonce || envelope`; đổi nonce hoặc lock mà giữ proof cũ bị chặn. Fixture chứa marker không phải blueprint, lock chỉ có schema, algorithm và hai chuỗi hex tự chọn vẫn được nhận. Guard không xác minh nội dung blueprint, component/fold, `cv_status` hoặc recompute HMAC với key thuộc custodian theo domain V2. Kiểm nonce chỉ xác nhận kiểu và độ dài, không chứng minh nguồn entropy hay custody.

**Ảnh hưởng** PASS scoped cho byte binding với proof đúng kỳ vọng. HMAC, custody và G_pre authenticity ở production vẫn HOLD.

**Probe** `P05`, `P06`, `P13`. [pre_g3_admission_guard.py L69–116](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L69-L116), [folds_raters.py L251–318](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/integrated_closure/folds_raters.py#L251-L318).

### F04 · HIGH · Source/runtime manifest được so bằng chuỗi tự khai

Sai chuỗi runtime giữa proof và envelope bị chặn. Cặp chuỗi 64 hex trùng nhau được nhận dù không có manifest file. Guard không đọc source/runtime thực thi, bind loaded artifact hay callback với các byte đã kiểm. Callback không nhận đối tượng dữ liệu đã xác minh từ guard.

**Ảnh hưởng** Production HOLD. Kết quả runtime Windows trước được kế thừa trong phạm vi smoke test cũ.

**Probe** `P08`, `P13`. [pre_g3_admission_guard.py L85–101](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L85-L101), [pre_g3_admission_guard.py L192–205](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L192-L205), [pre_g3_admission_guard.py L247–247](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L247-L247).

### F05 · HIGH · Thứ tự timestamp và trạng thái mất anchor chưa được thực thi

Hai bất đẳng thức kiểm `published ≤ signed ≤ verified ≤ now` và `signed ≤ accepted ≤ now` độc lập, dùng clock local. Receipt trước `verified_at` được nhận dù fixture không đưa bằng chứng acceptor đã tự xác minh. Khi publication, signed và acceptance trùng nhau, timestamp không chứng minh được thứ tự nghiêm ngặt mà callback vẫn chạy. Mô phỏng anchor mất trong bước nhận receipt sau lần check đầu, callback vẫn chạy. Chưa có freshness bound, trạng thái revoke hay kiểm lại trước dispatch và các bước phụ thuộc.

**Ảnh hưởng** Giữ HOLD cho pre-G3 order và enforcement mất evidence. Phải chứng minh thứ tự bằng trusted timestamps hoặc chuỗi sự kiện đã xác thực, cùng fail-closed khi trạng thái khó xác minh.

**Probe** `P15`, `P16`, `P17`. [pre_g3_admission_guard.py L188–226](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L188-L226), [pre_g3_admission_guard.py L229–247](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L229-L247), [TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md L39–42](https://github.com/minhtri22/TokenToModel-Lab/blob/b1231faef1b2a4166016ee78a9de6617800efeff/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md#L39-L42).

### F06 · HIGH · SQLite one-shot phụ thuộc ledger không đổi và schema tin cậy

`BEGIN IMMEDIATE`, uniqueness và commit trước callback chặn lặp trên cùng DB mới, ổn định. Đổi sang DB khác, khởi tạo sẵn table bỏ constraints hoặc restore bản DB chưa consume đều gọi callback thêm lần nữa. Hardlink leaf ghi vào DB alias ngoài thư mục ledger dự kiến nhưng vẫn trong scratch test. `parent.is_dir()` và leaf `is_symlink()` không xác thực canonical root, ancestor reparse/junction, ownership/ACL, cùng file identity khi mở, pinned DDL hay trạng thái chống rollback. Junction/ACL TOCTOU và crash/power loss chỉ phân tích source hoặc chưa thử.

**Ảnh hưởng** PASS scoped cho serialization trên cùng file/schema bình thường. Chưa có bằng chứng ledger chống thay đổi, rollback hoặc replay trên trust boundary production.

**Probe** `P12`, `P18`, `P19`, `P20`, `P21`. [pre_g3_admission_guard.py L171–177](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L171-L177), [pre_g3_admission_guard.py L227–247](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L227-L247).

### F07 · MEDIUM · JSON lỗi thoát qua exception ngoài AdmissionDenied

`json.loads` chấp nhận token `NaN` và lone surrogate escaped. Khâu canonicalize với `allow_nan=False` hoặc encode UTF-8 bên ngoài `try` phát `ValueError`/`UnicodeEncodeError`. Cả hai probe đều có 0 callback.

**Ảnh hưởng** Lỗi contract của đường từ chối, giữ QA source ở HOLD cùng các counterexample khác. Không quan sát thấy chạy callback qua hai input này.

**Probe** `P22`, `P23`. [pre_g3_admission_guard.py L69–84](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/pre_g3_admission_guard.py#L69-L84).

### F08 · LOW · Tên test cross-session vượt phạm vi điều đã đo

Test 19 chỉ dựng thêm guard trỏ lại cùng ledger và gửi cùng envelope có cùng session. Phép thử chứng minh replay qua instance mới trên cùng ledger. Session nằm trong bytes đã hash, vì vậy thay session làm đổi digest nếu không có va chạm.

**Ảnh hưởng** Không nâng 22/22 thành bằng chứng chống reissuance qua session hoặc ledger khác.

**Probe** `P12`. [test_pre_g3_admission_guard.py L219–224](https://github.com/minhtri22/TokenToModel-Lab/blob/9d210f1392e81a17f1c35cea12230bf7ff74fb02/docs/research/vector-memory/r8/integrated_closure/test_pre_g3_admission_guard.py#L219-L224).

### F09 · HIGH · Amendment cần chấp nhận độc lập và cơ chế vô hiệu hóa có hiệu lực

Miễn backup chỉ áp dụng R8-D, recovery chưa kiểm chứng. Nội dung immutable khi release tồn tại, trong khi người có quyền tương ứng vẫn có thể xóa cả release. Quy tắc hạ kết quả xuống forensic khi mất provenance hợp lý có điều kiện về khoa học. Cơ chế kiểm trước G3 và tái kiểm trước các bước phụ thuộc, chấp nhận riêng rủi ro retention và independent acceptance chưa có. Codex trong phiên này đã soạn đề xuất b1231fa, vì vậy đánh giá kỹ thuật ở đây không thể là ký nhận độc lập cho chính amendment.

**Ảnh hưởng** `RETENTION_AMENDMENT_REVIEW=HOLD`. Cần reviewer distinct với tác giả amendment ghi quyết định có ràng buộc scope/giao thức và kiểm enforcement.

**Probe** `P17`. [TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md L29–53](https://github.com/minhtri22/TokenToModel-Lab/blob/b1231faef1b2a4166016ee78a9de6617800efeff/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_OWNER_RISK_ACCEPTANCE_AND_SCOPED_FINAL_ADJUDICATION_20261115.md#L29-L53).

## Điều kiện còn thiếu trước khi xem xét authoring

1. Một quyết định review độc lập, xác thực và khóa theo exact amendment, scope R8-D, quyền chấp nhận rủi ro retention và quy tắc vô hiệu hóa. Bảo toàn tiền đăng ký prospective và guard G_post.
2. Adapter production được review thực hiện byte readback của source/runtime đang chạy, recompute HMAC V2 từ blueprint và key của custodian, xác minh remote exact asset và signature/timestamp, rồi xác thực riêng signer/commit/receipt chấp nhận cùng session và commitment. Sentinel, fixture mode, cờ do caller đặt hoặc timestamp không chứng minh được thứ tự đều phải từ chối.
3. Một đường launch duy nhất cho generator đã đăng ký, trong đó production không thể chọn fixture hoặc đưa callback tự do. Xác minh bằng probe trước callback, chống replay đồng thời, bảo vệ identity/schema/ACL ledger và chống rollback. Quyết định trước dispatch phải fail-closed khi release bị rút, stale hoặc không kiểm được. Kiểm lại trước bước phụ thuộc và áp dụng invalidation khi provenance mất.

`G2_HOLD · HOLD_INTEGRATED`. Giữ `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`. `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`, `ACTUAL_HMAC_KEY_GENERATED=FALSE`, `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE`.

SQLite transaction rules mô tả serialization của write transactions. Tài liệu SQLite nêu giới hạn khi một database mở qua nhiều link, nên thành công trên một canonical ledger trong race test chỉ chứng minh trong phạm vi đó. [SQLite transactions](https://sqlite.org/lang_transaction.html), [SQLite links and rollback](https://www.sqlite.org/howtocorrupt.html#multiple_links_to_the_same_file).
