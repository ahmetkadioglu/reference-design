# Design skill comparison

This is a source-based capability comparison, not a benchmark of generated designs. It reviews the specific skills and executable resources linked below. Features elsewhere in a large repository are not assumed to belong to the reviewed skill. Descriptions and source files were checked together; advertised checks are not treated as proof of runtime effectiveness.

## Our current baseline

Reference Design combines user-supplied reference intake, visual and accessible implementation inspection, persistent reference records, and later interface creation from that collection. Records preserve evidence, access limitations, user preferences, and revision history. Explicit briefs and reference roles take priority over a preset aesthetic.

The current implementation includes optional Playwright capture and basic UI checks, explicit interaction plans with DOM/style changes and bounded executed-JavaScript evidence, field-weighted BM25 retrieval, a reviewed mechanism library, project/page design decisions, and a blinded screenshot comparison workflow. Agent source interpretation, independent visual review, and host permissions remain necessary. Personal memory and captures are excluded from public distribution. Peer source revisions below remain the original reviewed snapshots; this is not a fresh benchmark of those projects.

## Peer comparison

| Peer and reviewed scope | What it provides | What we already cover | What we lack or cover less deeply |
| --- | --- | --- | --- |
| [Anthropic frontend-design][anthropic] | Detailed art direction, typography and composition guidance, aesthetic self-critique, and UX-writing rules. | Brief-driven direction, reference roles, token choices, critique and copy review guidance. | Richer aesthetic calibration and evidence that those guidelines improve actual output. This particular skill is primarily instructions, not an automated inspector. |
| [Impeccable][impeccable] | Specialized audit, critique, polish, extraction, hardening, and optimization flows; project product/design context; a bundled detector and edit hooks. | Technical capture, project design decisions, basic checks, and audit/critique/polish instructions. | Broader specialist tooling, automatic edit feedback, and design-system drift detection. Its audits combine executable detection with agent judgment; the whole audit is not automatic. |
| [UI UX Pro Max][uipro] | Curated design catalogs, BM25 retrieval, stack-aware guidance, and a design-system generator with a saved master and page overrides. | User references, BM25/facet retrieval, target-stack adaptation, and persistent master/page decisions with CSS export. | A shipped fallback catalog, stack-specific knowledge packs, and automatic design-system generation from curated data. Our project tool persists decisions the agent makes; it does not generate them from a catalog. |
| [Taste Skill, current default][taste] | Curated reference/direction libraries, direction selection, asset helpers, source linting, and a Chrome-based responsive inspector. | User reference memory, browser evidence reports, basic responsive checks, and local browser fixtures. | Richer starter/asset resources, broader source linting, and a visual output evaluation history. Its authored reference library differs from our incremental collection of user-selected URLs and preferences. |
| [Vercel web-design-guidelines][vercel] | Fetches current interface rules, reviews requested source files, and reports findings as `file:line`. | Basic executable checks and a source/selector-aware audit reporting workflow. | A broader continuously maintained interface rule catalog. The reviewed skill is source-review instructions, not a bundled browser auditor. |

## What distinguishes Reference Design

- **An accumulating personal reference collection:** add new websites over time and reuse earlier ones without resending their URLs.
- **Evidence-aware memory:** distinguish visual estimates, CSS declarations, runtime observations, and actual source findings. Keep inaccessible references with their limitations.
- **Preference and revision tracking:** remember what the user likes or dislikes, update duplicate URLs, and preserve earlier versions.
- **Reference roles:** take typography from one source and component behavior from another while obeying the current brief.

These are the focus of our implementation, not a claim of exclusivity. Impeccable keeps project context, UI UX Pro Max persists design systems, and Taste ships researched reference material. We have not established superior output quality, and a memory record only becomes useful when the agent's inspection is good.

## Upgrade coverage and remaining priorities

| Original priority | First upgrade | Remaining work |
| --- | --- | --- |
| Evidence capture | Chromium adapter, desktop/mobile and reduced-motion views, representative styles/rules, explicit menu/tab/dialog/scroll plans, DOM/style deltas, executed-code excerpts, and memory import | Deeper source/causality review, broader accessibility measurement, and more host adapters |
| Project design memory | Atomic project document, master/page inheritance, reference roles, and CSS token export | Existing-token synchronization, reusable component extraction, and drift detection |
| Retrieval | Field-weighted BM25, facets, explanations, legacy-store compatibility, and source-linked reviewed mechanism records with draft extraction | Larger retrieval evaluations and an optional licensed starter catalog; semantic retrieval only if justified |
| Evaluation and review | Runtime/browser fixtures, CI, review guidance, and blinded equal-input screenshot packages with evidence-based judgment summaries | Repeated comparisons across representative briefs, broader real-world fixtures, and performance measurements |

The next practical step is to exercise intake and creation on real user-supplied references, then prioritize failures observed in that workflow. Importing every peer's aesthetic restrictions would work against explicit user preferences.

## Source revisions and inspection scope

Links are pinned to the revisions reviewed so this report does not silently track later changes. No peer code or instruction text was copied into this skill. Any future reuse requires reviewing the relevant license and dependencies.

| Repository | Revision | Source files reviewed |
| --- | --- | --- |
| `ahmetkadioglu/reference-design` | `124fc77` original baseline; first implementation upgrade in the current tree | Skill guides, memory/project/capture helpers, browser probe, tests, and CI configuration |
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
