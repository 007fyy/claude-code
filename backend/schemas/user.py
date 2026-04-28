import re
from pydantic import BaseModel, ConfigDict, field_validator


class SendCodeReq(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def phone_must_be_valid(cls, v: str) -> str:
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v


class LoginReq(BaseModel):
    phone: str
    code: str


class UserOut(BaseModel):
    id: int
    phone: str
    nickname: str | None
    avatar_url: str | None
    role: str
    style_prefs: list | None
    occasion_prefs: list | None
    budget_pref: str | None

    model_config = ConfigDict(from_attributes=True)


class UpdateUserReq(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None


class UpdatePrefsReq(BaseModel):
    style_prefs: list[str] | None = None
    occasion_prefs: list[str] | None = None
    budget_pref: str | None = None


class LoginOut(BaseModel):
    token: str
    user: UserOut
