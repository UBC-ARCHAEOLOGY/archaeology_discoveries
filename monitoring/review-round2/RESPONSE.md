# PR #4 — response to independent Grade B review

We accept the report's scope: **minor revisions and re-review of default-OFF
infrastructure**, not approval of Issue #3 production completeness. The full
owner-supplied report is preserved in [INDEPENDENT_REVIEW.md](INDEPENDENT_REVIEW.md).
Original reviewed head: `2def086a9f9796fe483be415e653ccc1ffaf4f30`; main/base remains
`3d518218d4825a325cef60269c6d3cea4bc2cf93`. Revisions stay on
`monitoring/phase2b-scheduled-review`, the existing Draft PR #4 branch.

本轮不修改考古结论、证据等级、正式名单或排名。不合并、不启用生产监测或自动正式发布。
对仓库保护、变量及凭据的要求与已验证事实分别列明，不把文档建议写成已落实控制。

Line locations below refer to this revision's source; function and test names are
stable navigation points if documentation-only follow-up changes move line numbers.

## 1. Scholarly observation identity — corrected

**Original locations:** `operations.py:166–176`, `monitor.py:68–76`, `PHASE2B.md:71–78`.

**Changes:** [operations.py](../operations.py), `scholarly_projection` (line 191)
and `update_ledger` (line 213), replace the all-fields hash with projection version
2. DOI/URL, title, selected author metadata, publication dates, claims, earlier
history, work type, and correction/retraction relations enter identity. `indexed`,
`deposited`, citation/reference counts, reference payloads, score, retrieval date,
source ID and raw provider payload do not. Cross-source sightings merge `source_ids`
and last-seen while preserving first-seen. Meaningful revisions remain separate
observations grouped by hashed identity edges. The Phase 2A raw adapter is retained
for replay evidence; its raw payload no longer controls Phase 2B scholarly identity.

**Tests:** `test_round2.IdentityRevisionTests` (line 46):
`test_indexed_deposited_counts_references_score_and_source_do_not_create_revision`
and `test_scholarly_title_abstract_dates_authors_and_retractions_preserve_revisions`.
The first yields one observation despite provider churn; the second retains two
revisions for each title/abstract/date/author/retraction/correction change.

**Limit:** This is bibliographic/claim revision tracking, not evidence that a
revision creates a new archaeological discovery. Old schema-1 hashes cannot be
losslessly recomputed without original evidence; no silent migration is offered.

## 2. Three eligibility pathways — corrected

**Original location:** `publication.py:50–61`.

**Changes:** [eligibility.py](../eligibility.py), `publication_dates` (line 54)
and route-specific validation (line 65), integrated by [publication.py](../publication.py)
`evaluate` (line 24). The selected route has an exact structured schema and
source-ID references to dossier receipts:

| Route | Required structure |
|---|---|
| First public announcement | Exact 2026 announcement date; separately dated discovery/fieldwork; confirmed-firstness marker; announcement/context sources; earlier-announcement search |
| First substantive publication | Separate online, print and earliest publication dates; earliest reconciled date in 2026; peer-review evidence; dated/staged prior publications; history search; supported substantive increment |
| Reanalysis | Publication reconciliation/history; identified legacy collection/data with original dates and sources; exact 2026 analysis date before publication; supported important question and major interpretive gain; explicit `major_new_interpretation` |

Unknown/partial/future dates and wrong-route fields fail; legacy top-level
`publication_dates` is rejected to avoid conflicting parallel date structures.
Prior history may be empty only with a supported search. No year is padded with
an invented month/day. Human hash-bound attestations remain required. The final
gate still conservatively requires a DOI; DOI-less official announcements require
individual exception review pending an approved deduplication procedure.

**Tests:** `test_round2.RouteAndProvenanceTests` (line 83), including deletion of
every required field for each route; announcement vs bibliography; separate
online/print and 2025/2026 conflict; missing histories/increment; legacy provenance,
analysis date and gain; valid complete controls for all three routes. Prior
`GateTests` were updated to the new contract and still reject adversarial data.

