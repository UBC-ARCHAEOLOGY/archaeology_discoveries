# Numeric-warning triage | 数字警告人工审阅说明

**Scope:** PR #1 Editorial QA Refinement Pass.  
**Status:** Screening and prioritization only; no academic source wording, ranks, evidence grades, or candidate statuses have been changed.

## Verified starting point

At PR head `ee177c2`, the hosted CI source report contained **0 errors and 47 warnings**: one missing bilingual Reanalysis label for Tampa Bay, and 46 bilingual Arabic-number differences.

The first normalization pass (commit `8d7f3fa`) reduced that to **0 errors / 45 warnings** (44 numeric warnings plus the unchanged Tampa Bay label warning). The 44 remaining numeric warnings were mechanically classified as:

| Heuristic category | Count at 8d7f3fa | Review policy |
|---|---:|---|
| `spelled-number-or-scope` | 19 | Check English number words (e.g., *sixty-six*, *seventh*) and prose scope before suggesting any change |
| `unequal-detail-or-context` | 18 | Compare named quantities, dates, examples, and omitted context; don't require both language paragraphs to contain identical incidental detail |
| `unit-or-range-context` | 7 | Check quantities with scales, ranges, or period notation that may be equivalent despite different surface forms |

Subsequent commits extend recognition to `ka`/`Ma` next to Chinese characters; the latest CI JSON is the authoritative report for the resulting count. **The categories are heuristic triage hints, not verified outcomes.** All remaining discrepancies stay visible; no warning has been suppressed.

## Latest verified hosted CI result (commit `02ff4fc`)

The GitHub-hosted Editorial consistency QA workflow **passed** at commit `02ff4fc160814b3bd13207e9a595909dbdcc2731` (run `43625678174`):

- **0 structural errors**
- **42 review warnings total** (41 numeric screening warnings and 1 previously identified Tampa Bay bilingual Reanalysis-label warning)
- Numeric categories: **19** `spelled-number-or-scope`, **18** `unequal-detail-or-context`, **4** `unit-or-range-context`.
- The two Widgingarri warnings for range-unit syntax disappeared after handling English `between roughly 55 and 37 ka` and `ka` adjacent to Chinese characters.
- Academic source paragraphs, grades, candidate statuses and ranks remain unchanged by this PR.

The warning decrease from 47 to 42 reflects **better parsing**, not correction of five archaeological statements. The 41 remaining numeric warnings still need human screening against the original paired text and primary literature where necessary.

## Examples inspected against source paragraphs

- **Likely false positive: Shég’ Xdaltth’í’, page 24**, Chinese `66个AMS年代` vs English *Sixty-six AMS radiocarbon dates*. Different numeral notation, no substantive disagreement; retain as a warning unless a future audited number-word parser is added.
- **Likely false positive: Bongal, page 34**, Chinese `公元7–8世纪` vs English *seventh- to eighth-century*. Mixed Arabic/spelled ordinal notation; do not alter the archaeological chronology merely to make machine counts match.
- **Likely false positive addressed in parser: Widgingarri, page 33**, shared unit ranges such as `约55–37 ka层段` vs English *55 and 37 ka*. Units adjacent to CJK characters previously failed detection. The parser now supports explicit shared-unit ranges without inferring chronology from context.
- **Unequal detail requiring editorial reading: Yunxian, page 02**, Chinese mentions the Dmanisi range `185万—178万年前`, while the matching English paragraph describes the benchmark without reproducing those values. This is not a contradictory date claim, but whether to harmonize explanation/detail is an editorial question. Page 02 is locked: do not change it from QA alone.
- **Unequal detail requiring editorial reading: Roman Iberia, page 30**, Chinese says `跨31处遗址` while English uses *a large multi-site archaeogenomic synthesis*. The explicit count is missing in that English paragraph, not contradicted; harmonization is optional editorial work.
- **Likely false positive: Etowah, page 29**, Chinese `20世纪中期` vs English *mid-twentieth-century*. The expression differs; the archaeological curation claim remains the same.

## Triage order

1. **Potential conflicting measurements, dates, uncertainty or sample sizes** where *both* languages give different explicit values for the same claim: high priority, verify against primary publication.
2. **Explicit values present in one language but absent in the other**, especially substantive dates, populations, sizes, MNI or percent estimates: medium priority; assess whether omission harms bilingual equivalence.
3. **Spelled numbers, equivalent scales, shared suffix ranges, abbreviated chronology**, and other presentation differences: generally lower priority; keep visible until verified but do not treat as factual errors.

Use the JSON `review_category` and `review_categories` fields, but inspect the paired source sentences. A numeric multiset is not a translation model. No category grants permission to auto-edit academic content or closed V2.2 entries.

## Unresolved academic/editorial metadata

**Tampa Bay (#31):** The ranking marks this as `Reanalysis`, but the discovery page lacks an explicit `Reanalysis / 旧材料再分析` field. This remains an actionable **editorial** warning. Add the bilingual label only through an explicitly approved content PR; this QA-only branch must not silently make that scholarly classification change.

## Boundaries

The QA system still does not:
- independently verify a DOI, publication claim, archaeological interpretation, or date against external literature;
- validate the geographical coordinates of SVG markers (it checks membership, link identity and marker class);
- enforce human approval against simultaneous edits to academic pages and the observed inventory;
- determine whether a candidate deserves PROMOTE, HOLD, REJECT or a particular rank.

Human academic review, independent source checking and GitHub branch/PR governance remain necessary.
