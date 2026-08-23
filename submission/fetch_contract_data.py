import requests
import json

url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

payload = {
    "filters": {
        "award_type_codes": ["A", "B", "C", "D"],
        "naics_codes": ["336350", "336330", "336310", "336399"],
        "time_period": [{"start_date": "2023-01-01", "end_date": "2026-08-21"}]
    },
    "fields": [
        "Award ID", "Recipient Name", "Award Amount",
        "Awarding Agency", "Start Date", "End Date", "Description"
    ],
    "sort": "Award Amount",
    "order": "desc",
    "page": 1,
    "limit": 20
}

response = requests.post(url, json=payload)
response.raise_for_status()
data = response.json()

with open("raw_contract_awards.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Pulled {len(data.get('results', []))} awards")
print(json.dumps(data.get("results", [])[:2], indent=2))