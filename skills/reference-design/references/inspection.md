# Reference inspection guide

Scale inspection to the request. For a card, inspect that card and relevant states. For general site intake, use the eight-category inventory in [reference-intake.md](reference-intake.md), covering representative variants and relevant states even when the user has not named each feature. Prioritize highlighted details without reducing the rest of the site to a theme label.

## Inspect these properties

| Area | Useful observations |
| --- | --- |
| Composition | Content width, column proportions, alignment, asymmetry, margins, section rhythm |
| Hierarchy | First focal point, heading/body ratio, emphasis, CTA location, reading order |
| Typography | Serif/sans/mono character, weight, size relationships, leading, tracking, line length |
| Color | Page/surface/text/border/accent roles, saturation, temperature, contrast |
| Surfaces | Card shape, corners, outlines, shadow spread, elevation, layer order |
| Texture | Grain scale/intensity, gradient direction, transparency, blur, highlights |
| Components | Navigation, buttons, inputs, labels, tables; repetition and information density |
| Imagery | Photo/illustration treatment, aspect ratio, cropping, icon weight and scale |
| Interaction | Observed hover, focus, open/closed, active, loading, empty, and error states |
| Motion | Observed trigger, direction, rhythm, and purpose; label unobserved behavior as proposed |
| Responsive | Observed column, order, menu, spacing, and type changes at each inspected viewport |

## Evidence notes

Keep only notes that support decisions:

```text
Source: URL or supplied image name
Inspected: page/section, viewport, observed states
Access: visual / DOM / stylesheet / computed style / JS / repository; status of each
Observation: visible form, hierarchy, color, behavior
Technical evidence: element/selector/file, rule or behavior, applicable viewport/state
Evidence type: visual estimate / code declaration / runtime verification / source code
Approximation: estimated measurement or possible implementation
Adaptation: principle to reuse and how to change it for the target product
Limitation: missing mobile view, unverified font/effect, unavailable code, etc.
```

- Confirm exact font families through CSS/computed styles or source evidence; otherwise describe their visual character and propose alternatives.
- A still image does not establish hover, animation, or off-screen sections.
- Label unmeasured colors and dimensions as estimates. Keep proposed tokens separate from source measurements.
- An image does not prove a CSS mechanism: apparent background blur could be baked into an asset.
- Update evidence and decisions when a new reference changes the analysis.

## Synthesize sources for a creation brief

During intake, keep independent source/component inventories. Do not require references with different themes to compete for a primary role. When an actual target brief exists, use a compact mapping of component-level findings:

| Design area | Source | Supported finding | Target adaptation |
| --- | --- | --- | --- |
| Typography | A | Large headings and short lines | Apply a clear hierarchy to the product's own content |
| Cards | B | Thin outlines and soft shadows | Adapt to the requested palette and corner system |

Honor assigned roles. Otherwise select suitable component and mechanism findings, then define a coherent target system from the brief. A whole-site primary source is optional; contrasting palettes do not prevent learning from both sources.

## Decision record

Resolve these before implementation; identify source measurements versus proposed values:

- Page/component scope and primary user action.
- Required preferences and excluded visual choices.
- Selected component-level reference roles; a primary site only when useful to the actual brief.
- Semantic palette and heading/body/supporting type hierarchy.
- Width, grid, spacing, radius, border, shadow, and optional texture values.
- Supported DOM/layout, CSS/layer, and interaction mechanisms; target component/style organization.
- Observed mobile behavior versus your proposed adaptation.
- Required states and acceptance criteria.

Use the project's existing documentation structure for substantial work. Short working notes suffice for small tasks; do not generate a report file by default.
