from dotenv import load_dotenv
from langsmith import Client
from langchain_openai import ChatOpenAI

load_dotenv()

client = Client()

DATASET_NAME = "TenderAI-Requirement-Evaluation-v1"

model_a = ChatOpenAI(model="gpt-5-mini", temperature=0)
model_b = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

dataset = client.read_dataset(dataset_name=DATASET_NAME)

examples = list(client.list_examples(dataset_id=dataset.id))

def classify(model, requirement):
    prompt = f"""
You are evaluating a tender requirement against a company's known capabilities.

Classify the requirement using ONLY one of these labels:

SUPPORTED
PARTIALLY_SUPPORTED
INSUFFICIENT

Requirement:
{requirement}

Return ONLY the classification label.
"""

    response = model.invoke(prompt)
    return response.content.strip()

results_a = []
results_b = []

for example in examples:

    requirement = example.inputs["requirement"]
    expected = example.outputs["expected_classification"]

    answer_a = classify(model_a, requirement)
    answer_b = classify(model_b, requirement)

    correct_a = answer_a == expected
    correct_b = answer_b == expected

    results_a.append(correct_a)
    results_b.append(correct_b)

    print("\nRequirement:")
    print(requirement)

    print(f"Expected: {expected}")
    print(f"Model A: {answer_a} | Correct: {correct_a}")
    print(f"Model B: {answer_b} | Correct: {correct_b}")

accuracy_a = sum(results_a) / len(results_a) * 100
accuracy_b = sum(results_b) / len(results_b) * 100

print("\n==========================")
print("FINAL RESULTS")
print("==========================")

print(f"\nModel A - gpt-5-mini: {accuracy_a:.1f}% accuracy")
print(f"Model B - gpt-4.1-mini: {accuracy_b:.1f}% accuracy")