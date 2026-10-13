import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NTO MTF Scanner", page_icon="📈", layout="wide"
)

st.title("📊 Normalized Trend Oscillator (NTO) Multi-TF Scanner")
st.markdown(
    "Scanning Nifty universe across **5m, 15m, 1h, and 1d** timeframes using"
    " NTO(14, 80)."
)


@st.cache_data(ttl=600)  # Refresh data cache every 10 mins
def load_data():
  try:
    return pd.read_csv("nto_scan_results.csv")
  except FileNotFoundError:
    return pd.DataFrame()


df = load_data()

if df.empty:
  st.warning(
      "⚠️ No scan results found yet. Run `scanner.py` or wait for the GitHub"
      " Action to run."
  )
else:
  # Sidebar Filters
  st.sidebar.header("Filter Results")
  signal_filter = st.sidebar.selectbox(
      "Filter by Signal",
      [
          "All",
          "FULL BULLISH 🟢",
          "FULL BEARISH 🔴",
          "Mixed / Neutral",
      ],
  )

  filtered_df = df.copy()
  if signal_filter != "All":
    filtered_df = filtered_df[filtered_df["Signal"] == signal_filter]

  st.metric(label="Total Stocks Scanned", value=len(df))
  st.metric(label="Matching Filter", value=len(filtered_df))

  # Display Table
  st.dataframe(filtered_df, use_container_width=True, hide_index=True)

  if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
