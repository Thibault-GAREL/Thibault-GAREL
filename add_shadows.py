"""
Replace filter-based drop shadows with stacked translucent rects.
This approach works in all renderers (no filter needed) and is always visible.

Strategy:
- Strip old feDropShadow filter from each SVG
- Extend SVG dimensions to accommodate the shadow
- Draw 3 shadow rects BEFORE the card background, offset to bottom-right
"""

import re
from pathlib import Path


# ── helpers ───────────────────────────────────────────────────────────────────

def get_accent(content):
    m = re.search(r'\bstroke="(#[0-9a-fA-F]{6})"', content)
    if m:
        return m.group(1)
    for m in re.finditer(r'<rect\b[^>]*\bfill="(#[0-9a-fA-F]{6})"', content):
        c = m.group(1).lower()
        if c not in ('#0d1117', '#1e293b', '#111111', '#ffffff'):
            return m.group(1)
    return '#888888'


def is_light(content):
    m = re.search(r'<rect\b[^>]*\bfill="(#[0-9a-fA-F]{6})"', content)
    if not m:
        return False
    h = m.group(1).lstrip('#')
    r, g, b = int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299*r + 0.587*g + 0.114*b) > 150


def strip_old_filter(content):
    # Remove entire <defs> block containing our shadow filter
    content = re.sub(
        r'\s*<defs>\s*<filter id="sh"[\s\S]*?</filter>\s*</defs>',
        '', content
    )
    # Remove filter attr and overflow attr
    content = re.sub(r'\s*filter="url\(#sh\)"', '', content)
    content = re.sub(r'\s*overflow="visible"', '', content)
    return content


# ── main ──────────────────────────────────────────────────────────────────────

SKIP = {'spacer.svg'}  # 1-px transparent spacer used in the Skills & Tools table layout

# Shadow layers: (dx, dy, opacity_dark, opacity_light)
CARD_LAYERS  = [(8, 9, 0.30, 0.18), (5, 6, 0.22, 0.13), (3, 4, 0.14, 0.08)]
BADGE_LAYERS = [(5, 6, 0.38, 0.22), (3, 4, 0.26, 0.15)]

# Detect "already has stacked shadow rects" by matching an offset rect with opacity (a property
# the generator only ever emits for shadow layers, never the card bg/border).
SHADOW_RECT_RE = re.compile(
    r'<rect\s+x="\d+"\s+y="\d+"\s+width="\d+"\s+height="\d+"\s+rx="\d+"\s+'
    r'fill="#[0-9a-fA-F]{6}"\s+opacity="0\.\d+"\s*/>'
)


def apply_shadows() -> int:
    total = 0
    for directory in [Path('badges'), Path('badges/cards')]:
        for svg_path in sorted(directory.glob('*.svg')):
            if svg_path.name in SKIP:
                continue

            raw = svg_path.read_text(encoding='utf-8')
            content = strip_old_filter(raw)

            # Idempotency: skip if shadow rects already present (re-running compounds otherwise).
            if SHADOW_RECT_RE.search(content):
                print(f'  [skip] already has shadow: {svg_path.relative_to("badges")}')
                continue

            accent = get_accent(content)
            light  = is_light(content)
            is_badge = svg_path.parent.name != 'cards'
            layers = BADGE_LAYERS if is_badge else CARD_LAYERS

            wm = re.search(r'<svg\b[^>]*\bwidth="(\d+)"', content)
            hm = re.search(r'<svg\b[^>]*\bheight="(\d+)"', content)
            if not wm or not hm:
                print(f'  [skip] no dims: {svg_path.name}')
                continue
            ow, oh = int(wm.group(1)), int(hm.group(1))

            pad_x, pad_y = (6, 8) if is_badge else (10, 11)
            nw, nh = ow + pad_x, oh + pad_y

            content = re.sub(r'(<svg\b[^>]*\bwidth=")(\d+)"',  f'\\g<1>{nw}"', content)
            content = re.sub(r'(<svg\b[^>]*\bheight=")(\d+)"', f'\\g<1>{nh}"', content)

            rxm = re.search(r'<rect\b[^>]*\brx="(\d+)"', content)
            rx  = int(rxm.group(1)) if rxm else 12

            shadow_html = ''
            for dx, dy, op_dark, op_light in layers:
                op = op_light if light else op_dark
                shadow_html += (
                    f'  <rect x="{dx}" y="{dy}" width="{ow}" height="{oh}" '
                    f'rx="{rx}" fill="{accent}" opacity="{op}"/>\n'
                )

            idx = content.find('<rect ')
            content = content[:idx] + shadow_html + content[idx:]

            svg_path.write_text(content, encoding='utf-8')
            tag = 'light' if light else 'dark'
            print(f'  ✓  {svg_path.relative_to("badges")}  [{tag}]  {ow}×{oh}→{nw}×{nh}  {accent}')
            total += 1
    return total


if __name__ == '__main__':
    n = apply_shadows()
    print(f'\n{n} SVGs updated.')
