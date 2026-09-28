#!/usr/bin/env python3
"""For every mirrored page, pull the @font-face rules out of the LiteSpeed CSS
bundle the old site actually served for that page, and save them to
./raw/fonts/<page>.css. Those are exactly the web fonts visitors got (LiteSpeed
silently dropped some families, e.g. Cormorant Garamond / Manrope)."""
import os, re, subprocess, time

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")
OUT = os.path.join(RAW, "fonts")
IP = "147.79.116.118"

def get(url):
    r = subprocess.run(["curl", "-s", "--max-time", "60", "-w", "%{http_code}",
                        "--resolve", f"artofcommunication.life:443:{IP}", url], capture_output=True)
    return r.stdout[:-3].decode("utf-8", "replace"), r.stdout[-3:].decode()

def main():
    os.makedirs(OUT, exist_ok=True)
    for f in sorted(os.listdir(RAW)):
        if not f.endswith(".html"): continue
        name = f[:-5]
        slug = "" if name == "index" else name
        path = "/this-page-does-not-exist-xyz/" if name == "404" else (f"/{slug}/" if slug else "/")
        faces = None
        for attempt in range(4):
            html, _ = get(f"https://artofcommunication.life{path}")
            bundles = re.findall(r'/wp-content/litespeed/css/[0-9a-f]+\.css', html)
            css_all, ok = "", bool(bundles)
            for b in bundles:
                css, code = get(f"https://artofcommunication.life{b}")
                if code != "200": ok = False; break
                css_all += css
            if ok:
                faces = re.findall(r'@font-face\s*\{[^}]*\}', css_all)
                break
            time.sleep(5)  # bundle not generated yet; LiteSpeed builds it on the first request
        if faces is None:
            print(f"{name:66s} NO BUNDLE"); continue
        fams = sorted(set(re.findall(r'font-family:\s*["\']?([^;"\']+)', "\n".join(faces))))
        open(os.path.join(OUT, name + ".css"), "w").write("\n".join(faces) + "\n")
        print(f"{name:66s} {len(faces):3d} faces  {', '.join(fams)}")

if __name__ == "__main__":
    main()
