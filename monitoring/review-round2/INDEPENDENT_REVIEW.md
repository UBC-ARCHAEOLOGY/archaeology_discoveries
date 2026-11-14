# `archaeology_discoveries` Draft PR #4 独立学术与技术审阅

**Source:** Complete report supplied by the owner in this revision conversation on 2026-11-14. The text below is the authoritative independent review; implementation responses are in `RESPONSE.md`.

**Repository:** `UBC-ARCHAEOLOGY/archaeology_discoveries`
**PR:** #4 — *Phase 2B: scheduled review operations and disabled formal-publication gate*
**Base:** `3d518218d4825a325cef60269c6d3cea4bc2cf93`
**Head:** `2def086a9f9796fe483be415e653ccc1ffaf4f30`
**审阅日期:** 2026-11-14

## 一、结论

**评级：B — 小修后复审。**

这个评级有一个重要范围限定：**B 是针对“把 PR #4 作为默认关闭、尚未生产激活的 Phase 2B 基础设施”而言。它目前不能被批准为 Phase 2B 的生产部署，也不能开启 schedules，更不能开启 formal publication。**

我没有发现当前代码存在能够把新候选**自动写入 `main`、自动修改正式发现、排名或证据等级、或者自动部署到网站**的执行路径。正式发布策略确实是 `enabled: false`，没有 responsible editors，没有 approved dossiers；publication gate 也没有连接 archive writer 或 merge 功能。状态持久化只针对固定的 `monitoring/state-phase2b` ref；现有 Pages workflow 只在 `main` push 时触发，因此 state branch 的 push 不会间接触发网站部署。

但是，独立审阅发现了几项 Codex 报告和绿色测试没有暴露的问题。其中有四项应在复审前处理：**Crossref observation hash 会因非学术性元数据变化不断生成新 observation；publication gate 的 2026 路径验证尚不真正 route-specific；恢复的 state 缺乏足够深的 schema/allowlist 验证，而仓库目前没有 branch protection；状态持久化失败时 outage/reviewer issue 会被 GitHub Actions 的 `needs` 依赖一并跳过。**

此外，GitHub-hosted monitor/review/audit 三种 manual smoke 尚未完成，正式 source permissions、regional/local-language feeds、真实新 2026 records 和 ranking integration procedure 均尚未完成。因此：

> **可以在上述小修完成并复审通过后，把它作为“OFF 状态基础设施”合并；不能把这次合并解释为 Phase 2B production approval。**

如果把 PR #4 当作 Issue #3 全部 production requirements 的最终交付物来评，则应是 **C**；但按照 PR 自己实际的 Draft/infrastructure scope，我给正式评级 **B**。

## 二、我实际独立核查了什么

