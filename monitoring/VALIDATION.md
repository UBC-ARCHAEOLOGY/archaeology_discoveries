# Phase 2A validation and limitations

Tested 2026-11-14 against latest main at
`c963aa1e11f77c57b35db48a787e3aedb386a860`. This is a software foundation and
bounded evidence replay, not academic validation or a completed global scan.

## Results

| Check | Result |
|---|---|
| Monitor standard-library unit tests | 21 passed |
| Existing editorial mutation tests | 26 passed |
| Existing bilingual/Markdown structure checker | Passed |
| Source editorial QA | 0 errors, 42 review warnings |
| Quarto 1.11.9 render | Passed; 49 pages, monitoring/scratch excluded |
| Rendered editorial QA | 0 errors, 42 review warnings |
| Existing visual QA script | Completed, 46 desktop/mobile screenshots in isolated scratch output |
| Existing internal/external link checker | 0 internal broken, 0 observed external 404, 148 external unreachable |
| Offline reproducibility | Byte-identical JSON, CSV and both Markdown outputs on repeated replay |
| Academic-content preservation | Unit test compares protected source bytes before/after replay; branch diff contains no protected academic source changes |
| Bounded live API probe | 12 enabled sources unavailable at proxy; 0 records; state remains `{}` |

The external result does not prove link health: unreachable links could not be
checked. The 42 existing editorial warnings remain visible, including the Tampa
Bay Reanalysis-label warning and numerical/translation heuristics; none was used
to change academic content or inventory. Source-rewriting caption cleanup and
image-fetch scripts were deliberately not run, following `AGENTS.md`.

## Bounded sample and duplicate evidence

`fixtures/sample.json` contains 17 repository-sourced candidate records, plus
four controlled duplicate observations. Every original record links to its
repository source at the baseline commit, with a content hash and reproduced
primary source URL/DOI when present. The duplicate observations explicitly say
`controlled_duplicate_of_repository_excerpt`; they are tests, **not independent
corroboration**. There are no invented candidate authors, DOIs or institutions.

Replay produces **21 observations, 17 proposed identity groups and 10 duplicate
edges** (multiple bases may connect the same pair), with four extra observations
retained inside their groups. DOI, URL, exact normalized title and curated project
identity all have exercised match paths. Unit tests also cover transitive matches,
conflicting project DOIs, missing identifiers, and distinct studies at one site.
The CSV contains 21 evidence rows, not 21 distinct discoveries.

Classification proposals by group: 12 first substantive publications, three first
public announcements, one Reanalysis, one unresolved (Pabalugala). These derive
from explicit replay claims and are **not confirmation of firstness or scholarly
significance**. The sample largely replays existing archive content, so it must
not be counted as new candidates added to the formal list. All 17 groups remain
metadata-unverified. DOI suffixes and repository bibliographies are not themselves
independent evidence of publication dates.

The sample includes settlement/landscape, burial, production, maritime, writing,
rock-art and Indigenous-governed contexts. Tampa Bay exercises Reanalysis.
Bongal preserves its 2021 earlier publication; Widgingarri preserves earlier work
and the 2022 re-excavation; Font Major preserves prior discovery/publication
history. Other history gaps remain flagged. Earlier-history extracts contain
attributed background rather than a verified exhaustive bibliographic search.

## Coverage gaps

Lexical geographic tags count unique groups: South Asia 1, Central Asia 1,
Africa 2, Southeast Asia 3, Australia 1, wider Pacific **0**. These are coverage
indicators for this selected sample, not a global survey or complete regional
classification. Other regions are not exhaustively tagged by the priority-region
dictionary. New Guinea, Melanesia, Micronesia, Polynesia, much of South/Central
Asia, and large areas of Africa have no representative sample record. Indigenous
community leadership cannot reliably be inferred from a title or abstract.

The registry has eleven specialist journals, broad Crossref/OpenAlex metadata,
and eight official institution leads. Institutional polling is **not implemented
or enabled** without verified permission/stable feeds. No enabled institutional
RSS feed is claimed. OpenAlex is disabled pending API access/credential review.
Local-language journals, regional grey literature, inaccessible reports, delayed
metadata deposits, paywalled abstracts and community-restricted knowledge remain
major gaps. More registry entries do not imply those sources have been searched.

## False positives and ambiguity

- A 2026 bibliographic date is not proof of a first/substantive discovery. Live
  metadata without an explicit firstness or legacy claim stays unresolved.
- An online-2025/print-2026 control is screened outside 2026. The parser retains
  both dates rather than treating the print issue as the first publication.
- Synthetic physics and undated press-story controls in
  `fixtures/screening_controls.json` demonstrate off-topic and date uncertainty
  flags. They are deliberately synthetic, excluded from the 17-candidate report,
  and contain no bibliographic identifiers or scholarly results.
- India/Indonesia word-boundary regression test prevents one known lexical
  geographic false positive. Generic keywords, affiliations, historical place
  names and translated titles can still misclassify geography or themes.
- Four intentionally repeated observations were detected. Title/project matches
  are review suggestions, not proof that separate publications are the same study.
- No measured live precision/recall is reported: the network yielded no live data,
  and a curated replay cannot estimate a global discovery false-positive rate.
- Reported significance excerpts are repository assessments. The generated
  importance question is a review prompt, not a score or verified academic judgment.

## Operational boundary

Manual `workflow_dispatch` only; default offline; artifacts only; `contents: read`.
No schedule, repository write permission, deployment, automatic promotion or formal
candidate synchronization. The render exclusion prevents monitoring reports from
becoming site pages. Phase 2B scheduling awaits explicit human approval.
