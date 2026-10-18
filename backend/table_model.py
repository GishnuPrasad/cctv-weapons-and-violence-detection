import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    userid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    mobile_number = Column(String(15), unique=True, nullable=False)
    password = Column(String, nullable=False)

    cameras = relationship("Camera", back_populates="user")


class Camera(Base):
    __tablename__ = "cameras"

    camera_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.userid"))
    camera_name = Column(String(100))
    ip_url = Column(String, nullable=False)

    user = relationship("User", back_populates="cameras")
