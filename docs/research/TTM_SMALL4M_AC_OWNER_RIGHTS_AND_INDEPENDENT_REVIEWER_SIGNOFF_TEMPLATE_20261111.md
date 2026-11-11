# TTM Small4M A/C — Biên nhận owner và reviewer (chưa ký)

**Status:** `OWNER_ATTESTATION=NOT_RECEIVED` · `REVIEWER=UNASSIGNED`. Không có chữ ký hay ủy quyền nào được giả định từ việc lưu template này.

## A. Quyền dữ liệu — owner signoff (điều kiện trước science)

- Study: `TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1`.
- Private TRAIN/VAL pack SHA256: `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`.
- Parent checkpoint SHA256: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Source: `roneneldan/TinyStories`, revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`. License metadata `CDLA-Sharing-1.0`; official text `https://cdla.dev/sharing-1-0/`, rights to computational Use in §1.2, §1.13 and §2.1; Publication restrictions in §3.1–3.3; §3.5 describes Results. Review of license text is **not** legal advice or signed owner attestation.
- Intended use: exactly A/C equal-data-objective ablation, training internally only after separate science GO, no raw TRAIN/VAL/TEST, windows, checkpoint or original text republished; private outputs/escrow in owner-controlled locations, Github limited to public-safe receipts/digests. Any later release has separate rights review.
- Owner must confirm that the private pack indeed derives solely from the pinned licensed source, and that there are no additional restrictions from its preparation or storage.

**Fields requiring owner action (currently UNSET):** owner identifier, `RIGHTS_USE_APPROVED_FOR_AC_V1` true/false, acknowledgment of source/license and no raw redistributions, UTC datetime, SHA256 of final signed receipt. No project code treats this template as approval.

## B. Reviewer assignment (điều kiện trước scoring)

- Reviewer must be different from prompt author/trainer/code implementer and must never receive A/C mapping, AES key, training arm labels, checkpoints or pre-unblind scores.
- Reviewer receives neutral `R01..R24` packet with two text continuations per prompt; evaluates **each** text on three 0–3 axes (prompt adherence, coherence, consistency), integer scores. All 144 scores plus 24 notes, complete receipt and model/person identity must be frozen **before** unblinding.
- If an independent model rather than human is used: report provider/model and separation conditions, verdict at most `EXPLORATORY_SCOPED_AI_REVIEW`. Do not claim independent human or organizational science.
- Reviewer identity and acknowledgment of independence must be recorded **before science execution**, not after viewing content.
- There is **no reviewer yet assigned**. Do not recycle Codex FRESH12's earlier receipt as if it accepted this study.

**Fields requiring assigned reviewer action (currently UNSET):** reviewer identity, role/human-or-AI, source-access constraints, acceptance timestamp, signed or otherwise verifiable attestation SHA, score submission channel, freeze-before-unblind acknowledgment.

## C. Cryptographic blind escrow

- Source final prompts: `docs/research/TTM_SMALL4M_2X2_NEW_DEV12_BLIND_FINAL24_PROMPTS_FROZEN_20261110.json`, Git blob `f08f15c5049baf77771bed463a5119136566373b`.
- 24 neutral pair IDs, HMAC-SHA256 randomized/position-balanced 12 A-left/12 C-left, `AES-256-GCM` encrypted public JSON.
- Public encrypted escrow: `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_SMALL4M_AC_BLIND24_ENCRYPTED_ESCROW_PUBLIC_20261111.json`, SHA256 `519f3185d6202052ce1e5c98a7e7fa58a813d87ce9d9e2d173eb25f6a05f9f1c`.
- Original decrypted mapping SHA256 `68d4e303efd2c5809bf0e89f5564f70e1114349b463b5458174c1407e8deda1d`.
- Decryption key is **separate owner-only artifact**, not in repo. Owner must save it under project `_tmp` with restricted ACL and confirm receipt; no GH or reviewer distribution before score freeze.
- The GitHub file SHA256 has been independently recomputed from readback and matched exactly.
- **Custody status:** `ENCRYPTED_ESCROW=SEALED_PASS`, `PRIVATE_KEY_OWNER_WORKSPACE_CUSTODY=NOT_VERIFIED`, `REVIEWER_NO_KEY=PASS_BY_DESIGN`.

## D. Final guardrails

- No one-shot science authorization in this template.
- To issue exactly one science GO, need owner-signed rights receipt, reviewer attestation, private-key custody, exact Windows source QA, T4 FP16 zero-step smoke and actual P02 uninterrupted/resumed parity, locked source+evaluation+reviewer SHA, independently checked new owner lock.
- Stop on any missing or mismatched receipt. Never silently train, re-run TEST, Q1/Q2, OOD or prior one-shots.
