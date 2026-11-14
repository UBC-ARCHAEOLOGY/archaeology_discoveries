# Phase 2A: Global Archaeological Discovery Monitor

This is a read-only candidate **proposal** pipeline. It implements the three
2026 pathways in `methods.qmd`, field/context priority, and the geographic and
thematic gaps identified in `V2_3_BALANCE_AUDIT.md`. It never assigns evidence
grades, formal-list membership, rankings or PROMOTE/HOLD/REJECT decisions.
Human academic review remains mandatory under `AGENTS.md`.

## Reproduce the bounded sample (Python 3.12, standard library)

From the repository root:

```sh
python -m unittest discover -s monitoring -p 'test_*.py' -v
python monitoring/monitor.py --mode offline --as-of 2026-11-14 --output monitoring/runs/replay
```

Offline is the default and performs no requests. Committed reference output is in
`sample/candidates.json`, `sample/candidates.csv`, `sample/candidates.en.md` and
`sample/candidates.zh.md`. The same fixture/config produce byte-identical output.
The input SHA256 and configuration SHA256 are recorded; source provenance includes
the baseline Git commit, path and content hash. Missing dates remain null; a year
without a month/day remains a year. No authors or institutions are generated.

The sample contains **17 real repository-sourced candidate claims and four
explicitly controlled duplicate observations**, yielding 17 identity groups. It
is not 17 newly discovered projects or a fresh external search. Existing projects
are used only to exercise monitoring; their formal status is neither copied into
monitor output nor altered. Primary URLs/DOIs are reproduced from those pages,
**not independently verified**. Sample fieldwork histories and significance
statements are attributed repository claims, not verified results. See
`VALIDATION.md` for coverage and false-positive review.

## Bounded live retrieval and replay

```sh
python monitoring/monitor.py --mode live --as-of 2026-11-14 --verify-dois \
  --output monitoring/runs/live --state monitoring/runs/state.json
python monitoring/monitor.py --mode offline --input monitoring/runs/live/replay.json \
  --output monitoring/runs/live-replay
```

Reuse the same output directory and state together: live replay evidence is a
cumulative ledger of earlier observations. Changed metadata is retained as a new
observation, allowing conflicts to be inspected. Exact unchanged observations are
collapsed; duplicate evidence is grouped rather than overwritten. An incremental
state without its previous replay fails closed. Keep the replay and state together
when moving runs; the workflow intentionally starts fresh on each manual run and
does not download or commit state. Offline replay never advances state.

Crossref requests use **index dates**, overlapping seven days from the previous
successful window to catch late deposits/corrections. Bibliographic publication
dates remain separate. A source watermark advances only after exhausting its
cursor interval and successfully writing raw evidence/reports. Failure, repeated
cursors and page caps do not advance it. The default is two pages of 25 per
source; capped runs are explicitly incomplete. Increase the bounds deliberately
when a window cannot be exhausted. HTTP errors, rate limits, paywalls and proxy
failures are reported, never bypassed. No retry storm or alternate scrape occurs.
Sources are sequential with a finite timeout; 429 does not advance state.

OpenAlex has an adapter but is disabled pending access/credential review. It
rescans the configured publication window (no claimed incremental update-date
coverage), with bounded cursors. Do not put secrets into config or artifacts.
Future authenticated transport, automatic continuation across capped runs and
institutional RSS polling are outside this foundation.

## Source registry and coverage configuration

`sources.json` lists Crossref, OpenAlex, eleven specialist archaeology journals
(via Crossref journal metadata endpoints), and eight official institution leads.
Each entry records scope, enabled/disabled state, adapter and access limitations.
ISSNs are query configuration, not evidence of API completeness. Publishers may
omit or delay deposits; journal metadata does not imply access to article text.
No prestige/citation weighting is used. Molecular methods are tagged, not rewarded.

