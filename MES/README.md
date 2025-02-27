# Backtesting Application

This repository contains a simple **multi-timeframe backtesting** application written in Python. The primary script, `backtesting_app.py`, loads historical data for multiple timeframes, computes various technical indicators, applies a basic strategy, simulates trade execution (including stop-loss and take-profit), and finally analyzes the performance of those trades.

---

## Table of Contents

1. [Overview](#overview)  
2. [Features](#features)  
3. [Project Structure](#project-structure)  
4. [Installation](#installation)  
5. [Data Requirements](#data-requirements)  
6. [Configuration](#configuration)  
7. [Usage](#usage)  
8. [Outputs](#outputs)  
9. [Extending the Application](#extending-the-application)  
10. [License](#license)

---

## Overview

This application demonstrates how to:

- Load historical market data in multiple timeframes (e.g., 1-minute, 5-minute).
- Calculate a set of technical indicators (EMA, RSI, ATR, MACD, Stochastic).
- Merge lower-timeframe indicator columns (e.g., 1-minute) into a higher-timeframe dataset.
- Use a rudimentary strategy logic to generate entry signals (LONG or SHORT).
- Simulate trades, including stop-loss and take-profit logic, using an `ExecutionSimulator`.
- Produce a performance summary (win rate, profit factor, average P/L, etc.).

It is designed as a starting point for quantitative researchers or traders wanting to develop and test automated strategies.

---

## Features

- **Multiple Timeframes**: Automatically loads and merges indicators from different timeframes (1m, 5m, etc.).
- **Technical Indicators**: EMA, RSI, MACD, Stochastic, and ATR (with simple rolling or EMA-based calculations).
- **Configurable Strategy**: Strategy parameters and threshold values (RSI bounds, EMA periods, stop offsets, etc.) are read from `config.json`.
- **Trade Simulation**:
  - Entry signals (LONG/SHORT)
  - Stop-loss, take-profit, and optional trailing-stop
  - Position sizing (default quantity)
- **Performance Analysis**: Summaries include total trades, win rate, largest win/loss, profit factor, etc.

---

## Project Structure

```bash
Test_Strategies/
├─ MES/
│  ├─ data/
│  │  ├─ MES_1_min.csv
│  │  ├─ MES_5_mins.csv
│  │  └─ ...
│  ├─ backtesting_app.py          # Main entry point to run the backtest
│  ├─ config.json                 # Contains indicator/strategy/execution parameters
│  ├─ data_loader.py              # Handles reading historical data from CSV
│  ├─ indicator_calculator.py     # Computes EMA, RSI, ATR, MACD, Stoch, etc.
│  ├─ strategy_logic.py           # Simple strategy logic to generate signals
│  ├─ execution_simulator.py      # Simulates trade execution, stops, targets
│  ├─ performance_analyzer.py     # Computes performance metrics from trades
│  ├─ entry_manager.py            # (Optional) Additional logic for generating entry signals
│  ├─ exit_manager.py             # (Optional) Additional logic for generating exit signals
│  ├─ export_files_to_outputtext.py
│  └─ results_and_reporting.py    # (Optional) Tools for saving trades, generating plots, etc.
