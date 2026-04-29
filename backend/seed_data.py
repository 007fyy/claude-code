"""
Seed script: populate goods_spu + goods_sku tables from data/goods_seed.json.

Usage:
    cd backend && python seed_data.py          # first run — inserts all
    cd backend && python seed_data.py --force   # drop existing and re-seed

To replace with real data later, just edit data/goods_seed.json and re-run with --force.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from database import engine, Base, SessionLocal
from models.goods import GoodsSpu, GoodsSku
import models  # noqa – register all ORM models so create_all picks them up

Base.metadata.create_all(bind=engine)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "goods_seed.json")

SPU_FIELDS = {
    "name", "category", "sub_category", "brand", "description",
    "style_tags", "occasion_tags", "material", "target_face_shapes",
    "mount_type", "cover_url", "detail_images", "sort_weight",
}

SKU_FIELDS = {
    "sku_name", "color", "size", "price", "original_price",
    "stock", "ar_asset_url",
}


def load_json():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("goods_seed.json must be a JSON array")
    return data


def seed(force=False):
    db = SessionLocal()
    try:
        existing = db.query(GoodsSpu).count()

        if existing > 0 and not force:
            print(f"Already have {existing} SPUs. Use --force to drop and re-seed.")
            return

        if existing > 0 and force:
            db.query(GoodsSku).delete()
            db.query(GoodsSpu).delete()
            db.commit()
            print(f"Cleared {existing} existing SPUs.")

        items = load_json()
        spu_count = 0
        sku_count = 0

        for item in items:
            skus_data = item.pop("skus", [])

            spu_kwargs = {k: v for k, v in item.items() if k in SPU_FIELDS}
            spu_kwargs["status"] = 1
            spu = GoodsSpu(**spu_kwargs)
            db.add(spu)
            db.flush()

            for sku_raw in skus_data:
                sku_kwargs = {k: v for k, v in sku_raw.items() if k in SKU_FIELDS}
                sku_kwargs["status"] = 1
                sku = GoodsSku(spu_id=spu.id, **sku_kwargs)
                db.add(sku)
                sku_count += 1

            spu_count += 1

        db.commit()
        print(f"Seeded {spu_count} SPUs with {sku_count} SKUs from {DATA_FILE}")
    finally:
        db.close()


if __name__ == "__main__":
    force = "--force" in sys.argv
    seed(force=force)
