# Reference Design

An agent skill that studies reference websites, records visual and implementation evidence in persistent memory, and builds future interfaces from that collection and your brief.

## Install in Codex / VS Code

Paste this into the Codex chat:

```text
$skill-installer https://github.com/ahmetkadioglu/reference-design/tree/main/skills/reference-design
```

Check `/skills` after installation and restart Codex if the skill does not appear. Private repositories require authenticated access in the installation environment.

For manual installation, copy the complete `skills/reference-design/` directory to `~/.agents/skills/reference-design/`. On Windows, use `%USERPROFILE%\.agents\skills\reference-design\`. When using SSH or WSL, install where the agent runs.

## Use

Learn references:

```text
$reference-design
Add these websites to reference memory: [URL 1], [URL 2].
I like the first site's typography and the second site's card surfaces.
```

Build later without resending the URLs:

```text
$reference-design
Use reference memory to build a booking platform homepage.
Use a light theme, blue accents, strong headings, and subtly textured cards.
```

Request analysis, a brief, or an implementation prompt explicitly when that is the desired output. Reference intake alone updates memory without starting a website build. Instructions are maintained in English; the agent responds in the user's language, and search retains useful multilingual aliases.

## What it inspects

- Visual hierarchy, typography, color, spacing, surfaces, texture, and responsive composition.
- Accessible HTML/DOM, stylesheets, computed styles, layout rules, tokens, and effect layers.
- Relevant CSS/JavaScript interactions, animation, and state changes.
- Actual files, components, styling organization, and dependencies when source access is provided.
- Evidence type, source, inspection date, user preferences, and access limitations.

A live site exposes delivered frontend resources. Original project architecture and server code require source access. Unsupported implementation details remain unknown or are labeled as proposals.

## Persistent memory

The default store is the installed skill's `references/memory/store.json`, created on first intake. Personal records are excluded from this distribution repository and are not automatically pushed to GitHub. Repeated URLs update existing records; previous versions remain in history.

Set `REFERENCE_DESIGN_MEMORY_ROOT` to a persistent directory to keep one store independent of the installation location. Sharing it across devices requires separate synchronization; installing the skill does not configure that automatically.

Retrieval uses field-weighted BM25 with multilingual aliases and optional domain, component, and technique filters. Existing version 1 stores remain readable. Search results can explain which terms and fields matched; retrieval is not semantic search.

The helper uses Python 3 with no external Python dependencies:

```bash
python3 skills/reference-design/scripts/reference_memory.py list
python3 skills/reference-design/scripts/reference_memory.py search 'grain card'
python3 skills/reference-design/scripts/reference_memory.py search 'grain card' --domain booking --component card --explain
python3 skills/reference-design/scripts/reference_memory.py validate
```

On Windows, use `py -3` or `python` if appropriate for your installation. Place an optional `--root` argument before the subcommand.

## Optional automated inspection

With Python 3.10+ and a host that permits standalone browser execution:

```bash
python -m pip install -r skills/reference-design/requirements-browser.txt
python -m playwright install chromium
python skills/reference-design/scripts/capture_reference.py https://example.com/ \
  --output /absolute/private/captures \
  --memory-root /absolute/persistent/reference-memory
```

The tool captures desktop/mobile screenshots, representative DOM/computed styles, pseudo-element layers, matching accessible CSS rules, resource URLs, reduced-motion views, and a short keyboard-navigation sample. It checks basic overflow, labels, image alt attributes, simple contrast, and console errors. Add `--hover SELECTOR` or `--focus SELECTOR` for requested states. Use `--fail-on error` when checking your own running interface.

Reports include coverage limits. Cross-origin CSS rules, original component boundaries, server code, full JavaScript behavior, and complete accessibility conformance are not established by capture. The agent still reviews screenshots and relevant source. Imported captures remain `partial`; they do not automatically become analyzed references.

The helper uses isolated Chromium contexts and does not reuse account sessions. When host rules require a different browser workflow, the agent uses that permitted workflow instead. See the [capture guide](skills/reference-design/references/browser-capture.md) for options, exit codes, and adapter details.

### Trace a requested interaction

```bash
python skills/reference-design/scripts/capture_reference.py https://example.com/ \
  --output /absolute/private/captures \
  --interactions /absolute/private/interaction-plan.json --trace-js
