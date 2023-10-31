from fastapi import APIRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///game.db', echo=True)

Session = sessionmaker(bind=engine)
session = Session()

router = APIRouter()


@router.get("/create_game")
async def games():
    return {"message": "Hello World"}


@router.get("/list_games")
async def games():
    return {"message": "Hello World"}
