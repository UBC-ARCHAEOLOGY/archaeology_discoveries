#!/usr/bin/env python3
from __future__ import annotations
import re, requests
from ftfy import fix_text
from pathlib import Path

UA={"User-Agent":"archaeology-discoveries/2.1 (https://github.com/ZCJing2022/archaeology_discoveries)"}

DATA={
"01-wonderwerk-fire.qmd":[
("10.1371/journal.pone.0347480",
"文章提出以骨骼发光性质快速筛查受热微型骨骼，并用FTIR交叉验证，在Wonderwerk Cave早更新世地层中识别新的用火证据。它的贡献同时包括方法创新和年代推进，但论文支持的是早期人群利用并维持火，而不是证明已经掌握人工取火。",
"The paper introduces bone luminescence as a rapid screening method for heat-altered microfaunal remains, validated against FTIR, and applies it to Early Pleistocene deposits at Wonderwerk Cave. Its contribution is both methodological and chronological, but the evidence supports the use and maintenance of fire rather than demonstrating deliberate fire-making." )],
"02-yunxian-homo-erectus.qmd":[
("10.1126/sciadv.ady2270",
"文章利用与郧县头骨同层石英砾石的宇生核素 ²⁶Al/¹⁰Be 埋藏测年，将化石层位测定为 1.77±0.08 Ma。其核心贡献是把东亚原位人类头骨记录推进到接近德马尼西的年代，但这一年代与近期形态学解释之间仍存在需要进一步检验的张力。",
"The study uses cosmogenic ²⁶Al/¹⁰Be burial dating of quartz clasts from the fossil-bearing layer to obtain an age of 1.77 ± 0.08 Ma. Its main contribution is to place securely contextualized East Asian hominin crania close in age to Dmanisi, while leaving an important tension with recent morphological interpretations that requires further testing.")],
"03-megalopolis-wood-tools.qmd":[
("10.1073/pnas.2515479123",
"文章系统分析 Marathousa 1 的 144 件木质遗存，确认一件约81厘米长的桤木手持工具和一件较小的柳/杨木工具具有人工制作和使用痕迹。研究不仅把可确认的手持木器推到约43万年前，也说明中更新世技术系统不能仅依据石器来重建。",
"The paper systematically analyses 144 wooden remains from Marathousa 1 and identifies an approximately 81-cm alder implement and a smaller willow/poplar tool with anthropogenic manufacture and use traces. It both extends the record of securely identified handheld wooden tools to about 430 ka and demonstrates why Middle Pleistocene technology cannot be reconstructed from lithics alone.")],
"04-denisovans-yunnan.qmd":[
("10.1038/s41586-026-10976-9",
"文章通过形态预筛、ZooMS 与古蛋白分析，从蝙蝠洞大量碎骨中确认多件丹尼索瓦人遗存，并扩展其已知身体部位与牙齿变异范围。它把古蛋白组学从“鉴别人群”推进到建立更丰富的丹尼索瓦化石样本。",
"Using morphological prescreening, ZooMS and palaeoproteomics, the study identifies multiple Denisovan remains among highly fragmented bones from Bianfu Cave and expands the known anatomical and dental variation of the group. It demonstrates how palaeoproteomics can move beyond identification to building a richer Denisovan fossil record."),
("10.1038/s41586-026-10997-4",
"文章把约16.7万—13.4万年前的人类化石与约19万—7万年前的文化序列、石器、动物骨骼和环境记录结合起来，重建丹尼索瓦人的狩猎、骨骼利用与石器策略。其意义在于首次以完整遗址体系讨论丹尼索瓦人的行为与生态适应。",
"The paper integrates hominin fossils dated to roughly 167–134 ka with a cultural sequence spanning about 190–70 ka, lithics, fauna and environmental records. It provides the first site-scale reconstruction of Denisovan hunting, bone use, technological strategy and ecological adaptation."),
("10.1038/s41586-026-11132-z",
"文章对徐家窑中更新世人类遗存进行古蛋白分析，并把所得蛋白组与东亚其他中更新世化石比较，以讨论丹尼索瓦人共有的形态特征。它扩大了丹尼索瓦人在华北的化石证据，并为重新审视东亚若干争议人类化石提供分子依据。",
"The study applies palaeoproteomics to Middle Pleistocene human remains from Xujiayao and compares them with other East Asian fossils to investigate shared Denisovan morphology. It broadens the Denisovan fossil record in northern China and supplies molecular evidence for reassessing several taxonomically debated East Asian hominins.")],
"05-oldest-dog-genomes.qmd":[
("10.1038/s41586-026-10170-x",
"文章获得安纳托利亚 Pınarbaşı 约1.58万年前和英国 Gough's Cave 约1.43万年前犬科个体的核基因组，并确认其属于早期家犬而非狼。研究显示晚旧石器时代家犬已经分布于西欧与安纳托利亚，并把可靠的直接遗传证据推进到农业出现之前。",
"The study obtains nuclear genomes from canids including a ~15.8-ka individual from Pınarbaşı and a ~14.3-ka individual from Gough's Cave, identifying them as early dogs rather than wolves. It demonstrates that dogs were already distributed across western Europe and Anatolia in the Late Palaeolithic, well before agriculture."),
("10.1038/s41586-026-10112-7",
"配套研究通过更大规模的古代犬科基因组资料重建欧洲早期家犬的群体史、连续性与混合过程。它说明晚冰期犬群并非孤立个案，而是后来欧洲犬类遗传史的重要组成部分。",
"The companion study uses a much larger ancient canid genomic dataset to reconstruct the population history, continuity and admixture of early European dogs. It shows that Late Glacial dogs were not isolated curiosities but important contributors to the later genomic history of European dogs.")],
"06-romito-genetic-disease.qmd":[
("10.1056/NEJMc2513616",
"这篇通讯利用古DNA确定 Romito 1 与 Romito 2 均为女性且为一级亲属，并在 NPR2 基因中识别出与 Maroteaux 型肢端肢中发育不全相符的变异。文章把一个长期依赖骨骼形态推断的经典古病理案例推进到分子临床诊断层面，同时为史前残障个体的照护讨论增加直接证据。",
"This report uses ancient DNA to show that Romito 1 and Romito 2 were both female first-degree relatives and identifies NPR2 variants consistent with Maroteaux-type acromesomelic dysplasia. It moves a classic palaeopathological case from morphology-based inference to molecular clinical diagnosis and strengthens discussion of care for disabled individuals in prehistory.")],
"07-baikal-plague.qmd":[
("10.1038/s41586-026-10540-5",
"文章在贝加尔湖地区46名狩猎采集者中检测到18例鼠疫杆菌阳性个体，并重建早期 Yersinia pestis 基因组、亲属关系和死亡模式。研究表明，在缺乏农业聚落高密度人口和经典跳蚤传播适应的情况下，鼠疫仍可能造成高死亡率暴发。",
"The study detects Yersinia pestis in 18 of 46 hunter-gatherers from the Lake Baikal region and reconstructs early pathogen genomes, kinship and mortality patterns. It shows that highly lethal plague outbreaks could occur without dense farming settlements or the later classic flea-borne transmission adaptations.")],
"08-egypt-early-dynastic-tombs.qmd":[],
"09-troy-agora.qmd":[],
"10-alexandria-tigris.qmd":[
("10.34780/te7a-edx2",
"文章汇总 Charax Spasinou 项目的地表调查、陶器和城市考古成果，讨论这座希腊化—帕提亚时期港口城市的规模、年代与功能。它的重要性不在于2026年才找到遗址，而在于把长期已知的位置转化为可以分析街区、宗教、手工业、港口与区域贸易的城市考古资料。",
"The article synthesizes surface survey, ceramic and urban evidence from the Charax Spasinou project to clarify the scale, chronology and functions of this Hellenistic–Parthian port city. Its contribution is not the first location of the site, but the conversion of a long-suspected location into an archaeologically analyzable urban landscape of neighbourhoods, religion, craft, harbour infrastructure and regional trade.")],
"11-arsinoe-china-greece.qmd":[],
"12-uspallata-ancient-dna.qmd":[
("10.1038/s41586-026-10233-z",
"文章分析46名古代个体的全基因组，并结合稳定同位素、病原体DNA、考古和古气候资料，显示乌斯帕利亚塔谷地从狩猎采集向农业转型时存在长期遗传连续性。后期危机阶段的亲属迁移进一步说明，农业转型并非单纯的人口替代，而与家庭网络、疾病和环境压力共同作用。",
"The paper analyses whole genomes from 46 ancient individuals together with isotopes, pathogen DNA, archaeology and palaeoclimate. It demonstrates long-term genetic continuity across the local transition from foraging to farming and shows how kin-structured migration later mediated crises involving disease, nutrition and environmental stress.")],
"13-urartian-irrigation.qmd":[
("10.15184/aqy.2026.10344",
"文章利用卫星影像、多光谱数据和数字地形模型绘制阿尔吉什蒂希尼利周边1019公里水管理要素，其中约134.6公里被识别为可能的古代运河。研究把水利工程从单一设施提升为国家组织、农业生产与景观改造的区域性问题，同时提醒古代运河年代仍有部分依赖空间推断。",
"The study uses satellite imagery, multispectral data and digital terrain modelling to map 1,019 km of water-management features around Argishtikhinili, including about 134.6 km interpreted as possible ancient canals. It reframes irrigation as a regional problem of state organization, agricultural production and landscape transformation while noting that some ancient attribution remains spatially inferred.")],
"14-dide-west-iron-smelting.qmd":[
("10.1007/s10437-026-09653-z",
"文章报告 Didé West 1 约公元前4世纪至公元4世纪的冶铁作坊，分析35个炉基、多孔大型风嘴、炉渣和棕榈果核填料等证据。其核心贡献不是解决非洲冶铁起源，而是展示一种地方工艺传统如何在约八百年中保持基本稳定并发生有限调整。",
"The article reports an iron-smelting workshop at Didé West 1 used from roughly the fourth century BCE to the fourth century CE, analysing 35 furnace bases, large multiperforated tuyères, slag and palm-nut packing. Its central contribution is not to resolve the origin of African iron metallurgy, but to show how a local technological tradition persisted for about eight centuries while undergoing limited adjustment.")],
"15-kush-faience.qmd":[
("10.15184/aqy.2026.10434",
"文章通过 Sanam 神庙中的窑炉、模具、费昂斯珠、沙布提俑和生产废品，重建纳帕塔时期费昂斯生产体系。研究指出当地工匠使用与埃及不同的材料配方，并把神庙生产、专业知识与国家控制联系起来，从生产组织层面重新讨论库施与埃及的关系。",
"Using kilns, moulds, faience beads, shabtis and production waste from Sanam Temple, the article reconstructs a Napatan faience-production system. It identifies local recipes that differed from Egyptian practice and links temple production, specialist knowledge and state control, reframing Kushite–Egyptian relations through production organization rather than imitation alone.")],
"16-iliad-mummy.qmd":[],
"17-amazon-earthworks.qmd":[
("10.1038/s41586-026-10835-7",
"文章利用LiDAR调查和空间模型在西南亚马孙识别大量几何土方工程，并据此估算更广区域可能存在约2.4万—3万处前殖民土方遗迹。研究显著提高了对前殖民人口和土地利用强度的估计，但125万—300万人属于模型外推，应与直接考古计数区分。",
"The study combines LiDAR survey and spatial modelling to identify large numbers of geometric earthworks in southwestern Amazonia and estimate roughly 24,000–30,000 precolonial earthworks across the broader cultural region. It substantially raises estimates of settlement and land-use intensity, although the proposed population of 1.25–3 million is a modelled extrapolation rather than a direct count.")],
"18-chan-chan-tomb.qmd":[],
"19-celtic-ancient-dna.qmd":[
("10.1038/s41586-026-11198-9",
"文章汇集4587名古代个体的基因组资料，以欧洲青铜—铁器时代人口史检验多种凯尔特语扩散模型。结果支持约3000年前中东欧向西的人口移动与“凯尔特语自东向西传播”模型更相容，但作者明确强调基因流动不能等同于语言传播。",
"The paper compiles genome-wide data from 4,587 ancient individuals to test competing models of Celtic-language dispersal against Bronze–Iron Age demographic history. It finds westward population movement from east-central Europe around 3,000 years ago more compatible with an east-to-west Celtic model, while explicitly recognizing that genetic movement cannot be equated with language transmission."),
("10.1038/s41586-025-09064-1",
"配套论文利用大规模古基因组资料追踪与日耳曼语传播有关的斯堪的纳维亚人口变化，识别约4000年前进入瑞典以及后续铁器时代、迁徙时期的多阶段基因流。它为语言史提供人口学约束，而不是从DNA直接读取语言。",
"The companion study uses large-scale ancient genomic data to trace demographic changes in Scandinavia relevant to Germanic-language dispersal, identifying multiple phases of gene flow from around 4,000 years ago through the Iron Age and Migration Period. It constrains linguistic history demographically rather than treating DNA as direct evidence of language.")],
"20-sulawesi-rock-art.qmd":[
("10.1038/s41586-025-09968-y",
"文章采用激光烧蚀铀系测年分析覆盖在穆纳岛手印岩画之上的方解石，得到岩画至少6.78万年的最小年代。研究把可靠测年的图像传统推进到现代人穿越华莱西亚并向萨胡尔扩散的早期阶段，使象征行为、海洋迁徙和区域文化连续性能够在同一时间框架中讨论。",
"The study uses laser-ablation uranium-series dating of calcite overlying a hand stencil on Muna Island to establish a minimum age of 67.8 ka. It places a securely dated image-making tradition within the early modern-human dispersal through Wallacea toward Sahul, allowing symbolic behaviour, maritime movement and regional cultural continuity to be discussed within the same chronology.")],
"21-maya-mathematician.qmd":[
("10.15184/aqy.2026.10378",
"文章重新构建并释读 Xultun 10K-2 建筑东墙的 Text 19，识别出协调历法与金星、火星等周期的数学—天文公式，并确认末尾将成果归于 Sak Tahn Waax。它把古典玛雅科学从匿名知识体系转化为可以讨论具体知识工作者、书写空间和知识产权意识的考古对象。",
"The paper reconstructs and deciphers Text 19 on the east wall of Structure 10K-2 at Xultun, identifying a mathematical-astronomical formula that coordinates calendrical intervals with cycles including Venus and Mars and attributes the work to Sak Tahn Waax. It transforms Classic Maya science from an anonymous body of knowledge into an archaeological study of named intellectual workers, scholarly workspace and authorship.")],
"22-hittite-royal-archive.qmd":[],
"23-camarones-smallpox.qmd":[
("10.1126/science.aee6957",
"文章从智利北部 Camarones 9 两名早期殖民时期个体中重建出美洲最早的古代天花病毒基因组，并将其置于全球 variola 病毒系统发育树中。结果为欧洲接触后天花进入南美洲提供病原体本身的直接分子证据，并显示早期美洲毒株属于后来消失的谱系。",
"The study reconstructs the earliest ancient smallpox genomes yet recovered in the Americas from two early colonial individuals at Camarones 9 in northern Chile and places them within the global variola phylogeny. It provides direct molecular evidence for the introduction of smallpox into South America after European contact and shows that the early American viruses belonged to an extinct lineage.")]
}

