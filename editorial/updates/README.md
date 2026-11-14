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

## Review revision: frozen bootstrap and public wording

`editorial/updates/baseline-manifest.json` freezes the six original record IDs,
full canonical record hashes and 2026-11-14 recording day. A seventh baseline,
replacement ID, changed content or changed recording day fails validation. This is
an explicit one-time historical bootstrap exception; future public additions must
use `reviewed`, with responsible-editor and verified website-date evidence.
Editing the manifest and validator together is still a repository trust boundary:
these checks do not authenticate human approval or prove branch protection exists.

Baseline labels say Existing archive entry / 既有发现条目, Existing publication
reference / 既有文献记录, or Existing research note / 既有研究记录. Reviewed
additions say Archive entry added / 新收录条目 or Reference added / 新添文献.
These describe website editorial actions, never archaeological firstness or 2026
eligibility. Baselines retain registry order, not a fabricated date order. The
homepage omits repeated recording dates and detailed date tables; full dates,
evidence context and source links remain in the permanent history.

Substantive duplicate identity is now related page plus canonical source URL,
independent of category or date. This deliberately conservative rule may reject a
truly distinct later event using the same source: it requires a separately reviewed
identity/schema extension, not changing a category or date to bypass the check.
Mirrored sources and paraphrases still require human semantic duplicate review.

## Homepage correction: past week (supersedes initial homepage contract)

The owner clarified that the old Current coverage block is to become **过去一周的更新 |
Updates In the Past Week**, at its original position. The prior pre-map retrospective
card section is removed. Homepage includes only reviewed, verified website-dated
records from seven Vancouver calendar dates including today; no minimum, padding
with historical records or truncation by `homepage_limit` (retained for schema
compatibility). The permanent history retains all records. Within each category,
records are newest first. New `ranking_changed` and `site_updated` categories log
already approved actions; they do not authorize rankings or publication decisions.

A tiny local progressive-enhancement script removes records that age out between
site builds and updates the Vancouver window. It never fetches proposals or writes
data; without JavaScript the labelled build-date interval remains visible. New
records still require review and a new site build. No scheduled monitoring is added.

One real website event is now logged: PR #6's already successful 2026-11-14 Pages
release of bilingual Update History, tied to run 43645480011 and owner approval.
No undocumented archaeological additions or ranking changes are inferred from Git
timestamps. Empty groups mean no verified logged events, not proof of no changes.

The subsequent verification also located successful Pages run **42686436717**:
its deploy log reports success at 2026-11-09T19:49:26Z for exact build
`f86ffae6a66913f701920d95d79310729b9563e9`. The registry now logs that release's
Bongal addition (owner commit `3df8376`), Font Major earlier-reference addition
(`f86ffae`), Plain of Jars independent caution/report link (`29a6b9e`) and provisional
ranking revision (`d6eea18`). These are verified published release changes, not dates
inferred solely from commits, new scholarly decisions or assertions that the
underlying discoveries/publications occurred that week. Baseline inventory records
remain frozen separately; this is not a complete reconstruction of all site history.

## Beijing timezone supersession

The owner subsequently requested Beijing time. The active weekly digest now uses
Asia/Shanghai in both Python and browser calculations. Previously logged verified
website days are converted from UTC deployment-success receipts; optional structured
`published_at` requires a matching Beijing date. Frozen historical baselines keep
their original recording dates and remain outside the digest. Historical review
notes above describe the implementation at their time, not the current timezone.
See `BEIJING_AND_MEDIA.md` for timestamp evidence and media-coverage findings.
