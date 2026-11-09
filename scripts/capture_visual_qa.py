#!/usr/bin/env python3
from pathlib import Path
import shutil, subprocess, sys, time
from playwright.sync_api import sync_playwright

ROOT=Path("docs").resolve()
server=subprocess.Popen([sys.executable,"-m","http.server","8765","--directory",str(ROOT)],
                        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
OUT=Path("qa-screenshots")
OUT.mkdir(exist_ok=True)
chrome=shutil.which("google-chrome") or shutil.which("google-chrome-stable") or shutil.which("chromium")
if not chrome:
    print("No system Chrome/Chromium found; visual QA cannot run.",file=sys.stderr)
    sys.exit(2)

desktop_pages=[ROOT/"index.html",ROOT/"discoveries.html",ROOT/"map.html",ROOT/"under-review.html"]
desktop_pages += sorted((ROOT/"discoveries").glob("*.html"))
mobile_pages=[
    ROOT/"index.html",
    ROOT/"map.html",
    ROOT/"discoveries.html",
    ROOT/"under-review.html",
    ROOT/"discoveries/04-denisovans-yunnan.html",
    ROOT/"discoveries/07-baikal-plague.html",
    ROOT/"discoveries/17-amazon-earthworks.html",
    ROOT/"discoveries/20-sulawesi-rock-art.html",
]

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=chrome,args=["--no-sandbox","--disable-dev-shm-usage"])
    for src in desktop_pages:
        page=browser.new_page(viewport={"width":1440,"height":1000})
        url="http://127.0.0.1:8765/"+str(src.relative_to(ROOT)).replace("\\","/")
        page.goto(url,wait_until="networkidle",timeout=30000)
        page.evaluate("""async () => {
          for (let y=0; y<document.body.scrollHeight; y+=600) {
            window.scrollTo(0,y);
            await new Promise(r=>setTimeout(r,40));
          }
          window.scrollTo(0,0);
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path=str(OUT/(src.stem+"-desktop.png")),full_page=True)
        page.close()
    for src in mobile_pages:
        page=browser.new_page(viewport={"width":390,"height":844},is_mobile=True)
        url="http://127.0.0.1:8765/"+str(src.relative_to(ROOT)).replace("\\","/")
        page.goto(url,wait_until="networkidle",timeout=30000)
        page.evaluate("""async () => {
          for (let y=0; y<document.body.scrollHeight; y+=500) {
            window.scrollTo(0,y);
            await new Promise(r=>setTimeout(r,50));
          }
          window.scrollTo(0,0);
        }""")
        page.wait_for_timeout(700)
        page.screenshot(path=str(OUT/(src.stem+"-mobile.png")),full_page=True)
        page.close()
    browser.close()
server.terminate()
server.wait(timeout=5)
print(f"Captured {len(list(OUT.glob('*.png')))} visual-QA screenshots.")
