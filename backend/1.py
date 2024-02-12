import httpx

client = httpx.Client()


response = client.get(
    'http://localhost:8000/game/1/market/offer/list?team_secret=gogi')

print(response.json())

# make offer

response = client.post(
    'http://localhost:8000/game/1/player/1/market/offer/create?team_secret=gogi',
    json={
        "resource": 1,
        "price": 10,
        "size": 10,
        "expiration_tick": 100,
        "side": 0,
        "type": 1
    }
)

print(response.json())
