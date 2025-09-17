from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


# Modelo de la base de datos
class Users(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    favorite_sport = Column(String, nullable=True)

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