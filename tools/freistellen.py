#!/usr/bin/env python3
"""Stellt die Tierbilder aus tiere/original/ frei (heller Hintergrund -> transparent)
und speichert sie zugeschnitten als tiere/<name>.png.

Aufruf: python3 tools/freistellen.py
Benoetigt: Pillow, numpy
"""
import glob
import os
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tiere', 'original')
DST = os.path.join(ROOT, 'tiere')
TOL = 26


def cut_out(path):
    im = Image.open(path).convert('RGBA')
    im.thumbnail((700, 700), Image.LANCZOS)
    a = np.asarray(im).astype(np.int16)
    h, w = a.shape[:2]
    rgb = a[:, :, :3]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, axis=0)
    near = np.sqrt(((rgb - bg) ** 2).sum(axis=2)) < TOL
    # Flutfuellung vom Rand aus, nur durch hintergrundaehnliche Pixel
    mask = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if near[y, x] and not mask[y, x]:
                mask[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if near[y, x] and not mask[y, x]:
                mask[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not mask[ny, nx]:
                mask[ny, nx] = True
                q.append((ny, nx))
    alpha = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    out = im.copy()
    out.putalpha(alpha)
    box = alpha.point(lambda v: 255 if v > 20 else 0).getbbox()
    return out.crop(box)


def main():
    for path in sorted(glob.glob(os.path.join(SRC, '*.png')) + glob.glob(os.path.join(SRC, '*.jp*g'))):
        name = os.path.splitext(os.path.basename(path))[0]
        img = cut_out(path)
        img.save(os.path.join(DST, name + '.png'))
        print(name, img.size)


if __name__ == '__main__':
    main()
