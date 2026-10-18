# Working across agents

Use the same `SKILL.md`, references, scripts, and assets on every host. Resolve links and helper commands relative to the actual installed skill folder, not the project's working directory. Only `name` and `description` are required frontmatter. `agents/openai.yaml` is optional OpenAI UI metadata; other hosts can ignore it. Do not translate the core into always-on rules or add host-specific tool grants.

## Establish available capabilities

Before acting, identify the current task, persistent memory location, project instructions, and permitted tools. A discovered skill does not establish that a host can browse, run Python, render screenshots, inspect DOM/CSS, or write durable files.

| Available capabilities | Workflow |
| --- | --- |
| Files and Python 3.10+ | Read/write reference and mechanism memory with the bundled helpers |
| Permitted browser with screenshots and DOM/style access | Analyze visual and technical layers through that browser |
| Permitted standalone execution, Playwright, and Chromium | Optionally use the capture and interaction helpers |
| Repository/source access | Inspect original files and architecture within that source scope |
| Screenshots only | Analyze appearance and label implementation explanations as proposals |
| Text/code only | Report source findings; leave visual verification unconfirmed |
| Read-only or temporary storage | Use accessible findings and disclose unsaved additions |

Prefer the host's supported browser, plugins, and tools. Do not assume a tool is named Playwright, `browser`, `web`, or `computer`; inspect its advertised capability. Follow host rules for sessions, authentication, execution, and allowed actions. A Python dependency being installed is not authorization to launch it. Do not start a separate browser to evade host restrictions.

## Keep memory continuous

Different agent installations otherwise create different default stores. Reuse `REFERENCE_DESIGN_MEMORY_ROOT` when configured. If the host cannot propagate environment variables, use one explicit absolute `--root` for reference/mechanism helpers and `--memory-root` for captures. Read the [memory workflow](reference-memory.md) before saving. Do not silently merge conflicting stores or move personal references into project version control.

For cross-agent work on a project, retain the project's existing design system or `.reference-design/design.json` and its page overrides. That project document records product decisions; it does not replace the user's reference collection.

## Activate and verify

Invocation syntax is a host feature. Codex uses `$reference-design`; Claude Code and Cursor offer `/reference-design`; Cascade offers `@reference-design`. On other hosts, request “Use the reference-design skill” and confirm that the host actually loads it. Do not tell every user to type a Codex-only command.

Once loaded, follow the same intake, evidence, implementation, and review workflow. If a capability is missing, finish the supported scope and report the specific missing layer. Do not report installation or tool success as proof of visual fidelity. Keep responses in the user's language.
