import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import logging

load_dotenv()
API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

def call_gemini_api(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    params = {"key": API_KEY}

    response = requests.post(url, json=payload, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro na chamada à API do Google Gemini: {response.status_code}, {response.text}")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/infer', methods=['POST'])
def infer():
    data = request.get_json()
    prompt = data.get("prompt")
    logging.info(f"Recebido prompt: {prompt}")
    try:
        response = call_gemini_api(prompt)
        logging.info("Resposta enviada com sucesso.")
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Erro ao processar o prompt: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    prompt = data.get("prompt")
    logging.info(f"Recebido prompt: {prompt}")

    try:
        response = call_gemini_api(f"Escreva um codigo para: {prompt}")
        generated_code = response['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"generated_code": generated_code}), 200
    except Exception as e:
        logging.error(f"Erro no Agente Gerador: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/criticize', methods=['POST'])
@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    prompt = data.get("prompt")
    logging.info(f"Prompt recebido: {prompt}")

    # Simulação de chamada ao Google Gemini (ou API real)
    response = call_gemini_api(f"Gerar código para: {prompt}")
    logging.info(f"Resposta da API: {response}")

    try:
        generated_code = response['candidates'][0]['content']['parts'][0]['text']
        logging.info(f"Código gerado: {generated_code}")
        return jsonify({"response": generated_code}), 200
    except Exception as e:
        logging.error(f"Erro ao processar resposta da API: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/criticize', methods=['POST'])
def criticize_code():
    data = request.get_json()
    code = data.get("code")
    logging.info(f"Código recebido para crítica: {code}")

    # Simulação de chamada ao Google Gemini (ou API real)
    response = call_gemini_api(f"Avaliar e melhorar o seguinte código: {code}")
    logging.info(f"Resposta da API: {response}")

    try:
        feedback = response['candidates'][0]['content']['parts'][0]['text']
        logging.info(f"Feedback gerado: {feedback}")
        return jsonify({"response": feedback}), 200
    except Exception as e:
        logging.error(f"Erro ao processar resposta da API: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
