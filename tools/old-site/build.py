#!/usr/bin/env python3
"""Turn the mirrored WordPress pages (./raw) into static pages for GitHub Pages.

Writes into the site repo given as argv[1]:
  <slug>/index.html for every mirrored page (index.html for the home page),
  404.html, and the /wp-content + /wp-includes asset trees from ./site.
"""
import hashlib, html as htmllib, os, re, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from patches import PATCHES

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW, SITE = os.path.join(ROOT, "raw"), os.path.join(ROOT, "site")
DEST = sys.argv[1]
HOST = "artofcommunication.life"

# Our own host (not learn./staging. subdomains), plain or JSON-escaped.
SELF = re.compile(r'(?:https?:)?(\\?/\\?/)(?:www\.)?artofcommunication\.life(?=[\\/"\'\s<>)?#]|$)')

# Stand-in for WordPress's admin-ajax.php, which a static host doesn't have.
# The Bloom pop-up's sign-up goes straight to its Kit form (Bloom's own
# settings: service=convertkit, list_id=9323923); everything else (Bloom
# impression stats, plugin pings) is answered locally with an empty success.
AJAX_SHIM = """<script>
(function ($) {
  if (!$ || !$.ajax) return;
  var realAjax = $.ajax;
  $.ajax = function (url, opts) {
    var o = typeof url === 'object' ? url : $.extend({}, opts, { url: url });
    if (!o || !o.url || String(o.url).indexOf('admin-ajax.php') === -1) return realAjax.apply(this, arguments);
    var d = $.Deferred(), data = o.data || {};
    if (o.beforeSend) o.beforeSend();
    if (data.action === 'bloom_subscribe') {
      var sub = {}; try { sub = JSON.parse(data.subscribe_data_array || '{}'); } catch (e) {}
      fetch('https://app.kit.com/forms/' + (sub.list_id || '9323923') + '/subscriptions', {
        method: 'POST', headers: { 'Accept': 'application/json' },
        body: new URLSearchParams({ email_address: sub.email || '', first_name: sub.name || '' })
      }).then(function (r) { return r.ok ? { success: 'Subscribed' } : { error: 'Something went wrong. Please try again.' }; })
        .catch(function () { return { error: 'Something went wrong. Please try again.' }; })
        .then(function (res) { if (o.success) o.success(res); if (o.complete) o.complete(); d.resolve(res); });
    } else {
      setTimeout(function () { if (o.success) o.success(null); if (o.complete) o.complete(); d.resolve(null); }, 0);
    }
    return d.promise();
  };
})(window.jQuery);
</script>
"""

HEAD_JUNK = [
    r'<link[^>]+rel=["\']https://api\.w\.org/["\'][^>]*>\s*',
    r'<link[^>]+rel=["\']alternate["\'][^>]+(?:wp-json|oembed|feed)[^>]*>\s*',
    r'<link[^>]+(?:wp-json|oembed|/feed/)[^>]+rel=["\']alternate["\'][^>]*>\s*',
    r'<link[^>]+rel=["\']EditURI["\'][^>]*>\s*',
    r'<link[^>]+rel=["\']shortlink["\'][^>]*>\s*',
    r'<link[^>]+rel=["\']pingback["\'][^>]*>\s*',
    r'<meta[^>]+name=["\']generator["\'][^>]*>\s*',
]

# Web fonts: use exactly the Google @font-face rules the old site's LiteSpeed
# bundle served for each page (raw/fonts/<page>.css, made by fontfaces.py).
# LiteSpeed fetched Google's CSS server-side, which returns static .ttf files
# (they render slightly wider than the variable fonts a browser gets) and it
# silently dropped some families (Cormorant Garamond, Manrope, ...). Visitors
# saw that result, so the static site reproduces it instead of the raw links.
GF_DIR = "wp-content/gfonts"
def page_fonts(name):
    src = os.path.join(RAW, "fonts", name + ".css")
    faces = re.findall(r'@font-face\s*\{[^}]*\}', open(src).read())
    google = [f for f in faces if "fonts.gstatic.com" in f]
    out = os.path.join(DEST, GF_DIR, name + ".css")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write("\n".join(google) + "\n")
    return "/" + GF_DIR + "/" + name + ".css"

