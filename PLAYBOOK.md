# The Art of Communication — Website Rebuild Playbook

**Read this first in any new session.** It's written so a fresh Claude Code
session (no memory of prior conversations) can pick up exactly where things
left off.

## ⚠️ 2026-09-28 evening: the site is now a static copy of the OLD WordPress layout

**LIVE since 2026-09-28 ~16:28 GMT** (main = old-layout, commit 1177138), with
Mike's go-ahead. Live domain pixel-checked against the old server afterwards:
matches. Push over SSH (`origin` = `git@github.com:teachermikehebrew/art-of-communication-site.git`;
HTTPS has no stored credentials on Mike's Mac). Rollback: `git push -f origin 5e58c64:main`
restores the canvas design. A preview copy lived at teachermikehebrew.github.io
(repo `teachermikehebrew.github.io`, no CNAME). Mike to delete it himself
(deleting a repo is his call).

Danny didn't like the new canvas design ("drab", "informational"). Mike asked
to copy as much of the old layout as possible, across the board. Branch
`old-layout` does that. Everything below this section describes the canvas
design era and is **history**, kept for reference. The canvas artifact is
**no longer the design source of truth**.

**What the site is now.** The old Divi pages themselves, saved as static
HTML: `<slug>/index.html` for 37 pages (home = `index.html`), plus every
stylesheet, script, font and image they use, under `/wp-content/` and
`/wp-includes/` at their original paths. Checked with pixel-by-pixel
screenshots against the old server at 1440 / 768 / 390px widths
(`tools/old-site/compare.py`).

**Pages.** The 30 pages Mike chose to keep, plus the 7 "Intro Course" funnel
pages (`/introcourse`, `/aoc-intro-9v2k7`, `/presence-flow-x4m1`,
`/connection-lab-8p3z`, `/heart-skill-j6r2`, `/deep-learning-q9n5`,
`/attuned-q9n5`). Those 7 were on the retire list, but they're live: the
site's email pop-up (Kit form 9323923, ~5 sign-ups/3 weeks) redirects new
subscribers to `/aoc-intro-9v2k7/`, and Kit sequence "Intro Course" (2719511,
73 subscribers) links lessons 1–5 to them. The other 14 retired URLs still
redirect home. Root-level `foundations.html` etc. (new-design URLs from
2026-09-28 morning) now redirect to `/<slug>/`.

**How it was built** (`tools/old-site/`, run from a folder holding `raw/` and
`site/`):
1. `mirror.py`: fetches each page from the old Hostinger server (pinned
   by IP with `curl --resolve`, because the domain points at GitHub now) with
   `?LSCWP_CTRL=before_optm`, which returns the page *before* the LiteSpeed
   plugin bundles its CSS. Then downloads every referenced asset, including
   url()/@import inside CSS and JSON-escaped URLs.
2. `fontfaces.py`: reads the LiteSpeed CSS bundle the old site actually
   served per page and saves its @font-face rules. This matters: LiteSpeed
   fetched Google Fonts server-side and got static .ttf files (slightly wider
   than the variable fonts a browser gets, so text wrapped differently), and
   it dropped some families entirely (Cormorant Garamond, Manrope, Libre
   Baskerville, Nunito Sans never loaded on the old site). Visitors saw that
   result, so the copy reproduces it.
3. `build.py <repo>`: makes self-links root-relative (canonical/og:url stay
   absolute), strips WP-only head tags, swaps Google Fonts links for the
   per-page font file in `/wp-content/gfonts/`, and **restores LiteSpeed's
   CSS order** (every other style first, including body `<style>` blocks,
   then Divi's `divi-dynamic-css`, then Divi's `*-deferred-*` CSS; the
   unbundled order made different rules win). It also injects an
   `admin-ajax.php` shim after jQuery and applies `patches.py`.
4. `patches.py`: content fixes on top of the old pages. Each must match
   an exact count or the build stops. Currently: /introsession date (Oct 5
   2026) + form, /pastparticipants "new cohort" form.

**The email pop-up (Bloom)** still uses Bloom's own JS/CSS. The shim answers
its `bloom_subscribe` call by POSTing straight to Kit
(`https://app.kit.com/forms/9323923/subscriptions`, CORS allows it), then
Bloom does its normal success redirect to `/aoc-intro-9v2k7/`. Tested with
Kit's endpoint intercepted (`popup_test.py`). **A real sign-up has not been
tested yet**, since that would add a subscriber.

**Editing from now on.** Once Hostinger web hosting is cancelled the mirror
can't be re-run, so the built HTML in this repo *is* the source. Edit
`<slug>/index.html` directly. It's Divi markup (`et_pb_*` modules), so find
the text and change it in place. The header/menu (Divi Theme Builder
`tb-1650`) is copied into every page. A menu change means the same edit
across all pages (script it). Menu items link through Divi's JS (`et_clickable`),
not plain `<a href>`: test by clicking (`navtest.py`), not by grepping. After
any edit, run `errsweep.py` (JS errors/404s) against a local
`python3 -m http.server`.

**Known, deliberately left as on the old site:** stale dates on
`/cohort` (May–Jul 2025), `/meditators-course`, `/level-3-art-of-honesty`
(Apr–Jun 2025); old copy on the three registration-closed variants
(`/foundationsinactive`, `/artofempathyinterest`,
`/home-closed-for-current-cohort`); Doctors' "Free Intro Session Sep 27"
block (still waiting on Mike, same as before). None of these pages are in
the menu. The canvas-era rebuild had modernised them; ask Mike before
touching.

## The project

Rebuilding Danny Cohen's NVC training site (currently live WordPress/Divi
at `artofcommunication.life`) as a modern static site. Mike Korman owns the
domain, hosting decisions, and this GitHub repo.