| 项目 | 状态 | 独立审阅结果 |
|---|---|---|
| PR base/head | **已独立核实** | base 确为 `3d518218…`，head 为 `2def086a…`；PR 仍为 Draft |
| 修改范围 | **已独立核实** | 13 个文件，+1213/-0；没有修改任何 `discoveries/*.qmd`、`discoveries.qmd`、`ranking.qmd` 或 inventory 内容 |
| 当前 `main` | **已独立核实** | 仍为 `3d518218…` |
| 正式条目数 | **已独立核实** | 从实际 `discoveries.qmd` 重新计算为 **33** |
| ranking inventory | **已独立核实** | `editorial/inventory.json` 为 **44** 个位置，1–44 连续 |
| ID 29 | **已独立核实** | 不在 formal 33 项中；仍保留在 inventory/under-review 语境 |
| 新考古发现 | **已独立核实：无** | PR #4 没有增加任何新的考古发现条目，因此没有新的作者、机构、DOI、年代、数量或研究结论可作外部事实复核 |
| 2026 三条资格路径 | **已独立核实** | 与现有 `methods.qmd` 的三个 route 大体一致，但 gate 实现不完全落实 route-specific 证据要求 |
| GitHub Actions timezone | **已独立核实** | `timezone: America/Vancouver` 是当前 GitHub Actions 支持的有效语法，DST 可由 IANA timezone 处理。 |
| workflow_dispatch 在 PR branch 上的可运行性 | **已独立核实，有文档错误** | GitHub 当前规定 workflow 文件必须已经存在于 default branch 才能触发 `workflow_dispatch`；不是文档所说的“may require”。 |
| CI 38 tests | **已独立核实其确实运行** | GitHub-hosted log 显示 `Ran 38 tests ... OK`；但这只说明这些测试通过，不构成考古学或 production 认证 |
| local “12/12 proxy_403” | **内部一致但未独立核实** | PR 文档这样报告，但我没有独立 runner artifact 能证明该 local execution |
| GitHub-hosted Phase2B live smoke | **无法核实／尚未发生** | 没有 monitor/review/audit workflow_dispatch 成功记录 |
| official institutional feed permissions | **无法核实／尚未建立** | 当前所有这类 source 仍 disabled |
| `MONITORING_SCHEDULES_ENABLED` 当前值 | **无法核实** | 连接权限不能读取 repository Actions variables；合并前必须人工确认不是 `"true"` |
| branch protection | **已独立核实存在问题** | GitHub branch API 当前报告 `main` 为 `protected: false`；rulesets 查询返回空列表 |
| formal publication OFF | **已独立核实** | `publication-policy.json`：`enabled:false`、editors `[]`、approved dossiers `{}` |
| state branch | **已独立核实** | 当前尚不存在 `monitoring/state-phase2b` |
| accidental Pages deployment | **已独立核实没有该路径** | 现有 `pages-deploy.yml` 只在 `push: branches: [main]` 触发 |

# 三、需要修改的问题

## 1. 【重要】Observation hash 把 Crossref 的非学术性元数据变化当成新 observation

**位置：**

- `monitoring/operations.py:166–176`
- `monitoring/monitor.py:68–76`
- `monitoring/PHASE2B.md:71–78`

当前 observation identity 是：

`digest(record 中除 retrieved_at 外的全部字段)`

但 `monitor.crossref()` 把以下内容一并放进 record：

- `source_dates`，包括 `indexed`
- 整个 `provider_record`

这意味着即使 DOI、题名、作者、发表日期、摘要和考古学内容完全没有变化，只要 Crossref 更新了 `indexed` 时间、引用计数、reference metadata 或其他 provider-level 字段，就会产生新的 observation hash。

而 Phase 2B 又明确使用 `from-index-date`。Crossref 当前文档说明，index date 会随着 member、Crossref 本身以及外部服务造成的重新索引而改变，并不等价于作品发生了新的学术变化。

我按当前代码逻辑独立复算：只改变同一 DOI 记录的 `indexed` 值，observation hash 就变化。

**后果：**

identity grouping 因 DOI 相同，所以“candidate 数量”不会膨胀；但是：

- `observations` 会长期增长；
- `observation_count` 会持续增加；
- public review queue 会不断出现同一论文的新版本；
- state branch 会越来越大；
- 人工审阅会被“Crossref metadata churn”污染。

这不是简单的显示问题，而是长期生产运行中的数据模型问题。

**建议修改：**

建立一个明确的 **scholarly observation canonicalization**。用于 observation identity 的字段只应包括有学术意义的稳定字段，例如 normalized DOI、title、authors、publication dates、abstract/claims 等；`indexed`、reference counts、raw provider payload 等应排除。若希望保留 provider 变化，可另存 `provider_snapshot_hash`，但不要自动生成新的 editorial observation。

同时增加两个 regression tests：

- 仅 `indexed`/citation/reference metadata 改变 → observation 不新增；
- title/abstract/publication date 等实质内容改变 → 保留新 observation。

## 2. 【重要】2026 publication gate 并没有真正按三个 eligibility route 验证证据

