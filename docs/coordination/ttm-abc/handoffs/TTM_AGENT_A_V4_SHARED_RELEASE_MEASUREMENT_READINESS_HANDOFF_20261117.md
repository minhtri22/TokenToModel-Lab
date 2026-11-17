# HANDOFF — Agent A · V4 measurement/release input to ONE ABC contract

**Operation:** `TTM_A_V4_MEASUREMENT_RELEASE_BARRIER_AND_CROSS_TRACK_INTERFACE_DESIGN_ONEPACK`  
**Role:** Track A owner — measurement validity, release authority and OnePack atomicity semantics.  
**Mode:** `EXACT_SHA · DESIGN_ONLY · SOURCE_READBACK · NO_IMPLEMENTATION · NO_NATIVE_RUN · NO_I2`.

## Mandatory common contract and ACK

**FIRST read [PM shared contract at immutable commit](https://github.com/minhtri22/TokenToModel-Lab/blob/403491b698ba6586193f2ff2ae00c4441c10c595/docs/coordination/ttm-abc/TTM_PM_ABC_V4_SHARED_COORDINATION_CONTRACT_20261117.md) — exact Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`.** No alternate schema, no new I2 identifier, and no independent A owner permit. Post `ABC_CONTRACT_ACK_A` + shared blob, PR33 source HEAD and design review comment to [PM Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32) before authoring. If mismatch, `HOLD_CONTRACT_MISMATCH`.

**Source:** PR33 HEAD `e6746184603f038b49d1e7d472367b6354474ba2` (read HEAD again, do not silently substitute); I1 execution source `ec197b5f00d3a037420390edd11ee55047e1d37f`; V4 [contract](https://github.com/minhtri22/TokenToModel-Lab/blob/e6746184603f038b49d1e7d472367b6354474ba2/docs/coordination/ttm-abc/track-a/TTM_TRACK_A_BR_I2_01_02_V4_PAYLOAD_DUAL_HASH_RELEASE_EPOCH_CONTRACT_20261117.md); [independent verdict](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937099406) = `DESIGN_ACCEPT_SCOPED`.

## One integrated A task — do not invent V5

1. Treat **I1** as already `CLOSED_PASS_SCOPED_MEASUREMENT`; don't re-run, re-tune or equate I1 success with I2 permission. Map exact A measurement input/outputs and release authority to shared R0/R1/R5/R7/R8; explicitly tell C which measurement fields and domain-locked raw bytes are *meaningful* and which remain design-only.
2. Freeze **V4 schema as accepted design**: `ReleaseTBSV4.policy_epoch` within role-separated signed preimage, signed TBS / detached envelope / trusted policy epoch equality and antirollback floor; raw vs tagged payload SHA in `CompletionEnvelopeV4`; `H_SLOT_V3=581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f` stays identical across versions. No V4 hash-domain change for slot, final key, scope, payload, cert/provenance.
3. Compile an **implementability and native-proof plan**, not code: owner trust-anchor/key/principal custody, release preflight stale historical owner decision, Win32 handle-root ancestry proof after parent movement, no-replace final publication, crash/reboot/ledger one-shot, dual digest readback and committed envelope, no silent retry. Mark each `DESIGN_ACCEPTED` vs `NATIVE_NOT_EXECUTED` vs `OWNER_AUTHORITY_HOLD`. Address prior TOCTOU advisories as release barriers, not I1 rejections.
4. Preserve 65 distinct negative + 3 positive V4 **planned-only** IDs. Partition into source simulation versus owner-native/privileged future execution; list all existing 5 new falsifiers (`ATOMIC-28/29`, `AUTH-26/27`, `INTEG-09`) and POS-02 W1/W2. Do not say 68/68 runtime PASS. No real Ed25519 signatures or release keys now.
5. Provide C and B an explicit **A→(C,B) measurement/custody requirements table** with field names, units, byte/hash domains, version, validation, error/HOLD behavior, and exact source pin. These are **requirements**, not an incompatible replacement for B/C v2's UTF-8+LF artifact format. Tell B how future real runner must expose immutable evidence and stop on authorization failure; tell C what primary/secondary likelihood endpoints may use after their own distinct validity test.
6. Produce single `A_R0_R1_R5_R7_R8_READINESS.md` and `A_TO_BC_REQUIREMENTS.md` (names may be equivalent) on A's existing review/docs branch only. Include R0–R8 statuses for A, exact cited sources, proposed independent source/native negative QA, and one finite owner release decision question. Post GitHub immutable commit + file links + `A_PACKET_READY_SCOPED` to Issue #32 for Agent C.

## Acceptance and stop conditions

`A_PACKET_READY_SCOPED` means **a sufficiently specified design input** for C, *not* A-I2 science readiness. If missing keys, release decision, parent ancestry proof or no-overwrite durability, say `A_RELEASE_HOLD`. No changes to existing `owner_internal_admission.py`, `release_auth_v2.py`, source I1, original V4 contract, fixture, workflows, `lineage.md`, main or other agents' branches. No checkpoint/model/GPU/native/one-shot dispatch. No auto-merge.

**Handoff to Agent C (next in sequence):** exact A document commit, shared-contract blob, R0–R8 A statuses, issue comment and *unchanged* source pins. `TTM_C_SHARED_SCIENCE_DATA_EVAL_CONTRACT_DESIGN_ONEPACK`.
