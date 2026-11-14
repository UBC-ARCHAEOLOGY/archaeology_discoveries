# PR #6 independent review — focused response (2026-11-14)

Reviewed source: 0e13dd736e6e173614e82dca7a1d6a07f6be9fca.
The report is evidence/recommendations, not authorization. The owner separately
requested fixes, merge, render and deployment. No second independent academic
approval is claimed by these implementation checks.

| Finding | Correction and verification |
| --- | --- |
| P1 misleading “added” labels | `scripts/updates.py`: state-specific Existing archive entry / Existing publication reference / Existing research note labels for historical baseline; reviewed additions describe website actions only. Tests assert labels differ by state. |
| P1 baseline review bypass | `editorial/updates/baseline-manifest.json`, `scripts/updates.py`: fixed six IDs, full-record hashes and recording date. Tests reject seventh/replacement baseline, changed known record/date, and proposal-to-baseline or unapproved-reviewed conversion. |
| P2 recording date prominence | Baseline cards have no headline time; homepage omits recording dates; history places registry date in muted secondary metadata. Baseline group uses registry order, not date chronology. Tests assert markup; Playwright checks desktop/mobile. |
| Cross-category/date duplicates | Page + canonical source identity excludes category/date. Regression tests reject changing either to repeat an event. Conservative same-source rejection is documented; mirrored/semantic duplicates still need human review. |
| Homepage density | Compact cards omit full date tables, retain bilingual descriptions and source/page links, and link to stable history anchors for full dates. Responsive 2/1-column design preserved. |
| Archaeological precision | `updates.json` and discovery/ranking/grade/status sources unchanged. No date precision upgraded from this report alone; historical web dates remain unknown. |
| Approval authenticity | References are structural evidence, not authenticated decisions. Manifest/code changes still require repository human review; branch protection is not asserted. |
| External link uncertainty | Local proxy failures do not establish link health or failure. Report separately from successful internal-link checks. |

The six historical records remain a one-time bootstrap, not six newly discovered
projects or proof of the six most recent past website changes. Monitoring proposals
remain non-public; no production monitoring, persistent-state/Issue automation or
formal publication controls are activated. See `REVISION_VALIDATION.md` for observed
results and GitHub PR checks for independently hosted execution.
