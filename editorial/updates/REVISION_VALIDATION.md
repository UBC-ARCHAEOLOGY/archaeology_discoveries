# Focused revision validation — 2026-11-14

This supersedes the initial 13-test results for the revised implementation; earlier
`VALIDATION.md` describes the initial reviewed commit. Owner has explicitly requested
merge/render/deploy after corrections. No new independent reviewer approval is claimed.

- Registry regression: **18 passed**, including frozen baseline identity/content/day,
  proposal conversion, state-specific labels/date hierarchy and cross-category/date duplicates.
- Existing editorial mutation suite: **26 passed**. Monitoring offline suite: **65 passed**.
  State-store messages in tests refer to temporary local Git fixtures, not hosted writes.
- Bilingual structure: passed. Source/rendered editorial QA: **0 errors / 42 existing warnings**.
- Quarto **1.11.9**, **50 pages**, including permanent history; isolated source snapshot checked.
- Rendered registry identities/links: passed. Full link checker: **0 internal broken**,
  **0 observed external 404**, **149 external unreachable** due current cloud network/proxy.
  The latter are unresolved health checks, not verified source failures or successes.
- Desktop 1440×1000/mobile 390×844: 2/1 columns, no horizontal overflow or page errors,
  mobile history navigation passed. Eight screenshots produced; desktop viewport and
  mobile viewport/card inspected. Baseline has no headline time; compact home has no
  date tables, history retains full tables and secondary recording date.
- Discovery sources, methods, formal list, rankings, HOLD decisions, inventory and
  original six registry records unchanged. **33 formal entries / 44 ranking positions**.
- Monitoring schedules, state/Issue automation and formal-publication switches untouched.

GitHub-hosted exact-head results will be linked in PR #6 before merge. Deployment
is a separate main-push workflow; its success must be checked before claiming the
published website synchronized. No branch-protection enablement is claimed.
