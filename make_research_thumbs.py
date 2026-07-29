"""Build the assets of the Research paper section (OPENER).

Two outputs, both following the format used by every other project of the README:

1. Three logo tiles in `Logo_Featured_Projects[_compressed]/`, at the standard
   210x140 content size (canvas 221x152 once the gold shadow is added). Each tile
   is a white 3:2 card with a colored label band at the bottom:
   OPENER paper (gold), OPENER model (Hugging Face yellow), OPENER code (GitHub black).
2. Three description cards in `badges/cards/`, dark plus light variant, generated
   with `generate_cards.svg()` then `add_shadows` and the light-tint rules of
   `generate_light_cards`.

Unlike the other logos, two of the three sources are vector or PDF based (the HF
logo is drawn here as an SVG, the architecture comes from the project's SVG
diagram) and no SVG rasteriser is installed in the venvs, so headless Chrome does
the rasterising and Pillow the composition.

Usage (needs the LyRIDS_OPENER repo cloned next to this one):
    python make_research_thumbs.py
"""

import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import add_shadows
from categories import CATEGORIES
from generate_cards import projects as all_projects
from generate_cards import svg as card_svg
from generate_light_cards import light_tint
from round_logos import DISPLAY_H, process_frame

# ── paths ─────────────────────────────────────────────────────────────────────

OPENER_REPO = Path(r'D:\Loisir\Code_python\LyRIDS_Opener')
PAPER_PAGE  = OPENER_REPO / 'assets' / 'paper_pages' / 'page-01.png'
ARCHI_SVG   = OPENER_REPO / 'assets' / 'opener-architecture-v3.svg'

LOGO_DIRS = [
    Path('Logo_Featured_Projects'),
    Path('Logo_Featured_Projects_compressed'),
]
CARDS_DIR = Path('badges/cards')

CHROME    = Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
FONT_BOLD = Path(r'C:\Windows\Fonts\seguisb.ttf')      # Segoe UI Semibold

ACCENT = CATEGORIES['research'][1]   # gold #d4af37

# ── tile geometry (5x the final 210x140 so the downscale stays sharp) ─────────

SCALE     = 5
TILE_W    = 210 * SCALE
TILE_H    = DISPLAY_H * SCALE
BAND_H    = 34 * SCALE               # bottom label band
IMAGE_H   = TILE_H - BAND_H          # area left for the visual
LABEL_PT  = 21 * SCALE

# Square variants for the Vercel portfolio: its ProjectCard crops images with
# `object-cover` inside a 128x128 box, which would cut the label off a 3:2 tile.
# Same `_sq` convention as the group-project logos (they are listed in
# round_logos.SKIP so the shadow pipeline leaves them alone).
SQ_SIZE   = 440
SQ_BAND_H = 84
SQ_LABEL_PT = 46

# (file stem, label, band color, label color)
# One single yellow for the three bands, so the row reads as one project. Earlier
# tries with a per-destination color (gold for the paper, GitHub black then bronze
# for the code) broke that unity.
BAND      = '#FFD21E'   # Hugging Face brand yellow
BAND_TEXT = '#2d2d2d'

TILES = [
    ('research_opener_paper',  'OPENER paper', BAND, BAND_TEXT),
    ('research_opener_model',  'OPENER model', BAND, BAND_TEXT),
    ('research_opener_code',   'OPENER code',  BAND, BAND_TEXT),
]

# Architecture diagram: keep only the pipeline. The title line is unreadable once
# downscaled, and the legend block plus the trailing white area of the 980x1080
# canvas would only shrink the useful part.
ARCHI_TOP_Y    = 88
ARCHI_LEGEND_Y = 872

# Hugging Face visual, matching badges/huggingface.svg (the 🤗 brand emoji).
HF_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 300" width="420" height="300">
  <rect width="420" height="300" fill="#ffffff"/>
  <text x="210" y="245" font-size="245" text-anchor="middle">\U0001f917</text>
