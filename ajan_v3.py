from pathlib import Path
from saglayici import OllamaSaglayici, GeminiSaglayici
from dotenv import load_dotenv
from google import genai

CALISMA_ALANI = Path("calisma_alani").resolve()
MODEL = "gemini-3.5-flash-lite"

def hesapla(a, b, islem):
    if islem == "topla":
        return a + b
    if islem == "cikar":
        return a - b
    if islem == "carp":
        return a * b
    if islem == "bol":
        if b == 0:
            return "Hata: Sıfıra bölme yapılamaz."
        return a / b
    return f"Hata: Bilinmeyen işlem '{islem}'."


def dosya_oku(yol):
    tam_yol = Path(yol).resolve()
    if not tam_yol.is_relative_to(CALISMA_ALANI):
        return "Hata: Sadece calisma_alani klasöründeki dosyalar okunabilir."
    if not tam_yol.is_file():
        return f"Hata: '{yol}' adında bir dosya bulunamadı."
    return tam_yol.read_text(encoding="utf-8")


ARACLAR = {"hesapla": hesapla, "dosya_oku": dosya_oku}

ARAC_TANIMLARI = [
    {
        "ad": "hesapla",
        "aciklama": "İki sayı üzerinde dört işlem yapar: topla, cikar, carp, bol. Üs alma ve kök gibi işlemleri desteklemez.",
        "parametreler": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Birinci sayı"},
                "b": {"type": "number", "description": "İkinci sayı"},
                "islem": {
                    "type": "string",
                    "enum": ["topla", "cikar", "carp", "bol"],
                    "description": "Yapılacak işlem",
                },
            },
            "required": ["a", "b", "islem"],
        },
    },
    {
        "ad": "dosya_oku",
        "aciklama": "calisma_alani klasöründeki bir metin dosyasını okur ve içeriğini döndürür. Bu klasörün dışındaki dosyaları okuyamaz.",
        "parametreler": {
            "type": "object",
            "properties": {
                "yol": {
                    "type": "string",
                    "description": "Okunacak dosyanın yolu, örn. calisma_alani/notlar.txt",
                },
            },
            "required": ["yol"],
        },
    },
]


def araci_calistir(ad, parametreler):
    if ad not in ARACLAR:
        return f"Hata: '{ad}' adında bir araç yok."
    try:
        return ARACLAR[ad](**parametreler)
    except Exception as e:
        return f"Hata: {e}"


def ajani_calistir(saglayici, soru, adim_limiti=10):
    gecmis = [{"rol": "kullanici", "metin": soru}]

    for adim in range(adim_limiti):
        cevap = saglayici.cevap_uret(gecmis)
        gecmis.append({"rol": "model", "cevap": cevap})

        if not cevap.arac_cagrilari:
            return cevap.metin

        sonuclar = []
        for cagri in cevap.arac_cagrilari:
            sonuc = araci_calistir(cagri.ad, cagri.parametreler)
            sonuclar.append({"ad": cagri.ad, "sonuc": sonuc})
        gecmis.append({"rol": "arac", "sonuclar": sonuclar})

    return "Uyarı: Adım limitine ulaşıldı, ajan görevi tamamlayamadı."


if __name__ == "__main__":
    load_dotenv()
    client = genai.Client()

    saglayici = OllamaSaglayici("qwen2.5:7b", araclar=ARAC_TANIMLARI)
    # saglayici = GeminiSaglayici(client, MODEL, araclar=ARAC_TANIMLARI)

    soru = input("Soru: ")
    print(ajani_calistir(saglayici, soru))