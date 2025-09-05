
from flask import Flask, request, jsonify, redirect
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

# Toss 결제 성공 처리
@app.route('/payment/success', methods=['GET'])
def payment_success():
    # 토스에서 GET 파라미터로 결제 정보를 보내줍니다
    payment_key = request.args.get('paymentKey')
    order_id = request.args.get('orderId')
    amount = request.args.get('amount')
    
    if not all([payment_key, order_id, amount]):
        return "결제 정보가 누락되었습니다.", 400
    
    # 실제 운영에서는 여기서 토스 API를 호출해서 결제를 승인해야 합니다
    try:
        # 토스 결제 승인 API 호출
        toss_secret_key = os.environ.get('TOSS_SECRET_KEY')
        if not toss_secret_key:
            return "서버 설정 오류", 500
            
        url = "https://api.tosspayments.com/v1/payments/confirm"
        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{toss_secret_key}:'.encode()).decode()}",
            "Content-Type": "application/json"
        }
        data = {
            "paymentKey": payment_key,
            "amount": int(amount),
            "orderId": order_id
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # 결제 성공 - 프론트엔드로 리다이렉트
            return redirect(f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}?payment=success")
        else:
            return f"결제 승인 실패: {response.text}", 400
            
    except Exception as e:
        return f"결제 처리 중 오류: {str(e)}", 500

# Toss 결제 실패 처리
@app.route('/payment/fail', methods=['GET'])
def payment_fail():
    error_code = request.args.get('code')
    error_message = request.args.get('message')
    
    # 프론트엔드로 리다이렉트하면서 실패 정보 전달
    return redirect(f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}?payment=fail&error={error_message}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
