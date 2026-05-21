from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from database import engine, Base
import models  # noqa: F401 – registers ORM models before table creation
from config import BizError

from routers import goods, cart, order, auth as auth_router, user as user_router, favorite, tracking, browse_history, avatar

app = FastAPI(title="珑饰 API", version="1.0.0", docs_url="/docs")


@app.exception_handler(BizError)
async def biz_error_handler(request, exc: BizError):
    return JSONResponse({"code": exc.code, "message": exc.message, "data": None})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import text
    with engine.connect() as conn:
        for ddl in [
            "ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN face_type VARCHAR(20) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN skin_tone VARCHAR(20) DEFAULT NULL",
        ]:
            try:
                conn.execute(text(ddl))
                conn.commit()
            except Exception:
                pass


app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(user_router.router, prefix="/api/v1")
app.include_router(goods.router, prefix="/api/v1/goods", tags=["goods"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(order.router, prefix="/api/v1/order", tags=["order"])
app.include_router(favorite.router, prefix="/api/v1/favorite", tags=["favorite"])
app.include_router(tracking.router, prefix="/api/v1/tracking", tags=["tracking"])
app.include_router(browse_history.router, prefix="/api/v1/history", tags=["history"])
app.include_router(avatar.router, prefix="/api/v1", tags=["avatar"])

import os
_uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")


@app.get("/")
def root():
    return {"message": "饰品 VTryOn API 正常运行", "docs": "/docs"}
