"""
Generate AR jewelry PNG assets (transparent background) for virtual try-on.
Run: python backend/generate_ar_assets.py
"""
from PIL import Image, ImageDraw
import math, json, os

OUT = os.path.join(os.path.dirname(__file__), "uploads", "ar")
os.makedirs(OUT, exist_ok=True)

T        = (0, 0, 0, 0)
GOLD     = (212, 175, 55, 255)
GOLD_L   = (245, 215, 110, 255)
GOLD_D   = (150, 110, 20, 255)
PEARL    = (248, 243, 233, 255)
PEARL_SH = (195, 188, 175, 200)
CRYSTAL  = (130, 195, 235, 220)
CRYSTAL_H= (210, 240, 255, 180)
ROSE     = (183, 110, 121, 255)
ROSE_L   = (225, 165, 175, 255)
ROSE_D   = (140, 75, 85, 255)
EMERALD  = (25, 140, 75, 240)
EMERALD_H= (80, 200, 130, 180)
RUBY     = (185, 30, 55, 240)
RUBY_H   = (230, 100, 120, 200)


def cv(w, h):
    return Image.new("RGBA", (w, h), T)


def hook(d, cx, y0, color=GOLD):
    r = 10
    d.arc([cx - r, y0, cx + r, y0 + r * 2], 180, 360, fill=color, width=3)
    d.line([cx + r, y0 + r, cx + r, y0 + r + 10], fill=color, width=3)


def wire(d, x, y1, y2, color=GOLD):
    d.line([x, y1, x, y2], fill=color, width=2)


# ── 1. Pearl drop earring ──────────────────────────────────────────────────────
def make_pearl_drop():
    W, H = 160, 320
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx = W // 2
    hook(d, cx, 4)
    wire(d, cx, 30, 110)
    d.ellipse([cx - 6, 106, cx + 6, 118], fill=GOLD_L, outline=GOLD_D, width=1)
    pr, pcx, pcy = 58, cx, 185
    d.ellipse([pcx - pr + 5, pcy - pr + 7, pcx + pr + 5, pcy + pr + 7], fill=(160, 155, 145, 55))
    d.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=PEARL, outline=PEARL_SH, width=2)
    d.ellipse([pcx - 18, pcy - 28, pcx + 8, pcy - 8], fill=(255, 255, 255, 200))
    d.ellipse([pcx + 12, pcy + 12, pcx + 30, pcy + 30], fill=PEARL_SH)
    return img


# ── 2. Gold hoop earring ───────────────────────────────────────────────────────
def make_gold_hoop():
    W, H = 200, 215
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2 + 8
    d.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], outline=GOLD_D, width=28)
    d.ellipse([cx - 88, cy - 88, cx + 88, cy + 88], outline=GOLD,   width=22)
    d.arc([cx - 80, cy - 80, cx + 80, cy + 80], 210, 330, fill=GOLD_L, width=8)
    d.arc([cx - 80, cy - 80, cx + 80, cy + 80], 215, 280, fill=(255, 245, 170, 180), width=4)
    d.line([cx, cy - 88, cx, 4], fill=GOLD_D, width=4)
    d.ellipse([cx - 5, 2, cx + 5, 12], fill=GOLD_L)
    return img


# ── 3. Crystal teardrop earring ────────────────────────────────────────────────
def make_crystal_drop():
    W, H = 140, 300
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx = W // 2
    hook(d, cx, 4)
    wire(d, cx, 30, 88)
    d.ellipse([cx - 8, 84, cx + 8, 100], fill=GOLD, outline=GOLD_D, width=1)
    ty, bcy, br = 100, 235, 52
    pts = []
    for i in range(20):
        t = i / 19
        x = cx - 4 * (1 - t) - br * t + br * math.sin(math.pi * t) * 0.25
        y = ty + (bcy - ty) * t
        pts.append((x, y))
    for i in range(21):
        angle = math.pi + math.pi * i / 20
        pts.append((cx + br * math.cos(angle), bcy + br * math.sin(angle)))
    for i in range(19, -1, -1):
        t = i / 19
        x = cx + 4 * (1 - t) + br * t - br * math.sin(math.pi * t) * 0.25
        y = ty + (bcy - ty) * t
        pts.append((x, y))
    d.polygon(pts, fill=CRYSTAL, outline=(*CRYSTAL[:3], 255))
    d.ellipse([cx - 14, ty + 18, cx + 4, ty + 55], fill=CRYSTAL_H)
    d.line([cx, ty + 8, cx - 22, bcy - 18], fill=(180, 220, 250, 100), width=1)
    d.line([cx, ty + 8, cx + 22, bcy - 18], fill=(180, 220, 250, 100), width=1)
    return img


