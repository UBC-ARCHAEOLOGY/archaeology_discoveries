# Proposed standing authorization — inactive

Issue [#3](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/issues/3)
authorizes designing this exception, not activating it. `publication-policy.json`
is OFF, has no editors, approval references or approved dossiers. Collector data
cannot set policy. `publication.evaluate` is a pure gate and has no archive writer.
Passing it can authorize **preparing a transaction PR only**. There is no automatic
merge or direct-main publication capability in Phase 2B.

The general human-approval rule in `AGENTS.md` remains effective. The proposed narrow
exception permits a responsible editor's reviewed, hash-bound standing-policy
attestation to replace a separate per-run PROMOTE instruction for **new Additional
candidates only**. It never delegates scholarly judgment to metadata, keywords,
A/B grades, journal prestige, a model, or retrieved text. Existing CCTV entries,
locked 1–23, HOLD/REJECT decisions, grades, ranks and statuses remain protected.
Individual dossier attestations remain required in this conservative first version;
a later rule-based standing authorization needs its own independent review.

## Evidence and governance contract

A dossier contains live provenance receipts (accessible HTTPS URL, immutable content
hash, retrieval time, HTTP status), named authors, complete exact publication dates,
explicit 2026 route and earlier announcement/publication/fieldwork history. Include
bilingual descriptions, limitations, field context, reason for selection and an
attributed significance justification. Independent source reconciliation must cover
DOI/title/date and substantive claims, not another lookup in the same API. Record
online/print differences; 2025 online/2026 print and future/tentative dates block
this first gate version even when another route might merit individual review.
DOI-less official field announcements need individual human review in this version.

Every check named in `publication.CHECKS` requires an editor attestation and evidence
reference bound to the entire dossier SHA256. Missing/unresolved data fails closed.
Check retractions, journal reliability, twin DOI/project identities against the
whole archive and earlier ledger, full-text facts, eligibility/history, interpretation,
bilingual quantities/uncertainties, sensitive locations, community consent, geographic
outliers and balance. Do not publish coordinates or personal/community-restricted
information even if a source already exposes it. Non-numeric translation checking
requires a qualified human. No fixture can satisfy live evidence requirements.
Attestations are audit records, not cryptographic proof or independent verification
by the program. Repository review/protection must prevent collector self-approval.

## Transaction and integration blocker

The current QA requires formal-list/ranking crosswalk consistency. Automatic rank
editing is prohibited. Consequently **no new formal entry can ship through this
version** until an independently reviewed integration procedure resolves that
constraint. The future transaction must allocate an unused stable ID (never reuse
29), add a bilingual page, sidebar, formal table, map and counts, and update the QA
crosswalk in one PR, with separately approved ranking handling. Run source/rendered
QA, mutation/bilingual tests, deterministic builds, duplicate and privacy checks on
the exact PR head; discard stale approval after any dossier/content change. Merge
only after independent editorial review and successful CI. Never bypass a QA
failure by regenerating inventory. The collector cannot edit academic files.

## Activation procedure

1. Keep `enabled: false` and empty authorizations during this draft PR.
2. Run `workflow_dispatch` for monitor, review and audit on GitHub-hosted runners.
   Inspect each run, source diagnostics, state persistence/repeat runs and privacy.
   Resolve terms/permissions for institutional feeds; obtain real independently
   verified **new** 2026 records. Metadata retrieval alone is insufficient.
3. Independently review code, policy, regression tests, privacy safeguards and the
   publication integration/ranking procedure. Record review and editor identity in
   a separate reviewed PR. Configure branch protection and a scoped GitHub App if
   future transaction-PR creation is enabled; do not grant collector main write.
4. Supply authentic review/standing-authorization/live-verification/integration
   references and hash-bound dossier attestations. No placeholders or self-approval.
5. Only that later reviewed policy PR may switch formal publication ON. This PR
   does not implement a merge-capable publisher. Schedules have a separate repository
   variable `MONITORING_SCHEDULES_ENABLED`; enable only after all manual smoke tests.

## Exceptions, corrections and rollback

Exceptions always need individual responsible-editor approval in a review PR with
bilingual proposed changes, affected IDs, evidence and rationale. Never weaken a
gate field to pass an exceptional case. Weekly Friday review is a queue, not a
human decision. To stop, disable schedules/revoke App access and keep policy OFF.
Revert the entire publication transaction through a reviewed PR; keep IDs reserved
and retain provenance and decision references. State rollback requires a reviewed
recovery commit on `monitoring/state-phase2b`, preserving newer observations and
replaying with overlap; never force-push state or discard evidence to retry.