**Limit:** Structured assertions and receipt references establish completeness,
not firstness, scholarly truth or significance. No real candidate was qualified.

## 3. HTTPS provenance loophole — corrected

**Original locations:** `publication.py:62–70`, `monitor.py:31–36`, policy lines 21–29.

**Changes:** `eligibility.https_provenance_url` (line 10) checks the **supplied**
URL's HTTPS scheme directly. HTTP is not upgraded. Receipt ID, original URL,
SHA256, timezone-aware retrieval timestamp and integer 200 status are checked
as one dossier-bound structure. Credentials, local/private hosts, whitespace,
invalid ports, naive timestamps and future retrieval dates fail. Generic
`monitor.url` remains an identity normalizer only; it is not a provenance checker.
[PUBLICATION_POLICY.md](../PUBLICATION_POLICY.md) explicitly distinguishes an
attested HTTP receipt from a live fetch by the gate.

**Tests:** `test_https_receipt_is_raw_scheme_not_generic_normalization` verifies
HTTP rejection despite successful generic normalization; malformed URL controls;
`test_receipt_hash_time_status_and_ids_bound_to_dossier` covers receipts/approval
invalidation. All use synthetic receipts, never invented verification of real URLs.

**Limit:** The pure gate does not fetch HTTPS or independently verify receipt
content. Responsible-editor verification and authentic live evidence are still
mandatory; no archive writer is connected.

## 4. Restored state and absent branch protection — code corrected; deployment controls pending

**Original locations:** `operations.py:93–102`, `state_store.py:28–39`, guide lines 59–69.

**Changes:** [state_schema.py](../state_schema.py) implements schema 2 plus taxonomy
SHA256, exact nested fields/types, enabled-source allowlists, tag dimensions/labels,
hash lists, dates/order, collector category, pending windows/cursors, run keys and
digests, diagnostics and parent commit. Duplicate JSON keys, unknown fields and old
schemas fail closed. Removed `latest_report` entirely from durable state; reports
are regenerated instead of trusting restored prose. [state_store.py](../state_store.py)
`remote_payload` (line 35) checks blob size before reading it; `restore` validates
before atomically replacing local state; `persist` validates both histories and
rejects observation/run loss or watermark regression as well as stale parents.

**Tests:** `test_round2.StrictStateTests` (line 152) injects unknown source IDs,
valid-dimension invalid labels, extra dimensions/top-level/report fields, malformed
hashes/dates/classifications/windows/runs/parent, wrong taxonomy and legacy schema,
unsafe diagnostics, duplicate JSON keys and oversized remote blobs. Invalid restore
leaves the previous file unchanged. Existing real-bare-Git roundtrip/stale-parent/
main-preservation tests continue passing.

**External-control status:** The reviewer independently observed unprotected main,
no rulesets and no state branch on 2026-11-14. We did not change settings or claim
those protections now exist. Before any hosted contents-write run, an independent
reviewer must verify required main/state protections, no force-push/deletion,
expected writer identity, required checks/review and bypass restrictions. The
persistence job is now **hard-disabled with `if: false`**, not merely described as
safe. Schema checks cannot authenticate well-formed fabricated hashes or allowed labels;
branch protection and reviewed writer provenance remain essential.
Repository-variable value remains unverified and must be confirmed OFF by
the owner before a future authorized infrastructure merge. No settings were enabled.

## 5. Independent operational failure alerts — corrected and fixture-tested

**Original location:** workflow lines 93–124.

**Changes:** [.github/workflows/monitoring-phase2b.yml](../../.github/workflows/monitoring-phase2b.yml)
adds `operational-failure-alert` (line 137), using `always()` and explicit
collection/persistence/queue failure or cancellation outcomes. It needs no checkout,
collector output, state artifact or successful persistence. It has issues-write
only, builds a controlled-status summary/run link, and writes the job summary
before attempting bot-owned issue creation/update. Normal editorial queue remains
separate; it never fabricates a human decision.

