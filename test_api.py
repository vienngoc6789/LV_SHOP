import os
from google import genai

key = os.getenv("GEMINI_API_KEY")

print("API KEY:", "OK" if key else "MISSING")

client = genai.Client()

models = client.models.list()

print("\nMODEL LIST:")
for model in models:
    print(model.name)