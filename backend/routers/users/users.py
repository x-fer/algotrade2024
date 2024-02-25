from fastapi import APIRouter
from . import player, game, power_plant, market

router = APIRouter()


router.include_router(game.router, tags=["Games"])
router.include_router(player.router, tags=["Player"])
router.include_router(power_plant.router, tags=["Power plants"])
router.include_router(market.router, tags=["Market"])
