from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()
MODEL = "gemini-3.1-flash-lite"

def hesapla(a, b, islem):
    if islem == "topla":
        return a + b
    elif islem == "cikar":
        return a - b
    elif islem == "carp":
        return a * b
    elif islem == "bol":
        if b == 0:
            return "Hata: Sıfıra bölünemez"
        return a / b
    else:
        return f"Hata: Bilinmeyen işlem '{islem}'"

hesapla_tanimi = types.FunctionDeclaration(
    name="hesapla",
    description="İki sayı üzerinde dört işlemden birini yapar. Kullanıcı bir hesaplama istediğinde kendin hesaplamak yerine her zaman bu aracı kullan.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "a": types.Schema(type="NUMBER", description="Birinci sayı"),
            "b": types.Schema(type="NUMBER", description="İkinci sayı"),
            "islem": types.Schema(
                type="STRING",
                enum=["topla", "cikar", "carp", "bol"],
                description="Yapılacak işlem",
            ),
        },
        required=["a", "b", "islem"],
    ),
)

araclar = types.Tool(function_declarations=[hesapla_tanimi])

config = types.GenerateContentConfig(
    system_instruction="Sen yardımcı bir asistansın.",
    tools=[araclar],
)

gecmis = [
    types.Content(role="user", parts=[types.Part(text="1234 ile 5678'i çarpar mısın?")])
]

response = client.models.generate_content(
    model=MODEL,
    contents=gecmis,
    config=config,
)

cagri = response.function_calls[0]
print("Model şunu istiyor:", cagri.name, cagri.args)

sonuc = hesapla(**cagri.args)
print("Aracın sonucu:", sonuc)

gecmis.append(response.candidates[0].content)

gecmis.append(
    types.Content(
        role="user",
        parts=[types.Part.from_function_response(
            name=cagri.name,
            response={"sonuc": sonuc},
        )],
    )
)

response2 = client.models.generate_content(
    model=MODEL,
    contents=gecmis,
    config=config,
)

print("Final cevap:", response2.text)