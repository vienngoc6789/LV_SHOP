from google import genai

client = genai.Client(api_key="AIzaSyAogSu_14gq5g45wJS062N2s27Rmr7Fx7c")

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words"
)
print(response.text)