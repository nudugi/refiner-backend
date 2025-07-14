from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/refine', methods=['POST'])
def refine_text():
    data = request.get_json()
    input_text = data.get('text', '')
    style = data.get('style', 'essay')

    # 나중에 여기서 OpenAI API로 가공할 예정
    refined = f"[{style.upper()} 스타일로 다듬은 결과]\n{input_text.strip()}"

    return jsonify({"result": refined})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