**Tests:** `test_failure_alert_independent_of_artifacts_and_persist_success`
executes the exact inline workflow Python for (a) collection failure before reports
and (b) persistence failure, with no artifacts and mocked GitHub CLI; both produce
an issue-create call and summary. It checks all failure/cancelled conditions and
absence of checkout/artifact/write-contents dependencies.

**Limit:** No real hosted alert was triggered. GitHub-wide failure, denied issue
permissions, unavailable runner or full workflow cancellation can prevent delivery;
notification settings/external watchdog remain production prerequisites.

## 6. workflow_dispatch default-branch documentation — corrected

**Original locations:** guide lines 25–35 and results lines 45–49.

**Changes:** [PHASE2B.md](../PHASE2B.md) states the workflow **must** exist on default
branch; `--ref` does not bypass that requirement. Commands are labelled post-
prerequisite documentation, not reliable pre-merge smoke. Original results are
labelled historical and corrected too. Only a later independently reviewed OFF
infrastructure merge could satisfy the prerequisite; that is not a production
approval and this revision does not merge. Then artifact-only manual smoke,
verified protections/scopes, separately reviewed state-write testing, and a final
reviewed activation change are distinct stages.

**Tests:** `DocumentationAndPackageTests.test_default_branch_prerequisite_and_activation_limits_documented`
checks the corrected statements and removes the misleading “may require” wording.

**Safeguard:** Scheduled collection is hard-disabled by a manual-only job condition,
so an unknown repository-variable value cannot start collection. Persistence is
also hard-disabled. Formal policy remains OFF with empty authorizations. No manual
operational dispatch was attempted in this revision.

## 7. Stable Crossref contact/mailto — configuration implemented; actual mailbox pending owner

**Original location:** `operations.py:64–66`.

**Changes:** [contact.json](../contact.json) and `operations.crossref_contact` (line 62)
provide a stable project URL and nullable institutional mailbox/approval reference.
A reviewed, valid institutional email is added to Crossref's User-Agent and `mailto`
query only. No personal address, fixture address, credential or invented mailbox
is configured; current email/approval remain **null**. The existing project URL
continues to identify the client. No polite-pool access is claimed.

**Tests:** `test_no_invented_contact_and_reviewed_mailto_only_crossref` verifies
null defaults, rejects injected invalid contact text, and uses an explicitly test-
only example.org address in a mock to verify Crossref query/UA wiring and absence
from OpenAlex. Nothing contacts that example address.

**Limit:** An approved non-personal institutional mailbox must be supplied by the
responsible institution and independently verified before production. This cannot
be completed by inventing an email, and no credential/settings request is made now.

## 8. Pinned Actions and least privilege — hardened; repository restrictions unverified

**Changes:** All action references in the Phase 2B, monitoring tests, Phase 2A dry-run
and editorial-QA workflows are full commit SHAs, resolved read-only from upstream
refs during revision:

| Action/ref | Immutable SHA |
|---|---|
| actions/checkout v6.1.0 | `d23441a48e516b6c34aea4fa41551a30e30af803` |
| actions/setup-python v6.3.0 | `ece7cb06caefa5fff74198d8649806c4678c61a1` |
| actions/upload-artifact v4 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| actions/download-artifact v4 | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |
| quarto-dev/quarto-actions v2.2.0 | `8a96df13519ee81fd526f2dfca5962811136661b` |

Collector/persistence checkout credentials are not persisted; read/write auth is
provided only to the individual Git step through process environment. The failure
alert has issues-only permissions. The contents-write job stays disabled. A fixed-
ref script is **not** a credential scope boundary: GITHUB_TOKEN contents-write is
repository-wide. A future short-lived App/writer configuration must have verified
ruleset/bypass restrictions, not an assumed branch-only permission.

**Tests:** `test_actions_pinned_and_no_production_schedule_or_publication_activation`
checks every action in these workflows and the disabled latches/policy.
`test_remote_size_checked_before_blob_read_and_git_token_not_in_arguments` verifies
auth is absent from subprocess arguments. YAML parsing and Python compilation pass.

**Limit:** Pins prevent tag drift; upstream code has not received a new independent
supply-chain audit. The existing Pages workflow is unchanged and its mutable refs
remain a separately documented hardening task. No App, token, rule or secret was
created or activated.

