from collections import OrderedDict

from fastapi import APIRouter, Depends
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from database import get_db
from core.deps import get_current_user
from models.user import User
from models.browse_history import BrowseHistory
from models.goods import GoodsSpu
from schemas.common import ApiResponse
from schemas.browse_history import BrowseHistoryReq, BrowseHistoryGroup, BrowseHistoryItem

router = APIRouter()


@router.post("/record", response_model=ApiResponse[None])
def record_view(
    req: BrowseHistoryReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.add(BrowseHistory(user_id=current_user.id, spu_id=req.spu_id))
    db.commit()
    return ApiResponse()


@router.get("/list", response_model=ApiResponse[list[BrowseHistoryGroup]])
def list_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    latest = (
        db.query(
            BrowseHistory.spu_id,
            sa_func.max(BrowseHistory.id).label("max_id"),
        )
        .filter(BrowseHistory.user_id == current_user.id)
        .group_by(BrowseHistory.spu_id)
        .subquery()
    )

    rows = (
        db.query(BrowseHistory, GoodsSpu)
        .join(latest, BrowseHistory.id == latest.c.max_id)
        .join(GoodsSpu, GoodsSpu.id == BrowseHistory.spu_id)
        .order_by(BrowseHistory.created_at.desc())
        .all()
    )

    groups: OrderedDict[str, list[BrowseHistoryItem]] = OrderedDict()
    for hist, spu in rows:
        active_skus = [s for s in spu.skus if s.status == 1]
        price_min = min((float(s.price) for s in active_skus), default=0)
        price_max = max((float(s.price) for s in active_skus), default=0)

        date_str = hist.created_at.strftime("%Y年%m月%d日") if hist.created_at else "未知日期"
        item = BrowseHistoryItem(
            spu_id=spu.id,
            name=spu.name,
            cover_url=spu.cover_url or "",
            price_range=f"{price_min:.0f} - {price_max:.0f}",
            category=spu.category,
            material=spu.material or "",
            viewed_at=hist.created_at.isoformat() if hist.created_at else "",
        )
        groups.setdefault(date_str, []).append(item)

    result = [BrowseHistoryGroup(date=d, items=items) for d, items in groups.items()]
    return ApiResponse(data=result)


@router.delete("/clear", response_model=ApiResponse[None])
def clear_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(BrowseHistory).filter(BrowseHistory.user_id == current_user.id).delete()
    db.commit()
    return ApiResponse()