```

An explicit plan selects benign menu, tab, dialog, key, or scroll actions. Each step records before/after screenshots, DOM mutations, computed style changes, optional event-listener locations, and delivered JavaScript function ranges executed during the action window. Source excerpts and observations remain separate from causal interpretation. The tool does not expose internal framework state or reconstruct original source architecture. See the [interaction plan schema](skills/reference-design/references/interactions.md).

## Reusable mechanisms

Keep learned implementation patterns in private mechanism memory, linked to their reference records:

```bash
python skills/reference-design/scripts/mechanism_memory.py --root /absolute/private/memory extract --capture /absolute/capture/report.json
python skills/reference-design/scripts/mechanism_memory.py --root /absolute/private/memory upsert --file reviewed-mechanisms.json
python skills/reference-design/scripts/mechanism_memory.py --root /absolute/private/memory search 'layered card' --component card
```

Extraction produces drafts for layered surfaces, fluid type, responsive grids, and observed state transitions. The agent reviews the evidence, writes concrete adaptation steps, and records use conditions and limitations. Search uses reviewed mechanisms by default. Sources, revision history, and the current brief remain part of the decision. See the [mechanism workflow](skills/reference-design/references/mechanisms.md).

## Project design system

Keep selected project decisions separate from reference evidence. Use an equivalent existing project system, or initialize a project document:

```bash
python skills/reference-design/scripts/design_project.py --project /absolute/project init --name 'Booking'
python skills/reference-design/scripts/design_project.py --project /absolute/project update --file decisions.json
python skills/reference-design/scripts/design_project.py --project /absolute/project update --page booking --file page-overrides.json
python skills/reference-design/scripts/design_project.py --project /absolute/project show --page booking
python skills/reference-design/scripts/design_project.py --project /absolute/project export-css --page booking
```

The document stores master tokens/rules/reference roles and explicit page overrides. CSS export resolves inheritance; it does not rewrite existing styles automatically. See the [project guide](skills/reference-design/references/project-design.md) for the JSON schema. Audit, critique, and polish requests use the [quality review workflow](skills/reference-design/references/quality-review.md).

## Evaluate actual design outcomes

Build two outputs from equal briefs, content, references, and tool access. Capture them at identical viewport/state settings, then prepare a blinded review:

```bash
python skills/reference-design/scripts/design_evaluation.py prepare \
  --baseline /absolute/baseline/report.json --candidate /absolute/candidate/report.json \
  --brief /absolute/brief.md --output /absolute/private/review \
  --key-file /absolute/private/unblinding/key.json
```

The reviewer receives only the A/B package and completes the judgment template with screenshot evidence. Summarization checks the original artifacts and maps preferences back to conditions:

```bash
python skills/reference-design/scripts/design_evaluation.py summarize \
  --review /absolute/private/review --judgment /absolute/completed-judgment.json \
  --key-file /absolute/private/unblinding/key.json
```

This evaluates generated interfaces through an independent review, not an automatic aesthetic score or pixel-similarity target. Inconclusive and unfavorable results remain part of the record. See the [evaluation guide](skills/reference-design/references/design-evaluation.md).

The [recorded Morrow development case](evals/examples/morrow/README.md) includes an equal-input brief, two frozen implementations, an independent judgment, limitations, and a rerendering script. It is one case rather than a general quality benchmark.

## Requirements

- An Agent Skills-compatible agent with file access; installation above targets Codex.
- Python 3.10+ and writable persistent storage for the helpers.
- Permitted web/browser and relevant DOM/CSS inspection tools for live reference analysis.
- Optional Playwright and Chromium for the bundled capture adapter.

The skill uses the host's available tools and permissions. It does not install a browser or grant access to services.

## Development checks

```bash
python -m unittest discover -s tests -v
```

Memory and project tests use temporary stores. To include the real-browser fixture tests, install the optional browser requirements and Chromium, then set `REFERENCE_DESIGN_BROWSER_TESTS=1` before running the suite. `REFERENCE_DESIGN_BROWSER_PATH` can point to an explicitly configured local Chromium. GitHub Actions defines both standard-library checks and a browser integration job; runtime reports and personal memory are excluded from distribution.

## Comparison with other design skills

Read the [source-based comparison](docs/design-skill-comparison.md) for a review of Anthropic frontend-design, Impeccable, UI UX Pro Max, Taste Skill, and Vercel web-design-guidelines, including our current gaps and proposed priorities.
