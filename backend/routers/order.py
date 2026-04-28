import time
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas

router = APIRouter()

DEMO_USER = 1


def _make_order_no() -> str:
    ts = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"ORD{ts}{rand}"


def _make_refund_no() -> str:
    ts = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"RFD{ts}{rand}"


@router.post("/create", response_model=schemas.Resp)
def create_order(body: schemas.CreateOrderReq, db: Session = Depends(get_db)):
    # Fetch cart items
    q = db.query(models.CartItem).filter(
        models.CartItem.user_id == DEMO_USER,
        models.CartItem.selected == 1,
    )
    if body.cart_item_ids:
        q = q.filter(models.CartItem.id.in_(body.cart_item_ids))

    cart_items = q.all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="没有可下单的购物车项")

    # Check stock & calculate total
    order_items_data = []
    total = 0.0

    for ci in cart_items:
        sku = db.query(models.GoodsSku).filter(
            models.GoodsSku.id == ci.sku_id
        ).with_for_update().first()

        if not sku or sku.stock < ci.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"商品「{sku.sku_name if sku else ci.sku_id}」库存不足",
            )

        price = float(sku.price)
        subtotal = price * ci.quantity
        total += subtotal

        # Deduct stock
        sku.stock -= ci.quantity
        sku.frozen_stock += ci.quantity

        order_items_data.append({
            "spu_id": sku.spu_id,
            "sku_id": sku.id,
            "sku_name": sku.sku_name,
            "cover_url": sku.spu.cover_url if sku.spu else "",
            "price": price,
            "quantity": ci.quantity,
            "subtotal": subtotal,
        })

    # Create order
    new_order = models.Order(
        order_no=_make_order_no(),
        user_id=DEMO_USER,
        total_amount=total,
        pay_amount=total,
        status="pending_pay",
        receiver_name=body.receiver_name,
        receiver_phone=body.receiver_phone,
        receiver_address=body.receiver_address,
        remark=body.remark,
    )
    db.add(new_order)
    db.flush()

    for d in order_items_data:
        db.add(models.OrderItem(order_id=new_order.id, **d))

    # Clear bought cart items
    for ci in cart_items:
        db.delete(ci)

    db.commit()
    db.refresh(new_order)

    return schemas.Resp(
        data={"order_id": new_order.id, "order_no": new_order.order_no, "total_amount": total}
    )


@router.post("/pay", response_model=schemas.Resp)
def pay_order(body: schemas.PayOrderReq, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(
        models.Order.id == body.order_id,
        models.Order.user_id == DEMO_USER,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "pending_pay":
        raise HTTPException(status_code=400, detail="订单状态不支持支付")

    order.status = "paid"
    order.pay_time = datetime.now()

    # Release frozen stock
    for oi in order.items:
        sku = db.query(models.GoodsSku).filter(
            models.GoodsSku.id == oi.sku_id
        ).first()
        if sku:
            sku.frozen_stock = max(0, sku.frozen_stock - oi.quantity)

    db.commit()
    return schemas.Resp(data={"order_no": order.order_no, "status": "paid"})


@router.post("/cancel", response_model=schemas.Resp)
def cancel_order(
    order_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == DEMO_USER,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status not in ("pending_pay",):
        raise HTTPException(status_code=400, detail="只有待支付订单可以取消")

    # Return stock
    for oi in order.items:
        sku = db.query(models.GoodsSku).filter(
            models.GoodsSku.id == oi.sku_id
        ).first()
        if sku:
            sku.stock += oi.quantity
            sku.frozen_stock = max(0, sku.frozen_stock - oi.quantity)

    order.status = "cancelled"
    order.cancel_time = datetime.now()
    order.cancel_reason = reason
    db.commit()
    return schemas.Resp(message="订单已取消")


@router.get("/list", response_model=schemas.OrderListResp)
def order_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    q = db.query(models.Order).filter(models.Order.user_id == DEMO_USER)
    total = q.count()
    orders = (
        q.order_by(models.Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = [_order_to_out(o) for o in orders]
    return schemas.OrderListResp(total=total, items=result)


@router.get("/{order_id}", response_model=schemas.Resp)
def order_detail(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == DEMO_USER,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return schemas.Resp(data=_order_to_out(order).model_dump())


# ── Refund ────────────────────────────────────────────────────────────────────

@router.post("/refund/apply", response_model=schemas.Resp)
def apply_refund(body: schemas.ApplyRefundReq, db: Session = Depends(get_db)):
    oi = db.query(models.OrderItem).filter(
        models.OrderItem.id == body.order_item_id
    ).first()
    if not oi:
        raise HTTPException(status_code=404, detail="订单明细不存在")

    order = db.query(models.Order).filter(models.Order.id == oi.order_id).first()
    if not order or order.user_id != DEMO_USER:
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status not in ("paid", "shipped", "received", "completed"):
        raise HTTPException(status_code=400, detail="当前订单状态不支持售后")

    refund = models.RefundOrder(
        refund_no=_make_refund_no(),
        order_id=order.id,
        order_item_id=oi.id,
        user_id=DEMO_USER,
        sku_id=oi.sku_id,
        quantity=oi.quantity,
        refund_amount=float(oi.subtotal),
        reason_type=body.reason_type,
        reason_detail=body.reason_detail,
        status="pending_review",
    )
    db.add(refund)
    db.commit()
    db.refresh(refund)

    return schemas.Resp(
        data={"refund_id": refund.id, "refund_no": refund.refund_no, "status": refund.status}
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _order_to_out(o: models.Order) -> schemas.OrderOut:
    items = [
        schemas.OrderItemOut(
            sku_name=i.sku_name,
            cover_url=i.cover_url,
            price=float(i.price),
            quantity=i.quantity,
            subtotal=float(i.subtotal),
        )
        for i in o.items
    ]
    return schemas.OrderOut(
        order_id=o.id,
        order_no=o.order_no,
        total_amount=float(o.total_amount),
        pay_amount=float(o.pay_amount) if o.pay_amount else None,
        status=o.status,
        receiver_name=o.receiver_name,
        receiver_address=o.receiver_address,
        items=items,
        created_at=o.created_at.isoformat() if o.created_at else None,
    )
