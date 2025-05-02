import uuid
from sqlalchemy import Column, String, Text, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class AgentModel(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False)
    instruction = Column(Text, nullable=False)

    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=1.0)
    presence_penalty = Column(Float, default=0.0)
    frequency_penalty = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
