# Latest Updates — validation and independent-review scope

Base: latest main `ad4b7e270c7add9ad826f0d46b0681b02c4776b4` (merged PR #4).
Branch: `website/bilingual-latest-updates`. This is a Draft PR feature; it has not
been merged, deployed or published. Existing monitoring/publication controls are
unchanged. No archaeological discovery or status promotion is performed.

## Editorial/date assessment

The existing repository documents substantive additions, citations and corrections,
but the per-entry historical website-update dates are not independently established.
Dates on editorial reports, source publications or Git commits cannot fill that gap.
The feature therefore uses the explicitly permitted fallback: six **retrospective
baseline** records, two per category. Each has a real referenced archive page,
original source link already cited there, and checked source excerpts. No new
paper, media report, archaeological claim, evidence grade or selection judgment
has been invented. Stonehenge remains a research update, not a new formal entry.

`recorded_on:2026-11-14` is the actual registry-preparation/recording date, not a
claimed original page-update date or a claim of public feature deployment. All
six `website_updated_on` values are null and visibly labelled unverified. Dates
on publications/announcements retain their existing precision; exact announcement
and report dates are used only where explicitly documented. This baseline is not
represented as the six proven most recent historical changes. Future reviewed
records sort by verified website-update date; complete history retains all public
records, with retrospective entries separate.

Human review must independently assess the bilingual summaries and evidence before
merging. Source/citation checks substantiate what the archive already records; they
do not constitute a new external scholarly fact-check or HTTPS availability test.
See `README.md` for category, date, proposal and approval contracts.

## Local checks observed

| Check | Result |
|---|---|
| Registry/mutation tests | 13 passed |
| Existing editorial mutation tests | 26 passed |
| Retained monitoring tests | 65 passed |
| Bilingual/Markdown checker | Passed |
| Source editorial QA | 0 errors, 42 existing review warnings |
| Quarto 1.11.9, isolated scratch snapshot | 50 pages rendered, including permanent history |
| Rendered editorial QA | 0 errors, 42 existing warnings |
| Rendered registry identities/order/links | Six public cards on home/history; proposals absent; updates precede map |
| Existing full link checker | 0 internal broken, 0 observed external 404, 149 external unreachable |
| Targeted visual/DOM checks | Desktop 1440×1000 and mobile 390×844, homepage and history; no page/card horizontal overflow; 2/1 columns; bilingual text; no page errors; mobile navigation to history works |
| Visual captures | 8 focused screenshots plus 46 existing full-site desktop/mobile captures |
| Source preservation | 45 academic/safeguard files byte-identical to main; original homepage introduction preserved |
| Python compile, diff whitespace | Passed |

External unreachable results are a cloud network/proxy limitation, **not** proof
that those original sources are healthy or broken. There is no claimed successful
live source verification. Internal target/fragment checks and existing citation
bindings are separate from external HTTP health.

The existing 42 editorial warnings remain visible, including the Tampa Bay
Reanalysis-label warning. No warning was used to alter a discovery interpretation,
grade, rank, status, inventory or map. Current totals remain 33 formal discoveries
and 44 ranking positions; ID 29 remains outside the formal list. The only homepage
source change is the inserted information section; navigation adds the history
link and styles are scoped to update components.

Tests cover duplicate IDs, titles and substantive events; invalid/missing dates,
precision or source/date evidence; invalid categories; broken/unsafe links;
bilingual number drift; required editor/website-date evidence; date ordering;
history beyond the homepage limit; safe HTML escaping; proposal exclusion,
English-only monitoring drafts, and output-path/symlink isolation. A proposal is
not approval, and cannot overwrite the registry or academic source. Reported source
dates in proposals are explicitly unverified and never rendered as confirmed dates.

## Reproducibility and review evidence

`VALIDATION.json` records the baseline, current counts and source hashes. Source
checks are ordinary author-run verification, not independent academic certification.
The read-only Editorial consistency QA workflow now repeats registry tests and
checks, renders, checks generated identities/links, and uploads
`latest-updates-visual-qa` screenshots plus `layout-results.json` on the exact PR
head. Existing Monitoring offline regression continues independently. Hosted CI
results and artifact IDs are recorded in the Draft PR after observed completion.

Local rendering and screenshots used `work/latest-updates/render-source`, so
original untracked site HTML and screenshots were not regenerated. Generated HTML,
QA screenshots/reports and scratch data are excluded from commits. No caption
cleanup or source-rewriting image-fetch scripts were run. The deployment workflow
is untouched; this PR has no Pages permission or automatic publication step.

No new schema state/Issue/publication controls are activated. The feature is an
editorial information layer only. Any future monitored update requires a proposal,
privacy/source/date/bilingual checks and human PR review before entering the public
registry; formal discovery membership/grades/ranks remain governed separately.
