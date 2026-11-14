# Initial editorial QA results

Validated 2026-11-14 against academic corpus `f86ffae6a66913f701920d95d79310729b9563e9`.

## Executed checks

- 20 isolated mutation/regression tests: passed.
- Existing bilingual/Markdown structural checker: passed.
- Source editorial QA: 0 errors, 47 human-review warnings.
- Quarto 1.11.9: full website render passed (48 documents, including the new QA documentation).
- Rendered editorial QA: 0 errors, 47 human-review warnings; local targets, assets and fragments checked.
- Existing academic source, grades, statuses, conclusions and ranks: unchanged.

## Corpus consistency

The crosswalk contains 44 ranked candidates: 16 CCTV, 17 Additional, and 11 Under review. The formal list and map contain 33 projects, with 33 matching mobile selector entries. Discovery page 29 remains Under review, retaining its stable ID. Stonehenge remains an unranked research update. No project was promoted, held, rejected, regraded, or reordered by this work.

## Findings awaiting academic interpretation

One `reanalysis-label` warning: `discoveries/31-tampa-bay-migrant-potters.qmd` lacks the explicit bilingual Reanalysis label already present in ranking. This report proposes no change to its status, grade or conclusions.

The remaining 46 warnings are Arabic-number differences between explicitly labelled Chinese/English paragraphs. They are screening findings, **not 46 verified factual errors**. Spelled-out English numbers, Chinese number words, centuries, implicit range units and summaries account for some differences. For example, “5–8” versus “five to eight” is not a substantive disagreement. Publication-based human comparison is required before proposing any correction, particularly in locked pages.

| Source | Numeric review warnings |
|---|---:|
| `discoveries/01-wonderwerk-fire.qmd` | 1 |
| `discoveries/02-yunxian-homo-erectus.qmd` | 3 |
| `discoveries/03-megalopolis-wood-tools.qmd` | 1 |
| `discoveries/04-denisovans-yunnan.qmd` | 1 |
| `discoveries/05-oldest-dog-genomes.qmd` | 1 |
| `discoveries/06-romito-genetic-disease.qmd` | 1 |
| `discoveries/09-troy-agora.qmd` | 1 |
| `discoveries/10-alexandria-tigris.qmd` | 3 |
| `discoveries/13-urartian-irrigation.qmd` | 1 |
| `discoveries/16-iliad-mummy.qmd` | 1 |
| `discoveries/17-amazon-earthworks.qmd` | 1 |
| `discoveries/19-celtic-ancient-dna.qmd` | 1 |
| `discoveries/20-sulawesi-rock-art.qmd` | 1 |
| `discoveries/22-hittite-royal-archive.qmd` | 1 |
| `discoveries/24-sheg-xdaltthi.qmd` | 2 |
| `discoveries/25-huitzo-tomb-10.qmd` | 3 |
| `discoveries/26-plain-of-jars-death-jar.qmd` | 4 |
| `discoveries/28-font-major-rock-art.qmd` | 1 |
| `discoveries/29-etowah-cacao.qmd` | 1 |
| `discoveries/30-roman-iberia-adna.qmd` | 2 |
| `discoveries/32-karatau-palaeolithic.qmd` | 1 |
| `discoveries/33-widgingarri-shelter.qmd` | 1 |
| `discoveries/34-bongal-boats.qmd` | 3 |
| `ranking.qmd` | 2 |
| `under-review.qmd` | 8 |

Reproduce complete locations and quantity lists with the commands in `QA.md`; JSON reports are also uploaded by the PR workflow. No warnings have been suppressed or used to change academic text.

## Validation limits

The checker validates consistency and observed metadata, not publication truth, 2026 eligibility, appropriate grades, scholarship, translation equivalence or portfolio balance. Explicit human approval remains required. External citation reachability and browser screenshot capture were not part of this change's validation. The new GitHub Actions workflow has been checked locally through its underlying commands; a hosted Actions run is not claimed.
