"""
Generate light-mode versions of all project card SVGs,
then update README.md to use <picture> for dark/light switching.
"""

import re
from pathlib import Path


def hex_to_rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def light_tint(accent_hex, white_ratio=0.92):
    """Blend accent color with white at white_ratio to produce a subtle tint."""
    r, g, b = hex_to_rgb(accent_hex)
    lr = int(255 * white_ratio + r * (1 - white_ratio))
    lg = int(255 * white_ratio + g * (1 - white_ratio))
    lb = int(255 * white_ratio + b * (1 - white_ratio))
    return f"#{lr:02x}{lg:02x}{lb:02x}"


CARDS_DIR = Path("badges/cards")

# ── 1. Generate _light.svg files ──────────────────────────────────────────────

for svg_path in sorted(CARDS_DIR.glob("*.svg")):
    if svg_path.stem.endswith("_light"):
        continue

    content = svg_path.read_text(encoding="utf-8")

    # Extract accent color from the border rect stroke
    m = re.search(r'stroke="(#[0-9a-fA-F]{6})"', content)
    if not m:
        print(f"  [skip] no accent found in {svg_path.name}")
        continue

    accent = m.group(1)
    bg = light_tint(accent)

    light = content
    # Dark background → light tint
    light = light.replace('fill="#0d1117"', f'fill="{bg}"')
    # Title text: near-white → near-black
    light = light.replace('fill="#f0f6fc"', 'fill="#24292f"')
    # Description text: muted gray → GitHub light secondary
    light = light.replace('fill="#8b949e"', 'fill="#57606a"')

    out_path = CARDS_DIR / f"{svg_path.stem}_light.svg"
    out_path.write_text(light, encoding="utf-8")
    print(f"  ✓  {out_path.name}  (bg={bg}, accent={accent})")

print(f"\n{len(list(CARDS_DIR.glob('*_light.svg')))} light SVGs generated.\n")

# ── 2. Update README.md ────────────────────────────────────────────────────────

readme_path = Path("README.md")
readme = readme_path.read_text(encoding="utf-8")

# Match bare <img src="badges/cards/NAME.svg" width="N"/> (no picture wrapper yet)
pattern = re.compile(
    r'<img src="(badges/cards/(?!.*_light)[^"]+\.svg)" (width|height)="(\d+)"/>'
)

def wrap_with_picture(m):
    src   = m.group(1)          # e.g. badges/cards/gen_ai_gan.svg
    attr  = m.group(2)          # width or height
    val   = m.group(3)          # e.g. 200
    # derive light src:  badges/cards/gen_ai_gan_light.svg
    light_src = src.replace(".svg", "_light.svg")
    return (
        f'<picture>'
        f'<source media="(prefers-color-scheme: light)" srcset="{light_src}"/>'
        f'<img src="{src}" {attr}="{val}"/>'
        f'</picture>'
    )

new_readme = pattern.sub(wrap_with_picture, readme)

if new_readme == readme:
    print("README already up-to-date (no bare card <img> tags found).")
else:
    readme_path.write_text(new_readme, encoding="utf-8")
    count = len(pattern.findall(readme))
    print(f"README updated: {count} card <img> tags wrapped in <picture>.")
