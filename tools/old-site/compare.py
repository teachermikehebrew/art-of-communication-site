#!/usr/bin/env python3
"""Screenshot every page on the old WordPress server and on the local static
build, then pixel-compare them. Usage: compare.py [width] [slug ...]"""
import os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageChops

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "shots")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OLD_IP = "147.79.119.163"
LOCAL = "http://127.0.0.1:8765"
Image.MAX_IMAGE_PIXELS = None

def shoot(url, out, width, height, rules=None):
    """Load like a visitor: move the mouse, scroll to the bottom and back (fires
    delayed scripts, lazy images and Divi's scroll animations), then take a
    full-page shot. The Bloom pop-up is suppressed with its own 'seen' cookie."""
    from playwright.sync_api import sync_playwright
    if os.path.exists(out): os.remove(out)
    host = url.split("/")[2]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=["--headless=new", "--mute-audio"] + ([f"--host-resolver-rules={rules}"] if rules else []))
        ctx = b.new_context(viewport={"width": width, "height": 900}, device_scale_factor=1)
        ctx.add_cookies([{"name": "etBloomCookie_optin_5", "value": "true", "domain": host.split(":")[0], "path": "/"},
                         {"name": "etBloomCookie_optin_3", "value": "true", "domain": host.split(":")[0], "path": "/"}])
        pg = ctx.new_page()
        try:
            pg.goto(url, wait_until="networkidle", timeout=90000)
        except Exception:
            pass
        pg.mouse.move(200, 200)
        total = pg.evaluate("document.documentElement.scrollHeight")
        y = 0
        while y < total:
            y += 700; pg.mouse.wheel(0, 700); pg.wait_for_timeout(120)
            total = pg.evaluate("document.documentElement.scrollHeight")
        pg.wait_for_timeout(1500)
        pg.evaluate("window.scrollTo(0,0)"); pg.wait_for_timeout(1200)
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=out, full_page=True)
        b.close()
    return os.path.exists(out)

def trim(im):
    """Crop the empty tail below the page content (window is taller than most pages)."""
    g = im.convert("L"); w, h = g.size; px = g.load(); bg = px[w // 2, h - 1]
    y = h - 1
    while y > 0 and all(abs(px[x, y] - bg) < 4 for x in range(0, w, max(1, w // 40))): y -= 1
    return im.crop((0, 0, w, y + 1))

def compare(slug, width):
    name = slug or "index"
    path = f"/{slug}/" if slug else "/"
    h = 18000 if width > 800 else 26000
    old = os.path.join(OUT, f"{name}-{width}-old.png")
    new = os.path.join(OUT, f"{name}-{width}-new.png")
    shoot(f"https://artofcommunication.life{path}", old, width, h,
          f"MAP artofcommunication.life {OLD_IP},MAP www.artofcommunication.life {OLD_IP}")
    shoot(f"{LOCAL}{path}", new, width, h)
    if not (os.path.exists(old) and os.path.exists(new)):
        return name, None, "screenshot failed"
    a, b = trim(Image.open(old).convert("RGB")), trim(Image.open(new).convert("RGB"))
    note = "" if a.size == b.size else f"height old {a.height} vs new {b.height}"
    hh = min(a.height, b.height)
    diff = ImageChops.difference(a.crop((0, 0, width, hh)), b.crop((0, 0, width, hh))).convert("L")
    changed = sum(1 for v in diff.getdata() if v > 24)
    pct = 100.0 * changed / (width * hh)
    if pct > 0.05:
        bbox = diff.point(lambda v: 255 if v > 24 else 0).getbbox()
        note += f" diff box {bbox}"
    return name, pct, note

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 1440
    slugs = sys.argv[2:] or [l.strip() for l in open(os.path.join(ROOT, "slugs.txt")) if l.strip() != "#"]
    slugs = ["" if s == "/" else s for s in slugs]
    with ThreadPoolExecutor(3) as ex:
        for name, pct, note in ex.map(lambda s: compare(s, width), slugs):
            print(f"{name:66s} {'FAIL' if pct is None else f'{pct:6.2f}%'}  {note}", flush=True)
