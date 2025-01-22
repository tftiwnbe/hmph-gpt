from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class UserModel(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        username (str): Username, must be unique.
        tg_user_id (int, optional): Telegram user ID, can be null.
        ds_user_id (int, optional): Discord user ID, can be null.
        meet_date (datetime): Date when the user was registered or last met.
        is_active (bool): Indicates if the user is active in the system.
        is_admin (bool): Indicates if the user has admin privileges.
        wireguard_tunnels (list[WireGuardTunnelModel]): List of WireGuard tunnels
                                                        associated with the user.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    username: Mapped[str] = mapped_column(String(255), index=True, unique=True)
    tg_user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=True
    )
    ds_user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=True
    )
    meet_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
