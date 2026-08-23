import json
import os
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

EDGE_CASE_DATASET_NAME = "should-cost-contract-extraction-edge-cases"

edge_cases = [
    {
        "input": {"contract_notice": "Contract AWARDED to Precision Drivetrain Systems Inc. by Department of Defense. Description: REPLACEMENT TRANSMISSION HOUSINGS FOR M1 ABRAMS. Award amount not yet disclosed pending final negotiation."},
        "output": {"vendor_name": "Precision Drivetrain Systems Inc.", "award_amount": None, "award_id": None},
        "metadata": {"edge_case_type": "missing_amount_and_id"}
    },
    {
        "input": {"contract_notice": "Contract W91CRB24C0088 awarded jointly to Allison Transmission and BAE Systems Land & Armaments as a teaming arrangement, by Department of Defense, for $47,300,000. Description: HYBRID DRIVE MODULES FOR NEXT-GEN COMBAT VEHICLE."},
        "output": {"vendor_name": "Allison Transmission", "award_amount": 47300000, "award_id": "W91CRB24C0088"},
        "metadata": {"edge_case_type": "multiple_vendors"}
    },
    {
        "input": {"contract_notice": "Contract SPE7M124D0019 awarded to Curtiss-Wright Defense Solutions by Department of Defense for a base value of $12,400,000 with an option year potentially increasing total value to $38,900,000. Description: POWER TRAIN DIAGNOSTIC UNITS."},
        "output": {"vendor_name": "Curtiss-Wright Defense Solutions", "award_amount": 12400000, "award_id": "SPE7M124D0019"},
        "metadata": {"edge_case_type": "multiple_dollar_figures"}
    },
    {
        "input": {"contract_notice": "Contract W56HZV25C0201 awarded to Oshkosh Defense LLC by Department of Defense for approximately $2.3M. Description: SUSPENSION COMPONENTS FOR JLTV FLEET."},
        "output": {"vendor_name": "Oshkosh Defense LLC", "award_amount": 2300000, "award_id": "W56HZV25C0201"},
        "metadata": {"edge_case_type": "abbreviated_currency"}
    },
    {
        "input": {"contract_notice": "Modification to contract W56HZV20C0124, originally awarded to RENK AMERICA LLC, increases total award value by $15,200,000 to support extended production of THOR III hardware."},
        "output": {"vendor_name": "RENK AMERICA LLC", "award_amount": 15200000, "award_id": "W56HZV20C0124"},
        "metadata": {"edge_case_type": "modification_not_new_award"}
    }
]

existing = list(client.list_datasets(dataset_name=EDGE_CASE_DATASET_NAME))
if existing:
    dataset = existing[0]
    print(f"Using existing dataset: {dataset.id}")
else:
    dataset = client.create_dataset(
        dataset_name=EDGE_CASE_DATASET_NAME,
        description=(
            "5 hand-authored hard edge cases for contract field extraction: "
            "missing data, multi-vendor notices, multiple dollar figures, "
            "abbreviated currency, and contract modifications. Built to stress-test "
            "extraction beyond the verbatim-copy task in the main real-data dataset."
        )
    )
    print(f"Created new dataset: {dataset.id}")

client.create_examples(
    inputs=[ex["input"] for ex in edge_cases],
    outputs=[ex["output"] for ex in edge_cases],
    metadata=[ex["metadata"] for ex in edge_cases],
    dataset_id=dataset.id
)

print(f"Uploaded {len(edge_cases)} edge cases")