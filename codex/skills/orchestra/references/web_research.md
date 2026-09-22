# Web research playbook

For direct role use, apply WORKFLOW "Standalone tools": keep the engineering
guidance below, but omit phase-only transport, artifact IDs, and formal plan
bundles. Return inline evidence or an explicitly requested output path.

For a delegated capability assignment, use this playbook with the `orchestra_analyst` profile and the explicit `web_research` capability.

Technical techniques may also be consulted in the caller's current workflow
under WORKFLOW "Modular engineering". Assignment-specific role limits, phase
artifacts and independent-gate rules apply when that assignment is selected;
reading this reference does not itself dispatch a role or grant authority.

## Contract

- Research only the time-sensitive external questions named in the packet and explain why current evidence is needed.
- Prefer official documentation, standards, first-party repositories, and original research. Use secondary sources only to locate or contrast primary evidence.
- When the host exposes documentation, code-search, or package-metadata tools (for example documentation MCPs), use them as the preferred retrieval channel for primary sources; treat their answers as evidence that still needs version and date, never as authority. Do not inventory unrelated tools.
- Match evidence to the named product version, date, platform, or jurisdiction and call out material version gaps.
- Provide direct citations beside supported claims, publication or update dates when relevant, conflicts between sources, and clearly labeled inference or uncertainty.
- Do not browse broadly after the focused questions are answered and do not make repository or external-system changes.

Return `blocked` when the question is too broad, primary evidence is unavailable, access requires unauthorized credentials or cost, or the sources cannot support a reliable conclusion. Never fill a current-information gap from memory.
