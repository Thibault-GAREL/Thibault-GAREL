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
import numpy as np
import os

SRC_FOLDERS = ['Logo_Featured_Projects', 'Logo_Group_Projects']
SUFFIX = '_compressed'

JPEG_QUALITY = 75
GIF_COLORS = 128
TRANS_IDX = 255  # palette slot reserved for GIF transparency


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

    frames_p = []
    durations = []
    for i in range(n):
        src.seek(i)
        durations.append(src.info.get('duration', 100))

        rgba = src.convert('RGBA')
        arr = np.array(rgba, dtype=np.uint8)
        alpha = arr[:, :, 3]
        rgb = arr[:, :, :3]

        # Quantize on RGB with one slot reserved for transparency
        img_rgb = Image.fromarray(rgb)
        img_q = img_rgb.quantize(
            colors=GIF_COLORS - 1, method=Image.Quantize.MEDIANCUT)

        # Reserve palette slot TRANS_IDX for transparent pixels
        pal = img_q.getpalette()[:TRANS_IDX * 3] + [0, 0, 0]
        img_q.putpalette(pal)

        arr_q = np.array(img_q, dtype=np.uint8)
        arr_q[alpha == 0] = TRANS_IDX

        frame_p = Image.fromarray(arr_q, 'P')
        frame_p.putpalette(pal)
        frames_p.append(frame_p)

    frames_p[0].save(
        dst_path,
        format='GIF',
        save_all=True,
        append_images=frames_p[1:],
        loop=src.info.get('loop', 0),
        duration=durations,
        transparency=TRANS_IDX,
        disposal=2,
        optimize=False,
    )


def folder_size_mb(folder):
    total = 0
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        if os.path.isfile(fpath):
            total += os.path.getsize(fpath)
    return total / (1024 * 1024)


if __name__ == '__main__':
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
