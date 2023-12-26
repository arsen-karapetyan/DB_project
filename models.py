from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ChessPlayer(Base):
    __tablename__ = 'chess_player'
    
    id = Column(Integer, primary_key=True)
    family_name = Column(String(50)) 
    name = Column(String(50))  
    rating = Column(Float)  
    country = Column(String(50))  
    
    
    participations = relationship('Participation', back_populates='player')

class Tournament(Base):
    __tablename__ = 'tournament'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    date = Column(Date)
    country = Column(String(50))
    city = Column(String(50))
    participations = relationship('Participation', back_populates='tournament')

class Participation(Base):
    __tablename__ = 'participation'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('chess_player.id'))
    tournament_id = Column(Integer, ForeignKey('tournament.id'))
    start_number = Column(Integer)  
    known_place = Column(Integer)  
    qualification_level = Column(String(50))  

    player = relationship('ChessPlayer', back_populates='participations')
    tournament = relationship('Tournament', back_populates='participations')