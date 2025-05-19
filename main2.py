import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import time
from urllib.parse import urlparse, parse_qs

url = "http://192.168.88.123:15889/data"

def wait_for_data(max_attempts=10, delay=2):
    for attempt in range(max_attempts):
        try:
            print(f"Percobaan ke-{attempt+1} mendapatkan data...")
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Gagal: {e}")
            if attempt < max_attempts - 1:
                time.sleep(delay)
            else:
                raise Exception("Gagal mendapatkan data.")

def get_expected_points(url):
    query = parse_qs(urlparse(url).query)
    start_ts = int(query.get("startTs", [0])[0])
    end_ts = int(query.get("endTs", [0])[0])
    interval = int(query.get("interval", [86400000])[0])
    expected_points = (end_ts - start_ts) // interval + 1
    return expected_points, interval

def process_forecast():
    series = wait_for_data()
    URL = series["URL"]
    expected_points, interval = get_expected_points(URL)

    data_points = series["daily_kwh"]["daily_kwh"]
    ts_values = [int(dp["ts"]) for dp in data_points]
    timestamps = pd.to_datetime(ts_values, unit='ms', utc=True).tz_convert('Asia/Jakarta')
    values = [float(dp["value"]) for dp in data_points]
    print(f"Data diterima: {len(values)} dari {expected_points} expected points")

    # Buat DataFrame
    df = pd.DataFrame({"kWh": values}, index=pd.to_datetime(timestamps))

    # ARIMA model
    model = ARIMA(df["kWh"], order=(5, 0, 1))
    model_fit = model.fit()

    forecast_steps = expected_points - len(values)
    forecast = model_fit.forecast(steps=forecast_steps) if forecast_steps > 0 else []

    forecast_dates = [df.index[-1] + timedelta(milliseconds=interval * (i + 1)) for i in range(forecast_steps)]

    all_dates = list(df.index) + forecast_dates

    result = {
        "daily_kwh": list(df["kWh"]),
        "timestamps": [int(date.timestamp() * 1000) for date in all_dates],
        "forecast": list(forecast)
    }

    try:
        resp = requests.post("http://192.168.88.123:15889/sendToTB", json=result)
        resp.raise_for_status()
        print("Forecast success\n")
    except requests.exceptions.RequestException as e:
        print("Gagal kirim forecast:", e)

if __name__ == "__main__":
    while True:
        try:
            process_forecast()
        except Exception as e:
            print("Kesalahan:", e)
        time.sleep(1)