UNPUBLISHED={
"08-egypt-early-dynastic-tombs.qmd":("Egypt State Information Service. (2026, June 20). *Ancient tomb discovery sheds light on early Egyptian funerary architecture*.","目前尚未发现正式同行评议论文。现有信息来自埃及最高文物委员会/国家信息服务的发掘公告，因此墓葬年代、建筑功能以及与后期金字塔工程之间的关系都应视为初步解释。","No peer-reviewed publication has yet been identified. Current information derives from the Egyptian Supreme Council of Antiquities/State Information Service field announcement, so chronology, architectural function and any relationship to later pyramid engineering remain preliminary interpretations.","https://sis.gov.eg/en/media-center/news/ancient-tomb-discovery-sheds-light-on-early-egyptian-funerary-architecture/"),
"09-troy-agora.qmd":("Hürriyet Daily News. (2026, September). *Troy’s ancient agora uncovered in recent excavations*.","目前没有针对2026年“最早agora”解释的同行评议论文。现有说法主要来自发掘团队接受媒体采访，因此晚青铜时代空间是否确为市场、以及“agora”这一术语是否适用，仍需等待正式建筑与出土物分析。","No peer-reviewed publication has yet established the 2026 “earliest agora” interpretation. The claim currently rests mainly on excavation-team statements to the media, so both the market function of the Late Bronze Age space and the use of the term “agora” await formal architectural and artefactual analysis.","https://www.hurriyetdailynews.com/troys-ancient-agora-uncovered-in-recent-excavations-226718"),
"11-arsinoe-china-greece.qmd":("Hellenic Ministry of Culture. (2026, October 16). *Greek-Chinese archaeological research at Angelokastro in Aetolia-Acarnania*.","2026年首季成果尚无同行评议论文，主要依据希腊文化部的项目报告。报告确认了柱廊庭院建筑、多期使用和相关遗物，但这一阶段的主要意义是建立长期田野资料基础，而不是已经形成新的古典城市史解释。","The first 2026 season has not yet produced a peer-reviewed publication and is documented primarily through the Hellenic Ministry of Culture project report. The report establishes a peristyle building, multiple use phases and associated finds, but the main contribution at this stage is the creation of a long-term field-data base rather than a new historical interpretation of the city.","https://www.culture.gov.gr/el/Information/SitePages/view.aspx?nID=5816"),
"16-iliad-mummy.qmd":("University of Barcelona. (2026, April 20). *Oxyrhynchus excavation identifies a Homeric Iliad text in a Roman-period mortuary context*.","纸草尚未正式发表，当前识读来自巴塞罗那大学考古队的研究公告。现有证据足以确认其与《伊利亚特》第二卷有关，但纸草在木乃伊中的精确位置及其是否具有仪式功能仍需等待正式纸草学出版。","The papyrus has not yet received a formal scholarly edition; its identification is currently reported through the University of Barcelona research announcement. The evidence supports an association with Book 2 of the *Iliad*, but the exact placement of the papyrus and whether it carried a deliberate ritual function await formal papyrological publication.","https://web.ub.edu/en/web/actualitat/w/oxyrhynchus-iliad-homer"),
"18-chan-chan-tomb.qmd":("Ministerio de Cultura del Perú / Proyecto Especial Complejo Arqueológico Chan Chan. (2026). *Informe preliminar sobre la plataforma funeraria de Utzh An, Chan Chan*.","目前尚无完整同行评议论文，主要依据秘鲁文化部和PECACH的发掘公告及采访。现阶段最可靠的学术价值是墓葬情境保存完整、至少38名个体及其随葬品关系可在原位研究；身份、年代细分和墓葬使用过程仍需正式报告。","No full peer-reviewed publication has yet appeared; the evidence currently comes from Peru's Ministry of Culture/PECACH field announcements and interviews. The strongest present contribution is the unusually intact mortuary context, allowing at least 38 individuals and associated grave goods to be studied in situ; detailed identity, chronology and tomb-use history await formal publication.","https://www.nytimes.com/topic/subject/archaeology-and-anthropology"),
"22-hittite-royal-archive.qmd":("Koç University / Türkiye Ministry of Culture and Tourism. (2026). *Kayalıpınar (Šamuḫa) excavation: Preliminary announcement of the Hittite royal archive*.","184块泥板仍在整理与释读，尚无完整档案学出版。新闻中关于疫情、王室丧葬、鸟卜和军事求援的内容属于初步释读；真正的历史意义必须等待逐片编号、抄本、翻译、年代和出土情境正式发表后才能评估。","The corpus of 184 tablets is still being catalogued and deciphered, and no complete scholarly edition has yet appeared. Reports of epidemic disease, royal funerals, bird divination and military requests are preliminary readings; the archive's historical significance will require formal publication of tablet numbers, copies, translations, dates and find contexts.","https://www.hurriyetdailynews.com/cuneiform-tablets-from-hittite-king-unearthed-227946")
}

