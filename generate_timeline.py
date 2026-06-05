"""Generate the vertical 'Academic Background' timeline SVG (dark + light).

Style matches the project cards (rounded corners, accent left bar, no drop shadow).
Future -> present ordering, with the Polytechnique milestone highlighted.

Output:
  badges/academic_timeline.svg        (dark)
  badges/academic_timeline_light.svg  (light)
"""

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
EFONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI Emoji', 'Segoe UI', sans-serif"

# Future -> present (top -> bottom). highlight=True for the standout milestone.
MILESTONES = [
    {
        "date": "2026 - 2027",
        "icon": "⭐",
        "title": "École Polytechnique",
        "tag": "Double-Degree",
        "desc": ["M2 Data Science · Applied Mathematics & Statistics"],
        "accent": "#e0a82e",
        "highlight": True,
    },
    {
        "date": "2025 - 2026",
        "icon": "🎓",
        "title": "ECE Paris · 4th Year",
        "tag": "Data & AI Major",
        "desc": [
            "Paris Campus · taught in English",
            "Joined the Intelligence Lab to pursue my AI research goal",
        ],
        "accent": "#2563eb",
    },
    {
        "date": "2024 - 2025",
        "icon": "🏴",
        "title": "ECE Lyon · 3rd Year",
        "tag": "Exchange in Scotland",
        "desc": [
            "Sep - Dec 2024 · Edinburgh Napier University",
            "R&D · Game Engineering with AI · 3D Modelling",
        ],
        "accent": "#0f766e",
    },
    {
        "date": "2023 - 2024",
        "icon": "💡",
        "title": "ECE Lyon · 2nd Year",
        "tag": "The AI turning point",
        "desc": [
            "Discovered AI on my own - chose it over astrophysics",
            "First personal project: a NN library in C, fully from scratch",
            "My dogma since: build everything from scratch with rock-solid theory",
            "(maths, physics...) to grasp every cog, then study & master others' work",
        ],
        "accent": "#6e40c9",
    },
    {
        "date": "2022 - 2023",
        "icon": "🏆",
        "title": "ECE Lyon · 1st Year",
        "tag": "Valedictorian",
        "desc": ["Preparatory classes · 🏆 Top 1 student / Valedictorian at ECE Lyon"],
        "accent": "#16a34a",
    },
    {
        "date": "2022",
        "icon": "📜",
        "title": "High School Diploma · European Section",
        "tag": "Highest Honours",
        "desc": ["La Xavière, Lyon"],
        "accent": "#6b7280",
    },
]

# Geometry
W = 820
SPINE_X = 54
CARD_X = 92
CARD_W = W - CARD_X - 24
GAP = 18
TOP = 22
BOTTOM = 22


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def light_tint(accent_hex, white_ratio=0.92):
    r, g, b = hex_to_rgb(accent_hex)
    lr = int(255 * white_ratio + r * (1 - white_ratio))
    lg = int(255 * white_ratio + g * (1 - white_ratio))
    lb = int(255 * white_ratio + b * (1 - white_ratio))
    return f"#{lr:02x}{lg:02x}{lb:02x}"


def lighten(accent_hex, ratio):
    """Blend the accent toward white by `ratio` (0 = unchanged, 1 = white)."""
    r, g, b = hex_to_rgb(accent_hex)
    lr = int(r + (255 - r) * ratio)
    lg = int(g + (255 - g) * ratio)
    lb = int(b + (255 - b) * ratio)
    return f"#{lr:02x}{lg:02x}{lb:02x}"


def card_height(m):
    return 91 + (len(m["desc"]) - 1) * 18


