from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PublicUser(BaseModel):
    id: str
    name: str
    avatar: str | None
    profile: str | None
    created_at: datetime


class UserView(PublicUser):
    account: str
    role: Literal["user", "admin", "vip"]
    edited_at: datetime
    updated_at: datetime
    vip_expires_at: datetime | None
    vip_number: str | None


class UserPage(BaseModel):
    items: list[UserView]
    total: int
    page: int
    page_size: int


class CreatedUser(BaseModel):
    id: str


class CsrfView(BaseModel):
    csrf_token: str


class Credentials(StrictInput):
    account: str = Field(min_length=4, max_length=256)
    password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def validate_blank(self):
        if not self.account.strip() or not self.password.strip():
            raise ValueError("帳號與密碼不能空白")
        return self


class Registration(Credentials):
    confirm_password: str = Field(min_length=8, max_length=128)

    @model_validator(mode="after")
    def confirm(self):
        if self.password != self.confirm_password:
            raise ValueError("兩次密碼不一致")
        return self


class UserCreate(Credentials):
    name: str = Field(default="無名", max_length=256)
    avatar: str | None = Field(default=None, max_length=1024)
    profile: str | None = Field(default=None, max_length=512)
    role: Literal["user", "admin", "vip"] = "user"


class UserUpdate(StrictInput):
    name: str | None = Field(default=None, max_length=256)
    avatar: str | None = Field(default=None, max_length=1024)
    profile: str | None = Field(default=None, max_length=512)
    role: Literal["user", "admin", "vip"] | None = None

    @model_validator(mode="after")
    def required_fields_cannot_be_null(self):
        for field in ("name", "role"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} 不能為 null")
        return self


class Redemption(StrictInput):
    code: str = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def nonblank(self):
        if not self.code.strip():
            raise ValueError("代碼不能空白")
        return self
