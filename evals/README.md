# Forward evaluation tasks

`scenarios.json` contains reusable task inputs and review criteria, not generated results or a claimed quality benchmark.

Run each scenario in a fresh agent thread. Give the agent the installed skill path, the task's raw artifacts, and a new temporary memory/project location. For capture tasks, serve the fixture directory on localhost and pass its actual URL. Keep task turns sequential where memory continuity is the behavior being evaluated. Never use personal reference memory for these cases.

Review the agent's emitted artifacts and tool evidence as well as its final response. A plan or a claimed save is insufficient when the task requires persistent files. Preserve the raw outputs and failures outside the public distribution; do not seed a later run with prior answers.

For a visual comparison, run the same implementation brief with and without the skill, equal tool access, equal content, and equal viewport sizes. Have an independent reviewer assess screenshots without the condition labels. Evaluate brief compliance, hierarchy, readability, consistency, responsive behavior, and working interactions. Record observed differences; do not infer design quality from unit-test success.

Use `skills/reference-design/scripts/design_evaluation.py prepare` to create the reviewer package, and `summarize` after an independent judgment. Keep the condition key outside the reviewer directory. The [evaluation guide](../skills/reference-design/references/design-evaluation.md) documents the CLI and evidence requirements. Screenshot review covers appearance; verify working interactions separately through explicit capture plans.
