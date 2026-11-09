#!/usr/bin/env python3
from pathlib import Path
import re

EVIDENCE_ZH={
"01-wonderwerk-fire.qmd":"同行评议专业期刊研究（B级）；提供重要的新方法和早期用火证据，但年代应以区间表达。",
"02-yunxian-homo-erectus.qmd":"顶级同行评议研究（A级）；新年代仍有争议，更适合视为重新打开而不是终结系统发育问题。",
"03-megalopolis-wood-tools.qmd":"顶级同行评议研究（A级）。",
"04-denisovans-yunnan.qmd":"顶级同行评议研究（A级）；本页把2026年丹尼索瓦人多项成果作为相互关联的研究群处理。",
"05-oldest-dog-genomes.qmd":"顶级同行评议研究（A级）；应与同期关于欧洲早期家犬基因组史的Nature论文合并阅读。",
"06-romito-genetic-disease.qmd":"NEJM同行评议临床遗传学通讯；分子诊断证据强，考古意义主要体现在照护生物考古和个体生命史。",
"07-baikal-plague.qmd":"顶级同行评议研究（A级）；是2026年最有分量的候选项目之一。",
"08-egypt-early-dynastic-tombs.qmd":"目前仅有政府/发掘公告（D级）；尚未发现正式学术报告。",
"09-troy-agora.qmd":"目前仅有媒体/发掘公告（D级）；把该空间解释为“agora”仍属初步判断。",
"10-alexandria-tigris.qmd":"有多年系统田野研究支持（B级），但2026年报道是对既有项目的阶段性综合，并非首次发现地点。",
"11-arsinoe-china-greece.qmd":"首季机构性田野报告（D/C级）；国际合作意义突出，但尚未形成重大解释性突破。",
"12-uspallata-ancient-dna.qmd":"顶级同行评议研究（A级）；在古基因组、同位素、病原体、古气候、考古和原住民社区合作方面整合度很高。",
"13-urartian-irrigation.qmd":"同行评议专业期刊研究（B级）；遥感证据较强，但部分古代运河的年代归属仍依赖空间推断。",
"14-dide-west-iron-smelting.qmd":"同行评议专业期刊研究（B级）。",
"15-kush-faience.qmd":"同行评议专业期刊研究（B级）；目前是可靠识别的纳帕塔中期费昂斯生产作坊。",
"16-iliad-mummy.qmd":"发掘公告与初步专家识读（D→C级）；纸草尚未正式完整发表。",
"17-amazon-earthworks.qmd":"顶级同行评议研究（A级）；是原央视名单中明显遗漏的重要候选。",
"18-chan-chan-tomb.qmd":"重大田野发现，已有官方记录和广泛国际报道；完整同行评议研究仍待发表。",
"19-celtic-ancient-dna.qmd":"顶级同行评议研究（A级）；应与同期关于日耳曼语传播人口背景的古基因组研究合并理解。",
"20-sulawesi-rock-art.qmd":"顶级同行评议研究（A级）；是原央视名单中最重要的遗漏项目之一。",
"21-maya-mathematician.qmd":"同行评议专业期刊研究；对玛雅铭文学和科学史具有很高解释价值。",
"22-hittite-royal-archive.qmd":"重大田野发现（D/C级）；主要依据官方公告，泥板仍在释读，完整学术出版尚待完成。",
"23-camarones-smallpox.qmd":"顶级同行评议古病原体基因组研究（A级）。",
}

BACKGROUND={
"21-maya-mathematician.qmd":("""## 主要学术背景 | Scholarly background

**中文。** 古典期玛雅数学与天文学长期主要通过纪念碑铭文、历法记录和少数抄本传统来研究，但知识生产者本人通常是匿名的。Xultun 10K-2的壁画房间保存了大量小型计算文本、抄本制作相关证据和不同等级的书吏形象，使研究者能够把抽象的“玛雅科学”放回具体的工作空间、训练关系和知识劳动之中。

**English.** Classic Maya mathematics and astronomy have traditionally been studied through monumental inscriptions, calendrical records and the small surviving codex tradition, while the people who produced this knowledge usually remain anonymous. The mural room in Xultun Structure 10K-2 preserves numerous small calculation texts, evidence related to book production and depictions of ranked scribes, allowing “Maya science” to be reconstructed as situated intellectual labour within a specific workspace and training community.

"""),
"22-hittite-royal-archive.qmd":("""## 主要学术背景 | Scholarly background

**中文。** 赫梯国家史高度依赖哈图沙王室档案，因此首都以外成组出土的王室文书尤其重要。Šamuḫa是赫梯政治、宗教和军事体系中的关键区域中心；如果Kayalıpınar泥板确属同一档案群，它们可以提供不同于首都视角的战争、行政、疾病、占卜和王室仪式记录。

**English.** Hittite political history depends heavily on the royal archives from Hattusa, making coherent groups of royal documents from outside the capital especially valuable. Šamuḫa was an important regional centre within the Hittite political, religious and military system; if the Kayalıpınar tablets form a coherent archive, they can provide a perspective on warfare, administration, disease, divination and royal ritual that differs from the capital-centred record.

"""),
"23-camarones-smallpox.qmd":("""## 主要学术背景 | Scholarly background

**中文。** 欧洲接触后传染病造成的美洲人口崩溃是殖民史和生物考古学的核心问题，但长期主要依赖文献、人口模型和间接病理证据。古病原体基因组学能够直接识别感染个体，并比较古代病毒与后来的全球谱系，从而把“哪一种病原体何时进入美洲”转化为可以由分子证据检验的问题。

**English.** The demographic collapse associated with post-contact epidemics is central to colonial history and bioarchaeology in the Americas, but it has long been reconstructed mainly from documentary sources, demographic models and indirect pathological evidence. Ancient pathogen genomics can identify infections directly and compare ancient viruses with later global lineages, turning questions about which pathogens entered the Americas and when into testable molecular problems.

"""),
}

