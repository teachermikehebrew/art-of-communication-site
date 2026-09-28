from playwright.sync_api import sync_playwright
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CH,args=["--headless=new"])
    pg=b.new_page(viewport={"width":1440,"height":900})
    errors=[]; failed=[]; kit=[]
    pg.on("console", lambda m: errors.append(m.text) if m.type=="error" else None)
    pg.on("pageerror", lambda e: errors.append("PAGEERROR "+str(e)))
    pg.on("requestfailed", lambda r: failed.append(r.url))
    pg.on("response", lambda r: failed.append(f"{r.status} {r.url}") if r.status>=400 and "127.0.0.1" in r.url else None)
    def fake_kit(route, req):
        kit.append((req.method, req.url, req.post_data))
        route.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin":"*"}, body='{"status":"success"}')
    pg.route("https://app.kit.com/forms/**", fake_kit)
    pg.goto("http://127.0.0.1:8765/", wait_until="networkidle")
    pg.click("text=Get the Guide"); pg.wait_for_timeout(1500)
    vis=pg.evaluate("[...document.querySelectorAll('.et_bloom_popup')].map(e=>e.className.includes('et_bloom_visible'))")
    print("popup visible after click:", vis)
    pg.fill(".et_bloom_popup.et_bloom_visible input[placeholder='Email']", "test@example.com")
    with pg.expect_navigation(timeout=15000):
        pg.click(".et_bloom_popup.et_bloom_visible .et_bloom_submit_subscription")
    print("kit request:", kit)
    print("landed on:", pg.url, "| title:", pg.title())
    print("console errors:", errors[:10])
    print("failed/4xx local requests:", [f for f in failed if 'google' not in f][:10])
    b.close()
