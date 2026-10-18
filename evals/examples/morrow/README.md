# Morrow development comparison

This is one recorded development case, not a general claim that the skill improves all designs. Both frozen outputs were built independently from the same [brief](brief.md), the same local reference HTML/CSS/JavaScript/SVG, and the same rendered desktop/mobile reference images. Agent configuration and available tools were the same; no model override was used.

- `output-one/` is the implementation produced without a custom skill.
- `output-two/` is the implementation produced with Reference Design during this upgrade.
- Both use inline CSS/JavaScript and a local noise asset. They are synthetic examples, not deployed products.
- Reference inputs are `tests/fixtures/reference.html`, `reference.css`, `reference.js`, and `noise.svg` in this repository. The source/hash manifest is [inputs.json](inputs.json).

The outputs were captured with Chromium 153 through Playwright Python 1.58.0 at 1440×900 and 390×844. A fresh independent agent received only the randomly labeled A/B review package, the shared brief, and the supplied reference screenshots. It did not receive the condition mapping, implementation sources, or preferred outcome. Its evidence arrays were reformatted to exact pair IDs after schema validation; the preferences and observations were retained.

## Recorded result

The reviewer preferred the skill output overall. It preferred that output for hierarchy, composition, and responsive adaptation; preferred the other output for visual consistency; and tied brief compliance, readability, and reference use. These are seven qualitative criterion preferences, not a numerical design-quality score.

Read the full [judgment](judgment.json) and [unblinded result](result.json), including reasons and limitations. Only default-state still images were judged. The review does not establish functional behavior, complete accessibility, performance, or a repeatable advantage across other briefs or agent runs.

## Re-render and review independently

With the optional browser dependencies installed:

```bash
python evals/run_morrow_example.py --output /absolute/private/morrow-run
```

The runner serves only on localhost during capture, renders the reference and both frozen outputs, and creates a fresh `review/` package plus a separate private unblinding key. It does not regenerate the designs, launch a judge, or claim a new result. Share only the review folder with a fresh reviewer and keep this README, prior judgment, source directories, and key outside that review context.

After a completed independent judgment, use `design_evaluation.py summarize` as described in the [evaluation guide](../../../skills/reference-design/references/design-evaluation.md). New labels, environment versions, image hashes, and judgments can differ. Preserve unfavorable or inconclusive findings. To evaluate generalization, add independent generation runs and more product briefs rather than repeatedly scoring these same two outputs.
