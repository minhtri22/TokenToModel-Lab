# TTM PM · ABC V4 shared coordination contract — ONE source of truth for A/C/B handoffs

**Operation:** `TTM_PM_ABC_V4_CONTRACT_FIRST_OWNER_RELEASE_READINESS_AND_CROSS_AGENT_ALIGNMENT_DESIGN_ONEPACK`  
**Mode:** `DESIGN_ONLY · READ_EXISTING_EVIDENCE · NO_SCIENCE · NO_MERGE`  
**Contract steward:** PM. **Task sequence:** A → C → B → PM; no agent independently publishes a divergent "final integration contract". All handoffs reference **this exact Git blob and the immutable commit containing it**, not a moving branch name. This contract does *not* supersede project-specific frozen schemas or source artifacts.

## 1. Exact source registry (2026-11-17 snapshot; refresh HEAD before each agent acts)

| Ref | Exact SHA | Review status and boundary |
|---|---|---|
| `main` | `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` | `lineage.md` L0000–L0029 unchanged; no merge permit |
| PR #28 A stack base | `ebdc54575eed1ff60c402eecf60289f408bb38ca` | Draft, parent of PR #33 |
| PR #33 Track A | `e6746184603f038b49d1e7d472367b6354474ba2` | V4 independent `DESIGN_ACCEPT_SCOPED`, I1 source `ec197b5f00d3a037420390edd11ee55047e1d37f` PASS measurement, I2 HOLD |
| PR #34 Track B | `43896bcd034c82e8433bc6a2b53eefbd936616fb` | M3 PM `PASS_ENGINEERING_SCOPED` plus V3 peak-accounting dissent; no science |
| PR #35 Track C | `00afd25aa2234e30f7602592d49d5d9f2947965b` | C M4 PASS_DESIGN, real data/gold incomplete, C B/C Part B accepted |
| PR #36 B/C v2 | `09de6a46574146d863f416e056fcf01091f3efb8` | B source `a83e1526bce842761f3051dad28b90a55395a6aa`, synthetic interface PM `PASS_ENGINEERING_SCOPED` |
| PM R0–R8 design | `c4c8cccaa0bde34a5e93024c7c4e12be2d60a582` | Integrated release barriers, lineage append candidates only |
| PM BC final | `82aaf2a881bd677afd8f6e600eb570aea897fdba` | Independent 12/12 per Windows/Linux Python3.12, tested trusted bundle |
| Track A V4 independent verdict | [Issue #32 comment #6937099406](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937099406) | `DESIGN_ACCEPT_SCOPED`, 8/8 tagged vectors, RAW, 65 planned negatives + 3 positives **NOT EXECUTED** |

All GitHub PRs remain Draft/unmerged. If any exact candidate HEAD changes after this registry, **pin the new SHA and report the diff as `SOURCE_DRIFT`**; do not silently substitute mutable `HEAD` for pinned authority.

## 2. Two distinct frozen wire domains — do not conflate

**Track A release / OnePack V4 (domain A):**
- `ReleaseTBSV4.policy_epoch` must be present in role-bound Ed25519 signed canonical preimage; `epoch_TBS=epoch_envelope=epoch_trusted_policy>=antirollback_floor`.
- `CompletionEnvelopeV4` carries **separate** `payload_raw_sha256` (exact on-disk file bytes) and `payload_tagged_sha256` (V3/PAYLOAD tag + NUL + canonical bytes); no legacy `payload_sha256` fallback.
- Global `H_SLOT_V3=581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f` is frozen **across V4**; never mint another Q001 I2 one-shot identity.
- 65 negative and 3 positive **DESIGN ONLY**, not native PASS. Owner keys/principals, handle-root ancestry races, ledger consistency, power-loss durability, historical release preflight remain HOLD. **A design contract is not an owner signature or I2 release.**

**Track B/C synthetic SFT v2 (domain BC):**
- Typed C `str` → strict UTF-8 → B `list[int]` with byte tokens 0..255 and reserved EOS=256, PAD=257, BOS=258, SYS=259, USER=260, ASSIST=261, EOT=262; raw historical T4 BPE **is not proven equal** to this synthetic codec.
- B/C v2 canonical JSON: UTF-8 sorted/compact, **one terminal LF**, 7 persisted real artifact-byte SHA256 fields + manifest and fail-closed `bridge_schema`/manifest symlink. C contract A01–A16 and B/C negative QA apply to BC, not A.
- BC checkpoint schema is **metadata-only** and has no actual trained SFT weights; path-level symlink checks do not prove TOCTOU-safe untrusted Windows filesystems.
- **Do not force A canonical ASCII release bytes and BC canonical UTF-8 data bytes into a single serializer**; join them only in a higher-level PM evidence index with namespaced refs.

## 3. Single PM evidence-index contract (design-only; NO new runtime wire schema)

Each proposed evidence row MUST have exactly these *logical fields*: `track`, `artifact_kind`, `git_url`, `exact_commit`, `git_blob_sha1` (where available), `raw_sha256` (where available), `domain_tag` (A/V3,A/V4,BC/v2,or none), `origin_actor`, `review_actor`, `gate_status`, `scope`, `executed` (true/false), `limitation`. Unknown bytes must remain `UNVERIFIED` (never guess hashes). This is only a coordination index and does **not** create an on-disk receipt, signing key or checkpoint format. Link the immutable source artifact itself.

Common gate status vocabulary: `PASS_SCOPED`, `HOLD`, `FAIL`, `UNVERIFIED`, `NOT_EXECUTED`, `DESIGN_ONLY`. Always distinguish **author QA, C cross-contract QA, PM distinct AI QA, Windows native QA, and real science**. No AI session can claim authenticated independent human custody.

## 4. Ownership and R0–R8 accountability

| Barrier | Accountable agent(s) for **design evidence only** | Boundary |
|---|---|---|
| R0 source/dependency/merge graph | B owns code/checkpoint graph, A/C countersign their own exact inputs | No merge |
| R1 measurement + gold/rubric | A owns metric/oracle; C owns scientific gold/rater and test meaning | I1 PASS is *not* SFT quality |
| R2 data rights, provenance, fresh splits | C owns | No fake private-rights signoff or reused historical TEST |
| R3 checkpoint, tokenizer, interface | B owns actual weights/byte custody; C accepts semantic compatibility; A audits metric linkage | B/C synthetic v2 ≠ original T4 BPE |
| R4 hard compute/resource constraints | B owns feasibility, watchdog, budget readback; C specifies required compute | No new GPU/native dispatch |
| R5 atomic evidence and release authority | A owns OnePack V4; B owns future runner/BC filesystem surface | No V3 historical edits; TOCTOU held |
| R6 prereg, endpoints, equal-compute | C owns study design; A confirms measurement/falsifiers; B confirms feasible budget | No prereg freeze before joint review |
| R7 independent final candidate QA | PM distinct reviewer; all agents supply re-runnable evidence | Agent cross-check != final independent QA |
| R8 owner GO/HOLD | Owner/PM, never A/B/C self-authorization | Default HOLD |

## 5. Required anti-drift protocol (ALL A/C/B handoffs inherit this)

1. **Contract ACK first.** Agent reads exact shared-contract Git blob, posts `ABC_CONTRACT_ACK_<A|C|B>` with contract SHA, own source SHA, and source ref readback in [PM Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32). If inaccessible, stale or disagreeing: `HOLD_CONTRACT_MISMATCH`.
2. **Work sequentially:** A delivers namespaced release/measurement *readiness design*; C reads exact A evidence and delivers *prospective scientific/data contract*, leaving B resource/weight assumptions `HOLD_B_VERIFICATION` until tested; B reads both exact A and C deliverables and returns feasibility / mapping, not an alternative C endpoint. Output must include a same-revision `JOINT_COMPATIBILITY_MATRIX` acknowledging other agents' exact refs.
3. **One owner per field.** No agent changes another's versioned schema, canonical JSON, tokenizer policy, gold/rubric, release authority or QA threshold. A disagreement is filed as one `CONTRACT_CHANGE_REQUEST` to Issue #32 with proposed version, exact byte/hash impact, negative QA, owner and dependent agents' ACK; no silent schema aliases, HEAD churn or micro-permits.
4. **Freeze gate before implementation.** In this operation only produce docs/readback/source-only QA plans. All new runtime implementation, science, native resource runs and signature minting remain `NOT_AUTHORIZED`. A/B/C written compatibility ACK does not equal PM independent gate. PM makes one final `PASS_TO_PROSPECTIVE_DESIGN_ONLY` or `HOLD_CONTRACT_ALIGNMENT` and maintains owner release HOLD.
5. **Evidence+history:** one exact commit/branch evidence packet per agent, immutable pointers, explicit QA author/source/runtime distinctions, open blockers, prior HOLD/FAIL preservation, no mutation of main or append-only `lineage.md`.
6. **No cross-track circular waiting:** C can define *requirements* for tokens/compute/checkpoint without falsely claiming B already verified them; B can return `BLOCKED_BY_SOURCE` if bytes/rights unavailable. A need not wait for science claims to design I2 authority barriers. PM reconciles one integrated packet.

## 6. Single PM adjudication outcomes

- `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` **only** if A/C/B artifacts use this same contract SHA, named owners ACK exact dependent inputs, R0–R8 status matrix has no unexplained conflicts, and no forbidden execution occurred.
- Otherwise `HOLD_ABC_CONTRACT_ALIGNMENT`, report one consolidated blocker matrix (not piecemeal permits).
- Independent technical gates already closed stay scoped PASS; no silent downgrades, no promotion to science GO.
- **Owner release for I2 / real SFT / GPU / TEST / merge remains HOLD** in either outcome until a separate explicit owner authorization.

**Only next operation after A/C/B inputs:** `TTM_PM_ABC_UNIFIED_EXACT_SOURCE_DEPENDENCY_AND_OWNER_READINESS_ADJUDICATION_SINGLE_GATE`. PM prepares a single owner packet, not multiple experimental approvals.
