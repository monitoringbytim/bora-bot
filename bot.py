import requests
import os
import time  # 시간 표시를 위해 필요

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

# --- 실행 구간 (GitHub Actions는 1회 실행 방식입니다) ---
try:
    price, b_usd, a_usd = get_depth()
    total_depth = b_usd + a_usd

    # 알림 조건 체크
    condition_1 = (a_usd <= 1500) or (b_usd <= 1500)
    condition_2 = (total_depth <= 5000)

    # 테스트를 원하시면 아래 if 문을 무시하고 무조건 발송하게 코드를 짤 수 있으나, 
    # 일단은 요청하신 조건문 로직을 유지합니다.
    if condition_1 or condition_2:
        reason = ""
        if condition_1: reason += "⚠️ 한쪽 유동성 1,500$ 미만 발생!\n"
        if condition_2: reason += "📉 합산 유동성 5,000$ 미만 발생!\n"

        msg = (f"‼️ [BORA 유동성 경고]\n\n"
               f"{reason}\n"
               f"📍 현재가: ${price}\n"
               f"💰 +2% Depth: ${round(a_usd, 2):,}\n"
               f"💰 -2% Depth: ${round(b_usd, 2):,}\n"
               f"📊 합산 유동성: ${round(total_depth, 2):,}\n"
               f"⏰ 발생시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        send_telegram(msg)
        print(f"🚨 경고 전송 완료 ({time.strftime('%H:%M:%S')})")
    else:
        print(f"✅ 정상 상태: 합계 ${round(total_depth, 0)} (알림 미발송)")

except Exception as e:
    print(f"오류 발생: {e}")
    exit(1) # 오류 발생 시 GitHub Actions에 에러 알림
