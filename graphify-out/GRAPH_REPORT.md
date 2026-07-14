# Graph Report - implement-orchestra  (2026-07-14)

## Corpus Check
- 29 files · ~22,296 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 399 nodes · 794 edges · 22 communities (18 shown, 4 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 27 edges (avg confidence: 0.67)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef9e7744`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- sync.py
- pr.py
- PullRequestFlowTests
- validate_suite.py
- ValidateSuiteTests
- Route an Orchestra change
- SyncTests
- CommitPhaseTests
- PlannedFlowContractTests
- Orchestra Architecture
- integrate_local
- LocalIntegrationTests
- Product principles
- Orchestra Workflow
- commit_phase
- DeliveryPolicyTests
- Orchestra Agent Rules
- LightFlowContractTests
- Orchestra
- Orchestra Roadmap
- AGENTS.orchestra.md
- pre-commit

## God Nodes (most connected - your core abstractions)
1. `PullRequestFlowTests` - 30 edges
2. `SyncTests` - 27 edges
3. `ValidateSuiteTests` - 25 edges
4. `uninstall()` - 20 edges
5. `SyncError` - 18 edges
6. `PlannedFlowContractTests` - 17 edges
7. `CommitPhaseTests` - 16 edges
8. `integrate_local()` - 15 edges
9. `_analyze()` - 15 edges
10. `_apply_operation()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `integrate_local()` --calls--> `blocked()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py
- `integrate_local()` --calls--> `load_policy()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py
- `integrate_local()` --calls--> `run_checks()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py
- `_command_error()` --calls--> `blocked()`  [INFERRED]
  codex/scripts/pr.py → codex/scripts/policy.py
- `_json_output()` --calls--> `blocked()`  [INFERRED]
  codex/scripts/pr.py → codex/scripts/policy.py

## Import Cycles
- None detected.

## Communities (22 total, 4 thin omitted)

### Community 0 - "sync.py"
Cohesion: 0.19
Nodes (39): ArgumentParser, _allowed_entry(), _analyze(), _apply_operation(), _atomic_write(), _backup_path(), _block_span(), _check_before() (+31 more)

### Community 1 - "pr.py"
Cohesion: 0.17
Nodes (33): blocked(), load_policy(), main(), parse_args(), Any, Namespace, Path, Return validated policy data and a compact result. (+25 more)

### Community 2 - "PullRequestFlowTests"
Cohesion: 0.18
Nodes (3): PullRequestFlowTests, CompletedProcess, Deterministic fake-gh tests for Orchestra PR open, observe, and merge.

### Community 3 - "validate_suite.py"
Cohesion: 0.11
Nodes (27): check_delivery_config(), check_direct_sync(), check_distribution_boundary(), check_documentation(), check_hook(), check_python_syntax(), check_python_tests(), check_required_paths() (+19 more)

### Community 4 - "ValidateSuiteTests"
Cohesion: 0.13
Nodes (3): CompletedProcess, Behavioral tests for the Orchestra conformance engine., ValidateSuiteTests

### Community 5 - "Route an Orchestra change"
Cohesion: 0.08
Nodes (19): Choose an authorized delivery path, Resolve policy and authority, Execute the local contract, Integrate one task locally, Commit an accepted phase, Execute the thin path, Execute the merge contract, Merge one clean PR (+11 more)

### Community 6 - "SyncTests"
Cohesion: 0.14
Nodes (3): Path, Isolated tests for direct Orchestra synchronization., SyncTests

### Community 7 - "CommitPhaseTests"
Cohesion: 0.30
Nodes (3): CommitPhaseTests, CompletedProcess, Behavioral tests for the thin phase commit helper.

### Community 9 - "Orchestra Architecture"
Cohesion: 0.11
Nodes (17): Architectural objective, Behavioral tests, Browser testing constraint, Canonical validator, Complexity safeguards, Component responsibilities, Hooks, Installation boundary (+9 more)

### Community 10 - "integrate_local"
Cohesion: 0.30
Nodes (15): _branch(), _clean(), _command_reason(), _common_git_dir(), _git(), _head(), integrate_local(), main() (+7 more)

### Community 11 - "LocalIntegrationTests"
Cohesion: 0.30
Nodes (4): LocalIntegrationTests, CompletedProcess, Path, Temporary-repository tests for conservative local integration and cleanup.

### Community 12 - "Product principles"
Cohesion: 0.13
Nodes (14): Bounded autonomy, Evidence before claims, Intelligent orchestration, Mission, Non-goals, Orchestra Vision, Primary users, Product principles (+6 more)

### Community 13 - "Orchestra Workflow"
Cohesion: 0.14
Nodes (13): Commit path, Context and planning, Delivery policy, End-to-end flow, Local integration path, Maturity, Orchestra Workflow, Orchestrator behavior (+5 more)

### Community 14 - "commit_phase"
Cohesion: 0.35
Nodes (12): _blocked(), commit_phase(), _git(), _head_sha(), main(), parse_args(), CompletedProcess, Namespace (+4 more)

### Community 15 - "DeliveryPolicyTests"
Cohesion: 0.29
Nodes (3): DeliveryPolicyTests, CompletedProcess, Tests for explicit delivery policy and ordered argv checks.

### Community 16 - "Orchestra Agent Rules"
Cohesion: 0.18
Nodes (10): Anti-overengineering rules, Browser acceptance, Default agent flow, Delivery, Execution and commits, Language, Orchestra Agent Rules, Orchestrator responsibility (+2 more)

### Community 18 - "Orchestra"
Cohesion: 0.33
Nodes (5): Conformance, Delivery model, Direct sync, Orchestra, Product sources

### Community 19 - "Orchestra Roadmap"
Cohesion: 0.50
Nodes (3): Deferred distribution boundary, Orchestra Roadmap, Status

## Knowledge Gaps
- **66 isolated node(s):** `Product source of truth`, `Language`, `Orchestrator responsibility`, `Tier selection`, `Default agent flow` (+61 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_relative()` connect `sync.py` to `commit_phase`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **Why does `integrate_local()` connect `integrate_local` to `pr.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **What connects `Verify, fast-forward, confirm containment, and clean only safe resources.`, `Return validated policy data and a compact result.`, `Run checks in declaration order without a shell.` to the rest of the system?**
  _95 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `validate_suite.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10846560846560846 - nodes in this community are weakly interconnected._
- **Should `ValidateSuiteTests` be split into smaller, more focused modules?**
  _Cohesion score 0.12698412698412698 - nodes in this community are weakly interconnected._
- **Should `Route an Orchestra change` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `SyncTests` be split into smaller, more focused modules?**
  _Cohesion score 0.135632183908046 - nodes in this community are weakly interconnected._