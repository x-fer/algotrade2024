import random
import string

from model import Team
from model.player import Player


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    # TODO: Nemoguce da se dvaput stvori tim s istim idjem...
    return "".join(random.choice(chars) for _ in range(size))


team_names = [
    ("); DROP TABLE players; --", "R2KHWG3WNM"),
    ("brokeRS", "63TX9AH00B"),
    ("Cekmi", "GTPZGOP0YC"),
    ("Data Diggers", "FRVFO9ANAP"),
    ("Guta", "W7Z8WJ8T97"),
    ("INAI", "K2758VIHOE"),
    ("Kako mislis mene nema?", "UFVOQKGR64"),
    ("Kodirani Kapital", "5MN5ATVJDY"),
    ("LIMA", "SWANHGVS3C"),
    ("Maas", "PXUVRKRQAV"),
    ("Održavanje dalekovoda", "CWO9LH6DH9"),
    ("OptiMinds", "AH9L64F6JT"),
    ("Pip install v2", "J31LWN865I"),
    ("Šampioni Hackathona", "4TPTGJQ1AQ"),
    ("Three and a half men", "FWOOMZ5M30"),
    ("Between exams", "0F85SNN717"),
    ("Evolutionary Enigmas", "61PGJMGECE"),
    ("green48", "4QUYXUSLII"),
    ("Jerry & Totally Spies", "QHNILUTVS0"),
    ("Pigeons", "ZALW5495N6"),
    ("Polacy Robacy", "V8D3O7HH70"),
    ("si_intl", "JE673V0R3Q"),
    ("UW2", "FPY5E4V872"),
    ("Vanjo", "60IMBZPLWE"),
    ("Warsaw Mesh Trade AI", "9EJ6MAV3N5"),
]


if __name__ == "__main__":
    for team_name, team_secret in team_names:
        try:
            Team.find(Team.team_name == team_name).first()
            print(f"Team {team_name} already created")
        except Exception:
            team = Team(team_name=team_name, team_secret=team_secret)
            team.save()
            print(f"Created team {team_name}")
    print(len(team_names))
