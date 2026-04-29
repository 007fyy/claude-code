from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models.user import User
import models
import schemas

router = APIRouter()


@router.post("/add", response_model=schemas.Resp)
def add_to_cart(
    body: schemas.AddCartReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sku = db.query(models.GoodsSku).filter(
        models.GoodsSku.id == body.sku_id,
        models.GoodsSku.status == 1,
    ).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU 不存在")
    if sku.stock < body.quantity:
        raise HTTPException(status_code=400, detail="库存不足")

    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
        models.CartItem.sku_id == body.sku_id,
    ).first()

    if existing:
        existing.quantity += body.quantity
    else:
        db.add(models.CartItem(
            user_id=current_user.id,
            sku_id=body.sku_id,
            quantity=body.quantity,
        ))

    db.commit()
    return schemas.Resp(message="已加入购物车")


@router.get("/list", response_model=schemas.CartListResp)
def cart_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(models.CartItem)
        .filter(models.CartItem.user_id == current_user.id)
        .all()
    )

    result = []
    total_selected = 0.0
    selected_count = 0

    for item in items:
        sku = item.sku
        spu = sku.spu
        price = float(sku.price)
        subtotal = price * item.quantity

        result.append(schemas.CartItemOut(
            cart_item_id=item.id,
            sku_id=sku.id,
            spu_id=spu.id,
            sku_name=sku.sku_name,
            spu_name=spu.name,
            cover_url=spu.cover_url or "",
            price=price,
            quantity=item.quantity,
            selected=item.selected,
            subtotal=subtotal,
            ar_asset_url=sku.ar_asset_url,
            mount_type=spu.mount_type,
        ))

        if item.selected:
            total_selected += subtotal
            selected_count += 1

    return schemas.CartListResp(
        items=result,
        total_selected=total_selected,
        selected_count=selected_count,
    )


@router.put("/update", response_model=schemas.Resp)
def update_cart(
    body: schemas.UpdateCartReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == body.cart_item_id,
        models.CartItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")

    if body.quantity is not None:
        if body.quantity <= 0:
            db.delete(item)
        else:
            item.quantity = body.quantity
    if body.selected is not None:
        item.selected = body.selected

    db.commit()
    return schemas.Resp()


@router.delete("/remove/{cart_item_id}", response_model=schemas.Resp)
def remove_cart(
    cart_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")

    db.delete(item)
    db.commit()
    return schemas.Resp(message="已删除")
