# Blinded design evaluation

Use this workflow when asked to compare design outcomes or establish whether a skill change helps. Run the same brief, content, reference artifacts, tools, and target viewports for both conditions. Keep the agent runs independent. Existing runtime tests validate the tools; a visual comparison evaluates actual generated interfaces.

## Prepare two comparable outputs

Build and run each output locally through the permitted environment workflow. Capture both with the browser helper using identical viewport/state settings and the same browser version. Resolve capture errors first. Do not substitute unrelated sample pages or give one condition extra requirements or assets.

```bash
python scripts/design_evaluation.py prepare \
  --baseline /absolute/private/baseline/report.json \
  --candidate /absolute/private/candidate/report.json \
  --brief /absolute/private/brief.md \
  --output /absolute/private/review \
  --key-file /absolute/private/unblinding/key.json
```

The helper creates a static `index.html`, `review.json`, PNG assets, and `judgment-template.json`. A/B labels are randomly assigned once for the complete comparison. The private condition key remains outside the reviewer package. Share only the reviewer package with an independent reviewer. `--seed` gives reproducible assignment for infrastructure tests; omit it for ordinary review. Add repeatable `--reference-image PATH` flags to include the shared reference screenshots; with default criteria this adds a reference-use criterion.

Default pairing includes the normal-motion default view at each viewport. `--all-states` includes every report snapshot state and reduced-motion view, requiring matching state names. Per-step trace screenshots remain trace artifacts and are not automatically paired. Semantic scenario names help pair equivalent interactions when implementation selectors differ. Missing views and changed browser versions are errors, not silently omitted data.

## Independent judgment

Ask an independent human or fresh agent to inspect the actual images and complete a copy of the template. Do not disclose condition labels, desired winners, prior conclusions, or the key. Keep access to unrelated run folders outside the review scope.

Default criteria cover brief compliance, hierarchy, readability, composition, consistency, and responsive adaptation. `--criteria PATH` accepts a JSON array of `{ "id": "...", "instruction": "..." }` for relevant criteria. Provide actual reference evidence when evaluating reference fidelity.

For each criterion, choose `A`, `B`, `tie`, or `unassessed`, explain the reason, and cite screenshot pair IDs. An overall preference also requires a rationale and pair evidence. Use `unassessed` where the available screenshots do not establish the answer. Do not infer working forms, menu keyboard behavior, performance, or complete accessibility from still images; verify those separately with interaction scenarios and appropriate checks.

## Unblind and report

```bash
python scripts/design_evaluation.py summarize \
  --review /absolute/private/review \
  --judgment /absolute/private/completed-judgment.json \
  --key-file /absolute/private/unblinding/key.json
```

Summarization verifies comparison IDs, criterion coverage, evidence, and hashes of the original review manifest and screenshots. It maps the independent preferences back to baseline/candidate and reports criterion votes alongside separate automated quality observations. It does not produce an automatic aesthetic score or treat pixel similarity as quality.

One comparison is one case, not proof that a skill improves all designs. Preserve ties, losses, unassessed criteria, and limitations. Repeat across representative briefs before drawing general conclusions. Keep private runs and condition keys out of the public skill distribution; publish only deliberately selected, sanitized examples or results.
