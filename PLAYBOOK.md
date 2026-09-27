# The Art of Communication — Website Rebuild Playbook

**Read this first in any new session.** It's written so a fresh Claude Code
session (no memory of prior conversations) can pick up exactly where things
left off.

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
| Real domain (not yet live) | `artofcommunication.life` — still pointed at the old WordPress site |
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

**Not started / explicitly deferred:**
- **Home page** (`index.html`) — still the original placeholder draft, never
  got the real-content pass the 5 course pages got.
- **Blog page** (`blog.html`) — just a "coming soon" stub.
- **Mobile responsiveness** — basic breakpoints added (stacking grids,
  smaller padding) but never actually tested on a phone-sized viewport.
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
