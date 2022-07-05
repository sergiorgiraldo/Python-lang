import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class Session(Base):
    __tablename__ = "session"
    identifier = Column(String(12), nullable=False, primary_key=True)
 
class Request(Base):
    __tablename__ = "request"
    dt = Column(DateTime, nullable=False, primary_key=True)
    page = Column(String(200), nullable=False)
    identifier = Column(String(12), ForeignKey("session.identifier"))
    session = relationship(Session)
 
# Create an engine that stores data in the local directory's geru.db file.
engine = create_engine("sqlite:///geru.db")
 
# Create all tables in the engine. 
Base.metadata.create_all(engine)