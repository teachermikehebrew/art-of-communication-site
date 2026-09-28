#!/usr/bin/env python3
"""Mirror the old WordPress/Divi site (still served by Hostinger) into static files.

The domain now points at GitHub Pages, so every request is pinned to the old
Hostinger server with curl --resolve. Output goes to ./raw (untouched HTML) and
./site (assets, at their original /wp-content/... and /wp-includes/... paths).
"""
import os, re, subprocess, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor

OLD_IP = "147.79.116.118"
HOST = "artofcommunication.life"
ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")
SITE = os.path.join(ROOT, "site")

PAGES = [
    "", "foundations", "empathy", "doctors", "rabbis", "coaching", "blog",
    "moving-from-fight-flight-to-a-team-thats-tight",
    "how-to-stay-grounded-when-emotions-run-high-practical-nvc-skills",
    "how-to-ask-for-what-you-really-want-the-power-of-dialogue-requests",
    "accompaniment", "artofempathyinterest", "cancellation-policy-1-1-coaching",
    "cohort", "community-gateway", "community", "course-cancellation-policy",
    "course-cancellation-policy-selfpaced", "foundationsinactive", "guidethanks",
    "home-closed-for-current-cohort", "how-we-relate-to-money", "introsession",
    "level-3-art-of-honesty", "meditators-course", "newsletter",
    "pastparticipants", "paymentorientation", "paymentthanks", "preferences",
    # "Intro Course" funnel: the Bloom pop-up and Kit sequence 2719511 link here
    "introcourse", "aoc-intro-9v2k7", "presence-flow-x4m1", "connection-lab-8p3z",
    "heart-skill-j6r2", "deep-learning-q9n5", "attuned-q9n5",
]

def fetch(url, dest=None):
    """GET url from the old server. Returns bytes (or writes dest). None on non-200."""
    args = ["curl", "-s", "-L", "--max-time", "60", "-w", "%{http_code}",
            "--resolve", f"{HOST}:443:{OLD_IP}", "--resolve", f"www.{HOST}:443:{OLD_IP}",
            "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/140 Safari/537.36"]
    if dest:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        r = subprocess.run(args + ["-o", dest, url], capture_output=True)
        code = r.stdout.decode()[-3:]
        if code != "200":
            if os.path.exists(dest): os.remove(dest)
            return None
        return True
    r = subprocess.run(args + [url], capture_output=True)
    body, code = r.stdout[:-3], r.stdout[-3:].decode()
    return body if code == "200" else None

# Absolute URLs on our own host, in plain or JSON-escaped form.
ABS = re.compile(r'(?:https?:)?(?:\\?/\\?/)(?:www\.)?artofcommunication\.life((?:\\?/[^\s"\'<>()\\,]*)*)')
CSS_URL = re.compile(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)')
CSS_IMPORT = re.compile(r'@import\s+[\'"]([^\'"]+)[\'"]')

def local_path(path):
    """Map a site path like /wp-content/x.css?ver=1 to a file under SITE."""
    path = urllib.parse.unquote(path.split("?")[0].split("#")[0])
    return os.path.join(SITE, path.lstrip("/"))

def is_asset(path):
    p = path.split("?")[0]
    return p.startswith(("/wp-content/", "/wp-includes/")) and not p.endswith("/")

seen = set()
failed = []

def grab_asset(path):
    """Download one asset; if CSS, recurse into url()/@import references."""
    clean = path.replace("\\/", "/").split("#")[0]
    key = clean.split("?")[0]
    if key in seen: return
    seen.add(key)
    dest = local_path(clean)
    if not os.path.exists(dest):
        ok = fetch(f"https://{HOST}{clean}", dest)
        if not ok:
            failed.append(clean); return
    if key.endswith(".css"):
        css = open(dest, encoding="utf-8", errors="replace").read()
        base = key.rsplit("/", 1)[0] + "/"
        refs = CSS_URL.findall(css) + CSS_IMPORT.findall(css)
        subs = []
        for ref in refs:
            if ref.startswith("data:"): continue
            m = ABS.match(ref)
            if m: p = m.group(1)
            elif ref.startswith(("http:", "https:", "//")): continue  # external (e.g. Google Fonts)
            elif ref.startswith("/"): p = ref
            else: p = urllib.parse.urljoin(base, ref)
            if is_asset(p): subs.append(p)
        for p in subs: grab_asset(p)

def main():
    os.makedirs(RAW, exist_ok=True)
    asset_paths = set()
    for slug in PAGES:
        name = slug or "index"
        html = fetch(f"https://{HOST}/{slug + '/' if slug else ''}?LSCWP_CTRL=before_optm")
        if html is None:
            print("PAGE FAILED", slug); continue
        open(os.path.join(RAW, name + ".html"), "wb").write(html)
        text = html.decode("utf-8", errors="replace")
        for m in ABS.finditer(text):
            p = m.group(1).replace("\\/", "/")
            if is_asset(p): asset_paths.add(p)
        # root-relative references too (rare in WP output, but cheap to catch)
        for m in re.finditer(r'(?:src|href|srcset|data-src)=["\'](/wp-(?:content|includes)/[^"\']+)', text):
            asset_paths.add(m.group(1))
        # srcset lists: split out every candidate URL
        for m in re.finditer(r'srcset=["\']([^"\']+)', text):
            for cand in m.group(1).split(","):
                u = cand.strip().split(" ")[0]
                mm = ABS.match(u)
                if mm and is_asset(mm.group(1)): asset_paths.add(mm.group(1))
        print("page", slug or "/", len(html))
    # a 404 page for the static host
    nf = subprocess.run(["curl", "-s", "--resolve", f"{HOST}:443:{OLD_IP}",
                         f"https://{HOST}/this-page-does-not-exist-xyz/?LSCWP_CTRL=before_optm"], capture_output=True).stdout
    open(os.path.join(RAW, "404.html"), "wb").write(nf)
    for m in ABS.finditer(nf.decode("utf-8", "replace")):
        p = m.group(1).replace("\\/", "/")
        if is_asset(p): asset_paths.add(p)
    print(len(asset_paths), "assets referenced by pages")
    with ThreadPoolExecutor(12) as ex:
        list(ex.map(grab_asset, sorted(asset_paths)))
    # second pass for CSS pulled in by threads (grab_asset recursion is already inside)
    print("downloaded/seen:", len(seen), "failed:", len(failed))
    for f in sorted(set(failed)): print("  FAILED", f)

if __name__ == "__main__":
    main()
