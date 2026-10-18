# Agent compatibility and installation

Reference Design keeps one Agent Skills bundle in `skills/reference-design/`. It uses the shared `SKILL.md` format and relative resource links, without vendor-specific executable prompt syntax or mandatory MCP servers. `agents/openai.yaml` only supplies OpenAI UI metadata; it is not required by other hosts.

The profiles below are an interoperability selection, not a popularity ranking. Paths were checked against the linked vendor documentation on **2026-10-18**. Append `reference-design/` to each skills root. The machine-readable registry is [`tools/agents.json`](../tools/agents.json).

| Profile | Agent | Project skills root | User skills root | Activate |
| --- | --- | --- | --- | --- |
| `universal` | [Shared Agent Skills](https://agentskills.io/integrate-skills) | `.agents/skills/` | `~/.agents/skills/` | Use the reference-design skill |
| `codex` | [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills/` | `~/.agents/skills/` | $reference-design |
| `claude-code` | [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills/` | `~/.claude/skills/` | /reference-design |
| `cursor` | [Cursor](https://cursor.com/docs/skills) | `.cursor/skills/` | `~/.cursor/skills/` | /reference-design |
| `github-copilot` | [GitHub Copilot](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) | `.github/skills/` | `~/.copilot/skills/` | Use the reference-design skill |
| `gemini-cli` | [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `.gemini/skills/` | `~/.gemini/skills/` | Use the reference-design skill; /skills list to verify discovery |
| `opencode` | [OpenCode](https://opencode.ai/docs/skills/) | `.opencode/skills/` | `~/.config/opencode/skills/` | Use the reference-design skill |
| `windsurf` | [Windsurf / Cascade (legacy paths)](https://docs.devin.ai/desktop/cascade/skills) | `.windsurf/skills/` | `~/.codeium/windsurf/skills/` | @reference-design |
| `devin` | [Devin Desktop / Cascade](https://docs.devin.ai/desktop/cascade/skills) | `.devin/skills/` | `~/.config/devin/skills/` | @reference-design |
| `cline` | [Cline](https://docs.cline.bot/customization/skills) | `.cline/skills/` | `~/.cline/skills/` | Use the reference-design skill |
| `roo-code` | [Roo Code](https://roocodeinc.github.io/Roo-Code/features/skills/) | `.roo/skills/` | `~/.roo/skills/` | Use the reference-design skill |
| `antigravity` | [Google Antigravity](https://antigravity.google/docs/skills) | `.agents/skills/` | `~/.gemini/config/skills/` | /reference-design |
| `kilo` | [Kilo Code](https://kilo.ai/docs/customize/skills) | `.kilo/skills/` | `~/.kilo/skills/` | Use the reference-design skill |

`universal` is a shared location, not an additional agent. It works only where the host documents `.agents/skills` discovery; Claude Code and Cline have their own primary paths. Choosing Codex, Antigravity, and universal together writes their identical project destination once. Other cross-discovered locations can still expose duplicate skills: install only the profiles you need and avoid combining a shared install with agent-specific copies of the same skill.

Windsurf's current documentation redirects to Devin Desktop. `windsurf` keeps the documented legacy locations for existing installations; `devin` uses the current locations. Antigravity now documents `.agents/skills` and `~/.gemini/config/skills`; older `.agent/skills` and `~/.gemini/antigravity/skills` locations are compatibility fallbacks, not the default profiles here. Profiles can change as vendors ship new releases.

## Install from a checkout

Python 3.10+ is sufficient; the installer uses only the standard library, performs no network requests, and installs neither agents nor browser dependencies.

```bash
git clone https://github.com/ahmetkadioglu/reference-design.git
cd reference-design
python tools/install.py list
python tools/install.py install --agent codex claude-code cursor --scope user --dry-run
python tools/install.py install --agent codex claude-code cursor --scope user
```

For one project:

```bash
python tools/install.py install --agent github-copilot gemini-cli --scope project --project /absolute/project
python tools/install.py doctor --agent github-copilot gemini-cli --scope project --project /absolute/project
```

Use `python3` on systems where appropriate, or `py -3` on Windows. The same script works in PowerShell, bash, and zsh. Paths printed as `~/...` use the actual home directory on each OS. Quote paths containing spaces. For WSL, SSH, containers, cloud agents, and remote workers, install in the environment where the agent actually executes; a local user install does not automatically appear remotely.

The explicit bundle inventory in [`tools/bundle.json`](../tools/bundle.json) includes scripts, references, the optional browser requirements, and UI assets. Unlisted files, caches, captures, and private reference memory are not distributed. There is no reduced prompt-only substitute for a complete installation.

### Alternative: the Skills CLI

With Node.js available, the independent [Skills CLI](https://github.com/vercel-labs/skills) can discover this repository's standard skill bundle:

```bash
npx skills add ahmetkadioglu/reference-design --skill reference-design
```

Select the target agents and scope interactively. For example, `--agent codex claude-code cursor --global` selects those three user-level installs. The external CLI owns its agent names, installation modes, update behavior, and network access. Use one installer per destination; this repository's `--update` intentionally does not take over directories installed by other tools.

Codex users can also invoke its skill-installer with the repository's `skills/reference-design` URL. For manual installation, copy the complete bundle to the documented directory, retaining relative paths.

## Update without losing reference memory

Finish active agent tasks before updating an installation. From an updated checkout, run the same agent/scope selection with `--update`:

```bash
git pull --ff-only
python tools/install.py install --agent claude-code cursor --scope user --update --dry-run
python tools/install.py install --agent claude-code cursor --scope user --update
```

The installer records managed file hashes in `.reference-design-install.json`, refuses to overwrite edited managed resources or unmanaged installations, preserves local memory/custom files, and removes unchanged retired bundle files. Each destination is staged and replaced with rollback on replacement failure. A batch is preflighted before any destination is changed, but a later filesystem failure can still leave earlier destinations updated; inspect the reported error and rerun. Destination symlinks must be managed through their original installation method. The installer never changes agent settings, credentials, project instruction files, or tool grants.

For a manual or external-CLI installation, update with that method and preserve the private store. Do not remove an installed skill directory before moving or backing up any default memory stored inside it.

## Share one memory across agents

By default, each copied installation has its own `references/memory/` store. For one reusable collection, configure the same absolute `REFERENCE_DESIGN_MEMORY_ROOT` in the process that starts each agent. Both reference records and reusable mechanisms use that root. Setting a shell variable after an IDE has started may not reach its agent process.

For example, set `/absolute/private/reference-memory` on POSIX hosts or `C:\Users\you\ReferenceDesignMemory` on Windows through the shell or agent launcher. This is independent of skill installation. If environment configuration is unavailable, instruct the agent to use the same `--root` for `reference_memory.py` and `mechanism_memory.py`, and `--memory-root` for `capture_reference.py`.

Do not merge existing stores automatically or configure simultaneous cross-device writers through a generic file-sync folder. The helpers reject concurrent local writers rather than reconciling distributed edits. Use an explicitly chosen synchronization approach when cross-device continuity is required. Reference memory stays private; project design decisions can use the existing project system or `.reference-design/design.json`.

## Verify in the actual host

```bash
python tools/install.py doctor --agent codex claude-code cursor --scope user
```

`doctor` compares installed resources with the current checkout, reports the memory location, and detects whether Playwright is importable in that Python environment. Exit code 1 means resources are missing or differ. An older complete installation may differ simply because the checkout is newer. It performs no writes or browser launches and does not prove the host discovered the skill, inherited environment variables, or can use a signed-in browser.

Restart/reload the host as its documentation requires. Then activate the skill using the table above and confirm the host's actual skill-loading indicator or tool event. Gemini CLI provides `/skills list` and `/skills reload`; OpenCode loads it through its `skill` tool. Cline exposes skill toggles; Roo Code mode and tool configuration can affect execution. Use a host with edit/execute access when writing memory or running helpers.

A cross-agent smoke task:

```text
Use the reference-design skill. Read my existing reference memory first.
Report the configured store location and available records without saving examples.
Tell me which visual, DOM/CSS, source-file, and interaction inspection tools
are available in this host. Do not build or publish a website.
```

For an intake/build task, supply real references and a brief afterwards. Compare output quality separately from installation success.

## Compatibility evidence and limits

- **Documentation checked:** all listed agent paths link to primary vendor sources. No vendor certification is implied.
- **Installer tested:** fresh project/user paths, complete resources, updates preserving memory, conflicting/modified files, failed replacement rollback, and shared-path deduplication. CI runs installer tests on Linux, macOS, and Windows.
- **Runtime helpers tested:** memory, mechanisms, project decisions, evaluation packaging, and the Chromium adapter have repository tests. Browser integration runs on Linux.
- **Actual host discovery:** these changes do not execute every commercial agent or test every version, remote mode, model, browser tool, or subscription. Treat vendor discovery and end-to-end design results as separate verification steps.

The [agent portability guide](../skills/reference-design/references/agent-portability.md) tells agents how to select supported capabilities and preserve honest evidence when tools differ. Contribute new profiles with an official documentation link, a checked date, installation coverage, and an actual host smoke result when available.
