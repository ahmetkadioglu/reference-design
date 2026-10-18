# Design skill comparison

This is a source-based capability comparison, not a benchmark of generated designs. It reviews the specific skills and executable resources linked below. Features elsewhere in a large repository are not assumed to belong to the reviewed skill. Descriptions and source files were checked together; advertised checks are not treated as proof of runtime effectiveness.

## Our current baseline

Reference Design combines user-supplied reference intake, visual and accessible implementation inspection, persistent reference records, and later interface creation from that collection. Records preserve evidence, access limitations, user preferences, and revision history. Explicit briefs and reference roles take priority over a preset aesthetic.

The bundled executable is a Python memory helper. Site inspection, DOM/CSS analysis, screenshot comparison, and interface verification are agent workflows using the host's tools. They are **not bundled browser automation**. Retrieval uses weighted keywords and a small multilingual alias map, not semantic search or BM25. Personal memory is excluded from the public distribution.

## Peer comparison

| Peer and reviewed scope | What it provides | What we already cover | What we lack or cover less deeply |
| --- | --- | --- | --- |
| [Anthropic frontend-design][anthropic] | Detailed art direction, typography and composition guidance, aesthetic self-critique, and UX-writing rules. | Brief-driven direction, reference roles, token choices, and a visual review workflow. | More specific aesthetic critique criteria and copy guidance for labels, errors, and empty states. This particular skill is primarily instructions, not an automated inspector. |
| [Impeccable][impeccable] | Specialized audit, critique, polish, extraction, hardening, and optimization flows; project product/design context; a bundled detector and edit hooks. | Technical inspection instructions, central token usage, responsive and accessibility checks. | Reusable specialist flows, durable project design documentation, detector tooling, edit feedback, and design-system drift checks. Its audits combine executable detection with agent judgment; the whole audit is not automatic. |
| [UI UX Pro Max][uipro] | Curated design catalogs, BM25 retrieval, stack-aware guidance, and a design-system generator with a saved master and page overrides. | Stored references, keyword search, target-stack adaptation, and per-task design decisions. | A shipped fallback knowledge base, stronger domain-aware retrieval, a reproducible design-system generator, and persistent project/page inheritance. Its saved design systems are also a form of memory. |
| [Taste Skill, current default][taste] | Curated reference/direction libraries, direction selection, asset helpers, source linting, and a Chrome-based responsive inspector. | User reference analysis, evidence recording, and desktop/mobile review instructions. | Built-in inspection reports, automated overflow/layout checks, richer starter resources, and screenshot evaluation fixtures. Its authored reference library differs from our incremental collection of user-selected URLs and preferences. |
| [Vercel web-design-guidelines][vercel] | Fetches current interface rules, reviews requested source files, and reports findings as `file:line`. | Basic accessibility, interaction, responsive, and reduced-motion guidance. | A broader maintained rule catalog and a consistent, precise audit output format. The reviewed skill is source-review instructions, not a bundled browser auditor. |

## What distinguishes Reference Design

- **An accumulating personal reference collection:** add new websites over time and reuse earlier ones without resending their URLs.
- **Evidence-aware memory:** distinguish visual estimates, CSS declarations, runtime observations, and actual source findings. Keep inaccessible references with their limitations.
- **Preference and revision tracking:** remember what the user likes or dislikes, update duplicate URLs, and preserve earlier versions.
- **Reference roles:** take typography from one source and component behavior from another while obeying the current brief.

These are the focus of our implementation, not a claim of exclusivity. Impeccable keeps project context, UI UX Pro Max persists design systems, and Taste ships researched reference material. We have not established superior output quality, and a memory record only becomes useful when the agent's inspection is good.

## Recommended priorities

These are proposals, not features implemented by this comparison.

