from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client()

MODEL = "gemini-3.1-flash-lite"

gecmis = []

while True:

    soru = input("Sen:")

    if soru == "çık":
        break

    gecmis.append(types.Content(role="user", parts=[types.Part(text=soru)]))

    response = client.models.generate_content(
        model=MODEL,
        contents=gecmis,
        config=types.GenerateContentConfig(
            system_instruction="Sen kısa ve öz cevap veren bir yazılım asistanısın. Cevapların en fazla 3 cümle olsun.",
        )
    )

    gecmis.append(response.candidates[0].content)

    print("Model: " + response.text)
    print(f"[Gönderilen token: {response.usage_metadata.prompt_token_count}]")