from databases import Database

class Team:
    table_name = "teams"

    def __init__(self, team_id: int, team_name: str, team_secret: str):
        self.team_id = team_id
        self.team_name = team_name
        self.team_secret = team_secret

    def __repr__(self):
        return f"({self.team_id} {self.team_name} {self.team_secret})"

    @classmethod
    def set_db(cls, database: Database):
        cls.database = database

    @classmethod
    async def create_team(cls, team_name, team_secret):
        """
        return: id of created team
        """
        query = f"INSERT INTO {cls.table_name} (team_name, team_secret) VALUES (:team_name, :team_secret)"
        values = {"team_name": team_name, "team_secret": team_secret}
        return await cls.database.execute(query=query, values=values)

    @classmethod
    async def get_teams(cls):
        query = f"SELECT * FROM {cls.table_name}"
        # TODO: add try catch, mozda umjesto toga dodati error handler controller na razini fastapija
        result = await cls.database.fetch_all(query)
        return [cls(**team) for team in result]
    
    @classmethod
    async def get_team(cls, team_id=None, team_secret=None):
        if team_id is not None: 
            query = f"SELECT * FROM {cls.table_name} WHERE team_id=:team_id"
            values = {"team_id": team_id}
        elif team_secret is not None: 
            query = f"SELECT * FROM {cls.table_name} WHERE team_secret=:team_secret"            
            values = {"team_secret": team_secret}
        else: raise AttributeError("One of team_id or team_secret shouldn't be None")
        result = await cls.database.fetch_one(query, values)
        assert result, "Requested team doesn't exist"
        return cls(**result)