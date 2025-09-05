import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from espn_api.football import League
import datetime

# Load .env 
load_dotenv(find_dotenv(), override=True)

def must_get(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing env var: {name}. Add it to your .env file.")
    return v

LEAGUE_ID = int(must_get("LEAGUE_ID"))
YEAR = int(must_get("YEAR"))
ESPN_S2 = must_get("ESPN_S2")           
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


###Atrtibutes of a player object#####

#print("\nMy Roster:")
#for player in my_team.roster:
#    print(dir(player))  
#    break  

#####################

### All Attributes for defined player on my_team ####
p = my_team.roster[0] # 0 = puka
attrs = {attr: getattr(p, attr) for attr in dir(p) if not attr.startswith("_")and attr not in ["stats", "schedule"]}
df = pd.DataFrame(list(attrs.items()), columns=["Attribute", "Value"])
print(df)

####

### Compare Ownership ###

def top_available_by_ownership(league, positions=None, size_per_pos = 250, min_owned=50.0, top_n=25):
    if positions is None: 
        positions = ["QB", "RB", "WR", "TE", "K", "D/ST"]

    by_id = {}
    for pos in positions:
        for p in league.free_agents(size=size_per_pos, position=pos):
            pid = getattr(p, "playerId", None)
            if pid is None: 
                continue
            owned = getattr(p, "percent_owned", 0.0) or 0.0
            if pid not in by_id or owned > by_id[pid]["Owned%"]:
                by_id[pid] = {
                    "PlayerID": pid,
                    "Name": p.name,
                    "Pos": p.position,
                    "NFL": getattr(p, "team_abbreviation", getattr(p, "proTeam", "")),
                    "Owned%": round(owned, 2),
                    "Started%": round(getattr(p, "percent_started", 0.0) or 0.0, 2),
                    "ProjAvg": round(getattr(p, "projected_avg_points", 0.0) or 0.0, 2),
                    "ProjTotal": round(getattr(p, "projected_total_points", 0.0) or 0.0, 2),
                    "Injury": getattr(p, "injuryStatus", ""),
                    "Bye": getattr(p, "bye_week", getattr(p, "byeWeek", "")),
                }

    df = pd.DataFrame(by_id.values())
    if df.empty:
        return df

    df = df[df["Owned%"] >= min_owned].sort_values(["Owned%", "ProjAvg"], ascending=[False, False])
    return df.head(top_n).reset_index(drop=True)

# Example usage:
fa_df = top_available_by_ownership(league, min_owned=40.0, top_n=30)
print(fa_df.to_string(index=False))

#####

### Txn History (weekly) ###
today = datetime.datetime.now()
week_ago = today - datetime.timedelta(days=7)

rows = []
for t in league.transactions():
    # skip if no date
    if t.date is None:
        continue

    # convert ms → datetime
    tx_date = datetime.datetime.fromtimestamp(t.date / 1000)

    if tx_date >= week_ago:
        rows.append({
            "Date": tx_date,
            "Type": t.type,
            "Team": t.team.team_name if t.team else None,
            "Player": getattr(t, "playerName", None)
        })

txns_df = pd.DataFrame(rows)
txns_df.groupby("Team").size().sort_values(ascending=False)
summary = txns_df.groupby("Team").size().sort_values(ascending=False)

print("\n=== Transaction History (This Week) ===\n")
print(summary.to_string())

#####

####
print("\n", my_team, "(key metrics)")
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
####

#Change to who im playing
Weekly_team = next(t for t in league.teams if t.team_id == 3)

print("\n", Weekly_team,"(key metrics)")
header = f"{'Name':24} {'Pos':3} {'NFL':3} {'Proj':>6} {'Own%':>6} {'Start%':>7} {'Injury':>8} {'Slot':>6}"
print(header)
print("-" * len(header))

for p in Weekly_team.roster:
    nfl = getattr(p, "team_abbreviation", getattr(p, "proTeam", ""))
    proj = getattr(p, "projected_avg_points", None)
    own = getattr(p, "percent_owned", None)
    started = getattr(p, "percent_started", None)
    inj = getattr(p, "injuryStatus", "")
    slot = getattr(p, "lineupSlot", "")

    print(f"{p.name:24} {p.position:3} {str(nfl):3} {proj if proj is not None else 0:6.2f} "
          f"{(own or 0):6.1f} {(started or 0):7.1f} {inj:8} {slot:6}")
####



