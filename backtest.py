from strategy import Strategy
from preprocess import preprocess

def backtest(csv_path):
    df = preprocess(csv_path)
    strategy = Strategy()

    for time, row in df.iterrows():
        premium = row['straddle_premium']
        sma = row['sma_1min']

        
        if strategy.current_day != time.date():
            strategy._reset_day_state(time.date())

        
        strategy.update_day_low(premium)

        
        if not strategy.position_open and strategy.check_entry(premium, sma, time):
            strategy.enter_position(premium, time, reason="signal_entry")

        
        if strategy.position_open and strategy.check_exit(premium):
            strategy.exit_position(premium, time, reason="stop_loss")

        
        if not strategy.position_open and strategy.check_reentry(premium):
            strategy.enter_position(premium, time, reason="day_low_reentry")

    
    if strategy.position_open:
        strategy.exit_position(premium, time, reason="end_of_day")

    return strategy.trades
