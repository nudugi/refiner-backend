from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

# 환경변수 로드
load_dotenv()

# OpenAI 클라이언트
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Flask 앱 설정
app = Flask(__name__)
CORS(app)

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

당신은 전문적인 미술 평론가이자 전시기획자입니다. 제공된 정보를 바탕으로
심도 깊고 상세한 작가노트, 전시 서문, 작품 설명을 작성해 주세요.
각 섹션은 독립적인 문단으로 구성하며, 독자들이 예술가의 의도와 작품 세계를 깊이 이해할 수 있도록
풍부한 내용을 담아주십시오. 결과물은 아래 형식으로 명확히 구분해주세요:

작가노트:
[내용]

전시 서문:
[내용]

작품 설명:
[내용]
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 전문적인 미술 평론가이자 전시기획자입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7,
            )

            content = response.choices[0].message.content.strip()

            # 간단한 파싱
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

            prompt = f"""사용자 입력:
{text}

이 글을 {style} 형식으로 감성적이고 문학적으로 재작성하세요.
- 문맥을 확장하거나 요약하여 통일된 주제를 가진 글로 만드세요.
- 감성적이고 예술적인 표현을 사용하세요.
- 자연스러운 시작과 끝을 구성하세요.
"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 감성적이고 문학적인 작가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.85,
            )

            result = response.choices[0].message.content.strip()
            return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
