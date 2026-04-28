"""运行一次即可填充演示数据：python seed.py"""
from database import SessionLocal, engine, Base
import models

Base.metadata.create_all(bind=engine)

SPUS = [
    {
        "name": "复古法式流苏耳环",
        "category": "earring",
        "sub_category": "耳坠",
        "brand": "LUMIÈRE",
        "description": "925银镀金工艺，流苏设计随动感轻盈，法式浪漫气息，适合约会聚会。",
        "style_tags": ["复古", "法式", "浪漫"],
        "occasion_tags": ["约会", "聚会", "婚礼"],
        "material": "925银镀18K金",
        "target_face_shapes": ["oval", "heart"],
        "mount_type": "ear_lobe",
        "cover_url": "https://picsum.photos/seed/spu1/400/400",
        "detail_images": ["https://picsum.photos/seed/spu1d1/800/800"],
        "skus": [
            {"sku_name": "银色-短款3cm", "color": "银色", "size": "3cm",
             "price": 89, "original_price": 119, "stock": 50},
            {"sku_name": "金色-长款6cm", "color": "金色", "size": "6cm",
             "price": 129, "original_price": 169, "stock": 38},
        ],
    },
    {
        "name": "简约几何耳钉",
        "category": "earring",
        "sub_category": "耳钉",
        "brand": "MINIMO",
        "description": "几何菱形切割，冷酷极简风格，通勤搭配神器，日常百搭不出错。",
        "style_tags": ["简约", "几何", "通勤"],
        "occasion_tags": ["日常", "商务", "通勤"],
        "material": "钛钢镀玫瑰金",
        "target_face_shapes": ["square", "oval", "oblong"],
        "mount_type": "ear_top",
        "cover_url": "https://picsum.photos/seed/spu2/400/400",
        "detail_images": ["https://picsum.photos/seed/spu2d1/800/800"],
        "skus": [
            {"sku_name": "银色", "color": "银色", "size": "1.2cm",
             "price": 59, "original_price": 79, "stock": 100},
            {"sku_name": "玫瑰金", "color": "玫瑰金", "size": "1.2cm",
             "price": 69, "original_price": 89, "stock": 80},
        ],
    },
    {
        "name": "南洋珍珠项链",
        "category": "necklace",
        "sub_category": "珍珠项链",
        "brand": "PEARLUX",
        "description": "天然淡水珍珠，温润光泽，18K金珠扣，优雅百搭，适合多种脸型。",
        "style_tags": ["轻奢", "优雅", "珍珠"],
        "occasion_tags": ["婚礼", "宴会", "日常"],
        "material": "天然珍珠+18K金",
        "target_face_shapes": ["oval", "round", "square", "heart", "oblong", "diamond"],
        "mount_type": "neck",
        "cover_url": "https://picsum.photos/seed/spu3/400/400",
        "detail_images": ["https://picsum.photos/seed/spu3d1/800/800"],
        "skus": [
            {"sku_name": "40cm短款", "color": "白色", "size": "40cm",
             "price": 299, "original_price": 399, "stock": 30},
            {"sku_name": "45cm标准款", "color": "白色", "size": "45cm",
             "price": 349, "original_price": 459, "stock": 25},
        ],
    },
    {
        "name": "波西米亚头箍发饰",
        "category": "hairpin",
        "sub_category": "发箍",
        "brand": "BOHO",
        "description": "民族风编织图案，弹性发箍，轻松固定发型，节日感满满。",
        "style_tags": ["波西米亚", "民族风", "节日"],
        "occasion_tags": ["聚会", "节日", "度假"],
        "material": "布艺编织+弹力材料",
        "target_face_shapes": ["round", "oval", "heart"],
        "mount_type": "hair",
        "cover_url": "https://picsum.photos/seed/spu4/400/400",
        "detail_images": ["https://picsum.photos/seed/spu4d1/800/800"],
        "skus": [
            {"sku_name": "橙色图腾款", "color": "橙色", "size": "均码",
             "price": 45, "original_price": 65, "stock": 60},
            {"sku_name": "蓝色图腾款", "color": "蓝色", "size": "均码",
             "price": 45, "original_price": 65, "stock": 55},
        ],
    },
    {
        "name": "轻奢锆石手链",
        "category": "bracelet",
        "sub_category": "手链",
        "brand": "GLIMMER",
        "description": "仿锆石镶嵌，银色链条，精致闪耀，与任何穿搭完美融合。",
        "style_tags": ["轻奢", "闪耀", "百搭"],
        "occasion_tags": ["日常", "聚会", "约会"],
        "material": "925银+锆石",
        "target_face_shapes": ["oval", "round", "square", "heart", "oblong", "diamond"],
        "mount_type": "wrist",
        "cover_url": "https://picsum.photos/seed/spu5/400/400",
        "detail_images": ["https://picsum.photos/seed/spu5d1/800/800"],
        "skus": [
            {"sku_name": "银色-16cm", "color": "银色", "size": "16cm",
             "price": 168, "original_price": 228, "stock": 45},
            {"sku_name": "银色-18cm", "color": "银色", "size": "18cm",
             "price": 168, "original_price": 228, "stock": 40},
        ],
    },
    {
        "name": "18K金水滴耳坠",
        "category": "earring",
        "sub_category": "耳坠",
        "brand": "LUMIÈRE",
        "description": "18K真金工艺，水滴造型优雅垂坠，拉长颈部线条，修饰脸型效果极佳。",
        "style_tags": ["高级感", "轻奢", "修颜"],
        "occasion_tags": ["婚礼", "宴会", "约会"],
        "material": "18K金",
        "target_face_shapes": ["oval", "oblong", "round"],
        "mount_type": "ear_lobe",
        "cover_url": "https://picsum.photos/seed/spu6/400/400",
        "detail_images": ["https://picsum.photos/seed/spu6d1/800/800"],
        "skus": [
            {"sku_name": "黄金色-4cm", "color": "黄金", "size": "4cm",
             "price": 389, "original_price": 499, "stock": 20},
            {"sku_name": "玫瑰金-4cm", "color": "玫瑰金", "size": "4cm",
             "price": 399, "original_price": 499, "stock": 18},
        ],
    },
]


def seed():
    db = SessionLocal()
    try:
        if db.query(models.GoodsSpu).count() > 0:
            print("数据已存在，跳过 seed。")
            return

        for spu_data in SPUS:
            spu_data = dict(spu_data)
            skus_data = spu_data.pop("skus")
            spu = models.GoodsSpu(**spu_data)
            db.add(spu)
            db.flush()

            for sk in skus_data:
                db.add(models.GoodsSku(spu_id=spu.id, **sk))

        db.commit()
        print(f"[OK] 已插入 {len(SPUS)} 件商品及其 SKU。")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
