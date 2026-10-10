# Model notes

Read this when you first write a packet for a model family in a conversation.
Copy into the packet, verbatim, the lines whose condition matches the
assignment; add nothing else from a vendor guide. Task-root packets take none
of the leaf-role lines, because a root stops at approval gates. Each line
answers a behavior its vendor guide documents; drop a line a replay shows has
no effect.

## Every family

- Never ask a delegate to think longer or to write out its reasoning: effort
  comes from the assignment, and Opus 5.5 may decline reasoning extraction
  ([Opus 5.5: calibrate effort](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5#calibrate-effort),
  [safeguard refusals](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5#safeguard-refusals)).
- `web_research`: "Today is <YYYY-MM-DD>. Versions, prices, deprecations and
  anything 'latest' may have changed since your training data; search for
  them even when you feel sure. Facts that cannot change need no search."
  ([Haiku 5.5: accurate search results](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5#accurate-search-results))

## Claude (Opus, Sonnet, Haiku)

- Leaf roles: "End your turn only with your final report or a blocker you
  cannot resolve within your authority; put any status note in the same
  message as your next tool call."
  ([Opus 5.5: unattended agentic runs](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5#unattended-agentic-runs),
  [Haiku 5.5: early stopping](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-haiku-5-5#prevent-early-stopping-in-long-agent-prompts))
- `frontend_implementation` without a design system: name the concrete styles
  to avoid; "avoid a generic look" only swaps one default for another
  ([Opus 5.5: frontend design defaults](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5#frontend-design-defaults)).

## GPT (Sol, Astra, Luna)

- Every role: "If a skill or AGENTS.md instruction makes you pause or block,
  name its file, quote it, and separate its explicit requirement from your
  interpretation."
  ([GPT-6: instruction following](https://developers.openai.com/api/docs/guides/latest-model))
- Every role: "Write the Summary as short prose paragraphs; use lists only
  for parallel items."
  ([GPT-6: writing style](https://developers.openai.com/api/docs/guides/latest-model))
