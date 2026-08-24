import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith.wrappers import wrap_openai
from openai import OpenAI

load_dotenv()

langsmith_client = Client()
openai_client = wrap_openai(OpenAI())

PROJECT_NAME = "school-orders-extraction-eval"
os.environ["LANGCHAIN_PROJECT"] = PROJECT_NAME

print("LangSmith connected:", langsmith_client)