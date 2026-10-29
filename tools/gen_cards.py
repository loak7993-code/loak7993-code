#!/usr/bin/env python3
"""Generate static SVG cards for the loak7993-code profile README."""
import json
import subprocess
import textwrap
import html

ACCENT = "#3B82F6"
PANEL = "#161B22"
TEXT = "#E6EDF3"
MUTED = "#9198A1"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Code', Menlo, monospace"
SANS = "-apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

STAR_PATH = "M243,96a20.33,20.33,0,0,0-17.74-14l-56.59-4.57L146.83,24.62a20.36,20.36,0,0,0-37.66,0L87.35,77.44,30.76,82A20.45,20.45,0,0,0,19.1,117.88l43.18,37.24-13.2,55.7A20.37,20.37,0,0,0,79.57,233L128,203.19,176.43,233a20.39,20.39,0,0,0,30.49-22.15l-13.2-55.7,43.18-37.24A20.43,20.43,0,0,0,243,96ZM172.53,141.7a12,12,0,0,0-3.84,11.86L181.58,208l-47.29-29.08a12,12,0,0,0-12.58,0L74.42,208l12.89-54.4a12,12,0,0,0-3.84-11.86L41.2,105.24l55.4-4.47a12,12,0,0,0,10.13-7.38L128,41.89l21.27,51.5a12,12,0,0,0,10.13,7.38l55.4,4.47Z"
FORK_PATH = json.loads(open("/tmp/opencode/p-git-fork.svg").read().split('d="')[1].split('"')[0] and "null") if False else None
import re
_f = open("/tmp/opencode/p-git-fork.svg").read()
FORK_PATH = re.search(r'd="([^"]+)"', _f).group(1)


def gh(*args):
    return subprocess.run(["gh", "api", *args], capture_output=True, text=True).stdout


def repo_data(name):
    d = json.loads(gh(f"repos/loak7993-code/{name}"))
    return {
        "name": name,
        "desc": d.get("description") or "",
        "lang": (d.get("language") or "Code"),
        "stars": d["stargazers_count"],
        "forks": d["forks_count"],
    }


def esc(s):
    return html.escape(s, quote=True)


def wrap(desc, width=54, max_lines=2):
    desc = desc.replace("—", "·").replace("–", "·")
    for ch in ["⚡", "✌", "️", "🚀"]:
        desc = desc.replace(ch, "")
    desc = " ".join(desc.split())
    lines = textwrap.wrap(desc, width=width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: width - 1].rsplit(" ", 1)[0] + " ..."
    return lines


def card_svg(r):
    lines = wrap(r["desc"])
    y0 = 88 if len(lines) > 1 else 104
    y1 = 108 if len(lines) > 1 else 0
    desc_spans = ""
    if len(lines) == 1:
        desc_spans = f'<text x="28" y="106" font-size="14" fill="{MUTED}">{esc(lines[0])}</text>'
    else:
        desc_spans = (
            f'<text x="28" y="90" font-size="14" fill="{MUTED}">{esc(lines[0])}</text>'
            f'<text x="28" y="110" font-size="14" fill="{MUTED}">{esc(lines[1])}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="465" height="170" viewBox="0 0 465 170" font-family="{SANS}">
  <rect width="465" height="170" rx="12" fill="{PANEL}"/>
  <text x="28" y="48" font-size="21" font-weight="700" fill="{TEXT}" letter-spacing="-0.3">{esc(r["name"])}</text>
  <circle cx="437" cy="42" r="4" fill="{ACCENT}"/>
  <text x="28" y="70" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(r["lang"])}</text>
  {desc_spans}
  <g transform="translate(28,136)">
    <svg width="15" height="15" viewBox="0 0 256 256"><path d="{STAR_PATH}" fill="{ACCENT}"/></svg>
    <text x="22" y="13" font-family="{MONO}" font-size="13" fill="{TEXT}">{r["stars"]}</text>
  </g>
  <g transform="translate(92,136)">
    <svg width="15" height="15" viewBox="0 0 256 256"><path d="{FORK_PATH}" fill="{MUTED}"/></svg>
    <text x="22" y="13" font-family="{MONO}" font-size="13" fill="{TEXT}">{r["forks"]}</text>
  </g>
</svg>"""


def main():
    featured = ["termagent", "velox", "litebox", "fang", "basalt", "lockin"]
    for name in featured:
        r = repo_data(name)
        path = f"/tmp/opencode/profile/assets/card-{name}.svg"
        open(path, "w").write(card_svg(r))
        print(f"wrote {path}")

    repos = json.loads(gh("users/loak7993-code/repos?per_page=100&sort=created"))
    orig = [r for r in repos if not r["fork"] and r["name"] != "loak7993-code"]
    stars = sum(r["stargazers_count"] for r in orig)
    forks = sum(r["forks_count"] for r in orig)
    releases = 0
    for r in orig:
        try:
            releases += len(json.loads(gh(f"repos/loak7993-code/{r['name']}/releases?per_page=100")))
        except Exception:
            pass
    langs = {}
    for r in orig:
        l = r.get("language") or "Other"
        langs[l] = langs.get(l, 0) + 1
    stats = {
        "repos": len(orig),
        "stars": stars,
        "forks": forks,
        "releases": releases,
        "langs": langs,
    }
    print("stats:", stats)
    write_stats_card(stats)


def write_stats_card(s):
    order = sorted(s["langs"].items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in order)
    bar_w = 904
    segs = []
    x = 0.0
    opacities = [1.0, 0.75, 0.55, 0.42, 0.32, 0.24, 0.18, 0.14]
    labels = []
    lx = 0
    for i, (lang, count) in enumerate(order):
        w = max(24.0, bar_w * count / total)
        if x + w > bar_w:
            w = bar_w - x
        segs.append(
            f'<rect x="{x:.1f}" y="0" width="{w:.1f}" height="8" rx="4" fill="{ACCENT}" fill-opacity="{opacities[min(i, len(opacities)-1)]}"/>'
        )
        if lx < 860:
            labels.append(
                f'<text x="{lx}" y="0" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(lang)} <tspan fill="{TEXT}" fill-opacity="0.8">{count}</tspan></text>'
            )
            lx += 14 + 8 * (len(lang) + 3)
        x += w

    stat_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="176" viewBox="0 0 960 176" font-family="{SANS}">
  <rect width="960" height="176" rx="12" fill="{PANEL}"/>
  <text x="28" y="38" font-size="13" fill="{MUTED}">what {s['repos']} public repos add up to</text>
  <g font-family="{MONO}">
    <text x="28" y="82" font-size="34" font-weight="700" fill="{TEXT}">{s['releases']}</text>
    <text x="28" y="104" font-size="12" fill="{MUTED}">releases shipped</text>
    <text x="190" y="82" font-size="34" font-weight="700" fill="{TEXT}">{s['repos']}</text>
    <text x="190" y="104" font-size="12" fill="{MUTED}">original repos</text>
    <text x="345" y="82" font-size="34" font-weight="700" fill="{TEXT}">{s['stars']}</text>
    <text x="345" y="104" font-size="12" fill="{MUTED}">stars</text>
    <text x="465" y="82" font-size="34" font-weight="700" fill="{TEXT}">{len(order)}</text>
    <text x="465" y="104" font-size="12" fill="{MUTED}">languages</text>
  </g>
  <g transform="translate(28,126)">
    {''.join(segs)}
  </g>
  <g transform="translate(28,158)">
    {''.join(labels)}
  </g>
</svg>"""
    open("/tmp/opencode/profile/assets/stats.svg", "w").write(stat_svg)
    print("wrote stats card")


if __name__ == "__main__":
    main()
