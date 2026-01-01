from backtest import backtest
from analytics import calculate_analytics
from preprocess import preprocess
from visualization import *
import sys

def main(csv_path):
    trades = backtest(csv_path)
    df = preprocess(csv_path)

    analytics = calculate_analytics(trades)
    print("\nAnalytics:")
    for k, v in analytics.items():
        print(f"{k}: {v}")

    plot_price_with_signals(df, trades)
    plot_equity_curve(trades)
    plot_pnl_distribution(trades)
    plot_monthly_returns(trades)
    plot_trade_analysis(trades)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        csv_path = r"C:\Users\sanit\Downloads\DATA-20260101T064538Z-3-001\DATA\GFDLNFO_24092025 change.csv"
    main(csv_path)