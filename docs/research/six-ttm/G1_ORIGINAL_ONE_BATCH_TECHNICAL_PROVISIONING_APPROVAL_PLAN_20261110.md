# TTM × SIX G1 — Kế hoạch technical provisioning MỘT LÔ, trình owner phê duyệt

**Plan ID:** `TTM_SIX_G1_ORIGINAL_TECHNICAL_PROVISIONING_BATCH_V1_20261110`  
**Ngày:** 2026-11-10 (Asia/Bangkok)  
**Phạm vi owner đã CHỌN:** `ORIGINAL_G1_CONFIRMATORY_UNCHANGED`. **Technical approval:** `PENDING_EXPLICIT_OWNER_APPROVAL`.  
**Mục đích:** một reference instance bảo vệ khoa học G1 gốc, không phải hạ tầng production đa dự án.  
**Không cấp phép:** chạy science, đọc G1 TEST thật, truyền TinyStories/teacher vectors lên Colab, thay khóa PR #12, sửa `main`, `lineage.md`, TTM-Small-4M checkpoint, hoặc chạy lại Qwen technical smoke đã tiêu thụ.  
**Trạng thái bất biến:** `G1_SCIENCE_LOCK=HOLD` · `G1_PRIVATE_TEST_OPENED=NO` · `SCIENCE_EXECUTED=NO` · `OWNER_SCIENCE_PERMIT=NOT_ISSUED`.

## 0. Pin nguồn và hợp đồng gốc (không sửa trong lô này)

