#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests
from bs4 import BeautifulSoup

ROOT=Path("docs")
UA={"User-Agent":"Mozilla/5.0 archaeology-discoveries-link-check/2.1"}
TIMEOUT=8

internal_broken=[]
external={}
for html in ROOT.rglob("*.html"):
    soup=BeautifulSoup(html.read_text(encoding="utf-8",errors="ignore"),"html.parser")
    for a in soup.find_all("a",href=True):
        href=a["href"].strip()
        if not href or href.startswith(("#","mailto:","javascript:","tel:")): continue
        if href.startswith(("http://","https://")):
            external.setdefault(href,None)
            continue
        # Strip query/fragment and resolve local HTML/assets.
        clean=unquote(href.split("#")[0].split("?")[0])
        if not clean: continue
        target=(html.parent/clean).resolve()
        if clean.endswith("/"): target=target/"index.html"
        if not target.exists():
            internal_broken.append({"page":str(html.relative_to(ROOT)),"href":href})

def check(url):
    try:
        r=requests.head(url,headers=UA,allow_redirects=True,timeout=TIMEOUT)
        if r.status_code in (405,501) or r.status_code>=500:
            r=requests.get(url,headers=UA,allow_redirects=True,timeout=TIMEOUT,stream=True)
        code=r.status_code
        if code in (401,403,406,418,429): status="restricted"
        elif 200<=code<400: status="ok"
        elif code==404: status="404"
        else: status="other"
        return {"status":status,"code":code,"final_url":r.url}
    except Exception as e:
        return {"status":"unreachable","error":str(e)[:180]}

urls=list(external)
with ThreadPoolExecutor(max_workers=12) as pool:
    futs={pool.submit(check,u):u for u in urls}
    for fut in as_completed(futs):
        u=futs[fut]
        try: external[u]=fut.result()
        except Exception as e: external[u]={"status":"unreachable","error":str(e)[:180]}

report={"internal_broken":internal_broken,"external":external}
(ROOT/"link-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
bad404=[(u,v) for u,v in external.items() if v.get("status")=="404"]
unreach=[(u,v) for u,v in external.items() if v.get("status")=="unreachable"]
lines=[
"# Link QA report / 链接QA报告","",
f"- Internal broken links / 站内失效链接: **{len(internal_broken)}**",
f"- External 404 links / 外部404: **{len(bad404)}**",
f"- External unreachable / 外部无法连接: **{len(unreach)}**",
"",
"## Internal broken links / 站内失效链接",""
]
lines += [f"- `{x['page']}` → `{x['href']}`" for x in internal_broken] or ["- None / 无"]
lines += ["","## External 404 / 外部404",""]
lines += [f"- {u}" for u,v in bad404] or ["- None / 无"]
lines += ["","## External unreachable / 外部无法连接",""]
lines += [f"- {u} — {v.get('error','')}" for u,v in unreach] or ["- None / 无"]
(ROOT/"link-report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

print(f"Internal broken: {len(internal_broken)}")
print(f"External 404: {len(bad404)}")
print(f"External unreachable: {len(unreach)}")
# Internal broken links are build failures. External 404s are reported but do not block deploy.
if internal_broken:
    sys.exit(2)
