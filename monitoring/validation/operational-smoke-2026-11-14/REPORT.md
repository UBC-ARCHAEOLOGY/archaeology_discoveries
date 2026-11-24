# Phase 2B GitHub-hosted operational smoke validation

**Outcome: BLOCKED before runner execution. No operational smoke succeeded.**

Date: 2026-11-14 (America/Vancouver). Base is latest main
`ad4b7e270c7add9ad826f0d46b0681b02c4776b4`, containing merged PR #4.
Safety changes are isolated on `monitoring/phase2b-operational-smoke` in Draft
[PR #5](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/pull/5).
Main and the published website were not changed by this work.

## Requested GitHub-hosted tests and actual outcomes

The existing `monitoring-phase2b.yml` already exists on the default branch, so
GitHub's workflow_dispatch default-branch prerequisite is satisfied. Requests use
the guarded workflow definition at branch commit
`4dbcc321c4c989b23a459b62de499d5d280e71c9`, based directly on latest main; the
report is a subsequent documentation-only commit on the same Draft PR branch.
No old Phase 2A branch or offline fixture is used for dispatch.

| Mode | UTC request time | Request inputs | Dispatch outcome | Operational run ID | Logs/artifacts |
|---|---|---|---|---|---|
| monitor | 20:40:53 | full=true; read_only_smoke=true | Blocked, CLI exit 1, Forbidden | None | None created |
| review | 20:41:22 | full=false; read_only_smoke=true | Blocked, CLI exit 1, Forbidden | None | None created |
| audit | 20:41:22 | full=false; read_only_smoke=true | Blocked, CLI exit 1, Forbidden | None | None created |

Actual POST endpoint for all three:

```text
https://api.github.com/repos/UBC-ARCHAEOLOGY/archaeology_discoveries/actions/workflows/monitoring-phase2b.yml/dispatches
```

The CLI was invoked directly, avoiding a preliminary workflow-lookup GET:

```text
gh api --method POST repos/UBC-ARCHAEOLOGY/archaeology_discoveries/actions/workflows/monitoring-phase2b.yml/dispatches --input -
```

Payloads contain `ref: monitoring/phase2b-operational-smoke`, the actual mode,
`full`, and `read_only_smoke: "true"`. Exact timestamps, payloads, exit codes and
error strings are in [EVIDENCE.json](EVIDENCE.json). No credential/request-auth
header is recorded. All three returned the exact error:

```text
Post "https://api.github.com/repos/UBC-ARCHAEOLOGY/archaeology_discoveries/actions/workflows/monitoring-phase2b.yml/dispatches": Forbidden
```

An independent read-only shell transport diagnostic returned:

```text
URLError: <urlopen error Tunnel connection failed: 403 Forbidden>
```

This is evidence of a **cloud transport/proxy denial**. It is not proof of a
GitHub `Resource not accessible by integration` response or a token scope denial:
there is no GitHub application response body confirming that diagnosis. The
connected GitHub plugin can read runs and manage Draft PRs, but exposes no callable
workflow-dispatch write method. Its generic fetch interface is GET-only; it was
not misused to attempt an unsupported mutation. No token, secret, App grant or
repository setting was created/changed to bypass this limitation.

Using the connected GitHub API, we queried workflow runs filtered by
`branch=monitoring/phase2b-operational-smoke&event=workflow_dispatch` before and
after the attempts. Both returned **zero runs**. Therefore there are no operational
run IDs, runtime logs, or generated monitor/review/audit artifacts to download.
Older PR regression or Pages-deployment logs are not substituted for them.

## What is verified, and what remains untested

| Requirement | Verified evidence | Remaining limitation |
|---|---|---|
| Actual hosted Crossref connectivity | No hosted request occurred | Connectivity, record counts, source availability, 403/429 handling and retries untested on operational runners |
| Source retrieval | Dispatch payload requests live monitor, not fixture replay | No records were retrieved by an operational runner; this is absence of a run, not a successful zero-result scan |
| Human editorial report | Existing report generation and safety controls covered by regression | No hosted review artifact; appropriateness of a live review report not verified |
| Regional/chronological/type/field audit | Archive source and reporting paths preserved | No hosted audit artifact or independently inspected runtime statistics |
| Runtime logs/artifacts | GitHub run list confirms no dispatch-created runs | None exist for these three tests; cannot claim inspection of nonexistent artifacts |
| Read-only safety | Guard and literal-disabled jobs inspected/tested; main/source hashes unchanged; state ref absent | Execution-time side-effect assertions are untested because no operational runner started |

The retained archive baseline is 33 formal entries and 44 ranks, with conservative
categories 0 Field discovery, 1 Reanalysis, 0 Mixed and 32 Unresolved. Those are
source/regression expectations, **not new hosted-audit results**. Regional and
chronological dictionary counts remain screening labels rather than verified
archaeological distributions. No new dates, grades, statuses or scholarly judgments
were made. Institutional/local-language feeds and actual mailbox remain disabled/
unconfigured as before; no global coverage or independently verified new record
is claimed.

## Necessary safety correction in Draft PR #5

The workflow on main has literal-disabled persistent-state and normal editorial
Issue jobs, but an independent failure-alert job can still create/update an Issue
if collection fails. Dispatching that version without protection would not meet
this request's strictly read-only/Issue-automation restriction.

The review branch adds:

1. Boolean `read_only_smoke`, **default true**, checked by the failure-alert job.
   An explicit true suppresses all failure/cancellation Issue writes.
2. An informative run name including mode/smoke status for future run correlation.
3. `always()` uploads of safe state/report artifacts, where present, even if a
   collection step fails. No raw replay or source text is uploaded. A failure
   before files exist can still yield no artifact; the runtime log is then primary.
4. Three regression tests: the actual alert expression is exercised against all
   controlled success/failure/cancelled/skipped dependency combinations; other
   production controls remain disabled; artifact-upload attempts survive failure.

Local regression: **68 tests passed** (65 retained plus three new). The existing
real Git tests write only temporary local bare repositories. Their output mentioning
the state ref does not mean the production GitHub state ref was created. Any
read-only PR CI run IDs/results are listed separately in the Draft PR, explicitly
labelled **offline regression/editorial QA**, not operational smoke.

The smoke branch is intentionally not merged. Formal policy is unchanged
`enabled:false`, editors/approved dossiers empty. Scheduled collection remains
manual-dispatch-only. Persistence and normal Issue jobs remain `if:false`. The
collector has contents-read only and no Pages permission. No workflow_dispatch,
state write, Issue automation, schedule or formal publication was activated.

## Source, ranking and website preservation

The evidence record hashes 47 academic/navigation/policy files and compares their
bytes against `ad4b7e2`: discovery pages, formal list, ranking/under-review/methods,
inventory, map, navigation/style, gitignore and OFF publication policy are unchanged.
Git remote main remains exactly `ad4b7e270c7add9ad826f0d46b0681b02c4776b4`;
`monitoring/state-phase2b` remains absent. Branch pushes/Draft PR CI do not trigger
the main-only Pages deployment workflow. The last verified published deployment
remains the merged-main release; this task did not render/deploy a new public site.
Original untracked docs/screenshots are not overwritten or committed.

## Required corrections and safe continuation

- Obtain a working, authorized workflow-dispatch API path. First resolve the
  observed proxy/transport denial; then verify Actions-write authorization if a
  genuine GitHub permission error appears. Do not infer that existing read/PR access
  includes dispatch rights. No manual GitHub steps are requested of the user here.
- Keep the smoke guard true. The existing default-branch workflow permits testing
  this branch's changed definition once an authorized dispatch path is available;
  merging this Draft PR is not necessary just to test its branch ref.
- Run monitor, wait for its terminal result, then review, then audit. GitHub
  concurrency allows at most one pending run in the current group and may replace
  an older pending run; do not enqueue all three at once.
- After each accepted dispatch, record the actual run/head ID and runner type,
  inspect every job/step/log and safe report/state artifact. Check source diagnostic
  categories, complete/incomplete intervals, counts, privacy and no writes. Test
  error handling without enabling Issue automation. Do not suppress failed sources
  or advance capped windows as complete.
- With persistence disabled and no production state ref, separate review/audit
  runs start without monitor's in-memory observations. An empty queue must be
  labelled accordingly; it does not prove monitor found nothing. Testing a
  continuous live-review chain needs an explicitly reviewed read-only artifact
  handoff, not enabling state persistence or substituting offline fixtures.
- Independently verify repository protections, writer scope, contact and source
  permissions before any later production activation. None is approved here.

**Conclusion:** dispatch requests were attempted for every permitted mode, but
hosted operational execution is blocked. No successful operational tests, actual
Crossref access, runtime report/audit statistics or artifact inspection are claimed.
The remaining blocker is recorded with exact request/error evidence rather than
relabelled as a passed test.
