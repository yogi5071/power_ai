from google import genai
from config.settings import Settings

Settings.validate()

client = genai.Client(
    api_key=Settings.GEMINI_API_KEY
)

print("=" * 60)
print("Available Models")
print("=" * 60)

for model in client.models.list():
    print(model.name)