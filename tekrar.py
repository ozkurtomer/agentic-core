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
    description="İki sayı üzerinde toplama, çıkarma, çarpma veya bölme işlemi yapar. Bu dört işlemden birini gerektiren hesaplamalarda kendin hesaplamak yerine bu aracı kullan.",
    parameters=types.Schema(
        type="OBJECT",
        properties={
            "a": types.Schema(type="NUMBER", description="Birinci sayı"),
            "b": types.Schema(type="NUMBER", description="İkinci sayı"),
            "islem": types.Schema(
                type="STRING",
                enum=["topla", "cikar", "carp", "bol"],
                description="Yapılacak işlem türü"
            ),
        },
        required=["a", "b", "islem"],
    ),
)

araclar = types.Tool(function_declarations=[hesapla_tanimi])

config = types.GenerateContentConfig(
    system_instruction="Sen yardımcı bir asistansın. Cevaplarında Markdown veya LaTeX kullanma, sadece düz metin yaz.",
    tools=[araclar],
)

soru = input("Soru: ")

gecmis = [
    types.Content(role="user", parts=[types.Part(text=soru)])
]

sayac = 0
while sayac < 10:
    sayac += 1

    response = client.models.generate_content(
            model=MODEL,
            contents=gecmis,
            config=config,
    )

    gecmis.append(response.candidates[0].content)

    if not response.function_calls:
            print("Final cevap:", response.text)
            bitti = True
            break
    
    parcalar = []
    for cagri in response.function_calls:
        print(f"[Adım {sayac}] Araç: {cagri.name} {cagri.args}")
        sonuc = hesapla(**cagri.args)
        print(f"[Adım {sayac}] Sonuç: {sonuc}")

        parcalar.append(types.Part.from_function_response(
            name=cagri.name,
            response={"sonuc": sonuc},
        ))

    gecmis.append(types.Content(role="user", parts=parcalar))

if not bitti:
    print("Uyarı: Adım limitine ulaşıldı, ajan görevi tamamlayamadı.")