# ── 4. Rose gold stud ──────────────────────────────────────────────────────────
def make_rose_stud():
    W, H = 120, 120
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx, cy, r = W // 2, H // 2, 45
    d.ellipse([cx - r + 4, cy - r + 4, cx + r + 4, cy + r + 4], fill=(100, 50, 60, 55))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=ROSE, outline=ROSE_D, width=2)
    d.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8], fill=ROSE_L, outline=ROSE, width=1)
    d.ellipse([cx - 15, cy - 22, cx + 8, cy - 6], fill=(255, 220, 225, 200))
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=ROSE_D)
    return img


# ── 5. Emerald drop earring ────────────────────────────────────────────────────
def make_emerald_drop():
    W, H = 140, 280
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx = W // 2
    hook(d, cx, 4)
    wire(d, cx, 30, 84)
    d.rectangle([cx - 12, 80, cx + 12, 100], fill=GOLD, outline=GOLD_D, width=1)
    ex1, ey1, ex2, ey2, r = cx - 28, 100, cx + 28, 220, 10
    d.rectangle([ex1 + r, ey1, ex2 - r, ey2], fill=EMERALD)
    d.rectangle([ex1, ey1 + r, ex2, ey2 - r], fill=EMERALD)
    for bx, by in [(ex1, ey1), (ex2 - r*2, ey1), (ex1, ey2 - r*2), (ex2 - r*2, ey2 - r*2)]:
        d.ellipse([bx, by, bx + r*2, by + r*2], fill=EMERALD)
    d.rectangle([ex1 + 8, ey1 + 8, ex1 + 20, ey2 - 8], fill=EMERALD_H)
    d.line([cx - 10, ey1 + 15, cx + 10, ey1 + 15], fill=EMERALD_H, width=1)
    d.line([cx - 10, ey1 + 35, cx + 10, ey1 + 35], fill=EMERALD_H, width=1)
    return img


# ── 6. Ruby drop earring ───────────────────────────────────────────────────────
def make_ruby_drop():
    W, H = 130, 290
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx = W // 2
    hook(d, cx, 4)
    wire(d, cx, 30, 80)
    d.ellipse([cx - 10, 76, cx + 10, 96], fill=GOLD, outline=GOLD_D, width=1)
    pts = []
    ty, bcy, br = 96, 230, 48
    for i in range(20):
        t = i / 19
        x = cx - 4 * (1 - t) - br * t + br * math.sin(math.pi * t) * 0.2
        pts.append((x, ty + (bcy - ty) * t))
    for i in range(21):
        angle = math.pi + math.pi * i / 20
        pts.append((cx + br * math.cos(angle), bcy + br * math.sin(angle)))
    for i in range(19, -1, -1):
        t = i / 19
        x = cx + 4 * (1 - t) + br * t - br * math.sin(math.pi * t) * 0.2
        pts.append((x, ty + (bcy - ty) * t))
    d.polygon(pts, fill=RUBY, outline=(*RUBY[:3], 255))
    d.ellipse([cx - 12, ty + 15, cx + 4, ty + 45], fill=RUBY_H)
    d.line([cx, ty + 6, cx - 20, bcy - 15], fill=(240, 150, 160, 100), width=1)
    d.line([cx, ty + 6, cx + 20, bcy - 15], fill=(240, 150, 160, 100), width=1)
    return img


