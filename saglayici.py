from dataclasses import dataclass, field
from google.genai import types
from google.genai import errors

import time

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

GECICI_HATALAR = [429, 503]


class GeminiSaglayici:
    def __init__(self, client, model, config):
        self.client = client
        self.model = model
        self.config = config

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