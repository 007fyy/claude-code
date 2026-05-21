import time
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.deps import get_current_user, require_admin
from database import get_db
from models.user import User
import models
import schemas

router = APIRouter()


def _make_order_no() -> str:
    ts = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"ORD{ts}{rand}"


def _make_refund_no() -> str:
    ts = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"RFD{ts}{rand}"


@router.post("/create", response_model=schemas.Resp)
def create_order(
    body: schemas.CreateOrderReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(models.CartItem).filter(
        models.CartItem.user_id == current_user.id,
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
        user_id=current_user.id,
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
def pay_order(
    body: schemas.PayOrderReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(
        models.Order.id == body.order_id,
        models.Order.user_id == current_user.id,
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id,
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
    status: str = Query("", description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(models.Order).filter(models.Order.user_id == current_user.id)

    if status:
        if status == "refunding":
            q = q.filter(models.Order.status.in_(["refunding", "refunded"]))
        else:
            q = q.filter(models.Order.status == status)

    total = q.count()
    orders = (
        q.order_by(models.Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    result = [_order_to_out(o, db) for o in orders]
    return schemas.OrderListResp(total=total, items=result)


@router.get("/status_counts", response_model=schemas.Resp)
def order_status_counts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from sqlalchemy import func as sa_func
    rows = (
        db.query(models.Order.status, sa_func.count())
        .filter(models.Order.user_id == current_user.id)
        .group_by(models.Order.status)
        .all()
    )
    counts = {status: cnt for status, cnt in rows}
    return schemas.Resp(data={
        "pending_pay": counts.get("pending_pay", 0),
        "paid": counts.get("paid", 0),
        "shipped": counts.get("shipped", 0),
        "refunding": counts.get("refunding", 0) + counts.get("refunded", 0),
    })


@router.get("/{order_id}", response_model=schemas.Resp)
def order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    return schemas.Resp(data=_order_to_out(order, db).model_dump())


# ── Refund ────────────────────────────────────────────────────────────────────

@router.get("/refund/{refund_id}", response_model=schemas.Resp)
def get_refund(
    refund_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refund = db.query(models.RefundOrder).filter(
        models.RefundOrder.id == refund_id,
        models.RefundOrder.user_id == current_user.id,
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="售后单不存在")

    return schemas.Resp(data={
        "refund_id": refund.id,
        "refund_no": refund.refund_no,
        "order_id": refund.order_id,
        "order_item_id": refund.order_item_id,
        "status": refund.status,
        "reason_type": refund.reason_type,
        "reason_detail": refund.reason_detail,
        "refund_amount": float(refund.refund_amount),
        "return_tracking_no": refund.return_tracking_no,
        "reviewed_at": refund.reviewed_at.isoformat() if refund.reviewed_at else None,
        "refunded_at": refund.refunded_at.isoformat() if refund.refunded_at else None,
        "created_at": refund.created_at.isoformat() if refund.created_at else None,
    })


@router.post("/refund/return_tracking", response_model=schemas.Resp)
def submit_return_tracking(
    refund_id: int = Query(...),
    tracking_no: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refund = db.query(models.RefundOrder).filter(
        models.RefundOrder.id == refund_id,
        models.RefundOrder.user_id == current_user.id,
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="售后单不存在")
    if refund.status != "approved":
        raise HTTPException(status_code=400, detail="售后单尚未审核通过")
    refund.return_tracking_no = tracking_no
    db.commit()
    return schemas.Resp(message="快递单号已提交")


@router.post("/refund/cancel", response_model=schemas.Resp)
def cancel_refund(
    refund_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    refund = db.query(models.RefundOrder).filter(
        models.RefundOrder.id == refund_id,
        models.RefundOrder.user_id == current_user.id,
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="售后单不存在")
    if refund.status != "pending_review":
        raise HTTPException(status_code=400, detail="只有待审核的售后单可以撤销")

    order = db.query(models.Order).filter(models.Order.id == refund.order_id).first()
    if order and order.status == "refunding":
        order.status = "paid"

    db.delete(refund)
    db.commit()
    return schemas.Resp(message="售后申请已撤销")


@router.post("/refund/apply", response_model=schemas.Resp)
def apply_refund(
    body: schemas.ApplyRefundReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    oi = db.query(models.OrderItem).filter(
        models.OrderItem.id == body.order_item_id
    ).first()
    if not oi:
        raise HTTPException(status_code=404, detail="订单明细不存在")

    order = db.query(models.Order).filter(models.Order.id == oi.order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status not in ("paid", "shipped", "completed"):
        raise HTTPException(status_code=400, detail="当前订单状态不支持售后")

    refund = models.RefundOrder(
        refund_no=_make_refund_no(),
        order_id=order.id,
        order_item_id=oi.id,
        user_id=current_user.id,
        sku_id=oi.sku_id,
        quantity=oi.quantity,
        refund_amount=float(oi.subtotal),
        reason_type=body.reason_type,
        reason_detail=body.reason_detail,
        status="pending_review",
    )
    db.add(refund)
    order.status = "refunding"
    db.commit()
    db.refresh(refund)

    return schemas.Resp(
        data={"refund_id": refund.id, "refund_no": refund.refund_no, "status": refund.status}
    )


@router.post("/confirm_receive", response_model=schemas.Resp)
def confirm_receive(
    order_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "shipped":
        raise HTTPException(status_code=400, detail="只有已发货订单可以确认收货")
    order.status = "completed"
    order.receive_time = datetime.now()
    db.commit()
    return schemas.Resp(message="已确认收货")


# ── Admin endpoints ──────────────────────────────────────────────────────────

@router.get("/admin/list", response_model=schemas.OrderListResp)
def admin_order_list(
    status: str = Query("", description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    q = db.query(models.Order)
    if status:
        q = q.filter(models.Order.status == status)
    total = q.count()
    orders = (
        q.order_by(models.Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    result = [_order_to_out(o, db) for o in orders]
    return schemas.OrderListResp(total=total, items=result)


@router.post("/admin/ship", response_model=schemas.Resp)
def admin_ship_order(
    order_id: int = Query(...),
    tracking_no: str = Query(""),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail="只有已付款订单可以发货")
    order.status = "shipped"
    order.ship_time = datetime.now()
    db.commit()
    return schemas.Resp(message="已发货")


@router.post("/admin/complete", response_model=schemas.Resp)
def admin_complete_order(
    order_id: int = Query(...),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "shipped":
        raise HTTPException(status_code=400, detail="只有已发货订单可以确认收货")
    order.status = "completed"
    order.receive_time = datetime.now()
    db.commit()
    return schemas.Resp(message="已确认收货")


@router.post("/admin/refund/approve", response_model=schemas.Resp)
def admin_approve_refund(
    order_id: int = Query(...),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    refund = db.query(models.RefundOrder).filter(
        models.RefundOrder.order_id == order_id,
        models.RefundOrder.status == "pending_review",
    ).first()
    if not refund:
        raise HTTPException(status_code=404, detail="售后单不存在")
    if refund.status != "pending_review":
        raise HTTPException(status_code=400, detail="该售后单已处理")
    refund.status = "approved"
    refund.reviewed_at = datetime.now()
    refund.refunded_at = datetime.now()

    order = db.query(models.Order).filter(models.Order.id == refund.order_id).first()
    if order:
        order.status = "refunded"

    db.commit()
    return schemas.Resp(message="已同意退款")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _order_to_out(o: models.Order, db: Session = None) -> schemas.OrderOut:
    items = []
    for i in o.items:
        spu_name = i.sku_name or ""
        if db and i.spu_id:
            spu = db.query(models.GoodsSpu).filter(models.GoodsSpu.id == i.spu_id).first()
            if spu:
                spu_name = spu.name
        items.append(schemas.OrderItemOut(
            order_item_id=i.id,
            spu_name=spu_name,
            sku_name=i.sku_name,
            cover_url=i.cover_url,
            price=float(i.price),
            quantity=i.quantity,
            subtotal=float(i.subtotal),
        ))
    return schemas.OrderOut(
        order_id=o.id,
        order_no=o.order_no,
        total_amount=float(o.total_amount),
        pay_amount=float(o.pay_amount) if o.pay_amount else None,
        status=o.status,
        receiver_name=o.receiver_name,
        receiver_phone=o.receiver_phone,
        receiver_address=o.receiver_address,
        item_count=len(o.items),
        items=items,
        created_at=o.created_at.isoformat() if o.created_at else None,
    )