</svg>
"""

# Chrome renders a standalone SVG scaled and offset inside the viewport, so the
# markup is wrapped in a zero-margin page to get an exact 1:1 framing.
HTML_WRAPPER = """<!doctype html><meta charset="utf-8">
<style>html,body{{margin:0;padding:0;background:#fff}}svg{{display:block}}</style>
{svg}"""

# In headless=new the window decoration eats ~100 px of viewport height, which
# silently clips the bottom of the render. The window is asked taller than needed
# and the screenshot is cropped back to the exact SVG size.
WINDOW_SLACK = 240

# ── description cards ────────────────────────────────────────────────────────
# Wording lives in generate_cards.projects, so both scripts stay in sync.

CARDS = [p for p in all_projects if p[1] == 'research']


# ── rendering helpers ─────────────────────────────────────────────────────────

def hex_rgb(h):
    h = h.lstrip('#')
    return int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def render_svg(svg: str, width: int, height: int, scale: int = 4) -> Image.Image:
    """Rasterise SVG markup through headless Chrome and return it as an RGB image."""
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / 'page.html'
        png  = Path(tmp) / 'render.png'
        page.write_text(HTML_WRAPPER.format(svg=svg), encoding='utf-8')
        subprocess.run(
            [str(CHROME), '--headless=new', '--disable-gpu', '--hide-scrollbars',
             f'--force-device-scale-factor={scale}',
             f'--window-size={width},{height + WINDOW_SLACK}',
             f'--screenshot={png}', page.resolve().as_uri()],
            check=True, capture_output=True,
        )
        return Image.open(png).convert('RGB').crop((0, 0, width * scale, height * scale))


def trim_white(img: Image.Image, tol: int = 250) -> Image.Image:
    """Crop the uniform near-white border around the content."""
    gray = img.convert('L').point(lambda v: 0 if v >= tol else 255)
    bbox = gray.getbbox()
    return img.crop(bbox) if bbox else img


def build_tile(visual: Image.Image, label: str, band: str, fg: str,
               size: tuple[int, int] = (TILE_W, TILE_H),
               band_h: int = BAND_H, label_pt: int = LABEL_PT) -> Image.Image:
    """White card: visual fitted in the upper area, colored label band below."""
    width, height = size
    image_h = height - band_h
    tile = Image.new('RGB', size, 'white')

    fitted = visual.copy()
    fitted.thumbnail((width, image_h), Image.LANCZOS)
    tile.paste(fitted, ((width - fitted.width) // 2, (image_h - fitted.height) // 2))

    draw = ImageDraw.Draw(tile)
    draw.rectangle([0, image_h, width, height], fill=hex_rgb(band))
    font = ImageFont.truetype(str(FONT_BOLD), label_pt)
    bbox = draw.textbbox((0, 0), label, font=font)
    draw.text(((width - (bbox[2] - bbox[0])) // 2 - bbox[0],
               image_h + (band_h - (bbox[3] - bbox[1])) // 2 - bbox[1]),
              label, font=font, fill=hex_rgb(fg))
    return tile


def save_tile(tile: Image.Image, name: str) -> None:
    """Round corners, add the gold shadow, write to both logo folders."""
    out = process_frame(tile, ACCENT)
    for logo_dir in LOGO_DIRS:
        logo_dir.mkdir(exist_ok=True)
        path = logo_dir / name
        out.save(path, 'PNG', optimize=True)
        print(f'  ok  {path}  {out.width}x{out.height}')


def write_light_variant(stem: str) -> None:
    """Derive `<stem>_light.svg` with the exact rules of generate_light_cards.py."""
    content = (CARDS_DIR / f'{stem}.svg').read_text(encoding='utf-8')
    accent  = re.search(r'stroke="(#[0-9a-fA-F]{6})"', content).group(1)
    light   = (content
               .replace('fill="#0d1117"', f'fill="{light_tint(accent)}"')
               .replace('fill="#f0f6fc"', 'fill="#24292f"')
               .replace('fill="#8b949e"', 'fill="#57606a"')
               .replace('fill="#ffffff"', 'fill="#24292f"'))
    (CARDS_DIR / f'{stem}_light.svg').write_text(light, encoding='utf-8')
    print(f'  ok  {CARDS_DIR / (stem + "_light.svg")}')


def apply_card_shadow(path: Path) -> None:
    """Stack the 3 shadow rects of add_shadows.py on one card only.

    `add_shadows.apply_shadows()` walks the whole badges/ tree, which would also
    hit the two timeline SVGs, deliberately kept shadowless. Same geometry and
    same opacities, applied to a single file.

    Idempotency is checked on the outermost shadow rect rather than on
    `add_shadows.SHADOW_RECT_RE`: that pattern also matches the label badge rect
    (`x`, `y`, `width`, `height`, `rx`, `fill`, `opacity`) that `generate_cards.svg()`
    emits, so it reports every freshly generated card as already shadowed.
    """
    content = add_shadows.strip_old_filter(path.read_text(encoding='utf-8'))
    dx0, dy0 = add_shadows.CARD_LAYERS[0][:2]
    if f'<rect x="{dx0}" y="{dy0}" width="' in content:
        print(f'  skip (already shadowed)  {path}')
        return

    accent = add_shadows.get_accent(content)
    light  = add_shadows.is_light(content)
    ow = int(re.search(r'<svg\b[^>]*\bwidth="(\d+)"', content).group(1))
    oh = int(re.search(r'<svg\b[^>]*\bheight="(\d+)"', content).group(1))
    rx = int(re.search(r'<rect\b[^>]*\brx="(\d+)"', content).group(1))

    content = re.sub(r'(<svg\b[^>]*\bwidth=")(\d+)"',  f'\\g<1>{ow + 10}"', content)
    content = re.sub(r'(<svg\b[^>]*\bheight=")(\d+)"', f'\\g<1>{oh + 11}"', content)

    shadow = ''.join(
        f'  <rect x="{dx}" y="{dy}" width="{ow}" height="{oh}" '
        f'rx="{rx}" fill="{accent}" opacity="{op_light if light else op_dark}"/>\n'
        for dx, dy, op_dark, op_light in add_shadows.CARD_LAYERS
    )
    idx = content.find('<rect ')
    path.write_text(content[:idx] + shadow + content[idx:], encoding='utf-8')
    print(f'  ok  {path}  [{"light" if light else "dark"}]  {ow}x{oh} -> {ow + 10}x{oh + 11}')


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print(f'accent = {ACCENT}   tile = 210x{DISPLAY_H}  (band {BAND_H // SCALE}px)')

    print('\nvisuals')
    # The page margins are trimmed first: kept as-is, the sheet floats inside the
    # tile with a white border, which makes it look smaller than the other logos
    # even though every tile is exactly 221x152.
    paper_page = trim_white(Image.open(PAPER_PAGE).convert('RGB'))

    def paper_top(width: int, height: int) -> Image.Image:
        """Top of the first page (title, authors, abstract), cropped to fit width:height."""
        return paper_page.crop((0, 0, paper_page.width,
                                min(paper_page.height,
                                    round(paper_page.width * height / width))))

    paper = paper_top(TILE_W, IMAGE_H)
    hf = render_svg(HF_SVG, 420, 300)
    archi = render_svg(ARCHI_SVG.read_text(encoding='utf-8'), 980, 1080)
    ascale = archi.height / 1080                                 # device px per SVG unit
    archi = trim_white(archi.crop((0, int(ARCHI_TOP_Y * ascale),
                                   archi.width, int(ARCHI_LEGEND_Y * ascale))))

    print('\nlogo tiles')
    for visual, (stem, label, band, fg) in zip([paper, hf, archi], TILES):
        save_tile(build_tile(visual, label, band, fg), f'{stem}.png')

    print('\nsquare variants (portfolio)')
    paper_sq = paper_top(SQ_SIZE, SQ_SIZE - SQ_BAND_H)
    for visual, (stem, label, band, fg) in zip([paper_sq, hf, archi], TILES):
        square = build_tile(visual, label, band, fg, size=(SQ_SIZE, SQ_SIZE),
                            band_h=SQ_BAND_H, label_pt=SQ_LABEL_PT)
        for logo_dir in LOGO_DIRS:
            path = logo_dir / f'{stem}_sq.png'
            square.save(path, 'PNG', optimize=True)
            print(f'  ok  {path}  {square.width}x{square.height}')

    # Pipeline order matters: the light variant is derived from the shadowless
    # dark card, then both get their own shadow opacities.
    print('\ndescription cards')
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    for stem, cat, title, desc, links, members in CARDS:
        (CARDS_DIR / f'{stem}.svg').write_text(
            card_svg(cat, title, desc, links, members, min_h=DISPLAY_H), encoding='utf-8')
        print(f'  ok  {CARDS_DIR / (stem + ".svg")}')
        write_light_variant(stem)

    print('\ncard shadows')
    for stem, *_ in CARDS:
        apply_card_shadow(CARDS_DIR / f'{stem}.svg')
        apply_card_shadow(CARDS_DIR / f'{stem}_light.svg')


if __name__ == '__main__':
    main()