## Where things live

| What | Where |
|---|---|
| Design source of truth | Claude canvas artifact: `https://claude.ai/artifact/Y9ZHuJ38CkidKPe8D5Yrat` (Design-type artifact, one `.dc.html` file per page under `project/`) |
| Static site repo | `github.com/teachermikehebrew/art-of-communication-site`, branch `main` |
| Live preview (no DNS needed) | `https://teachermikehebrew.github.io/art-of-communication-site/` |
| Real domain (LIVE since 2026-09-28) | `artofcommunication.life` — DNS at Hostinger points at GitHub Pages; `CNAME` file present |
| Live WordPress site (for pulling real content/links) | `https://artofcommunication.life/<slug>/` |

## Current status (as of this session)

**Done and live on GitHub Pages:**
- Foundations, Empathy, Doctors, Rabbis, Coaching — full pages, real content
  pulled from the live WP site, converted from canvas `.dc.html` to plain
  static HTML/CSS/vanilla JS (`foundations.html`, `empathy.html`,
  `doctors.html`, `rabbis.html`, `coaching.html` at repo root).
- Every CTA button/link cross-checked against the live WordPress site and
  fixed where wrong (see "Known link fixes already applied" below).
- Danny's bio photo updated site-wide to the new photo (see "Danny's current
  photo" below).
- A shared whitespace bug in the accordion component fixed (was leaving dead
  space under every closed accordion item, site-wide — fixed in
  `assets/canvas/site.css`, one shared file for all 5 pages).
- Two Foundations visual fixes: Free Intro Session background photo faded to
  20% opacity (was too vivid, text illegible); "This Course Is Right for You
  If" photo switched from a hard crop to showing the full frame.

- **Home page** (`index.html`) rebuilt (2026-09-28) from the canvas's chosen
  home design — `OptionC.dc.html` ("Home — Option C (chosen: Soft & Human)"
  in `canvas.json`; `Main.dc.html` and `OptionB` are archived alternatives).
  Now uses the shared `assets/canvas/site.css`/`site.js` like the course
  pages, with real copy, testimonials and step photos pulled from the live WP
  home (images in `assets/home/`). The old placeholder's `assets/css`,
  `assets/js`, `assets/images` were deleted (nothing else used them).
- **Mobile**: all 7 pages checked at 390px with Playwright — no horizontal
  overflow.
