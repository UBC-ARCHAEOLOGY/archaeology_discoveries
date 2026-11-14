# Latest Updates registry — editorial contract

`updates.json` is the canonical editorial registry. The Quarto filter
`scripts/updates.lua` calls the standard-library Python renderer with fixed
arguments for the homepage and `update-history.qmd`. HTML is escaped and generated
at render time; there is no hand-maintained homepage HTML, browser fetch, JavaScript
ordering, commit-time inference or monitoring publication connection.

## Initial history and dates

The registry was prepared on **2026-11-14**. It is a draft feature, not a claim that
it was deployed on that date. Six documented existing-content records form a
**retrospective baseline**, with two records in each category. Their historical
website-update dates are **null/unverified**; editorial report dates, article dates
and Git commit timestamps are not repurposed as webpage dates. Their shared
`recorded_on` identifies registry entry, not publication or archaeological recency.
No relative historical order is claimed. Original citation/date excerpts are
retained with their exact precision and hashes; this documents the archive's
existing claims, not a new independent fact-check of the underlying discoveries.

Homepage display uses up to six records (configurable within 5–8): reviewed updates
sort by actual `website_updated_on`, newest first; remaining retrospective entries
are separate and explicitly labelled. Ties use stable record IDs only, not rank.
The full history retains every public registry record; it is complete **from registry
inception**, not a claim to reconstruct all earlier site changes. With no verified
historical web dates, the initial six are a baseline, not the six proven most recent
updates. This is the request's fallback, not invented chronology.

`discovery_date`, `announcement_date`, and `publication_date` are independent
value/precision/evidence objects. Unknown is null; years stay years, not January 1.
Exact ISO dates, when used, need a source quotation supporting the value. Labels
make clear that an announcement/report date is not an excavation or website date.
Bilingual descriptions must agree on numbers; the automated check is a screen, not
full translation or archaeological validation.

## Categories and review

Only `discovery_added`, `publication_added`, `research_update` are valid. They mean
an editorial addition/update, never approval of archaeological significance,
formal-list promotion, CCTV selection, evidence grade or ranking. A research update
can refer to an existing under-review research section (Stonehenge); no formal ID
or rank is invented for it.

All changes to the public registry go through a human-reviewed PR. A `reviewed`
record needs a named responsible editor/reference and independently supported
website-update date/reference, in addition to bilingual text, relevant page and
source evidence. An approval-shaped reference is not automatically authenticated;
repository review and the existing `AGENTS.md` policy remain essential. The initial
baseline repeats documented content and records no new editor decisions or invented
approval references. This Draft PR is the review point before publication.

Evidence excerpt hashes bind the relevant quoted text, not entire source pages;
licensed-image fetching or unrelated typographic edits must not silently invalidate
historical claims. If cited text changes, validation fails for explicit review.
Original source links must already occur in the related archive page for public
records. This preserves attribution without claiming their live accessibility or
new external verification. Missing publication/report sources fail validation.

## Monitoring proposals — never automatic publication

A future monitor can call the proposal-only CLI on a draft record:

```sh
python scripts/updates.py propose --input work/draft-update.json \
  --output monitoring/runs/update-proposal.json
```

The input uses the record schema in `updates.json`; for a new project without an
approved discovery page, link the existing under-review intake page, not a fabricated
formal ID. Proposals may lack verified evidence or Chinese translation. At least one language
must contain draft text; missing translations remain empty with explicit review
flags and cannot pass public-record validation. No machine translation is presented
as checked scholarship. The helper forces `state:proposed`,
removes approval/website-date assertions, moves supplied source-date claims into
`reported_dates_unverified`, and leaves displayable dates unknown pending review.
It only writes inside resolved, non-symlinked `work/` or `monitoring/runs/` roots.
It cannot overwrite `updates.json`, academic pages or output outside those roots.
Protect private/community-restricted content before even producing a draft; no raw
monitor response or sensitive coordinates should be included.

Proposals are excluded from both homepage and history, even if accidentally present
in the registry. Moving one to public state requires an editor to verify source
and website dates, earlier history, duplicates, bilingual wording, privacy and any
existing status/grade/ranking protections, then author a review PR. A new source
must first be properly cited on the relevant page; missing pages/links fail rather
than creating a discovery automatically. Existing monitoring OFF switches, disabled
state/Issue jobs, and formal-publication policy are unchanged. No workflow is wired
to write this registry or to merge proposals.

## Checks and visual evidence

```sh
python -m unittest discover -s scripts -p 'test_updates.py' -v
python scripts/updates.py check
quarto render
python scripts/updates.py check --rendered docs
python scripts/editorial_qa.py --rendered docs
python scripts/check_updates_visual.py --site docs --output work/updates-visual
```

The mutation suite checks identity/semantic/title duplicates, source quotations,
ISO dates and precision, category values, links, numeric bilingual agreement,
required editorial/website-date evidence, chronological ordering, complete history,
HTML escaping and proposal isolation/symlink boundaries. The read-only Editorial
QA PR workflow runs these alongside existing academic checks and uploads desktop/
mobile screenshots/layout results. No Pages permission or deployment is added.
Do not commit generated docs, screenshots or temporary reports.
