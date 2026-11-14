# Second-round independent review package — Draft PR #4

Review target: **default-OFF, non-publishing infrastructure only**. Nothing in this
package requests merge, production approval, new credentials, repository settings
changes, schedule activation or formal publication. 本轮仅提交默认关闭的基础设施复审；
不申请合并、生产激活或正式发现自动发布。

- [Authoritative independent report](INDEPENDENT_REVIEW.md): owner's full supplied
  Grade B report, referring to original head `2def086a9f9796fe483be415e653ccc1ffaf4f30`.
- [Point-by-point response](RESPONSE.md): all ten findings, code/test locations,
  results, unresolved controls, and focused second-review checklist.
- [Machine-readable local verification](VERIFICATION.json): commands, statuses,
  academic-source preservation hashes, and implementation/test file hashes. These
  are reproducible author-run results, not independent certification.
- [Operating guide](../PHASE2B.md), [publication contract](../PUBLICATION_POLICY.md),
  [OFF manifest](../publication-policy.json), [contact config](../contact.json).
- [Targeted tests](../test_round2.py), [prior controls](../test_operations.py),
  [Phase 2A regressions](../test_monitor.py). All new dossier examples are synthetic.

The read-only PR workflow **Monitoring offline regression** checks out the exact
PR head with history, runs the suite and uploads `phase2b-round2-review-package`
(30-day retention): full committed source ZIP, round-two diff against the reviewed
head, complete diff against main base, SHA256 file manifest, and hosted test log.
`manifest.json` inside the ZIP identifies the exact snapshot commit. The separate
Editorial consistency QA workflow tests/renders the academic archive. Neither
workflow activates Phase 2B operational jobs or publication. GitHub artifact
availability and CI success must be confirmed on the actual head, not assumed.

Rebuild the same source package from a checkout with full history:

```sh
python monitoring/package_review.py --output work/phase2b-round2-review.zip
```

Only Git-committed files enter the ZIP; untracked docs/screenshots/intake/state,
local reports and credentials are excluded. Source fixtures remain labelled
fixtures. A package created before committing changes would describe the old head;
use the manifest and exact reviewed SHA.

For this round the collector accepts manual dispatch only, so a schedule event
cannot collect even if an unknown repository variable is true. The persistence
job has literal `if: false`, blocking a contents-write hosted run pending independently
verified branch protection and credentials. The independent issues-only failure
alert is tested with mocked outcomes; no hosted operational job or issue was run.
The PR remains Draft and is submitted for second independent review, not marked
ready or merged. Repository protections are requirements, not claimed existing.
