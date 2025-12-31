import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

print("Testando Gemini Flash 3.0...")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3-flash-preview")

test_prompt = """Voce e um revisor de transcricoes. Corrija o texto abaixo:

"ola pessoal, entao, eeeh, hoje vamos falar sobre, hum, enxaqueca, ne? A enxaqueca e uma doenca, assim, muito comum."

Corrija removendo hesitacoes e melhorando a pontuacao."""

print("\nEnviando prompt para Gemini...")
response = model.generate_content(test_prompt)

print("\nResposta do Gemini:")
print("-" * 60)
print(response.text)
print("-" * 60)
print("\nGemini Flash 3.0 funcionando corretamente!")