- **No WordPress hotlinks left**: Foundations' Free Intro Session background
  was loading from `artofcommunication.life/wp-content/...` (would break at
  cutover); now self-hosted as `assets/canvas/intro-bg.jpg`. That section
  also got `id="intro-session"` (the home page's step 1 links to it).
- **Old WP URLs for the 5 course pages** (`/foundations/`, `/empathy/`,
  `/doctors/`, `/rabbis/`, `/coaching/`) redirect to the new `.html` pages via
  stub `<slug>/index.html` files.

**Not started / explicitly deferred:**
- **Blog page** (`blog.html`) — just a "coming soon" stub.
- **The other WordPress pages — Mike's decision (2026-09-27, from Drive
  `Work/Danny/D 🌐 Website Rebuild/Website Rebuild - Notes.md`):**
  - **Recreate (27 total) — ALL DONE (2026-09-28).** Each lives at
    `<slug>/index.html` so the old `/<slug>/` URL works unchanged.
    - Small pages (policies, thank-you pages, payment orientation, how we
      relate to money, accompaniment, past participants, community gateway,
      newsletter w/ same Kit embed `9411f62e6f`, intro session).
    - Registration-closed variants (`/foundationsinactive`,
      `/artofempathyinterest`, `/home-closed-for-current-cohort`) were built
      FROM THE CURRENT foundations/empathy/index pages with the cohort-specific
      bits swapped for each page's original register-interest form — not
      from their old WP copy (which was stale: Oct 2025 dates, old bio).
    - `/community`, `/level-3-art-of-honesty`, `/cohort`, `/meditators-course`:
      full content from the live pages; their advertised cohorts (2024/2025)
      are over, so dates show as TBC with interest/newsletter CTAs.
    - Blog: `blog.html` + `blog/index.html` (old URL) list the 3 posts; each
      post at its original slug. Verified word-for-word coverage vs. live.
    - `/introsession` shows the current Oct 5 2026 intro (same as the
      Foundations page), not the stale Oct 2025 date.
    - `/pastparticipants` "new cohort" button → current Fall 2026 application
      (`forms.gle/pyHUu7FqG6Kyvoit8`), was last year's form.
    - Danny's photo on all new pages is the current one (`c22413f0.jpg`).
    - All 57 pages pass a local link/asset check; zero references to
      `artofcommunication.life/wp-content` remain.
  - **Redirect to homepage (done — stub `<slug>/index.html` files):**
    `/jorinde`, `/testimonials`, `/the-plan`, `/introcourse`, `/attuned-q9n5`,
    `/deep-learning-q9n5`, `/heart-skill-j6r2`, `/connection-lab-8p3z`,
    `/presence-flow-x4m1`, `/aoc-intro-9v2k7`, `/introdenizen`,
    `/denizenfoundations`, `/1-1denizen`, `/denizennvc`, `/home`, `/hometest`,
    `/homeold`, `/level-2-art-of-empathy`, `/level-1-art-of-communication`,
    `/coachingold`, `/executive-course`. (The notes say 22 but list 21.)
  - `/webinar` (in neither list) → Mike said redirect to homepage (2026-09-28); done.
  - Hosting: the notes planned Netlify/Vercel; we're using GitHub Pages
    instead (same idea: static, git-based, auto-deploy). Domain + email stay
    at Hostinger; only the root A records change. WP stays up as a fallback
    until the new site is confirmed stable.
- **Note:** `learn.artofcommunication.life` is Mike's Mighty Networks
  community — never touch that DNS record.
- **DNS cutover** — the actual "go live" step. See below.

## The DNS cutover (the one big remaining step)

The static site works and is proven at the GitHub Pages URL above. To make
it the *real* live site:

1. In the repo's GitHub Pages settings, re-add the custom domain
   `artofcommunication.life` (this recreates the `CNAME` file at repo root —
   it was deliberately removed so the `.github.io` URL could preview
   standalone; see "Why there's no CNAME file" below).
2. At Mike's domain registrar, set DNS for `artofcommunication.life`:
   - **A records** (root domain) → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
   - **CNAME** for `www` (if used) → `teachermikehebrew.github.io`
   - **Leave MX records alone** (email, unrelated).
3. Claude cannot do step 2 — no registrar access, no DNS connector
   configured in this workspace. Mike has to do it himself.

### Why there's no CNAME file right now
GitHub Pages auto-redirects the `.github.io` URL to whatever's in the
`CNAME` file, even if that domain isn't pointed at GitHub yet — which broke
previewing. So `CNAME` was removed to let the `.github.io` URL work
standalone for review. **Before going live, re-add it**: a file named
`CNAME` at repo root containing just `artofcommunication.life`.

## Architecture: canvas vs. static site (read this before editing anything)

Two parallel copies of each page exist and **do not auto-sync**:

