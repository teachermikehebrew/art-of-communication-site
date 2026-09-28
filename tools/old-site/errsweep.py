from playwright.sync_api import sync_playwright
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
slugs=[l.strip() for l in open("slugs.txt") if l.strip()]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=["--headless=new","--mute-audio"])
    for s in slugs:
        path="/" if s=="/" else f"/{s}/"
        pg=b.new_page(viewport={"width":1440,"height":900}); errs=[]; bad=[]
        pg.on("console", lambda m: errs.append(m.text[:140]) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append("PAGEERROR "+str(e)[:140]))
        pg.on("response", lambda r: bad.append(f"{r.status} {r.url[:110]}") if r.status>=400 else None)
        try: pg.goto("http://127.0.0.1:8765"+path, wait_until="networkidle", timeout=60000)
        except Exception as e: errs.append("GOTO "+str(e)[:80])
        pg.mouse.wheel(0,2000); pg.wait_for_timeout(1200)
        if errs or bad: print(f"{s}: errors={errs[:4]} bad={bad[:4]}")
        pg.close()
    b.close()
print("sweep done", len(slugs))
