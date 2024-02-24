# import pytest
# from tick import Ticker, TickData
# from model import Game, Player, PowerPlantType, Resource, DatasetData


# @pytest.fixture
# def ticker_instance(self):
#     return Ticker()


# def test_run_power_plants_renewable(self, ticker_instance):
#     # Test scenario with renewable power plants
#     game = Game(game_id=1, is_finished=False, start_time="2024-01-01",
#                 current_tick=1, total_ticks=10, game_name="Test Game", dataset_id=1)
#     player = Player(player_id=1, game_id=1, solar=10,
#                     solar_plants_powered=5, energy=0)  # Sample player data
#     dataset_row = DatasetData(
#         dataset_id=1, tick=1, energy_demand=100, max_energy_price=200)  # Sample dataset row

#     tick_data = TickData(game=game, players={player.player_id: player}, markets={
#     }, bots=[], pending_orders=[], user_cancelled_orders=[], dataset_row=dataset_row)

#     updated_tick_data = ticker_instance.run_power_plants(tick_data)

#     assert updated_tick_data.players[1].energy == (
#         5 * PowerPlantType.SOLAR.get_produced_energy(dataset_row))


# def test_run_power_plants_nonrenewable_limitation(self, ticker_instance):
#     # Test scenario with non-renewable power plants and limitation
#     game = Game(game_id=1, is_finished=False, start_time="2024-01-01",
#                 current_tick=1, total_ticks=10, game_name="Test Game", dataset_id=1)
#     player = Player(player_id=1, game_id=1, coal=5,
#                     coal_plants_powered=10, energy=0)  # Sample player data
#     dataset_row = DatasetData(
#         dataset_id=1, tick=1, energy_demand=100, max_energy_price=200)  # Sample dataset row

#     tick_data = TickData(game=game, players={player.player_id: player}, markets={
#     }, bots=[], pending_orders=[], user_cancelled_orders=[], dataset_row=dataset_row)

#     updated_tick_data = ticker_instance.run_power_plants(tick_data)

#     assert updated_tick_data.players[1].energy == (
#         5 * PowerPlantType.COAL.get_produced_energy(dataset_row))


# def test_run_power_plants_no_power_plants(self, ticker_instance):
#     # Test scenario with no power plants
#     game = Game(game_id=1, is_finished=False, start_time="2024-01-01",
#                 current_tick=1, total_ticks=10, game_name="Test Game", dataset_id=1)
#     player = Player(player_id=1, game_id=1, coal=0,
#                     coal_plants_powered=0, energy=0)  # Sample player data
#     dataset_row = DatasetData(
#         dataset_id=1, tick=1, energy_demand=100, max_energy_price=200)  # Sample dataset row

#     tick_data = TickData(game=game, players={player.player_id: player}, markets={
#     }, bots=[], pending_orders=[], user_cancelled_orders=[], dataset_row=dataset_row)

#     updated_tick_data = ticker_instance.run_power_plants(tick_data)

#     assert updated_tick_data.players[1].energy == 0


# def test_run_power_plants_edge_cases(self, ticker_instance):
#     # Test edge cases
#     game = Game(game_id=1, is_finished=False, start_time="2024-01-01",
#                 current_tick=1, total_ticks=10, game_name="Test Game", dataset_id=1)
#     # Player has exactly the resources needed
#     player1 = Player(player_id=1, game_id=1, coal=5,
#                      coal_plants_powered=5, energy=0)
#     # Player has more power plants powered than available resources
#     player2 = Player(player_id=2, game_id=1, solar=20,
#                      solar_plants_powered=30, energy=0)

#     dataset_row = DatasetData(
#         dataset_id=1, tick=1, energy_demand=100, max_energy_price=200)  # Sample dataset row

#     tick_data1 = TickData(game=game, players={player1.player_id: player1}, markets={
#     }, bots=[], pending_orders=[], user_cancelled_orders=[], dataset_row=dataset_row)
#     tick_data2 = TickData(game=game, players={player2.player_id: player2}, markets={
#     }, bots=[], pending_orders=[], user_cancelled_orders=[], dataset_row=dataset_row)

#     updated_tick_data1 = ticker_instance.run_power_plants(tick_data1)
#     updated_tick_data2 = ticker_instance.run_power_plants(tick_data2)

#     assert updated_tick_data1.players[1].energy == (
#         5 * PowerPlantType.COAL.get_produced_energy(dataset_row))
#     assert updated_tick_data2.players[2].energy == (
#         20 * PowerPlantType.SOLAR.get_produced_energy(dataset_row))
