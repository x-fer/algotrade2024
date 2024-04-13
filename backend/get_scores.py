team_names = [
    "); DROP TABLE players; --",
    "brokeRS",
    "Cekmi",
    "Data Diggers",
    "Guta",
    "INAI",
    "Kako mislis mene nema?",
    "Kodirani Kapital",
    "LIMA",
    "Maas",
    "Održavanje dalekovoda",
    "OptiMinds",
    "Pip install v2",
    "Šampioni Hackathona",
    "Three and a half men",
    "Between exams",
    "Evolutionary Enigmas",
    "green48",
    "Jerry & Totally Spies",
    "Pigeons",
    "Polacy Robacy",
    "si_intl",
    "UW2",
    "Vanjo",
    "Warsaw Mesh Trade AI",
]

leaderboard_scores = [200, 182, 170, 158, 146, 134, 124, 114, 104, 94, 84, 78, 72, 66, 60, 54, 48, 42, 36, 30, 24, 18, 12, 6, 0]


lines = []
with open('scores/01HVAB7VVCN6DYYAYHM8142WGB_First contest round.txt', "r") as f:
    for line in f:
        lines.append(line)
    last_line_1 = line

with open('scores/01HVB6VYT63CFMDPR42GM6N37B_Second contest round.txt', "r") as f:
    for line in f:
        lines.append(line)
    last_line_2 = line

with open('scores/01HVBSHM3NEW37N5RWDN749XGM_Third contest round.txt', "r") as f:
    for line in f:
        lines.append(line)
    last_line_3 = line

last_line = last_line_3

# text = "1196, [(Polacy Robacy/Polacy_Robacy, 107251400), (Jerry & Totally Spies/Botko, 94323634), (Pip install v2/pom, 37574900), (Održavanje dalekovoda/, 136683600), (si_intl/dfg, 53925395), (Evolutionary Enigmas/ttt, 224211978), (Data Diggers/diggy, 220143262), (Kako mislis mene nema?/ElonMusk Kukulele, 167075037), (OptiMinds/OptiMindsPlayer, 62426452), (Kruno/Casey Jones, 163297233), (Maas/Maas, 39749469), (green48/test2, 100015214), (Cekmi/ivkalu_bot, 43196913), (brokeRS/brrsbot, 270338065), (Between exams/string, 322312528), (Kodirani Kapital/Kodirani Kapital, 1196722622), (Warsaw Mesh Trade AI/croatia_on_steroids, 310802358), (Three and a half men/test, 326151613), (UW2/mati, 320454914), (LIMA/LIMA_1, 56961157), (Šampioni Hackathona/testko3, 392445174)]"
def parse_one(text):
    team_scores = []
    for team_name in team_names:
        try:
            ind = text.index(team_name)
        except Exception:
            continue
        # try:
        ind_1 = text.index(", ", ind)
        try:
            ind_2 = text.index("), ", ind_1)
        except Exception:
            ind_2 = text.index(")]", ind_1)
        score = int(text[ind_1+2: ind_2])
        team_scores.append((score, team_name))
        # except Exception:
        #     print(f"Error parsing score for team {team_name}")
    return team_scores

def print_last():
    team_scores = parse_one(last_line)
    team_scores.sort(reverse=True)
    for i, value in enumerate(team_scores):
        score, team_name = value
        print(f"{i+1}) {leaderboard_scores[i]} - {score}$ - {team_name}, {score/50_000_000}")


def one_to_dict(team_scores):
    scores_dict = {}
    for score, team_name in team_scores:
        scores_dict[team_name] = score
    return scores_dict


def get_real_scores(team_scores):
    team_scores.sort(reverse=True)
    real_scores = dict()
    for i, value in enumerate(team_scores):
        score, team_name = value
        score = leaderboard_scores[i]
        real_scores[team_name] = score
    return real_scores


# all_scores_dict = {team_name: [] for team_name in team_names}

# scores = []
# for line in lines:
#     tick_dict = one_to_dict(parse_one(line))
#     for team_name in team_names:
#         try:
#             score = tick_dict[team_name]
#         except Exception:
#             score = 50_000_000
#         all_scores_dict[team_name].append(score)


# print(len(scores))

# print_last()

# print(last_line)

# DataFrame


# GET TOTAL SCORE
prva = get_real_scores(parse_one(last_line_1))
druga = get_real_scores(parse_one(last_line_2))
treca = get_real_scores(parse_one(last_line_3))

ukupno = dict()

for team in prva:
    ukupno[team] = prva[team] + druga[team] + treca[team]

ukupno_list = []
for team, score in ukupno.items():
    ukupno_list.append((score, team))
ukupno_list.sort(reverse=True)

for score, team in ukupno_list:
    print(f"{score} {team}")
