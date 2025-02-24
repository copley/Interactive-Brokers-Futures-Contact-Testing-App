import pandas as pd

class PerformanceAnalyzer:
    """
    Computes PnL, drawdown, win rate, etc. on the trades recorded by ExecutionSimulator.
    """
    def __init__(self, trades):
        # trades is a list of dicts: each containing entry_price, exit_price, etc.
        self.trades = trades
        self.trades_df = None
        if trades:
            self.trades_df = pd.DataFrame(trades)

    def compute_basic_metrics(self):
        """
        Returns a dict of basic performance metrics: total PnL, win rate, etc.
        """
        if self.trades_df is None or self.trades_df.empty:
            return {
                'total_trades': 0,
                'total_pnl': 0.0,
                'win_rate': 0.0,
            }
        
        # For a LONG position, PnL = exit_price - entry_price
        # For a SHORT position, PnL = entry_price - exit_price
        def calculate_trade_pnl(row):
            if row['position_type'] == 'LONG':
                return row['exit_price'] - row['entry_price']
            elif row['position_type'] == 'SHORT':
                return row['entry_price'] - row['exit_price']
            else:
                return 0.0

        self.trades_df['pnl'] = self.trades_df.apply(calculate_trade_pnl, axis=1)

        total_trades = len(self.trades_df)
        total_pnl = self.trades_df['pnl'].sum()
        wins = self.trades_df[self.trades_df['pnl'] > 0]
        win_rate = len(wins) / total_trades if total_trades > 0 else 0

        return {
            'total_trades': total_trades,
            'total_pnl': total_pnl,
            'win_rate': win_rate,
        }

    def compute_drawdown(self):
        """
        A simplistic approach to compute drawdown from a running PnL series.
        """
        if self.trades_df is None or self.trades_df.empty:
            return 0.0
        
        # Construct an equity curve from the trades. This is simplified.
        self.trades_df = self.trades_df.sort_values(by='exit_time')
        self.trades_df['cum_pnl'] = self.trades_df['pnl'].cumsum()
        peak = self.trades_df['cum_pnl'].cummax()
        drawdown = (self.trades_df['cum_pnl'] - peak).min()
        return drawdown  # negative number indicating max drawdown
    # In performance_analyzer.py

    def compute_detailed_metrics(self):
        if self.trades_df is None or self.trades_df.empty:
            return {}

        # Calculate trade PnL for each trade:
        def calculate_trade_pnl(row):
            if row['position_type'] == 'LONG':
                return row['exit_price'] - row['entry_price']
            elif row['position_type'] == 'SHORT':
                return row['entry_price'] - row['exit_price']
            else:
                return 0.0

        self.trades_df['pnl'] = self.trades_df.apply(calculate_trade_pnl, axis=1)

        winners = self.trades_df[self.trades_df['pnl'] > 0]
        losers = self.trades_df[self.trades_df['pnl'] < 0]
        total_trades = len(self.trades_df)
        winning_trades = len(winners)
        losing_trades = len(losers)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_pl = self.trades_df['pnl'].mean()
        largest_win = self.trades_df['pnl'].max()
        largest_loss = self.trades_df['pnl'].min()
        sum_winners = winners['pnl'].sum()
        sum_losers = abs(losers['pnl'].sum())
        profit_factor = (sum_winners / sum_losers) if sum_losers != 0 else float('inf')
        avg_win = winners['pnl'].mean() if not winners.empty else 0
        avg_loss = abs(losers['pnl'].mean()) if not losers.empty else 0
        ratio_avg_win_loss = (avg_win / avg_loss) if avg_loss != 0 else float('inf')

        # Optionally, calculate avg_bar_count if you have time/index data that represents bars.
        avg_bar_count = None  # Replace with your own logic if needed

        stats = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_pl': avg_pl,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'profit_factor': profit_factor,
            'ratio_avg_win_loss': ratio_avg_win_loss,
            'avg_bar_count': avg_bar_count,
        }

        return stats