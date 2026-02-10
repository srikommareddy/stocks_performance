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
        # Fetch data with auto_adjust to avoid the 'Adj Close' header issue
        # We use 'Close' which will now represent the adjusted price
        data = yf.download(symbols, start=start, interval="1d")
    
        # Access the 'Close' prices specifically
        close_prices = data['Close']
    
        # Resample logic
        monthly_close = close_prices.resample('ME').last()
        monthly_open = close_prices.resample('ME').first()
    
        df_result = pd.DataFrame(index=monthly_close.index)
    
        # Column 1 & 2: Index Points
        df_result['Index Open'] = monthly_open[index_ticker]
        df_result['Index Close'] = monthly_close[index_ticker]
    
        # Column 3: Index % Change
        df_result['Index % Change'] = (df_result['Index Close'] / df_result['Index Open'] - 1) * 100
    
        # Column 4, 5, 6, 7: Stock % Changes
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