`config.json` controls year/date window, API query, page bounds, overlap, priority
regions and tag dictionaries. Fieldwork/stratigraphy/survey place observations in
an intake-priority bucket, not a significance rank. Geographic matches use word
boundaries (India must not match Indonesia). Tags are proposals with matching
terms; lexical rules miss implicit geography and can confuse a researcher's
affiliation with a find location. Explicit curated `tags` can supplement them.
Coverage is counted by identity group, not raw duplicate observations. Counts
reflect the sample, not archaeological activity in a region.

Official institution entries are deliberately disabled: stable endpoints,
permissions, robots/terms and community restrictions have not been established.
There is **no institutional page scraper**. API calls are restricted to the two
metadata API hosts. A pure RSS/Atom parser is unit-tested for future permitted
feeds but does not fetch anything. A dated feed entry is not automatically a
first announcement. Researchers may supply attributed extracts in an offline
input with the same `records`/`source_access` structure, clearly recording URL,
retrieval date, permission basis, quotation/claim and earlier history. Do not
supply protected/sensitive site coordinates or community-restricted information.

## Evidence and classification contract

Each observation retains retrieved claims (`claims.en`/`claims.zh`), publication
and announcement dates, source timestamps where supplied, raw provider payload,
provenance, earlier history and unresolved flags. Field/discovery dates belong in
`earlier_history`/fieldwork context and must not be replaced by article dates.
Crossref `created`/`indexed` dates are never announcement dates. Earliest online
publication takes precedence over later print publication; a 2026 print issue does
not establish first publication when online publication was in 2025.

DOI syntax and URL normalization do **not** establish resolution. Optional DOI
lookups check reported DOI, publication title and year against Crossref metadata;
conflicts are retained. `metadata_matched` means matching bibliographic fields,
not verification of archaeological results or academic significance. Same-provider
checks are explicitly flagged as not independent. URL metadata linkage is checked
against the returned metadata or DOI URL; HTTP target availability and page
contents remain unverified. Unfetched links are labelled `syntax_only_not_resolved`.
The restricted-network sample has no successful verification response.

Classification requires explicit input claims: `first_announcement_claim`,
`substantive_publication_claim`, or `legacy_material`, along with the relevant
2026 date. All results are **proposals**, including those claims in the curated
sample. Date alone leaves classification unresolved. Earlier-history gaps and
substantive-increment questions are flagged; the program cannot establish that
no earlier announcement exists. Legacy-material studies require review of a
major interpretive gain. No rule infers reanalysis from molecular method alone.

Deduplication uses normalized DOI, normalized URL, exact normalized publication
title and explicit curated project/site key, with transitive grouping. Every
match records its basis. Title/project edges require review; conflicting DOIs
within a project remain visible. Different papers at one site may be distinct
studies; no fuzzy/site proximity merge is made. Missing identifiers remain missing.
Candidate IDs are hashes of grouped observations, not permanent discovery IDs;
adding evidence can change a group ID. There is no formal-list synchronization.

Bilingual reports quote available source-language excerpts; no machine translation
is presented as checked scholarship. Missing Chinese summaries are explicitly
flagged and replaced with a Chinese review notice. JSON retains full evidence,
CSV provides observation-level rows and group IDs, and Markdown provides discovery
facts, reported importance, a proposed review question, fieldwork context,
primary links, history and caveats. Significance is intentionally not scored.

## Actions and editorial safeguards

`.github/workflows/monitoring-dry-run.yml` has **only workflow_dispatch**, default
offline; it runs tests and uploads artifacts for 14 days with `contents: read`.
It does not commit, open issues, edit pages, deploy, or activate a schedule.
A future maintainer must explicitly supply replay/state between runs; there is
no hidden state cache. Phase 2B scheduling requires separate explicit approval.
The site's explicit Quarto render list excludes monitoring and scratch Markdown,
so candidate proposals cannot become public site pages through automatic discovery.
CLI writes are confined to resolved subpaths of `monitoring/`, including state,
and reject symlink escapes. Source files, registry and config are read-only inputs.
