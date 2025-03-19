import streamlit as st
import yfinance as yf
import pandas as pd

def get_data(ticker, start_date, end_date, interval):
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        if data.empty:
            st.error(f"No data found for {ticker} with the specified parameters.")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None
