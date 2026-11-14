# Phase 2B operating guide

Base verified against fetched `origin/main` and live remote main:
`3d518218d4825a325cef60269c6d3cea4bc2cf93` (merged PR #2).
Branch: `monitoring/phase2b-scheduled-review`. Issue #3 body and all comments
(no comments at implementation time) were read through the GitHub connector.

## Cadence and activation

`.github/workflows/monitoring-phase2b.yml` declares timezone-aware schedules:

| America/Vancouver | Mode |
|---|---|
| Monday 08:00 | Full backfill (finish a pending interval first) |
| Thursday 08:00 | Incremental monitoring with seven-day overlap |
| Friday 09:00 | Human editorial review queue refresh |
| Sunday 09:00 | Formal archive and candidate balance audit |

GitHub's `schedule.timezone` handles PST/PDT; UTC times are not hard-coded.
Scheduled jobs are guarded by repository variable
`MONITORING_SCHEDULES_ENABLED == 'true'`. Leave absent/false until successful manual
GitHub-hosted smoke runs for **all three modes**, repeated durable-state runs and
inspection of diagnostics. `workflow_dispatch` works while this switch is OFF:

```sh
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review -f mode=monitor -f full=true
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review -f mode=review
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review -f mode=audit
```

GitHub may require a workflow file to exist on the default branch before dispatch
is available. A draft-branch run does not activate a schedule; schedules run on
default branch after merge only. If dispatch is unavailable before merge, leave the
schedule switch OFF, review/merge infrastructure only, then smoke-test before
activation. Never imply the hosted smoke runs happened based on local execution.
The formal-publication switch is **separate**, in `publication-policy.json`, OFF.
Do not turn it on as part of enabling monitoring.

## Durable state and idempotency

A dedicated `monitoring/state-phase2b` branch stores **one `state.json`** containing
source windows/cursors/watermarks, hashed observations, controlled tags, run digests
and a safe latest report. It contains no raw titles, abstracts, personal names,
new source URLs, DOI strings, or coordinates. It is public if the repository is
public. Hashes permit correlation, not reconstruction of primary evidence; do not
submit community-restricted inputs in the first place. Raw API payloads are only in
runner memory. They are deliberately not persisted or uploaded. This is an
observation ledger, not an immutable primary-source archive or evidence verifier.

Within each runner, JSON is fsynced then atomically replaced; source progress and
observations share a single state transaction. A pending bounded cursor retains
its original fixed interval across days. Complete intervals alone advance a
watermark; repeated/missing cursors and failures remain incomplete. First runs and
Monday scans use January backfill; Thursday starts seven days before the last
complete watermark. Provider cursor expiry must be diagnosed and recovered by
reviewed removal of the pending cursor with overlap/backfill, retaining the ledger.
Nothing automatically resets a cursor or creates an empty state after remote errors.

Git plumbing commits state without touching the checkout or main. Every write
requires the exact parent read by the collector, a superset of previous observation
hashes, and a non-force push. A concurrent writer fails and must rerun from the
new state. Workflow concurrency serializes all three modes, never cancelling the
current writer. First-run creation requires repository contents permission. Branch
rules should restrict `monitoring/state-phase2b` to the dedicated automation and
prevent force-push/deletion. GitHub token is read-only for retrieval; only the
separate state-persistence job has contents write. It does not execute source text
or use the publication policy to merge. There is no Pages permission, deployment,
main push or source rewriting in these workflows. The existing deployment is
untouched; monitoring never shares its rendered output or edits its inputs.

Repeated identical records collapse by content hash excluding retrieval date.
Revised payloads remain observations. Hashed normalized DOI/URL/title edges group
transitively for candidate coverage, preventing repeat-DOI inflation. A title edge
is provisional identity evidence, not proof; twin DOIs and project-level identity
need academic review. Ledger queue entries have stable observation hashes, not
formal project IDs. Storage grows with changed evidence; archival/compaction needs
review, never silent truncation. Long-running/capped global Crossref backfills can
be slow; incomplete sources are explicitly reported and not called coverage.

## Reports and human queue

Safe JSON includes actual formal membership read from `discoveries.qmd`, joined
by stable ID to `editorial/inventory.json`, and discovery-page hashes. Raw region
and period columns and their frequency tables preserve the archive's actual dates.
Controlled tag counts are multi-label heuristics, not archaeological classification.
Geography/chronology tags use the corresponding table cells (not affiliations or
bibliography); methodological/type labels screen page text and may overmatch.
Unknowns remain explicit. Reanalysis uses the existing inventory; **not labelled
Reanalysis does not mean verified new field discovery**. Molecular methods are
counted without prestige weighting. Candidate coverage uses identity groups;
formal and candidate counts are shown separately. No quota or automatic selection.

The Friday bilingual summary and safe report artifact form the provisional review
queue. An operational bot-owned issue links to each run; source outages/incomplete
pagination get a separate issue on monitoring/audit runs. Queue refresh changes no
human decision. Download safe JSON for observation hashes, source IDs, dates and
screening labels. Raw primary URLs/text are withheld: an editor must retrieve them
in a controlled environment, verify accessibility and privacy, and prepare a
reviewed dossier before publishing any substantive candidate report. Thus the
implemented automatic report lane publishes operational **provisional summaries**,
not unreviewed discovery descriptions. That conservative limitation is intentional.

## Connectivity and regional sources

The Phase 2B API transport uses registered HTTPS hosts, an identified User-Agent,
25-second timeouts, 8 MB response limit, no cross-host redirects, at most three
attempts and bounded exponential/Retry-After waits. 403 is not retried; 429 and
transient server/network failures are. Public diagnostics are typed categories:
`proxy_403`, `http_403_access_or_terms`, `rate_limited`, `metadata_not_found`,
server/client response errors, network/invalid response, and cursor incompleteness.
403 alone cannot establish a site's terms; review access policy separately.
No exception body/query/credential is copied to public artifacts. OpenAlex remains
disabled pending current access/credential review; no secret is saved in config.

The existing source registry's official institutional leads (ASI, Sri Lanka,
BRIN, INAH, CABAH, ANU, Wits and Samarkand) remain disabled. This environment blocks
institutional pages as well as metadata APIs; **no verified permissible live RSS
endpoint or first-announcement extractor could be established here**. Claiming
permission, license or verified dates would be fabrication. `parse_feed` remains
a tested offline parser, not an enabled polling adapter. In particular a feed
pubDate is not proof of a first public announcement. This is an outstanding Issue
#3 deliverable, not solved by adding more unverified URLs.

