from dataclasses import dataclass, field
from google.genai import types
from google.genai import errors

import time
import ollama

@dataclass
class AracCagrisi:
    ad: str
    parametreler: dict

@dataclass
class ModelCevabi:
    metin: str | None = None
    arac_cagrilari: list = field(default_factory=list)
    ham: object = None

def gemini_cevabini_cevir(response):
    arac_cagrilari = []

    if response.function_calls:
        for function_call in response.function_calls:
            arac_cagrilari.append(AracCagrisi(
                ad=function_call.name,
                parametreler=dict(function_call.args),
            ))

    return ModelCevabi(
        metin=response.text if not response.function_calls else None,
        arac_cagrilari=arac_cagrilari,
        ham=response.candidates[0].content,
    )

def ollama_cevabini_cevir(cevap):
    arac_cagrilari = []

    if cevap.message.tool_calls:
        for tool_call in cevap.message.tool_calls:
            arac_cagrilari.append(AracCagrisi(
                ad=tool_call.function.name,
                parametreler=tool_call.function.arguments,

            ))

    return ModelCevabi(
        metin=cevap.message.content if not cevap.message.tool_calls else None,
        arac_cagrilari=arac_cagrilari,
        ham=cevap.message,)

def mesajlari_ollama_formatina_cevir(mesajlar):
    sonuc = []

    for mesaj in mesajlar:

        if mesaj["rol"] == "kullanici":
            sonuc.append({"role": "user", "content": mesaj["metin"]})

        elif mesaj["rol"] == "model":
            sonuc.append(mesaj["cevap"].ham)

        elif mesaj["rol"] == "arac":
            for kayit in mesaj["sonuclar"]:
                sonuc.append({
                    "role": "tool",
                    "tool_name": kayit["ad"],
                    "content": str(kayit["sonuc"]),
                })

    return sonuc

def mesajlari_gemini_formatina_cevir(mesajlar):
    icerikler = []

    for mesaj in mesajlar:

        if mesaj["rol"] == "kullanici":
            icerikler.append(types.Content(
                role="user",
                parts=[types.Part(text=mesaj["metin"])],
            ))

        elif mesaj["rol"] == "model":
            icerikler.append(mesaj["cevap"].ham)

        elif mesaj["rol"] == "arac":
            parcalar = []
            for kayit in mesaj["sonuclar"]:
                parcalar.append(types.Part.from_function_response(
                    name=kayit["ad"],
                    response={"sonuc": kayit["sonuc"]},
                ))

            icerikler.append(types.Content(role="user", parts=parcalar))

    return icerikler

def araclari_gemini_formatina_cevir(tanimlar):
    bildirimler = []
    for t in tanimlar:
        bildirimler.append(types.FunctionDeclaration(
            name=t["ad"],
            description=t["aciklama"],
            parameters_json_schema=t["parametreler"],
        ))
    return types.Tool(function_declarations=bildirimler)

def araclari_ollama_formatina_cevir(tanimlar):
    sonuc = []
    for t in tanimlar:
        sonuc.append({
            "type": "function",
            "function": {
                "name": t["ad"],
                "description": t["aciklama"],
                "parameters": t["parametreler"],
            },
        })
    return sonuc

GECICI_HATALAR = [429, 503]

class GeminiSaglayici:
    def __init__(self, client, model, araclar=None, sistem_talimati=None):
        self.client = client
        self.model = model
        self.config = types.GenerateContentConfig(
            system_instruction=sistem_talimati,
            tools=[araclari_gemini_formatina_cevir(araclar)] if araclar else None,
        )

    def cevap_uret(self, mesajlar, deneme_limiti=4):
        icerikler = mesajlari_gemini_formatina_cevir(mesajlar)
        bekleme = 1

        for deneme in range(1, deneme_limiti + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=icerikler,
                    config=self.config,
                )
                return gemini_cevabini_cevir(response)
            except errors.APIError as e:
                if e.code not in GECICI_HATALAR or deneme == deneme_limiti:
                    raise

                print(f"Uyarı: API çağrısı başarısız oldu (durum kodu {e.code}). {bekleme} saniye bekleniyor...")
                time.sleep(bekleme)
                bekleme *= 2

class OllamaSaglayici:
    def __init__(self, model, araclar=None):
        self.model = model
        self.araclar = araclari_ollama_formatina_cevir(araclar) if araclar else None

    def cevap_uret(self, mesajlar):
        ollama_mesajlari = mesajlari_ollama_formatina_cevir(mesajlar)
        cevap = ollama.chat(
            model=self.model,
            messages=ollama_mesajlari,
            tools=self.araclar,
        )
        return ollama_cevabini_cevir(cevap)               