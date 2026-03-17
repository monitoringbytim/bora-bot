import requests
import os

# 금고에서 정보 가져오기
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SYMBOL = "BORA_USDT"

def get_depth():
    url = f"https://api.gateio.ws/api/v4/spot/order_book?currency_pair={SYMBOL}&limit=1000"
    response = requests.get(url).json()
    current_price = float(response['asks'][0][0])
    
    # +2%, -2% 구간 계산 (테스트용이므로 수치만 가져옴)
    bid_usd = sum(float(p) * float(q) for p, q in response['bids'] if float(p) >= current_price * 0.98)
    ask_usd = sum(float(p) * float(q) for p, q in response['asks'] if float(p) <= current_price * 1.02)
    return current_price, bid_usd, ask_usd

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    requests.get(url, params=params)

# --- 강제 실행 구간 ---
try:
    price, b_usd, a_usd = get_depth()
    
    # 조건문(if) 없이 무조건 메시지 생성
    test_msg = (f"✅ [GitHub Actions 연결 성공!]\n\n"
                f"📍 현재가: ${price}\n"
                f"💰 +2% Depth: ${round(a_usd, 0):,}\n"
                f"💰 -2% Depth: ${round(b_usd, 0):,}\n"
                f"🚀 배달 주소: {CHAT_ID}\n"
                f"⏰ 테스트 시각: {os.popen('date').read()}") # 서버 시간 확인용
    
    send_telegram(test_msg)
    print("메시지 전송 명령 완료!")
except Exception as e:
    print(f"오류 발생: {e}")
