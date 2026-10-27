#!/usr/bin/env python3
"""Builds the zen-themed visuals for the profile README as SVGs in assets/.

GitHub READMEs can't set fonts or backgrounds, so the decorative parts (header,
section dividers, stats, featured project, toolkit) are SVGs with the fonts
embedded. Everything people read or click lives in README.md as plain markdown.

Run locally:
    GITHUB_TOKEN=$(gh auth token) python scripts/build_profile.py
The GitHub Action runs it daily so the stats stay current.
"""
import base64
import json
import math
import os
import random
import urllib.request
from datetime import datetime, timezone
from html import escape

USER = "senanayakenithikas-ux"
NAME = "NITHIKA"
TAGLINE = "UNDERGRAD @ IIT  ·  AI APPS  ·  FULL-STACK  ·  HACKATHONS"

FEATURED = {
    "name": "Sana",
    "repo": f"{USER}/sana-emotional-support",
    "desc": "A calm AI companion for emotional support. Chat by text or voice, it remembers the "
            "conversation, and it installs on your phone as an app.",
    "tags": ["PYTHON", "LLM", "VOICE", "PWA"],
}
DIVIDERS = [
    ("01", "ORIGIN"),
    ("02", "PROJECTS"),
    ("03", "TOOLKIT"),
    ("04", "SAY HI"),
]
# (name, weight 1-3): weight sets the size of each pebble
STACK = {
    "LANGUAGES": [("TypeScript", 3), ("Python", 3), ("JavaScript", 2), ("Java", 2), ("SQL", 1)],
    "FRAMEWORKS": [("Next.js", 3), ("React", 2), ("NestJS", 2), ("Flask", 2), ("JavaFX", 1)],
    "DATA & SHIP": [("Supabase", 3), ("PostgreSQL", 2), ("Prisma", 2), ("Docker", 2), ("Render", 1)],
    "AI": [("LLM APIs", 3), ("Agents", 2), ("RAG", 2), ("Voice / TTS", 1)],
}

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ASSETS = os.path.join(ROOT, "assets")

W = 1200
JADE = "#5eead4"
INDIGO = "#a5b4fc"
SAKURA = "#f9a8d4"
TEXT = "#e6f1ef"
DIM = "#8aa3a8"
LINE = "#1d3340"


# ---------------------------------------------------------------- data

