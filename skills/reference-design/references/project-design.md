# Project design decisions

Use project design memory for substantial builds, multi-page work, or explicit requests to preserve a design system. Reference memory records what sources demonstrate; this document records what the current product chooses. Do not create a project for intake-only or prompt-only work unless requested.

Inspect existing project documentation and tokens first. Reuse them when they already provide an equivalent source of truth. Otherwise use `scripts/design_project.py` with the target project path. The file is `<project>/.reference-design/design.json`; keep it in the target project's normal persistence workflow, not the public skill distribution.

```bash
python scripts/design_project.py --project /absolute/project init --name 'Booking'
python scripts/design_project.py --project /absolute/project update --file /absolute/decisions.json
python scripts/design_project.py --project /absolute/project update --page booking --file /absolute/page-overrides.json
python scripts/design_project.py --project /absolute/project show --page booking
python scripts/design_project.py --project /absolute/project export-css --page booking
python scripts/design_project.py --project /absolute/project validate
```

Initialization refuses to overwrite an existing document. Updates merge nested objects and replace explicitly supplied arrays. Omitted values survive. The complete document is validated before an atomic locked write; invalid or corrupt documents are preserved. Read resolved values at the start of later implementation tasks.

An update is a layer patch with any of these keys:

```json
{
  "tokens": {
    "color": {"background": "#f8fafc", "text": "#14213d", "accent": "#2563eb"},
    "space": {"card": "24px"},
    "radius": {"card": "24px"}
  },
  "rules": {
    "theme": "light",
    "texture": "Only card surfaces, subtle, behind readable content",
    "typography": "Use the project's existing sans-serif family"
  },
  "references": [
    {"url": "https://example.com/", "role": "Card surface mechanism; target values are proposed"}
  ]
}
```

Treat this as a schema example, not a source or palette to import automatically. Record actual selected URLs and assigned roles. Keep measurements versus proposed target values clear in the rules and source evidence.

The master layer is the baseline. Page layers inherit it and override only explicit keys. `show --page` resolves the combined layer; an unknown page is an error rather than a silent fallback. Updating the master also validates every resolved page. Page names are lowercase slugs such as `booking/details`.

CSS export prints resolved token values as custom properties, for example `--color-accent` and `--space-card`. Names must be lowercase CSS-safe identifiers; nested paths must not collide when flattened. Values must be finite numbers or single CSS values. Export emits `:root`; scope the generated variables to the page using the target stack when necessary. It does not build components or synchronize existing styles automatically.

When polishing an existing product, preserve its system and change the narrowest relevant layer. When the user changes the brief, update the relevant decisions and explain material changes. Page overrides cannot excuse violating explicit global product requirements.
