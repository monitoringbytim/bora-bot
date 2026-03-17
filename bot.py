import requests
import os

# GitHub Secrets에서 정보를 가져오도록 수정 (보안을 위해)
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SYMBOL = "BORA_USDT"
DEPTH_PERCENT = 0.02

def get_depth():
    url = f"https://api.gateio.ws/api/v4/spot/order_book?currency_pair={SYMBOL}&limit=1000"
    response = requests.get(url).json()
    current_price = float(response['asks'][0][0])
    
    lower_bound = current_price * (1 - DEPTH_PERCENT)
    bid_usd_depth = sum(float(price) * float(qty) for price, qty in response['bids'] if float(price) >= lower_bound)

    upper_bound = current_price * (1 + DEPTH_PERCENT)
    ask_usd_depth = sum(float(price) * float(qty) for price, qty in response['asks'] if float(price) <= upper_bound)

    return current_price, bid_usd_depth, ask_usd_depth

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    requests.get(url, params=params)

price, b_usd, a_usd = get_depth()
total_depth = b_usd + a_usd

condition_1 = (a_usd <= 5000) or (b_usd <= 5000)
condition_2 = (total_depth <= 15000)

if condition_1 or condition_2:
    reason = "⚠️ 유동성 부족 감지!\n"
    msg = (f"‼️ [BORA 알림]\n{reason}\n📍 현재가: ${price}\n"
           f"💰 +2%: ${round(a_usd, 0):,}\n💰 -2%: ${round(b_usd, 0):,}\n"
           f"📊 합계: ${round(total_depth, 0):,}")
    send_telegram(msg)
