from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from core.deps import get_current_user
from models.user import User
from models.favorite import UserFavorite
from models.goods import GoodsSpu, GoodsSku
from schemas.common import ApiResponse
from schemas.favorite import FavoriteToggleReq, FavoriteOut, FavoriteListItem

router = APIRouter()


@router.post("/toggle", response_model=ApiResponse[FavoriteOut])
def toggle_favorite(
    req: FavoriteToggleReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.spu_id == req.spu_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return ApiResponse(data=FavoriteOut(spu_id=req.spu_id, is_favorited=False))

    fav = UserFavorite(user_id=current_user.id, spu_id=req.spu_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return ApiResponse(data=FavoriteOut(
        spu_id=req.spu_id,
        is_favorited=True,
        created_at=fav.created_at.isoformat() if fav.created_at else None,
    ))


@router.get("/list", response_model=ApiResponse[list[FavoriteListItem]])
def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(UserFavorite, GoodsSpu)
        .join(GoodsSpu, GoodsSpu.id == UserFavorite.spu_id)
        .filter(UserFavorite.user_id == current_user.id)
        .order_by(UserFavorite.id.desc())
        .all()
    )

    items = []
    for fav, spu in rows:
        active_skus = [s for s in spu.skus if s.status == 1]
        price_min = min((float(s.price) for s in active_skus), default=0)
        price_max = max((float(s.price) for s in active_skus), default=0)
        items.append(FavoriteListItem(
            spu_id=spu.id,
            name=spu.name,
            cover_url=spu.cover_url or "",
            price_range=f"{price_min:.0f} - {price_max:.0f}",
            category=spu.category,
            material=spu.material or "",
            created_at=fav.created_at.isoformat() if fav.created_at else None,
        ))

    return ApiResponse(data=items)


@router.get("/check", response_model=ApiResponse[FavoriteOut])
def check_favorite(
    spu_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.spu_id == spu_id,
    ).first()

    return ApiResponse(data=FavoriteOut(
        spu_id=spu_id,
        is_favorited=existing is not None,
        created_at=existing.created_at.isoformat() if existing and existing.created_at else None,
    ))
