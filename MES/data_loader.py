import pandas as pd
import os

class DataLoader:
    """
    Reads historical market data (from CSV in this example) for multiple
    timeframes (1m, 5m, 30m, 1h).
    """
    def __init__(self, data_path: str = '.'):
        self.data_path = data_path

    def load_data(self, file_name: str) -> pd.DataFrame:
        """
        Load CSV data containing at least columns:
        ['time', 'open', 'high', 'low', 'close', 'volume'].
        The 'time' column should be parseable as a datetime.
        """
        csv_path = os.path.join(self.data_path, file_name)
        df = pd.read_csv(csv_path, parse_dates=['time'], index_col='time')
        df = df.sort_index()
        # Ensure columns are in the correct order; fill missing with 0 or ffill if needed
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()
        df.dropna(inplace=True)
        return df

    def load_all_timeframes(self, file_map: dict) -> dict:
        {
            '1m': 'MES_1_min.csv',
            '5m': 'MES_5_mins.csv',
            '30m': 'MES_30_mins.csv',
            '1h': 'MES_1_hour.csv'
        }
        dataframes = {}
        for tf, file_name in file_map.items():
            df = self.load_data(file_name)
            dataframes[tf] = df
        return dataframes
