import os

from dotenv import load_dotenv
from langsmith import traceable

load_dotenv()

project = os.getenv("LANGSMITH_PROJECT")

print("Project:", project)
print("Workspace configured:", bool(os.getenv("LANGSMITH_WORKSPACE_ID")))


@traceable(project_name=project)
def test_function():
    return "LangSmith trace test successful"


try:
    result = test_function()
    print("Trace test: SUCCESS")
    print("Result:", result)

except Exception as e:
    print("Trace test: FAILED")
    print(type(e).__name__)
    print(e)