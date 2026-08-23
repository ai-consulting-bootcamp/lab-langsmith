import json

with open("raw_contract_awards.json", encoding="utf-8") as f:
    raw = json.load(f)["results"]

dataset_examples = []
for award in raw[:15]:
    input_text = (
        f"Contract {award['Award ID']} awarded to {award['Recipient Name']} "
        f"by {award['Awarding Agency']} for ${award['Award Amount']:,.2f}. "
        f"Description: {award['Description']}"
    )
    dataset_examples.append({
        "input": {"contract_notice": input_text},
        "output": {
            "vendor_name": award["Recipient Name"],
            "award_amount": award["Award Amount"],
            "award_id": award["Award ID"]
        },
        "metadata": {
            "awarding_agency": award["Awarding Agency"],
            "start_date": award["Start Date"]
        }
    })

with open("dataset_examples.json", "w", encoding="utf-8") as f:
    json.dump(dataset_examples, f, indent=2)

print(f"Structured {len(dataset_examples)} examples")
print(json.dumps(dataset_examples[0], indent=2))