**位置：**

`monitoring/publication.py:50–61`

目前代码只做：

- `publication_dates` 至少有一个日期；
- 最早日期的年份为 2026；
- route 值属于三个合法字符串之一。

但之后没有根据 route 分别要求不同的结构化证据。

### 2.1 `first_public_announcement`

当前 gate **不要求 `announcement_date`**。

因此一个 dossier 可以写：

- `eligibility_route = first_public_announcement`
- `publication_dates = ["2026-01-01"]`
- 完全没有 `announcement_date`

只要人工 attestation 等其他字段齐全，程序本身仍会允许。

这与 `methods.qmd` 的规则不同：这一途径的核心事实正是**首次公开公布发生于 2026 年，而且要和实际 excavation/discovery date 区分**。

### 2.2 `Reanalysis`

route 设为 `Reanalysis` 后，程序没有结构化要求：

- legacy material/data 是什么；
- 原始发掘/数据年代；
- 此前发表历史；
- 2026 analysis date；
- major interpretive gain 的结构化标记。

这些目前全部依赖自由文本和 editor attestation。

### 2.3 `first_substantive_publication`

同样没有分别表示：

- earliest online publication；
- print date；
- prior preliminary publications；
- substantive increment。

虽然 `earlier_history` 是 required text，但 gate 本身不能判断 route-specific completeness。

**建议：**

不要让三个 route 共享一个单纯的 `publication_dates` test。至少建立：

- `first_public_announcement` → exact `announcement_date` + discovery/fieldwork history；
- `first_substantive_publication` → exact earliest online/publication dates + prior-publication history + substantive-increment evidence；
- `Reanalysis` → legacy source/material provenance + 2026 analysis/publication date + major-interpretive-gain review。

现有 human attestation 可以继续作为学术判断，但程序应该先保证每种 route 的**证据结构完整**。

## 3. 【重要】“HTTPS primary provenance”在代码中并没有真正 fail closed

**位置：**

- `monitoring/publication.py:62–70`
- `monitoring/monitor.py:31–36`
- `monitoring/PUBLICATION_POLICY.md:21–29`

Policy 明确要求：

> accessible HTTPS URL

但是 `m.url()` 接受：

```text
http://...
https://...
```

然后无论原始输入是哪一种，都返回 scheme 为 `https` 的 normalized URL。

因此：

`http://example.org/source`

会先被改写成：

`https://example.org/source`

然后通过 `publication.evaluate()` 的 URL syntax test。这里并没有实际证明 HTTPS endpoint 可访问。

`http_status: 200` 同样只是 dossier 的字段，不是 gate 自己的网络验证。

这与 policy 所声称的“live provenance receipt”存在差异。

**建议：**

publication gate 应直接检查原始 URL 的 `urlsplit(...).scheme == "https"`；不要依赖会改写 scheme 的 generic normalization helper。Live receipt 的 URL、content hash、retrieval timestamp、status 应作为一个不可混淆的 provenance structure。

## 4. 【重要】恢复的 state 是一个信任边界，但 schema validation 太浅；当前仓库又没有 branch protection

**位置：**

- `monitoring/operations.py:93–102`
- `monitoring/state_store.py:28–39`
- `monitoring/PHASE2B.md:59–69`

`load_state()` 目前检查：

- schema number；
- sources/observations/runs 是 dict；
- observation key 是 SHA256；
- observation row 恰好有六个字段。

但没有验证：

- `source_id` 是否来自 registry；
- `tags` 是否只有四个合法 dimensions；
- tag value 是否属于当前 allowlist；
- `identity_keys` 是否都是 64-char hashes；
- dates 是否 ISO date；
- `classification` 是否合法 enum；
- `sources` 中 pending/window/cursor 的 schema；
- restored `latest_report` 的结构。

与此同时，我通过 GitHub branch API 独立确认，当前：

- `main`：`protected:false`
- repository rulesets：空
- `monitoring/state-phase2b` 尚不存在。

