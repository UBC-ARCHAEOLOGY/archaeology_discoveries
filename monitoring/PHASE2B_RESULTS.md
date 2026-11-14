# Phase 2B round-one results (historical)

Current focused third-round assessment and results are in
[review-round3/RESPONSE.md](review-round3/RESPONSE.md); prior second-round results
remain in [review-round2/RESPONSE.md](review-round2/RESPONSE.md). The 38-test figures below
describe original head `2def086`, not the revised implementation.

Date: 2026-11-14. Verified base:
`3d518218d4825a325cef60269c6d3cea4bc2cf93`, latest origin/main including PR #2.
No automatic formal publication, merge, schedule activation or main write occurred.

| Check | Observed result |
|---|---|
| Monitoring offline regression | 38 tests passed (21 existing, 17 new) |
| Editorial mutation regression | 26 tests passed |
| Bilingual/Markdown checker | Passed |
| Source editorial QA | 0 errors, 42 existing review warnings |
| Quarto 1.11.9 render | Passed; 49 pages |
| Rendered editorial QA | 0 errors, 42 existing review warnings |
| Python compile check | Passed |
| Live monitor full scan, local cloud runner | 12/12 enabled sources `proxy_403`, zero observations, no completed watermark |
| Local review and audit smoke modes | Completed, formal archive 33, ranking inventory 44 |
| Git persistence integration | Temporary bare remote roundtrip passed; stale-parent write rejected; main unchanged |
| Repeat runs and replay | Deterministic replay and idempotent observation ledger passed |
| Atomic write failure | Previous state preserved on replacement failure |
| Privacy output test | Raw source title/coordinates/email/instructions/DOI absent from safe ledger |
| Schedule checks | All three crons use America/Vancouver; PST/PDT offsets checked; schedule variable required |
| Formal gate | Committed OFF manifest, no editors or authorized dossiers; adversarial controls fail closed |
| GitHub-hosted workflow_dispatch smoke tests | BLOCKED: cloud GitHub REST/GraphQL requests return Forbidden; no hosted run success claimed |
| Official institutional feeds and first-announcement verification | BLOCKED: no verifiable endpoint/permission/date semantics established through restricted network |
| New independently verified 2026 discoveries | ZERO; no live primary verification or production eligibility claimed |

Gate tests cover DOI/twin-title duplicates, offline and metadata-only data,
2025-online/2026-print conflict, tentative/future/partial dates, missing authors,
retractions, quality concerns, contradictory evidence, sensitive Indigenous-site
locations, bilingual mismatch, geography outliers, identity conflicts, protected
existing/ranking changes, missing evidence attestations, and changed dossier hashes.
These are explicitly synthetic controls, not real verified discoveries. Passing
software tests is not approval of a publication policy or archaeological claims.

Required render refreshed the untracked generated `docs/` output and link reports;
these are not included in the implementation commit. Screenshots remain untracked.
Tracked academic pages, map, ranking, inventory, status and grade decisions are
unchanged. `.gitignore` remains unchanged. No source-rewriting caption/image-fetch
scripts were run. Existing QA warnings remain visible, including Tampa Bay's
Reanalysis-label warning; none were silently repaired or reclassified.

## Before production activation

- Obtain real GitHub-hosted results for monitor/review/audit, including repeated
  state restore/persist, inspect reports and source failures, and test outage queue.
  Workflow dispatch requires the workflow file on default branch first. A PR-only
  workflow cannot be dispatched with --ref; any later infrastructure-only merge
  must keep schedules and publication OFF and is not production approval. Keep the
  schedule switch OFF until then. The local CLI API failure does not establish
  GitHub-hosted source connectivity, and no runner-side fix is claimed as verified.
- Review regional/local-language official feeds' access/license/robots/community
  permissions and first-announcement provenance; implement and test authorized
  live polling before claiming those sources are covered.
- Add controlled primary-source verification and privacy-reviewed bilingual
  candidate dossiers. The public hash queue intentionally withholds unreviewed
  source text/URLs, so full substantive candidate-report publication remains pending.
- Independently review the formal gate and standing-authorization proposal; resolve
  rank-coverage integration in a separately approved procedure. There is no connected
  archive-writing/merge publisher in this draft. Formal activation is unavailable
  until that work and live verified new records exist.
- Apply branch protections, verify token/issue permissions on hosted runners, then
  follow `PHASE2B.md` / `PUBLICATION_POLICY.md`. Do not enable formal publication
  merely because scheduled operational reports work.