# ── 7. Gold star pendant necklace ──────────────────────────────────────────────
def make_neck_star():
    W, H = 320, 180
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cx = W // 2
    # Chain (dots)
    for x in range(30, W - 30, 10):
        d.ellipse([x - 3, 18, x + 3, 24], fill=GOLD_D)
        d.ellipse([x - 2, 19, x + 2, 23], fill=GOLD_L)
    # Pendant drop wire
    d.line([cx, 24, cx, 55], fill=GOLD_D, width=3)
    # Star
    star_cx, star_cy, star_r, star_ir = cx, 110, 50, 22
    pts = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = star_r if i % 2 == 0 else star_ir
        pts.append((star_cx + r * math.cos(angle), star_cy - r * math.sin(angle)))
    d.polygon(pts, fill=GOLD, outline=GOLD_D)
    d.polygon(pts, outline=GOLD_L, width=2)
    # Center gem
    d.ellipse([star_cx - 10, star_cy - 10, star_cx + 10, star_cy + 10], fill=CRYSTAL, outline=GOLD_D, width=1)
    d.ellipse([star_cx - 5, star_cy - 6, star_cx + 2, star_cy - 1], fill=CRYSTAL_H)
    return img


# ── 8. Gold hair pin ───────────────────────────────────────────────────────────
def make_hair_pin():
    W, H = 320, 90
    img = cv(W, H)
    d = ImageDraw.Draw(img)
    cy = H // 2
    # Pin body
    d.rectangle([60, cy - 4, W - 20, cy + 4], fill=GOLD_D)
    d.rectangle([60, cy - 3, W - 20, cy + 3], fill=GOLD)
    d.line([60, cy, W - 20, cy], fill=GOLD_L, width=1)
    # Pointed tip
    d.polygon([(W - 20, cy - 4), (W - 20, cy + 4), (W - 5, cy)], fill=GOLD_D)
    # Flower decoration at left end
    fcx, fcy, fr = 38, cy, 28
    petals = 6
    for i in range(petals):
        angle = i * math.pi * 2 / petals
        px = fcx + fr * 0.6 * math.cos(angle)
        py = fcy + fr * 0.6 * math.sin(angle)
        d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=ROSE, outline=ROSE_D, width=1)
    d.ellipse([fcx - 12, fcy - 12, fcx + 12, fcy + 12], fill=GOLD, outline=GOLD_D, width=1)
    d.ellipse([fcx - 5, fcy - 6, fcx + 3, fcy + 1], fill=GOLD_L)
    return img


# ── Generate all & build manifest ─────────────────────────────────────────────
items = [
    ("ear_pearl_drop.png",   make_pearl_drop,   "ear_lobe", "珍珠垂坠耳环",   0,   0, 1.0,  0),
    ("ear_gold_hoop.png",    make_gold_hoop,    "ear_lobe", "金色圆圈耳环",  -8,  -8, 1.3,  0),
    ("ear_crystal_drop.png", make_crystal_drop, "ear_lobe", "水晶泪滴耳环",   0,   0, 1.0,  0),
    ("ear_rose_stud.png",    make_rose_stud,    "ear_lobe", "玫瑰金耳钉",     0,  -5, 0.75, 0),
    ("ear_emerald_drop.png", make_emerald_drop, "ear_lobe", "祖母绿垂坠耳环", 0,   0, 1.0,  0),
    ("ear_ruby_drop.png",    make_ruby_drop,    "ear_lobe", "红宝石垂坠耳环", 0,   0, 1.0,  0),
    ("neck_gold_star.png",   make_neck_star,    "neck",     "金色星形项链",   0,   0, 1.0,  0),
    ("hair_gold_pin.png",    make_hair_pin,     "hair",     "金色花朵发簪",   0,   0, 1.0,  0),
]

manifest = []
for fname, fn, mount, name, ox, oy, scale, rot in items:
    img = fn()
    path = os.path.join(OUT, fname)
    img.save(path, "PNG")
    manifest.append({
        "filename":          fname,
        "ar_asset_url":      f"/uploads/ar/{fname}",
        "name":              name,
        "mount_type":        mount,
        "ar_offset_x":       ox,
        "ar_offset_y":       oy,
        "ar_scale_base":     scale,
        "ar_rotation_offset": rot,
        "image_size":        list(img.size),
    })
    print(f"[OK] {fname}  ({img.size[0]}x{img.size[1]})")

manifest_path = os.path.join(OUT, "manifest.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"\n[manifest] {manifest_path}")
print(f"[done] {len(manifest)} assets generated → {OUT}")
