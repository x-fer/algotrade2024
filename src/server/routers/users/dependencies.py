from fastapi import HTTPException, Query
from db import Team


async def team_id(team_secret: str = Query(..., description="User secret")):
    try:
        return await Team.get(team_secret).team_id
    except:
        raise HTTPException(status_code=403, detail="Invalid team_secret")