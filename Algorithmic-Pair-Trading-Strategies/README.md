# **Algorithmic-Pair-Trading-Strategies**

## **Quantitative Analysis of Financial Markets (ADMF Project)**

This repository contains the complete analysis pipeline, modeling, and backtesting results for an algorithmic **Pair Trading Strategy** applied to various stock portfolios (Technology, Energy, and Retail sectors). This project was developed as part of the *Análise de Dados de Mercados Financeiros (ADMF)* course curriculum.

### **Project Goal**

The primary objective is to develop, test, and evaluate profitable, market-neutral trading strategies by identifying co-integrated pairs of stocks and exploiting short-term divergences in their price ratios.

### **Technologies & Libraries**

* **Language:** Python  
* **Core Libraries:** pandas, numpy, matplotlib, plotly  
* **Financial/Statistical Tools:** yfinance (data fetching), statsmodels.tsa.stattools.coint (Cointegration Test), vectorbt (Backtesting)

### **Repository Structure**

The project is divided into two main portfolios, with dedicated notebooks for data handling and strategy implementation:

| File Name | Description |
| :---- | :---- |
| Portfolio\_I\_V\&A.ipynb | **Strategy Implementation & Backtesting (NVDA/AMD Pair).** Defines the z-score boundaries and executes the core pair trading logic on the technology sector. |
| Portfolio\_I\_V\&A(6M&2M).ipynb | **Advanced Backtesting (NVDA/AMD Pair).** Refines the analysis by calculating profit/loss across multiple time horizons (1, 3, 6, 12, 18, 24 months). |
| galp\_edp.ipynb | **Secondary Pair Analysis (GALP/EDP Pair).** Applies the cointegration and trading strategy to two major European energy stocks. |
| AMF\_DATA.ipynb | **Pair Data Preparation.** Contains functions and code for fetching and preprocessing financial data for the chosen pairs (e.g., Apple/Microsoft, AMD/NVIDIA). |
| Portfolio\_II\_Data.ipynb | **Data Extraction for Portfolio II.** Focuses on scraping and preparing data for a broader set of stocks across multiple sectors (Technology, Energy, Retail, Healthcare, etc.). |
| Portfolio\_II\_V\&A.ipynb | **Visualization & Analysis for Portfolio II.** Includes visualizations and T-SNE/Clustering analysis to explore relationships within the broader, multi-sector portfolio. |
| Project\_example.ipynb | A sandbox notebook demonstrating initial concepts and visualizations of the price ratio and Z-score triggers. |
| README.md | This document. |

###  **Key Concepts Implemented**

1. **Data Acquisition:** Automated fetching of historical stock price data using the yfinance API.  
2. **Cointegration Testing:** Using the **Engle-Granger test (coint)** to statistically prove that a pair of stocks moves together over the long term, making them suitable for pair trading.  
3. **Z-Score Modeling:** Calculating the rolling **Z-score** of the ratio spread to identify instances where the spread deviates significantly from its historical mean, triggering trade signals.  
4. **Trading Strategy Logic:** Implementation of a market-neutral strategy:  
   * **Entry:** Go **short** the high-priced stock and **long** the low-priced stock when the Z-score exceeds an upper threshold (+1.5, \+2.0).  
   * **Exit:** Close the position when the Z-score reverts to zero (mean reversion).  
5. **Performance Evaluation:** Backtesting the strategy across different lookback windows and calculating key performance metrics (P\&L, Sharpe Ratio, Drawdown, etc.).