def transform(html, slug):
    fonts_href = page_fonts(slug)
    html = html.replace("?LSCWP_CTRL=before_optm", "").replace("&#038;LSCWP_CTRL=before_optm", "")
    html = html.replace("LSCWP_CTRL=before_optm", "")
    for pat in HEAD_JUNK:
        html = re.sub(pat, "", html, flags=re.I)
    # Keep canonical / og:url absolute; make every other self-link root-relative.
    keep = {}
    def protect(m):
        k = f"\x00KEEP{len(keep)}\x00"; keep[k] = m.group(0); return k
    html = re.sub(r'<link[^>]+rel=["\']canonical["\'][^>]*>|<meta[^>]+property=["\']og:url["\'][^>]*>', protect, html)
    html = SELF.sub(lambda m: "", html)  # "https://artofcommunication.life/x" -> "/x", "https:\/\/…\/x" -> "\/x"
    for k, v in keep.items(): html = html.replace(k, v)
    # A link that was exactly the home URL is now empty ("" or "\/" remains fine); fix bare href="".
    html = re.sub(r'(href=)(["\'])\2', r'\1\2/\2', html)
    html, n = re.subn(r"<link[^>]+href=['\"]https://fonts\.googleapis\.com/css2?\?[^>]*>\s*", "", html)
    html = html.replace("</head>", f'<link rel="stylesheet" id="old-site-fonts-css" href="{fonts_href}" media="all" />\n</head>', 1)
    # Cascade order. On the old site LiteSpeed folded every other stylesheet and
    # <style> block (head and body) into one bundle at the top of <head>, then
    # came Divi's dynamic CSS, then Divi's "deferred" CSS. The unbundled pages
    # have a different order, which flips which rule wins in places (blog posts
    # got 54px section padding and 1.7 line-height instead of 4% and 1.8).
    # Rebuild the old order: move body <style> blocks up into <head>, then put
    # dynamic, then deferred, last.
    head_end = html.find("</head>")
    moved_styles = []
    def take_body_style(m):
        moved_styles.append(m.group(0)); return ""
    body = re.sub(r"<style[^>]*>.*?</style>\s*", take_body_style, html[head_end:], flags=re.S)
    html = html[:head_end] + body
    tail = []
    for pat in (r"<link[^>]+id=['\"]divi-dynamic-css['\"][^>]*>\s*",
                r"<link[^>]+id=['\"][^'\"]*-deferred-[^'\"]*['\"][^>]*>\s*"):
        for m in list(re.finditer(pat, html)):
            tail.append(m.group(0).strip())
        html = re.sub(pat, "", html)
    html = html.replace("</head>", "\n".join(moved_styles + tail) + "\n</head>", 1)
    # Shim right after jQuery loads, before any plugin script can call $.ajax.
    html, n = re.subn(r'(<script[^>]+/wp-includes/js/jquery/jquery\.min\.js[^>]*></script>\s*)', r'\1' + AJAX_SHIM.replace('\\', '\\\\'), html, count=1)
    if n == 0 and "jquery" in html.lower():
        print("  WARN: no jquery tag found for shim in", slug)
    return html

def main():
    pages = sorted(f[:-5] for f in os.listdir(RAW) if f.endswith(".html"))
    for name in pages:
        html = open(os.path.join(RAW, name + ".html"), encoding="utf-8").read()
        out = transform(html, name)
        for page, old, new, *cnt in PATCHES:
            if page != name: continue
            n, want = out.count(old), (cnt[0] if cnt else 1)
            assert n == want, f"patch for {page} matched {n} times (expected {want}): {old[:60]}"
            out = out.replace(old, new)
        if name == "index": path = os.path.join(DEST, "index.html")
        elif name == "404": path = os.path.join(DEST, "404.html")
        else: path = os.path.join(DEST, name, "index.html")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(out)
        leftover = len(re.findall(r'//(?:www\.)?artofcommunication\.life(?![\w.-])', out))
        print(f"{name:70s} {len(out):>7d} bytes  abs-self-links left: {leftover}")
    for tree in ("wp-content", "wp-includes"):
        src = os.path.join(SITE, tree)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(DEST, tree), dirs_exist_ok=True)
    # Divi's cached CSS points background images at https://artofcommunication.life/...
    # Make those site-relative so the files load from wherever the site is hosted
    # (the preview repo, or the real domain if it ever moves).
    for tree in ("wp-content", "wp-includes"):
        for d, _, files in os.walk(os.path.join(DEST, tree)):
            for f in files:
                if not f.endswith((".css", ".js")): continue
                path = os.path.join(d, f)
                txt = open(path, encoding="utf-8", errors="surrogateescape").read()
                new = re.sub(r'https?://(?:www\.)?artofcommunication\.life(?=/)', "", txt)
                if new != txt:
                    open(path, "w", encoding="utf-8", errors="surrogateescape").write(new)

if __name__ == "__main__":
    main()
