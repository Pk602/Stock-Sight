import requests
import json
import os
import time
from datetime import datetime, timedelta

# === CONFIGURATION ===

# Top 20 NSE companies
symbols = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "ITC", "LT", "AXISBANK",
    "KOTAKBANK", "SBIN", "HCLTECH", "SUNPHARMA", "BAJFINANCE", "TITAN",
    "HINDUNILVR", "M&M", "ASIANPAINT", "MARUTI", "NESTLEIND", "WIPRO"
]

# Time intervals and their minute values for the Groww API
intervals = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "1d": 1440  # 1 day = 1440 minutes
}

# Max days to query per API request, per interval
days_per_chunk = {
    "1m": 3,
    "5m": 10,
    "15m": 30,
    "1d": 180
}

# Time window: Last 3 years
def get_start_date(interval_label):
    return datetime.now() - timedelta(days=3*365)

end_date = datetime.now()

# API endpoint base (symbol is added at the end)
base_url = "https://groww.in/v1/api/charting_service/v4/chart/exchange/NSE/segment/CASH"

# Create the main output folder if it doesn't exist
output_folder = "groww_3year_data"
os.makedirs(output_folder, exist_ok=True)

# === MAIN SCRIPT ===

# Loop over each company
for symbol in symbols:
    print(f"\nFetching data for {symbol}")

    # Create a subfolder for each company
    symbol_dir = os.path.join(output_folder, symbol)
    os.makedirs(symbol_dir, exist_ok=True)

    # Loop over each interval (e.g., 1m, 5m, 1d)
    for label, interval in intervals.items():
        print(f"  Timeframe: {label}")

        all_candles = []
        chunk_days = days_per_chunk[label]
        current_end = end_date
        custom_start_date = get_start_date(label)

        no_data_count = 0

        while current_end > custom_start_date:
            current_start = current_end - timedelta(days=chunk_days)
            start_ms = int(current_start.timestamp() * 1000)
            end_ms = int(current_end.timestamp() * 1000)

            params = {
                "startTimeInMillis": start_ms,
                "endTimeInMillis": end_ms,
                "intervalInMinutes": interval
            }

            try:
                res = requests.get(f"{base_url}/{symbol}", params=params)
                res.raise_for_status()
                data = res.json()

                if "candles" in data and data["candles"]:
                    all_candles.extend(data["candles"])
                    print(f"    {len(data['candles'])} records: {current_start.date()} to {current_end.date()}")
                    no_data_count = 0
                else:
                    print(f"    No data available: {current_start.date()} to {current_end.date()}")
                    no_data_count += 1
                    if no_data_count >= 2:
                        print("    Skipping to next interval due to consecutive data gaps.")
                        break

            except Exception as e:
                print(f"    Error: {e}")

            current_end = current_start
            time.sleep(1.5)

        filename = os.path.join(symbol_dir, f"{symbol}_{label}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_candles, f, indent=2)

        print(f"    Saved {len(all_candles)} records to {filename}")
