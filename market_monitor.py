import os
import requests
import ccxt
import pandas as pd

# GitHub Secrets에서 등록한 값 불러오기
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 토큰 또는 Chat ID가 설정되지 않았습니다.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"텔레그램 전송 실패: {e}")

def main():
    exchange = ccxt.bybit()
    symbols = ['BTC/USDT', 'XRP/USDT']
    reports = []

    for sym in symbols:
        # 주봉(1w) 50개 데이터 가져오기
        ohlcv = exchange.fetch_ohlcv(sym, timeframe='1w', limit=50)
        df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
        
        # 주봉 20 EMA(지수이동평균) 계산
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        
        cur_price = df['close'].iloc[-1]
        ema20 = df['ema20'].iloc[-1]
        state = "🟢 20 EMA 상단 (유지/상승)" if cur_price >= ema20 else "🔴 20 EMA 하단 (주의/이탈)"
        
        reports.append(f"*{sym}*\n- 현재가: \({cur_price:,.2f}\n- 주봉 20 EMA:\){ema20:,.2f}\n- 상태: {state}")

    msg = "📊 *[GitHub Actions 정기 코인 브리핑]*\n\n" + "\n\n".join(reports)
    send_telegram(msg)
    print("브리핑 전송 완료")

if __name__ == "__main__":
    main()