所以 PHASE2B 文档里的：

> Branch rules should restrict...

目前只是**建议状态**，不是已经存在的控制。

这尤其重要，因为 persisted state 最终会重新进入 public `report.json` 和 issue queue。虽然 raw primary text 没有写入 ledger，但如果 state branch 被人为或其他 token 修改，恶意/错误的 tag/source_id 等内容可能被带入 public artifact。

**建议：**

在 hosted write-token 测试之前：

1. 对 restored state 做完整 schema + allowlist validation；
2. 增加 taxonomy/schema version；
3. 对 state branch 和 `main` 建立保护；
4. 禁止 state branch force push/deletion；
5. 确保只有预期 automation 可以写 state branch。

GitHub 官方也建议将 `GITHUB_TOKEN` 权限保持最低限度，并强化第三方 Action 的供应链约束。

## 5. 【重要】state persistence 失败时，反而不会生成 outage/reviewer issue

**位置：**

`.github/workflows/monitoring-phase2b.yml:93–124`

当前关系为：

```text
collect
  ↓
persist
  ↓
editorial-queue
```

而 `editorial-queue`：

```yaml
needs: [collect, persist]
```

GitHub Actions 默认情况下，只要 `persist` 失败，依赖它的 job 就不会运行。

这会造成一个不理想的故障模式：

> 正是 durable state 写入失败、权限失效、branch push 冲突等最需要通知人的时候，operational issue 可能完全不出现。

同样，如果 collect 在 report 生成之前失败，也没有独立 failure-notification path。

**建议：**

增加独立的 failure/outage notification job，例如使用 `if: always()` 并检查 `needs.collect.result` / `needs.persist.result`。正常 review queue 和 operational failure alert 应分开，不能要求 state persistence 成功之后才能报告 persistence failure。

同时应该增加 workflow-level regression 或 fixture test 来覆盖这一情况。

## 6. 【文档与激活流程】`workflow_dispatch` 的说明不准确

**位置：**

- `monitoring/PHASE2B.md:25–35`
- `monitoring/PHASE2B_RESULTS.md:45–49`

目前文字说：

> GitHub **may require** a workflow file to exist on the default branch before dispatch is available.

当前 GitHub 文档不是“may require”，而是明确：

> `workflow_dispatch` event **will only trigger if the workflow file is on the default branch**.

所以文档中针对尚未进入 default branch 的：

```text
gh workflow run monitoring-phase2b.yml --ref monitoring/phase2b-scheduled-review ...
```

不能被视为一个可靠的 pre-merge smoke-test 方法。

**正确流程应明确写成：**

PR #4 经独立代码审阅后，如果要解决这一 GitHub 平台限制，可以先以 **schedule variable 明确 OFF、formal policy OFF** 的状态合并基础设施；workflow 文件进入 default branch 后，再执行三种 `workflow_dispatch` hosted smoke。只有全部通过后，才考虑打开 schedule variable。

这也意味着：**合并基础设施 ≠ 激活生产运行。**

## 7. 【生产可靠性】Crossref client 没有提供 contact/`mailto`

**位置：**

`monitoring/operations.py:64–66`

当前 User-Agent 是有标识性的，这一点是好的，但没有 email/contact，也没有 `mailto` query parameter。

Crossref 当前 REST API 文档明确建议提供联系方式，并说明使用 `mailto`/identified client 可进入更友好的 polite pool，具有更合适的 rate limits 和联系机制。

对于一个计划长期定时运行的 institutional monitoring service，建议配置一个非个人、稳定的项目联系地址，并在 UA/`mailto` 中使用。

这不是安全漏洞，但会直接影响“production monitoring reliability”。

## 8. 【安全加固】具有 `contents: write` 权限的 workflow 仍使用 mutable Action tags

**位置：**

`.github/workflows/monitoring-phase2b.yml`

例如：

