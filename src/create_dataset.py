import os
import json
from datasets import load_dataset

def main():
    print("[+] Loading AG News dataset from Hugging Face...")
    
    # FIXED: Actually using the namespace this time!
    dataset = load_dataset("fancyzhx/ag_news", split="train")

    label_map = {
        0: "World",
        1: "Sports",
        2: "Business",
        3: "Sci/Tech"
    }
    
    DIFFICULTY_OVERRIDES = {
        492: "easy", 493: "medium", 494: "hard", 495: "medium",
        448: "easy", 449: "medium", 450: "hard", 451: "medium",
        0: "easy", 1: "medium", 2: "hard", 3: "medium",
        78: "easy", 79: "easy", 80: "hard", 81: "medium",
    }

    examples = []

    # Your dynamic selection logic!
    for label_id in range(4):
        category_name = label_map[label_id]
        print(f"\n=== Extracting {category_name} ===")
        
        # Find all indices matching this label, grab the first 4
        matches = [i for i, r in enumerate(dataset) if r["label"] == label_id][:4]
        
        for idx in matches:
            row = dataset[idx]
            text_snippet = row["text"][:75].replace("\n", " ")
            print(f"  -> Added {idx}: {text_snippet}...")
            
            examples.append({
                "inputs": {
                    "question": f"Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: {row['text']}"
                },
                "outputs": {
                    "expected_output": category_name
                },
                "metadata": {
                    "source_index": idx,
                    "dataset": "ag_news",
                    "category": category_name,
                    "difficulty": DIFFICULTY_OVERRIDES.get(idx, "medium"),
                }
            })

    os.makedirs("data", exist_ok=True)
    output_path = "data/content_creation_dataset.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2)

    print(f"\n[✓] Created '{output_path}' with {len(examples)} examples.")

if __name__ == "__main__":
    main()