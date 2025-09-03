import sys
print("Python:", sys.version.split()[0])

# if this import works, our venv + package install is healthy
from espn_api.football import League
print("espn_api imported OK")
