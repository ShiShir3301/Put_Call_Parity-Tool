# -*- coding: utf-8 -*-
"""app2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1-jF4R7-HwY7-s9it_iTCUDM8HVI8iuM_
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import requests

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
def plot_volatility_heatmap(K_values, T_values, base_volatility, volatility_adjustment):
    adjusted_volatility = base_volatility + volatility_adjustment
    volatility_matrix = np.outer(K_values, T_values) * adjusted_volatility

    plt.figure(figsize=(4, 4))
    sns.heatmap(volatility_matrix, annot=True, fmt=".2f", xticklabels=T_values, yticklabels=K_values, cmap="coolwarm")
    plt.title("Volatility Heatmap")
    plt.xlabel("Time to Expiry (T)")
    plt.ylabel("Strike Price (K)")
    st.pyplot(plt)

# Streamlit App
def main():
    st.title("Put-Call Parity and Arbitrage Tool")

    # Sidebar for user inputs
    S = st.sidebar.number_input('S (Stock Price)', value=100)
        K = st.sidebar.number_input('K (Strike Price)', value=100)
    r = st.sidebar.number_input('r (Risk-Free Rate)', value=0.05, step=0.01)
    T = st.sidebar.number_input('T (Time to Expiration)', value=1.0, step=0.1)
    C = st.sidebar.number_input('C (Call Option Price)', value=10.0)
    P = st.sidebar.number_input('P (Put Option Price)', value=5.0)

    volatility = st.sidebar.slider('Volatility (as a decimal)', 0.01, 1.0, 0.2, 0.01)
    volatility_adjustment = st.sidebar.slider('Volatility Adjustment', -0.5, 0.5, 0.0, 0.01)

    try:
        # Calculate the parity and identify arbitrage
        C, P, _ = put_call_parity(S, K, r, T, C, P)
        arbitrage_message = identify_arbitrage(S, K, r, T, C, P)

        # Display Arbitrage Message
        st.subheader("Arbitrage Strategy:")
        st.write(arbitrage_message)

        # Plot profit/loss graph
        plot_profit(S, K, r, T, C, P)

        # Generate and plot volatility heatmap
        st.subheader("Volatility Heatmap:")
        K_values = [80, 100, 120]
        T_values = [0.5, 1.0, 2.0, 5.0]
        plot_volatility_heatmap(K_values, T_values, volatility, volatility_adjustment)

    except ValueError as e:
        st.error(str(e))

if __name__ == "__main__":
    main()