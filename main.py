from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

participation_table = Table('participation', Base.metadata,
    Column('player_id', ForeignKey('chess_player.id'), primary_key=True),
    Column('tournament_id', ForeignKey('tournament.id'), primary_key=True)
)

class ChessPlayer(Base):
    __tablename__ = 'chess_player'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    rating = Column(Float)
    country = Column(String(50))
    participations = relationship('Tournament', secondary=participation_table, back_populates='players')

class Tournament(Base):
    __tablename__ = 'tournament'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    date = Column(Date)
    country = Column(String(50))
    city = Column(String(50))
    players = relationship('ChessPlayer', secondary=participation_table, back_populates='participations')

class ChessPlayerBase(BaseModel):
    name: str
    rating: float
    country: str

class ChessPlayerCreate(ChessPlayerBase):
    pass

class ChessPlayerDB(ChessPlayerBase):
    id: int
    class Config:
        orm_mode = True

class TournamentBase(BaseModel):
    name: str
    date: Date
    country: str
    city: str

class TournamentCreate(TournamentBase):
    pass

class TournamentDB(TournamentBase):
    id: int
    class Config:
        orm_mode = True

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/chess_players/", response_model=ChessPlayerDB)
def create_chess_player(chess_player: ChessPlayerCreate, db: Session = Depends(get_db)):
    db_player = ChessPlayer(**chess_player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

@app.get("/chess_players/", response_model=List[ChessPlayerDB])
def read_chess_players(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    players = db.query(ChessPlayer).offset(skip).limit(limit).all()
    return players

@app.get("/chess_players/{player_id}", response_model=ChessPlayerDB)
def read_chess_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(ChessPlayer).filter(ChessPlayer.id == player_id).first()
    if player is None:
        raise HTTPException(status_code=404, detail="Chess player not found")
    return player

@app.put("/chess_players/{player_id}", response_model=ChessPlayerDB)
def update_chess_player(player_id: int, chess_player: ChessPlayerCreate, db: Session = Depends(get_db)):
    db_player = db.query(ChessPlayer).filter(ChessPlayer.id == player_id).first()
    if db_player is None:
        raise HTTPException(status_code=404, detail="Chess player not found")
    for var, value in vars(chess_player).items():
        setattr(db_player, var, value) if value else None
    db.commit()
    db.refresh(db_player)
    return db_player

@app.delete("/chess_players/{player_id}")
def delete_chess_player(player_id: int, db: Session = Depends(get_db)):
    db_player = db.query(ChessPlayer).filter(ChessPlayer.id == player_id).first()
    if db_player is None:
        raise HTTPException(status_code=404, detail="Chess player not found")
    db.delete(db_player)
    db.commit()
    return {"ok": True}
