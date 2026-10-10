# Persistent project workspace

WORKFLOW "Initiative coordination" owns location, authority, retention and the
single-writer rule. This is an optional Markdown shape, not a board service or a
parser contract. Use the existing register when one already serves the project.
Obsidian, a native Project store or a plain editor can display the same files.

A caller-owned external folder is the ordinary default. A user-selected ignored
`<persistent-repo>/orchestra/projects/<project>/` can contain:

- `BOARD.md`: the one live register read by the coordinator on continuation.
- `PROJECT.md`: optional stable repo identities, context links and working choices.
- Child report links or retained evidence whose actual access has been verified.

Resolve the local Git exclude file through Git before adding the selected path;
do not assume `.git` is a directory. This keeps the board out of source delivery,
but does not back it up. Record its retention owner and handoff destination before
its storage is released. Do not use an ephemeral child checkout for this folder.

## Example BOARD.md

```markdown
# Project

Brief and authority: <approved conversation/document>
Repositories and persistent context: <PROJECT.md or existing references>
Coordinator: <native handle>; retention: <owner and destination>

## Now

- Task A: <objective>, <repo>, <route/tier>, <root model/effort>.
  Owner/checkout: <native handle and isolated checkout>.
  Dependency: <accepted contract/revision>; result/review: <accessible links>.
  Observed: <blocker or accepted SHA>; delivery: <actual outcome, if any>.
- Task B: dispatch pending <intent and host>; reconcile before relaunch.

## Next

- <Candidate task and dependencies; does not grant execution authority>.

## Done

- <Task>: accepted <SHA>, delivered <SHA/environment>, <evidence>.
```

Human edits remain meaningful. The parent rereads before a narrow update and
consumes child handoffs; children never rewrite the board. Stable repository
knowledge belongs in its existing maintained docs under the established authority,
not in duplicated progress notes. Read [the packet example](packet-example.md)
for the bounded information passed to each task root.

## Project working instructions

Keep Project preferences as a pointer to the prepared source, not a copy of its
workflow. For example:

```text
Use orchestrator from Orchestra revision <full approved SHA>.
Resolve that source's runtime and read its coordination entry and host transport.
Project context: <accessible PROJECT.md and BOARD.md>.
Task authority: <the grants from this conversation; backlog is not approval>.
Report the instruction revision the next child actually resolves.
```

Replace the pin only for new assignments or an explicitly reconciled continuation.
Updating a plugin on a developer's machine does not edit remote Project preferences.
