import ollama

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

soru = input("Soru: ")

cevap = ollama.chat(
    model="llama3.1:8b",
    messages=[{"role": "user", "content": soru}],
    tools=araclar
)

print(cevap)

if cevap.message.tool_calls:
    istek = cevap.message.tool_calls[0]
    print(type(istek.function.arguments["a"]))
