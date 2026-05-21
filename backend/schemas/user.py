import re
from pydantic import BaseModel, ConfigDict, field_validator


class SendCodeReq(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("邮箱格式不正确")
        return v.lower()


class SendCodeOut(BaseModel):
    is_registered: bool


class LoginReq(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("邮箱格式不正确")
        return v.lower()


class VerifyReq(BaseModel):
    email: str
    code: str
    password: str | None = None
    nickname: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str | None) -> str | None:
        if v is not None and len(v) < 8:
            raise ValueError("密码至少8位，需包含字母和数字")
        return v


class UserOut(BaseModel):
    id: int
    email: str
    nickname: str | None
    avatar_url: str | None
    phone: str | None
    gender: str | None
    birthday: str | None
    signature: str | None
    bio: str | None
    role: str
    style_prefs: list | None
    occasion_prefs: list | None
    budget_pref: str | None
    face_type: str | None
    skin_tone: str | None

    model_config = ConfigDict(from_attributes=True)


class LoginOut(BaseModel):
    token: str
    user: UserOut
    is_new_user: bool = False


class UpdateUserReq(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    phone: str | None = None
    gender: str | None = None
    birthday: str | None = None
    signature: str | None = None
    bio: str | None = None


class UpdatePrefsReq(BaseModel):
    style_prefs: list[str] | None = None
    occasion_prefs: list[str] | None = None
    budget_pref: str | None = None
    face_type: str | None = None
    skin_tone: str | None = None


class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少8位")
        return v


class ResetPasswordReq(BaseModel):
    email: str
    code: str
    new_password: str

    @field_validator("email")
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("邮箱格式不正确")
        return v.lower()

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少8位")
        return v
