# Frontend and source-code inspection

Apply this workflow alongside visual analysis when URLs or code are supplied. Focus on the pages, components, and effects relevant to the brief rather than reading unrelated bundles.

## Separate access layers

| Available source | Supported conclusions | Unsupported conclusions |
| --- | --- | --- |
| Screenshot | Visual proportions, surfaces, hierarchy, approximate values | Original CSS/DOM/JS, hover behavior, source directories |
| HTML / rendered DOM | Element tree, semantics, classes, repeated structures | Original framework component boundaries or folder layout |
| CSS / computed styles | Declared rules; applied values for inspected runtime states | Whether an unused declaration affects the page |
| Delivered JavaScript | Accessible behavior code and some technology signals | The complete original architecture or server implementation |
| Accessible source repository | Actual files, components, tokens, state logic, dependency manifests | Whether a different revision matches the deployed version |

Follow the environment's browser, session, and tool rules. Do not assume DevTools access exists. Inspect only accessible pages, linked resources, and provided or accessible repositories.

## 1. Locate relevant implementation

- Distinguish initial HTML from the DOM rendered after JavaScript. An empty application shell is not the complete interface.
- Identify relevant elements, ancestor containers, and linked styles/scripts. Search accessible sources by selector, class, variable, or event.
- Use permitted read-only DOM/computed-style inspection. An accessibility snapshot is not a complete DOM/CSS inspection.
- In repositories, read applicable project instructions first, then follow relevant components, styles, theme/token files, manifests, and imports.
- Use directly linked, accessible source maps only when environment rules permit. State when analysis remains at compiled-code level.

## 2. Explain layout and organization

- Extract container sizing, max-width relationships, margins, padding, gaps, and alignment.
- Trace grid/flex parent-child behavior: column definitions, minmax/auto-fit, basis/grow/shrink, order, wrapping, and content expansion.
- Inspect positioning, overflow, sticky behavior, transforms, z-index, and stacking-context creation.
- Find custom properties, theme scopes, repeated tokens, and how components consume them.
- Record media/container queries and their changed rules. Separate source breakpoints from tested viewport behavior; inspect near a breakpoint when possible.
- With source access, explain directory responsibilities, shared components, variant APIs, style encapsulation, and repeated patterns using actual files. Do not invent a source tree from repeated DOM elements.

## 3. Find the effect's real layer

- Inspect font family/weight/size, leading, tracking, font-face, and actual resolved fonts for heading/body/label/code roles when tools expose them. A declared font stack does not establish successful loading.
- Inspect representative icons: inline SVG or sprite/use targets, viewBox, stroke/fill, size, alignment, image/font assets, accessible name, and decorative treatment. Follow actual imports or asset evidence before naming an icon library.
- Decompose card variants into container, media/icon, text, metadata and action areas. Inspect parent layout and card states separately from the page palette.
- Record colors, borders, radius, and shadows for the relevant element and state. Account for cascade, overrides, and resolved theme variables.
- Determine whether a surface uses gradients, background images, SVG filters, texture assets, canvas, or CSS filters.
- Trace pseudo-elements, opacity, blending, masks, filters, backdrop filters, and isolation.
- For grain, find the actual source, such as SVG turbulence, a texture asset, or canvas generation. Texture visible in a screenshot does not identify its implementation.
- Distinguish filtering an element from blurring the background behind it. One blur declaration does not establish a glass treatment across the whole interface.

## 4. Follow interaction and motion

- Find whether hover/focus/active/open states come from pseudo-classes, classes, data/ARIA attributes, or JavaScript state.
- Identify transition/keyframe targets, timing, delays, easing, and triggers. Verify behavior at runtime when possible; source inspection alone is not an execution test.
- Follow trigger → state change → DOM/class/attribute update → visual result for menus, tabs, and dialogs.
- During general intake, inspect relevant sections while scrolling rather than waiting for a separate motion request. For observed scroll effects, trace the observer/listener/animation connection and affected element/property. Record sticky/reveal/pinning behavior, timing, trigger conditions and reduced-motion handling when accessible. A script filename or still image is not proof of a mechanism or of animation absence.
- Support framework/library claims with dependencies, imports, or explicit runtime evidence. Surface similarity and class names are insufficient. State architectural inference limits without repository access.

## 5. Convert findings into decisions

A short working table is enough:

| Feature | Evidence | Mechanism | Target adaptation |
| --- | --- | --- | --- |
| Card layout | .cards and its media query in the inspected stylesheet | Grid changes to one column at the observed breakpoint | Apply that layout principle to the existing CardList |
| Textured surface | .card::before and its linked texture | Separate low-opacity decorative layer | Preserve legibility and pointer access |
| Menu | Handler and aria-expanded update | State-controlled panel visibility | Use the project's existing state/accessibility pattern |

Include source URL/file and selector/function, plus a line or runtime state when available. Use names and values actually found in the source. Label new target tokens as proposals.

Distinguish the original mechanism from the target implementation. Adapt to the user's brief and existing architecture instead of imposing the reference stack.

## Completion criteria

- Explain the relevant DOM/layout, card/icon/font implementations, styling/layers, UX/state patterns, and interaction logic.
- For intake, account for all required inventory categories; record unavailable layers instead of replacing missing analysis with light/dark style adjectives.
- Connect important findings to concrete evidence.
- State unavailable layers and runtime verification limits.
- Inspect actual component/file organization when a repository is available; otherwise leave those boundaries unknown.
- Preserve the explicit brief and target project's conventions in the implementation plan.
