# File: C:\cygwin64\home\student\Test_Strategies\MES\strategy_logic.py

from entry_manager import EntryManager
from exit_manager import ExitManager

class StrategyLogic:
    """
    Combines EntryManager and ExitManager to produce trade signals.
    """
    def __init__(self, strategy_config: dict):
        self.entry_manager = EntryManager(strategy_config)
        self.exit_manager = ExitManager()
        self.current_position = None  # {'type': 'LONG'/'SHORT', 'entry_price': ...}

    def update_position(self, new_position):
        self.current_position = new_position

    def check_signal(self, data_point: dict, multi_indicators: dict):
        # If no position is open, decide on an entry based solely on 5m data:
        if self.current_position is None:
            # For example, consider an uptrend if the current 5m close is above the 5m medium EMA.
            close_5m = data_point['close']
            ema_medium_5m = multi_indicators['5m']['EMA_medium']
            ema_short_5m = multi_indicators['5m']['EMA_short']
            rsi_5m = multi_indicators['5m']['RSI']
            
            # Define a simple trend: if close is above the medium EMA, call it uptrend; otherwise, downtrend.
            uptrend = close_5m > ema_medium_5m
            downtrend = close_5m < ema_medium_5m
            
            if uptrend:
                # Enter long if EMA_short is above EMA_medium and RSI is greater than 50
                if ema_short_5m > ema_medium_5m and rsi_5m > 45:
                    return {'type': 'LONG', 'reason': '5m uptrend: close > EMA_medium and RSI > 50'}
            if downtrend:
                # Enter short if EMA_short is below EMA_medium and RSI is less than 50
                if ema_short_5m < ema_medium_5m and rsi_5m < 55:
                    return {'type': 'SHORT', 'reason': '5m downtrend: close < EMA_medium and RSI < 50'}
        
        return None
