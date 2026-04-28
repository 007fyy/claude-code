from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_current_user
from database import get_db
from models.user import User
from schemas.address import AddressCreate, AddressOut, AddressUpdate
from schemas.common import ApiResponse
from schemas.user import UpdatePrefsReq, UpdateUserReq, UserOut
from services.address_service import AddressService
from services.user_service import UserService

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/me", response_model=ApiResponse[UserOut])
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ApiResponse(data=UserOut.model_validate(current_user))


@router.put("/me", response_model=ApiResponse[UserOut])
def update_me(
    req: UpdateUserReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService(db).update_me(current_user, req)
    return ApiResponse(data=UserOut.model_validate(user))


@router.patch("/prefs", response_model=ApiResponse[UserOut])
def update_prefs(
    req: UpdatePrefsReq,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = UserService(db).update_prefs(current_user, req)
    return ApiResponse(data=UserOut.model_validate(user))


# ── 收货地址 ────────────────────────────────────────────────────────────────

@router.get("/address", response_model=ApiResponse[list[AddressOut]])
def list_address(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addrs = AddressService(db, current_user.id).list()
    return ApiResponse(data=[AddressOut.model_validate(a) for a in addrs])


@router.post("/address", response_model=ApiResponse[AddressOut])
def create_address(
    req: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = AddressService(db, current_user.id).create(req)
    return ApiResponse(data=AddressOut.model_validate(addr))


@router.put("/address/{address_id}", response_model=ApiResponse[AddressOut])
def update_address(
    address_id: int,
    req: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = AddressService(db, current_user.id).update(address_id, req)
    return ApiResponse(data=AddressOut.model_validate(addr))


@router.delete("/address/{address_id}", response_model=ApiResponse[None])
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AddressService(db, current_user.id).delete(address_id)
    return ApiResponse()


@router.patch("/address/{address_id}/default", response_model=ApiResponse[AddressOut])
def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    addr = AddressService(db, current_user.id).set_default(address_id)
    return ApiResponse(data=AddressOut.model_validate(addr))
