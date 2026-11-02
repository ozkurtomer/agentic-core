from saglayici import OllamaSaglayici

araclar = [
    {
        "type": "function",
        "function": {
            "name": "hesapla",
            "description": "İki sayı üzerinde dört işlem yapar.",
            "parameters": {
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
    }
]

s = OllamaSaglayici("llama3.1:8b", araclar=araclar)
cevap = s.cevap_uret([{"rol": "kullanici", "metin": "1234 ile 5678'i çarp"}])
print(cevap.metin)
print(cevap.arac_cagrilari)