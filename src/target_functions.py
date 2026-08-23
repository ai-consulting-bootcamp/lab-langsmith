from dotenv import load_dotenv
from langsmith import traceable
from langsmith.wrappers import wrap_openai
from openai import OpenAI

# 1. Load environment and initialize wrapped client
load_dotenv()
openai_client = wrap_openai(OpenAI())

# 2. Define the Target Function with the @traceable decorator
@traceable(name="news-classifier-target")
def target_classifier(inputs: dict) -> dict:
    """
    Target function to classify news articles into one of four categories.
    
    Parameters:
    - inputs (dict): A dictionary containing the key "question", which holds 
                     the prompt and the raw news article text.
                     
    Returns:
    - dict: A dictionary containing the key "expected_output" with the predicted 
            category (e.g., 'World', 'Sports', 'Business', 'Sci/Tech'). Named
            "expected_output" to match the dataset's reference output schema,
            so exact_match_evaluator can compare both sides using the same key.
    """
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0, # Deterministic output for consistent evaluation
            max_tokens=10,   # Keep it short; we only need the category name
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert news classifier. Classify the user's text into "
                        "exactly one of these categories: World, Sports, Business, Sci/Tech. "
                        "Reply ONLY with the exact category name. Do not add any punctuation, "
                        "explanation, or extra text."
                    )
                },
                {
                    "role": "user", 
                    "content": inputs.get("question", "")
                }
            ]
        )
        
        # Extract the text and strip any accidental whitespace
        predicted_category = response.choices[0].message.content.strip()
        return {"expected_output": predicted_category}
        
    except Exception as e:
        # Graceful error handling to prevent the entire evaluation suite from crashing
        print(f"[!] API Error: {str(e)}")
        return {"expected_output": "Error", "error_details": str(e)}

# 3. Test block for 3 examples
def main():
    test_inputs = [
        {"question": "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: Phelps, Thorpe Advance in 200 Freestyle. Michael Phelps took care of qualifying for the Olympic 200-meter freestyle semifinals."},
        {"question": "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: Oil and Economy Cloud Stocks' Outlook. Soaring crude prices plus worries about the economy are expected to hang over the stock market."},
        {"question": "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: Palestinians in Israeli Jails Start Hunger Strike. Thousands of Palestinian prisoners in Israeli jails began a hunger strike for better conditions."}
    ]
    
    print("[+] Testing target_classifier on 3 examples...\n")
    for i, example in enumerate(test_inputs, 1):
        result = target_classifier(example)
        
        # Pull the string manipulation outside of the f-string
        prefix_to_remove = "Classify the following article text into one of these categories: World, Sports, Business, Sci/Tech.\n\nText: "
        clean_input = example['question'].replace(prefix_to_remove, '')[:60]
        
        print(f"Test {i}:")
        print(f"  Input  : {clean_input}...")
        print(f"  Output : {result['expected_output']}\n")

if __name__ == "__main__":
    main()