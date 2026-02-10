import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="AI Stock Monthly Agent", layout="wide")

st.title("📈 Monthly Stock Performance Agent")
st.write("Compare four stocks against the S&P 500 Index.")

# Sidebar Inputs
st.sidebar.header("Configuration")
index_ticker = "^GSPC" # S&P 500
tickers = st.sidebar.text_input("Enter 4 Tickers (comma separated)", "AAPL, MSFT, GOOGL, TSLA")
selected_tickers = [t.strip().upper() for t in tickers.split(",")]

start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2023-01-01"))

if len(selected_tickers) != 4:
    st.error("Please enter exactly 4 stock tickers.")
else:
    all_tickers = [index_ticker] + selected_tickers
    
    @st.cache_data
    def get_monthly_data(symbols, start):
        # Fetch daily data
        data = yf.download(symbols, start=start, interval="1d")['Adj Close']
        # Resample to Monthly (takes the last available price of the month)
        monthly_close = data.resample('ME').last()
        # Get the first available price of the month (approximate from daily)
        monthly_open = data.resample('ME').first()
        
        # Calculate Index points (Column 1 & 2)
        df_result = pd.DataFrame(index=monthly_close.index)
        df_result['Index Open'] = monthly_open[index_ticker]
        df_result['Index Close'] = monthly_close[index_ticker]
        
        # Calculate % Changes
        df_result['Index % Change'] = (df_result['Index Close'] / df_result['Index Open'] - 1) * 100
        
        for stock in selected_tickers:
            stock_pct = (monthly_close[stock] / monthly_open[stock] - 1) * 100
            df_result[f'{stock} % Chg'] = stock_pct
            
        return df_result

    # Display Data
    try:
        final_df = get_monthly_data(all_tickers, start_date)
        
        # Formatting the table for readability
        formatted_df = final_df.copy()
        for col in formatted_df.columns:
            if '%' in col:
                formatted_df[col] = formatted_df[col].map('{:.2f}%'.format)
            else:
                formatted_df[col] = formatted_df[col].map('{:.2f}'.format)
        
        st.subheader("Monthly Performance Summary")
        st.dataframe(formatted_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
