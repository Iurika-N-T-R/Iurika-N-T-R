"""Radar chart of the languages used across every repo I own (private included).

Needs `gh` authenticated with a token that can read private repos.
Writes langs.svg; only totals per language leave the private repos.
"""
import json, math, subprocess
from collections import Counter

AXES = 6
ACCENT, TEXT = "#E4572E", "#8B8B9A"


def gh(path):
    out = subprocess.run(["gh", "api", path, "--paginate"], check=True, capture_output=True, text=True).stdout
    return json.loads(out.replace("][", ","))  # --paginate concatenates JSON arrays


totals = Counter()
for repo in gh("user/repos?affiliation=owner&per_page=100"):
    if not repo["fork"]:
        totals.update(gh(f"repos/{repo['full_name']}/languages"))

grand = sum(totals.values())
top = [(lang, 100 * n / grand) for lang, n in totals.most_common(AXES)]

W, H, cx, cy, R = 520, 430, 260, 235, 140


def point(i, r):
    a = -math.pi / 2 + 2 * math.pi * i / len(top)
    return cx + r * math.cos(a), cy + r * math.sin(a)


peak = top[0][1]
shape = " ".join("%.1f,%.1f" % point(i, R * p / peak) for i, (_, p) in enumerate(top))
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
         f'<text x="{cx}" y="24" text-anchor="middle" font-size="16" font-weight="600" fill="{ACCENT}">Languages across all my projects</text>']
for ring in (0.5, 1):
    pts = " ".join("%.1f,%.1f" % point(i, R * ring) for i in range(len(top)))
    parts.append(f'<polygon points="{pts}" fill="none" stroke="{TEXT}" stroke-opacity="0.25"/>')
for i, (lang, pct) in enumerate(top):
    x, y = point(i, R)
    lx, ly = point(i, R + 28)
    anchor = "middle" if abs(lx - cx) < 10 else ("start" if lx > cx else "end")
    parts += [f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{TEXT}" stroke-opacity="0.35"/>',
              f'<text x="{lx:.1f}" y="{ly - 4:.1f}" text-anchor="{anchor}" font-size="13" font-weight="600" fill="{ACCENT}">{"&lt;1" if pct < 1 else f"{pct:.0f}"}%</text>',
              f'<text x="{lx:.1f}" y="{ly + 12:.1f}" text-anchor="{anchor}" font-size="13" fill="{TEXT}">{lang}</text>']
parts.append(f'<polygon points="{shape}" fill="{ACCENT}" fill-opacity="0.25" stroke="{ACCENT}" stroke-width="2" stroke-linejoin="round"/>')
parts += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{ACCENT}"/>' for x, y in (point(i, R * p / peak) for i, (_, p) in enumerate(top))]
parts.append("</svg>")
open("langs.svg", "w").write("\n".join(parts))
print(", ".join(f"{l} {p:.1f}%" for l, p in top))