1. **Automate evidence capture and verification.** Add a host-compatible browser adapter that can save screenshots, representative DOM/computed-style evidence, viewport/state metadata, and source locators. Add executable overflow, console-error, keyboard/focus, and accessibility checks. Preserve the existing evidence distinctions and report checks that could not run. Taste and Impeccable demonstrate useful inspection tooling; neither is being credited here with our proposed reference-ingestion pipeline.
2. **Separate reference memory from project design decisions.** Add a project design document and token export, with page overrides and links back to selected reference evidence. Preserve existing project conventions. Impeccable's context and UI UX Pro Max's master/page approach are useful precedents.
3. **Improve retrieval and fallback coverage.** Add domain/component fields and evaluate BM25 or hybrid retrieval against real queries before introducing embeddings. An optional licensed starter catalog could help with sparse memory; it should remain distinguishable from the user's own references.
4. **Ship repeatable evaluation and focused review flows.** Commit synthetic memory regression cases and CI, then add baseline-versus-skill screenshot tasks and focused audit/polish/copy workflows. Existing scratch validation is not a published test suite. Measure whether changes improve useful retrieval, correct reference roles, and the resulting interfaces.

The first two priorities most directly serve the intended workflow: reliably understand supplied sites, then reuse that knowledge consistently across a new project. Importing every peer's aesthetic restrictions would work against explicit user preferences.

## Source revisions and inspection scope

Links are pinned to the revisions reviewed so this report does not silently track later changes. No peer code or instruction text was copied into this skill. Any future reuse requires reviewing the relevant license and dependencies.

| Repository | Revision | Source files reviewed |
| --- | --- | --- |
| `ahmetkadioglu/reference-design` | `124fc77` baseline, plus this English documentation update | `SKILL.md`, all four guides, metadata, and the memory helper |
| `anthropics/skills` | `dbd4588` | [`frontend-design/SKILL.md`][anthropic] |
| `pbakaus/impeccable` | `2f46b7a` | [Skill][impeccable], [audit][impeccable-audit], [extract][impeccable-extract], [hooks][impeccable-hooks], repository source/test tree |
| `nextlevelbuilder/ui-ux-pro-max-skill` | `56ea9cf` | [Skill][uipro], [`core.py`][uipro-search], [`design_system.py`][uipro-system], data tree and README |
| `Leonxlnx/taste-skill` | `a206bbf` | [Current skill][taste], [`inspect.mjs`][taste-inspect], [evaluation cases][taste-evals], resource tree and README |
| `vercel-labs/agent-skills` | `063bee9` | [Web design guidelines skill][vercel] and its [live rule source][vercel-rules] (unpinned upstream rules) |

[anthropic]: https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md
[impeccable]: https://github.com/pbakaus/impeccable/blob/2f46b7a8b059af00d20dd13b64dbe165e7c6a742/plugin/skills/impeccable/SKILL.md
[impeccable-audit]: https://github.com/pbakaus/impeccable/blob/2f46b7a8b059af00d20dd13b64dbe165e7c6a742/plugin/skills/impeccable/reference/audit.md
[impeccable-extract]: https://github.com/pbakaus/impeccable/blob/2f46b7a8b059af00d20dd13b64dbe165e7c6a742/plugin/skills/impeccable/reference/extract.md
[impeccable-hooks]: https://github.com/pbakaus/impeccable/blob/2f46b7a8b059af00d20dd13b64dbe165e7c6a742/plugin/skills/impeccable/reference/hooks.md
[uipro]: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/56ea9cf174ed86786187daa9de0e6247cb0747e4/.claude/skills/ui-ux-pro-max/SKILL.md
[uipro-search]: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/56ea9cf174ed86786187daa9de0e6247cb0747e4/src/ui-ux-pro-max/scripts/core.py
[uipro-system]: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/56ea9cf174ed86786187daa9de0e6247cb0747e4/src/ui-ux-pro-max/scripts/design_system.py
[taste]: https://github.com/Leonxlnx/taste-skill/blob/a206bbf75a9d80554c0de17c1198ee2fbbc555aa/skills/taste-skill/SKILL.md
[taste-inspect]: https://github.com/Leonxlnx/taste-skill/blob/a206bbf75a9d80554c0de17c1198ee2fbbc555aa/skills/taste-skill/scripts/inspect.mjs
[taste-evals]: https://github.com/Leonxlnx/taste-skill/blob/a206bbf75a9d80554c0de17c1198ee2fbbc555aa/skills/taste-skill/evals/evals.json
[vercel]: https://github.com/vercel-labs/agent-skills/blob/063bee94c3f4df8453406c830b0a7df0f2860278/skills/web-design-guidelines/SKILL.md
[vercel-rules]: https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md
