from . import produced_energy as energy_service
from model import Player, PowerPlant, Game, PowerPlantType, Contract, ContractStatus
from config import config


def update_energy_and_power_plants(game: Game, player: Player, power_plants: dict[int, list[PowerPlant]]):
    player.energy = 0
    for power_plant in power_plants[player.player_id]:
        plant_type = PowerPlantType(power_plant.type)
        if power_plant.temperature == 1 and power_plant.powered_on:
            resources_per_tick = config["power_plant"]["resources_per_tick"]
            resources = player[plant_type.get_name()]
            if plant_type.is_renewable():
                player.energy += energy_service.get_produced_renewable_energy(
                    game.dataset, game.current_tick, plant_type)
            elif resources > resources_per_tick:
                player.energy += energy_service.get_produced_energy(
                    game.dataset, game.current_tick, plant_type)
                resources -= resources_per_tick
                player[plant_type.get_name()] = resources
            else:
                power_plant.powered_on = False
        power_plant.temperature = plant_type.get_new_temp(power_plant.temperature,
                                                          power_plant.powered_on)


def update_energy_and_contracts(game: Game, player: Player, players: dict[int, Player], old_contracts: dict[int, Contract]):
    if not player.player_id in old_contracts:
        return
    for contract in old_contracts[player.player_id]:
        if contract.end_tick <= game.current_tick:
            player.money += contract.price
            player.money += contract.down_payment
            contract.contract_status = ContractStatus.COMPLETED
        elif player.energy < contract.size:
            contract.contract_status = ContractStatus.CANCELLED
        else:
            player.energy -= contract.size
            players[contract.bot_id].energy += contract.size
