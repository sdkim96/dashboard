import datetime as dt

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class UserBase(DeclarativeBase):
    pass


class User(UserBase):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    username: Mapped[str] = mapped_column(
        nullable=False, 
        unique=True
    )
    email: Mapped[str] = mapped_column(
        nullable=False, 
        unique=True
    )
    password_hash: Mapped[str] = mapped_column(
        nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        nullable=False
    )


    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    
def create_user_all(engine: Engine):
    UserBase.metadata.create_all(engine)