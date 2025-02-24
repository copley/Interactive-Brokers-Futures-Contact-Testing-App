# File: C:\cygwin64\home\student\Test_Strategies\MES\execution_simulator.py

class ExecutionSimulator:
    """
    Simulates trade execution in a backtest environment.
    Tracks open positions, stop-loss/target offsets, trailing stops, position sizing, and PnL.
    """

    def __init__(self, 
                 stop_offset: float = 2.0,
                 target_offset: float = 5.0,
                 default_quantity: int = 1,
                 enable_trailing_stop: bool = False,
                 trailing_stop_offset: float = 2.0):
        """
        :param stop_offset: How many points below entry to set the initial stop-loss (for a LONG).
        :param target_offset: How many points above entry to set the take-profit (for a LONG).
        :param default_quantity: Number of contracts/shares traded per signal.
        :param enable_trailing_stop: Whether to use trailing-stop logic.
        :param trailing_stop_offset: Points behind the best favorable price for a trailing stop.
        """
        self.stop_offset = stop_offset
        self.target_offset = target_offset
        self.default_quantity = default_quantity

        self.enable_trailing_stop = enable_trailing_stop
        self.trailing_stop_offset = trailing_stop_offset

        # Track any currently open position (dict or None).
        self.open_position = None

        # Keep a list of completed trades (dicts).
        self.trades = []

    def process_signal(self, signal: dict, data_point: dict):
        """
        Processes a trading signal (LONG, SHORT, or EXIT).
        If LONG/SHORT, opens a position if none is open.
        If EXIT, closes the open position if it matches the position_type.
        Returns the position or trade dict, or None.
        """
        signal_type = signal.get('type')
        time_ = data_point.get('time')
        close_price = data_point.get('close', 0.0)

        if signal_type in ['LONG', 'SHORT']:
            # Only open a new position if none is currently open.
            if self.open_position is None:
                self.open_position = {
                    'type': signal_type,
                    'entry_price': close_price,
                    'entry_time': time_,
                    'quantity': self.default_quantity,
                    'reason': signal.get('reason', ''),

                    # For trailing stop logic:
                    # Track the best favorable price since entry (for LONG: highest high; for SHORT: lowest low).
                    'best_price': close_price
                }
                print(f"ExecutionSimulator: Opened {signal_type} at {close_price} on {time_} for qty={self.default_quantity}")
                return self.open_position

        elif signal_type == 'EXIT':
            # Close the position if it matches the signal's position_type
            if (self.open_position is not None and
                self.open_position['type'] == signal.get('position_type')):
                
                exit_price = signal.get('exit_price', close_price)
                trade = {
                    'position_type': self.open_position['type'],
                    'entry_price': self.open_position['entry_price'],
                    'exit_price': exit_price,
                    'entry_time': self.open_position['entry_time'],
                    'exit_time': time_,
                    'quantity': self.open_position['quantity'],
                    'reason': signal.get('reason', '')
                }
                self.trades.append(trade)
                print(f"ExecutionSimulator: Closed {trade['position_type']} at {exit_price} on {time_}, reason={trade['reason']}")

                self.open_position = None
                return trade

        return None  # No action if conditions not met

    def check_stop_loss_or_profit_target(self, data_point: dict):
        """
        Checks if the current bar (via its high/low) hits:
          1) The trailing stop (if enabled)
          2) The fixed stop-loss 
          3) The take-profit target

        Returns a dict with exit info if triggered, else None.
        """
        if not self.open_position:
            return None  # No open position to check

        bar_high = data_point.get('high', 0.0)
        bar_low = data_point.get('low', 0.0)
        close_price = data_point.get('close', 0.0)
        position_type = self.open_position['type']
        entry_price = self.open_position['entry_price']
        
        # 1) Update best favorable price if trailing stop is enabled
        if self.enable_trailing_stop:
            if position_type == 'LONG':
                # If the current bar's high is above the previous best_price, update
                if bar_high > self.open_position['best_price']:
                    self.open_position['best_price'] = bar_high
            else:  # SHORT
                # If current bar's low is below the previous best_price, update
                if bar_low < self.open_position['best_price']:
                    self.open_position['best_price'] = bar_low

        # 2) Compute potential stop-loss levels
        if position_type == 'LONG':
            # A) If trailing is enabled, trailing_stop is best_price - trailing_stop_offset
            if self.enable_trailing_stop:
                trailing_stop_price = self.open_position['best_price'] - self.trailing_stop_offset
            else:
                trailing_stop_price = entry_price - self.stop_offset

            # B) fixed target
            take_profit = entry_price + self.target_offset

            # Check if we hit trailing stop or fixed stop
            if bar_low <= trailing_stop_price:
                return {
                    'exit_price': trailing_stop_price,
                    'reason': 'StopLoss hit (trailing)' if self.enable_trailing_stop else 'StopLoss hit'
                }
            # Then check take-profit
            elif bar_high >= take_profit:
                return {
                    'exit_price': take_profit,
                    'reason': 'TakeProfit hit'
                }

        else:  # SHORT
            if self.enable_trailing_stop:
                trailing_stop_price = self.open_position['best_price'] + self.trailing_stop_offset
            else:
                trailing_stop_price = entry_price + self.stop_offset

            take_profit = entry_price - self.target_offset

            if bar_high >= trailing_stop_price:
                return {
                    'exit_price': trailing_stop_price,
                    'reason': 'StopLoss hit (trailing)' if self.enable_trailing_stop else 'StopLoss hit'
                }
            elif bar_low <= take_profit:
                return {
                    'exit_price': take_profit,
                    'reason': 'TakeProfit hit'
                }

        return None  # No stop or target triggered

    def get_open_position(self):
        """Return the currently open position dict or None."""
        return self.open_position

    def get_closed_trades(self):
        """Return a list of all completed trades."""
        return self.trades
