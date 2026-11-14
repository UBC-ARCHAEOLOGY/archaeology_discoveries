# Assessment of the second independent review and focused PR #4 revisions

**Reviewed head:** `d07dc52262ebb9d6604cc11127686924bf289369`.
**Main/base:** `3d518218d4825a325cef60269c6d3cea4bc2cf93`.
**Branch:** existing `monitoring/phase2b-scheduled-review`; PR #4 stays Draft.

The attached report's **B — minor revisions and re-review** assessment is sound
for default-OFF infrastructure. Its two required findings are actual gaps in the
reviewed code; the normal-queue limitation is real; the affiliation recommendation
improves long-term review quality. None establishes that existing archaeology,
rankings or evidence grades are wrong. We agree with the report's separation of
OFF infrastructure, production monitoring and formal-publication approval.

The attachment is review evidence and recommendations. The owner's request is to
assess and revise the PR. The report's conditional suggestion about a later merge
is not user authorization to merge, activate settings or operate production.
Only the four focused issues are changed here, plus their tests, documentation
and necessary observation-version/package bookkeeping. No source access,
credentials, branch rules, variables, formal content or ranks are changed.

## 1. Existing Reanalysis can be silently overridden — agree; corrected

**Reviewed location:** `operations.py:256–266`.

The old function consulted proposed `research_type` before `reanalysis:true`.
A plausible editor name and HTTPS-shaped provenance therefore changed audit
classification to Field discovery without authenticating a reversal decision.
That is a real academic-governance problem even though the archive itself was
not rewritten and the publishing gate is OFF.

**Revision:** [operations.py](../operations.py), `archive_classification`,
`archive_category` and `archive_audit`. Existing `reanalysis:true` remains
Reanalysis. Any recognized conflicting proposal (Field discovery, Mixed, or
Unresolved) produces `classification_conflict:true`, preserves the proposed
category separately and requires human review, regardless of provenance syntax.
The audit lists conflicting stable IDs and adds per-row conflict/review fields.
An approval-shaped URL cannot clear the existing decision; a reversal requires
a separate explicit human academic decision. No bypass switch was introduced.

**Tests:** [test_round3.py](../test_round3.py), `ClassificationConflictTests`:

- All three conflicting categories, with and without formatted provenance, retain
  Reanalysis and require review.
- Compatible Reanalysis and genuinely unresolved inputs avoid false conflicts.
- An in-memory ID 31 proposal surfaces in audit conflict IDs/row fields while
  preserving totals and leaving actual inventory bytes unchanged.

**Observed current archive:** 0 Field discovery, 1 Reanalysis, 0 Mixed, 32
Unresolved; 33 formal entries and 44 ranks. Nothing was newly classified.

## 2. Both online and print unknown, asserted first date accepted — agree; corrected

**Reviewed location:** `eligibility.py:54–62`.

The old checker accepted a first-publication scalar with both edition dates null.
A human attestation is still required by the overall gate, but that does not
satisfy the promised structural evidence check. It could hide unresolved earlier
online publication, so stronger date semantics are warranted before OFF-infrastructure
acceptance as well as before any activation.

**Revision:** [eligibility.py](../eligibility.py), `publication_dates`, used by
both first-substantive-publication and Reanalysis routes. At least one actual
online/print date is required. Each of online, print and first-publication has
an explicit `verification` record with `status`, receipt `source_ids`, and
`rationale`. Known dates require `verified`; a missing edition requires supported
`not_applicable`, such as a genuinely online-only journal. `unknown`, unsupported
N/A, absent evidence, unresolved receipt references, two null editions and a later
first-date assertion all fail closed. The earliest-date/2026/future-date checks
remain. Announcement-route requirements are unchanged.

**Tests:** `PublicationDateEvidenceTests`:

- Both-null online/print fails for substantive publication and Reanalysis under
  unknown, N/A and purported verified markers. A re-authorized synthetic dossier
  also fails, proving rejection is not merely an outdated approval hash.
- Missing verification fields, unknown status, missing rationale and missing or
  unresolvable receipt references fail.
- Genuine online-only/print-only structures can pass with cited N/A; changing the
  absent-edition status to unknown or removing its citation makes them fail.
- Retained route-completeness and 2025-online/2026-print regressions still pass.

**Limit:** `verified` and `not_applicable` are dossier assertions to be independently
checked by the named editor, not network verification performed by this pure gate.
A syntactically complete fictional receipt can still lie. The gate remains OFF,
with no authorized dossiers, archive writer or merge path. Exact/unknown chronology
is never repaired by inventing dates.

## 3. Normal editorial Issue queue blocked by disabled persist — agree; explicitly limited

**Reviewed location:** `monitoring-phase2b.yml:97–136`.

