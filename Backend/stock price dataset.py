import requests
import json
import time


# Company details: (symbol, exchange, segment)
companies = [
    ("RAYMOND", "NSE", "CASH"),
    ("RELIANCE", "NSE", "CASH"),
    ("INFY", "NSE", "CASH"),
]
import time

# Get current time in milliseconds
end_time = int(time.time() * 1000)

# 5 market days = approx 5 * 24 * 60 * 60 seconds (adjusted below for precision)
# Assuming 1 trading day = 6.5 hours = 23400 seconds
# But Groww allows date range in milliseconds, so:
start_time = end_time - (3* 24 * 60 * 60 * 1000)  # 5 days ago

print("Start:", start_time)
print("End:", end_time)

# Base URL
base_url = "https://groww.in/v1/api/charting_service/v4/chart/exchange"

# Loop and fetch
for symbol, exchange, segment in companies:
    print(f"Fetching data for {symbol} ({exchange})...")

    url = f"{base_url}/{exchange}/segment/{segment}/{symbol}"
    params = {
        "startTimeInMillis": start_time,
        "endTimeInMillis": end_time,
        "intervalInMinutes": 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Check if it contains candles
        if 'candles' in data and len(data['candles']) > 0:
            filename = f"{symbol}_{exchange}.json"
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved data for {symbol} to {filename}")
        else:
            print(f"No candle data for {symbol}")

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")

    time.sleep(1)

import yfinance as yf

tickers = ["AAPL", "GOOGL", "MSFT", "TSLA"]

for ticker in tickers:
    print(f"Fetching data for {ticker}...")
    data = yf.download(ticker, interval="1d", period="5d", auto_adjust=True)
    
    # Save as CSV
    csv_filename = f"{ticker}_daily_data.csv"
    data.to_csv(csv_filename)
    print(f"Saved CSV to {csv_filename}")
    
    # Save as JSON
    json_filename = f"{ticker}_daily_data.json"
    data.to_json(json_filename, orient="records", date_format="iso")
    print(f"Saved JSON to {json_filename}")



