# Editorial consistency QA

The checker is a read-only, offline screening tool, not a fact verifier or academic
decision maker. `methods.qmd` defines the criteria. `AGENTS.md` defines editorial
and human approval requirements. Existing academic content is not rewritten.

## Run

From the repository root with Python 3.12 (standard library only):

```sh
python3 -m unittest discover -s scripts -p 'test_editorial_qa.py' -v
python3 scripts/check_bilingual.py
python3 scripts/editorial_qa.py --json /tmp/editorial-source.json
```

Render the website before checking generated targets and fragments. In the prepared
cloud environment use `/workspace/.setup/render-site`, which runs `quarto render`
and prints Git status; it does **not** restore `.gitignore`.
Elsewhere run `quarto render` with Quarto 1.11.9. Inspect changes to tracked
files afterwards; never silently overwrite or discard pre-existing edits. Then:

```sh
python3 scripts/editorial_qa.py --rendered docs --json /tmp/editorial-rendered.json
```

Exit 1 means structural consistency errors; exit 0 may still contain warnings
requiring academic review. Missing required summary claims and missing rendered
pages fail rather than silently yielding a zero-item success. Reports contain
severity, check code, source location, and the discrepancy. Do not commit generated
`docs/`, screenshot directories, Python caches, or transient report files.

The separate `Editorial consistency QA` pull-request workflow runs the same checks,
renders, and uploads source/rendered JSON findings. It neither publishes nor changes
academic text. The existing deployment workflow is unchanged.

## Identity crosswalk and observed baseline

`inventory.json` records the corpus observed at `f86ffae`: 44 ranked projects,
33 formal entries (16 CCTV and 17 Additional), and 11 under-review candidates.
Discovery IDs 1–34 retain their original meanings; 29 is under review, so only 33
have formal-list/map membership. Stonehenge is a separate research update and is
neither a numbered candidate section nor a ranked project.

Ranking and review headings currently have no explicit project-ID fields. The
crosswalk maps their exact headings to stable discovery IDs or QA-only `review:`
keys. These keys do not assign new academic project numbers. Never join by rank or
under-review section position. Exact headings deliberately fail closed on renames;
review the identity mapping when a heading changes. The crosswalk is an observed
regression baseline, not a newly approved editorial decision or independent source
of historical truth. Explicit existing HOLD decisions are recorded; absent decisions
remain absent rather than being inferred from monitoring language.

Do not regenerate the inventory automatically to silence failures. For a proposed
status, evidence-grade, decision, or ranking change, obtain the human academic
editor's explicit approval and record its reference in the review PR before applying
the change to both the pages and inventory. A consistent edit to both can evade a
baseline check: code review and human governance remain necessary. No software
approval gate or GitHub branch-protection rule is claimed here.

## Coverage

- Formal table, discovery metadata, ranking metadata, inventory, and map must agree
  on membership/status. Both language labels and evidence grades are checked.
- Stable filename/title/table IDs, consecutive ranks/review sections, explicit
  bilingual review decisions, and observed ranks/grades are checked.
- Chinese and English home/ranking summaries are compared with derived totals.
  Methods must retain three numbered eligibility pathways in each language and
  bilingual definitions of grades A–D. This checks structure, not scholarly meaning.
- The SVG map must have exactly one marker per formal project with the correct
  status class; the mobile selector must contain the same identities exactly once.
  A duplicate marker cannot pass by keeping the total unchanged.
- Markdown and HTML local links in the selected source corpus and map are checked.
  Generated HTML targets, assets, and cross-page/same-page fragments are checked
  after rendering. External URLs are deliberately not requested.
- Adjacent explicitly labelled Chinese/English prose paragraphs are screened for
  unequal Arabic-number multisets. Common `ka`, `Ma`, 千, 万, 百万 scales are normalized.
  These are warnings: spelled-out numbers, implicit units across ranges, centuries,
  unequal explanatory detail, percentages and conversions require human reading.
  This is not a full translation/date validator. Unlabelled prose, table chronology,
  Chinese number words, reference-style Markdown links, and source-only fragments
  are not fully interpreted; rendered links supply the broader link check.
- Existing ranking Reanalysis flags are checked against discovery-page bilingual
  labels; a missing label is reported, never automatically classified or inserted.

The mutation suite changes isolated temporary copies to demonstrate detection of
count drift, status/grade disagreement, rank/decision changes, retired IDs, map
duplicates/colors/options, missing targets/fragments, and numeric divergence. It
also verifies that running QA leaves academic source files unchanged.

## Review warnings

See `QA_RESULTS.md` for the initial run. Warnings are deliberately visible and are
not suppression lists or approval requests. Review each against the cited source
and publication before proposing corrections, especially within locked entries
1–23. Passing checks cannot establish 2026 eligibility, archaeological truth,
appropriate importance, balanced representation, or a justified ranking.
