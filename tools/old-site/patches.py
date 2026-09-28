"""Content fixes applied on top of the mirrored old pages.

Each entry is (page, old, new[, count]): `old` must appear exactly `count`
times (default 1) in that page's built HTML or the build stops. Only fixes Mike already approved on the new
site (2026-09-27/28) that the old WordPress pages don't have.
"""

PATCHES = [
    # /introsession: the homepage's "Intro session" button lands here. The old
    # page still advertised Tue 21 Oct 2025. Same session + form as the
    # Foundations page's Free Intro Session (Mon Oct 5 2026).
    ("introsession",
     'Free Intro Session - Tuesday 21 October - 2025 <span style="font-weight: 400;">5 PM (PT) / 7 PM (CT) / 8 PM (ET)</span>',
     'Free Intro Session - Monday 5 October - 2026 <span style="font-weight: 400;">8:15am PT / 11:15am ET / 5:15pm CET / 6:15pm IL</span>'),
    ("introsession",
     'href="https://forms.gle/Phk4bvm6nDCJGhct5"',
     'href="https://forms.gle/a2UrZ14Af635U4aL9"', 2),  # top and bottom "Register" buttons
    ("introsession",  # "Session Details" block further down the page
     '<strong>Date &amp; time:\u00a0</strong>Tuesday 21 October <span style="font-weight: 400;">5 PM (PT) / 7 PM (CT) / 8 PM (ET)</span>',
     '<strong>Date &amp; time:\u00a0</strong>Monday 5 October 2026 <span style="font-weight: 400;">8:15am PT / 11:15am ET / 5:15pm CET / 6:15pm IL</span>'),
    # /pastparticipants: "Register for the new cohort" pointed at last year's form.
    ("pastparticipants",
     'href="https://forms.gle/7JQWznfunYq9hudb6"',
     'href="https://forms.gle/pyHUu7FqG6Kyvoit8"'),
]