## 9. Field / Reanalysis / Mixed / Unresolved — supported without reclassifying the archive

**Original location:** `operations.py:224–229`.

**Changes:** `state_schema.CATEGORIES` and `operations.archive_category` (line 256)
keep the four categories distinct. Future explicit archive type must carry named
editor, approval and primary-source references; unapproved labels are ignored.
Existing inventory Reanalysis remains authoritative. Collector observations are
strictly `Unresolved`. No lexical method/fieldwork label becomes confirmed field
provenance; no archive metadata was added or changed.

**Tests:** `test_four_categories_need_reviewed_provenance_no_field_inference`
checks every category with/without provenance and recomputes the current archive:
**0 Field discovery, 1 Reanalysis (ID 31), 0 Mixed, 32 Unresolved**. Existing tests
still verify 33 formal entries, 44 ranks and ID 29 absent from formal membership.

**Limit:** A substantive field-vs-reanalysis balance cannot be claimed until a
human editor independently classifies those 32 entries. This revision preserves
that uncertainty instead of manufacturing an answer.

## 10. Regional/local-language intake — acknowledged production blocker, not represented as solved

No source/permission status was changed. The production collector still supports
Crossref only; OpenAlex and all official institutional leads remain disabled.
No global coverage, first-announcement verification, new archaeological fact or
independently verified 2026 record is claimed. Regional/local-language endpoints,
robots/terms/license/community protocols and verified announcement semantics still
require independent work. Existing disabled-source regression remains in the suite;
no fixture is used as production input. [PHASE2B.md](../PHASE2B.md) retains explicit
regional priorities and the permission/date contract for a future source review.

## Verification evidence and unchanged academic scope

Local author-run verification on 2026-11-14:

| Check | Result |
|---|---|
| Monitoring tests | **57 passed**: 38 retained/updated controls plus 19 targeted round-two tests |
| Editorial mutation tests | **26 passed** |
| Bilingual/Markdown checker | Passed |
| Source editorial QA | 0 errors, 42 existing review warnings |
| Quarto 1.11.9, isolated tracked-source snapshot | 49 pages rendered; passed |
| Rendered editorial QA on that clean snapshot | 0 errors, 42 existing warnings |
| YAML parsing, Python compile, whitespace | Passed |
| Academic-source preservation | Compared to reviewed head and main: no changes to discoveries, methods, formal list, rank/status/grade inventory, map or Quarto navigation |
| Hosted live monitor/review/audit smoke or state writes | **Not run**; default-branch/protection prerequisites remain |
| New verified archaeological findings | **None** |

[VERIFICATION.json](VERIFICATION.json) records commands, result counts and preservation
hashes. These local results are not independent certification. The read-only PR
workflow uploads a committed full-source ZIP, diffs, SHA256 manifest and actual
hosted test log for independent reproduction. The PR description links the exact
head's hosted CI results after those results are observed; historical green CI is
not used as proof of the revised head.

The first attempt to render with an alternate output directory copied the existing
untracked docs as resources and produced 33 duplicate-resource link errors. The
verification above instead renders a clean tracked-source snapshot in scratch with
the normal `docs` layout and runs QA against that root; original untracked site
output is not overwritten. No academic source-rewriting script was run.

## Focused second-review request and remaining stop conditions

Please review the two identity controls, route completeness/receipt controls, state
trust-boundary mutations, and the exact workflow failure fixture. Confirm the
manual-only collection condition, literal-disabled persistence and unchanged OFF
policy. Independently inspect the source package manifest and CI for this head.

The following remain **not completed or not verified**, not implied by test success:
branch protections/rulesets/bypass scope; actual repository-variable value; approved
institutional contact; hosted operational smoke and alert delivery; official source
permissions/local-language coverage; real new-record primary verification; human
classification of 32 unresolved entries; independent ranking/integration procedure;
future publication writer and independent gate approval. The pure gate still has
no archive writer/merge path. Do not activate anything or interpret submission as
permission to merge. Stop after second-round independent review submission.
