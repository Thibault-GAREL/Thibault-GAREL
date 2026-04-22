"""
Add rounded corners + colored drop shadow to all project logos and GIFs.
- Static images (PNG, JPG) → saved as PNG with full RGBA transparency
- Animated GIFs → each frame processed, saved back as animated GIF
All images are first resized to display height (140px) then padded with shadow.
"""

import re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageSequence


# ── accent color per filename prefix ─────────────────────────────────────────

ACCENT = {
    'gen_ai':            '#6e40c9',
    'neural':            '#2563eb',
    'rl_snake_decision': '#22c55e',
    'rl_snake_ppo':      '#059669',
    'rl_snake_dql':      '#10b981',
    'rl_snake_genetic':  '#16a34a',
    'rl_snake':          '#10b981',
    'rl_driving_dql':    '#10b981',
    'rl_driving':        '#16a34a',
    'rl_walking':        '#16a34a',
    'rl_q_learning':     '#10b981',
    'rl_starcraft':      '#059669',
    'rl_sc2':            '#059669',
    'rl_unity':          '#0f766e',
    'speech':            '#ea580c',
    'robotics':          '#dc2626',
    'game':              '#0891b2',
    'physics':           '#0d9488',
    'n8n':               '#db2777',
    'data':              '#d97706',
    'group':             '#00b4c2',
}

def get_accent(stem):
    stem = stem.lower()
    for prefix, color in ACCENT.items():
        if stem.startswith(prefix):
            return color
    return '#888888'

def hex_rgb(h):
    h = h.lstrip('#')
    return int(h[:2], 16), int(h[2:4], 16), int(h[4:6], 16)


# ── image processing ──────────────────────────────────────────────────────────

DISPLAY_H  = 140   # target display height in README
RADIUS     = 14    # corner radius (pixels at display size)
SHADOW_DX  = 9     # shadow offset right
SHADOW_DY  = 10    # shadow offset down
PAD_X      = 11    # extra canvas width for shadow
PAD_Y      = 12    # extra canvas height for shadow
SHADOW_LAYERS = [  # (dx, dy, opacity) — outer drawn first, inner last (REPLACE mode)
    (SHADOW_DX,     SHADOW_DY,     0.13),   # outermost = lightest
    (SHADOW_DX - 3, SHADOW_DY - 3, 0.22),   # middle
    (SHADOW_DX - 6, SHADOW_DY - 6, 0.38),   # innermost = darkest (closest to image)
]


def resize_to_height(img, h):
    """Resize an image to target height, maintaining aspect ratio."""
    w = max(1, int(img.width * h / img.height))
    return img.resize((w, h), Image.LANCZOS)


def make_round_mask(size, radius):
    """Return an L-mode mask with anti-aliased rounded corners (2× supersample)."""
    scale = 4
    big = Image.new('L', (size[0] * scale, size[1] * scale), 0)
    draw = ImageDraw.Draw(big)
    draw.rounded_rectangle([0, 0, big.width - 1, big.height - 1],
                            radius=radius * scale, fill=255)
    return big.resize(size, Image.LANCZOS)


def apply_shadow(frame_rgba, accent_hex):
    """
    Draw 3 shadow rects then paste the rounded-corner image on top.
    Returns a larger RGBA canvas.
    """
    w, h = frame_rgba.size
    canvas = Image.new('RGBA', (w + PAD_X, h + PAD_Y), (0, 0, 0, 0))
    draw   = ImageDraw.Draw(canvas)
    r, g, b = hex_rgb(accent_hex)

    for dx, dy, op in sorted(SHADOW_LAYERS, key=lambda x: -x[0]):  # outer first
        a = int(op * 255)
        draw.rounded_rectangle([dx, dy, dx + w - 1, dy + h - 1],
                                radius=RADIUS, fill=(r, g, b, a))

    canvas.paste(frame_rgba, (0, 0), frame_rgba)
    return canvas


def process_frame(img_any, accent_hex):
    """Resize, round corners, add shadow. Returns RGBA."""
    img  = resize_to_height(img_any.convert('RGBA'), DISPLAY_H)
    mask = make_round_mask(img.size, RADIUS)
    img.putalpha(mask)
    return apply_shadow(img, accent_hex)


# ── GIF save helper ───────────────────────────────────────────────────────────

GH_DARK = np.array([13, 17, 23], dtype=np.float32)   # GitHub dark background (#0d1117)
TRANS_IDX = 255  # palette slot reserved for GIF transparency

