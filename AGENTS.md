# Academic editorial principles

This bilingual research archive requires human academic judgment. Automation may
identify inconsistencies and prepare proposals; passing QA is not academic approval.

- **Field-discovery priority:** when significance and evidence are comparable,
  prefer new field discoveries, in-situ contexts, secure stratigraphy, direct dates,
  and coherent assemblages. Molecular methods, records, and journal prestige alone
  do not establish importance.
- **Scholarly significance:** assess changes to important archaeological questions,
  interpretive reach, evidence/context, and likely value in five to ten years.
  Separate observed findings, authors' interpretations, and editorial assessments.
- **2026 eligibility:** follow `methods.qmd`: (1) first public announcement of a
  field discovery in 2026, disclosing earlier excavation dates; (2) first full or
  substantively transformative peer-reviewed publication in 2026, disclosing prior
  publications; or (3) a 2026 reanalysis of legacy material/data producing a major
  new interpretation. A 2026 news story alone does not establish eligibility.
- **Reanalysis:** label applicable projects explicitly `Reanalysis / 旧材料再分析`
  consistently across the archive. Reanalysis is eligible, but must change an
  important question rather than merely enlarge a sample or refine classification.
  Do not infer a new classification from a QA heuristic.
- **Evidence grades:** A = strong, high-quality peer-reviewed evidence with robust
  primary support; B = reliable peer-reviewed evidence with important limitations;
  C = credible institutional/preliminary scholarly evidence awaiting full publication;
  D = announcement/media stage without sufficient independently verifiable detail.
  Evidence confidence is separate from scholarly importance. Never assign or change
  a grade automatically; use the full definitions in `methods.qmd`.
- **Balance:** audit geography, chronology, field/reanalysis, and discovery types.
  Use balance for comparable projects and portfolio calibration; never override
  evidence or significance to fill a quota.
- **Bilingual consistency:** Chinese and English must agree on dates, quantities,
  units, uncertainty, attribution, grades, and status. Flag ambiguity for review;
  do not silently harmonize academic claims. Numeric QA is a screening aid.
- **Stable IDs:** discovery filename prefixes and table IDs identify projects,
  not ranks. Never renumber/reuse them after a withdrawal or status change. ID 29
  remains Etowah. Under-review section numbers and ranking positions are not IDs.
- **Human approval:** PROMOTE, HOLD, REJECT, candidate-status changes, evidence-grade
  changes, academic conclusions, and ranking changes require explicit approval by
  the responsible human academic editor before implementation. Prepare evidence,
  proposed bilingual wording, affected IDs/pages, and rationale in a review PR.
  Do not treat an automated result, registry update, or a request for QA as approval.
  Record the editor's decision and approval reference before applying it.
- **Locked content:** respect `RELEASE_V2_2.md`, baseline
  `dd6c083df0477f1ab85b0b06739f0fc8630ffb6e`, and locked discoveries 1–23.
  Report new factual/logical/citation/rendering regressions; do not reopen settled
  conclusions or rewrite locked content without explicit human authorization.

## Development and review

Work in the existing checkout on a review branch; do not push directly to main.
Read `editorial/QA.md` before changing the checker or its observed inventory.
Run `python3 scripts/editorial_qa.py`, its mutation tests, and
`python3 scripts/check_bilingual.py`. Render with Quarto and run the rendered QA
mode. Keep generated `docs/`, screenshots, and temporary reports out of commits.
Do not run source-rewriting cleanup/image-fetch scripts as part of QA.
Quarto may alter tracked `.gitignore`; inspect `git status` and `git diff` after rendering. The current Codex `render-site` helper reports status but does not restore `.gitignore`. Do not reset, overwrite, or discard pre-existing user changes.