CAPTION_TRANSLATIONS={
"图1—受热、未受热与氟化骨骼的发光与FTIR比较":"图1—受热、未受热与氟化骨骼的发光与FTIR比较 / Figure 1—Luminescence and FTIR comparison of heated, unheated and fluorinated bone",
"图2—Wonderwerk Cave各发掘方格烧骨比例":"图2—Wonderwerk Cave各发掘方格烧骨比例 / Figure 2—Proportions of burnt bone across Wonderwerk Cave excavation squares",
"图3—早更新世烧骨证据的分析图版":"图3—早更新世烧骨证据的分析图版 / Figure 3—Analytical evidence for Early Pleistocene burnt bone",
"图1—Marathousa 1遗址与木器发现背景":"图1—Marathousa 1遗址与木器发现背景 / Figure 1—Marathousa 1 site and wooden-tool context",
"图2—43万年前木制手持工具及加工痕迹":"图2—43万年前木制手持工具及加工痕迹 / Figure 2—Handheld wooden tools and modification traces from about 430 ka",
"图3—木器使用痕迹与比较分析":"图3—木器使用痕迹与比较分析 / Figure 3—Use traces and comparative analysis of the wooden implements",
"图1—贝加尔湖墓地、年代与鼠疫阳性个体分布":"图1—贝加尔湖墓地、年代与鼠疫阳性个体分布 / Figure 1—Lake Baikal cemeteries, chronology and plague-positive individuals",
"图2—古代鼠疫感染个体的亲属关系与疫情结构":"图2—古代鼠疫感染个体的亲属关系与疫情结构 / Figure 2—Kinship and outbreak structure among plague-positive individuals",
"图3—早期鼠疫杆菌的系统发育位置":"图3—早期鼠疫杆菌的系统发育位置 / Figure 3—Phylogenetic position of early Yersinia pestis",
"图1—阿尔吉什蒂希尼利与亚拉拉特平原研究区":"图1—阿尔吉什蒂希尼利与亚拉拉特平原研究区 / Figure 1—Argishtikhinili and the Ararat Plain study area",
"图2—遗址周边古代与现代水管理景观":"图2—遗址周边古代与现代水管理景观 / Figure 2—Ancient and modern water-management landscape around the site",
"图3—遥感识别的运河、古河道与地形信息":"图3—遥感识别的运河、古河道与地形信息 / Figure 3—Remotely sensed canals, palaeochannels and terrain",
"图1—Sanam神庙及费昂斯作坊位置":"图1—Sanam神庙及费昂斯作坊位置 / Figure 1—Location of Sanam Temple and the faience workshop",
"图2—神庙后部生产设施与作坊遗迹":"图2—神庙后部生产设施与作坊遗迹 / Figure 2—Production installations and workshop remains behind the temple",
"图3—费昂斯珠、废品与生产证据":"图3—费昂斯珠、废品与生产证据 / Figure 3—Faience beads, wasters and production evidence",
"图1—西南亚马孙Aquiry土方工程区域分布":"图1—西南亚马孙Aquiry土方工程区域分布 / Figure 1—Regional distribution of Aquiry earthworks in southwestern Amazonia",
"图2—LiDAR揭示的几何土方工程":"图2—LiDAR揭示的几何土方工程 / Figure 2—Geometric earthworks revealed by LiDAR",
"图3—土方工程密度与区域尺度模型":"图3—土方工程密度与区域尺度模型 / Figure 3—Earthwork density and regional-scale modelling",
"图1—凯尔特语起源与传播的竞争模型":"图1—凯尔特语起源与传播的竞争模型 / Figure 1—Competing models for Celtic origins and dispersal",
"图2—青铜时代相关人口移动与遗传结构":"图2—青铜时代相关人口移动与遗传结构 / Figure 2—Bronze Age population movements and genetic structure",
"图3—古基因组对凯尔特语传播模型的约束":"图3—古基因组对凯尔特语传播模型的约束 / Figure 3—Ancient-genomic constraints on Celtic dispersal models",
"图1—苏拉威西东南部岩画地点与区域位置":"图1—苏拉威西东南部岩画地点与区域位置 / Figure 1—Rock-art sites and regional setting in Southeast Sulawesi",
"图2—Liang Metanduno手印岩画及最小年代":"图2—Liang Metanduno手印岩画及最小年代 / Figure 2—Liang Metanduno hand stencil and minimum age",
"图3—激光烧蚀铀系测年与岩画年代关系":"图3—激光烧蚀铀系测年与岩画年代关系 / Figure 3—Laser-ablation U-series dating and the age of the rock art",
}

