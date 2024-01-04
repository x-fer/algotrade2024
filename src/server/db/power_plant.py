from dataclasses import dataclass, field
from db.table import Table

@dataclass
class PowerPlant(Table):
    table_name = "power_plants"
    power_plant_id: int
    type: int
    player_id: int
    price: int
    is_active: bool
    temperature: int = field(default=0)

    @classmethod
    async def list(cls, player_id: int) -> list["PowerPlant"]:
        """Returns all power plants owned by player"""
        # TODO: mozda nema potrebe za ovom metodom, nego donju liniju samo staviti direktno u router
        return await cls.get(player_id=player_id)
    
    @classmethod
    async def buy_plant(cls, type: int, price: int, player_id: int):
        # TODO: 
        # pocetak transakcije
        # provjera stanja novca za igraca u bazi
        # oduzimanje novca u bazi
        # dodavanje power_planta u bazi
        # kraj transakcije
        pass

    @classmethod
    async def sell_plant(cls, type: int, plant_id: int):
        # TODO: 
        # pocetak transakcije
        # brisanje power planta ako postoji u bazi
        # dodavanje novca u bazi
        # kraj transakcije
        pass

    @classmethod
    async def turn_on(cls, type: int, plant_id: int):
        # TODO: 
        # placa li se paljenje? ako da, to treba u transaction
        # TODO: provjeriti sto vraca execute
        query = f"UPDATE {cls.table_name} SET is_active=1 WHERE plant_id=:plant_id"
        await cls.database.execute(query, {"plant_id": plant_id})

    @classmethod
    async def turn_off(cls, type: int, plant_id: int):
        query = f"UPDATE {cls.table_name} SET is_active=0 WHERE plant_id=:plant_id"
        await cls.database.execute(query, {"plant_id": plant_id})
