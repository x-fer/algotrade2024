from fastapi import APIRouter

from game.bots.bots import Bots

# BOT PATHS

# GET	/admin/bot/list	-	[{"id": [id], "name": [name]}, {}, {}, {}]

router = APIRouter()


@router.get("/bot/list", tags=["admin"])
def bot_list():
    return Bots.list()
