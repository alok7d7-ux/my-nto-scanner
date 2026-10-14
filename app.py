import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="NTO MTF Scanner", page_icon="📈", layout="wide"
)

st.title("📊 Normalized Trend Oscillator (NTO) Multi-TF Scanner")
st.markdown(
    "Scanning live universe across **5m, 15m, 1h, and 1d** timeframes using"
    " NTO(14, 80). Click any row's **TradingView Chart** link to open the live"
    " chart."
)


@st.cache_data(ttl=300)
def load_data():
  try:
    return pd.read_csv("nto_scan_results.csv")
  except FileNotFoundError:
    return pd.DataFrame()


df = load_data()

if df.empty:
  st.warning("⚠️ No scan results found yet. Please run the scanner action.")
else:
  # Sidebar Controls
  st.sidebar.header("Filters & Sorting")
  signal_filter = st.sidebar.selectbox(
      "Filter by Signal",
      [
          "All",
          "FULL BULLISH 🟢",
          "FULL BEARISH 🔴",
          "Mixed / Neutral",
      ],
  )

  # Sorting Options
  sort_column = st.sidebar.selectbox(
      "Sort By", ["Symbol", "5m", "15m", "1h", "1d", "Signal"]
  )
  sort_order = st.sidebar.radio(
      "Direction", ["Highest first ⬇️", "Lowest first ⬆️"]
  )
  ascending_bool = True if "Lowest" in sort_order else False

  filtered_df = df.copy()
  if signal_filter != "All":
    filtered_df = filtered_df[filtered_df["Signal"] == signal_filter]

  # Apply sorting
  if sort_column in filtered_df.columns:
    filtered_df = filtered_df.sort_values(
        by=sort_column, ascending=ascending_bool
    )

  col1, col2 = st.columns(2)
  with col1:
    st.metric(label="Total Stocks Scanned", value=len(df))
  with col2:
    st.metric(label="Matching Filter Count", value=len(filtered_df))

  st.markdown("---")

  # Display Interactive Table
  st.dataframe(
      filtered_df,
      column_config={
          "TradingView": st.column_config.LinkColumn(
              "TradingView Chart",
              help="Click to open direct chart on TradingView",
              display_text="📈 Open Chart",
          )
      },
      use_container_width=True,
      hide_index=True,
  )

  if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
