import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

client = Client()

DATASET_NAME = "school-orders-extraction"
DATASET_DESCRIPTION = (
    "Raw WhatsApp-style school book order messages paired with the correct "
    "structured extraction (school, class, title, qty). Mirrors the "
    "production extraction task in the school-book-order-bot n8n workflow."
)

examples = [
    {
        "inputs": {"raw_message": "Sai Vidyanikethan, 6th class, white long notebook 500 nos"},
        "outputs": {"items": [
            {"school": "Sai Vidyanikethan", "class": "6th", "title": "White Long Notebook", "qty": 500}
        ]},
        "metadata": {"category": "simple_single_item", "qty_source": "real"},
    },
    {
        "inputs": {"raw_message": "Sai Vidyanikethan 6th — telugu 40 sets, english 40 sets, science 40 sets, social 40 sets"},
        "outputs": {"items": [
            {"school": "Sai Vidyanikethan", "class": "6th", "title": "Telugu", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "6th", "title": "English", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "6th", "title": "Science", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "6th", "title": "Social", "qty": 40},
        ]},
        "metadata": {"category": "multi_item_same_class", "qty_source": "real"},
    },
    {
        "inputs": {"raw_message": "8th class sai vidyanikethan — physics record 40, biology record 40, social map pointing 40"},
        "outputs": {"items": [
            {"school": "Sai Vidyanikethan", "class": "8th", "title": "Physics Record", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "8th", "title": "Biology Record", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "8th", "title": "Social Map Pointing", "qty": 40},
        ]},
        "metadata": {"category": "multi_item_records", "qty_source": "real"},
    },
    {
        "inputs": {"raw_message": "NJR EM school class 3 need 30 hindi bharathi-3"},
        "outputs": {"items": [
            {"school": "NJR EM School", "class": "CLASS 3", "title": "Hindi Bharathi-3", "qty": 30}
        ]},
        "metadata": {"category": "simple_single_item", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "njr nursery — 15 telugu aksharamala, 15 alphabet capital letters, 15 numbers 1-100 & nursery rhymes"},
        "outputs": {"items": [
            {"school": "NJR EM School", "class": "NURSERY", "title": "Telugu Aksharamala", "qty": 15},
            {"school": "NJR EM School", "class": "NURSERY", "title": "Alphabet Capital Letters", "qty": 15},
            {"school": "NJR EM School", "class": "NURSERY", "title": "Numbers 1-100 & Nursery Rhymes", "qty": 15},
        ]},
        "metadata": {"category": "multi_item", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "bramharshi class 2 — 25 techno semester series 1&2, 25 telugu bharathi-2 & work book, 25 english work book-2"},
        "outputs": {"items": [
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 2", "title": "Techno Semester Series 1 & 2", "qty": 25},
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 2", "title": "Telugu Bharathi-2 & Work Book", "qty": 25},
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 2", "title": "English Work Book-2", "qty": 25},
        ]},
        "metadata": {"category": "multi_item", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "bramharshi vidya mandr clas 6 — 20 map pointing n science drawing6, 20 shirdi study matrials for ap govt 6"},
        "outputs": {"items": [
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 6", "title": "Map Pointing and Science Drawing-6", "qty": 20},
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 6", "title": "Shirdi Study Materials for A.P. Govt.-6", "qty": 20},
        ]},
        "metadata": {"category": "messy_typo", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "class 10 njr - 50 study materials, 50 map pointing & science drawing"},
        "outputs": {"items": [
            {"school": "NJR EM School", "class": "CLASS 10", "title": "Study Materials", "qty": 50},
            {"school": "NJR EM School", "class": "CLASS 10", "title": "Map Pointing & Science Drawing", "qty": 50},
        ]},
        "metadata": {"category": "photo_caption_fragment", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "class 5 — 20 hindi bharathi-5, 20 school diary-1, 20 slate-1"},
        "outputs": {"items": [
            {"school": None, "class": "CLASS 5", "title": "Hindi Bharathi-5", "qty": 20},
            {"school": None, "class": "CLASS 5", "title": "School Diary-1", "qty": 20},
            {"school": None, "class": "CLASS 5", "title": "Slate-1", "qty": 20},
        ]},
        "metadata": {"category": "missing_school", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "njr class 1 — 18 sets of crown maths b/r-1, b/r-2, ruled-5, d/r-1"},
        "outputs": {"items": [
            {"school": "NJR EM School", "class": "CLASS 1", "title": "Crown Maths B/R-1, B/R-2, Ruled-5, D/R-1", "qty": 18}
        ]},
        "metadata": {"category": "ambiguous_bundle", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "sai vidyanikethan — 9th telugu 40 sets, 9th hindi 40 sets, 7th telugu 40 sets"},
        "outputs": {"items": [
            {"school": "Sai Vidyanikethan", "class": "9th", "title": "Telugu", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "9th", "title": "Hindi", "qty": 40},
            {"school": "Sai Vidyanikethan", "class": "7th", "title": "Telugu", "qty": 40},
        ]},
        "metadata": {"category": "multi_class", "qty_source": "real"},
    },
    {
        "inputs": {"raw_message": "bvm class 9 — 22 ap govt text books-9, 22 study materials for ap govt-9"},
        "outputs": {"items": [
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 9", "title": "A.P. Government Text Books-9", "qty": 22},
            {"school": "Bramharshi Vidya Mandir", "class": "CLASS 9", "title": "Study Materials for A.P. Govt.-9", "qty": 22},
        ]},
        "metadata": {"category": "abbreviated_school_name", "qty_source": "synthetic"},
    },
    {
        "inputs": {"raw_message": "njr class 6 — study materials, map pointing & science drawing needed"},
        "outputs": {"items": [
            {"school": "NJR EM School", "class": "CLASS 6", "title": "Study Materials", "qty": None},
            {"school": "NJR EM School", "class": "CLASS 6", "title": "Map Pointing & Science Drawing", "qty": None},
        ]},
        "metadata": {"category": "no_quantity", "qty_source": "synthetic"},
    },
]

existing = list(client.list_datasets(dataset_name=DATASET_NAME))
if existing:
    dataset = existing[0]
    print(f"Using existing dataset: {dataset.id}")
else:
    dataset = client.create_dataset(dataset_name=DATASET_NAME, description=DATASET_DESCRIPTION)
    print(f"Created new dataset: {dataset.id}")

client.create_examples(
    inputs=[ex["inputs"] for ex in examples],
    outputs=[ex["outputs"] for ex in examples],
    metadata=[ex["metadata"] for ex in examples],
    dataset_id=dataset.id,
)

print(f"Uploaded {len(examples)} examples to '{DATASET_NAME}'.")