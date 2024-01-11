from fastapi import APIRouter
from routers.users import player, game


router = APIRouter()


router.include_router(player.router)
router.include_router(game.router)