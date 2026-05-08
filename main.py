from flask import Flask, request, jsonify, send_from_directory
import os
app = Flask(__name__, static_folder='static')
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')
@app.route('/api/ocr', methods=['POST'])
def ocr():
    import anthropic, base64
    data = request.json
    image_b64 = data.get('image')
    media_type = data.get('media_type', 'image/jpeg')
    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
                {"type": "text", "text": """Filipeta de fechamento sistema Eye. Extraia os valores numéricos.
Retorne SOMENTE JSON válido sem markdown:
{\"caixa\":null,\"dinheiro\":0,\"debito\":0,\"credito\":0,\"pix\":0,\"total\":0,\"liberacao_tag\":0,\"confianca\":\"alta\"}
Use ponto decimal, sem R$ ou pontos de milhar."""}
            ]
        }]
    )
    import json, re
    txt = message.content[0].text
    json_match = re.search(r'\{[\s\S]*\}', txt)
    if not json_match:
        return jsonify({"error": "No JSON found", "raw": txt}), 500
    clean = json_match.group(0)
    try:
        result = json.loads(clean)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"JSON parse failed: {str(e)}", "raw": txt}), 500
    return jsonify(result)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
