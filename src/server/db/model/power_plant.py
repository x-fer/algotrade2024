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
    async def buy_plant(cls, type: int, price: int, player_id: int):
        # TODO:
        # pocetak transakcije
        # provjera stanja novca za igraca u bazi
        # oduzimanje novca u bazi
        # dodavanje power_planta u bazi
        # kraj transakcije
        # nesto ovako:
        # async with database.transaction():
        # goran_id = await Team.create(team_name="Goran 40", team_secret=id_generator())
        # if goran_id == 43:
        #     assert False
        # return await Team.get(team_id=goran_id)
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
        await cls.update(is_active=0, plant_id=plant_id)

    @classmethod
    async def turn_off(cls, type: int, plant_id: int):
        await cls.update(is_active=1, plant_id=plant_id)
