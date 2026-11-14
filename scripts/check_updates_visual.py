#!/usr/bin/env python3
"""Desktop/mobile layout assertions and screenshots of the rendered update feature.

Needs Playwright and a system Chromium/Chrome. Serves local output only; does not
visit original sources, rewrite source pages, publish, or change monitoring state.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading
from playwright.sync_api import sync_playwright


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site',type=Path,default=Path('docs'))
    parser.add_argument('--output',type=Path,default=Path('work/updates-visual'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'layout-results.json').unlink(missing_ok=True)
    chrome=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('google-chrome-stable')
    if not chrome:raise RuntimeError('System Chrome/Chromium required')
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(args.site.resolve())))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    registry=json.loads((Path(__file__).resolve().parents[1]/'updates.json').read_text())
    public=[r for r in registry['records'] if r['state'] in ('baseline','reviewed')]
    results=[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=chrome,args=['--no-sandbox','--disable-dev-shm-usage'])
            for label,width,height in [('desktop',1440,1000),('mobile',390,844)]:
                for filename in ('index.html','update-history.html'):
                    page=browser.new_page(viewport={'width':width,'height':height},is_mobile=label=='mobile')
                    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                    response=page.goto(f'http://127.0.0.1:{server.server_port}/{filename}',wait_until='networkidle')
                    assert response.status==200
                    expected=min(len(public),registry['homepage_limit']) if filename=='index.html' else len(public)
                    assert page.locator('.update-card').count()==expected
                    assert page.locator('.update-category').all_text_contents()
                    assert page.locator('.update-card [lang=zh]').count()==expected*2
                    assert page.locator('.update-card [lang=en]').count()==expected*2
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), filename+': horizontal overflow'
                    for card in page.locator('.update-card').all():
                        assert card.evaluate('(el)=>el.scrollWidth<=el.clientWidth'), 'Card content overflow'
                    if filename=='index.html':
                        positions=page.evaluate('''() => ({hero:document.querySelector('.homepage-hero').getBoundingClientRect().bottom,
                            updates:document.querySelector('#latest-updates').getBoundingClientRect().top,
                            map:document.querySelector('iframe').getBoundingClientRect().top,
                            last:document.querySelector('.updates-panel').getBoundingClientRect().bottom})''')
                        assert positions['hero']<positions['updates']<positions['last']<positions['map']
                        panel=page.locator('.latest-updates-grid')
                        columns=panel.evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").length')
                        assert columns==(1 if label=='mobile' else 2), columns
                        page.evaluate("window.scrollTo(0, document.querySelector('#latest-updates').getBoundingClientRect().top + window.scrollY - 110)")
                        page.screenshot(path=str(args.output/f'{label}-latest-viewport.png'))
                        page.locator('.update-card').first.screenshot(path=str(args.output/f'{label}-update-card.png'))
                    page.screenshot(path=str(args.output/f'{label}-{Path(filename).stem}.png'),full_page=True)
                    assert not errors, errors
                    results.append({'viewport':label,'page':filename,'cards':expected,'horizontal_overflow':False,'page_errors':errors})
                    if label=='mobile' and filename=='index.html':
                        page.evaluate('window.scrollTo(0,0)')
                        page.wait_for_function("document.querySelector('.navbar-toggler').getBoundingClientRect().top >= 0")
                        page.locator('.navbar-toggler').click()
                        link=page.get_by_role('link',name='更新日志 Updates',exact=True)
                        link.wait_for(state='visible')
                        link.click()
                        page.wait_for_url('**/update-history.html')
                        assert page.locator('.update-card').count()==len(public)
                    page.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    (args.output/'layout-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Latest Updates visual QA passed: desktop/mobile homepage, complete history and mobile navigation.')


if __name__=='__main__':main()
