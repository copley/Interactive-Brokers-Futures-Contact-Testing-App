import pandas as pd
import matplotlib.pyplot as plt

class ResultsAndReporting:
    """
    Outputs trade logs, visualizes performance, etc.
    """
    def __init__(self, trades):
        self.trades = trades
        self.trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()

    def save_trades_to_csv(self, file_path: str):
        """Save the trades DataFrame to a CSV file."""
        if not self.trades_df.empty:
            self.trades_df.to_csv(file_path, index=False)
            print(f"Trades have been saved to {file_path}")

