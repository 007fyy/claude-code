from pydantic import BaseModel, ConfigDict


class AddressCreate(BaseModel):
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False


class AddressUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    detail: str | None = None
    is_default: bool | None = None


class AddressOut(BaseModel):
    id: int
    user_id: int
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)