def render(milestones, theme):
    dark = theme == "dark"
    page_spine = "#30363d" if dark else "#d0d7de"
    title_col = "#f0f6fc" if dark else "#24292f"
    desc_col = "#b8c2cc" if dark else "#57606a"
    node_stroke = "#0d1117" if dark else "#ffffff"

    # total height
    total = TOP + BOTTOM + sum(card_height(m) for m in milestones) + GAP * (len(milestones) - 1)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total}" '
           f'viewBox="0 0 {W} {total}" font-family="{FONT}">']

    # Compute node centers first (for the spine)
    cy_list = []
    ct = TOP
    for m in milestones:
        h = card_height(m)
        cy_list.append(ct + 34)
        ct += h + GAP

    # Spine line
    out.append(f'  <line x1="{SPINE_X}" y1="{cy_list[0]}" x2="{SPINE_X}" y2="{cy_list[-1]}" '
               f'stroke="{page_spine}" stroke-width="3" stroke-linecap="round"/>')

    # Cards
    ct = TOP
    for m, cy in zip(milestones, cy_list):
        accent = m["accent"]
        h = card_height(m)
        hl = m.get("highlight")
        card_bg = ("#161b22" if dark else light_tint(accent)) if not hl else \
                  ("#1c1709" if dark else light_tint(accent, 0.85))
        border_op = "0.85" if hl else "0.4"
        border_w = "2" if hl else "1"

        # connector node -> card
        out.append(f'  <line x1="{SPINE_X}" y1="{cy}" x2="{CARD_X}" y2="{cy}" '
                   f'stroke="{page_spine}" stroke-width="2"/>')

        # card body
        out.append(f'  <rect x="{CARD_X}" y="{ct}" width="{CARD_W}" height="{h}" rx="12" fill="{card_bg}"/>')
        out.append(f'  <rect x="{CARD_X}" y="{ct}" width="{CARD_W}" height="{h}" rx="12" '
                   f'fill="none" stroke="{accent}" stroke-width="{border_w}" opacity="{border_op}"/>')
        out.append(f'  <rect x="{CARD_X}" y="{ct}" width="4" height="{h}" rx="2" fill="{accent}"/>')

        # date pill (accent bg, white text)
        pill_w = len(m["date"]) * 7 + 22
        pill_y = ct + 13
        out.append(f'  <rect x="{CARD_X + 16}" y="{pill_y}" width="{pill_w}" height="19" rx="9" fill="{accent}"/>')
        out.append(f'  <text x="{CARD_X + 16 + pill_w/2:.0f}" y="{pill_y + 13}" text-anchor="middle" '
                   f'font-family="{EFONT}" font-size="11" font-weight="700" fill="#ffffff">{esc(m["date"])}</text>')

        # tag (accent text, right-aligned on the pill row); lightened in dark mode for contrast
        tag_col = lighten(accent, 0.5) if dark else accent
        out.append(f'  <text x="{CARD_X + CARD_W - 16}" y="{pill_y + 13}" text-anchor="end" '
                   f'font-family="{FONT}" font-size="11.5" font-weight="600" fill="{tag_col}">{esc(m["tag"])}</text>')

        # title (icon + name)
        ty = ct + 54
        out.append(f'  <text x="{CARD_X + 16}" y="{ty}" font-family="{EFONT}" font-size="15.5" '
                   f'font-weight="700" fill="{title_col}">{esc(m["icon"])}  {esc(m["title"])}</text>')

        # description lines
        dy = ty + 22
        for dl in m["desc"]:
            out.append(f'  <text x="{CARD_X + 16}" y="{dy}" font-family="{FONT}" '
                       f'font-size="12.5" fill="{desc_col}">{esc(dl)}</text>')
            dy += 18

        # node on the spine (highlight = bigger + glow ring)
        if hl:
            out.append(f'  <circle cx="{SPINE_X}" cy="{cy}" r="19" fill="{accent}" opacity="0.18"/>')
            out.append(f'  <circle cx="{SPINE_X}" cy="{cy}" r="13" fill="{accent}" '
                       f'stroke="{node_stroke}" stroke-width="3"/>')
            out.append(f'  <text x="{SPINE_X}" y="{cy + 4}" text-anchor="middle" '
                       f'font-family="{EFONT}" font-size="13" fill="#ffffff">★</text>')
        else:
            out.append(f'  <circle cx="{SPINE_X}" cy="{cy}" r="9" fill="{accent}" '
                       f'stroke="{node_stroke}" stroke-width="3"/>')

        ct += h + GAP

    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import os
    os.makedirs("badges", exist_ok=True)
    with open("badges/academic_timeline.svg", "w", encoding="utf-8") as f:
        f.write(render(MILESTONES, "dark"))
    with open("badges/academic_timeline_light.svg", "w", encoding="utf-8") as f:
        f.write(render(MILESTONES, "light"))
    print("OK - badges/academic_timeline.svg + _light.svg generated")