For each regional/local-language feed, a subsequent reviewed registry change must
record exact endpoint/official ownership, language/region, robots and terms review
URLs/date, license/reuse basis, response/redirect limits, date semantics, community
protocols, primary first-announcement verification and outage tests. Prioritize
South Asia, Central Asia, Africa, Southeast Asia, Aboriginal Australia and the
Pacific, including local-language institutional reports. Do not bypass robots,
paywalls or community restrictions to fill coverage gaps. Hosted smoke results
must establish connectivity independently of this cloud proxy.

## Formal-publication boundary

Read `PUBLICATION_POLICY.md`. The pure gate checks a live, fully attributed dossier
and hash-bound editor attestations, rejects metadata-only/offline/unresolved cases,
and can only authorize preparation of a transaction PR. No archive-writing or
merge-capable publisher is connected. A separate independently reviewed ranking /
formal-entry integration procedure is mandatory before that can be implemented.
All current 33 entries, 44 ranks, grades, statuses and HOLD decisions are preserved.
The independent review and activation blockers must not be bypassed for a demo.

## Reproduce locally

Python 3.12, standard library only:

```sh
python -m unittest discover -s monitoring -p 'test_*.py' -v
python monitoring/operations.py --mode monitor --full
python monitoring/operations.py --mode review
python monitoring/operations.py --mode audit
python -m unittest discover -s scripts -p 'test_editorial_qa.py' -v
python scripts/check_bilingual.py
python scripts/editorial_qa.py
```

Local operations default to `monitoring/runs/durable/state.json`; do not call
`state_store persist` for local smoke data. Tests use temporary local bare repos,
never the production state ref. Old Phase 2A fixtures remain offline regressions
and are not read anywhere by the scheduled collector. Keep generated files,
reports, state, caches and screenshots out of implementation commits.
