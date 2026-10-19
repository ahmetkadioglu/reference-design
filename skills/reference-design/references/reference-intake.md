# Component-first reference intake

Use this workflow for every general request to learn, analyze, or save reference websites. Treat each URL as a collection of reusable components and implementation mechanisms. A future product brief is not needed to inspect it. Preserve each source independently even when its theme differs from another.

Do not finish with only labels such as light/minimal or dark/glowing, a comparison of site personalities, a proposed blend, or a request to choose a primary reference. Theme belongs in metadata. Learn the components before making future product decisions. Choose a coherent direction only when an actual creation brief calls for it.

## Required inventory

Account for all eight categories on each supplied site. Inspect representative variants and the user's highlighted details. For a large site, define the pages/sections and sampled variants actually covered; do not claim every component was inspected.

| Category | What to learn and save |
| --- | --- |
| cards | Card variants and anatomy, media/content/action hierarchy, dimensions and padding, grid behavior, borders/radius/elevation, hover/focus/click states |
| icons | Representative SVG/sprite/image/icon-font elements, stroke/fill, size/viewBox, alignment and semantics; identify an icon library only with source evidence |
| typography | Heading/body/label/code roles; declared and applied family, weight, size, line height and tracking; font-face/assets and resolved loading when accessible |
| layout | Containers, grids/flex relationships, alignment, gaps, section rhythm, positioning and responsive transformations |
| navigation | Header/menu/sidebar/anchor behavior, active and open states, mobile variants and focus behavior |
| motion | Inspect sections while scrolling and relevant benign controls: trigger, animated property, timing/easing, sticky/pinning/parallax/reveal logic, CSS/JS source, reduced-motion behavior |
| surfaces | Backgrounds, borders, shadows, texture/gradient/blur/masks and pseudo-element/asset/canvas layers, with scope and implementation |
| ux | Information architecture, reading and action hierarchy, affordances, feedback, forms and relevant empty/loading/error states, keyboard and touch behavior |

Scroll through relevant accessible sections before reporting scroll behavior. Build explicit benign interaction plans after inspecting actual controls; the user need not separately request menus or scroll inspection during a general intake. Follow host authorization and action rules. A still screenshot, a static CSS declaration, or one viewport does not prove that animation is absent or that a control works.

For each concrete finding connect: feature and variant -> observed or declared behavior -> selector/file and evidence -> implementation mechanism -> reusable principle. Keep typography roles and component variants separate instead of flattening the page into a single aesthetic. A dark source can teach card geometry, an icon treatment, or scroll mechanics for a later light product without transferring its palette.

## Record coverage with evidence

Store the inventory under technical.intake in the same reference record. Existing visual/technical fields, preferences, facets, evidence and history remain useful. Add component and technique search facets so retrieval can find a saved pattern independently of the source's theme.

Use scripts/intake_inventory.py to create an unfinished upsert scaffold:

~~~bash
python scripts/intake_inventory.py template https://example.com/
~~~

Replace every pending category with one of:

- inspected: concrete findings with source-linked evidence and actual checks.
- not_observed: an absence finding limited to the actual pages, variants, viewports and states checked. Explain those checks.
- unavailable: the necessary layer could not be accessed. Record the attempted route and reason; do not replace it with a guess.
- out_of_scope: only for an explicit component/visual/source-limited task, with the reason. A general site intake includes all categories.

The scope is site by default. Use component for an explicitly limited component task, visual-only for screenshot/appearance-only work, or source-only for supplied code with no rendered inspection. Finding fields are feature, observation, mechanism, reuse and evidence. Use null for an unknown mechanism; a mechanism claim needs code-declaration, runtime, or source-code evidence. Visual estimates can describe appearance without establishing the code behind it.

Example of one category entry (complete the other categories too):

~~~json
{
  "status": "inspected",
  "checks": ["Read .feature-card and its :hover rule in the supplied stylesheet"],
  "findings": [{
    "feature": "Feature card hover elevation",
    "observation": "The stylesheet declares a -4px vertical translation on hover; runtime appearance is unverified.",
    "mechanism": "A transform transition on .feature-card:hover moves the card without changing layout.",
    "reuse": "Use a restrained elevation cue on actionable cards when appropriate to the target brief.",
    "evidence": [{
      "kind": "code-declaration",
      "source": "Actual inspected stylesheet URL or supplied file path",
      "locator": ".feature-card:hover",
      "finding": "transform: translateY(-4px)"
    }]
  }],
  "reason": ""
}
~~~

This is a schema example, not a reference to save. Use actual values, source names, selectors and checks. Do not mark a category inspected merely to complete a checklist. Unknown icon libraries, unverified font loading and unobserved scroll effects stay explicit unknowns.

## Completion and reuse

After upserting the actual findings, review every supplied reference ID or URL:

~~~bash
python scripts/intake_inventory.py --root /absolute/private/memory review ref-ACTUAL-ID
~~~

Fix missing inventory coverage before reporting intake complete. The command exits 1 for missing categories, pending inspections, unsupported mechanism claims, or missing evidence locators. Exit 0 establishes accounted-for structured coverage, not that the inspection is true or exhaustive. A ready result may still be partial because layers are unavailable or a mechanism is unknown. Preserve those limitations and keep the reference status partial where scoped inspection is incomplete.

The helper is read-only and does not change legacy records. Enrich existing shallow records in place, preserving preferences and history. When tools cannot save or run the check, deliver the supported analysis and disclose the unsaved or unvalidated portion; do not claim a completed save.

Extract reviewed reusable mechanisms after source interpretation. During intake, do not select a dominant source, invent a target composition, or require the user to assign every source a role. Later, search by needed component/technique and adapt suitable findings to the actual brief.

Report saved/updated counts, a few specific component/behavior findings and material coverage gaps. For example: card layout/state mechanisms, identified icon implementation, typography evidence and observed or unavailable scroll behavior. A concise response can point to the saved inventory; it must still show that component-level learning occurred.