1. **Canvas `.dc.html` files** (`project/*.dc.html` in the artifact) — use a
   component templating syntax (`{{accent}}`, `sc-for`, `sc-if`,
   `onClick="{{...}}"`, images as `/_blob/<id>`). This is what Mike edits
   directly in the canvas UI (including from his phone) between chat
   sessions — **check here for the latest design intent**, since he may have
   made changes a prior session doesn't know about.
2. **Static HTML files** (`foundations.html` etc. in the repo) — plain
   HTML/CSS/vanilla JS, hand-converted from the canvas files. `{{accent}}` →
   literal `#D97757`; `/_blob/<id>` → `assets/canvas/<8-char-prefix>.<ext>`;
   accordions unrolled from the canvas's JS data arrays into static markup
   with a shared `toggleAcc()` JS function (see `assets/canvas/site.js` /
   `site.css`).

**When Mike asks for a change and doesn't specify canvas vs. site**: he's
usually looking at the canvas (that's the "design" surface he reviews on).
Fix it there, then **also port the fix into the matching static HTML file**
and push — otherwise the live site silently drifts out of sync with what he
approved. This has already happened once this session (background-opacity
and photo-crop fixes were made in canvas but initially forgotten in the
static repo — caught because Mike said "I don't see them live").

**Before publishing to the canvas artifact**, always re-read the target file
first (`action: "read"`, same `url`, `path: "project/<Name>.dc.html"`) —
publishing against stale content is rejected with a "not what you last saw"
error, and direct edits from the canvas UI are common between sessions.

**Publish mechanics gotcha**: `Artifact` tool's `file_path` for both the
canvas and static-site publishes must point to a file *inside* the current
session's working directory tree (e.g. copy into `/home/user/project/` or
`/home/user/art-of-communication-site/` first) — a path under
`/tmp/.../scratchpad/...` will be rejected even though `Read`/`Edit` work on
it fine.

## Danny's current photo

