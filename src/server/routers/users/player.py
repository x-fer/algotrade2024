from fastapi import APIRouter, Depends, HTTPException
from db import Player, database, Team
from routers.users.dependencies import team_id, player

# PLAYER PATHS

# /game/[id]/player/create?team_secret=
# /game/[id]/player/list?team_secret=
# /game/[id]/player/[player_id]/delete?team_secret=


router = APIRouter()


@router.get("/game/{game_id}/player/list")
async def player_list(game_id: int, team_id: int=Depends(team_id)):
    players = await Player.list(game_id=game_id, team_id=team_id)
    return {"players": players}


@router.get("/game/{game_id}/player/create")
async def player_create(game_id: int, team_id: int=Depends(team_id), player_name=None):
    # TODO: pretvoriti u post
    with database.transaction():
        if player_name is None: 
            team = await Team.get(team_id=team_id)
            team_players_len = len(await Player.count(team_id=team_id, game_id=game_id))
            player_name = f"{team.team_name}_{team_players_len}"
        player_id = await Player.create(game_id=game_id, team_id=team_id, player_name=player_name)
    return {"player_id": player_id}


@router.get("/game/{game_id}/player/{player_id}")
async def player_get(player=Depends(player)):
    return {"player": await Player.get(player_id=player.player_id)}


@router.get("/game/{game_id}/player/{player_id}/delete")
async def player_delete(player=Depends(player)):
    return {"successfull": await Player.update(player_id=player.player_id, is_active=False)}