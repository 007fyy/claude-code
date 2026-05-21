"""
Generate 5 jewelry products: cover images + seed into database.
Run: python backend/seed_products.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw
import math

COVER_DIR = os.path.join(os.path.dirname(__file__), "uploads", "covers")
os.makedirs(COVER_DIR, exist_ok=True)

GOLD=(212,175,55,255); GOLD_L=(245,215,110,255); GOLD_D=(150,110,20,255)
PEARL=(248,243,233,255); PEARL_SH=(195,188,175,200)
CRYSTAL=(130,195,235,220); CRYSTAL_H=(210,240,255,180)
ROSE=(183,110,121,255); ROSE_L=(225,165,175,255); ROSE_D=(140,75,85,255)

def grad(w, h, c1, c2):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for i in range(h):
        t = i/(h-1)
        d.line([(0,i),(w,i)], fill=tuple(int(c1[k]*(1-t)+c2[k]*t) for k in range(3)))
    return img

def shadow(d, cx, cy, r):
    for i in range(6):
        d.ellipse([cx-r-i*2,cy-r//3-i,cx+r+i*2,cy+r//3+i], fill=(0,0,0,max(0,35-i*6)))

def make_pearl():
    img = grad(400,400,(248,244,238),(232,222,208)); d=ImageDraw.Draw(img,"RGBA")
    for cx in [140,260]:
        shadow(d,cx,295,50)
        d.arc([cx-14,40,cx+14,68],180,360,fill=GOLD_D,width=4)
        d.line([cx+14,54,cx+14,62],fill=GOLD_D,width=4)
        d.line([cx,65,cx,145],fill=GOLD,width=3)
        d.ellipse([cx-8,141,cx+8,157],fill=GOLD_L,outline=GOLD_D,width=1)
        pr=72; pcy=235
        d.ellipse([cx-pr+6,pcy-pr+8,cx+pr+6,pcy+pr+8],fill=(180,170,160,50))
        d.ellipse([cx-pr,pcy-pr,cx+pr,pcy+pr],fill=PEARL,outline=PEARL_SH,width=2)
        d.ellipse([cx-22,pcy-35,cx+10,pcy-10],fill=(255,255,255,200))
        d.ellipse([cx+15,pcy+15,cx+38,pcy+38],fill=PEARL_SH)
    return img.convert("RGB")

def make_hoop():
    img = grad(400,400,(26,23,20),(45,28,16)); d=ImageDraw.Draw(img,"RGBA")
    for cx in [130,270]:
        cy=200
        d.ellipse([cx-88,cy-88,cx+88,cy+88],outline=GOLD_D,width=28)
        d.ellipse([cx-88,cy-88,cx+88,cy+88],outline=GOLD,width=22)
        d.arc([cx-80,cy-80,cx+80,cy+80],210,330,fill=GOLD_L,width=8)
        d.arc([cx-80,cy-80,cx+80,cy+80],215,280,fill=(255,245,170,180),width=4)
    return img.convert("RGB")

def make_crystal():
    img = grad(400,400,(238,248,252),(210,235,245)); d=ImageDraw.Draw(img,"RGBA")
    for cx in [140,260]:
        shadow(d,cx,315,42)
        d.arc([cx-12,30,cx+12,54],180,360,fill=GOLD_D,width=3)
        d.line([cx+12,42,cx+12,50],fill=GOLD_D,width=3)
        d.line([cx,53,cx,112],fill=GOLD,width=2)
        d.ellipse([cx-10,108,cx+10,124],fill=GOLD,outline=GOLD_D,width=1)
        ty,bcy,br=124,272,64
        pts=[]
        for i in range(20):

            
            t=i/19; x=cx-5*(1-t)-br*t+br*math.sin(math.pi*t)*0.25
            pts.append((x,ty+(bcy-ty)*t))
        for i in range(21):
            a=math.pi+math.pi*i/20; pts.append((cx+br*math.cos(a),bcy+br*math.sin(a)))
        for i in range(19,-1,-1):
            t=i/19; x=cx+5*(1-t)+br*t-br*math.sin(math.pi*t)*0.25
            pts.append((x,ty+(bcy-ty)*t))
        d.polygon(pts,fill=CRYSTAL,outline=(*CRYSTAL[:3],255))
        d.ellipse([cx-18,ty+22,cx+5,ty+68],fill=CRYSTAL_H)
        for sx,sy in [(cx-52,ty-18),(cx+56,ty+28),(cx-44,bcy+62)]:
            d.line([sx-7,sy,sx+7,sy],fill=(255,255,255,160),width=1)
            d.line([sx,sy-7,sx,sy+7],fill=(255,255,255,160),width=1)
    return img.convert("RGB")

def make_necklace():
    img = grad(400,400,(250,249,247),(240,235,228)); d=ImageDraw.Draw(img,"RGBA")
    cx,cr=200,145
    for deg in range(-62,63,8):
        a=math.radians(deg); x=cx+cr*math.sin(a); y=155-cr*math.cos(a)+cr
        d.ellipse([x-4,y-3,x+4,y+3],fill=GOLD_D); d.ellipse([x-3,y-2,x+3,y+2],fill=GOLD_L)
    dy=155-cr+cr; d.line([cx,dy,cx,dy+42],fill=GOLD_D,width=3)
    scx,scy=cx,dy+42+58; sr,sir=56,24
    pts=[]
    for i in range(10):
        a=math.pi/2+i*math.pi/5; r=sr if i%2==0 else sir
        pts.append((scx+r*math.cos(a),scy-r*math.sin(a)))
    shadow(d,scx,scy+12,52)
    d.polygon(pts,fill=GOLD,outline=GOLD_D); d.polygon(pts,outline=GOLD_L,width=2)
    d.ellipse([scx-12,scy-12,scx+12,scy+12],fill=CRYSTAL,outline=GOLD_D,width=1)
    d.ellipse([scx-6,scy-7,scx+2,scy-1],fill=CRYSTAL_H)
    return img.convert("RGB")

def make_stud():
    img = grad(400,400,(253,242,244),(245,228,232)); d=ImageDraw.Draw(img,"RGBA")
    for cx in [140,260]:
        cy=200; r=72
        shadow(d,cx+5,cy+8,r)
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=ROSE,outline=ROSE_D,width=3)
        d.ellipse([cx-r+12,cy-r+12,cx+r-12,cy+r-12],fill=ROSE_L,outline=ROSE,width=2)
        d.ellipse([cx-22,cy-30,cx+10,cy-8],fill=(255,230,235,200))
        d.ellipse([cx-10,cy-10,cx+10,cy+10],fill=ROSE_D)
        d.ellipse([cx-5,cy-6,cx+2,cy],fill=(220,160,170,200))
    return img.convert("RGB")

covers = [
    ("cover_pearl.jpg",    make_pearl),
    ("cover_hoop.jpg",     make_hoop),
    ("cover_crystal.jpg",  make_crystal),
    ("cover_necklace.jpg", make_necklace),
    ("cover_stud.jpg",     make_stud),
]
for fname, fn in covers:
    p = os.path.join(COVER_DIR, fname)
    fn().save(p, "JPEG", quality=92)
    print(f"[cover] {fname}")

# ── Seed database ──────────────────────────────────────────────────────────────
from database import SessionLocal
from models.goods import GoodsSpu, GoodsSku

PRODUCTS = [
  { "name":"月光珍珠耳环 · 优雅弧线款","category":"earring","material":"925银 / 天然淡水珍珠",
    "description":"精选天然淡水珍珠，925银镀白金工艺，弧线造型修饰脸型，日常佩戴不易过敏。珍珠直径8-10mm，光泽饱满，每颗独一无二。",
    "style_tags":["优雅复古","轻奢高级"],"occasion_tags":["约会出行","职场正式"],
    "target_face_shapes":["鹅蛋脸","圆脸"],"mount_type":"ear_lobe","sort_weight":100,
    "cover_url":"/uploads/covers/cover_pearl.jpg","ar_asset":"/uploads/ar/ear_pearl_drop.png",
    "ar_scale_base":1.0,"ar_offset_x":0,"ar_offset_y":0,
    "skus":[
      {"sku_name":"银色 · 8mm珍珠","price":168,"original_price":228,"stock":56},
      {"sku_name":"金色 · 8mm珍珠","price":188,"original_price":258,"stock":32},
      {"sku_name":"银色 · 10mm珍珠","price":198,"original_price":278,"stock":24},
    ]},
  { "name":"金色圆圈耳环 · 极简百搭款","category":"earring","material":"18K镀金 / 钛钢",
    "description":"经典圆圈设计，18K镀金工艺，钛钢基底防过敏，简约百搭，从日常通勤到派对聚会都适合。",
    "style_tags":["简约极简","日常通勤"],"occasion_tags":["日常通勤","约会出行"],
    "target_face_shapes":["鹅蛋脸","方脸","心形脸"],"mount_type":"ear_lobe","sort_weight":99,
    "cover_url":"/uploads/covers/cover_hoop.jpg","ar_asset":"/uploads/ar/ear_gold_hoop.png",
    "ar_scale_base":1.3,"ar_offset_x":-8,"ar_offset_y":-8,
    "skus":[
      {"sku_name":"金色 · 小号(3cm)","price":128,"original_price":168,"stock":75},
      {"sku_name":"金色 · 大号(5cm)","price":148,"original_price":198,"stock":45},
      {"sku_name":"玫瑰金 · 小号","price":138,"original_price":178,"stock":60},
    ]},
  { "name":"水晶泪滴耳环 · 闪耀派对款","category":"earring","material":"925银 / 施华洛世奇水晶",
    "description":"施华洛世奇水晶切面设计，折射迷人光彩，925银耳钩，泪滴造型优雅垂坠，派对约会完美选择。",
    "style_tags":["优雅复古","派对聚会"],"occasion_tags":["派对聚会","约会出行"],
    "target_face_shapes":["鹅蛋脸","方脸"],"mount_type":"ear_lobe","sort_weight":98,
    "cover_url":"/uploads/covers/cover_crystal.jpg","ar_asset":"/uploads/ar/ear_crystal_drop.png",
    "ar_scale_base":1.0,"ar_offset_x":0,"ar_offset_y":0,
    "skus":[
      {"sku_name":"蓝水晶","price":198,"original_price":268,"stock":38},
      {"sku_name":"粉水晶","price":198,"original_price":268,"stock":42},
      {"sku_name":"透明水晶","price":188,"original_price":258,"stock":55},
    ]},
  { "name":"金色星形项链 · 浪漫星空款","category":"necklace","material":"14K包金 / 锆石",
    "description":"五角星吊坠镶嵌锆石，14K包金工艺，搭配精致细链，星光闪耀，送礼自戴皆宜。链长可调节40-45cm。",
    "style_tags":["甜美少女","轻奢高级"],"occasion_tags":["约会出行","日常通勤"],
    "target_face_shapes":[],"mount_type":"neck","sort_weight":97,
    "cover_url":"/uploads/covers/cover_necklace.jpg","ar_asset":"/uploads/ar/neck_gold_star.png",
    "ar_scale_base":1.0,"ar_offset_x":0,"ar_offset_y":0,
    "skus":[
      {"sku_name":"金色 · 40cm","price":288,"original_price":368,"stock":30},
      {"sku_name":"金色 · 45cm","price":298,"original_price":378,"stock":25},
      {"sku_name":"玫瑰金 · 40cm","price":298,"original_price":378,"stock":20},
    ]},
  { "name":"玫瑰金耳钉 · 日常精致款","category":"earring","material":"玫瑰金镀层 / AAA锆石",
    "description":"玫瑰金色调温柔浪漫，AAA级锆石火彩媲美钻石，小巧精致适合日常佩戴，不挑脸型，百搭单品。",
    "style_tags":["简约极简","甜美少女"],"occasion_tags":["日常通勤","职场正式"],
    "target_face_shapes":["鹅蛋脸","圆脸","心形脸","方脸"],"mount_type":"ear_lobe","sort_weight":96,
    "cover_url":"/uploads/covers/cover_stud.jpg","ar_asset":"/uploads/ar/ear_rose_stud.png",
    "ar_scale_base":0.75,"ar_offset_x":0,"ar_offset_y":-5,
    "skus":[
      {"sku_name":"玫瑰金 · 小号","price":88,"original_price":128,"stock":120},
      {"sku_name":"玫瑰金 · 大号","price":108,"original_price":148,"stock":85},
    ]},
]

db = SessionLocal()
try:
    for p in PRODUCTS:
        spu = GoodsSpu(
            name=p["name"], category=p["category"], material=p["material"],
            description=p["description"], style_tags=p["style_tags"],
            occasion_tags=p["occasion_tags"], target_face_shapes=p["target_face_shapes"],
            mount_type=p["mount_type"], cover_url=p["cover_url"],
            sort_weight=p["sort_weight"], status=1,
        )
        db.add(spu); db.flush()
        for s in p["skus"]:
            db.add(GoodsSku(
                spu_id=spu.id, sku_name=s["sku_name"], price=s["price"],
                original_price=s.get("original_price"), stock=s["stock"],
                ar_asset_url=p["ar_asset"], ar_scale_base=p["ar_scale_base"],
                ar_offset_x=p["ar_offset_x"], ar_offset_y=p["ar_offset_y"],
                status=1,
            ))
        db.commit()
        print(f"[DB] {p['name']}  ({len(p['skus'])} SKUs)")
    print("\n[done] 5 products seeded.")
finally:
    db.close()
