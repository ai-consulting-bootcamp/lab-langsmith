from dotenv import load_dotenv
load_dotenv()

from langsmith import Client, wrappers
from openai import OpenAI

client = Client()
print("LangSmith OK, datasets:", [d.name for d in client.list_datasets(limit=5)])

oai = wrappers.wrap_openai(OpenAI())
r = oai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Say hi"}])
print("OpenAI OK:", r.choices[0].message.content)