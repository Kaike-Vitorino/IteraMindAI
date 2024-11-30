import requests

BASE_URL = "http://127.0.0.1:5000"

generate_payload = {"prompt": "Escreva uma função Python que calcula a média de uma lista."}
response = requests.post(f"{BASE_URL}/generate", json=generate_payload)
print("Response /generate:", response.json())

criticize_payload = {"code": "def average(lst): return sum(lst) / len(lst)"}
response = requests.post(f"{BASE_URL}/criticize", json=criticize_payload)
print("Response /criticize:", response.json())

integrate_payload = {
    "code": "def average(lst): return sum(lst) / len(lst)",
    "feedback": "Adicione uma verificação para listas vazias."
}
response = requests.post(f"{BASE_URL}/integrate", json=integrate_payload)
print("Response /integrate:", response.json())
