import unittest
from strategy import Strategy
import pandas as pd

class TestStrategy(unittest.TestCase):
    def setUp(self):
        self.strat = Strategy()
    
    def test_entry_check(self):
        time = pd.Timestamp('2023-01-01 09:20:00')
        self.assertTrue(self.strat.check_entry(100, 95, time))  # diff=5.26% >5%
        self.assertFalse(self.strat.check_entry(100, 96, time))  # diff=4.17% <5%
        time_wrong = pd.Timestamp('2023-01-01 09:21:00')
        self.assertFalse(self.strat.check_entry(100, 95, time_wrong))
    
    def test_exit_check(self):
        self.strat.enter_position(100, pd.Timestamp('2023-01-01 09:20:00'))
        self.assertTrue(self.strat.check_exit(89)[0])  # 89 < 90, stop loss
        self.assertEqual(self.strat.check_exit(89)[1], 'stop_loss')
        self.strat.day_low = 95
        self.assertTrue(self.strat.check_exit(95)[0])  # = day low, re-entry
        self.assertEqual(self.strat.check_exit(95)[1], 're_entry')

if __name__ == '__main__':
    unittest.main()