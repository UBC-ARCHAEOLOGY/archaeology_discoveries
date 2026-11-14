# Phase 2B operating guide

Base verified against fetched `origin/main` and live remote main:
`3d518218d4825a325cef60269c6d3cea4bc2cf93` (merged PR #2).
Branch: `monitoring/phase2b-scheduled-review`. Issue #3 body and all comments
(no comments at implementation time) were read through the GitHub connector.

## Planned cadence and activation (all schedules disabled)

`.github/workflows/monitoring-phase2b.yml` declares timezone-aware schedules:

| America/Vancouver | Mode |
|---|---|
| Monday 08:00 | Full backfill (finish a pending interval first) |
| Thursday 08:00 | Incremental monitoring with seven-day overlap |
| Friday 09:00 | Human review summary/artifact; Issue queue disabled |
| Sunday 09:00 | Formal archive and candidate balance audit |

GitHub's `schedule.timezone` handles PST/PDT; UTC times are not hard-coded.
Scheduled collection is **hard-disabled in the committed workflow**: the collector
accepts only `workflow_dispatch`, irrespective of repository-variable values. The
contents-write persistence job also has `if: false`, so manual smoke cannot mint
its write token. Both latches require a later reviewed workflow change. Keep
`MONITORING_SCHEDULES_ENABLED` absent/false; its actual current value is unverified.
The following commands are for **after the workflow exists on the default branch**,
and are documentation only in this round (none is executed):

```sh
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review -f mode=monitor -f full=true
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review -f mode=review
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review -f mode=audit
```

GitHub requires the workflow file to exist on the default branch for
`workflow_dispatch` to trigger. `--ref` selects a ref to run only after that
prerequisite; it cannot make a PR-only workflow dispatchable. After independent
code review, an infrastructure-only merge with both switches OFF could establish
that prerequisite; this revision neither performs nor authorizes that merge.
Merge of OFF infrastructure is not production approval. Then run artifact-only
manual smoke for monitor/review/audit. Before any hosted contents-write test,
independently verify branch protections and credential scope, and obtain a separate
reviewed change lifting only the persistence latch. Successful hosted state tests
and a later reviewed schedule-latch change plus the explicitly approved repository
variable are required before any production schedule. Local execution is not
hosted smoke evidence. See [GitHub workflow_dispatch documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch).
The formal-publication switch is **separate**, in `publication-policy.json`, OFF.
Do not turn it on as part of enabling monitoring.

## Durable state and idempotency

A dedicated `monitoring/state-phase2b` branch stores **one `state.json`** containing
source windows/cursors/watermarks, hashed observations, controlled tags, run digests
and report digests. Schema 3 does not retain a restored `latest_report`;
reports are regenerated from validated state and the actual archive. It contains no raw titles, abstracts, personal names,
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
separate state-persistence job declares contents write, and that job is currently
hard-disabled. Read authentication is injected in the restore process environment
only; checkout does not retain a collector credential. It does not execute source text
or use the publication policy to merge. There is no Pages permission, deployment,
main push or source rewriting in these workflows. The existing deployment is
untouched; monitoring never shares its rendered output or edits its inputs.

Scholarly observations use a versioned explicit projection: normalized DOI/URL,
title, author identity (not affiliation metadata), publication dates, claims/abstract, earlier history, work type and
correction/retraction relations. Raw provider payloads, indexed/deposited timestamps,
reference metadata, author-affiliation formatting, scores and citation counts do not enter identity. A scholarly
change retains a new revision; a source/retrieval change merges source IDs and
updates last-seen without adding an editorial observation. Hashed DOI/URL/title
edges still group revisions; title edges are proposals, not identity proof.

Schema 3, observation projection version 3 and a taxonomy SHA256 bind the state format and local tag dictionary.
`state_schema.py` validates the entire restored object before replacement or use:
exact field sets, enabled source allowlist, tag dimensions/labels, source ID lists,
hash types, dates, category, windows/cursors, run keys/digests, diagnostics and parent
commit. Duplicate JSON keys, oversized state, unexpected fields and old schemas
fail closed. The collector category must be `Unresolved`; academic categories can
only come from reviewed archive provenance. Schemas 1 and 2 are **not silently migrated**; projection 3 excludes affiliation-only edits.
The schema binds the projection version so incompatible old observation hashes cannot
be mixed with new identity hashes.
The reviewer observed no production state branch. If any legacy state exists later,
preserve it, stop writes, review an explicit migration/backfill; old hashes alone
cannot recover the scholarly projection from discarded raw payloads. Taxonomy
changes also need reviewed migration, not dropping unknown labels. Bounds (32 MB,
100,000 observations, 10,000 runs, 16 KB cursor) stop rather than truncate.
Storage still grows with genuinely revised evidence. Compaction and cursor-expiry
recovery require review; incomplete backfills must never be described as coverage.

## Reports and human queue

Safe JSON includes actual formal membership read from `discoveries.qmd`, joined
by stable ID to `editorial/inventory.json`, and discovery-page hashes. Raw region
and period columns and their frequency tables preserve the archive's actual dates.
Controlled tag counts are multi-label heuristics, not archaeological classification.
Geography/chronology tags use the corresponding table cells (not affiliations or
bibliography); methodological/type labels screen page text and may overmatch.
The four output categories are `Field discovery / Reanalysis / Mixed / Unresolved`.
Existing Reanalysis flags remain respected. A future explicit category requires a
named editor, approval reference and source references in reviewed archive metadata;
no such metadata is added by this PR. A conflicting proposal cannot reverse an
existing `reanalysis:true`, even with syntactically valid provenance. The audit keeps
Reanalysis, emits `classification_conflict`, the proposed category and human-review
requirement, and lists conflicting stable IDs. Resolving the established academic
flag requires a separate explicit human decision; an approval-shaped URL alone
cannot authorize a reversal. The current audit remains **0 Field discovery,
1 Reanalysis, 0 Mixed, 32 Unresolved**. Non-Reanalysis never implies field discovery. Molecular methods are
counted without prestige weighting. Candidate coverage uses identity groups;
formal and candidate counts are shown separately. No quota or automatic selection.

The Friday bilingual summary and safe report artifact are the available provisional
review output for manual smoke. **Normal Issue queue is disabled**: its
`needs: [collect, persist]` dependency would skip it whenever persist is skipped.
The job now also has literal `if: false`, making that intended restriction explicit.
A manual `mode=review` can produce JSON/Markdown artifacts; it cannot publish or
refresh an editorial Issue. Before enabling any normal Issue queue, a separately
reviewed workflow change must either require successful protected persistence and
restore both jobs together, or decouple an artifact-only queue with explicit
success/failure/skipped semantics. Test those dependencies on hosted runners.
The independent failure alert does not depend on normal-queue execution and remains
separate; skipped is not failure. The proposed bot-owned Issue would link each run; source outages/incomplete
pagination get a separate issue on monitoring/audit runs once operational writes
are separately approved. An independent `always()` alert job checks collection,
persistence and queue failures/cancellations without downloading reports/state or
checking out code. It has issues-write only, and emits a safe job summary even if
the issue API fails. Full workflow cancellation, runner outage, unavailable GitHub
API or denied issue permissions can still prevent delivery; an external watchdog
and repository notification settings must be reviewed before production. Queue refresh changes no
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
No exception body/query/credential is copied to public artifacts.
`contact.json` provides a reviewed stable institutional contact configuration. Its
email and approval reference are intentionally null, not a fabricated address.
The existing project URL identifies the client. After the responsible institution
supplies and approves a non-personal mailbox, Crossref requests use it in User-Agent
and `mailto`; OpenAlex requests do not. Polite-pool access is not claimed before
that configuration and hosted verification. Do not configure a mailbox during this
revision or place credentials in this file. OpenAlex remains
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

## Repository safeguards: required, not claimed enabled

The independent review on 2026-11-14 found `main protected:false`, no rulesets and
no state branch. This round does not modify settings and has no current independent
proof that those conditions changed. Repository-variable value and future App
restrictions are unverified. Before **any** hosted contents-write run, the owner
must establish and an independent reviewer must verify main/state branch protections,
required editorial/monitoring checks, independent review and dismissal of stale
approvals, no force-push/deletion and a state-writer identity that cannot bypass
main protections. Protect workflow/policy changes through owner review. Provide
API/settings evidence at a recorded commit/time; do not treat this document as proof.

`GITHUB_TOKEN contents:write` is repository-scoped, **not ref-scoped**. A fixed-ref
script and a separate job reduce exposure but are not an authorization boundary.
Use a reviewed GitHub App/appropriate repository and ruleset configuration for the
future state writer, with narrowly scoped permissions and short-lived credentials;
do not introduce a PAT here. Confirm actual bypass behavior rather than assuming
an App is automatically limited to one branch. The persistence job stays disabled
until this is resolved. Schema validation does not authenticate fabricated but well-formed hashes/labels.
No variables, credentials or protections were activated.

All actions in monitoring workflows and editorial QA are pinned to upstream tag
SHAs resolved read-only during this revision. These pins prevent tag movement;
they are not a claim that upstream implementation received a full security audit.
The existing Pages deployment workflow is untouched and still uses mutable refs;
harden it in a separate deployment review. Re-review pins/dependency updates and
retain provenance for the selected commits. See `review-round2/RESPONSE.md`.
