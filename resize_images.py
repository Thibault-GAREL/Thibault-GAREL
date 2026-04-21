"""
Redimensionne toutes les images/GIFs des projets à une taille uniforme 300x200
via un crop centré (fill, pas de distorsion, pas de bandes noires).
"""
from PIL import Image, ImageSequence
import os

TARGET_W, TARGET_H = 300, 200

def fill_crop(img, tw, th):
    """Scale to fill, then center-crop."""
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw = max(int(sw * scale), 1)
    nh = max(int(sh * scale), 1)
    img = img.resize((nw, nh), Image.LANCZOS)
    left = (nw - tw) // 2
    top  = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))

def process_gif(path, tw, th):
    src = Image.open(path)
    n = getattr(src, 'n_frames', 1)
    if n <= 1:
        # Traiter comme image statique
        process_static(path, tw, th)
        return

    frames = []
    durations = []
    for i in range(n):
        src.seek(i)
        dur = src.info.get('duration', 100)
        durations.append(dur)
        frame = src.copy().convert('RGBA')
        frame = fill_crop(frame, tw, th)
        # Convertir en palette pour GIF
        frame_p = frame.convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        frames.append(frame_p)

    frames[0].save(
        path,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=durations,
        optimize=False,
    )

def process_static(path, tw, th):
    img = Image.open(path).convert('RGB')
    img = fill_crop(img, tw, th)
    img.save(path)

FOLDERS = ['Logo_Featured_Projects', 'Logo_Group_Projects']

for folder in FOLDERS:
    for fname in sorted(os.listdir(folder)):
        # Ignorer les fichiers non-image
        ext = fname.lower().rsplit('.', 1)[-1]
        if ext not in ('png', 'jpg', 'jpeg', 'gif'):
            continue
        fpath = os.path.join(folder, fname)
        try:
            if ext == 'gif':
                process_gif(fpath, TARGET_W, TARGET_H)
            else:
                process_static(fpath, TARGET_W, TARGET_H)
            print(f'  ✓  {folder}/{fname}')
        except Exception as e:
            print(f'  ✗  {folder}/{fname}  →  {e}')

print(f'\nTerminé — toutes les images sont en {TARGET_W}x{TARGET_H}')
