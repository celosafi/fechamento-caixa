from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/ocr', methods=['POST'])
def ocr():
    import anthropic, json, re
    data = request.json
    image_b64 = data.get('image')
    media_type = data.get('media_type', 'image/jpeg')

    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
                {"type": "text", "text": """Esta é uma filipeta de fechamento do sistema Eye (eye.com.br).
Extraia EXATAMENTE os seguintes valores numéricos.
Use ponto decimal, sem R$, sem pontos de milhar.

Retorne SOMENTE JSON válido sem markdown:
{
  "caixa": null,
  "dinheiro": 0,
  "debito": 0,
  "credito": 0,
  "pix": 0,
  "total": 0,
  "liberacao_tag": 0,
  "tag_devolvida": 0,
  "resgate_saldo": 0,
  "confianca": "alta"
}

Onde encontrar cada campo:
- dinheiro: valor na linha "Dinheiro" do Resumo do caixa
- debito: valor em "Total Débito"
- credito: valor em "Total Crédito"
- pix: valor em "PIX"
- total: valor em "Total" (linha destacada)
- liberacao_tag: valor em "Liberacao de TAG" na seção Conferência
- tag_devolvida: valor em "Tag devolvida" na seção Conferência
- resgate_saldo: valor em "Resgate de saldo" na seção Conferência
- caixa: número do caixa no rodapé
"""}
            ]
        }]
    )

    txt = message.content[0].text
    json_match = re.search(r'\{[\s\S]*\}', txt)
    if not json_match:
        return jsonify({"error": "JSON não encontrado", "raw": txt}), 500

    clean = json_match.group(0)
    try:
        result = json.loads(clean)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Erro JSON: {str(e)}", "raw": txt}), 500

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
