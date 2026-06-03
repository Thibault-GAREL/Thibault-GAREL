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


def generate_light_variants() -> int:
    """Derive `*_light.svg` from each dark `*.svg` by swapping color tokens."""
    n = 0
    for svg_path in sorted(CARDS_DIR.glob("*.svg")):
        if svg_path.stem.endswith("_light"):
            continue

        content = svg_path.read_text(encoding="utf-8")
        m = re.search(r'stroke="(#[0-9a-fA-F]{6})"', content)
        if not m:
            print(f"  [skip] no accent found in {svg_path.name}")
            continue

        accent = m.group(1)
        bg = light_tint(accent)

        light = content
        light = light.replace('fill="#0d1117"', f'fill="{bg}"')        # bg
        light = light.replace('fill="#f0f6fc"', 'fill="#24292f"')      # title
        light = light.replace('fill="#8b949e"', 'fill="#57606a"')      # desc
        light = light.replace('fill="#ffffff"', 'fill="#24292f"')      # label

        out_path = CARDS_DIR / f"{svg_path.stem}_light.svg"
        out_path.write_text(light, encoding="utf-8")
        print(f"  ✓  {out_path.name}  (bg={bg}, accent={accent})")
        n += 1
    return n

# Wrap bare <img src="badges/cards/NAME.svg" width="N"/> with <picture> for dark/light.
# Use a stateful parser so we don't double-wrap <img> tags already inside a <picture> block.
# (The previous regex-only approach with (?!.*_light) was buggy: it succeeded on the LAST
#  inner img of each line, producing nested <picture><picture> wrappers.)
IMG_RE = re.compile(
    r'<img src="(badges/cards/(?!.*_light\.svg)[^"]+\.svg)" (width|height)="(\d+)"/>'
)

def wrap_cards(text: str) -> tuple[str, int]:
    out = []
    i = 0
    n = 0
    while i < len(text):
        if text.startswith("<picture>", i):
            # Skip past existing <picture>...</picture> block untouched
            end = text.find("</picture>", i)
            if end == -1:
                out.append(text[i:])
                break
            end += len("</picture>")
            out.append(text[i:end])
            i = end
            continue
        m = IMG_RE.match(text, i)
        if m:
            src, attr, val = m.group(1), m.group(2), m.group(3)
            light_src = src.replace(".svg", "_light.svg")
            out.append(
                f'<picture>'
                f'<source media="(prefers-color-scheme: light)" srcset="{light_src}"/>'
                f'<img src="{src}" {attr}="{val}"/>'
                f'</picture>'
            )
            i = m.end()
            n += 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out), n


if __name__ == "__main__":
    n_generated = generate_light_variants()
    print(f"\n{n_generated} light SVGs generated.\n")

    readme_path = Path("README.md")
    readme = readme_path.read_text(encoding="utf-8")
    new_readme, count = wrap_cards(readme)

    if new_readme == readme:
        print("README already up-to-date (no bare card <img> tags found).")
    else:
        readme_path.write_text(new_readme, encoding="utf-8")
        print(f"README updated: {count} card <img> tags wrapped in <picture>.")
