import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Stock Monthly Agent", layout="wide")

st.title("📈 Monthly Stock Performance Agent")
st.write("Compare four stocks against the S&P 500 Index.")

# --- Sidebar Configuration ---
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
        # Fetch data
        data = yf.download(symbols, start=start, interval="1d")
        close_prices = data['Close']
        
        # Resample logic
        monthly_close = close_prices.resample('ME').last()
        monthly_open = close_prices.resample('ME').first()
        
        df_result = pd.DataFrame(index=monthly_close.index)
        
        # Columns 1 & 2: Index Points
        df_result['Index Open'] = monthly_open[index_ticker]
        df_result['Index Close'] = monthly_close[index_ticker]
        
        # Column 3: Index % Change
        df_result['Index % Change'] = (df_result['Index Close'] / df_result['Index Open'] - 1) * 100
        
        # Columns 4, 5, 6, 7: Stock % Changes
        for stock in selected_tickers:
            stock_pct = (monthly_close[stock] / monthly_open[stock] - 1) * 100
            df_result[f'{stock} % Chg'] = stock_pct
            
        return df_result

    try:
        raw_data = get_monthly_data(all_tickers, start_date)

        # --- Section 1: The Chart ---
        st.subheader("Monthly % Change Trends")
        
        # Prepare data for plotting (we only want the % Change columns)
        plot_cols = ['Index % Change'] + [f'{s} % Chg' for s in selected_tickers]
        df_plot = raw_data[plot_cols].reset_index()
        
        # Melt the dataframe to make it "Long-form" (ideal for Plotly)
        df_melted = df_plot.melt(id_vars='Date', var_name='Ticker', value_name='Monthly % Change')

        fig = px.line(
            df_melted, 
            x='Date', 
            y='Monthly % Change', 
            color='Ticker',
            markers=True,
            template="plotly_dark",
            labels={'Monthly % Change': 'Percentage Change (%)', 'Date': 'Month'}
        )
        
        # Add a horizontal line at 0 for reference
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        
        st.plotly_chart(fig, use_container_width=True)

        # --- Section 2: The Table ---
        st.subheader("Monthly Performance Data")
        
        # Format for display
        formatted_df = raw_data.copy()
        for col in formatted_df.columns:
            if '%' in col:
                formatted_df[col] = formatted_df[col].map('{:.2f}%'.format)
            else:
                formatted_df[col] = formatted_df[col].map('{:.2f}'.format)
        
        st.dataframe(formatted_df, use_container_width=True)

        # --- Section 3: Download ---
        csv = raw_data.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name='stock_performance.csv',
            mime='text/csv',
        )
        
    except Exception as e:
        st.error(f"Error fetching data: {e}")
