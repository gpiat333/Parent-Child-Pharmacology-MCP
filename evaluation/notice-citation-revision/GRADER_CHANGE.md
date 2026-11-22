# Evaluation method in this revision

The grader v2 prompt, 28 questions and task criteria are unchanged from the 473-test run. The deterministic URL scanner now separates adjacent Markdown links and preserves balanced parentheses. Historical raw scores are unchanged. A separate regression rechecks the prior saved answers with the corrected parser.

MCP answers now receive applicable fixed application notices after generation. Before-notice text and notice IDs are retained. Plain-model answers receive neither tools nor these notices. This compares workflows, not raw-model ability or clinical accuracy. S2 and S6 still require human clinical framing review; no clinician adjudication occurred. Completed answers are never regenerated to improve scores. Nothing deployed.
