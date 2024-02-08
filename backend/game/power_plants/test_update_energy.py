from config import config
from model import Player, Game, PowerPlantType
from config import config
from . import update_energy_and_power_plants, update_energy_and_contracts
from game.fixtures.fixtures import *


class TestPowerPlants:
    def test_update_energy_and_power_plants(self, game: Game, get_player, get_power_plant):
        starting_coal = 100
        player_1: Player = get_player(energy=0, coal=starting_coal, uranium=0)
        player_2: Player = get_player(energy=0, coal=0, uranium=0)

        power_plant_1 = get_power_plant(player_1.player_id, type=PowerPlantType.COAL, powered_on=True, temperature=1)
        power_plant_2 = get_power_plant(player_1.player_id, type=PowerPlantType.COAL, powered_on=False, temperature=1)
        power_plant_3 = get_power_plant(player_1.player_id, type=PowerPlantType.URANIUM, powered_on=True, temperature=1)
        power_plant_4 = get_power_plant(player_2.player_id, type=PowerPlantType.COAL, powered_on=True, temperature=1)

        power_plants = {
            player_1.player_id:
            [
                power_plant_1,
                power_plant_2,
                power_plant_3,
            ],
            player_2.player_id: [power_plant_4]
        }

        update_energy_and_power_plants(game, player_1, power_plants)

        expected_coal = starting_coal - config["power_plant"]["resources_per_tick"] 

        assert power_plant_1.powered_on
        assert not power_plant_2.powered_on
        assert not power_plant_3.powered_on
        assert power_plant_4.powered_on
        assert player_1.coal == expected_coal
        assert player_1.energy > 0
        assert player_2.coal == 0

    def test_power_plant_shut_down(self, game: Game, get_player, get_power_plant):
        player_1: Player = get_player(energy=0, coal=0)
        
        power_plant_1 = get_power_plant(player_1.player_id, type=PowerPlantType.COAL, powered_on=True, temperature=1)

        power_plants = {
            player_1.player_id: [power_plant_1]
        }

        update_energy_and_power_plants(game, player_1, power_plants)

        assert not power_plant_1.powered_on
        assert player_1.energy == 0
        assert player_1.coal == 0


class TestContracts:
    def test_contract_completed(self, game: Game, get_player, get_contract):
        player: Player = get_player(energy=50, money=0)
        bot: Player = get_player(energy=50, money=0)
        contract: Contract = get_contract(
            player_id=player.player_id,
            bot_id=bot.player_id,
            price=10,
            size=10,
            down_payment=5,
        )
        players = {player.player_id: player, bot.player_id: bot}
        contracts = {player.player_id: [contract]}
        game.current_tick = contract.end_tick

        update_energy_and_contracts(game, player, players, contracts)

        assert contract.contract_status == ContractStatus.COMPLETED
        assert player.energy == 50
        assert player.money == 15
        assert bot.energy == 50
        assert bot.money == 0
    
    def test_contract_tick_and_fail(self, game: Game, get_player, get_contract):
        player: Player = get_player(energy=15, money=0)
        bot: Player = get_player(energy=0, money=0)
        contract: Contract = get_contract(
            player_id=player.player_id,
            bot_id=bot.player_id,
            price=10,
            size=10,
            down_payment=5,
        )
        contracts = {player.player_id: [contract]}
        players = {player.player_id: player, bot.player_id: bot}

        update_energy_and_contracts(game, player, players, contracts)

        assert contract.contract_status == ContractStatus.ACTIVE
        assert player.energy == 5
        assert player.money == 0
        assert player.energy == 5
        assert bot.energy == 10

        update_energy_and_contracts(game, player, players, contracts)

        assert contract.contract_status == ContractStatus.CANCELLED
        assert player.energy == 5
        assert player.money == 0
        assert player.energy == 5
        assert bot.energy == 10
    
    def test_no_contract(self, game: Game, get_player, get_contract):
        player: Player = get_player(energy=50, money=0)
        players = {player.player_id: player}

        update_energy_and_contracts(game, player, players, dict())

        assert player.energy == 50
        assert player.money == 0