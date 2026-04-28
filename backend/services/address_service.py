from sqlalchemy.orm import Session

from config import BizError
from models.address import Address
from schemas.address import AddressCreate, AddressUpdate


class AddressService:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def list(self) -> list[Address]:
        return (
            self.db.query(Address)
            .filter(Address.user_id == self.user_id)
            .order_by(Address.is_default.desc(), Address.created_at.asc())
            .all()
        )

    def create(self, req: AddressCreate) -> Address:
        count = (
            self.db.query(Address)
            .filter(Address.user_id == self.user_id)
            .count()
        )
        if count >= 5:
            raise BizError(1102, "最多保存5个收货地址")

        is_default = req.is_default or count == 0
        if is_default:
            self._set_all_non_default()

        addr = Address(
            user_id=self.user_id,
            name=req.name,
            phone=req.phone,
            province=req.province,
            city=req.city,
            district=req.district,
            detail=req.detail,
            is_default=is_default,
        )
        self.db.add(addr)
        self.db.commit()
        self.db.refresh(addr)
        return addr

    def update(self, address_id: int, req: AddressUpdate) -> Address:
        addr = self._get_or_403(address_id)
        if req.is_default is True:
            self._set_all_non_default()
        update_data = req.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(addr, field, value)
        self.db.commit()
        self.db.refresh(addr)
        return addr

    def delete(self, address_id: int) -> None:
        addr = self._get_or_403(address_id)
        was_default = addr.is_default
        self.db.delete(addr)
        self.db.flush()

        if was_default:
            next_addr = (
                self.db.query(Address)
                .filter(Address.user_id == self.user_id)
                .order_by(Address.created_at.desc())
                .first()
            )
            if next_addr:
                next_addr.is_default = True

        self.db.commit()

    def set_default(self, address_id: int) -> Address:
        addr = self._get_or_403(address_id)
        self._set_all_non_default()
        addr.is_default = True
        self.db.commit()
        self.db.refresh(addr)
        return addr

    def _get_or_403(self, address_id: int) -> Address:
        addr = self.db.get(Address, address_id)
        if not addr or addr.user_id != self.user_id:
            raise BizError(1103, "地址不存在")
        return addr

    def _set_all_non_default(self) -> None:
        self.db.query(Address).filter(Address.user_id == self.user_id).update(
            {"is_default": False}
        )