| Vật liệu | Pin/cam kết |
|---|---|
| Git origin | `https://github.com/minhtri22/TokenToModel-Lab.git` |
| Research G1 v1c | `d5d0c5346a595557a76349f900d09be50bce289c` |
| Implementation v1e source được reviewer kiểm tra | `1efca4ca080572dcd22bbe658701b221ca46f7dd`; mã lỗi sẽ **chỉ** có phiên bản mới trên nhánh implementation riêng |
| Codex review v1e | `review/ttm-six-g1-v1e-codex-distinct-owner-import-20261110@365c352daee276ed5f8c12046ffc17444e0a7b35`; verdict `HOLD` |
| Original T1 split manifest | SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9` |
| Sealed private G1 split manifest | SHA256 `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6` |
| Data/split | G1 uses only original TTM pilot TRAIN as candidate source; G1 `128 TRAIN / 64 DEV / 64 TEST`. Do not touch TTM original VAL/TEST |
| Models | Qwen3-0.6B `c1899de289a04d12100db370d81485cdf75e47ca`; Qwen3-1.7B `70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`; exact weights/tokenizer/config checks retained |
| Methods | 8 fixed probes, `hidden_states[28]`, ridge `[1,10,100]`, 1.000 TRAIN-pair shuffles, 1.000 CKA permutations, 2.000 bootstrap, B-direct/oracle/mean/CKA; **v1e methods candidate is NOT approved** |
| One-shot budget | Target Colab Free Tesla T4 only if actually available, source ≤3.600 s, target ≤3.600 s, all phases ≤7.200 s, peak GPU ≤12 GiB |
| Existing QA | v1c corrections and scoped Windows 45/45, v1e author CPU 61/61, v1e Win32 fault paths 2/2 OWNER PASS, Codex new CPU 13/13. Preserve without replay |

**Reviewer findings to fix in batch:** (a) `verify_owner_admission` checks only *syntax* of launcher commit / methods SHA; it must compare against independently trusted expected values and disallow signed bogus pins; (b) row-wise CKA permutations can be severely anti-conservative for grouped data; real T1 grouping/exchangeability must be evaluated **before TEST**, not assumed from synthetic 8×8 counterexample; (c) same nonce cached ACK can be replayed without an external single-use latest-tip service.

## 1. Threat model đúng phạm vi G1

**Untrusted/low-trust:** QA notebook, GPU worker process, worker scratch, user-controlled input/status flags, staged archives, symlinks/hardlinks/junctions, cached ACKs and a controller that may crash/roll back. **Trusted by contract:** owner/admin signer, exact verified launcher, broker+writer under different OS authorization than worker, and a truly external witness outside both controller's and worker's rollback/admin domain.

Owner/OS administrator compromise, Google cloud operator compromise and physical host compromise are **outside this single-run threat model**, and must be disclosed as limitations. A Windows DACL by itself does not protect against local Administrator; distinct keys on one shared writable account are not independent.

An authorized TEST feature process necessarily receives TEST data *after* release; “one-shot” means one authorized extraction/consumption event and no permitted second execution or release. It does **not** mathematically prevent a malicious process that already received bytes from retaining them. If the intended stronger requirement is uncopyable TEST bytes against a malicious post-release worker, standard Colab notebooks do not provide proof of that guarantee: report `HOLD` and amend trusted-compute scope before science.

## 2. Chính xác thay đổi được đề xuất trong một batch

**Scope filesystem:** only `D:\WORK\RESEARCH\TokenToModel-Lab\_trusted\g1\batch_v1` and `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_PROVISION_BATCH_V1_*` on Windows; versioned code/docs on a new `implementation/ttm-six-g1-original-single-batch-v1-20261110` Git branch. Never overwrite `_tmp\ttm_six_g1_private_manifest_v1`, existing private TEST, original source, other projects or non-G1 worktrees.

**Global Windows exception that REQUIRES this plan's owner approval:** creating precisely four NEW non-admin local service identities and setting their local logon restrictions changes system account configuration; no other OS accounts, groups, services or root ACLs may be modified. If account names already exist, or OS policy/edition disallows isolation, **STOP before any write**. Do not create privileged services to evade this restriction.

| Proposed principal name (never invent SID) | Role | Rights only after authoritative OS SID resolution |
|---|---|---|
| `TTM_G1_Controller` | Verified launcher, state machine, accepted owner permit verification | Full only its controller state; no raw sealed TEST, no signer private keys, no witness state write |
| `TTM_G1_Broker` | TEST vault and controlled release | Read/modify synthetic sealed TEST root only during QA; READ true G1 TEST requires **separate later science permit** |
| `TTM_G1_Writer` | Content-addressed staging, verified pack commit & immutable receipt interface | Modify only its staging/commit/receipt storage, not controller/witness/TEST |
| `TTM_G1_Worker` | TRAIN/DEV synthetic work, limited outputs | Read synthetic TRAIN/DEV, modify own scratch; denied vault, receipts, controller and witnessed state |

**Permissions on newly created roots (do not apply to existing project parents):**
- `batch_v1\controller`: SYSTEM + owner-admin = Full; controller = Modify; others none.
- `batch_v1\broker\sealed_test_synthetic`: SYSTEM + owner-admin = Full; broker = Modify; controller/writer/worker none; inheritance **disabled** with explicit protected DACL.
- `batch_v1\writer\{staging,committed,receipts}`: SYSTEM + owner-admin = Full; writer = Modify; others none. Worker sends untrusted bytes via audited IPC; worker never writes a trusted receipt.
- `batch_v1\worker\train_dev_synthetic`: worker = Read/Execute; broker may publish; no TEST content. `batch_v1\worker\scratch`: worker = Modify; no trusted data/state placed there.
- `batch_v1\controller\state`: trusted controller only for mutable state; witness state **must be offhost**.
- Newly created `batch_v1\evidence`: owner/QA reviewer controlled sanitized metadata/hashes; no raw SID/DACL published.
- Explicit principal resolution saved in a **private** manifest (`account_name→SID`, protected DACL); deny should be shown by actual `LogonUser`/restricted-token read attempts, not simply a string comparison. Owner/admin rights remain and are noted as a limitation.
- `icacls` pre/post exports, `Get-Acl`, file IDs, inheritance and reparse-point inventory before/after; file-level ACL protects hardlinks sharing a file object. Reject path redirects; test via alternate names and process token. All ACL tests use *new fake TEST files*, never actual G1 TEST.

**Key and external witness boundaries:**
- Three trust anchors: owner, pack writer, witness. Private keys never in Git, `_tmp`, worker filesystem, environment dumps or log; externally pinned public key hashes. Prefer separate domains of operation; key distinction alone is not OS/administrative separation.
- Owner signature verified over exact immutable payload: `run_id`, phase, code/launcher `Git commit and executable blob`, methods-amendment SHA256, model/tokenizer/weights, T1/G1 manifests, permitted source rights, destination, TTL and one-shot budget; compare *every expected pin* against a launcher-controlled read-only trust manifest **not supplied by caller**. Reject unknown/synthetic keys in release path.
- External witness is **not** a new directory on D:, the Git repo under the same owner credentials, nor Google Drive shared with worker. Must be an authenticated **offhost endpoint under separate administrative/rollback control** offering `latest(run_id, fresh_challenge)`, atomic `append(run_id, seq, prev_hash, event_hash, nonce)`, signing/ack, and one-use nonce/consume; controller/worker only append/query, **never** reset/delete or change witness signing key. A fresh challenged latest-tip is required before release and again before TEST consume; verify replay after rollback of controller+worker.
- **No endpoint / independent admin / zero-cost resource available today is assumed.** Preflight resolves exact URL, provider, account owner, scopes, secret custody, immutable retention and evidence of non-rollback from controller/worker. If any missing or not approved, `STOP_NO_MUTATION`. Do not enroll in a paid service or create cloud accounts under this plan without an explicit owner amendment.

**Colab execution boundary:**
- Colab Free only by normal interactive notebook workflow; no SSH/remote-controlled daemon, no unlimited/scheduled service assumption.
- No `drive.mount` containing G1 TEST or private story files in worker-accessible Drive. A Colab runtime allowed to mount a Drive can access files in that Drive; separate file names alone do not isolate secrets.
- TEST release protocol must actually cross a broker-controlled authorization point **after** independent witness `FIT_FROZEN` ack; worker cannot prefetch TEST via local cache, Drive, signed URLs, environment variables, tokenized input, model artifacts or aliases. Validate end-to-end with synthetic TEST under precisely the runtime topology intended for G1.
- Because a free Colab runtime is ephemeral and GPU access is not guaranteed, there is no claim an external watchdog can forcibly terminate the managed VM/process or preserve state across VM deletion until **actual target QA** demonstrates the specified containment. A Linux supervisor/cgroup/process-group check is required on the target; Windows Job Object QA is only support.
- Without a Colab-valid isolation/witness/supervisor design, **DO NOT stage actual data or mark any production gate PASS**. One STOP decision instead of indefinite workarounds.

## 3. One-batch implementation & QA order — no micro-permits

**Phase A — READONLY readiness preflight, zero mutation.** Verify immutable Git source & current repo clean enough for separate branch, target host Python/Windows/NTFS and ability to create four *new* principals, workspace paths not reparse points, *external* witness endpoint domain/identity and zero-cost eligibility, Colab target topology and ability to keep TEST absent until freeze. Check owner data rights: current approval is T1 TRAIN metadata/hash seal/QA **only**. Need a separately scoped future authority to inspect raw T1 TRAIN for near-duplicate lineage or stage source/derived features. If any critical preflight prerequisite is missing, output ONE `FEASIBILITY_HOLD` and do **not** provision any identity, ACL or external resource.

**Phase B — one controlled implementation transaction (only after owner technical approval and Phase A PASS).** Create four designated identities and the new `batch_v1` subtree; record owner-approved private SID mapping and DACL delta; make exact expected-pin external trust manifest; create isolated owner/writer/witness keys and one-use latest-tip interface; implement TEST broker, writer/ledger, trusted launcher and target-appropriate OS supervisor; update new methods amendment draft with precommitted lineage grouping/null assumptions and prospective power. Do not edit frozen v1c/methods/TEST/PR/main. Keep precise source hashes after each code change in *one* manifest. All pre-science data remains synthetic unless separately authorized.

**Phase C — ONE integrated negative QA run, never opening G1 real TEST.** Apply tests below to fake TEST, actual distinct Windows tokens, permitted offhost witness and permitted Colab-free synthetic process. Reviewer may inspect prior receipts without rerunning unchanged `29/45/61/2` or consumed Qwen tests.

| Gate | Minimum PASS evidence; mark NOT_TESTED otherwise |
|---|---|
| 1. Authority | An otherwise-valid signed permit with bogus launcher/method SHA **fails**; wrong expected manifest or key swap fails; expired/foreign `run_id` fails; no worker self-granted science |
| 2. Split broker | Real worker SID gets `AccessDenied` on fake TEST pre-freeze via normal path, hardlink/junction/symlink/reparse, Drive/cache/API; no TEST plaintext available before verified freeze+witness ACK; rightful broker access documented |
| 3. Writer/ledger | Writer service separate from worker; byte-identical parse/hash/receipt; orphan/partial pack and concurrent runs fail closed; before/after durable commit crash injection; forged worker receipt rejected |
| 4. Witness | Independent latest-tip and single-use challenge/nonce; replay cached signed ACK denied; controller+worker local rollback then relaunch rejected; witness outage prevents TEST release; trust domain/credentials documented without secrets |
| 5. Watchdog | Owned process tree truly killed on timeout/crash and no orphan observed; simulate 3.600/3.600/7.200 cumulative clock across phases; synthetic T4 GPU workload checks real process-group kill and resource telemetry/limit enforcement; peak ≤12 GiB contract. No full 2-hour science test needed |
| 6. Methods | Exact first-occurrence lineage/group mapping, precommitted near-dup rule and split-group audit (requires *authorized* T1 TRAIN audit, not TEST); grouped/permutation/bootstrap exchangeability and false-positive simulation; CKA tolerance/degeneracy; prospective TEST=64 power and INCONCLUSIVE table. Distinct methods reviewer approves final amendment version and hash |

**Synthetic GPU resource bound (proposed):** a *single* owner-approved target technical QA session if free Tesla T4 actually available, ≤120 s intentional GPU work, GPU utilization/memory bounded far below 12 GiB, no Qwen weights, no TinyStories/TEST/derived teacher data. Simulated clock/rate budget enforcement is separately tested without waiting 7.200 s. If target T4 unavailable or process group cannot be killed independently, `NOT_TESTED` and STOP. This cap is for *technical QA only*, not science.

**Phase D — one independent adjudication:** one redacted `.md` + machine-readable `.json`, both exact source SHA256 and SHA256 of evidence, one six-row PASS/FAIL/NOT_TESTED matrix and one verdict `PASS_DISTINCT_REVIEWER/HOLD/FAIL`. Reviewer is not source author; signoff never grants scientific permit.

**Phase E — one separate owner science decision (NOT INCLUDED in this batch):** if and only if all mandatory gate objectives PASS and data/licensing/staging/retention conditions are explicitly accepted, owner may issue a new `run_id` one-shot science admission. Reviewer PASS alone cannot open TEST. If Phase A or Phase D says HOLD/FAIL, freeze scope, keep negative evidence, present **one** finite blocker/cost decision, not six further micro-permits.

## 4. Change inventory, rollback, privacy and budget envelope

| Category | Allowed by a later exact owner approval | Explicitly forbidden |
|---|---|---|
| Git | New implementation/reviewer branches and sanitized `docs/research/six-ttm` evidence. No merge in this batch | `main`, frozen v1c, PR #12, `lineage.md`, checkpoint/source history rewriting |
| Files | Create only two new project-root-bounded families `_trusted\g1\batch_v1`, `_tmp\G1_PROVISION_BATCH_V1_*` | Existing sealed TEST or T1 private source; Windows roots outside project; Docker/WSL disks |
| Windows OS | Create the four named **new non-admin accounts only**, change ACL **only on new batch_v1 files**; private key locations per approved trust design | Touch existing accounts/groups/admins, security policy outside these identities, Windows services/startup/task scheduler, firewall, network/system-wide ACL |
| Remote/offhost | Dedicated independently administered witness endpoint **only if already available and owned**, scopes and credentials owner-verified | New paid services/accounts, reusing worker/controller admin credentials, exposing private keys or TEST data |
| Colab | One bounded synthetic-only QA under interactive free tier, if available/allowed | Qwen model reload, actual teacher extraction, original G1 TEST, science work, repeated technical smoke, remote daemon |
| Evidence | Private raw receipts in project `_tmp`; Git only sanitized SHA+summary; record before/after account SID and ACL delta locally | Raw SID/account identifiers, signing private keys, TEST IDs/text, teacher vectors or sensitive telemetry on Git |

**Pre-mutation rollback plan:** produce no-op `WHAT_WILL_CHANGE` manifest enumerating each OS account, SID (when provisioned), new path, inherited/protected ACL rule, key location, witness endpoint, planned process/service, and cleanup command. Compare to this plan byte-for-byte; unexpected existing name, path/privilege, provider/cost, or new system service `STOP_NO_MUTATION`.

**Post-mutation failure:** immediately stop test processes/release, revoke temporary credentials and disable only **batch-created** principals after verifying identity; retain receipts and ACL snapshots; do not delete unrelated files, existing accounts, TEST or evidence. Any destructive cleanup of new batch objects must verify exact ownership/path and be logged; no automatic removal of pre-existing security principals.

**Free resource envelope:** no monetary spend without new owner approval; no full-scale Qwen one-shot in QA; no repeated old negative suites; at most one synthetic target GPU session ≤120 s once Colab is proven eligible; one independent integrated review. No promise of guaranteed T4 availability or runtime survival.

## 5. Approval semantics — exactly one authorization, not blanket execution

**Owner already selected:** `G1_ORIGINAL_CONFIRMATORY_UNCHANGED`.

**Owner technical authorization proposed, NOT YET GIVEN:**  
`APPROVE_TTM_SIX_G1_ORIGINAL_TECHNICAL_PROVISIONING_BATCH_V1_20261110`

If owner gives this exact instruction, it authorizes **only** read-only Phase A and, **only when every Phase A condition is verified**, the bounded Phase B/C/D technical changes with synthetic TEST and batch-created identities as defined here. Approval does **not** supply missing external endpoint, credentials, data rights, a stable Colab GPU, nor any authority to broaden identity/ACL/service scope. Unresolved prerequisite → `STOP_NO_MUTATION` with one report. Do not assume approval from choosing original G1 in conversation.

Separate later `G1_OWNER_SCIENCE_PERMIT` must explicitly bind exact validated code, amendment, model+tokenizer+data hashes, source rights, storage destinations/retention, run ID, safe supervisor and TEST release. Before that: `SCIENCE_EXECUTED=NO`, `G1_PRIVATE_TEST_OPENED=NO`, `G1_SCIENCE_LOCK=HOLD`.

## 6. Exit and next step

**This document's exit:** `ORIGINAL_SCOPE_SELECTED` · `PROVISIONING_PLAN_FROZEN_FOR_REVIEW` · `OWNER_TECHNICAL_APPROVAL=PENDING` · `TEST_PROTECTION=UNCHANGED` · `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** `TTM_SIX_G1_ORIGINAL_SINGLE_BATCH_OWNER_TECHNICAL_APPROVAL`. Owner approves the *one* bounded plan or requests a precise amendment; only afterwards preflight read-only and batch provisioning may begin. Final distinct QA must decide `PASS/HOLD/FAIL` for all six gates before a new, separate science permit.
