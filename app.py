from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import requests
import base64

# OpenAI 클라이언트
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Flask
app = Flask(__name__)
CORS(app)

# Refiner endpoint
@app.route('/refine', methods=['POST'])
def refine_text():
    data = request.get_json()
    style = data.get("style", "essay")

    try:
        if style == "작가노트 & 전시 서문":
            exhibition_title = data.get('exhibition_title', '')
            exhibition_theme = data.get('exhibition_theme', '')
            artist_name = data.get('artist_name', '')
            work_description = data.get('work_description', '')
            exhibition_intent = data.get('exhibition_intent', '')
            additional_info = data.get('additional_info', '')

            prompt = f"""전시 제목: {exhibition_title}
전시 주제: {exhibition_theme}
작가 이름: {artist_name}
작품 설명: {work_description}
전시 의도: {exhibition_intent}
추가 정보: {additional_info}

당신은 전문적인 미술 평론가이자 전시기획자입니다.
심도 깊고 상세한 작가노트, 전시 서문, 작품 설명을 작성하세요.
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "전문 미술 평론가 및 전시기획자"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            content = response.choices[0].message.content.strip()
            artist_note = content.split("작가노트:")[1].split("전시 서문:")[0].strip() if "작가노트:" in content else ""
            exhibition_preface = content.split("전시 서문:")[1].split("작품 설명:")[0].strip() if "전시 서문:" in content else ""
            work_explanation = content.split("작품 설명:")[1].strip() if "작품 설명:" in content else ""

            result = {
                "artist_note": artist_note,
                "exhibition_preface": exhibition_preface,
                "work_explanation": work_explanation
            }
            return jsonify(result)

        else:
            text = data.get("text", "")
            if not text.strip():
                return jsonify({"error": "텍스트가 비어있습니다."}), 400

            prompt = f"""사용자 입력: {text}
이 글을 {style} 형식으로 감성적, 문학적으로 재작성하세요.
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "감성적이고 문학적인 작가"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.85,
            )

            result = response.choices[0].message.content.strip()
            return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Toss 결제 성공/실패
@app.route('/api/payment/success')
def payment_success():
    return "결제 성공! (테스트)"

@app.route('/api/payment/fail')
def payment_fail():
    return "결제 실패! (테스트)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