def oa_status(doi):
    cc_by={"10.1371/journal.pone.0347480","10.1038/s41586-026-10540-5","10.15184/aqy.2026.10344","10.15184/aqy.2026.10434","10.1038/s41586-026-10835-7","10.1038/s41586-026-11198-9"}
    cc_by_nc_nd={"10.1073/pnas.2515479123","10.1038/s41586-025-09968-y"}
    cc_by_nc={"10.15184/aqy.2026.10378"}
    if doi in cc_by:
        return "开放获取，CC BY 4.0；单幅图仍需检查第三方署名。 / Open access, CC BY 4.0; individual figure credits are still checked."
    if doi in cc_by_nc_nd:
        return "开放获取，CC BY-NC-ND 4.0；原图仅按许可原样使用。 / Open access, CC BY-NC-ND 4.0; figures are used unmodified under the licence."
    if doi in cc_by_nc:
        return "开放获取，CC BY-NC 4.0。 / Open access, CC BY-NC 4.0."
    if doi=="10.1056/NEJMc2513616":
        return "可免费阅读，但不是Creative Commons许可；再利用需遵循NEJM权限政策。 / Free to read, but not Creative Commons licensed; reuse follows NEJM permissions."
    if doi=="10.34780/te7a-edx2":
        return "期刊页面为订阅访问；没有确认通用开放许可。 / Subscription access on the journal site; no general open licence confirmed."
    return "文章可在线访问；再利用许可与图像权利按出版方rights statement和单幅图署名核查。 / The article is accessible online; reuse and figure rights follow the publisher rights statement and individual credits."