GitHub's default dependency behavior skips `editorial-queue` when persist is
skipped. This was an intentional staged shutdown but not sufficiently clear as
a feature limitation. Removing its dependency or making it `always()` now would
enable Issue writes and broaden this revision beyond default-OFF infrastructure.

**Revision:** [.github/workflows/monitoring-phase2b.yml](../../.github/workflows/monitoring-phase2b.yml)
adds literal `if:false` to the normal queue, with an explanation. [PHASE2B.md](../PHASE2B.md)
now says **Normal Issue queue is disabled** and distinguishes manual JSON/Markdown
review artifacts from a working Issue queue. Before a future queue activation,
a separate reviewed workflow change must either restore successful protected
persistence and queue together or decouple an artifact-only queue with tested
success/failure/skipped conditions. This PR does neither. The independent
failure-alert path remains unchanged; skipped is not an operational failure.

**Tests:** `AffiliationAndQueueTests.test_issue_queue_disabled_but_manual_review_report_still_available`
checks the explicit latch/dependency/documentation, exercises artifact-only local
review, and ensures skipped queue is not an alert trigger. Retained exact-inline
workflow fixtures still simulate collection/persistence failures without artifacts.

**Limit:** No normal Issue queue or independent alert was exercised on hosted
operational runners. A manual collection entry point remains available after
GitHub's default-branch prerequisite; it is not production schedule activation.
No operational dispatch or Issue write occurred in this revision.

## 4. Affiliation-only edits generate observation noise — agree; revised narrowly

**Reviewed location:** `operations.py:191–210`.

Affiliation typography or provider identifiers are bibliographic housekeeping,
not by themselves a scholarly claim revision. Excluding them is appropriate;
this does not imply that author identity, retractions or publication dates are
unimportant or that every retained revision is a new discovery.

**Revision:** `scholarly_projection` excludes affiliation metadata while retaining
author identity, title, claims, dates, correction/retraction links and the prior
scholarly fields. Its identity version is 3. State schema 3 explicitly binds
`observation_projection:3` so old hashes cannot be mixed silently with new ones.
Legacy schema 1/2 and projection 2 are rejected, not reset or auto-migrated.
The state branch is still absent. If legacy state is encountered later, preserve
it and obtain an explicit reviewed migration/backfill; original discarded payloads
cannot be reconstructed from old hashes alone.

**Tests:** `test_affiliation_only_edits_do_not_create_scholarly_revision` changes
only affiliation formatting/identifiers and gets one observation, then changes
an author's family name and gets a retained second revision. It also rejects old
schema/projection versions. The existing provider-churn, title/abstract/date,
author and correction/retraction controls remain in the suite.

## Verification and evidence boundaries

[VERIFICATION.json](VERIFICATION.json) records exact local commands, outcomes,
source hashes, and controlled before/after reproduction of the three code gaps
against `d07dc52`. These are reproducible author-run checks, not new independent
certification or archaeological fact verification. Targeted data is synthetic;
no fixture enters production. The read-only PR workflows provide exact-head hosted
logs, render QA and a committed source/diff/manifest artifact. Their results are
recorded in the updated PR after observed completion, not inferred from earlier CI.

Local results:

| Check | Result |
|---|---|
| Monitoring regression | 65 passed: 57 retained/updated + 8 focused tests |
| Editorial mutation regression | 26 passed |
| Bilingual/Markdown | Passed |
| Source editorial QA | 0 errors, 42 existing warnings |
| Quarto 1.11.9 | 49 pages rendered from clean scratch source snapshot |
| Rendered QA | 0 errors, 42 existing warnings |
| Python compilation, YAML parse, full focused diff whitespace | Passed |
| Academic/navigation preservation | 46 files byte-identical to reviewed head and main; no content/rank/grade/status edits |

Original untracked site output/screenshots are excluded from commits and not
rewritten. All settings and policy OFF latches remain. The original attached report
is preserved in [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md), with trailing Markdown
spaces normalized and original-byte SHA256 in verification. The package includes
`round3.diff` against the exact reviewed head and `complete-pr.diff` against main.

No new claim is made about external protection, variable/credential scope,
real hosted collection/persistence/alerts, institutional contact or source
permissions, global/regional completeness, 2026 firstness, authentic new records,
32 unresolved academic classifications, or ranking/publication integration.
Well-formed fabricated state still requires trusted writers and branch controls;
schema cannot establish authenticity. The supplied review's positive findings
and unresolved external blockers are retained, not reopened or marked complete.

**Requested outcome:** a brief third independent review of these four focused
issues on the exact revised SHA, for default-OFF infrastructure only. No merge or
production/publication activation is requested or authorized by this submission.
