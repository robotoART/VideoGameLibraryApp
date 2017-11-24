from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    game_machine = relationship('GameMachine', cascade='all, delete-orphan')


class GameMachine(Base):
    __tablename__ = 'game_machine'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    manufacturer = Column(String(80), nullable=False)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    video_game = relationship('VideoGame', cascade='all, delete-orphan')

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'manufacturer' : self.manufacturer,
           'id'           : self.id,
       }


class VideoGame(Base):
    __tablename__ = 'video_game'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    game_machine_id = Column(Integer,ForeignKey('game_machine.id'))
    game_machine = relationship(GameMachine)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'description'  : self.description,
           'id'           : self.id,
       }


engine = create_engine('sqlite:///videogamelibrary.db')


Base.metadata.create_all(engine)
