from dotenv import load_dotenv
from google import genai
from google.genai import types
from saglayici import GeminiSaglayici

load_dotenv()
saglayici = GeminiSaglayici(genai.Client(), "gemini-3.5-flash-lite", types.GenerateContentConfig())
print(saglayici.cevap_uret([{"rol": "kullanici", "metin": "Merhaba, nasılsın?"}]))