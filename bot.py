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
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

print("🚨 BORA 유동성 위기 감시 모드 가동 중...")

while True:
    try:
        price, b_usd, a_usd = get_depth()
        total_depth = b_usd + a_usd

        # 알림 조건 체크
        # 조건 1: 어느 한쪽이라도 5,000불 이하
        condition_1 = (a_usd <= 5000) or (b_usd <= 5000)
        # 조건 2: 양쪽 합산 15,000불 이하
        condition_2 = (total_depth <= 15000)

        if condition_1 or condition_2:
            reason = ""
            if condition_1: reason += "⚠️ 한쪽 유동성 5,000$ 미만 발생!\n"
            if condition_2: reason += "📉 합산 유동성 15,000$ 미만 발생!\n"

            msg = (f"‼️ [BORA 유동성 경고]\n\n"
                   f"{reason}\n"
                   f"📍 현재가: ${price}\n"
                   f"💰 +2% Depth: ${round(a_usd, 2):,}\n"
                   f"💰 -2% Depth: ${round(b_usd, 2):,}\n"
                   f"📊 합산 유동성: ${round(total_depth, 2):,}\n"
                   f"⏰ 발생시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")

            send_telegram(msg)
            print(f"🚨 경고 전송 완료: {time.strftime('%H:%M:%S')}")

            # 알림 후 10분간 휴식 (너무 자주 울리지 않게)
            time.sleep(600)
        else:
            # 정상일 때는 화면에 로그만 찍고 1분 뒤 다시 체크
            print(f"정상 가동 중... 합계: ${round(total_depth, 0)} ({time.strftime('%H:%M:%S')})")
            time.sleep(60)

    except Exception as e:
        print(f"오류 발생: {e}")
        time.sleep(10) # 오류 시 10초 후 재시도
