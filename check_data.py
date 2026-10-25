import json
from pathlib import Path

database_path = Path("data") / "passport_data.json"

with database_path.open("r", encoding="utf-8") as file:
    passport_data = json.load(file)

print("SUCCESS: Passport database loaded.")
print("Available page options:", list(passport_data["fees_2026"].keys()))
print("Available validity options:", list(passport_data["eligibility_rules"].keys()))