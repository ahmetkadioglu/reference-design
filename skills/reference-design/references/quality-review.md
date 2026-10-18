# Audit, critique, and polish

Use this guide when reviewing or refining work created from references. Respect the requested mode: audit reports findings; polish implements authorized refinements. Do not turn an audit-only request into a redesign.

## Audit

Run the optional capture tool against the working interface when permitted. Read its findings, coverage, screenshots, and limitations. Verify each suspected problem in context; automated counts can include repeated observations or false positives.

Review what the tool does not establish: complete keyboard navigation, focus visibility and order, menu/dialog behavior, form errors, empty/loading states, zoom and text wrapping, touch interactions, real device behavior, and appropriate motion alternatives. Inspect source for semantics, token consistency, image sizing/loading, expensive effects, and unnecessary animation. Do not claim measured performance or standards conformance without the relevant measurements.

Report findings with severity, actual file:line when source is available, or URL + selector + viewport/state otherwise. Include the user impact and a concrete correction. Separate confirmed defects, heuristic warnings, and visual judgment. Prioritize blocked tasks and unreadable content before isolated polish. Do not manufacture an aggregate quality score.

## Design critique

Compare the result against the explicit brief, assigned reference roles, and saved project decisions:

- Does the first viewport establish the product, audience, and primary action?
- Do type hierarchy, reading measure, spacing rhythm, and density support actual content?
- Does the composition suit the product, or would the same structure fit any unrelated site?
- Do imagery, surface layers, and motion add useful meaning while preserving readability?
- Do repeated components follow the same visual and behavioral rules?

Describe concrete mismatches and a small set of fixes. Keep intentional user choices, including gradients, glass, grain, or restrained layouts. Do not impose blanket aesthetic bans.

## Polish

Load the resolved project/page decisions and relevant reference evidence. Fix structural hierarchy, layout, wrapping, and interaction states first; then tune surfaces and details. Consolidate clearly repeated tokens/components into the existing system without introducing broad abstractions for one-off elements.

Make copy specific to the product: action labels should say what happens, terminology should remain consistent, empty states should explain the next useful step, and errors should help recovery. Match the product's language and tone. Never replace real information with invented performance numbers, testimonials, or integration success.

Rerun affected checks and inspect the changed desktop/mobile views. State what was actually verified and what remains untested. Update project decisions when a refinement changes the system rather than only one implementation detail.
