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

The helper uses Python 3 with no external Python dependencies:

```bash
python3 skills/reference-design/scripts/reference_memory.py list
python3 skills/reference-design/scripts/reference_memory.py search 'grain card'
python3 skills/reference-design/scripts/reference_memory.py validate
```

On Windows, use `py -3` or `python` if appropriate for your installation. Place an optional `--root` argument before the subcommand.

## Requirements

- An Agent Skills-compatible agent with file access; installation above targets Codex.
- Python 3 and writable persistent storage for the memory helper.
- Permitted web/browser and relevant DOM/CSS inspection tools for live reference analysis.

The skill uses the host's available tools and permissions. It does not install a browser or grant access to services.

## Comparison with other design skills

Read the [source-based comparison](docs/design-skill-comparison.md) for a review of Anthropic frontend-design, Impeccable, UI UX Pro Max, Taste Skill, and Vercel web-design-guidelines, including our current gaps and proposed priorities.
