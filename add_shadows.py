"""
Add a colored drop shadow (bottom-right) to every project card SVG and badge SVG.
Shadow color = accent color of the SVG (stroke color for cards, fill for badges).
"""

import re
from pathlib import Path


# ── helpers ───────────────────────────────────────────────────────────────────

def get_accent_color(content):
    """Return accent color: stroke for cards, first non-dark rect fill for badges."""
    m = re.search(r'\bstroke="(#[0-9a-fA-F]{6})"', content)
    if m:
        return m.group(1)
    for m in re.finditer(r'<rect\b[^>]*\bfill="(#[0-9a-fA-F]{6})"', content):
        c = m.group(1).lower()
        if c not in ('#0d1117', '#1e293b', '#111111', '#ffffff', 'none'):
            return m.group(1)
    return '#888888'


def is_light_bg(content):
    """True if the first rect (background) is light-colored."""
    m = re.search(r'<rect\b[^>]*\bfill="(#[0-9a-fA-F]{6})"', content)
    if not m:
        return False
    h = m.group(1).lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    # Perceived luminance
    return (0.299 * r + 0.587 * g + 0.114 * b) > 150


def add_shadow(content, color, opacity, dx, dy, blur):
    """Inject <defs>/<filter> and apply to first <rect>. Skip if already done."""
    if 'feDropShadow' in content or 'id="sh"' in content:
        return content

    filter_block = (
        f'  <defs>\n'
        f'    <filter id="sh" x="-25%" y="-25%" width="150%" height="150%">\n'
        f'      <feDropShadow dx="{dx}" dy="{dy}" stdDeviation="{blur}" '
        f'flood-color="{color}" flood-opacity="{opacity}"/>\n'
        f'    </filter>\n'
        f'  </defs>\n'
    )

    # Add overflow="visible" to <svg ...> and insert <defs> right after
    def inject(m):
        tag_attrs = m.group(1)
        # avoid double overflow attr
        if 'overflow' not in tag_attrs:
            tag_attrs += ' overflow="visible"'
        return f'<svg{tag_attrs}>\n{filter_block}'

    content = re.sub(r'<svg([^>]*)>', inject, content, count=1)

    # Apply filter only to first <rect> (the card / badge background)
    content = re.sub(r'(<rect\b)', r'\1 filter="url(#sh)"', content, count=1)

    return content


# ── process files ─────────────────────────────────────────────────────────────

SKIP = {'spacer.svg', 'portfolio_dark.svg', 'gan_card.svg'}

total = 0

for directory in [Path('badges'), Path('badges/cards')]:
    for svg_path in sorted(directory.glob('*.svg')):
        if svg_path.name in SKIP:
            continue

        content = svg_path.read_text(encoding='utf-8')
        accent  = get_accent_color(content)
        light   = is_light_bg(content)

        # Shadow params: cards get a softer / larger shadow, badges a tighter one
        is_card = svg_path.parent.name == 'cards'
        if is_card and light:
            opacity, dx, dy, blur = 0.28, 5, 6, 8
        elif is_card:
            opacity, dx, dy, blur = 0.45, 6, 7, 9
        else:                          # badges (pills)
            opacity, dx, dy, blur = 0.45, 3, 4, 6

        new_content = add_shadow(content, accent, opacity, dx, dy, blur)

        if new_content != content:
            svg_path.write_text(new_content, encoding='utf-8')
            tag = 'light' if light else 'dark'
            print(f'  ✓  {svg_path.relative_to("badges")}  [{tag}]  shadow={accent}')
            total += 1
        else:
            print(f'  –  {svg_path.relative_to("badges")}  (skipped)')

print(f'\n{total} SVGs updated.')
