class EntryManager:
    def __init__(self, strategy_config: dict):
        self.rsi_overbought = strategy_config.get('RSI_overbought', 70)
        self.rsi_oversold = strategy_config.get('RSI_oversold', 30)
        self.last_signal = None

    def evaluate_entry(self, data_point: dict, indicators: dict, timeframe: str = None):
        """
        Evaluate indicators and price data to decide whether to enter a trade.
        Returns a signal dict if entry criteria are met, otherwise None.
    
        data_point: e.g. {'time': ..., 'close': ..., 'open': ..., etc.}
        indicators: e.g. {'EMA': ..., 'RSI': ...}
        timeframe: string identifier for logging/debugging purposes.
        """
        signal = None
        price = data_point.get('close')
        if price is None:
            return None
    
        ema_value = indicators.get('EMA')
        rsi_value = indicators.get('RSI')
    
        # For demonstration, use the same logic as before.
        if rsi_value is not None and ema_value is not None:
            if rsi_value < self.rsi_oversold and price > ema_value:
                signal = {'type': 'LONG', 'reason': f'RSI oversold and price > EMA on {timeframe}'}
            elif rsi_value > self.rsi_overbought and price < ema_value:
                signal = {'type': 'SHORT', 'reason': f'RSI overbought and price < EMA on {timeframe}'}
    
        if signal:
            print(f"EntryManager ({timeframe}): Entry signal detected -> {signal}")
        self.last_signal = signal
        return signal
