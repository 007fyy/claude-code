from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models  # noqa: F401 – registers ORM models before table creation

from routers import goods, cart, order

app = FastAPI(title="饰品 VTryOn API", version="1.0.0", docs_url="/docs")

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


app.include_router(goods.router, prefix="/api/v1/goods", tags=["goods"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(order.router, prefix="/api/v1/order", tags=["order"])


@app.get("/")
def root():
    return {"message": "饰品 VTryOn API 正常运行", "docs": "/docs"}
