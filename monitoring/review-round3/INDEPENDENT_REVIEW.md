# Draft PR #4 第二轮独立学术与技术复审报告

**Repository:** `UBC-ARCHAEOLOGY/archaeology_discoveries`
**PR:** https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/pull/4
**审阅提交：** `d07dc52262ebb9d6604cc11127686924bf289369`
**上一轮审阅提交：** `2def086a9f9796fe483be415e653ccc1ffaf4f30`
**Base/main：** `3d518218d4825a325cef60269c6d3cea4bc2cf93`
**日期：** 2026-11-14
**结论：** **B — 小修后复审**（默认关闭的基础设施；不构成生产运行或自动正式发布批准）

## 一、总体判断

第二轮修改明显改善了 Phase 2B 的学术证据约束、状态数据验证和权限边界。我已核对第一轮独立报告、`monitoring/review-round2/RESPONSE.md`、实际代码差异、针对性测试及该提交的 GitHub Actions 日志。以下判断不以 Codex 的修改说明或绿色 CI 代替学术判断。

**第一轮最重要的三个技术缺陷已获得针对性实质修复**：Crossref 非学术性元数据变化引发新 observation、三条 2026 资格路径缺乏分别验证、HTTP 来源被规范化为 HTTPS 后通过来源检查。

新版还采取更严格的默认关闭措施：采集 job 只允许 `workflow_dispatch`；状态持久化 job 设置 `if: false`；正式发布策略仍为 `enabled: false`，没有已授权档案；不存在与正式条目自动写入、自动合并或 Pages 发布相连的执行路径。因此即使外部 `MONITORING_SCHEDULES_ENABLED` 变量意外为 `true`，也不能仅凭 schedule 事件启动当前采集 job。

**评级 B，小修后复审。** 当前不建议不经修改直接合并，但建议在聚焦修订后允许将 PR #4 **作为默认关闭的基础设施**合并。此项批准与定时监测启用、自动正式发布启用必须严格分开。

## 二、已独立核验的仓库和测试状态

| 项目 | 结果 |
|---|---|
| PR 当前 head | `d07dc52262ebb9d6604cc11127686924bf289369`，与指定提交一致 |
| PR 状态 | Open、Draft、未合并 |
| Base/main | `3d518218d4825a325cef60269c6d3cea4bc2cf93`，未变化 |
| 相对第一轮新增提交 | 2 个 |
| 本轮相对第一轮涉及文件 | 21 个 |
| 当前 PR 总修改文件 | 24 个 |
| `main` branch protection | 未启用；GitHub branch API 报告 `protected: false` |
| Repository rulesets | 空列表 |
| `monitoring/state-phase2b` | 尚不存在 |
| Hosted monitoring regression | [Run 43634701325](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/actions/runs/43634701325)：实际日志显示 `Ran 57 tests ... OK` |
| Hosted editorial QA | [Run 43634701326](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/actions/runs/43634701326)：成功；0 errors、42 review warnings |
| 独立审阅包 artifact | Artifact ID `14129144347`，实际上传成功 |
| Live monitor/review/audit hosted smoke | 尚未执行 |
| Hosted state persistence | 尚未执行；job 被禁用 |

**说明：** 57 项测试的实际执行已从 GitHub Actions 日志核查，但测试通过并不证明真实考古材料已核验、外部权限已配置，或生产端到端流程可用。42 项既有编辑警告也不应被绿色 CI 隐去。

## 三、第一轮十项问题逐项复审

| 编号 | 第一轮问题 | 第二轮结果 |
|---|---|---|
| 1 | Crossref 元数据噪声导致重复 observation | **核心修复已核实**；作者单位等噪声仍有边界 |
| 2 | 2026 三条资格路径未分别验证 | **实质修复**；发表日期结构仍可补强 |
| 3 | HTTP→HTTPS 来源绕过 | **原漏洞已修复**；真实来源收据仍需独立核验 |
| 4 | 恢复状态的严格验证不足 | **结构验证已修复**；格式合法的虚假记录仍可污染统计 |
| 5 | 持久化失败阻断故障告警 | **独立失败告警已实现**；正常编辑队列仍被关闭的 persist 依赖阻断 |
| 6 | `workflow_dispatch` 文档和默认关闭 | **已修复** |
| 7 | Crossref contact / `mailto` | **接口已实现**；正式联系邮箱尚未配置 |
| 8 | GitHub Actions 权限及固定引用 | **代码已加固**；仓库保护仍未落实 |
| 9 | 田野发现与再分析分类 | **部分解决**；存在既有 Reanalysis 分类可能被新分类覆盖的问题 |
| 10 | 区域及本地语言资料来源 | **未实现**；作为明确生产部署阻碍保留 |