def save_animated_gif(frames_rgba, durations, path):
    """
    Save RGBA frames as animated GIF with proper corner transparency.
    - Corner pixels (alpha=0) → transparent via GIF palette index 255
    - Shadow pixels (0 < alpha < 255) → composited on GH_DARK
    """
    frames_p = []

    for f in frames_rgba:
        arr    = np.array(f, dtype=np.float32)
        rgb    = arr[:, :, :3]
        alpha  = arr[:, :, 3]

        # Pixels that must be transparent (rounded-corner cutouts)
        corner_mask = (alpha == 0)

        # Composite all pixels on dark bg (corners will be masked out after quantize)
        a3       = (alpha / 255.0)[:, :, np.newaxis]
        rgb_comp = (rgb * a3 + GH_DARK * (1 - a3)).clip(0, 255).astype(np.uint8)

        # Quantize to 255 colors, leaving slot 255 for transparency key
        img_q = Image.fromarray(rgb_comp).quantize(colors=TRANS_IDX, dither=1)

        # Extend palette to 256 entries; last entry = transparent key color (pure black)
        pal = img_q.getpalette()[:TRANS_IDX * 3] + [0, 0, 0]
        img_q.putpalette(pal)

        # Stamp corner pixels with the transparent index
        arr_q = np.array(img_q, dtype=np.uint8)
        arr_q[corner_mask] = TRANS_IDX

        frame_p = Image.fromarray(arr_q, 'P')
        frame_p.putpalette(pal)
        frames_p.append(frame_p)

    frames_p[0].save(
        path,
        format='GIF',
        save_all=True,
        append_images=frames_p[1:],
        duration=durations,
        loop=0,
        transparency=TRANS_IDX,
        disposal=2,       # clear to background (transparent) after each frame
        optimize=False,
    )


# ── main ──────────────────────────────────────────────────────────────────────

DIRS = [
    Path('Logo_Featured_Projects'),
    Path('Logo_Group_Projects'),
]
SKIP = {'REs.png', 'Insigne_CND.png',  # raw unused sources
        'group_hackathon_cnd.png', 'group_ppe_smart_contract.jpg',
        'group_resilient_ai.jpg'}       # non-square originals (sq versions used)

total = 0
readme_renames = {}   # old_rel → new_rel for JPG→PNG renames
processed_stems = set()   # avoid double-processing stem when JPG+PNG both exist

for d in DIRS:
    for img_path in sorted(d.glob('*')):
        if img_path.name in SKIP:
            continue
        suffix = img_path.suffix.lower()
        if suffix not in {'.png', '.jpg', '.jpeg', '.gif'}:
            continue

        if img_path.stem in processed_stems:
            print(f'  skip (already processed)  {img_path}')
            continue
        accent = get_accent(img_path.stem)
        print(f'  processing  {img_path}  accent={accent}')

        # ── animated GIF ──────────────────────────────────────────────────────
        if suffix == '.gif':
            src   = Image.open(img_path)
            frames, durations = [], []
            for frame in ImageSequence.Iterator(src):
                dur = frame.info.get('duration', 80)
                frames.append(process_frame(frame, accent))
                durations.append(dur)
            save_animated_gif(frames, durations, img_path)
            processed_stems.add(img_path.stem)
            print(f'  ✓  GIF  {img_path.name}  ({len(frames)} frames)')

        # ── static image ──────────────────────────────────────────────────────
        else:
            src    = Image.open(img_path)
            result = process_frame(src, accent)

            # Always save as PNG to support RGBA transparency
            out_path = img_path.with_suffix('.png')
            result.save(out_path, 'PNG', optimize=True)

            if img_path.suffix.lower() in {'.jpg', '.jpeg'}:
                # Record rename so we can patch README
                readme_renames[str(img_path).replace('\\', '/')] = \
                    str(out_path).replace('\\', '/')
                img_path.unlink()   # remove original JPG
                print(f'  ✓  JPG→PNG  {out_path.name}')
            else:
                print(f'  ✓  PNG  {out_path.name}')
            processed_stems.add(img_path.stem)

        total += 1

print(f'\n{total} images processed.')

# ── patch README for JPG→PNG renames ─────────────────────────────────────────

if readme_renames:
    readme = Path('README.md').read_text(encoding='utf-8')
    for old, new in readme_renames.items():
        # use only the relative path from repo root
        old_rel = re.sub(r'^.*?(Logo_)', r'\1', old)
        new_rel = re.sub(r'^.*?(Logo_)', r'\1', new)
        readme = readme.replace(old_rel, new_rel)
    Path('README.md').write_text(readme, encoding='utf-8')
    print(f'README patched for {len(readme_renames)} JPG→PNG renames.')
