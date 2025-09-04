import os
from dotenv import load_dotenv, find_dotenv
from espn_api.football import League

# Load .env from the project root
load_dotenv(find_dotenv(), override=True)

def must_get(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing env var: {name}. Add it to your .env file.")
    return v

LEAGUE_ID = int(must_get("LEAGUE_ID"))
YEAR = int(must_get("YEAR"))
ESPN_S2 = must_get("ESPN_S2")           #
SWID = must_get("SWID")                 

league = League(
    league_id=LEAGUE_ID,
    year=YEAR,
    espn_s2=ESPN_S2,
    swid=SWID
)

print("League:", league.settings.name)
print("Teams:")
for t in league.teams:
    print(t.team_id, t.team_name)

#Define my team
my_team = next(t for t in league.teams if t.team_id == 10)
print(my_team)


###Atrtibutes of a player object#####
#print("\nMy Roster:")
#for player in my_team.roster:
#    print(dir(player))  
#    break  
#####################

print("\nMy Roster (key metrics)")
header = f"{'Name':24} {'Pos':3} {'NFL':3} {'Proj':>6} {'Own%':>6} {'Start%':>7} {'Injury':>8} {'Slot':>6}"
print(header)
print("-" * len(header))

for p in my_team.roster:
    nfl = getattr(p, "team_abbreviation", getattr(p, "proTeam", ""))
    proj = getattr(p, "projected_avg_points", None)
    own = getattr(p, "percent_owned", None)
    started = getattr(p, "percent_started", None)
    inj = getattr(p, "injuryStatus", "")
    slot = getattr(p, "lineupSlot", "")

    print(f"{p.name:24} {p.position:3} {str(nfl):3} {proj if proj is not None else 0:6.2f} "
          f"{(own or 0):6.1f} {(started or 0):7.1f} {inj:8} {slot:6}")


