# Track A — A_R0_R1_R5_R7_R8_READINESS · PM ABC V4 one-pack input

**Ngày:** 2026-11-17 · **Operation:** `TTM_A_V4_MEASUREMENT_RELEASE_BARRIER_AND_CROSS_TRACK_INTERFACE_DESIGN_ONEPACK`  
**Role:** Agent A — Measurement/Release Contract Owner · **Mode:** `DESIGN_ONLY · SOURCE_ONLY · NO SCIENCE`  
**Required shared contract (frozen):** [PM ABC V4 contract](https://github.com/minhtri22/TokenToModel-Lab/blob/403491b698ba6586193f2ff2ae00c4441c10c595/docs/coordination/ttm-abc/TTM_PM_ABC_V4_SHARED_COORDINATION_CONTRACT_20261117.md) · commit `403491b698ba6586193f2ff2ae00c4441c10c595`, **Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`**, exact content fetched and matched. **ACK trước authoring:** [`ABC_CONTRACT_ACK_A`](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937430413).  
**A input:** [Draft PR #33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) HEAD `e6746184603f038b49d1e7d472367b6354474ba2`, PR #28 base `ebdc54575eed1ff60c402eecf60289f408bb38ca`; I1 accepted source `ec197b5f00d3a037420390edd11ee55047e1d37f`, evidence `e3e1c802815f4db1534e92d9848d6015eb9203cc`. [V4 distinct AI verdict `DESIGN_ACCEPT_SCOPED`](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937099406).  
**Contract authority:** PM owns unified A→C→B→PM handoff, not Agent A. This document is **a readiness design supplement**, not ReleaseTBSV5, not a new wire format, signer key, scientific endpoint or permit.

## 1. Decision boundary, evidence and traceability

- **I1:** `I1_PASS_SCOPED_MEASUREMENT` closed at `ec197b5f00d3a037420390edd11ee55047e1d37f` only. Independent F01/F02 **35/35**, custody **38/38**, private 80/80 case & 5/5 group digest; source readback from [evidence](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md). No rerun is being claimed in this handoff. I1 does **not** entail model ability, real SFT success, any I2 entitlement, or a new scientific result.
- **V4 source/design:** independently `DESIGN_ACCEPT_SCOPED` at `e6746184603f038b49d1e7d472367b6354474ba2`: 8/8 tagged SHA-256 vectors + raw payload checksum reviewed, six Git blobs matched; 65 future negatives, three positives structurally sound. Author QA and **distinct AI review are not native proof or human signature**. Prior V1/V2/V3 adverse verdicts retained.
- **Release state:** Historical owner-internal preflight remains `HOLD_OWNER_INTERNAL_I1_NOT_PASS`, exit code 2, because its legacy versioned verdict does not apply to M0 v3 acceptance. `release_auth_v2.py` has unpopulated trusted Ed25519 map; no trust anchor or signed release authorized. DO NOT change historical verdict, repoint guard, or patch runtime to fabricate PASS. `I2=NOT_EXECUTED`, no checkpoint forward/nonce/optimizer, no auto-merge.
- **Cross-track anti-conflation:** A canonical **ASCII**, schema-closed `ReceiptPayloadV3` + `ReleaseTBSV4` / `CompletionEnvelopeV4` uses tagged hash prefixes. B/C synthetic SFT v2 uses **UTF-8** sorted compact JSON + terminal LF and its own 7 raw artifact SHA-256/manifest. A's original TRAIN-only T4 BPE (`cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`) is **not** equivalent to B/C synthetic byte tokenizer without independently sourced token-level compatibility. They coexist only as **namespaced logical refs** in PM evidence index.

## 2. A-owned R0–R8 readiness (global PM decision is NOT made here)

| Gate | Accountable design role and evidence | A assessment | Unresolved STOP/HOLD |
|---|---|---|---|
| **R0** · Source/dependencies/merge graph | A verifies PR33 exact V4, I1 source SHA, shared contract and parent PR28; B owns code graph | `PASS_SCOPED` | HOLD_MERGE; no final stack merge authorization |
| **R1** · I1 measurement oracle | I1 M0 v3 independent 35/35 + custody 38/38 + 80 cases/5 groups; verified report, NOT a new real model evaluation | `PASS_SCOPED` | C gold/rater and real eval remain HOLD_UNPROVEN |
| **R2** · Data rights, split provenance | C owns source/rights/splits; A can require raw digest/lineage only | `HOLD` | No rights signature or proof from A |
| **R3** · Checkpoint/tokenizer/interface | B owns actual real weights and codec; B/C v2 synthetic UTF8 byte tokens not original T4 BPE | `HOLD` | No substitution of B/C metadata for real checkpoint |
| **R4** · Native host compute/watchdog | B host resource proof missing for prospective I2/real SFT | `HOLD` | No memory/rate/budget PASS inferred from synthetic CI |
| **R5** · Atomic receipt/release authority | V4 dual raw/tag hashes, signed release epoch, frozen Q001 SLOT; independent DESIGN_ACCEPT_SCOPED | `DESIGN_ONLY` | Native ancestor/ACL/sharelock, no-overwrite, crash/powerloss, global ledger, owner signers HOLD |
| **R6** · Prereg/equal-budget scientific endpoints | C owns evaluation question, fresh TEST and statistical thresholds; A supplies scorer linkage | `HOLD` | No prospective freeze/TEST GO |
| **R7** · Distinct candidate QA | V4 reviewer separate AI session accepted source/design 8/8 vectors and 68/68 declared schemas | `DESIGN_ONLY` | 65 negatives and 3 positives executed 0; distinct native/implementation QA missing |
| **R8** · Owner authorization | Single signed and independently validated owner/PM decision after all program predicates | `HOLD` | I2 NOT_EXECUTED, historical preflight HOLD exit 2, no signature/permit |

**Only A-owned input:** R0 source pins, R1 metric/oracle, R5 OnePack/release design, R7 A-side negative QA plan, R8 owner decision requirements. R2 and R6 **belong to C**; R3 and R4 **belong to B**; no A self-adjudication or transfer of their field ownership.

## 3. Frozen V4 release and measurement semantics — NO V5

| Contract element | Frozen V4 meaning | Proof required for future release | Current |
|---|---|---|---|
| `payload_raw_sha256` | `SHA256(C(ReceiptPayloadV3))`: whole **on-disk canonical payload file** raw bytes, no prefix | source/stage/final file bytes, independent final readback, compare to envelope field | `DESIGN_ACCEPT_SCOPED`; no runtime |
| `payload_tagged_sha256` | `SHA256(ASCII("TTM-A-BR-I2/V3/PAYLOAD") || 00 || C(payload))`; NOT raw | recompute from exact raw canonical payload in opened handles; rejects swapped raw/tagged | `DESIGN_ACCEPT_SCOPED`; no runtime |
| `CompletionEnvelopeV4` | contains both mandatory hashes, transaction ID and scope; does **not** contain its own SHA | only after flush, no-replace publish and separate postpublish rehash; external evidence SHA after envelope frozen | `DESIGN_ACCEPT_SCOPED`; no native |
| `ReleaseTBSV4.policy_epoch` | positive safe integer included in signed raw canonical TBS bytes | `epoch_TBS = epoch_detached = epoch_trusted_policy >= epoch_floor`; authenticated trust policy SHA, expiry/revocation and anti-rollback | `DESIGN_ACCEPT_SCOPED`; no signed permit |
| V4 Ed25519 role-bound preimage | `ASCII("TTM-A-BR-I2/V4/SIG/RELEASE_TBS/" + role) || 00 || C(ReleaseTBSV4)` | owner, distinct reviewer, rights custodian independently authenticated, out-of-band trust roots, signature and principal custody check | `OWNER_AUTHORITY_HOLD` |
| `H_SLOT_V3` | **`581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f`** global Q001 `I2_RUN` one-shot identity | signed registry deriving same immutable slot for any permit/runner revision; one global claim ledger and alias rejection | `DESIGN_ACCEPT_SCOPED`; global/native ledger HOLD |
| `H_FINAL_KEY_V3` | stable deterministic receipt key, randomized staging only | concurrent W1/W2 no-replace test, read-only idempotent same-tx ACK, competing tx HOLD | `NATIVE_NOT_EXECUTED` |
| Historical preflight | old verdict URL and old runtime SHA scope remain immutable | future **separate reviewed** versioned authority adapter without bypass; cannot silently reuse old verdict | `RELEASE_HOLD_EXIT_2` |

Synthetic illustrative digest pins (never a valid owner authority): `PAYLOAD_RAW=a4bca0d2d9d64b2c3b1882764abf421fe872e671e42fa1a62a8147d2675c55b4`; `PAYLOAD_TAGGED=e27ae8e39fbd669e152339b271ef69034f69564063d57f286dbc878bc433ce55`; `H_RELEASE_TBS_V4=c3cf68c0ad731a127857dc20248b419ca21f0247475304426f3803c9a78dbac3`. These are **example vector bytes**, not actual run receipt or signed release.

## 4. Finite implementability and owner-native negative QA proof plan (future, not authorized)

**R5-A input custody:** from trusted project root, open each ancestor **component by component**, reject symlink/junction/reparse/ADS/untrusted ACL; pin trusted handles, volume & FileId; test attacker moves ancestor outside root *while FileId unchanged*. The native protocol must prove containment at rename linearization via verified share/ACL constraints or HOLD. Early `resolve()`, `Test-Path` and post-hoc FileId alone are insufficient.

**R5-A no-overwrite/atomic publish:** local NTFS verified, create-new randomized same-dir stage → canonical ASCII payload → flush+hash raw/tag → native handle-relative `SetFileInformationByHandle(FileRenameInfo)` with `RootDirectory` trusted parent and `ReplaceIfExists=FALSE` → reopen final under verified handle → rehash and compare raw/tag → separately create/flush/no-replace envelope. Race two synchronized writers for the same deterministic final; **exactly one** can win, loser HOLD. Target existing, post-publish mutation, renamed ancestor, cross-volume, unsupported FS, ACL or share violation => HOLD; **no path-based rename fallback**.

**R5-A crash/durability:** fault injection before stage, after stage flush, immediately before rename, after namespace rename/before ACK, after envelope, and after science claim/before possible dispatch; process crash vs cold reboot/power loss are different test classes. Distinguish NTFS namespace atomicity from *directory-entry durability after power loss*. Future test must document OS/NTFS/volume, failure injection, stable file identity and hash after reboot, anti-rollback/custody audit, and any unsupported guarantee as HOLD. **Do not destructively power-cycle an active owner machine without owner controlled experiment plan**. Unknown crash status => `HOLD_UNKNOWN`, never automatic retry science.

**R5/R8 one-shot and signing:** immutable PM policy owns global Q001 slot independent of nonce/permit revision. Require one globally authoritative atomic no-retry claim before any checkpoint read; two IDs for one scientific intent must conflict. After possible claim, ambiguous crash consumes attempt, not reauthorizes. Independently trust-root-anchored owner/key/principal identities, exact TBS signable bytes, policy epoch anti-rollback, expiry/revocation, and owner decision must be verified outside unsigned issue comments. **Today no key, permit, signature, register/ledger claim or native execution is authorized.**

**R7 QA plan:** [machine-readable classification](../../../../artifacts/ttm-abc/track-a/A_V4_SOURCE_NATIVE_QA_PROOF_MATRIX_20261117.json) reproduces **65 unchanged V4 negative IDs** and **POS-01/02/03**, with source/native tier and evidence oracle. Counts: **41 future source negative**, **24 future Windows-native negative**, 3 positive (tiers per frozen matrix); all `NOT_EXECUTED_DESIGN_ONLY` and `DISTINCT_IMPL_QA_NOT_EXECUTED`. Mandatory high-risk negative clusters: `ATOMIC-02/05/06/17/21/23/28/29`, `AUTH-09/10/13/20/22/26/27`, `INTEG-06/08/09`, plus W1/W2 POS-02. One source-only QA pass will never substitute for native fault/race/privileged proof.

## 5. Exact merge/dependency and joint compatibility boundaries

| Input/output | Exact source | Owner | A claim / dependency |
|---|---|---|---|
| PR #28 → PR #33 | `ebdc54575eed1ff60c402eecf60289f408bb38ca` → `e6746184603f038b49d1e7d472367b6354474ba2` | A/PM | stacked, both Draft, no merge; source I1 frozen |
| PR #34 → PR #36 | `43896bcd034c82e8433bc6a2b53eefbd936616fb` → `09de6a46574146d863f416e056fcf01091f3efb8` | B/PM | synthetic BC `PASS_ENGINEERING_SCOPED`; not a real trained SFT |
| PR #35 | `00afd25aa2234e30f7602592d49d5d9f2947965b` | C/PM | C M4 design; rights, gold/real evaluation remain HOLD |
| `main` | `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` | PM | no merge and no `lineage.md` mutation |
| Shared authority | `403491b698ba6586193f2ff2ae00c4441c10c595` (Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`) | PM | A ACK posted; C/B must separately ACK same exact blob |

**Single owner release question for future PM:** *Given exact A/C/B source and scientist-approved data/gold, actual independent source+native guards, global ledger durability, authenticated signer/principal trust roots and capacity/prereg evidence, may one specified Q001 I2 action be authorized on the pinned host/bytes/expiry?* **Currently answer = HOLD**. PM adjudicates one integrated A/C/B R0–R8 packet; A does not issue release permit.

**Result of this operation:** `A_PACKET_READY_SCOPED` **means A input documents are ready for C**, NOT `I2_RELEASE_PASS`. No executable changes, no native tests, no model, no merge, no owner GO.
