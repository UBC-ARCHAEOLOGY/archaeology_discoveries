# Beijing weekly dates and reader-highlighted reporting

Base: latest main 21ac031ae28c763b8cd62ef6ebcd30c443513999.
Owner requested Beijing time and asked why three important media reports were not
represented. Existing permission to fix/merge/render/deploy the homepage persists;
no new promotion or ranking approval is inferred from that request.

## Timezone correction

Active homepage/history prose, Python day/window and browser Intl day/window now
use **Asia/Shanghai (Beijing time, UTC+08:00)**. Phase 2B's America/Vancouver
monitoring configuration is unchanged and remains inactive.

A label-only substitution would be incorrect. Verified website dates were converted
from exact UTC deployment-success receipts, now stored as optional structured
`website_date_evidence.published_at`. When present, validation requires an exact UTC
instant and a matching Beijing calendar date; arbitrary naive timestamps fail.

| Verified deployment success (UTC) | Beijing website day |
| --- | --- |
| 2026-11-09T19:49:26Z, run 42686436717 | 2026-11-10 |
| 2026-11-14T22:00:57Z, run 43645480011 | 2026-11-15 |

The six frozen baseline recording dates are preserved as historical records; they
have no website date and never enter the weekly window. Source publication and
archaeological dates are unchanged. Reviewed recording dates are normalized to the
Beijing date of registry preparation. The homepage digest remains a seven-calendar-
day window, including today, not a seven-day news-publication filter.

## Coverage findings and correction

- Cannabis NYT report: existing Tunnug 1 record in `under-review.qmd`; HOLD remains
  in effect. No new judgment of ingestion or promotion. NYT citation itself was
  absent from the public source navigation.
- Celtic Science report: subject already formally included as ID 19, rank 25.
  The Science news link was absent. Existing two Nature references and interpretations
  remain unchanged; no second discovery or automatic ranking increase.
- Neanderthal NYT report: true coverage gap. It covers **Abric Romaní** woodworking
  and **Shanidar A** trauma, not the existing Greek Marathousa 1 project. Register
  source leads only in `sources.qmd#reader-reports`, with separate original papers,
  and no formal IDs, candidate decisions, grades or ranks. The publisher explicitly
  leaves accident versus intentional violence unresolved. No “proven murder” claim.

The new bilingual source crosswalk links all three supplied reports to their actual
archive record or distinct research leads; homepage has a direct link to it. The
locked discovery pages and all current academic decisions are unchanged.

## Evidence inspected and access limits

- NYT originals: direct access failed. Search indexing and Cambridge's institutional
  media index confirm the November 3 wood/trauma reporting; an accessible Business
  Times NYT-attributed republication identifies both projects. Bern/CU institutional
  indexing corroborates the cannabis report. No paywall bypass or full NYT reading
  claimed.
- Science news: direct 403. Indexed title and topic corroborated; underlying Celtic
  study independently matched through Gothenburg's 4 November release and existing
  Nature DOI 10.1038/s41586-026-11198-9. No full news-text verification claimed.
- Abric Romaní: accessible full paper at https://pmc.ncbi.nlm.nih.gov/articles/PMC13644747/,
  DOI 10.1126/sciadv.aeh2287, online 7 October 2026. Important scope limit: 597 wood
  specimens are not 597 tools; paper distinguishes a smaller anthropogenic subset.
- Shanidar A: https://www.nature.com/articles/s41598-026-69193-z and publisher synopsis
  https://www.natureasia.com/en/info/press-releases/detail/9463, plus St John's Cambridge
  institutional account. Paper published 15 October 2026; synopsis dated 16 October.
  Excavation dates and comparative-firstness need fuller editorial review before
  any candidate dossier or formal inclusion. These two projects must be assessed
  separately, including prior literature and 2026 eligibility.

The coverage gap is not evidence that media prominence alone establishes inclusion.
The archive is curated and its disabled metadata monitor does not provide complete
NYT/Science reporting intake. Source mapping improves discoverability without
changing 33 formal entries / 44 ranking positions or existing interpretations.

## Observed local verification

22 registry tests (including Beijing midnight and receipt-date mismatch/naive-time
rejection), 26 editorial mutation tests and 65 offline monitoring regressions passed.
Quarto 1.11.9 rendered 50 pages. Source/rendered editorial QA: 0 errors/42 existing
warnings; bilingual checks passed. Internal links: 0 broken; local external checks
returned 0 observed 404/160 proxy-unreachable URLs, not verified source health.
Desktop/mobile home/history checks passed, including Beijing boundary and eight-day
expiry simulations. Separate source-crosswalk desktop/mobile checks passed with no
overflow/page errors and linked report titles; key screenshots inspected. New anchor
scroll margin avoids clipping its heading under mobile navigation. Generated files
are excluded from commits. Exact-head hosted evidence and release receipts will be
recorded in the PR.
