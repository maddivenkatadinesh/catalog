import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(220), nullable=False)
    picture = Column(String(300))


class AeroplaneName(Base):
    __tablename__ = 'aeroplanename'
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="aeroplanename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class ModelName(Base):
    __tablename__ = 'modelname'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    capacity = Column(String(150))
    topspeed = Column(String(150))
    rating = Column(String(150))
    service = Column(String(10))
    date = Column(DateTime, nullable=False)
    aeroplanenameid = Column(Integer, ForeignKey('aeroplanename.id'))
    aeroplanename = relationship(
        AeroplaneName, backref=backref('modelname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="modelname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'capacity': self. capacity,
            'topspeed': self. topspeed,
            'rating': self. rating,
            'service': self. service,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///aeroplanes.db')
Base.metadata.create_all(engin)
