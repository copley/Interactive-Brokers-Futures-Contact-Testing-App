# backtesting_app.py

import json
import pandas as pd

from data_loader import DataLoader
from indicator_calculator import IndicatorCalculator
from strategy_logic import StrategyLogic
from execution_simulator import ExecutionSimulator
from performance_analyzer import PerformanceAnalyzer

def main():
    print("===== Starting Backtesting Application =====")

    # 1) Load config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    # 2) Create DataLoader
    loader = DataLoader(data_path='./data')
    file_map = {
        '1m': 'MES_1_min.csv',
        '5m': 'MES_5_mins.csv',
    }
    timeframes = loader.load_all_timeframes(file_map)
    print("Loaded timeframes:", list(timeframes.keys()))

    # 3) Compute indicators from config
    calculator = IndicatorCalculator()
    ind_cfg = config["indicators"]

    df_1m = calculator.add_indicators(
        timeframes['1m'].copy(),
        short_ema_period = ind_cfg["short_ema_period"],
        medium_ema_period = ind_cfg["medium_ema_period"],
        rsi_period = ind_cfg["rsi_period"],
        atr_period = ind_cfg["atr_period"],
        compute_macd = ind_cfg["compute_macd"],
        compute_stoch = ind_cfg["compute_stoch"]
    ).reset_index()

    df_5m = calculator.add_indicators(
        timeframes['5m'].copy(),
        short_ema_period = ind_cfg["short_ema_period"],
        medium_ema_period = ind_cfg["medium_ema_period"],
        rsi_period = ind_cfg["rsi_period"],
        atr_period = ind_cfg["atr_period"],
        compute_macd = ind_cfg["compute_macd"],
        compute_stoch = ind_cfg["compute_stoch"]
    ).reset_index()

    # 4) Rename columns, merge 1m into 5m
    df_1m = df_1m.rename(columns={
        'EMA_short': 'EMA_short_1m',
        'EMA_medium': 'EMA_medium_1m',
        'RSI': 'RSI_1m',
        'ATR': 'ATR_1m',
        'MACD': 'MACD_1m',
        'MACD_signal': 'MACD_signal_1m',
        'StochK': 'StochK_1m',
        'StochD': 'StochD_1m',
    })
    df_5m = df_5m.rename(columns={
        'EMA_short': 'EMA_short_5m',
        'EMA_medium': 'EMA_medium_5m',
        'RSI': 'RSI_5m',
        'ATR': 'ATR_5m',
        'MACD': 'MACD_5m',
        'MACD_signal': 'MACD_signal_5m',
        'StochK': 'StochK_5m',
        'StochD': 'StochD_5m',
    })

    merged = pd.merge_asof(
        df_5m,
        df_1m[['time','EMA_short_1m','EMA_medium_1m','RSI_1m','ATR_1m',
               'MACD_1m','MACD_signal_1m','StochK_1m','StochD_1m']],
        on='time'
    )
    merged.ffill(inplace=True)
    print("Merged DataFrame head:")
    print(merged.head())
    # 4) Initialize Strategy & Simulator with trailing stop config
    exec_cfg = config["execution"]
    simulator = ExecutionSimulator(
        stop_offset = exec_cfg["stop_offset"],
        target_offset = exec_cfg["target_offset"],
        default_quantity = exec_cfg.get("default_quantity", 1),
        enable_trailing_stop = exec_cfg.get("enable_trailing_stop", False),
        trailing_stop_offset = exec_cfg.get("trailing_stop_offset", 2.0)
    )
    # 5) Initialize Strategy & Simulator
    strategy_config = config["strategy"]
    strategy_logic = StrategyLogic(strategy_config)

    # Pass stop_offset/target_offset from config
    simulator = ExecutionSimulator(
        stop_offset=config["execution"]["stop_offset"],
        target_offset=config["execution"]["target_offset"]
    )

    # 6) Main loop: iterate each bar, check signals, process stop/target
    for idx, row in merged.iterrows():
        bar_time = row['time']
        
        # (A) If outside session, skip new trades, but still check open position
        if not is_within_full_session(bar_time):
            # Check if an open position hits stop/target even outside session
            if simulator.open_position:
                exit_info = simulator.check_stop_loss_or_profit_target(row)
                if exit_info:
                    exit_signal = {
                        'type': 'EXIT',
                        'position_type': simulator.open_position['type'],
                        'exit_price': exit_info['exit_price'],
                        'reason': exit_info['reason']
                    }
                    simulator.process_signal(exit_signal, row)
            continue

        # Build data_point for the bar
        data_point = {
            'time': bar_time,
            'open':  row['open'],
            'high':  row['high'],
            'low':   row['low'],
            'close': row['close'],
            'volume': row['volume']
        }

        # Build multi_indicators for 1m & 5m
        multi_indicators = {
            '1m': {
                'EMA_short': row['EMA_short_1m'],
                'EMA_medium': row['EMA_medium_1m'],
                'RSI': row['RSI_1m'],
                'ATR': row['ATR_1m'],
                'MACD': row['MACD_1m'],
                'MACD_signal': row['MACD_signal_1m'],
                'StochK': row['StochK_1m'],
                'StochD': row['StochD_1m'],
            },
            '5m': {
                'EMA_short': row['EMA_short_5m'],
                'EMA_medium': row['EMA_medium_5m'],
                'RSI': row['RSI_5m'],
                'ATR': row['ATR_5m'],
                'MACD': row['MACD_5m'],
                'MACD_signal': row['MACD_signal_5m'],
                'StochK': row['StochK_5m'],
                'StochD': row['StochD_5m'],
            },
        }

        # 6a) Check for new entry signal
        signal = strategy_logic.check_signal(data_point, multi_indicators)
        if signal:
            # If we get a LONG/SHORT, open the position
            simulator.process_signal(signal, data_point)

        # 6b) If position is open, check for stop-loss or take-profit
        if simulator.open_position:
            exit_info = simulator.check_stop_loss_or_profit_target(data_point)
            if exit_info is not None:
                # That means we must exit the position
                exit_signal = {
                    'type': 'EXIT',
                    'position_type': simulator.open_position['type'],
                    'exit_price': exit_info['exit_price'],
                    'reason': exit_info['reason']
                }
                simulator.process_signal(exit_signal, data_point)

    # 7) Analyze trades
    trades = simulator.trades
    analyzer = PerformanceAnalyzer(trades)
    stats = analyzer.compute_detailed_metrics()

    label = "Two-Timeframe (1m & 5m) - Full 8H Session"
    print(f"\n=== {label} Trades ===")
    print(f"Total Trades:          {stats.get('total_trades', 0)}")
    print(f"Winners / Losers:      {stats.get('winning_trades', 0)} / {stats.get('losing_trades', 0)}")
    print(f"Win Rate:              {stats.get('win_rate', 0):.2f}%")
    print(f"Avg P/L:               {stats.get('avg_pl', 0):.2f}")
    print(f"Largest Win:           {stats.get('largest_win', 0):.2f}")
    print(f"Largest Loss:          {stats.get('largest_loss', 0):.2f}")
    print(f"Profit Factor:         {stats.get('profit_factor', 0):.3f}")
    print(f"Avg Win / Avg Loss:    {stats.get('ratio_avg_win_loss', 0):.3f}")
    if stats.get("avg_bar_count") is not None:
        print(f"Avg # bars in trades:  {stats['avg_bar_count']:.1f}")

def is_within_full_session(bar_time):
    """Example session: 9:30 to 17:30 local/ET."""
    if bar_time.hour < 9:
        return False
    if bar_time.hour == 9 and bar_time.minute < 30:
        return False
    if bar_time.hour > 17:
        return False
    if bar_time.hour == 17 and bar_time.minute >= 30:
        return False
    return True

if __name__ == "__main__":
    main()
