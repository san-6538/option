import pandas as pd

class Strategy:
    def __init__(self, trigger=0.05, stoploss=0.10):
        self.trigger = trigger
        self.stoploss = stoploss

        self.position_open = False
        self.entry_premium = None
        self.entry_time = None

        self.day_low = None
        self.waiting_for_reentry = False
        self.trade_taken_today = False
        self.current_day = None

        self.trades = []

    def _reset_day_state(self, date):
        """
        Reset all day-specific state variables.
        """
        self.day_low = None
        self.trade_taken_today = False
        self.waiting_for_reentry = False
        self.current_day = date

    def check_entry(self, premium, ma, time):
        """
        Entry check exactly at 09:20 AM IST.
        Only one signal per trading day.
        """
        if self.trade_taken_today:
            return False

        if time.time() != pd.Timestamp("09:20").time():
            return False

        if ma == 0:
            return False

        diff = abs(premium - ma) / ma
        return diff >= self.trigger

    def enter_position(self, premium, time, reason):
        self.position_open = True
        self.entry_premium = premium
        self.entry_time = time
        self.day_low = premium
        self.trade_taken_today = True

        self.trades.append({
            'entry_time': time,
            'entry_premium': premium,
            'exit_time': None,
            'exit_premium': None,
            'reason': reason
        })

    def update_day_low(self, premium):
        if self.day_low is None or premium < self.day_low:
            self.day_low = premium

    def check_exit(self, premium):
        """
        Only stop-loss can exit an active position.
        """
        if not self.position_open:
            return False

        return premium <= self.entry_premium * (1 - self.stoploss)

    def exit_position(self, premium, time, reason):
        """
        Exit current position.
        """
        trade = self.trades[-1]
        trade['exit_time'] = time
        trade['exit_premium'] = premium
        trade['reason'] = reason

        self.position_open = False
        self.entry_premium = None
        self.entry_time = None

        # After stop-loss, allow re-entry at day low
        if reason == "stop_loss":
            self.waiting_for_reentry = True

    def check_reentry(self, premium):
        """
        Re-enter only after stop-loss and only at new day low.
        """
        if not self.waiting_for_reentry:
            return False

        return premium <= self.day_low    
            