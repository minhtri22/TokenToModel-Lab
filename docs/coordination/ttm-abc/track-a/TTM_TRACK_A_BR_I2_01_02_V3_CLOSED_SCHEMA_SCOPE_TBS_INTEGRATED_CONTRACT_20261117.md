# TTM Track A · BR-I2-01/02 V3 — F01/F04/F05/F06 exact-schema, science slot & detached TBS

**Ngày:** 2026-11-17 · **Operation:** `TTM_TRACK_A_BR_I2_01_02_V3_F01_F04_F05_F06_EXACT_SCHEMA_SCOPE_SIGNATURE_FALSIFIER_AMENDMENT_AND_DISTINCT_REREVIEW_ONEPACK`  
**Mode:** `SOURCE_ONLY · DESIGN_ONLY · NO_IMPLEMENTATION · NO_SCIENCE`  
**Exact V2 source for amendment:** `7438e0c16860e69f063307fed5886a5f6bee211b`; distinct [V2 HOLD #6936401307](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6936401307).  
**Integration:** [PM Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32) · `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` (single A/B/C R0–R8 packet, **no Track A micro-permit**).
**I1 accepted and immutable:** M0 v3 source `ec197b5f00d3a037420390edd11ee55047e1d37f`, independent evidence `e3e1c802815f4db1534e92d9848d6015eb9203cc` (35/35 F01/F02, 38/38 custody, 80/80 case, 5/5 group), original frozen record SHA `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`, manifest SHA `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`. V1 and V2 FAIL/HOLD records retained.

## 1. Exact wire rules — closes F01

For this V3 design, all eight schemas below are **CLOSED**. Every named field is required, exactly once, with the type listed; no optional properties, no omitted checkpoint, no null substitution. Schema validators reject unknown keys, duplicate keys **at every object depth**, arrays where not declared, floats, NaN/Infinity, leading zeros, negative integers, int over 2^53−1, untrusted aliases and wrong literal enum values. `uint53_positive` means base-10 integral 1..9007199254740991. `sha256_lower_64` is exactly 64 lowercase `[0-9a-f]`, Git SHA-1 is 40 lowercase hex. `ascii_token_1_to_64` matches `[A-Za-z0-9._:/-]{1,64}`; `utc_seconds_Z` exact `YYYY-MM-DDTHH:MM:SSZ`, valid UTC, no leap-second normalization. Hash value all-zero **only in clearly synthetic test vectors**, and must be rejected for authentic owner/policy/prereg provenance.

`C(obj)` = closed typed JSON object, ASCII field names sorted ascending by raw ASCII byte, compact `:` and `,`, strings restricted to pure ASCII token set requiring **no escaping** (including `created_utc`, whose colons are allowed), JSON literal `true`/`false`, decimal canonical positive integer, no floats/arrays unless a schema explicitly lists them, no BOM, with **exactly one trailing LF byte 0x0A**. Compare original raw bytes to this emitted byte sequence **byte-for-byte** (do not parse and silently reserialize malformed incoming bytes). Newlines inside strings, backslashes, escape forms, Unicode, surrogate encodings, CR/CRLF, double terminal LF, pretty-print and reordered object fields are noncanonical and must HOLD. The detached signature envelope has a tightly defined signatures array; its elements are closed role/key/signature structs, sorted by role then key_id and de-duplicated; no other array permitted. An actual canonical implementation/byte-schema validator has **NOT** been authorized or executed.

For a kind `K` from `SLOT, FINAL_KEY, SCOPE, PAYLOAD, CERT_TBS, PROVENANCE_TBS, RELEASE_TBS, ENVELOPE`, compute:

```
canonical_bytes = C(closed_typed_object)
tag_prefix = ASCII("TTM-A-BR-I2/V3/" + K) || 0x00
H_K = SHA256(tag_prefix || canonical_bytes)
```

The prefix delimiter is a **single binary NUL**, never the ASCII sequence `\\0`. Exact valid object byte streams and expected SHA-256 appear in [machine-readable synthetic test vectors](../../../../artifacts/ttm-abc/track-a/BR_I2_01_02_V3_BYTE_EXACT_TEST_VECTORS_20261117.json) and must be independently recomputed. They are **not real signed attestations**, owner decisions or permission to open checkpoint.

### ScienceSlotV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.science_slot.v3` |
| `question_id` | `literal:TTM-SM4M-DIAG-Q001` |
| `one_shot_family` | `literal:Q001_SINGLE_DIAG` |
| `run_kind` | `literal:I2_RUN` |

### FinalKeyMaterialV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.final_key.v3` |
| `operation_id` | `literal:TTM_TRACK_A_I2` |
| `measurement_source_commit` | `git_sha1_40` |
| `science_slot_sha256` | `sha256_lower_64` |

### LogicalScopeV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.logical_scope.v3` |
| `question_id` | `literal:TTM-SM4M-DIAG-Q001` |
| `operation_id` | `literal:TTM_TRACK_A_I2` |
| `phase_intent` | `literal:I2_RUN` |
| `measurement_source_commit` | `git_sha1_40` |
| `fixture_records_sha256` | `sha256_lower_64` |
| `fixture_manifest_sha256` | `sha256_lower_64` |
| `checkpoint_sha256` | `sha256_lower_64` |
| `prereg_sha256` | `sha256_lower_64` |
| `owner_decision_sha256` | `sha256_lower_64` |
| `science_slot_sha256` | `sha256_lower_64` |

### ReceiptPayloadV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.receipt_payload.v3` |
| `scope_sha256` | `sha256_lower_64` |
| `transaction_id` | `ascii_token_1_to_64` |
| `measurement_source_commit` | `git_sha1_40` |
| `fixture_records_sha256` | `sha256_lower_64` |
| `fixture_manifest_sha256` | `sha256_lower_64` |
| `science_executed` | `literal:false` |
| `i2` | `literal:NOT_EXECUTED` |
| `created_utc` | `utc_seconds_Z` |
| `payload_kind` | `literal:DESIGN_VECTOR_ONLY|PROSPECTIVE_RECEIPT` |

### CertificateTBSV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.cert_tbs.v3` |
| `question_id` | `literal:TTM-SM4M-DIAG-Q001` |
| `measurement_scope` | `literal:M0_V3_ONLY` |
| `source_commit` | `git_sha1_40` |
| `source_review_commit` | `git_sha1_40` |
| `i1_decision` | `literal:I1_PASS_SCOPED_MEASUREMENT` |
| `fixture_records_sha256` | `sha256_lower_64` |
| `fixture_manifest_sha256` | `sha256_lower_64` |
| `issuer_policy_sha256` | `sha256_lower_64` |
| `policy_epoch` | `uint53_positive` |

### ProvenanceTBSV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.provenance_tbs.v3` |
| `certificate_tbs_sha256` | `sha256_lower_64` |
| `review_evidence_commit` | `git_sha1_40` |
| `pm_closure_commit` | `git_sha1_40` |
| `issuer_policy_sha256` | `sha256_lower_64` |
| `policy_epoch` | `uint53_positive` |
| `issuance_intent` | `literal:ISSUE_MEASUREMENT_CERTIFICATE` |

### ReleaseTBSV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.release_tbs.v3` |
| `certificate_tbs_sha256` | `sha256_lower_64` |
| `provenance_tbs_sha256` | `sha256_lower_64` |
| `phase_intent` | `literal:I2_RUN` |
| `adapter_phase` | `literal:run` |
| `science_slot_sha256` | `sha256_lower_64` |
| `scope_sha256` | `sha256_lower_64` |
| `owner_decision_sha256` | `sha256_lower_64` |
| `owner_policy_sha256` | `sha256_lower_64` |
| `one_shot_nonce` | `sha256_lower_64` |
| `expires_utc` | `utc_seconds_Z` |

### CompletionEnvelopeV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.completion_envelope.v3` |
| `scope_sha256` | `sha256_lower_64` |
| `payload_sha256` | `sha256_lower_64` |
| `transaction_id` | `ascii_token_1_to_64` |
| `final_file_id_sha256` | `sha256_lower_64` |
| `verification` | `literal:VERIFIED` |

### DetachedSignatureEnvelopeV3

| Field | Exact type or allowed value |
|---|---|
| `schema` | `literal:ttm.track_a.detached_sig.v3` |
| `tbs_kind` | `enum:CERT_TBS|PROVENANCE_TBS|RELEASE_TBS` |
| `tbs_sha256` | `sha256_lower_64` |
| `policy_sha256` | `sha256_lower_64` |
| `policy_epoch` | `uint53_positive` |
| `signatures` | `array<SignatureEntryV3>_nonempty` |

### SignatureEntryV3

| Field | Exact type or allowed value |
|---|---|
| `role` | `enum:owner|distinct_reviewer|rights_custodian|pm_issuer` |
| `principal_id` | `ascii_token_1_to_64` |
| `key_id` | `ascii_token_1_to_64` |
| `signature_b64` | `canonical_ed25519_base64_64_bytes` |

### Exact absence-vs-null policy and byte construction

Every schema's all-required fields must exist; `checkpoint_sha256` in LogicalScopeV3 cannot be omitted or set to `null`. The real checkpoint pin must match the separately reviewed signed release scope. Any unissued owner/prereg value, omitted policy, or synthetic-only all-zero field is an explicit **HOLD** in production. `created_utc` is frozen at initial journal creation and never refreshed on retry. `ReceiptPayloadV3` contains neither `payload_sha256` nor `staging_sha256`; `CompletionEnvelopeV3` contains payload SHA, but **not its own `envelope_sha256`**. The external PM/Git record may pin envelope SHA after publication. No fixed-point self-hash.

**Receipt stages:** typed logical scope → receipt payload canonical raw bytes → same-dir exclusive stage create → flush + SHA`(PAYLOAD)` → handle-bound native no-replace final publish → re-open final and independently rehash identical byte stream → separately create CompletionEnvelopeV3 holding `payload_sha256` → stage/flush/no-replace publish envelope → external completion digest. Evidence digest domains must be tagged and tied to the same exact bytes; a file's **raw SHA256** must be distinguished from `H_K` tagged semantic digest in the completion record. Document and tests must not conflate these two hashes.

## 2. Global one-shot scientific intent identity — closes F04

**Scope is NOT permit-controlled.** The *frozen policy-owned* Q001 slot identity is the closed `ScienceSlotV3`:
`{schema:"ttm.track_a.science_slot.v3", question_id:"TTM-SM4M-DIAG-Q001", one_shot_family:"Q001_SINGLE_DIAG", run_kind:"I2_RUN"}`. Thus `science_slot_sha256=H_SLOT`, computed by verifier from a separately authenticated **immutable program registry**, not from a field supplied in permit, nonce, checkpoint path, seed, runner version, issue comment or new prereg draft. The fixed Q001 I2 *family* is **one scientific execution intent**; new owner permit versions, retries, minor plan/schema changes, branch changes, signer rotation, or changed `single_science_scope_id` values **do not** mint another Q001 I2 slot.

**Global uniqueness policy:** `question_id`, `one_shot_family`, `run_kind` are immutable signed registry records under the single PM program authority. Registry maps all aliases and historical permit IDs for this intent to the one canonical `H_SLOT`; `NEW_OR_UNKNOWN_ALIAS` without separately adjudicated *new study* => `HOLD_SCOPE_ALIAS_UNKNOWN`. Require a scoped program-owned conflict index preventing duplicate Q001 family enrollment, **not merely one CREATE_NEW file per applicant-selected ID**. A truly distinct future study must have a separately owner-accepted new scientific question/prereg and globally reviewed scope registration; such authority is **NOT** issued in this packet.

**Trusted registry and ledger ordering (future only):** resolve signed root+role policy at exact Git trust anchor → derive `H_SLOT` from immutable policy's fixed Q001 tuple → compare candidate permit slot field to derived hash, reject if different → compare alias registry and already-claimed slot index, reject conflicts → atomically `CREATE_NEW` and **durably seal** ONE global claim keyed by derived `H_SLOT` (not applicant scope) with handle-bound filesystem and global jurisdiction → only after independent release/R0–R8 gates and trusted claim may owner dispatch. If two hosts cannot prove one **shared authoritative global ledger**, reject second and all ambiguous requests (host pinned now; no host migration). Atomic enrollment and claim namespace must be externally audited; no claim may be undone by retry/crash. Status of native registry/ledger implementation = **NOT_EXECUTED**.

**Adversarial equivalence:** Two signed permits P1/P2 with same frozen `Q001_SINGLE_DIAG` but different `single_science_scope_id` or owner decision hash must both resolve to the *same* slot digest. If P2 requests another slot ID, reject **before** any claim. Concurrent create of two aliases to one family => one reserved slot and second HOLD, no second science dispatch. This is stricter than V2 INTEG-06 (same ID replay). **Never claim exactly-once science:** claim after crash is consumed, outcome unknown => HOLD, at-most-one attempted dispatch.

`FinalKeyMaterialV3` binds `operation_id=TTM_TRACK_A_I2`, `measurement_source_commit` and **verifier-derived** `science_slot_sha256` into `H_FINAL_KEY`. Final basename `TTM_A_BR_I2_${H_FINAL_KEY}.receipt.json`, common for all writers of that operation/source/intent regardless random transaction ID or permit version. Stage filename alone contains random tx ID. Different transaction, even identical payload semantics, conflicts; only matching authenticated journal tx + byte hashes permits read-only idempotent ACK.

## 3. Detached signed byte domains — closes F05

### 3.1 TBS (to-be-signed) objects and immutable ordering

All three `CertificateTBSV3`, `ProvenanceTBSV3`, `ReleaseTBSV3` are **closed canonical objects** in §1; none includes `signatures`, `signature_b64`, `public_key`, or its own signature. Frozen TBS bytes use `C(object)` exactly; `H_CERT_TBS`, `H_PROVENANCE_TBS`, `H_RELEASE_TBS` are each tagged `SHA256(tag_prefix||C)`. Vectors include real SHA-256 digests of synthetic unsigned TBS bytes and mutation counterexamples.

For each required `kind` and `role`, signature message (signed raw bytes, **not** JSON envelope including signatures) is:

```
signed_preimage(kind,role,obj) =
 ASCII("TTM-A-BR-I2/V3/SIG/" + kind + "/" + role) || 0x00 || C(obj)
signature_b64 = base64_RFC4648_canonical(Ed25519.Sign(private_role_key, signed_preimage))
```

Roles `pm_issuer, owner, distinct_reviewer, rights_custodian` are separate trusted policy bindings, not strings supplied in permit. The role/kind pair is domain-separated: a valid owner release signature cannot be replayed as reviewer measurement certificate, or as another TBS type. `C(obj)` and signed preimage bytes are frozen **before signing**. Neither `DetachedSignatureEnvelopeV3` nor any signature entry is itself in `C(obj)`; all detached signatures are appended only after verification inputs are fixed.

### 3.2 Detached container and trust verification

`DetachedSignatureEnvelopeV3` has exactly `schema`, `tbs_kind`, `tbs_sha256`, `policy_sha256`, `policy_epoch`, `signatures` (nonempty ordered array of `SignatureEntryV3` with `role,principal_id,key_id,signature_b64`). Each `signature_b64` must decode to exactly 64 Ed25519 signature bytes and use canonical RFC4648 base64 without whitespace; no extra fields, duplicate role, duplicate key ID, role alias, or signature in TBS allowed. Public keys are **never** loaded from this envelope; lookup and independently verify identity/role, effective policy epoch, key ID and revocation in separately reviewed signed **trust-root policy**. Require owner/PM issuer and distinct measurement reviewer for issued I1 provenance; prospective I2 needs three current roles: owner, distinct reviewer, rights custodian. Distinct keys without distinct controlled principal identities and independent private-key custody **do not PASS**.

**Deterministic verification procedure:** parse closed TBS raw with duplicate-key detector → verify raw canonical bytes and schema → recompute tagged TBS hash → compare envelope `tbs_kind`, `tbs_sha256`, `policy_sha256`, `policy_epoch` to TBS and signed policy → resolve each role+principal+key from immutable reviewed policy (never permit contents) → check revocation/expiry/policy anti-rollback → compute **role-specific** signed preimage from raw TBS, verify Ed25519 for every role → reject any missing/extra roles, role swap, mutation, invalid signature, shared principal/controller, source/fixture mismatch. A signed certificate does **not** imply I2 release: separately verify ReleaseTBSV3 and fresh owner decision plus R0–R8.

**Authority status:** no actual issuer keys, trust-root policy attestations, independently signed I1 cert or prospective owner I2 release are created or trusted by V3. All-zero owner sha in test vector is **synthetic** and must be production HOLD. Existing `owner_internal_admission.py` historical URL/runtime and `release_auth_v2.py` three-role fail-closed/no-key configuration remain **unchanged**. `I2_RUN` may map to legacy `run` only by a future exact-SHA reviewed adapter with separate authority; `M0_V3` is never treated as a release permit. No historical verdict rewrite.

## 4. Retained F02/F03 design constraints

V2 design pattern retained, **native proof still HOLD**: `SetFileInformationByHandle(FileRenameInfo)` with `RootDirectory` trusted directory handle, validated relative filename, `ReplaceIfExists=FALSE`, and no `MoveFileExW` path-based fallback; parent/ancestor FileId and ACL plus locking/share modes must prove ancestry remains within trusted project root **at rename linearization**. FileId staying the same after ancestor relocation outside project root is an explicit adversarial falsifier. Same-volume local NTFS, create-new staging, flush, no overwrite, handle-based post-publish SHA/file identity, no unsafe power-loss durability claim. Any unsupported share mode/junction/parent swap/cross-volume or unknown behavior => HOLD.

V2 FSM retained: `ABSENT→PREPARED→STAGED→SEALED→PUBLISHED→ACKED`; incomplete/crash ambiguous => `HOLD_UNKNOWN`. Science FSM `NO_AUTHORITY→AUTHORIZED→CLAIMED_CONSUMED→DISPATCH_ATTEMPTED→TERMINAL/HOLD_UNCERTAIN` only after separate integrated owner release. Receipt publication is **never** science authorization.

## 5. F06 — Adversarial matrix and independent admission

[Machine-readable V3 matrix](../../../../artifacts/ttm-abc/track-a/BR_I2_01_02_V3_NEGATIVE_POSITIVE_QA_MATRIX_20261117.json) keeps all 50 V2 negatives and adds **10 direct falsifiers**: payload self-hash, absent/null schema, noncanonical wire, wrong SHA domain, changed TBS preimage, detached signature cycle, wrong role/domain, two different applicant slot IDs for same Q001 science intent, alias conflict, and concurrent global enrollment. POS-02 now actually specifies *two writers W1/W2* that collide at a deterministic final key; its oracle requires one winner and one loser. All **60 negative + 3 positive cases** carry required fields, all `NOT_EXECUTED_DESIGN_ONLY`. Synthetic wire vectors supply **8 valid + 12 invalid future examples**. **No native/source runtime implementation test is claimed.**

**Author-only gates:** check V2→V3 Git diff contains only design docs/matrix/vectors/handoff/status/receipt, no `tools/`, `.github/`, checkpoint, `lineage.md`, or old V2 files; validate JSON, field sets and unique IDs, cross-check expected test-vector hashes and Git blobs. Author self-QA is not an independent review.

**Independent design gate:** a *different* reviewer must evaluate F01/F04/F05/F06 exact-scope falsifiers and retained F02/F03 at exact V3 SHA, independently recompute 8 vector SHA-256 from raw canonical ASCII + domain NUL, inspect all new negatives and POS-02 two-writer semantics; conclude exactly `DESIGN_ACCEPT_SCOPED` or `HOLD_DESIGN_AMENDMENT`. This is only design acceptance: native API proof, signer custody, global ledger implementation, resource budget and R0–R8 **remain HOLD** until distinct implementation QA and one integrated PM prospective release decision. No new Track A permit.

**Decision invariant:** `I1_MEASUREMENT_CLOSED_PASS_SCOPED · V2_HOLD_PRESERVED · V3_AUTHOR_DESIGN_AMENDED · DISTINCT_V3_REVIEW_PENDING · OWNER_RELEASE_HOLD · I2_NOT_EXECUTED · NO_IMPLEMENTATION · PR33_DRAFT · NO_MERGE`.
