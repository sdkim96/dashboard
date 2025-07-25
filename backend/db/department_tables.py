import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class DepartmentBase(DeclarativeBase):
    pass

class Department(DepartmentBase):
    __tablename__ = 'department'

    department_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the department."
    )
    name: Mapped[str] = mapped_column(
        doc="Name of the department, unique across all departments."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the department was created."
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the department was last updated."
    )

    def __repr__(self):
        return f"<Department(id={self.department_id}, name={self.name})>"