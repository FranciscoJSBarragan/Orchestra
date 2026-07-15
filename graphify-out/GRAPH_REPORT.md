# Graph Report - .  (2026-07-14)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 366 nodes · 776 edges · 21 communities (14 shown, 7 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5d1386d9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- sync.py
- pr.py
- SyncTests
- PullRequestFlowTests
- ValidateSuiteTests
- validate_suite.py
- integrate_local
- CommitPhaseTests
- commit_phase.py
- Orchestra Skill
- LocalIntegrationTests
- PlannedFlowContractTests
- Orchestra Workflow
- DeliveryPolicyTests
- Orchestra Agent Rules
- LightFlowContractTests
- pre-commit
- Orchestra Local Integrate Skill
- Orchestra PR Merge Skill
- Orchestra PR Open Skill
- Orchestra PR Review Skill

## God Nodes (most connected - your core abstractions)
1. `PullRequestFlowTests` - 30 edges
2. `SyncTests` - 30 edges
3. `ValidateSuiteTests` - 28 edges
4. `uninstall()` - 20 edges
5. `SyncError` - 18 edges
6. `CommitPhaseTests` - 16 edges
7. `integrate_local()` - 15 edges
8. `_analyze()` - 15 edges
9. `_apply_operation()` - 15 edges
10. `synchronize()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Root Orchestrator` --calls--> `Orchestra Skill`  [EXTRACTED]
  README.md → codex/skills/orchestra/SKILL.md
- `Orchestra Architecture` --references--> `Orchestra Vision`  [EXTRACTED]
  docs/ARCHITECTURE.md → VISION.md
- `integrate_local()` --calls--> `blocked()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py
- `integrate_local()` --calls--> `load_policy()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py
- `integrate_local()` --calls--> `run_checks()`  [INFERRED]
  codex/scripts/integrate_local.py → codex/scripts/policy.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Orchestra Base Agent Profiles** — codex_agents_analyst, codex_agents_implementation_worker, codex_agents_reviewer, codex_agents_verifier [EXTRACTED 1.00]
- **Internal Capability Playbooks** — codex_skills_orchestra_references_technical_planning, codex_skills_orchestra_references_repository_context, codex_skills_orchestra_references_frontend_implementation, codex_skills_orchestra_references_browser_acceptance, codex_skills_orchestra_references_runtime_verification, codex_skills_orchestra_references_difficult_debugging, codex_skills_orchestra_references_web_research [EXTRACTED 1.00]
- **Orchestra Delivery Workflow** — codex_skills_orchestra_delivery_policy_skill, codex_skills_orchestra_pr_open_skill, codex_skills_orchestra_local_integrate_skill [EXTRACTED 1.00]
- **Orchestra Base Profiles** — analyst, implementation_worker, reviewer, verifier [EXTRACTED 1.00]
- **Orchestra Workflow Skills** — codex_skills_orchestra_agents_openai, codex_skills_orchestra_delivery_policy_agents_openai, codex_skills_orchestra_local_integrate_agents_openai, codex_skills_orchestra_phase_commit_agents_openai, codex_skills_orchestra_pr_merge_agents_openai, codex_skills_orchestra_pr_open_agents_openai, codex_skills_orchestra_pr_review_agents_openai [EXTRACTED 1.00]
- **Deterministic Mechanical Helpers** — codex_scripts_policy, codex_scripts_pr, codex_scripts_integrate_local, codex_scripts_commit_phase, codex_scripts_validate_suite [EXTRACTED 1.00]

## Communities (21 total, 7 thin omitted)

### Community 0 - "sync.py"
Cohesion: 0.19
Nodes (39): ArgumentParser, _allowed_entry(), _analyze(), _apply_operation(), _atomic_write(), _backup_path(), _block_span(), _check_before() (+31 more)

### Community 1 - "pr.py"
Cohesion: 0.14
Nodes (38): blocked(), load_policy(), main(), parse_args(), Any, Namespace, Path, Return validated policy data and a compact result. (+30 more)

### Community 2 - "SyncTests"
Cohesion: 0.12
Nodes (4): Path, Isolated tests for direct Orchestra synchronization., Model a pre-composition install without depending on retired sources., SyncTests

### Community 3 - "PullRequestFlowTests"
Cohesion: 0.18
Nodes (3): PullRequestFlowTests, CompletedProcess, Deterministic fake-gh tests for Orchestra PR open, observe, and merge.

### Community 4 - "ValidateSuiteTests"
Cohesion: 0.12
Nodes (3): CompletedProcess, Behavioral tests for the Orchestra conformance engine., ValidateSuiteTests

### Community 5 - "validate_suite.py"
Cohesion: 0.11
Nodes (27): check_delivery_config(), check_direct_sync(), check_distribution_boundary(), check_documentation(), check_hook(), check_python_syntax(), check_python_tests(), check_required_paths() (+19 more)

### Community 6 - "integrate_local"
Cohesion: 0.17
Nodes (22): Analyst Profile, _branch(), _clean(), _command_reason(), _common_git_dir(), _git(), _head(), integrate_local() (+14 more)

### Community 7 - "CommitPhaseTests"
Cohesion: 0.30
Nodes (3): CommitPhaseTests, CompletedProcess, Behavioral tests for the thin phase commit helper.

### Community 8 - "commit_phase.py"
Cohesion: 0.23
Nodes (16): Orchestra Routing Instructions, _blocked(), commit_phase(), _git(), _head_sha(), main(), parse_args(), CompletedProcess (+8 more)

### Community 9 - "Orchestra Skill"
Cohesion: 0.13
Nodes (16): Analyst Profile, Implementation Worker Profile, Reviewer Profile, Verifier Profile, Phase Commit Skill, Architecture Guidance Reference, Browser Acceptance Playbook, Difficult Debugging Playbook (+8 more)

### Community 10 - "LocalIntegrationTests"
Cohesion: 0.30
Nodes (4): LocalIntegrationTests, CompletedProcess, Path, Temporary-repository tests for conservative local integration and cleanup.

### Community 12 - "Orchestra Workflow"
Cohesion: 0.14
Nodes (13): Commit path, Context and planning, Delivery policy, End-to-end flow, Local integration path, Maturity, Orchestra Workflow, Orchestrator behavior (+5 more)

### Community 13 - "DeliveryPolicyTests"
Cohesion: 0.29
Nodes (3): DeliveryPolicyTests, CompletedProcess, Tests for explicit delivery policy and ordered argv checks.

### Community 14 - "Orchestra Agent Rules"
Cohesion: 0.18
Nodes (10): Anti-overengineering rules, Browser acceptance, Default agent flow, Delivery, Execution and commits, Language, Orchestra Agent Rules, Orchestrator responsibility (+2 more)

## Knowledge Gaps
- **39 isolated node(s):** `Product source of truth`, `Language`, `Orchestrator responsibility`, `Tier selection`, `Default agent flow` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Orchestra Routing Instructions` connect `commit_phase.py` to `pr.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `Orchestra Architecture` connect `integrate_local` to `pr.py`, `validate_suite.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `_relative()` connect `sync.py` to `commit_phase.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **What connects `Product source of truth`, `Language`, `Orchestrator responsibility` to the rest of the system?**
  _69 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `pr.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13974358974358975 - nodes in this community are weakly interconnected._
- **Should `SyncTests` be split into smaller, more focused modules?**
  _Cohesion score 0.12477718360071301 - nodes in this community are weakly interconnected._
- **Should `ValidateSuiteTests` be split into smaller, more focused modules?**
  _Cohesion score 0.11612903225806452 - nodes in this community are weakly interconnected._