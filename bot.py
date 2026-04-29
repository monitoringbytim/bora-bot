import requests
import os
import time

# GitHub Secrets에서 정보 가져오기
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SYMBOL = "BORA_USDT"
DEPTH_PERCENT = 0.02

def get_depth():
    url = f"https://api.gateio.ws/api/v4/spot/order_book?currency_pair={SYMBOL}&limit=1000"
    response = requests.get(url).json()
    
    current_price = float(response['asks'][0][0])
    
    # -2% 구간 매수 물량 합계 (USDT)
    lower_bound = current_price * (1 - DEPTH_PERCENT)
    bid_usd_depth = sum(float(price) * float(qty) for price, qty in response['bids'] if float(price) >= lower_bound)

    # +2% 구간 매도 물량 합계 (USDT)
    upper_bound = current_price * (1 + DEPTH_PERCENT)
    ask_usd_depth = sum(float(price) * float(qty) for price, qty in response['asks'] if float(price) <= upper_bound)

    return current_price, bid_usd_depth, ask_usd_depth

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

# --- 실행 구간 ---
try:
    price, b_usd, a_usd = get_depth()
    total_depth = b_usd + a_usd

    # [요청사항 반영] 알림 조건 수치 수정
    condition_1 = (a_usd <= 5000) or (b_usd <= 5000)  # 한쪽 5,000$ 이하
    condition_2 = (total_depth <= 10000)             # 합산 10,000$ 이하

    # 메시지 제목 설정
    if condition_1 or condition_2:
        header = "🚨 [BORA 유동성 위험 경고]"
        reason = "⚠️ 유동성 부족 상태가 감지되었습니다!\n"
        if condition_1: reason += "- 한쪽 유동성 5,000$ 미만\n"
        if condition_2: reason += "- 합산 유동성 10,000$ 미만\n"
    else:
        header = "📊 [BORA 유동성 정기 보고]"
        reason = "✅ 현재 유동성은 설정 기준치 이상입니다.\n"

    # 메시지 구성 (조건 상관없이 상세 수치는 항상 포함)
    msg = (f"{header}\n\n"
           f"{reason}\n"
           f"📍 현재가: ${price}\n"
           f"💰 +2% Depth: ${round(a_usd, 2):,}\n"
           f"💰 -2% Depth: ${round(b_usd, 2):,}\n"
           f"📊 합산 유동성: ${round(total_depth, 2):,}\n"
           f"--------------------------\n"
           f"⏰ 확인시각(KST): {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # [요청사항 반영] 조건문 없이 '무조건' 전송
    send_telegram(msg)
    print(f"✅ 리포트 전송 완료 ({time.strftime('%H:%M:%S')})")

except Exception as e:
    print(f"오류 발생: {e}")
    exit(1)
