# Legacy Preservation and Clean Rebuild Migration

## Goal

Preserve the current multi-platform repository as `Orchestra-legacy`, create a
fresh Codex-only `Orchestra`, and begin the new implementation from the
canonical bootstrap documents without importing legacy control-plane design by
accident.

## Migration status

Completed on 2026-07-13 through creation of the clean repository:

- legacy `main` closed at `3c250ad` with tag `orchestra-legacy-final`;
- unfinished work preserved at
  `archive/task-worktree-hybrid-delivery-wip-20260713` (`d908b10`);
- complete bundle verified at
  `/Users/fjsbarragan/Code/Orchestra-legacy.bundle`;
- installed legacy resources quarantined at
  `/Users/fjsbarragan/Code/Orchestra-legacy-runtime-backup`;
- linked worktrees removed cleanly;
- legacy repository renamed to `/Users/fjsbarragan/Code/Orchestra-legacy`;
- fresh Codex-only repository initialized at
  `/Users/fjsbarragan/Code/Orchestra`.

Runtime implementation and installation have not started.

## Historical pre-migration state

At the documentation snapshot before migration:

- the main repository is `/Users/fjsbarragan/Code/Orchestra`;
- `main` is clean at `d3705ab`;
- no Git remote is configured;
- two linked detached worktrees exist;
- `task-worktree-hybrid-delivery` contains tracked and untracked work;
- the linked worktrees contain absolute `.git` references to the current
  `Orchestra` path.

Renaming the repository before preserving and repairing those worktrees can
break their Git linkage and risk uncommitted work.

## Target layout

```text
/Users/fjsbarragan/Code/
├── Orchestra-legacy/   # complete historical multi-platform repository
└── Orchestra/          # new Git history, Codex only
```

## Migration sequence

### 1. Approve the bootstrap documentation

Review this package with the user. Correct any misunderstanding before Git or
runtime changes. The package becomes the handoff source for the new task.

### 2. Preserve linked worktrees

Inspect both linked worktrees again immediately before migration.

- Give the dirty detached worktree a named archival branch.
- Preserve its changes in a clearly marked legacy WIP commit, or use another
  user-approved lossless snapshot if the diff is not commit-ready.
- Confirm the second worktree is clean before removal.
- Do not delete a dirty or unmerged worktree.

### 3. Close and back up the legacy repository

- Add the approved bootstrap package as the final legacy documentation change.
- Create a final legacy commit and an annotated `orchestra-legacy-final` tag.
- Create a Git bundle containing all refs because there is no remote backup.
- Verify the bundle before continuing.
- Remove clean linked worktrees and repair remaining metadata as needed.

These are separately authorized Git/filesystem actions; documentation approval
alone does not execute them.

### 4. Quarantine installed legacy runtime resources

Inventory resources actually managed by the legacy Codex sync before moving
anything. Quarantine, rather than destroy, the installed legacy copies of:

- `orchestra` and `orchestra-*` skills;
- legacy-managed agent profiles;
- the legacy-managed block in the global Codex `AGENTS.md`;
- any legacy plugin registration or install manifest.

Do not quarantine unrelated personal skills or agents. Keep the proven
standalone references available:

- `commitbot`
- `openprbot`
- `prbot`
- `prmerge`

The source for all quarantined resources remains in `Orchestra-legacy`.

Codex may cache its available skill inventory for the current task. After
quarantine, start a new task—and restart/reload Codex if needed—before planning
the new repository.

### 5. Rename legacy and create the clean repository

- Rename the preserved repository directory to `Orchestra-legacy`.
- Initialize a new `/Users/fjsbarragan/Code/Orchestra` Git repository.
- Copy the bootstrap package into its canonical root paths.
- Make the documentation foundation the new repository's first commit.
- Do not copy `.orchestra/runs`, Graphify output, legacy plans, Hermes, or Devin.

### 6. Inventory legacy candidates

The new task inspects candidates read-only and assigns one disposition before
copying code:

| Disposition | Meaning |
| --- | --- |
| `reuse` | Small deterministic asset is already aligned and can be copied with tests. |
| `adapt` | Preserve behavior while rewriting or reducing implementation. |
| `reference` | Use only to understand requirements or failure history. |
| `reject` | Explicitly exclude from the new architecture. |

Initial expected dispositions:

| Legacy asset or behavior | Expected disposition |
| --- | --- |
| Structured commit intent from `commitbot` | `adapt` |
| `openprbot` branch-range collection and `PR-CONTEXT` | `adapt` |
| `prbot` poller, triage, impacted verification, and clean cycles | `adapt` |
| `prmerge` verification and cleanup behavior | `adapt` |
| Specialized agent prompts and compact task packets | `reference` / selective `adapt` |
| Single-suite validator and safe sync concepts | `reference` / selective `adapt` |
| Authority bundles and per-action approval chains | `reject` |
| Commit recovery journal and Git-index replacement | `reject` |
| Global workflow event/state engine | `reject` |
| Repeated authority subprocess validation | `reject` |
| Hermes and Devin implementations | `reference later`, not part of rebuild |

No file is copied merely because it already exists.

### 7. Plan in a fresh task

The new task receives:

- the new repository path;
- `VISION.md`, `AGENTS.md`, `docs/WORKFLOW.md`, and
  `docs/ARCHITECTURE.md`;
- this migration record;
- the legacy path as read-only reference;
- an instruction to produce a minimal formal implementation plan.

Suggested handoff:

```text
Build the Codex-only Orchestra described by the canonical documents in this
repository. Treat /Users/fjsbarragan/Code/Orchestra-legacy as read-only
historical evidence. Do not copy a legacy asset until it is classified as
reuse, adapt, reference, or reject. Optimize for reliable quality per token,
specialized subagents, a thinking orchestrator, lean Git mechanics, and the
documented hybrid delivery flow. First inspect the new repository and propose
the smallest coherent implementation plan; do not install or mutate production.
```

## Rollback

Until the user accepts the new repository, rollback is simple:

- stop work in the new repository;
- keep or remove it only with explicit user approval;
- restore quarantined runtime resources from their backup if needed;
- continue reading the untouched legacy repository and verified Git bundle.

The migration does not delete legacy history or make the new runtime active.
