#!/usr/bin/env python3
from pathlib import Path

CAPTIONS = {
"图1—受热、未受热与氟化骨骼的发光与FTIR比较":"Figure 1—Luminescence and FTIR comparison of heated, unheated and fluorinated bone",
"图2—Wonderwerk Cave各发掘方格烧骨比例":"Figure 2—Proportions of burnt bone across Wonderwerk Cave excavation squares",
"图3—早更新世烧骨证据的分析图版":"Figure 3—Analytical evidence for Early Pleistocene burnt bone",
"图1—Marathousa 1遗址与木器发现背景":"Figure 1—Marathousa 1 site and wooden-tool context",
"图2—43万年前木制手持工具及加工痕迹":"Figure 2—Handheld wooden tools and modification traces from about 430 ka",
"图3—木器使用痕迹与比较分析":"Figure 3—Use traces and comparative analysis of the wooden implements",
"图1—贝加尔湖墓地、年代与鼠疫阳性个体分布":"Figure 1—Lake Baikal cemeteries, chronology and plague-positive individuals",
"图2—古代鼠疫感染个体的亲属关系与疫情结构":"Figure 2—Kinship and outbreak structure among plague-positive individuals",
"图3—早期鼠疫杆菌的系统发育位置":"Figure 3—Phylogenetic position of early Yersinia pestis",
"图1—阿尔吉什蒂希尼利与亚拉拉特平原研究区":"Figure 1—Argishtikhinili and the Ararat Plain study area",
"图2—遗址周边古代与现代水管理景观":"Figure 2—Ancient and modern water-management landscape around the site",
"图3—遥感识别的运河、古河道与地形信息":"Figure 3—Remotely sensed canals, palaeochannels and terrain",
"图1—Sanam神庙及费昂斯作坊位置":"Figure 1—Location of Sanam Temple and the faience workshop",
"图2—神庙后部生产设施与作坊遗迹":"Figure 2—Production installations and workshop remains behind the temple",
"图3—费昂斯珠、废品与生产证据":"Figure 3—Faience beads, wasters and production evidence",
"图1—西南亚马孙Aquiry土方工程区域分布":"Figure 1—Regional distribution of Aquiry earthworks in southwestern Amazonia",
"图2—LiDAR揭示的几何土方工程":"Figure 2—Geometric earthworks revealed by LiDAR",
"图3—土方工程密度与区域尺度模型":"Figure 3—Earthwork density and regional-scale modelling",
"图1—凯尔特语起源与传播的竞争模型":"Figure 1—Competing models for Celtic origins and dispersal",
"图2—青铜时代相关人口移动与遗传结构":"Figure 2—Bronze Age population movements and genetic structure",
"图3—古基因组对凯尔特语传播模型的约束":"Figure 3—Ancient-genomic constraints on Celtic dispersal models",
"图1—苏拉威西东南部岩画地点与区域位置":"Figure 1—Rock-art sites and regional setting in Southeast Sulawesi",
"图2—Liang Metanduno手印岩画及最小年代":"Figure 2—Liang Metanduno hand stencil and minimum age",
"图3—激光烧蚀铀系测年与岩画年代关系":"Figure 3—Laser-ablation U-series dating and the age of the rock art",
}

for path in Path("discoveries").glob("*.qmd"):
    txt = path.read_text(encoding="utf-8")
    before = txt
    for zh,en in CAPTIONS.items():
        pair = zh + " / " + en
        repeated = pair + " / " + en
        while repeated in txt:
            txt = txt.replace(repeated, pair)
        if zh in txt and pair not in txt:
            txt = txt.replace(zh, pair)
    if txt != before:
        path.write_text(txt, encoding="utf-8")
