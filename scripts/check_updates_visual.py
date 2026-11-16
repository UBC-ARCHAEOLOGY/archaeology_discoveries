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
import updates as u
from datetime import datetime, timedelta, timezone
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
                    expected=len(u.recent(registry)) if filename=='index.html' else len(public)
                    assert page.locator('.update-card').count()==expected
                    assert page.locator('.update-category').all_text_contents()
                    baselines=page.locator('.update-card[data-update-state="baseline"]')
                    assert baselines.locator('.update-date').count()==0
                    if filename=='index.html':
                        assert baselines.locator('time').count()==0
                        assert page.locator('.update-dates').count()==0
                        assert baselines.count()==0
                        assert page.locator('#past-week-updates').count()==1
                        assert page.locator('.updates-group-title').count()==len(u.CATEGORIES)
                    else:
                        assert baselines.locator('.update-recorded-date time').count()==baselines.count()
                        assert page.locator('.update-dates').count()==expected
                    assert page.locator('.update-card [lang=zh]').count()==expected*2
                    assert page.locator('.update-card [lang=en]').count()==expected*2
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), filename+': horizontal overflow'
                    for card in page.locator('.update-card').all():
                        assert card.evaluate('(el)=>el.scrollWidth<=el.clientWidth'), 'Card content overflow'
                    if filename=='index.html':
                        positions=page.evaluate('''() => ({hero:document.querySelector('.homepage-hero').getBoundingClientRect().bottom,
                            updates:document.querySelector('#past-week-updates').getBoundingClientRect().top,
                            map:document.querySelector('iframe').getBoundingClientRect().top,
                            last:document.querySelector('.updates-panel').getBoundingClientRect().bottom})''')
                        assert positions['hero']<positions['map']<positions['updates']<positions['last']
                        if expected:
                            panel=page.locator('.latest-updates-grid').filter(has=page.locator('.update-card')).first
                            columns=panel.evaluate('(el)=>getComputedStyle(el).gridTemplateColumns.split(" ").filter(x=>parseFloat(x)>0).length')
                            assert columns==(1 if label=='mobile' else min(2,panel.locator('.update-card').count())), columns
                        else:
                            assert page.locator('.updates-empty:visible').count()==len(u.CATEGORIES)
                        page.evaluate("window.scrollTo(0, document.querySelector('#past-week-updates').getBoundingClientRect().top + window.scrollY - 110)")
                        page.screenshot(path=str(args.output/f'{label}-latest-viewport.png'))
                        if expected:
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
                for report in sorted((args.site/'reports').glob('*.html')):
                    filename='reports/'+report.name
                    page=browser.new_page(viewport={'width':width,'height':height},is_mobile=label=='mobile')
                    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                    response=page.goto(f'http://127.0.0.1:{server.server_port}/{filename}',wait_until='networkidle')
                    assert response.status==200
                    assert '|' in page.locator('main h1').inner_text(), 'Bilingual report title required'
                    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), filename+': horizontal overflow'
                    if report.stem.count('-')>2:
                        assert page.get_by_text('中文。',exact=True).count()==3
                        assert page.get_by_text('English.',exact=True).count()==3
                    assert not errors, errors
                    page.screenshot(path=str(args.output/f'{label}-reports-{report.stem}.png'),full_page=True)
                    results.append({'viewport':label,'page':filename,'horizontal_overflow':False,'page_errors':errors})
                    page.close()
            boundary=browser.new_page()
            boundary.clock.install(time=datetime(2026,11,14,16,1,tzinfo=timezone.utc))
            boundary.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle')
            assert '2026-11-09 – 2026-11-15' in boundary.locator('.updates-window').inner_text()
            assert 'Asia/Shanghai' in boundary.locator('.updates-window').inner_text()
            boundary.close()
            # Existing entries must age out without a scheduled build or publication.
            future=browser.new_page()
            day=u.today()+timedelta(days=8)
            future.clock.install(time=datetime(day.year,day.month,day.day,4,tzinfo=timezone.utc))
            future.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle')
            assert future.locator('.update-card').count()==0
            assert future.locator('.updates-empty:visible').count()==len(u.CATEGORIES)
            assert day.isoformat() in future.locator('.updates-window').inner_text()
            future.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    (args.output/'layout-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('Latest Updates visual QA passed: desktop/mobile homepage, complete history and mobile navigation.')
    print('Weekly report viewport checks:',sum(row['page'].startswith('reports/') for row in results))


if __name__=='__main__':main()
