from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import engine, Base
import models  # noqa: F401 – registers ORM models before table creation
from config import BizError

from routers import goods, cart, order, auth as auth_router, user as user_router

app = FastAPI(title="珑饰 API", version="1.0.0", docs_url="/docs")


@app.exception_handler(BizError)
async def biz_error_handler(request, exc: BizError):
    return JSONResponse({"code": exc.code, "message": exc.message, "data": None})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(user_router.router, prefix="/api/v1")
app.include_router(goods.router, prefix="/api/v1/goods", tags=["goods"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(order.router, prefix="/api/v1/order", tags=["order"])


@app.get("/")
def root():
    return {"message": "饰品 VTryOn API 正常运行", "docs": "/docs"}
