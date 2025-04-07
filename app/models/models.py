from sqlalchemy import Column, String, Text
from sqlalchemy.orm import DeclarativeBase


# -----------------------
# DATABASE MODEL
# -----------------------
class Base(DeclarativeBase):
    pass


class Storage(Base):
    __tablename__ = "storage"
    key = Column(String, primary_key=True)
    value = Column(Text)
