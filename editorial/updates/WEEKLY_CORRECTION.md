# Owner clarification: weekly homepage digest

Base: latest main `197f55b3c39989fc57289963aebc8beb3e3a415f`.
The owner's final clarification specifies **one week**, superseding the earlier
“two weeks” message, and explicitly authorizes merge/render/deployment.

- `index.qmd`: replace Current coverage in place with the exact bilingual weekly
  heading; remove the mistaken pre-map baseline card block.
- `scripts/updates.py`: only reviewed records with verified website dates in the
  seven Vancouver calendar dates including today; category grouping/newest-first;
  ranking and other-site categories; no baseline/proposal padding or minimum.
- `updates-window.js`: expire old records at viewing time without network reads,
  writes, scheduled Actions or new publication authority. No-JS fallback labels
  the build's date interval. New entries still need human review and site rebuild.
- `updates.json`: five real published events, sourced to successful Pages runs
  42686436717 (November 9, four records) and 43645480011 (November 14, history launch).
  Source commits identify the actual prior changes; deploy logs establish publication.
  Earlier reference added to a page is not a newly published paper.
- `scripts/editorial_qa.py`: retired required 16/17 coverage prose checks because
  that block was explicitly removed; mandatory bilingual map total, formal list,
  ranking totals/status/grades and all other checks remain. Test fixture includes
  new static JS resource so link checks retain meaning.
- `scripts/test_updates.py`: 20 tests, including inclusive seven-day boundaries,
  stale/future/baseline/proposal exclusion and review requirements for new categories.
- Visual checks cover new position, linked cards, mobile history navigation and a
  simulated eight-day clock advance (all old cards disappear, empty states shown).

Discovery/ranking/grade/status sources and six original baseline records are not
edited. Existing academic approval and default-OFF monitoring controls remain.
Source quotations/review references are structural checks, not authenticated approval.
Missing logged events do not prove no changes; scholarly duplicate/mirror detection
still needs human review. Local external health checks remain network-limited.

Observed local checks: 20 registry tests, 26 editorial mutation tests and 65 monitoring
offline regressions passed; bilingual checks passed; source/rendered editorial QA
0 errors/42 existing warnings; Quarto 1.11.9 rendered 50 pages. Internal links: 0
broken; 0 observed external 404, 150 external unreachable via the cloud proxy (not
verified healthy). Desktop/mobile visual/navigation checks and eight-day expiry
simulation passed; key screenshots inspected. Generated files remain uncommitted.
Exact-head hosted checks and final deployment evidence will be recorded in the PR.
