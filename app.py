# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kHvMjZe07w3rYzmFZnVzczJiwo69leg6
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import requests
import pandas as pd

# Function to calculate values based on Put-Call Parity
def put_call_parity(S, K, r, T, C=None, P=None):
    present_value_of_strike = K * np.exp(-r * T)
    if C is None and P is not None:
        # Calculate Call value using Put-Call Parity
        C = P + S - present_value_of_strike
    elif P is None and C is not None:
        # Calculate Put value using Put-Call Parity
        P = C - S + present_value_of_strike
    elif C is None and P is None:
        raise ValueError("At least one of C (Call price) or P (Put price) must be provided.")
    return C, P, present_value_of_strike

def identify_arbitrage(S, K, r, T, C, P):
    """
    Identifies and explains arbitrage opportunities based on the put-call parity principle.

    Parameters:
    - S: Current stock price
    - K: Strike price
    - r: Risk-free interest rate
    - T: Time to maturity (in years)
    - C: Call option price
    - P: Put option price

    Returns:
    - Detailed explanation of the arbitrage strategy or a message indicating no arbitrage.
    """
    # Calculate the present value of the strike price and parity price
    _, _, pv_strike = put_call_parity(S, K, r, T, C, P)
    parity_price = P + S - pv_strike

    # Determine arbitrage opportunities
    if C > parity_price:
        return (
            f"Arbitrage Opportunity Detected (Overpriced Call):\n"
            f"Call Price (C): {C:.2f} > Parity Price: {parity_price:.2f}\n"
            f"Strategy:\n"
            f"1. Short the call option (Sell the call at {C:.2f}).\n"
            f"2. Buy the put option (Buy the put at {P:.2f}).\n"
            f"3. Buy the underlying asset (Stock price: {S:.2f}).\n"
            f"4. Borrow the present value of the strike price (PV(K): {pv_strike:.2f}) at the risk-free rate ({r:.2%}).\n"
            f"Outcome:\n"
            f"- Arbitrage profit locked in due to the mispricing of the call option.\n"
            f"- This is a 'reverse arbitrage' strategy where you exploit the overpriced call."
        )
    elif C < parity_price:
        return (
            f"Arbitrage Opportunity Detected (Underpriced Call):\n"
            f"Call Price (C): {C:.2f} < Parity Price: {parity_price:.2f}\n"
            f"Strategy:\n"
            f"1. Buy the call option (Buy the call at {C:.2f}).\n"
            f"2. Short the put option (Sell the put at {P:.2f}).\n"
            f"3. Short the underlying asset (Stock price: {S:.2f}).\n"
            f"4. Invest the present value of the strike price (PV(K): {pv_strike:.2f}) at the risk-free rate ({r:.2%}).\n"
            f"Outcome:\n"
            f"- Arbitrage profit locked in due to the mispricing of the call option.\n"
            f"- This is a 'classic arbitrage' strategy where you exploit the underpriced call."
        )
    elif P > parity_price:
        return (
            f"Arbitrage Opportunity Detected (Overpriced Put):\n"
            f"Put Price (P): {P:.2f} > Parity Price: {parity_price:.2f}\n"
            f"Strategy:\n"
            f"1. Short the put option (Sell the put at {P:.2f}).\n"
            f"2. Buy the call option (Buy the call at {C:.2f}).\n"
            f"3. Buy the underlying asset (Stock price: {S:.2f}).\n"
            f"4. Borrow the present value of the strike price (PV(K): {pv_strike:.2f}) at the risk-free rate ({r:.2%}).\n"
            f"Outcome:\n"
            f"- Arbitrage profit locked in due to the mispricing of the put option.\n"
            f"- This strategy takes advantage of an overpriced put."
        )
    elif P < parity_price:
        return (
            f"Arbitrage Opportunity Detected (Underpriced Put):\n"
            f"Put Price (P): {P:.2f} < Parity Price: {parity_price:.2f}\n"
            f"Strategy:\n"
            f"1. Buy the put option (Buy the put at {P:.2f}).\n"
            f"2. Short the call option (Sell the call at {C:.2f}).\n"
            f"3. Short the underlying asset (Stock price: {S:.2f}).\n"
            f"4. Invest the present value of the strike price (PV(K): {pv_strike:.2f}) at the risk-free rate ({r:.2%}).\n"
            f"Outcome:\n"
            f"- Arbitrage profit locked in due to the mispricing of the put option.\n"
            f"- This is a 'reverse arbitrage' strategy where you exploit the underpriced put."
        )
    else:
        return (
            f"No Arbitrage Opportunity:\n"
            f"Call Price (C): {C:.2f} matches Parity Price: {parity_price:.2f}\n"
            f"Put Price (P): {P:.2f} matches Parity Price: {parity_price:.2f}\n"
            f"The market prices are consistent with the put-call parity principle."
        )

