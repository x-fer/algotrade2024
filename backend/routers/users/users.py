from fastapi import APIRouter, Depends
from routers.users.dependencies import team_id
from routers.users import player, game, power_plant, market


router = APIRouter(dependencies=[Depends(team_id)])


router.include_router(player.router)
router.include_router(game.router)
router.include_router(power_plant.router)
router.include_router(market.router)
