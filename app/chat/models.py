from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship

from app.database import Base


# Modelo de la base de datos
class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    sport_id = Column(ForeignKey('sports.id', ondelete="CASCADE"), nullable=True)

    sport = relationship("Sports")

class Threads(Base):
    __tablename__ = "threads"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id', ondelete="CASCADE"), nullable=True)

class History(Base):
    __tablename__ = "history"
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(ForeignKey('threads.id', ondelete="CASCADE"), nullable=True)
    input_message = Column(String, nullable=True)
    output_message = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Sports(Base):
    __tablename__ = "sports"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)