from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    tg_user_id: Optional[int] = None
    ds_user_id: Optional[int] = None


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[str] = None
    tg_user_id: Optional[int] = None
    ds_user_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserSearch(BaseModel):
    username: Optional[str] = None
    tg_user_id: Optional[int] = None
    ds_user_id: Optional[int] = None
    create: bool = False


class UserRead(UserCreate):
    is_admin: bool

    class Config:
        from_attributes = True