- `actions/checkout@v6`
- `actions/setup-python@v6`
- `actions/download-artifact@v4`

这些是 major-version tags，而不是 immutable commit SHA。

普通 read-only CI 中风险相对有限；但是 `persist` job 拥有 `contents: write`。在 repository 当前又没有 branch protection 的情况下，建议在真正生产运行前将关键 third-party actions pin 到经过审核的 commit SHA，或采用等价的 dependency control。

GitHub 官方供应链安全指导也建议对第三方 Actions 使用 immutable reference/commit SHA 作为最强保护方式。

## 9. 【学术审计】Sunday 的“field-vs-reanalysis”目前实际上是“Reanalysis vs unknown”

**位置：**

`monitoring/operations.py:224–229`

这里有一个值得肯定的学术选择：

```text
Reanalysis
not_labelled_reanalysis_field_status_unverified
```

程序**没有**把“没有 Reanalysis 标签”自动等同于“field discovery”。这是正确的。

但 Issue #3 要求的是：

> field-vs-reanalysis balance audit

当前正式 33 项中，我独立重新计算得到：

- 明确 `Reanalysis`: 1 项（ID 31）
- 其余 32 项：程序只能称 `not_labelled_reanalysis_field_status_unverified`

所以目前并没有真正的 field-vs-reanalysis balance，只是：

> 1 Reanalysis + 32 未分类。

建议继续保持这种保守性，不要用 heuristic 把 32 项自动改成 field；正确做法是建立经过人工核验的 provenance category，允许至少：

`Field discovery / Reanalysis / Mixed / Unresolved`

然后 Sunday audit 才能真正回答 Issue #3 所要求的问题。

## 10. 【Issue #3 production blocker】regional/local-language source coverage 尚未实现

当前 `sources.json` 中真正启用的生产 collector 来源仍全部走 Crossref：

- global Crossref；
- 若干 archaeology journal 的 Crossref metadata endpoints。

OpenAlex disabled。

ASI、Sri Lanka Department of Archaeology、BRIN、INAH、CABAH、ANU、Wits、Samarkand 等 institutional leads 全部 disabled。

而 `operations.collect()` 当前只处理：

```python
source['adapter'] == 'crossref'
```

所以 South Asia、Central Asia、Africa、Southeast Asia、Aboriginal Australia、Pacific 等区域的**官方首次公布和 local-language institutional reporting** 尚没有 production intake。

这不构成 PR #4 内部事实错误——文件已经明确把它列为 blocker——但它意味着不能宣称 Phase 2B 已经具备全球监测覆盖，也不能利用当前 metadata queue 判断一个项目是不是“2026 年首次公开公布”。

# 四、关于考古学事实、作者、机构、DOI、年代和数量的独立核查

这一部分有一个很重要的结论：

**PR #4 没有修改任何一个 archaeological discovery entry。**

因此这次 PR 没有提出新的：

- archaeological site/project；
- author attribution；
- excavation/research institution；
- DOI；
- archaeological age；
- artifact/sample count；
- substantive research conclusion；
- scholarly significance claim。

所以不能为了“完成事实核查”而把仓库原有 33 项重新冒充成 PR #4 的新增主张。

我独立核实的是**档案结构事实**：

- formal list = **33**
- ranking inventory = **44**
- formal IDs 无重复
- ID 29 不在 formal list
- ranks 1–44 连续
- formal list 中显式 Reanalysis 当前只有 ID 31

这些是对 repository source 的独立复算，不等于对 33 个既有 archaeological discoveries 的全部外部学术事实重新复审。

对于未来新候选，目前 Crossref metadata 只能用于**发现线索和 bibliographic screening**。它不能独立证明：

- 2026 firstness；
- archaeological field context；
- “首次”“最早”等比较性主张；
- substantive interpretive increment；
- prior publication absence；
- scholarly significance。

因此 PR 的 `metadata_only` fail-closed 原则本身是正确的。

