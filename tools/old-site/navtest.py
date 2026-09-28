from playwright.sync_api import sync_playwright
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
items=["Foundations Course","Art of Empathy (Level II)","Doctors Cohort","Rabbis Cohort","Executive Coaching","Blog","About","Contact","Free Intro Course"]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=["--headless=new","--mute-audio"])
    ctx=b.new_context(viewport={"width":1440,"height":900})
    for it in items:
        pg=ctx.new_page(); pg.goto("http://127.0.0.1:8765/",wait_until="domcontentloaded"); pg.wait_for_timeout(1500)
        popup_url=None; req=[]
        pg.on("request", lambda r: req.append(r.url) if r.is_navigation_request() else None)
        try:
            with ctx.expect_page(timeout=3000) as np:
                pg.get_by_text(it, exact=True).first.click()
            popup_url=np.value.url
        except Exception:
            pg.wait_for_timeout(1500)
        print(f"{it:28s} -> {popup_url or pg.url} {'(new tab)' if popup_url else ''} {[r for r in req if 'mailto' in r]}")
        pg.close()
    b.close()
