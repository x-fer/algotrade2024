from fastapi import APIRouter

# BOT PATHS

# GET	/admin/bot/list	-	[{"id": [id], "name": [name]}, {}, {}, {}]

router = APIRouter()


@router.get("/bot/list")
async def bot_list():
    return {"message": "Hello World"}