# 五、已经做得较好的部分

以下不是引用 Codex 自评，而是我从代码路径独立确认：

1. **formal publication 当前确实是 OFF。**
   `publication-policy.json` 没有 active authorization。
2. **publication gate 是纯函数，没有 archive writer。**
   通过后最多返回 `prepare_transaction_pr`；不存在直接 main push 或 auto-merge。
3. **现有 33 项、44 ranks 没有被这个 PR 改写。**
4. **state push 固定到 `refs/heads/monitoring/state-phase2b`。**
   不接受任意 branch 参数，也没有 force push。
5. **有 stale-parent check 和 non-force Git push。**
   对 concurrent writer 的基本防护设计合理。
6. **watermark 只有完整 interval 才推进。**
   page cap、missing/repeated cursor、网络错误不会静默推进。
7. **原始 Crossref title、abstract、DOI、coordinates 等没有直接写入 durable public ledger。**
8. **retrieved text 没有进入 shell command 或 publication instruction path。**
9. **Pages deployment 不会被 state branch push 触发。**
   现有 Pages workflow 只监听 `main`。
10. **GitHub-hosted regression 的确实际执行了 38 tests。**
    我检查了 job log，而不是只接受 PR 描述；但这些测试仍然不能替代本次独立审阅。

# 六、三类证据状态的最终划分

### 已独立核实

PR diff/base/head；13 changed files；33 formal/44 ranking；ID 29 非 formal；正式 policy OFF；没有 archive writer/auto merge；state 写入 fixed branch；Pages 仅 main push；GitHub timezone syntax；workflow_dispatch 的 default-branch 要求；CI 的 38 tests 实际执行；当前 `main` 没有 branch protection/rulesets。

### 内部一致但尚未独立核实

`PHASE2B_RESULTS.md` 所述 local cloud runner “12/12 proxy_403”、local Quarto 49-page render、local CLI smoke 的具体执行结果。这些陈述与代码和 PR 描述不矛盾，但我没有把 Codex 自报结果当成独立证据。

### 无法核实或尚不存在

当前 `MONITORING_SCHEDULES_ENABLED` repository variable 的实际值；GitHub-hosted monitor/review/audit live smoke；official institutional source 的 robots/terms/license/first-announcement semantics；真实 independently verified new 2026 records；正式 ranking integration procedure；future responsible-editor attestations。

# 七、B 级复审前的最低修订清单

1. 重做 observation canonical hash，排除 Crossref volatile provider metadata，并加 regression test。
2. 把三个 2026 eligibility routes 改成 route-specific evidence validation；修正 HTTP→HTTPS provenance loophole。
3. 对 restored state 做完整 schema/allowlist validation。
4. 为 `collect`/`persist` failure 增加独立 `always()` operational alert。
5. 把 `workflow_dispatch` 的 default-branch 说明改正确。
6. 合并前人工确认 `MONITORING_SCHEDULES_ENABLED` 为 absent/false；在任何 write-token hosted run 前落实 main/state branch protection，并建议 pin write-job Actions。
7. 为 Crossref production client 增加稳定 contact/`mailto`。
8. 不得把 Sunday audit 的 32 个 `not labelled Reanalysis` 表述为 field discoveries。

完成以上修改后，我认为可以进行一次**很集中的第二轮复审**，不需要重新从头审 PR。

# 最终决定

**B — 小修后复审。**

**可以接受的目标：**
修订后作为 **default-OFF、non-publishing Phase 2B infrastructure** 合并。

**目前不能批准：**

- `MONITORING_SCHEDULES_ENABLED=true`
- formal-publication activation
- automated formal entry creation
- production completeness claim
- global/regional coverage claim
- “已具备自动判断 2026 世界考古发现资格”的表述

在 hosted smoke、source permissions、real new-record verification、branch protection 和独立 ranking/integration procedure 完成之前，Phase 2B 应继续保持 **inactive / provisional**。
