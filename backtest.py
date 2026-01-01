from strategy import Strategy
from preprocess import preprocess

def backtest(csv_path):
    df = preprocess(csv_path)
    strategy = Strategy()

    for time, row in df.iterrows():
        premium = row['straddle_premium']
        sma = row['sma_1min']

        # Detect new trading day
        if strategy.current_day != time.date():
            strategy._reset_day_state(time.date())

        # Always update day low
        strategy.update_day_low(premium)

        # Entry at 09:20
        if not strategy.position_open and strategy.check_entry(premium, sma, time):
            strategy.enter_position(premium, time, reason="signal_entry")

        # Stop-loss exit
        if strategy.position_open and strategy.check_exit(premium):
            strategy.exit_position(premium, time, reason="stop_loss")

        # Day-low re-entry
        if not strategy.position_open and strategy.check_reentry(premium):
            strategy.enter_position(premium, time, reason="day_low_reentry")

    # Square-off at end of data
    if strategy.position_open:
        strategy.exit_position(premium, time, reason="end_of_day")

    return strategy.trades