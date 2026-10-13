import concurrent.futures
import time
import pandas as pd
import yfinance as yf

# Expanded Nifty 200 / F&O universe sample (Add your full list here)
NIFTY_200_SYMBOLS = [
    "RELIANCE.NS",
    "TCS.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "INFY.NS",
    "BHARTIARTL.NS",
    "SBIN.NS",
    "LICI.NS",
    "ITC.NS",
    "HINDUNILVR.NS",
    "LT.NS",
    "BAJFINANCE.NS",
    "MARUTI.NS",
    "HCLTECH.NS",
    "SUNPHARMA.NS",
    "ADANIENT.NS",
    "TITAN.NS",
    "TATAMOTORS.NS",
    "NTPC.NS",
    "ONGC.NS",
    "AXISBANK.NS",
    "KOTAKBANK.NS",
    "TITAN.NS",
    "BAJAJFINSV.NS",
    "WIPRO.NS",
    "ULTRACEMCO.NS",
    "NESTLEIND.NS",
    "GRASIM.NS",
    "JSWSTEEL.NS",
    "TATASTEEL.NS",
]

TIMEFRAMES = {
    "5m": {"interval": "5m", "period": "5d"},
    "15m": {"interval": "15m", "period": "1mo"},
    "1h": {"interval": "60m", "period": "3mo"},
    "1d": {"interval": "1d", "period": "6mo"},
}

NTO_LENGTH = 14
NTO_SMOOTH = 80


def calculate_nto(df, length=14, smooth=80):
  """Computes the Normalized Trend Oscillator values."""
  if df is None or len(df) < max(length, smooth):
    return None

  close = df["Close"]
  high = df["High"]
  low = df["Low"]

  highest_high = high.rolling(window=length).max()
  lowest_low = low.rolling(window=length).min()

  range_val = highest_high - lowest_low
  range_val = range_val.replace(0, 0.0001)

  raw_nto = ((close - lowest_low) / range_val) * 100
  nto_line = raw_nto.rolling(window=smooth).mean()

  return round(float(nto_line.iloc[-1]), 2)


def scan_ticker(symbol):
  results = {"Symbol": symbol.replace(".NS", "")}
  for tf_name, tf_config in TIMEFRAMES.items():
    try:
      df = yf.download(
          symbol,
          period=tf_config["period"],
          interval=tf_config["interval"],
          progress=False,
      )
      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
      results[tf_name] = calculate_nto(df, NTO_LENGTH, NTO_SMOOTH)
    except:
      results[tf_name] = None

  # Determine Multi-Timeframe Alignment Signal (Threshold > 50 / < 50)
  try:
    vals = [results["5m"], results["15m"], results["1h"], results["1d"]]
    if all(v is not None for v in vals):
      if all(v > 50 for v in vals):
        results["Signal"] = "FULL BULLISH 🟢"
      elif all(v < 50 for v in vals):
        results["Signal"] = "FULL BEARISH 🔴"
      else:
        results["Signal"] = "Mixed / Neutral"
    else:
      results["Signal"] = "Data Error"
  except:
    results["Signal"] = "Error"

  return results


def run_scanner():
  print(f"🚀 Scanning {len(NIFTY_200_SYMBOLS)} symbols across Multi-TF...")
  scan_results = []

  with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(scan_ticker, sym) for sym in NIFTY_200_SYMBOLS
    ]
    for future in concurrent.futures.as_completed(futures):
      scan_results.append(future.result())

  df_results = pd.DataFrame(scan_results)
  # Save to CSV for Streamlit consumption
  df_results.to_csv("nto_scan_results.csv", index=False)
  print("✅ Scan complete. Saved to nto_scan_results.csv")


if __name__ == "__main__":
  run_scanner()