def apa(doi):
    url="https://doi.org/"+doi
    r=requests.get(url,headers={**UA,"Accept":"text/x-bibliography; style=apa; locale=en-US"},timeout=30)
    r.raise_for_status()
    raw=r.content.decode("utf-8", errors="replace")
    return fix_text(re.sub(r"\s+"," ",raw.strip()))

def make_block(name, items):
    out=["## 学术出版物 | Academic publications",""]
    if items:
        for i,(doi,zh,en) in enumerate(items,1):
            try: citation=apa(doi)
            except Exception:
                citation=f"DOI: https://doi.org/{doi}"
            if len(items)>1:
                out += [f"### 论文 {i} | Paper {i}",""]
            out += [citation,"",f"**开放获取状态 | Open-access status.** {oa_status(doi)}","",f"**出版物内容（中文）。** {zh}","",f"**What the publication shows (English).** {en}",""]
    else:
        citation,zh,en,url=UNPUBLISHED[name]
        out += ["**尚无同行评议论文 | No peer-reviewed publication yet.**","",f"[{citation}]({url})","",f"**现有资料内容（中文）。** {zh}","",f"**What the current source shows (English).** {en}",""]
    out += ["<!-- APA-V2.1 -->",""]
    return "\n".join(out)

for path in sorted(Path("discoveries").glob("*.qmd")):
    name=path.name
    if name not in DATA:
        continue
    txt=path.read_text(encoding="utf-8")
    block=make_block(name,DATA[name])
    # Rebuild an existing APA module, or replace older publication sections.
    apa_pat=r"## 学术出版物 \| Academic publications[\s\S]*?<!-- APA-V2\.1 -->\n?"
    old_verify=r"## 论文核查 \| Publication verification[\s\S]*?(?=## 主要媒体报道 \| Major media coverage)"
    old_pubs=r"## 学术论文 \| Academic publications[\s\S]*?(?=## 主要媒体报道 \| Major media coverage)"
    if re.search(apa_pat,txt):
        txt=re.sub(apa_pat,block+"\n",txt)
    elif re.search(old_verify,txt):
        txt=re.sub(old_verify,block+"\n",txt)
    else:
        txt=re.sub(old_pubs,block+"\n",txt)
    path.write_text(txt,encoding="utf-8")
