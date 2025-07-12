from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer
from typing import Any

@as_declarative()
class Base:
    """Base class which provides automated table name
    and surrogate primary key column.
    """

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    __name__: str

    # Generate __repr__ method for the model
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
