# File: C:\cygwin64\home\student\Test_Strategies\MES\indicator_calculator.py

import pandas as pd
import numpy as np

class IndicatorCalculator:
    """
    Computes technical indicators such as EMA, RSI, ATR, MACD, Stochastic, etc.
    """

    def __init__(self):
        # You can store default periods here or pass them in methods below
        pass

    def compute_ema(self, df: pd.DataFrame, span: int) -> pd.Series:
        return df['close'].ewm(span=span, adjust=False).mean()

    def compute_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Compute RSI using a simplified (ema-based) method.
        """
        delta = df['close'].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)

        ema_up = up.ewm(com=period - 1, adjust=False).mean()
        ema_down = down.ewm(com=period - 1, adjust=False).mean()

        rs = ema_up / ema_down
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def compute_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()  # Alternatively use an EMA
        return atr

    def compute_macd(self, df: pd.DataFrame, fast=12, slow=26, signal=9):
        """
        Returns MACD line and Signal line as a tuple (macd, macd_signal).
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
        return macd_line, macd_signal

    def compute_stochastic(self, df: pd.DataFrame, k_period=14, d_period=3):
        """
        Returns %K and %D lines for Stochastic.
        """
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()

        stoch_k = 100 * (df['close'] - low_min) / (high_max - low_min + 1e-9)
        stoch_d = stoch_k.rolling(window=d_period).mean()
        return stoch_k, stoch_d

    def add_indicators(
        self,
        df: pd.DataFrame,
        short_ema_period=5,
        medium_ema_period=15,
        rsi_period=14,
        atr_period=14,
        compute_macd=False,
        compute_stoch=False
    ) -> pd.DataFrame:
        """
        Add multiple indicators to the DataFrame.
        """
        # Short EMA
        df['EMA_short'] = self.compute_ema(df, short_ema_period)

        # Medium EMA
        df['EMA_medium'] = self.compute_ema(df, medium_ema_period)

        # RSI
        df['RSI'] = self.compute_rsi(df, rsi_period)

        # ATR
        df['ATR'] = self.compute_atr(df, atr_period)

        # Optional MACD
        if compute_macd:
            macd_line, macd_signal = self.compute_macd(df)
            df['MACD'] = macd_line
            df['MACD_signal'] = macd_signal

        # Optional Stochastic
        if compute_stoch:
            stoch_k, stoch_d = self.compute_stochastic(df)
            df['StochK'] = stoch_k
            df['StochD'] = stoch_d

        return df
