# Track A BR-I2-01/02 V4 · Dual payload hash domains và signed release policy epoch

**Ngày:** 2026-11-17 · **Mode:** `SOURCE_ONLY · DESIGN_ONLY · NO_IMPLEMENTATION · NO_I2`  
**Operation:** `TTM_TRACK_A_BR_I2_01_02_V4_PAYLOAD_HASH_DOMAIN_AND_RELEASE_POLICY_EPOCH_INTEGRATED_AMENDMENT_ONEPACK`  
**Parent PM one-pack:** `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` · [PM Issue #32, V3 independent HOLD](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6936941604).  
**Exact V3 predecessor:** `f97298098c12c55a3abb00cddd757dfde7b364ac` · independent verdict `HOLD_DESIGN_AMENDMENT`.  
**Approved I1 measurement source unchanged:** `ec197b5f00d3a037420390edd11ee55047e1d37f`, independent I1 evidence `e3e1c802815f4db1534e92d9848d6015eb9203cc`. **I1 measurement CLOSED / I2 release HOLD.**

## 0. Amendment scope & frozen successful design

This V4 is a **narrow supplement** to V3: it replaces **only** the ambiguous CompletionEnvelopeV3 schema/semantics and unsigned ReleaseTBSV3 epoch omission for prospective use. All V1–V3 documents, source bytes and adverse reviews are preserved. Retain F02 handle-root `SetFileInformationByHandle(FileRenameInfo)` with `RootDirectory`, native ancestor/root proof HOLD; F03 frozen deterministic `FINAL_KEY`, two competing writers, no overwrite; F04 **globally policy-derived frozen V3 science SLOT** with alias dedup, crash fail-closed and at-most-one dispatch. Detached TBS separation and role/principal constraints remain in force.

**Critical anti-replay invariant:** V4 does **NOT** re-hash `SLOT` under a V4 tag. Frozen V3 `ScienceSlotV3` and `H_SLOT_V3=581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f` remain the only Q001 I2 ledger identity, irrespective of permit/wire version. `H_FINAL_KEY_V3`, `H_SCOPE_V3`, `H_PAYLOAD_V3`, `H_CERT_TBS_V3`, `H_PROVENANCE_TBS_V3` likewise retain exact V3 domains and vectors for compatibility; only prospective `RELEASE_TBS` and `ENVELOPE` move to independently disambiguated V4 schemas/tags. **No old V3 release TBS/envelope may be silently accepted as V4.**

## 1. F01: raw file SHA-256 ≠ tagged semantic SHA-256

### 1.1 Closed prospective CompletionEnvelopeV4

Every property is required, exactly once, no null, unknown fields, duplicates, non-canonical encoding, or implicit fallback:

| Field | Type / meaning |
|---|---|
| `schema` | literal `ttm.track_a.completion_envelope.v4` |
| `scope_sha256` | lowercase 64-hex **frozen `H_SCOPE_V3`** |
| `payload_raw_sha256` | lowercase 64-hex `SHA256(C(ReceiptPayloadV3))`; **hash of on-disk payload file bytes**, no domain prefix |
| `payload_tagged_sha256` | lowercase 64-hex `SHA256(ASCII("TTM-A-BR-I2/V3/PAYLOAD") || 0x00 || C(ReceiptPayloadV3))`; **semantic tagged hash** |
| `transaction_id` | same immutable journal transaction identifier, ASCII token |
| `final_file_id_sha256` | lowercase 64-hex evidence digest of *opened final file identifier*, not payload digest; only public-safe hashed value |
| `verification` | literal `VERIFIED` and **only after** independent raw+tagged checks have both passed |

No field `payload_sha256`, `staging_sha256`, `published_sha256` or `envelope_sha256` allowed. `CompletionEnvelopeV4` itself **does not contain its own SHA**. An external immutable Git/PM evidence record may hash the completed envelope bytes after publish.

**Mathematical domains (exact bytes):**

```text
B = C(ReceiptPayloadV3)   # canonical ASCII JSON, compact/sorted, one terminal 0x0A
RAW = SHA256(B)            # payload file/stage/final whole-byte integrity
TAG = SHA256(ASCII("TTM-A-BR-I2/V3/PAYLOAD") || 0x00 || B)
CompletionEnvelopeV4.payload_raw_sha256 = RAW
CompletionEnvelopeV4.payload_tagged_sha256 = TAG
H_ENVELOPE_V4 = SHA256(ASCII("TTM-A-BR-I2/V4/ENVELOPE") || 0x00 || C(CompletionEnvelopeV4))
```

**Fixed synthetic PAYLOAD test vector from V3** (`PAYLOAD-VALID`, 533 exact bytes):
- `RAW = a4bca0d2d9d64b2c3b1882764abf421fe872e671e42fa1a62a8147d2675c55b4`
- `TAG = e27ae8e39fbd669e152339b271ef69034f69564063d57f286dbc878bc433ce55`
- These must be independently recomputed **from the exact canonical_ascii bytes**, not copied from the expected values.
- Synthetic `ENVELOPE-VALID` V4 contains **both**, yielding 458 bytes and `H_ENVELOPE_V4 = 7151df6bbca3b7e8ff8f2bff520795ce4431efc620438958448a97f4f5f6f5df`.

**Publication/verification order:** source pin & handle-open → read frozen input snapshots → canonical `B` → stage create-new → flush → compute `RAW_stage` over **stage handle bytes** and `TAG_stage` over exact same `B` → handle-relative no-replace publish → open final by validated handle → independently compute `RAW_final` and `TAG_final`; assert `RAW_stage=RAW_final=RAW`, `TAG_stage=TAG_final=TAG` → build **separate** CompletionEnvelopeV4 after both checks → stage/flush/no-replace publish envelope → external Git evidence hash of envelope. Any mismatch or ambiguous provenance = **HOLD**, no "repair" by overwriting final. A raw SHA alone **never** proves the correct semantic tag; a tagged SHA alone **never** proves raw-file equality.

V3 `CompletionEnvelopeV3.payload_sha256` is a historical ambiguous field; do not support it under V4 `schema` even with equal value. `ATOMIC-28` swaps RAW/TAG but retains syntactically valid hashes; `ATOMIC-29` sends lone legacy field or missing/null. **Both must HOLD**.

## 2. F05: signed release policy epoch exact binding

### 2.1 ReleaseTBSV4: additive mandatory signed field

V4 closed schema is exactly ReleaseTBSV3's original **eleven** named fields, plus mandatory `policy_epoch:uint53_positive` and versioned literal `schema=ttm.track_a.release_tbs.v4`. Every field required, exact typed, no unknown/extra/null/duplicate. `policy_epoch` is integer from trusted policy, not a free-form applicant field. Values of `owner_policy_sha256` must be digest of **exact separately reviewed raw trusted policy bytes**, pinned to a Git blob and owner/out-of-band root (not derived from provided permit). The trusted policy record must itself include that epoch and monotonic anti-rollback anchor; signatures/role/key binding are verified separately.

**V4 detached signature TBS preimage** (same role separation as V3, but strictly new tag):
```text
B_release = C(ReleaseTBSV4)
H_RELEASE_TBS_V4 = SHA256(ASCII("TTM-A-BR-I2/V4/RELEASE_TBS") || 0x00 || B_release)
SIGNED_RELEASE_ROLE_BYTES = ASCII("TTM-A-BR-I2/V4/SIG/RELEASE_TBS/" + role) || 0x00 || B_release
signature[role] = ED25519.Sign(trusted_role_private_key, SIGNED_RELEASE_ROLE_BYTES)
```
The signature container **does not contain its own signatures in signed TBS**. Future `DetachedSignatureEnvelopeV4` is a *different object* holding `schema=ttm.track_a.detached_sig.v4`, `tbs_kind=RELEASE_TBS`, `tbs_wire_version=V4`, `tbs_sha256=H_RELEASE_TBS_V4`, `policy_sha256=ReleaseTBSV4.owner_policy_sha256`, `policy_epoch=ReleaseTBSV4.policy_epoch`, and ordered verified signature entries. **No trusted key is supplied in permit/envelope**. For historical `CERT_TBS` / `PROVENANCE_TBS`, the wire version remains V3 and their own issuer policy/epochs remain pinned; cross-kind signature reuse is prohibited.

**Verifier equality rules (all mandatory):**
```text
TBS.policy_epoch
  == DetachedSignatureEnvelopeV4.policy_epoch
  == TrustedOwnerPolicy.policy_epoch
  >= TrustedOwnerPolicy.antirollback_epoch_floor
TBS.owner_policy_sha256
  == DetachedSignatureEnvelopeV4.policy_sha256
  == SHA256(exact_trusted_policy_raw_bytes)
H_RELEASE_TBS_V4 == DetachedSignatureEnvelopeV4.tbs_sha256
```
`TrustedOwnerPolicy` MUST be resolved by immutable externally reviewed trust anchor, not a permit-supplied URL/key/epoch; the monotonic trusted epoch floor must survive rollback and be outside attacker-controlled permit storage. If TBS epoch missing, old schema V3, epoch mutated after signing, envelope epoch 2 vs signed TBS epoch 1, trusted policy epoch=2 but signed old epoch=1, root/host/signer mapping changes, or policy SHA mismatch => **HOLD** before any release gate/nonce/checkpoint. Do not treat the epoch as a data-only annotation: it is included **inside signed canonical TBS preimage**.

**Synthetic release vector only:** `ReleaseTBSV4.policy_epoch=1`, `owner_policy_sha256=4444...`, `owner_decision_sha256=0000...` are non-authoritative test fixtures; the last all-zero value is **invalid** for a real owner decision. Exact `C(ReleaseTBSV4)` length **758** bytes and `H_RELEASE_TBS_V4=c3cf68c0ad731a127857dc20248b419ca21f0247475304426f3803c9a78dbac3`. No actual Ed25519 keys or valid release signatures are produced.

### 2.2 Phase adapter and historic authority unchanged

`I2_RUN` can map to `authenticate_release(phase="run")` only by a future separately reviewed adapter and separately authenticated owner release. `M0_V3` measurement certificate is **not** release. Legacy `owner_internal_admission.py` still points to historical Q001 verdict and will fail closed; `release_auth_v2.py` trust anchor map remains empty. This amendment contains **no patch to either file**, no external key issuance and no native one-shot ledger run. A DESIGN_ACCEPT would not itself authorize implementation.

## 3. Retained F02/F03/F04 & direct falsifiers

The F02 handle-based rename/ancestor race proof, F03 final-key competitive no-replace semantics and F04 globally fixed `ScienceSlotV3` are **unchanged as design** and continue to require independent Windows-native and owner-signature proof in a future authorized integrated release packet. Do not recreate a new global ledger identity by reusing a V4 domain tag for `SLOT`.

[Machine-readable V4 vectors](../../../../artifacts/ttm-abc/track-a/BR_I2_01_02_V4_EXACT_DOMAIN_TEST_VECTORS_20261117.json) retain **six V3 preimages/digests** and update exactly **RELEASE_TBS** / **ENVELOPE** under explicit V4 tags; include the raw file hash separately for `PAYLOAD` and five new invalid examples.

[Adversarial V4 matrix](../../../../artifacts/ttm-abc/track-a/BR_I2_01_02_V4_NEGATIVE_POSITIVE_QA_MATRIX_20261117.json) retains all **60 V3 negative IDs + 3 positive controls**, adds **5 new negatives** with direct F01/F05 falsifiers: `ATOMIC-28/29`, `AUTH-26/27`, `INTEG-09`. `POS-02` remains the true W1/W2 two-writer race and now independently verifies both raw and tagged file digests in its success oracle. All cases `NOT_EXECUTED_DESIGN_ONLY`.

**Reviewer criteria:** independent exact SHA re-review must recompute 8 tagged vector SHA-256 + **payload RAW SHA-256** from wire bytes, check new `ReleaseTBSV4.policy_epoch` is signed and matches policy/envelope epoch, inspect role-specific signed preimage version separation, reject `ATOMIC-28/29`, `AUTH-26/27`, `INTEG-09`, and check no code/guard/frozen fixture/lineage diff. Review decision limited to `DESIGN_ACCEPT_SCOPED` / `HOLD_DESIGN_AMENDMENT`; author static QA **not independent**. R0–R8 PM owner GO/HOLD remains consolidated, never micro-permit.

**Status:** `V3_HOLD_DESIGN_AMENDMENT_PRESERVED · F01_F05_V4_AMENDED_AUTHOR_ONLY · F02_F03_F04_SCOPED_DESIGN_PRESERVED · OWNER_RELEASE_HOLD · I2_NOT_EXECUTED · NO_IMPLEMENTATION · NO_MERGE`.
