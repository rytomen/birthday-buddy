from sqlalchemy import Column, Date, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    birth_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat(),
        }
