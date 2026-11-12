#!/usr/bin/env python3
"""Extract the two Kurumi gun sprites from the reference photo."""
from pathlib import Path
import sys
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "d7232u4-3a6527c6-e26e-4407-b675-a3d6a3d51370.jpg"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "Modding/KurumiWeapons/Textures/Items"

def polygon_mask(width, height, polygon, core_polygon):
    mask = np.zeros((height, width), dtype=np.uint8)
    pts = np.array(polygon, dtype=np.int32)
    cv2.fillPoly(mask, [pts], cv2.GC_PR_FGD)
    core = np.array(core_polygon, dtype=np.int32)
    cv2.fillPoly(mask, [core], cv2.GC_FGD)
    return mask

def extract(box, polygon, core_polygon, filename, target_width):
    image = cv2.imread(str(SOURCE), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Could not read source image: {SOURCE}")
    x0, y0, x1, y1 = box
    crop = image[y0:y1, x0:x1].copy()
    h, w = crop.shape[:2]
    mask = polygon_mask(w, h, polygon, core_polygon)
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(crop, mask, None, bgd, fgd, 7, cv2.GC_INIT_WITH_MASK)

    alpha = np.where(
        (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
    ).astype(np.uint8)

    # Remove small detached background speckles while preserving separate metal details.
    count, labels, stats, _ = cv2.connectedComponentsWithStats((alpha > 0).astype(np.uint8), 8)
    if count > 1:
        areas = stats[1:, cv2.CC_STAT_AREA]
        largest = int(areas.max())
        keep = np.zeros_like(alpha)
        for label in range(1, count):
            if stats[label, cv2.CC_STAT_AREA] >= max(18, int(largest * 0.003)):
                keep[labels == label] = 255
        alpha = keep

    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    alpha = cv2.GaussianBlur(alpha, (3, 3), 0)

    ys, xs = np.where(alpha > 12)
    if len(xs) < 100:
        raise RuntimeError(f"Foreground segmentation failed for {filename}")

    pad = 6
    bx0 = max(0, int(xs.min()) - pad)
    by0 = max(0, int(ys.min()) - pad)
    bx1 = min(w, int(xs.max()) + pad + 1)
    by1 = min(h, int(ys.max()) + pad + 1)
    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA)
    rgba = np.dstack((rgb[:, :, :3], alpha))[by0:by1, bx0:bx1]
    sprite = Image.fromarray(rgba)

    # Preserve aspect ratio, fit to a 64 px item-cell height and use transparent padding.
    target_height = 64
    scale = min(target_width / sprite.width, target_height / sprite.height)
    new_size = (max(1, int(round(sprite.width * scale))), max(1, int(round(sprite.height * scale))))
    sprite = sprite.resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 0))
    canvas.alpha_composite(sprite, ((target_width - new_size[0]) // 2, (target_height - new_size[1]) // 2))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / filename
    canvas.save(path, optimize=True)
    print(f"Created {path} ({canvas.width}x{canvas.height}, foreground pixels={int((np.array(canvas)[:,:,3]>12).sum())})")

# The hand-drawn foreground polygons seed GrabCut, with sure-foreground cores
# on the wood/metal body. Coordinates are relative to each crop.
extract(
    (28, 130, 990, 286),
    [(14,78),(207,53),(251,34),(281,32),(791,30),(939,28),(939,48),(794,54),(620,64),(484,72),(367,80),(287,96),(263,126),(232,137),(17,142)],
    [(28,82),(208,59),(261,40),(307,40),(786,36),(920,35),(918,42),(790,48),(610,57),(484,65),(366,73),(284,91),(255,119),(55,135)],
    "kurumi_long_rifle.png",
    320
)
extract(
    (230, 215, 610, 375),
    [(17,137),(25,111),(63,90),(84,64),(113,35),(135,23),(156,21),(200,35),(262,41),(348,43),(350,61),(281,64),(222,77),(193,103),(169,129),(146,147),(42,146)],
    [(27,128),(37,107),(77,87),(101,61),(125,34),(143,30),(158,29),(206,40),(266,46),(340,47),(336,54),(275,57),(215,71),(188,99),(163,127),(143,140),(45,138)],
    "kurumi_pistol.png",
    192
)
