
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.memory.database import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)

    question = Column(Text, nullable=False)

    answer = Column(Text, nullable=False)

    confidence = Column(Integer, nullable=False)

    categories = Column(String, nullable=False)

    sources = Column(Text, nullable=False)

    status = Column(
        String,
        nullable=False,
        default="approved",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

