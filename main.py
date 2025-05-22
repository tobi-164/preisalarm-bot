import os
import time
import requests
from telegram import Bot

# Telegram Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# Zu überwachende Assets und ihre Schritte
# Format: "Symbol": Schrittweite (in Euro)
WATCHLIST = {
    "BTC-EUR": 500,            # Bitcoin in 500 € Schritten
    "EUNL.DE": 1,              # iShares Core MSCI World (XETRA Symbol)
    "NDX": 1,                  # Nasdaq 100 ETF
    "NVDA": 1,                 # Nvidia Aktie
    "AAPL": 1,                 # Apple Aktie
    "TSLA": 1,                 # Tesla Aktie
    "BMW.DE": 1,               # BMW Aktie
    "MSFT": 1,                 # Microsoft Aktie
}

# Aktueller Stand der letzten "Schwellen"
last_notified_prices = {}

def get_price_yahoo(symbol):
    url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        price = data["quoteResponse"]["result"][0]["regularMarketPrice"]
        return price
    except Exception as e:
        print(f"Fehler beim Abrufen von {symbol}: {e}")
        return None

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
        print(f"Nachricht gesendet: {text}")
    except Exception as e:
        print(f"Fehler beim Senden der Telegram-Nachricht: {e}")

def round_to_step(price, step):
    return round(price / step) * step

def check_prices():
    for symbol, step in WATCHLIST.items():
        price = get_price_yahoo(symbol)
        if price is None:
            continue

        rounded_price = round_to_step(price, step)
        last_price = last_notified_prices.get(symbol)

        if last_price is None:
            last_notified_prices[symbol] = rounded_price
            send_telegram_message(f"🔔 Überwachung gestartet für {symbol}: aktueller Preis {price:.2f} €")
            continue

        if rounded_price != last_price:
            direction = "↑" if rounded_price > last_price else "↓"
            msg = f"{direction} {symbol} Preis hat die Schwelle {rounded_price:.2f} € erreicht (aktueller Preis: {price:.2f} €)"
            send_telegram_message(msg)
            last_notified_prices[symbol] = rounded_price

def main():
    send_telegram_message("👋 Preisalarm-Bot gestartet und überwacht die Kurse.")
    while True:
        check_prices()
        time.sleep(60)

if __name__ == "__main__":
    main()
