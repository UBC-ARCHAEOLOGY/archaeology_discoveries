#!/usr/bin/env python3
from pathlib import Path
import re, sys

errors=[]
mojibake_markers=["Ã¡","Ã©","Ã­","Ã³","Ãº","Ã±","â","Â ","Â·"]
for path in sorted(Path("discoveries").glob("*.qmd")):
    txt=path.read_text(encoding="utf-8")
    name=path.name
    if "English: English:" in txt:
        errors.append(f"{name}: repeated English evidence-status prefix")
    evidence_chunk = txt.split("**Evidence status / 证据状态**",1)[1].split("**CCTV status / 央视遴选状态**",1)[0] if "**Evidence status / 证据状态**" in txt else ""
    if evidence_chunk.count("中文：") != 1:
        errors.append(f"{name}: evidence status must contain exactly one Chinese line")
    for marker in mojibake_markers:
        if marker in txt:
            errors.append(f"{name}: possible mojibake marker {marker!r}")
    for section,next_section in [
        ("## 主要学术背景 | Scholarly background","## 主要发现 | Major findings"),
        ("## 主要发现 | Major findings","## 学术重要性 | Intellectual significance"),
        ("## 学术重要性 | Intellectual significance","## 学术出版物 | Academic publications"),
    ]:
        if section not in txt:
            errors.append(f"{name}: missing {section}")
            continue
        start=txt.index(section)
        end=txt.find(next_section,start+len(section))
        chunk=txt[start:end if end!=-1 else None]
        if "**中文" not in chunk:
            errors.append(f"{name}: {section} missing Chinese paragraph label")
        if "**English" not in chunk:
            errors.append(f"{name}: {section} missing English paragraph label")
    if "**Evidence status / 证据状态**" in txt:
        block=txt.split("**Evidence status / 证据状态**",1)[1].split("**CCTV status / 央视遴选状态**",1)[0]
        if "English:" not in block or "中文：" not in block:
            errors.append(f"{name}: evidence status not bilingual")
    if "## 学术出版物 | Academic publications" not in txt:
        errors.append(f"{name}: missing academic publications section")
    if "## 主要媒体报道 | Major media coverage" not in txt:
        errors.append(f"{name}: missing media coverage section")

if errors:
    print("\n".join(errors))
    sys.exit(2)
print("Bilingual discovery-page QA passed for all discovery pages.")
