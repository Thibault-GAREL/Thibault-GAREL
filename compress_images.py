"""
Crée des versions compressées (qualité modérée) des images des dossiers
Logo_Featured_Projects et Logo_Group_Projects, dans des dossiers parallèles
suffixés _compressed. Objectif : réduire le temps de chargement du README
sans perte visuelle notable.

- PNG  : optimize=True (recompression sans perte)
- JPEG : quality=75, optimize=True, progressive=True
- GIF  : palette 128 couleurs, optimize=True (préserve toutes les frames)
"""
from PIL import Image, ImageSequence
import os

SRC_FOLDERS = ['Logo_Featured_Projects', 'Logo_Group_Projects']
SUFFIX = '_compressed'

JPEG_QUALITY = 75
GIF_COLORS = 128


def compress_static(src_path, dst_path):
    img = Image.open(src_path)
    ext = os.path.splitext(dst_path)[1].lower()

    if ext in ('.jpg', '.jpeg'):
        img = img.convert('RGB')
        img.save(dst_path, format='JPEG',
                 quality=JPEG_QUALITY, optimize=True, progressive=True)
    elif ext == '.png':
        img.save(dst_path, format='PNG', optimize=True)
    else:
        img.save(dst_path)


def compress_gif(src_path, dst_path):
    src = Image.open(src_path)
    n = getattr(src, 'n_frames', 1)

    if n <= 1:
        compress_static(src_path, dst_path)
        return

    frames = []
    durations = []
    for i in range(n):
        src.seek(i)
        durations.append(src.info.get('duration', 100))
        frame = src.copy().convert('RGBA')
        frame_p = frame.convert('RGB').quantize(
            colors=GIF_COLORS, method=Image.Quantize.MEDIANCUT)
        frames.append(frame_p)

    frames[0].save(
        dst_path,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        loop=src.info.get('loop', 0),
        duration=durations,
        optimize=True,
        disposal=2,
    )


def folder_size_mb(folder):
    total = 0
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            total += os.path.getsize(fpath)
    return total / (1024 * 1024)


for folder in SRC_FOLDERS:
    if not os.path.isdir(folder):
        print(f'  !  Dossier introuvable : {folder}')
        continue

    dst_folder = folder + SUFFIX
    os.makedirs(dst_folder, exist_ok=True)

    src_size = folder_size_mb(folder)
    print(f'\n=== {folder}  →  {dst_folder}  ({src_size:.2f} MB) ===')

    for fname in sorted(os.listdir(folder)):
        ext = fname.lower().rsplit('.', 1)[-1]
        if ext not in ('png', 'jpg', 'jpeg', 'gif'):
            continue

        src_path = os.path.join(folder, fname)
        dst_path = os.path.join(dst_folder, fname)

        try:
            if ext == 'gif':
                compress_gif(src_path, dst_path)
            else:
                compress_static(src_path, dst_path)

            src_kb = os.path.getsize(src_path) / 1024
            dst_kb = os.path.getsize(dst_path) / 1024
            ratio = (1 - dst_kb / src_kb) * 100 if src_kb else 0
            print(f'  ✓  {fname:45s}  {src_kb:8.1f} KB → {dst_kb:8.1f} KB  ({ratio:+.1f}%)')
        except Exception as e:
            print(f'  ✗  {fname}  →  {e}')

    dst_size = folder_size_mb(dst_folder)
    saved = (1 - dst_size / src_size) * 100 if src_size else 0
    print(f'  TOTAL : {src_size:.2f} MB → {dst_size:.2f} MB  ({saved:+.1f}%)')

print('\nTerminé.')