PRIORITY=["New York Times","BBC","CNN","Guardian","Smithsonian","Associated Press","Science News","Nature News","Nature Portfolio","National Geographic","Scientific American","Archaeology Magazine"]

def normalize_media(txt):
    pat=r"## 主要媒体报道 \| Major media coverage\n\n([\s\S]*?)(?=\n## )"
    m=re.search(pat,txt)
    if not m:return txt
    bullets=[]
    seen=set()
    for line in m.group(1).splitlines():
        line=line.strip()
        if not line.startswith("- ["): continue
        um=re.search(r"\((https?://[^)]+)\)",line)
        if not um: continue
        url=um.group(1)
        low=line.lower()
        if url in seen: continue
        if "original article" in low or "original report" in low or "article page" in low:
            continue
        seen.add(url); bullets.append(line)
    def score(line):
        for i,p in enumerate(PRIORITY):
            if p.lower() in line.lower():return i
        return 99
    ranked=sorted(enumerate(bullets),key=lambda x:(score(x[1]),x[0]))
    ordered=[x[1] for x in ranked]
    if len(ordered)>5:
        body="### 主要报道 | Major coverage\n\n"+"\n".join(ordered[:5])+"\n\n### 其他报道 | Additional coverage\n\n"+"\n".join(ordered[5:])
    else:
        body="\n".join(ordered)
    return txt[:m.start()]+"## 主要媒体报道 | Major media coverage\n\n"+body+"\n"+txt[m.end():]

for path in sorted(Path("discoveries").glob("*.qmd")):
    txt=path.read_text(encoding="utf-8")
    name=path.name
    # Rebuild Evidence status idempotently: exactly one English line + one Chinese line.
    if name in EVIDENCE_ZH:
        pat=r"(\*\*Evidence status / 证据状态\*\*  \n)([\s\S]*?)(?=\n\*\*CCTV status / 央视遴选状态\*\*)"
        m=re.search(pat,txt)
        if m:
            raw=m.group(2).strip()
            first=raw.splitlines()[0].strip() if raw else ""
            english=re.sub(r"^(?:English:\s*)+","",first).strip()
            repl=m.group(1)+f"English: {english}  \n中文：{EVIDENCE_ZH[name]}\n"
            txt=txt[:m.start()]+repl+txt[m.end():]
    # Add scholarly background to 21-23.
    if name in BACKGROUND and "## 主要学术背景 | Scholarly background" not in txt:
        txt=txt.replace("## 主要发现 | Major findings",BACKGROUND[name]+"## 主要发现 | Major findings")
    # Make generic link-only statement bilingual.
    txt=txt.replace("版权许可未确认可复制，本站不保存图片文件。","版权许可未确认可复制，本站不保存图片文件。 / Reuse permission has not been confirmed; the image file is not stored on this site.")
    # Bilingual local figure captions.
    for zh,bi in CAPTION_TRANSLATIONS.items():
        txt=txt.replace(zh,bi)
    # Replace verbose English-only key-image guidance with compact bilingual status text.
    kp=r"## 关键图像与许可 \| Key images and permissions[\s\S]*?(?=## 页面图像 \| Page images)"
    if re.search(kp,txt):
        local='<img src="../figures/' in txt
        if local:
            rep=("## 关键图像与许可 | Key images and permissions\n\n"
                 "**中文。** 下列图像来自已核查许可的学术出版物；图注同时标明来源、作者、许可与原文链接。若单幅图含第三方版权材料，自动抓取程序会跳过该图并改用原图链接。\n\n"
                 "**English.** The images below come from scholarly publications with verified reuse licences. Each caption records the source, author, licence and original link. If an individual figure contains third-party rights language, the automated fetcher skips it and the page falls back to a source-image link.\n\n")
        else:
            rep=("## 关键图像与许可 | Key images and permissions\n\n"
                 "**中文。** 这些图像具有解释价值，但目前没有确认可由本站重新发布的许可，因此本站不复制图片文件，只提供原始图像或来源页面链接。\n\n"
                 "**English.** These images are interpretively useful, but permission for republication on this site has not been confirmed. The site therefore does not copy the image files and provides links to the original images or source pages instead.\n\n")
        txt=re.sub(kp,rep,txt)
    txt=normalize_media(txt)
    path.write_text(txt,encoding="utf-8")