### 1. Crossref observation identity

**位置：** [`monitoring/operations.py:191–225`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/operations.py#L191-L225)

`scholarly_projection()` 已将 `indexed`、`deposited`、引用计数、参考文献 payload、score、原始 provider record 和抓取/来源 bookkeeping 排除于 observation hash 之外。测试 `test_round2.py:57–80` 确实覆盖仅改变这些字段不新增 observation，以及题名、摘要、发表日期、作者、撤稿/更正改变时保留新版本。这是算法层面的实质修复。

**剩余边界：** 第 201 行仍将作者 `affiliation` 纳入投影。单位名称格式修订可能是非实质性书目噪声，建议增加 affiliation-only 变化的回归测试，并区分普通书目更正与学术主张修订。

**结论：原主要缺陷已修复。**

### 2. 三条 2026 年资格路径

**位置：** [`monitoring/eligibility.py:54–126`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/eligibility.py#L54-L126)

现在三条 route 的结构化要求不同：

- **首次公开公布：** 精确 2026 公布日期、田野发现日期、首次公布标记、原始来源引用和早期公布史检索。
- **首次完整/实质性转折发表：** 线上/纸本发表信息、同行评议标记、此前发表史及实质性解释增量依据。
- **旧材料再分析：** 旧材料或数据来源、原始年代、2026 分析日期、重要问题和解释增量。

`test_round2.py` 针对完整结构和删除必要字段、日期冲突、错误 route 以及 reanalysis 历史做了针对性测试。

**剩余问题：** `publication_dates()` 允许 `online` 与 `print` 同时为 `null`，只要填写 `first_publication = "2026-02-01"` 就可能通过日期结构检查。这并不等于首次发表日期得到原始出版记录确认。对于标记 `peer_reviewed=True` 的论文，应进一步要求明确日期来源及核验状态；不能把未知的 online/print 史自动视为已核实。

**结论：实质修复，但正式发布 gate 启用前应补强日期来源要求。**

### 3. HTTPS 与来源收据

**位置：** [`eligibility.py:10–27`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/eligibility.py#L10-L27)、[`publication.py:57–79`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/publication.py#L57-L79)

新函数直接检查原始 URL 的 HTTPS scheme，不再通过 `monitor.url()` 把 HTTP 规范化成 HTTPS 后放行。还拒绝嵌入凭证、内网 IP、非法端口、空白字符与不合规时间戳；收据增加 ID、SHA256、带时区检索时间及严格整数 200 状态，并与 dossier hash 绑定。

**剩余证据边界：** 纯 gate 不实际验证服务器曾返回 200 或内容 hash 对应真实论文。格式完整的虚构收据仍需依靠独立取证与具名责任编辑核验。这属于外部事实认证而非原 HTTP 绕过漏洞。

**结论：原漏洞已修复。**

### 4. 恢复状态与格式合法的虚假数据

**位置：** [`state_schema.py:48–121`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/state_schema.py#L48-L121)、[`state_store.py:35–77`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/state_store.py#L35-L77)

新版严格检查 schema 2、taxonomy SHA256、来源 ID、标签值、日期、cursor、报告摘要、重复 JSON keys 和体积上限；不再从 state 恢复 `latest_report` 自由文本；在写入本地状态前完成验证。这解决了第一轮多数**结构污染**问题。

但**结构合法不等于来源真实**。如果攻击者或错误的写入者能够改写 state branch，他可以填入合法 source ID、合法区域/年代标签、日期和格式正确但虚构的 64 位 hash；schema 无法证明它们确实源于 Crossref 或对应真实记录。这些数据仍可影响 observation count、candidate coverage 与 queue。

本轮 GitHub API 再次确认 `main` 未受保护、rulesets 为空、state branch 未建立。状态真实性需要受保护的写入身份、可靠审计和来源验证，不能仅靠 schema。

**结论：代码结构验证已修复；生产真实性保障尚未落实。**

### 5. 失败告警与正常编辑队列

**位置：** [`monitoring-phase2b.yml:97–178`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/.github/workflows/monitoring-phase2b.yml#L97-L178)

新增 `operational-failure-alert` 使用 `always()`，检查 collect、persist 和 editorial-queue 的 failure/cancelled 状态；无需 checkout、报告或 state artifact。测试还执行了从 workflow 抽取的告警 Python，模拟 collect failure 和 persist failure。**第一轮所指出的“persist 失败导致故障 issue 同时跳过”已经得到针对性修正。**

但正常队列仍配置 `needs: [collect, persist]`，而 persist 当前永久 `if: false`。因此目前即使手动 `mode=review` 成功生成 artifact，正常 `editorial-queue` 也会因为 persist skipped 而被跳过。这个行为可视为有意的分阶段关闭，却不能表述为已经可运行的人工 Issue queue。应在文档明确限制，并在启用队列时调整依赖或联动恢复持久化。

**结论：独立失败告警代码已修复；正常队列未具备生产运行能力。**

### 6. 默认关闭与手动触发

**位置：** `monitoring-phase2b.yml:27–30, 97–100`、`monitoring/publication-policy.json`

三重限制已核实：采集只接受 `workflow_dispatch`，persist `if: false`，正式发布策略 `enabled: false` 且没有授权 dossiers。未见在当前代码中绕过三个限制自动更新考古档案或推送 main 的路径。

不过有相应权限的用户仍可手动执行 collection；这属于受控 smoke 入口，不等于完全无执行能力，也不等于网站发布。

**结论：已修复；不构成生产激活批准。**

### 7–8. Crossref contact、GitHub token、Actions 固定引用

**位置：** `monitoring/contact.json`、`monitoring/operations.py:62–85`、`monitoring/state_store.py:15–23`、各 workflow YAML。

Crossref institutional contact 的配置和 `mailto` 拼接逻辑已经实现，但当前 mailbox 和 approval reference 仍为 `null`，不能声称已启用 polite-pool 条件。

Actions 引用现已固定到完整 commit SHA；checkout 的 `persist-credentials` 设置为 `false`；GitHub token 由 Git 子进程环境传递而不是写入命令行。权限边界比上一轮更强。不过 `contents: write` 是仓库级 token 权限，而非 state branch 级权限。固定 ref 的 Python 代码不能代替 branch protection/rulesets 及受限制的自动化身份。

**结论：代码加固已完成；生产权限与机构配置仍未落实。**

### 9. 周日平衡审计及 Reanalysis 分类保护

**位置：** [`operations.py:256–300`](https://github.com/UBC-ARCHAEOLOGY/archaeology_discoveries/blob/d07dc52262ebb9d6604cc11127686924bf289369/monitoring/operations.py#L256-L300)

新版提出 `Field discovery / Reanalysis / Mixed / Unresolved` 四分类；当前 33 项统计是：

| 分类 | 数量 |
|---|---:|
| Field discovery | 0 |
| Reanalysis | 1（ID 31） |
| Mixed | 0 |
| Unresolved | 32 |

这种保守处理是正确的：没有把其他 32 项自动定义为田野发现。

**仍有应修复的分类优先级问题：** `archive_category()` 优先采用新添的 `research_type` 和格式合规的 `research_type_provenance`，只有前者不满足格式要求时才退回既有 `reanalysis: true`。因此已有 Reanalysis 标签的项目，如果后来被附上形式合规但实质上未经验证的 `Field discovery` 分类，会在审计输出中被覆盖。当前的 provenance URL 语法检查并不能独立确认审批者身份或审批内容。

建议：凡新分类与既有已确认 Reanalysis 标记冲突，应产生 `classification_conflict` 并等待明确的人工学术决定，而不是静默覆盖。同时，地区和年代审计仍偏重词典筛查，需保留原始记录、未知比例和经人工核实的分类，避免把词频统计等同于真实考古发现分布。

**结论：部分解决；分类冲突保护建议合并前修复。**

### 10. 官方机构及本地语言来源

当前生产采集仍主要依赖 Crossref；OpenAlex 和主要官方机构线索仍被禁用，尚不能充分监测以地区性、官方田野公告、本地语言报告为主要首次公布渠道的发现。

这不是本轮新增的事实错误，Codex 也明确承认尚未完成。但它阻止任何“全球覆盖完整”或“自动确认 2026 首次发现资格”的生产宣称。

**结论：未完成，保留为生产激活前重要学术任务。**

## 四、合并前的最低聚焦修订

| 优先级 | 文件位置 | 应处理事项 |
|---|---|---|
| **必改** | `monitoring/operations.py:256–266` | 防止已有 Reanalysis 分类被形式合规但未核实的新分类静默覆盖；冲突应进入人工审阅 |
| **必改** | `monitoring/eligibility.py:54–62` | 对 online/print 均未知但 first_publication 自报日期的情况明确证据状态与核验要求 |
| **必须修复或明确限制** | `.github/workflows/monitoring-phase2b.yml:97–136` | 说明正常 editorial queue 在 persist disabled 时不会执行；相应调整测试/文档，启用前修复依赖 |
| **建议修订** | `monitoring/operations.py:191–210` | 增加 affiliation-only 更正的 regression test，减少非学术性观察噪声 |

前两项涉及考古学证据和既有编辑决定的保护，因此建议在默认关闭基础设施合并前完成。第三项至少须准确标记为未启用功能，不得称已经具有可运行的人工 Issue queue。

## 五、三个独立批准关口

### 关口一：默认关闭基础设施合并

**小修复审通过后可以合并。** 保持 scheduled collection 只允许手动 dispatch，persist disabled，formal policy OFF；完成上述聚焦修订，重跑测试并核对准确 commit SHA。合并本身不等于生产运行授权。

### 关口二：启用定时监测

**当前不批准。** 启用前至少需要：

- 落实 main/state branch protection、writer 身份限制、force-push/deletion 和 bypass 控制；
- 核实仓库变量、凭据权限与监控专用联系地址；
- 在 GitHub-hosted runners 上完成 monitor、review、audit 三种人工 smoke；
- 验证真实 Crossref/API 连通性、许可和限流处理；
- 重复执行 state restore/persist、并发冲突与恢复检查；
- 在真实 hosted 环境演练故障告警和正常人工 Issue queue；
- 经单独独立审阅的 workflow 改动解除硬关闭，并显式批准 repository variable；
- 对官方机构、本地语言及地区来源制定并执行经过许可和日期语义核实的接入计划。

### 关口三：自动正式发布

**当前明确不批准。** 除关口二要求之外，还需：

- 真实的 2026 新候选及独立原始证据、作者/机构、DOI、最早发表史核对；
- 学术意义、重要既有研究、反例和替代解释的独立判断；
- 具名责任编辑的完整双语 dossier、来源收据、敏感地点和社群许可检查；
- 对未分类档案的人工分类及字段/时代/地区平衡审计；
- 稳定 ID、正式名单、导航、地图、数量、排名的受审阅事务集成；
- 完整 publication gate 和未来 archive writer 的独立技术/学术审阅；
- 在准确 PR head 上运行的确定性构建、内容 QA、隐私、重复识别和 rollback 测试；
- 独立学术批准，不以模型判断、数据库匹配或绿色 CI 替代。

## 六、最终评级与证据状态

**正式评级：B — 小修后复审。** PR #4 已达到一个可以继续聚焦修订的基础设施成熟度，原则上可在小修后作为 **default-OFF、non-publishing infrastructure** 合并。但不应将合并视为完成 Issue #3 生产范围或批准定时监测和自动正式发布。

**已独立核实：** PR SHA/差异、GitHub-hosted 57 tests 实际执行、默认关闭条件、formal publication OFF、route-specific validation 代码、严格 state schema、独立 failure alert 路径、main 未受 branch protection/rulesets 保护。

**内部一致但未完成独立运行验证：** 合成反例测试的预期行为、模拟 Git persistence、模拟故障 issue 更新、Codex 报告的本地完整 Quarto 构建。测试通过不能代替真实 hosted 端到端运行。

**尚未核实或未建立：** 实际 GitHub-hosted monitoring/persistence/alert，仓库监测变量真实值，机构 contact，官方区域来源许可与首次公布日期，真实 2026 新发现的一手证据，32 项 Unresolved 的人工审定，未来的正式发布事务与学术批准。

**建议 Codex 下一步：** 仅处理第四节列出的四项聚焦问题，并提交准确新 head SHA、差异和测试证据供第三轮简短复审；不重开既有 33 项学术发现、不启用自动监测、不改写正式名单或排名。

---

**审阅行为声明：** 本轮只进行了只读代码、仓库、工作流及日志审阅；没有修改代码、提交评论、合并 PR、启用定时监测或正式发布。
