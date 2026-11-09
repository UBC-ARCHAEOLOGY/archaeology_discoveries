# V2.2 Finalization Record | V2.2 定稿记录

**Project:** 2026 Archaeological Discoveries | 2026年世界考古发现  
**Repository:** `UBC-ARCHAEOLOGY/archaeology_discoveries`  
**Finalized:** 2026-11-09  
**Locked baseline commit:** `dd6c083df0477f1ab85b0b06739f0fc8630ffb6e`

## Status | 状态

V2.2 is the finalized editorial baseline for the current 2026 archaeological-discoveries corpus. Content review, bilingual consistency checks, Markdown/rendering QA, map adjustments, and GitHub Pages deployment have been completed for this baseline.

V2.2 为当前“2026年世界考古发现”资料库的编审定稿基线。正文审校、中英文一致性检查、Markdown/渲染质量检查、地图标记调整以及 GitHub Pages 部署均已完成。

## Final editorial fixes after the offline review package | 离线编审包后的最后修订

Relative to review baseline `ba69e93`, the finalized baseline includes:

- corrected Markdown list spacing on the home page and the under-review page;
- a regression check in `scripts/check_bilingual.py` for missing blank lines before Markdown lists;
- revised wording of Volker Auwärter's criticism so that the directly verifiable Associated Press quotation is clearly attributed and unsupported specificity is removed;
- harmonized the Lake Baikal plague wording to “the most likely source of zoonotic spillover” while retaining the evidentiary limits of the marmot hypothesis;
- normalized `Hawaiʻi` with the correct ʻokina;
- reduced marker congestion in the Aegean–Anatolian area of the map with offset markers and leader lines;
- corrected the final leader-line markup newline issue.

相对于 `ba69e93` 编审基线，定稿版完成了首页和待评估页列表渲染、列表空行回归检查、Auwärter 质疑的可核查引语处理、贝加尔湖鼠疫表述统一、`Hawaiʻi` 字符规范、爱琴海—安纳托利亚地图标记疏解，以及最后的引线标记换行修复。

## QA and deployment | 质量检查与部署

The GitHub Actions workflow **Deploy Quarto site to GitHub Pages** completed successfully for commit `dd6c083` on 2026-11-09.

Known non-blocking observations retained from editorial QA:

- the Egyptian State Information Service link may reject automated checks even when manually reachable;
- fixed navigation/sidebar behavior should be verified in an ordinary browser when visual-capture tooling truncates the viewport.

## Baseline rule for subsequent work | 后续工作的基线规则

All future additions, candidate evaluations, and annual final-selection work should start from `dd6c083` or a descendant of it. The issues resolved between `ba69e93` and `dd6c083` are considered closed unless a new regression is detected.

后续新增发现、候选项目评估和年度最终遴选均应以 `dd6c083` 或其后续提交为起点。除非出现新的回归问题，不再重新处理 `ba69e93` 至 `dd6c083` 之间已经解决的问题。