# Function to fetch live stock price from Tiingo API
def fetch_live_price(ticker, token):
    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[0]['close']
    else:
        raise ValueError(f"Failed to fetch data for ticker {ticker}. Check the ticker and token.")

# Function to compute Historical Volatility (Realized Volatility)
def compute_historical_volatility(ticker, token, days=30):
    url = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}&startDate=2023-01-01"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df['returns'] = df['close'].pct_change()
        df.dropna(subset=['returns'], inplace=True)
        
        # Compute the daily volatility (standard deviation of returns)
        daily_volatility = df['returns'].std()
        annualized_volatility = daily_volatility * np.sqrt(252)  # Annualize the volatility assuming 252 trading days per year
        return annualized_volatility
    else:
        raise ValueError(f"Failed to fetch data for ticker {ticker}. Check the ticker and token.")

# Function to plot profit/loss
def plot_profit(S, K, r, T, C, P):
    stock_prices = np.linspace(0.5 * K, 1.5 * K, 500)
    call_payoff = np.maximum(stock_prices - K, 0) - C
    put_payoff = np.maximum(K - stock_prices, 0) - P
    combined_payoff = call_payoff + put_payoff + stock_prices - K * np.exp(-r * T)

    plt.figure(figsize=(5, 3))
    plt.plot(stock_prices, call_payoff, label="Call Payoff", linestyle="--")
    plt.plot(stock_prices, put_payoff, label="Put Payoff", linestyle="--")
    plt.plot(stock_prices, combined_payoff, label="Arbitrage Payoff", linewidth=2)
    plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
    plt.title("Profit/Loss Visualization")
    plt.xlabel("Stock Price at Expiration")
    plt.ylabel("Profit/Loss")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# Function to create a volatility heatmap
def plot_volatility_heatmap(K_values, T_values, volatility_matrix):
    plt.figure(figsize=(6, 6))
    sns.heatmap(volatility_matrix, annot=True, fmt=".2f", xticklabels=T_values, yticklabels=K_values, cmap="coolwarm")
    plt.title("Volatility Heatmap")
    plt.xlabel("Time to Expiry (T)")
    plt.ylabel("Strike Price (K)")
    plt.show()

# Main application
def main():
    st.title("Option Pricing & Arbitrage")
    
    ticker = st.text_input("Enter Stock Ticker", "AAPL")
    token = st.text_input("Enter Tiingo API Token", "")
    
    # Fetch live stock price
    if ticker and token:
        try:
            stock_price = fetch_live_price(ticker, token)
            st.write(f"Live stock price for {ticker}: ${stock_price:.2f}")
        except Exception as e:
            st.error(f"Error fetching stock price: {e}")
    
    st.header("Option Pricing")
    
    # Option parameters input
    S = st.number_input("Enter Stock Price (S)", min_value=0.0, value=stock_price)
    K = st.number_input("Enter Strike Price (K)", min_value=0.0, value=100.0)
    r = st.number_input("Enter Risk-Free Interest Rate (r)", min_value=0.0, max_value=1.0, value=0.05)
    T = st.number_input("Enter Time to Expiry (T) in years", min_value=0.0, value=0.5)
    C = st.number_input("Enter Call Option Price (C)", min_value=0.0, value=10.0)
    P = st.number_input("Enter Put Option Price (P)", min_value=0.0, value=10.0)

    # Put-Call Parity & Arbitrage Analysis
    st.subheader("Put-Call Parity & Arbitrage")
    parity_data = put_call_parity(S, K, r, T, C, P)
    st.write(f"Call Option Price: {parity_data[0]:.2f}, Put Option Price: {parity_data[1]:.2f}, Present Value of Strike: {parity_data[2]:.2f}")
    arbitrage_opportunity = identify_arbitrage(S, K, r, T, C, P)
    st.text_area("Arbitrage Opportunity", arbitrage_opportunity, height=200)

    # Profit-Loss Plot
    plot_profit(S, K, r, T, C, P)

    # Volatility Heatmap
    K_values = np.linspace(80, 120, 5)  # Strike prices range
    T_values = np.linspace(0.1, 2.0, 5)  # Time to expiry in years
    volatility_matrix = []

    for K_val in K_values:
        row = []
        for T_val in T_values:
            # Compute historical volatility
            volatility = compute_historical_volatility(ticker, token)
            row.append(volatility)
        volatility_matrix.append(row)

    plot_volatility_heatmap(K_values, T_values, volatility_matrix)

if __name__ == "__main__":
    main()
