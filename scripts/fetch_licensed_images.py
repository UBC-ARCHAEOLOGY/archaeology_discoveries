#!/usr/bin/env python3
"""
Fetch only figures from publications whose article-level reuse licence has been
verified. Figure captions are screened for third-party rights language; those
figures are skipped and must be presented as link-only cards instead.

The script runs during GitHub Pages build and writes PNG files under
figures/discoveries/01 ... 20.
"""
from __future__ import annotations
import io, os, re, sys
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from PIL import Image

UA={"User-Agent":"Mozilla/5.0 (compatible; archaeology-discoveries/2.1; +https://github.com/ZCJing2022/archaeology_discoveries)"}
ROOT=Path("figures/discoveries")
ROOT.mkdir(parents=True,exist_ok=True)

RULES=[
    # folder, article URL, requested figure numbers, verified article licence
    ("01","https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0347480",[3,4,5],"CC BY 4.0"),
    ("03","https://pmc.ncbi.nlm.nih.gov/articles/PMC12890827/",[1,2,3],"CC BY-NC-ND 4.0"),
    ("07","https://pmc.ncbi.nlm.nih.gov/articles/PMC13275307/",[1,2,3],"CC BY 4.0"),
    ("13","https://www.cambridge.org/core/journals/antiquity/article/water-management-around-the-urartian-fortress-of-argishtikhinili-armenia/137974774D303DE4F7AE91B8581EAB7D",[1,2,3],"CC BY 4.0"),
    ("15","https://www.cambridge.org/core/journals/antiquity/article/crafting-power-in-kush-faience-production-and-state-control-in-the-napatan-region/A15CF88886CC39E3C6D4110DD58B94A5",[1,2,3,4],"CC BY 4.0"),
    ("17","https://pmc.ncbi.nlm.nih.gov/articles/PMC13558069/",[1,2,3],"CC BY 4.0"),
    ("19","https://www.nature.com/articles/s41586-026-11198-9",[1,2,3],"CC BY 4.0"),
    ("20","https://pmc.ncbi.nlm.nih.gov/articles/PMC12916292/",[1,2,3],"CC BY-NC-ND 4.0"),
]
RIGHTS_RE=re.compile(r"(reproduced with permission|copyright|©|courtesy of|image credit|photo credit)",re.I)

def figure_candidates(soup):
    figs=[]
    for f in soup.find_all(["figure","div"]):
        cls=" ".join(f.get("class",[])).lower()
        if f.name=="div" and not ("fig" in cls or "figure" in cls):
            continue
        img=f.find("img")
        if not img:
            continue
        cap=f.get_text(" ",strip=True)
        label=""
        for el in f.find_all(["span","div","strong","b"]):
            t=el.get_text(" ",strip=True)
            m=re.search(r"(?:Fig(?:ure)?\.?\s*)(\d+)",t,re.I)
            if m:
                label=m.group(1); break
        if not label:
            m=re.search(r"(?:Fig(?:ure)?\.?\s*)(\d+)",cap,re.I)
            if m: label=m.group(1)
        src=img.get("data-src") or img.get("data-original") or img.get("src")
        if src:
            figs.append((int(label) if label.isdigit() else None,src,cap))
    # dedupe preserving order
    out=[]; seen=set()
    for x in figs:
        key=x[1]
        if key not in seen:
            seen.add(key); out.append(x)
    return out

def to_png(data:bytes,dst:Path):
    im=Image.open(io.BytesIO(data))
    if im.mode not in ("RGB","RGBA","L","P"):
        im=im.convert("RGBA")
    im.save(dst,"PNG",optimize=True)

def fetch(folder,url,wanted,licence):
    outdir=ROOT/folder
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"LICENSE.txt").write_text(
        f"Article source: {url}\nVerified article licence: {licence}\n"
        "Each downloaded figure passed an automated caption screen for obvious "
        "third-party rights language. Human caption-level verification remains required.\n",
        encoding="utf-8")
    html=requests.get(url,headers=UA,timeout=45).text
    soup=BeautifulSoup(html,"html.parser")
    figs=figure_candidates(soup)
    bynum={n:(src,cap) for n,src,cap in figs if n is not None}
    log=[]
    for n in wanted:
        if n not in bynum:
            log.append(f"Fig {n}: not found")
            continue
        src,cap=bynum[n]
        if RIGHTS_RE.search(cap):
            log.append(f"Fig {n}: SKIPPED third-party/copyright wording: {cap[:240]}")
            continue
        imgurl=urljoin(url,src)
        try:
            r=requests.get(imgurl,headers=UA,timeout=45)
            r.raise_for_status()
            dst=outdir/f"fig{n}.png"
            to_png(r.content,dst)
            (outdir/f"fig{n}.txt").write_text(
                f"Figure {n}\nSource: {url}\nImage URL: {imgurl}\n"
                f"Licence: {licence}\nCaption: {cap}\n",encoding="utf-8")
            log.append(f"Fig {n}: downloaded -> {dst}")
        except Exception as e:
            log.append(f"Fig {n}: download failed: {e}")
    (outdir/"fetch.log").write_text("\n".join(log)+"\n",encoding="utf-8")
    print(folder,*log,sep="\n  ")

def main():
    for folder,url,wanted,licence in RULES:
        try: fetch(folder,url,wanted,licence)
        except Exception as e:
            print(f"{folder}: article fetch failed: {e}",file=sys.stderr)
            (ROOT/folder).mkdir(parents=True,exist_ok=True)
            (ROOT/folder/"fetch.log").write_text(f"Article fetch failed: {e}\n",encoding="utf-8")

if __name__=="__main__":
    main()
