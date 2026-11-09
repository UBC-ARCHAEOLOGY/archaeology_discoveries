#!/usr/bin/env python3
from pathlib import Path
import re, sys

errors=[]
mojibake_markers=["Ã¡","Ã©","Ã­","Ã³","Ãº","Ã±","â","Â ","Â·"]
for path in sorted(Path("discoveries").glob("*.qmd")):
    txt=path.read_text(encoding="utf-8")
    name=path.name
    # Metadata fields must use the current evidence/importance schema.
    if "**Evidence grade / 证据等级**" not in txt:
        errors.append(f"{name}: missing evidence grade")
    if "**Scholarly importance assessment / 学术重要性评估**" not in txt:
        errors.append(f"{name}: missing scholarly importance assessment")
    if "**Evidence status / 证据状态**" in txt:
        errors.append(f"{name}: obsolete evidence-status field remains")
    if "**Lead researchers / 主要负责人**" in txt:
        errors.append(f"{name}: obsolete lead-researchers field remains")
    if "**Key researchers / project leads / 主要研究者或项目负责人**" not in txt:
        errors.append(f"{name}: missing key researchers/project leads field")
    meta = txt.split("::: {.discovery-meta}",1)[1].split(":::",1)[0] if "::: {.discovery-meta}" in txt else ""
    if "**Evidence grade / 证据等级**" in meta:
        grade_block=meta.split("**Evidence grade / 证据等级**",1)[1].split("**Scholarly importance assessment / 学术重要性评估**",1)[0]
        if not any(g in grade_block for g in ["A —","B —","C —","D —"]):
            errors.append(f"{name}: evidence grade must be A, B, C, or D")
    if "**Scholarly importance assessment / 学术重要性评估**" in meta:
        imp_block=meta.split("**Scholarly importance assessment / 学术重要性评估**",1)[1].split("**CCTV status / 央视遴选状态**",1)[0]
        if "/" not in imp_block:
            errors.append(f"{name}: scholarly importance assessment should be bilingual")
    # Guard against the former repeated placeholder bug.
    placeholder="Reuse permission has not been confirmed; the image file is not stored on this site."
    for line in txt.splitlines():
        if line.count(placeholder) > 1:
            errors.append(f"{name}: repeated image-permission placeholder")
            break
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
    if "## 学术出版物 | Academic publications" not in txt:
        errors.append(f"{name}: missing academic publications section")
    if "## 主要媒体报道 | Major media coverage" not in txt:
        errors.append(f"{name}: missing media coverage section")

print("Discovery-page structural checks completed.")


# Markdown list-spacing QA: a bold paragraph/label followed immediately by a
# list marker is parsed by Pandoc as running text rather than a list.
# Check both top-level pages and discovery pages.
all_qmd = list(Path(".").glob("*.qmd")) + list(Path("discoveries").glob("*.qmd"))
for path in sorted(all_qmd):
    txt = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(txt.splitlines(), start=1):
        lines = txt.splitlines()
        if lineno < len(lines):
            current = lines[lineno-1].strip()
            nxt = lines[lineno].lstrip()
            if re.fullmatch(r"\*\*[^*]+\*\*", current) and re.match(r"[-+*]\s+", nxt):
                errors.append(f"{path}: line {lineno}: blank line required before Markdown list")

if errors:
    print("\n".join(errors))
    sys.exit(2)
print("Bilingual and Markdown-layout QA passed.")