def gh(path, body=None):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request("https://api.github.com/" + path, data=data,
                                 headers={"Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_stats():
    user = gh(f"users/{USER}")
    repos = gh(f"users/{USER}/repos?per_page=100&type=owner")
    q = ('{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions '
         'weeks{contributionDays{contributionCount}}}}}}') % USER
    cal = gh("graphql", {"query": q})["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    return {
        "contribs": cal["totalContributions"],
        "repos": user["public_repos"],
        "stars": sum(r["stargazers_count"] for r in repos if not r["fork"]),
        "followers": user["followers"],
        "weeks": weeks[-26:],
        "featured_stars": gh(f"repos/{FEATURED['repo']}")["stargazers_count"],
    }


# ---------------------------------------------------------------- drawing helpers

def font_css():
    faces = [("Sora", "sora-latin-700-normal.woff2", 700), ("Sora", "sora-latin-400-normal.woff2", 400),
             ("JetBrains Mono", "jetbrains-mono-latin-400-normal.woff2", 400)]
    out = []
    for family, file, weight in faces:
        with open(os.path.join(ASSETS, "fonts", file), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        out.append(f"@font-face{{font-family:'{family}';font-weight:{weight};"
                   f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
    return "\n".join(out)


FONT_CSS = None


def svg(h, body, title, seed, glows=(), extra_css="", petals=14):
    """Wraps body in a rounded dark card with aurora glows, ripples and drifting petals."""
    global FONT_CSS
    FONT_CSS = FONT_CSS or font_css()
    rnd = random.Random(seed)
    grads, rects = [], []
    for i, (cx, cy, r, color, op) in enumerate(glows):
        grads.append(f'<radialGradient id="g{i}" cx="{cx}%" cy="{cy}%" r="{r}%">'
                     f'<stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
                     f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        rects.append(f'<rect width="{W}" height="{h}" fill="url(#g{i})"/>')
    dots = []
    for _ in range(petals):
        x, y = rnd.uniform(0, W), rnd.uniform(0, h)
        color = rnd.choice([SAKURA, JADE, INDIGO, "#ffffff"])
        dur, delay = rnd.uniform(9, 16), rnd.uniform(0, 8)
        rx = rnd.uniform(1.5, 3.2)
        dots.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rx:.1f}" ry="{rx * .6:.1f}" fill="{color}" '
                    f'opacity="{rnd.uniform(.25, .6):.2f}" class="drift" '
                    f'style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-labelledby="title">
<title id="title">{escape(title)}</title>
<style>
{FONT_CSS}
.d{{font-family:'Sora','Segoe UI',sans-serif}}
.m{{font-family:'JetBrains Mono',Consolas,monospace}}
.drift{{animation:drift 12s ease-in-out infinite}}
@keyframes drift{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(18px,-10px)}}}}
.breathe{{animation:breathe 6s ease-in-out infinite;transform-origin:center;transform-box:fill-box}}
@keyframes breathe{{50%{{opacity:.35;transform:scale(1.04)}}}}
{extra_css}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
  <clipPath id="frame"><rect width="{W}" height="{h}" rx="18"/></clipPath>
  <linearGradient id="base" x1="0" y1="0" x2=".4" y2="1"><stop offset="0" stop-color="#0d1526"/><stop offset=".55" stop-color="#0a1a22"/><stop offset="1" stop-color="#050b10"/></linearGradient>
  <linearGradient id="rule" x1="0" x2="1"><stop offset="0" stop-color="{JADE}" stop-opacity=".7"/><stop offset="1" stop-color="{JADE}" stop-opacity="0"/></linearGradient>
  {"".join(grads)}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{h}" fill="url(#base)"/>
{"".join(rects)}
{"".join(dots)}
{body}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="18" fill="none" stroke="{LINE}"/>
</svg>
'''


def ripples(cx, cy, n, gap, color=JADE, op=.18, squash=.42):
    """Concentric ellipses, like raked sand around a stone."""
    out = []
    for i in range(1, n + 1):
        r = i * gap
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r * squash:.1f}" fill="none" '
                   f'stroke="{color}" stroke-opacity="{op * (1 - i / (n + 1)):.3f}"/>')
    return "".join(out)


def enso(cx, cy, r, width=14):
    """A brush-stroke circle left slightly open, drawn on with a dash animation."""
    circ = 2 * math.pi * r
    gap = circ * .07
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TEXT}" stroke-opacity=".08" '
            f'stroke-width="{width + 10}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="url(#ensoGrad)" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-dasharray="{circ - gap:.0f} {circ:.0f}" '
            f'transform="rotate(-70 {cx} {cy})" class="draw" style="--len:{circ:.0f}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r - width * 1.1:.0f}" fill="none" stroke="{SAKURA}" '
            f'stroke-opacity=".25" stroke-width="1.5" stroke-dasharray="2 9"/>')


def tag(x, y, text, color=JADE):
    w = len(text) * 8.4 + 26
    return (f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{color}" fill-opacity=".1" '
            f'stroke="{color}" stroke-opacity=".45"/>'
            f'<text x="{x + w / 2:.0f}" y="{y + 18.5}" text-anchor="middle" class="m" font-size="12.5" '
            f'fill="{color}" letter-spacing="1">{escape(text)}</text>'), w


# ---------------------------------------------------------------- assets

def header():
    h = 360
    css = (".draw{stroke-dashoffset:var(--len);animation:draw 2.6s cubic-bezier(.6,0,.2,1) forwards}"
           "@keyframes draw{to{stroke-dashoffset:0}}"
           ".rise{opacity:0;animation:rise 1.2s ease-out forwards}"
           "@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
           "@media (prefers-reduced-motion:reduce){.draw{stroke-dashoffset:0}.rise{opacity:1}}")
    body = f'''
<defs><linearGradient id="ensoGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{JADE}"/><stop offset=".6" stop-color="{INDIGO}"/><stop offset="1" stop-color="{SAKURA}"/></linearGradient>
<linearGradient id="nameGrad" x1="0" x2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{JADE}"/></linearGradient></defs>
{ripples(960, 300, 9, 70, JADE, .22)}
{enso(960, 175, 112)}
<circle cx="960" cy="175" r="6" fill="{SAKURA}" class="breathe"/>
<g class="rise">
  <text x="80" y="118" class="m" font-size="15" fill="{JADE}" letter-spacing="4">HELLO, WORLD. I'M</text>
  <text x="76" y="212" class="d" font-weight="700" font-size="96" fill="url(#nameGrad)" letter-spacing="10">{NAME}</text>
</g>
<g class="rise" style="animation-delay:.5s">
  <rect x="80" y="240" width="380" height="2" fill="url(#rule)"/>
  <text x="80" y="276" class="m" font-size="14.5" fill="{DIM}" letter-spacing="1.5">{escape(TAGLINE)}</text>
  <text x="80" y="306" class="d" font-size="16" fill="{TEXT}" fill-opacity=".8">Building calm, useful software with AI.</text>
</g>
'''
    title = f"{NAME.title()}: {TAGLINE.title()}"
    return svg(h, body, title, seed=1, extra_css=css,
               glows=[(82, 40, 38, "#2dd4bf", .22), (10, 100, 45, "#6366f1", .25), (55, 0, 30, "#f472b6", .10)])


def divider(num, label):
    h = 84
    body = f'''
<text x="40" y="53" class="m" font-size="15" fill="{JADE}" letter-spacing="2">{num}</text>
<circle cx="84" cy="48" r="3" fill="{SAKURA}" class="breathe"/>
<text x="104" y="55" class="d" font-weight="700" font-size="22" fill="{TEXT}" letter-spacing="6">{escape(label)}</text>
<rect x="{120 + len(label) * 21}" y="47" width="560" height="1.5" fill="url(#rule)"/>
{ripples(1110, 42, 4, 22, INDIGO, .35, .5)}
<circle cx="1110" cy="42" r="5" fill="{INDIGO}" fill-opacity=".7"/>
'''
    return svg(h, body, f"{num} {label.title()}", seed=int(num) + 10, petals=6,
               glows=[(95, 50, 30, "#6366f1", .18)])


def stats(s):
    h = 300
    tiles = [("CONTRIBUTIONS", s["contribs"], "past year"), ("PUBLIC REPOS", s["repos"], "and counting"),
             ("STARS", s["stars"], "earned"), ("FOLLOWERS", s["followers"], "thank you")]
    body = [f'<text x="48" y="58" class="m" font-size="13" fill="{JADE}" letter-spacing="3">DAILY STATS</text>',
            f'<text x="48" y="84" class="d" font-size="15" fill="{DIM}">Refreshed every day by a GitHub Action</text>']
    tw = 165
    for i, (label, value, sub) in enumerate(tiles):
        x = 48 + i * (tw + 16)
        body.append(f'<rect x="{x}" y="112" width="{tw}" height="140" rx="14" fill="#ffffff" fill-opacity=".03" stroke="{LINE}"/>'
                    f'<text x="{x + 20}" y="142" class="m" font-size="11" fill="{DIM}" letter-spacing="1.5">{label}</text>'
                    f'<text x="{x + 18}" y="200" class="d" font-weight="700" font-size="46" fill="{TEXT}">{value:,}</text>'
                    f'<text x="{x + 20}" y="230" class="d" font-size="13" fill="{JADE}" fill-opacity=".8">{sub}</text>')
    # weekly contributions for the last 26 weeks, as stones of different heights
    weeks = s["weeks"] or [0]
    peak = max(max(weeks), 1)
    gx, gw, base = 790, 362, 252
    bw = gw / len(weeks)
    body.append(f'<text x="{gx}" y="142" class="m" font-size="11" fill="{DIM}" letter-spacing="1.5">LAST 26 WEEKS</text>')
    for i, c in enumerate(weeks):
        bh = 4 + (c / peak) * 86
        color = SAKURA if i == len(weeks) - 1 else JADE
        op = .25 + .75 * (c / peak)
        body.append(f'<rect x="{gx + i * bw + 2:.1f}" y="{base - bh:.1f}" width="{bw - 4:.1f}" height="{bh:.1f}" '
                    f'rx="{min(bw - 4, 8) / 2:.1f}" fill="{color}" fill-opacity="{op:.2f}"/>')
    updated = datetime.now(timezone.utc).strftime("%d %b %Y").upper()
    body.append(f'<text x="1152" y="58" text-anchor="end" class="m" font-size="12" fill="{DIM}">UPDATED {updated}</text>')
    title = (f"Stats: {s['contribs']} contributions in the past year, {s['repos']} public repos, "
             f"{s['stars']} stars, {s['followers']} followers.")
    return svg(h, "".join(body), title, seed=3, petals=10,
               glows=[(100, 0, 40, "#2dd4bf", .15), (0, 100, 40, "#6366f1", .15)])


def featured(s):
    h = 300
    f = FEATURED
    words, lines, line = f["desc"].split(), [], ""
    for w in words:
        if len(line) + len(w) > 62:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    lines.append(line)
    desc = "".join(f'<tspan x="48" dy="{0 if i == 0 else 26}">{escape(l)}</tspan>' for i, l in enumerate(lines))
    tags, x = [], 48
    for t in f["tags"]:
        markup, w = tag(x, 228, t, INDIGO if len(tags) % 2 else JADE)
        tags.append(markup)
        x += w + 10
    # a gentle conversation on the right: two chat bubbles and a heart
    bubbles = (f'<rect x="850" y="66" width="220" height="70" rx="22" fill="#0f2230" stroke="{INDIGO}" stroke-opacity=".6"/>'
               f'<path d="M872 134l-8 18 26-16z" fill="#0f2230" stroke="{INDIGO}" stroke-opacity=".6"/>'
               + "".join(f'<rect x="872" y="{88 + i * 18}" width="{170 - i * 60}" height="6" rx="3" fill="{TEXT}" fill-opacity=".25"/>'
                         for i in range(2))
               + f'<rect x="930" y="160" width="200" height="62" rx="22" fill="{JADE}" fill-opacity=".1" stroke="{JADE}" stroke-opacity=".6"/>'
               f'<path d="M1110 220l8 16-24-14z" fill="#0d2329" stroke="{JADE}" stroke-opacity=".6"/>'
               + "".join(f'<circle cx="{985 + i * 22}" cy="191" r="5" fill="{JADE}" class="breathe" '
                         f'style="animation-delay:{i * .4:.1f}s;animation-duration:1.8s"/>' for i in range(3)))
    heart = (f'<path d="M1125 72c-10-16-34-8-30 10 3 12 30 28 30 28s27-16 30-28c4-18-20-26-30-10z" '
             f'fill="{SAKURA}" fill-opacity=".85" class="breathe"/>')
    body = f'''
{ripples(1000, 270, 6, 60, SAKURA, .18)}
{bubbles}{heart}
<text x="48" y="58" class="m" font-size="13" fill="{SAKURA}" letter-spacing="3">FEATURED PROJECT</text>
<text x="48" y="112" class="d" font-weight="700" font-size="44" fill="{TEXT}">{escape(f["name"])}</text>
<text x="{60 + len(f["name"]) * 27}" y="110" class="m" font-size="15" fill="{DIM}">★ {s["featured_stars"]}</text>
<text x="48" y="150" class="d" font-size="17" fill="{TEXT}" fill-opacity=".78">{desc}</text>
{"".join(tags)}
'''
    return svg(h, body, f"Featured project: {f['name']}. {f['desc']}", seed=4, petals=10,
               glows=[(85, 30, 40, "#f472b6", .14), (0, 0, 40, "#2dd4bf", .12)])


def toolkit():
    rows = list(STACK.items())
    h = 70 + len(rows) * 74
    body = []
    rnd = random.Random(7)
    for r, (group, items) in enumerate(rows):
        y = 70 + r * 74
        body.append(f'<text x="48" y="{y + 6}" class="m" font-size="12" fill="{DIM}" letter-spacing="2">{escape(group)}</text>')
        x = 250
        for name, weight in items:
            ph = 30 + weight * 6
            pw = len(name) * (8.6 + weight * .6) + 34 + weight * 8
            color = [INDIGO, JADE, SAKURA][weight - 1]
            tilt = rnd.uniform(-2.5, 2.5)
            body.append(f'<g transform="rotate({tilt:.1f} {x + pw / 2:.0f} {y})">'
                        f'<rect x="{x}" y="{y - ph / 2:.0f}" width="{pw:.0f}" height="{ph}" rx="{ph / 2:.0f}" '
                        f'fill="{color}" fill-opacity="{.05 + weight * .04:.2f}" stroke="{color}" stroke-opacity=".5"/>'
                        f'<text x="{x + pw / 2:.0f}" y="{y + 5 + weight:.0f}" text-anchor="middle" class="d" '
                        f'font-weight="{700 if weight == 3 else 400}" font-size="{13 + weight * 1.5}" fill="{TEXT}">{escape(name)}</text></g>')
            x += pw + 16
        body.append(f'<rect x="250" y="{y + 34}" width="850" height="1" fill="{LINE}"/>' if r < len(rows) - 1 else "")
    body.append(f'<text x="1152" y="{h - 18}" text-anchor="end" class="m" font-size="11" fill="{DIM}">bigger pebble = more time spent</text>')
    alt = "Toolkit: " + "; ".join(f"{g.title()}: " + ", ".join(n for n, _ in items) for g, items in rows)
    return svg(h, "".join(body), alt, seed=5, petals=12,
               glows=[(100, 100, 45, "#6366f1", .16), (0, 0, 35, "#2dd4bf", .10)])


def main():
    os.makedirs(ASSETS, exist_ok=True)
    try:
        s = fetch_stats()
    except Exception as e:  # keep the last good stats rather than failing the build
        print("Could not fetch stats:", e)
        s = None
    out = {"header.svg": header(), "toolkit.svg": toolkit()}
    for i, (num, label) in enumerate(DIVIDERS, 1):
        out[f"divider-{i:02d}.svg"] = divider(num, label)
    if s:
        out["stats.svg"] = stats(s)
        out["featured-project.svg"] = featured(s)
    for name, content in out.items():
        with open(os.path.join(ASSETS, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("wrote", name)


if __name__ == "__main__":
    main()