Canvas blob id: `33e05e5a7f3e2804e38beaa4b689a54b` (uploaded this session,
source: `https://artofcommunication.life/wp-content/uploads/2026/05/Amir_Ganun_Photography-0699.jpg-scaled.jpeg`).
This replaced two older blobs that are now retired — if you see either of
these anywhere, they're stale and should be swapped to the id above:
- `c22413f09863bab19245bace30e8e184` (old main Danny bio photo)
- `0ecee2771a12083e4df46cb0c6a3396b` (old "Tim-Portrait.png" — actually also
  Danny, used in Rabbis' "2x 1-on-1 coaching" icon and "Free 15-Minute
  Consultation" section)

Static site: the same photo lives at `assets/canvas/c22413f0.jpg` (used by
all 5 pages) and `assets/canvas/0ecee277.jpg` (Rabbis' two extra spots —
note this was renamed from `.png` to `.jpg` to match its real format; the
two references in `rabbis.html` were updated accordingly).

## Known link fixes already applied (don't re-break these)

Cross-checked every CTA button against the live WordPress site's actual
`href`s. Doctors and Coaching were already 100% correct. Fixed on the
others:

- **Foundations, Empathy, Rabbis**: hero (and some mid-page) "Apply" buttons
  now link to `#registration` (scrolls to the "How to Register" section,
  which has a matching `id="registration"`) instead of opening a Google Form
  directly — this matches the real site's behavior.
- **Foundations** "Register Here" (Free Intro Session) →
  `https://forms.gle/a2UrZ14Af635U4aL9`
- **Foundations** "Click Here to Apply" / "Apply Now" →
  `https://forms.gle/pyHUu7FqG6Kyvoit8`
- **Rabbis** "Email Me" mailto subject line matches the live site's exact
  URL encoding (`Rabbis%27%20Cohort...`, with the apostrophe).

All form links were verified to actually resolve (200), not just match the
source.

## Blob-ID → static-asset filename map

If you need to sync more canvas changes into the static site, every image
in `assets/canvas/` is named by the first 8 hex chars of its canvas blob id
(extension matches actual format). Full map is in git history (commit
`2e0c937`) if you need to reconstruct it — there are ~37 images, mostly
1:1 copies of canvas blobs. Three exceptions where the canvas's original
upload bytes couldn't be recovered via the Artifact API and a same-subject
real photo was substituted instead: the header logo (`537305ff.png`, now
using the site's real favicon mark), one AI-coach decorative icon
(`e6574aa8.jpeg`), and one "Who This Is For" portrait slot in Foundations/
Empathy (`1dea7fa5.jpg`) — these are cosmetically fine substitutes but not
byte-identical to whatever's currently in the canvas for those specific
slots, worth a visual diff if it matters.

## Suggested next steps, in order

1. Confirm with Mike whether Home/Blog should get the same real-content
   treatment before or after the DNS cutover.
2. If before: repeat the Foundations/Empathy/etc. workflow for
   `index.html`/Home — fetch `https://artofcommunication.life/`, pull real
   copy/images, rebuild to match the design system.
3. Do a mobile-viewport pass on all 5 finished pages (resize browser or use
   Playwright at e.g. 390×844) — the CSS breakpoints exist but are untested.
4. Once Mike's ready: re-add `CNAME`, walk him through the DNS records, then
   verify `artofcommunication.life` resolves correctly.
5. After DNS is live, do one more full click-through with Danny on the real
   domain — real users may hit edge cases the canvas preview didn't surface.

## Useful commands for a fresh session

```bash
# Clone/check the static repo (should already be in the container if this
# session's repo config includes it; otherwise check environment docs)
cd /home/user/art-of-communication-site && git log --oneline -10

# Check GitHub Pages is still serving correctly
curl -sS -o /dev/null -w "%{http_code}\n" https://teachermikehebrew.github.io/art-of-communication-site/foundations.html

# Playwright is available for visual QA — see this session's history for the
# exact launch args needed (chromium binary at /opt/pw-browsers/chromium-1194/chrome-linux/chrome,
# needs --headless=new --no-sandbox, npm-install playwright into /tmp since it's not preinstalled)
```

## Go-live log (2026-09-28)

- Merged to `main`, then Mike changed DNS in Hostinger hPanel
  (Domains → artofcommunication.life → DNS records). Deleted: `ALIAS @ →
  artofcommunication.life.cdn.hstgr.net` (Hostinger CDN), `CNAME www →
  …cdn.hstgr.net`, old AAAA @. Added: A @ → 185.199.108–111.153, CNAME www →
  teachermikehebrew.github.io. Left alone: MX/SPF (Hostinger email), CNAME
  learn → ssl.mn.co (Mighty Networks), ALIAS staging (old WP staging),
  hostingermail CNAMEs.
- Rollback: re-add `ALIAS @ → artofcommunication.life.cdn.hstgr.net` and
  `CNAME www → www.artofcommunication.life.cdn.hstgr.net`, delete the 4 A
  records, and remove the `CNAME` file from the repo.
- `CNAME` file re-added at repo root. The `.github.io` preview URL now
  redirects to the real domain (expected).
- HTTPS certificate issued; Mike ticked Enforce HTTPS in repo Settings → Pages (`http://` now 301s to `https://`). Old WordPress hosting on Hostinger can be cancelled after a week or two of stability — keep domain + email there.

## Editing `assets/canvas/site.css` or `site.js` — bump the version tag

GitHub Pages serves assets with `cache-control: max-age=600`, so a browser
can pair new page HTML with a cached old stylesheet (this broke the home
hero for Mike on 2026-09-28). Every page links `site.css?v=<stamp>` /
`site.js?v=<stamp>`. After changing either file, bump the stamp site-wide:

```bash
V=$(date +%Y%m%d%H%M); grep -rl 'assets/canvas/site\.\(css\|js\)?v=' --include=*.html . \
  | xargs sed -i -E "s#(assets/canvas/site\.(css|js))\?v=[0-9]+#\1?v=$V#g"
```

## Full-photo headers

Home, Foundations (+ `/foundationsinactive`), Doctors, Rabbis and Empathy (+ `/artofempathyinterest`) use the
full-bleed photo hero (`.hero-full` / `.hero-shade` / `.hero-copy` in
site.css; per-page framing via `--pos-d` / `--pos-m`). Photos live in
`assets/heroes/`. Empathy uses the `.hero-bottom` variant (text along the bottom) because its
photo has faces at both edges. Still on the old boxed-photo hero: Coaching.

## Session handoff (2026-09-28, end of day)

**Live and working:** all 27 kept pages + 22 redirects + blog on
artofcommunication.life (GitHub Pages, HTTPS enforced). Full-photo headers on
Home, Foundations, Doctors, Rabbis, Empathy (+ their registration-closed
variants). Footers read "© 2026 The Art of Communication" (names removed at
Mike's request). Foundations mission line: "a grounded, practice-rich path
into…" (site + canvas).

**Open items, in priority order:**
1. **Danny's feedback: the new look feels "drab / informational"; he wants
   the old WordPress aesthetic back** ("it looked great before"). Plan: keep
   content/structure, restyle to match the old site. BLOCKED on seeing the
   old site:
   - Internet Archive has the old pages but NOT their stylesheet/images, so
     renders are unstyled. One surviving clue: the "Hi, I'm Danny" block was
     deep burgundy `#6c2940` beside cream — the old palette was bolder.
   - Old WordPress still runs on Hostinger server `77.37.35.80`
     (srv1371 / uk-fast-web1371.hstgr.io), but this sandbox's egress proxy
     blocks raw-IP connections and resolves the domain to GitHub, so Claude
     can't load it. `staging.artofcommunication.life` returns a WP 500 error.
   - Asked Mike for either (a) a Hostinger "Preview website" / temporary
     `*.hostingersite.com` link (Claude can load that), or (b) screenshots,
     e.g. via a temporary `/etc/hosts` line `77.37.35.80 artofcommunication.life`
     on his Mac (remove afterwards). Then: mock up Home in the old style for
     Mike + Danny to approve before going live.
   - Do NOT use the phpMyAdmin / File Manager session links Mike pasted —
     they're logged-in admin surfaces.
2. **Doctors page:** the "Free Intro Session" section still says Sep 27, 2026
   (past). Header line already removed. Ask Mike what replaces it.
3. **Coaching:** still on the old boxed-photo hero — waiting on a photo.
4. **Community page** lists Mike as a lead facilitator (content, not
   footer) — left in place; ask if he wants it removed.
5. **Danny's Mac** showed a certificate warning after the DNS switch; his
   phone was fine → stale DNS cache on his network (restart Mac/router or
   wait). Site itself verified valid via SSL Labs.
6. Cancel Hostinger **web hosting** after a week or two of stability (keep
   domain + email). WP needs to stay up until item 1 is resolved, since it's
   the only full copy of the old design.

**Workflow reminders:** edit static HTML directly, commit on the session
branch, then fast-forward `main` (Mike approved publishing to main); bump the
`site.css?v=` stamp whenever site.css/js changes (see above); new full-photo
headers: `.hero-full` markup (see index.html / doctors.html), `.hero-bottom`
variant when faces sit at both edges of the photo.

## Divi slide-in images (`et-waypoint`) — keep `aoc-waypoint-fix`
Divi's animated images (`et-waypoint et_pb_animation_*`) start at opacity 0
and rely on animation CSS that no longer exists (broken on the old WordPress
site too, since the Divi 5 upgrade). Each page that has them carries
`<style id="aoc-waypoint-fix">.et-waypoint:not(.et_pb_counters){opacity:1!important}</style>`
before `</head>` (commit 661423c, 2026-09-28). Any new page copied from Divi
markup with `et-waypoint` images needs the same line, or its images vanish.

## Menu toggle, pop-up buttons, Rabbis hero (2026-09-28)
- The slide-in menu is opened by one plain-JS click listener per page
  (replaces the Divi code module's jQuery double-toggle). It derives the
  icon's `open` class from the panel's `slide-in-menu` class, so they
  always match. Any new page needs the same script in its header.
- Home body buttons (both now labelled "Free Intro Course") and the
  /cohort one open the Bloom pop-up: the pop-up div carries
  `et_bloom_trigger_click` + `data-trigger_click=".aoc-open-popup"`, and
  the buttons carry class `aoc-open-popup` (Bloom binds the click itself;
  closing hides it rather than deleting it). Submit → Kit form 9323923 →
  /aoc-intro-9v2k7/. Their href (Kit intro-course page) is only the no-JS
  fallback. Known quirk: if someone opens and closes it within the first
  15 s, Bloom's timer pop-up still appears once at 15 s.
- /rabbis carries `<style id="aoc-hero-fit">` removing the hero's
  843px max-height (≥768px), so the Apply button stays inside the photo.
