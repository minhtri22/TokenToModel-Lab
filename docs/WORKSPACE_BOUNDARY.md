# TTM — workspace boundary and destructive-operation governance

- **Canonical GitHub:** `https://github.com/minhtri22/TokenToModel-Lab.git`
- **Exact approved Windows project root:** `D:\WORK\RESEARCH\TokenToModel-Lab`
- The Git main working tree is the root itself. P00 local development worktree resides only within `worktrees/` under the root, except RemoteMCP managed tasks, which use **only** their `project_status.worktrees_root_rel` location within the same root.
- Refuse any repository with a different `origin` or a root that is a Windows junction, symlink or reparse point.
- Never create or delete a worktree outside the approved root. Refuse paths that canonicalize outside the root, including through reparse points.
- No cleanup is permitted without a separate exact-path proposal and explicit user approval. Do not use `git clean -fdx`, `git reset --hard`, `git worktree prune`, `git worktree remove --force`, recursive removal, `Remove-Item -Recurse`, or path globs.
- All run outputs, temp, training data, model checkpoints, caches and logs must be directed under root. Git credentials and existing user-wide environment must not be altered.
- P00 source is correctness-only. The paged KV implementation gathers K/V into contiguous tensors for attention and is **not** a true direct-paged GPU kernel.
- `lineage.md` append only; log positive, negative and inconclusive evidence. No fabricated local QA results.
