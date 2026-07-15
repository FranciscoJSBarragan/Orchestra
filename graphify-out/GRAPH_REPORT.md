# Graph Report - .  (2026-07-14)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 362 nodes · 759 edges · 38 communities (12 shown, 26 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.68)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b8c7fa5b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- sync.py
- ValidateSuiteTests
- SyncTests
- PullRequestFlowTests
- validate_suite.py
- integrate_local
- pr.py
- CommitPhaseTests
- PlannedFlowContractTests
- LocalIntegrationTests
- Root Orchestrator
- commit_phase.py
- DeliveryPolicyTests
- LightFlowContractTests
- Architecture Guidance Reference
- pre-commit
- Analyst Profile
- Implementation Worker Profile
- Reviewer Profile
- Verifier Profile
- Orchestra Routing Instructions
- Namespace
- Path
- Orchestra Change Routing Skill
- Orchestra Delivery Policy Skill
- Orchestra Local Integrate Skill
- Orchestra Phase Commit Skill
- Orchestra PR Merge Skill
- Orchestra PR Open Skill
- Orchestra PR Review Skill
- Browser Acceptance Playbook
- Difficult Debugging Playbook
- Frontend Implementation Playbook
- Runtime Verification Playbook
- Web Research Playbook
- CompletedProcess
- Orchestra Roadmap
- Local Task Plan

## God Nodes (most connected - your core abstractions)
1. `ValidateSuiteTests` - 34 edges
2. `PullRequestFlowTests` - 30 edges
3. `SyncTests` - 30 edges
4. `uninstall()` - 20 edges
5. `SyncError` - 18 edges
6. `PlannedFlowContractTests` - 18 edges
7. `CommitPhaseTests` - 16 edges
8. `integrate_local()` - 15 edges
9. `_analyze()` - 15 edges
10. `_apply_operation()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `integrate_local()` --calls--> `blocked()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py
- `merge_pr()` --calls--> `load_policy()`  [INFERRED]
  codex/scripts/pr.py → codex/scripts/policy.py
- `open_pr()` --calls--> `load_policy()`  [INFERRED]
  codex/scripts/pr.py → codex/scripts/policy.py
- `merge_pr()` --calls--> `run_checks()`  [INFERRED]
  codex/scripts/pr.py → codex/scripts/policy.py
- `Orchestra Agent Rules` --references--> `Orchestra Architecture`  [EXTRACTED]
  AGENTS.md → docs/ARCHITECTURE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Base Agent Profiles** — analyst, implementation_worker, reviewer, verifier [EXTRACTED 1.00]
- **Canonical Product Sources** — vision_md, docs_workflow_md, docs_architecture_md, agents_md [EXTRACTED 1.00]
- **Tracked Graphify Artifacts** — graphify_out_graph_json, graphify_out_graph_html, graphify_out_graph_report_md [INFERRED 0.90]

## Communities (38 total, 26 thin omitted)

### Community 0 - "sync.py"
Cohesion: 0.19
Nodes (39): ArgumentParser, _allowed_entry(), _analyze(), _apply_operation(), _atomic_write(), _backup_path(), _block_span(), _check_before() (+31 more)

### Community 1 - "ValidateSuiteTests"
Cohesion: 0.10
Nodes (3): Behavioral tests for the Orchestra conformance engine., ValidateSuiteTests, CompletedProcess

### Community 2 - "SyncTests"
Cohesion: 0.12
Nodes (4): Path, Isolated tests for direct Orchestra synchronization., Model a pre-composition install without depending on retired sources., SyncTests

### Community 3 - "PullRequestFlowTests"
Cohesion: 0.18
Nodes (3): PullRequestFlowTests, CompletedProcess, Deterministic fake-gh tests for Orchestra PR open, observe, and merge.

### Community 4 - "validate_suite.py"
Cohesion: 0.10
Nodes (27): check_delivery_config(), check_direct_sync(), check_distribution_boundary(), check_documentation(), check_hook(), check_python_syntax(), check_python_tests(), check_required_paths() (+19 more)

### Community 5 - "integrate_local"
Cohesion: 0.14
Nodes (27): _branch(), _clean(), _command_reason(), _common_git_dir(), _git(), _head(), integrate_local(), main() (+19 more)

### Community 6 - "pr.py"
Cohesion: 0.23
Nodes (26): blocked(), _check_state(), _command_error(), _gh(), _git(), _json_output(), main(), merge_pr() (+18 more)

### Community 7 - "CommitPhaseTests"
Cohesion: 0.30
Nodes (3): CommitPhaseTests, CompletedProcess, Behavioral tests for the thin phase commit helper.

### Community 9 - "LocalIntegrationTests"
Cohesion: 0.30
Nodes (4): LocalIntegrationTests, CompletedProcess, Path, Temporary-repository tests for conservative local integration and cleanup.

### Community 10 - "Root Orchestrator"
Cohesion: 0.19
Nodes (14): Orchestra Agent Rules, Analyst Profile, Repository Context Playbook, Orchestra Skill, Orchestra Architecture, Orchestra Workflow, Graphify Lifecycle, Implementation Worker Profile (+6 more)

### Community 11 - "commit_phase.py"
Cohesion: 0.31
Nodes (13): _blocked(), commit_phase(), _git(), _head_sha(), main(), parse_args(), CompletedProcess, Namespace (+5 more)

### Community 12 - "DeliveryPolicyTests"
Cohesion: 0.29
Nodes (3): DeliveryPolicyTests, CompletedProcess, Tests for explicit delivery policy and ordered argv checks.

## Knowledge Gaps
- **26 isolated node(s):** `Analyst Profile`, `Implementation Worker Profile`, `Reviewer Profile`, `Verifier Profile`, `Local Task Plan` (+21 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ValidateSuiteTests` connect `ValidateSuiteTests` to `validate_suite.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Why does `PlannedFlowContractTests` connect `PlannedFlowContractTests` to `validate_suite.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `_relative()` connect `sync.py` to `commit_phase.py`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **What connects `Analyst Profile`, `Implementation Worker Profile`, `Reviewer Profile` to the rest of the system?**
  _26 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `ValidateSuiteTests` be split into smaller, more focused modules?**
  _Cohesion score 0.10317460317460317 - nodes in this community are weakly interconnected._
- **Should `SyncTests` be split into smaller, more focused modules?**
  _Cohesion score 0.12477718360071301 - nodes in this community are weakly interconnected._
- **Should `validate_suite.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09885057471264368 - nodes in this community are weakly interconnected._