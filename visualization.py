import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def plot_price_with_signals(df, trades):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(df.index, df['straddle_premium'], label='Straddle Premium')
    ax.plot(df.index, df['sma_1min'], label='MA', linestyle='--')
    
    for trade in trades:
        if trade['entry_time']:
            ax.scatter(trade['entry_time'], trade['entry_premium'], color='green', marker='^', s=100, label='Entry')
        if trade['exit_time']:
            color = 'red' if trade['exit_premium'] < trade['entry_premium'] else 'blue'
            ax.scatter(trade['exit_time'], trade['exit_premium'], color=color, marker='v', s=100, label='Exit')
    
    ax.set_title('Price with Signals')
    ax.legend()
    plt.savefig('output/price_signals.png')
    plt.show()

def plot_equity_curve(trades):
    if not trades:
        return
    completed = [t for t in trades if t['exit_time']]
    pnls = [t['exit_premium'] - t['entry_premium'] for t in completed]
    cumulative = np.cumsum(pnls)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(cumulative, label='Equity Curve')
    peak = np.maximum.accumulate(cumulative)
    drawdown = peak - cumulative
    ax.fill_between(range(len(cumulative)), 0, -drawdown, color='red', alpha=0.3, label='Drawdown')
    ax.set_title('Equity Curve with Drawdown')
    ax.legend()
    plt.savefig('output/equity_curve.png')
    plt.show()

def plot_pnl_distribution(trades):
    if not trades:
        return
    completed = [t for t in trades if t['exit_time']]
    pnls = [t['exit_premium'] - t['entry_premium'] for t in completed]
    
    plt.figure(figsize=(10, 6))
    sns.histplot(pnls, kde=True)
    plt.title('PnL Distribution')
    plt.xlabel('PnL')
    plt.savefig('output/pnl_distribution.png')
    plt.show()

def plot_monthly_returns(trades):
    # Since intraday, group by day
    if not trades:
        return
    completed = [t for t in trades if t['exit_time']]
    df_trades = pd.DataFrame(completed)
    df_trades['date'] = df_trades['exit_time'].dt.date
    daily_pnl = df_trades.groupby('date')['exit_premium'].sum() - df_trades.groupby('date')['entry_premium'].sum()
    
    # Heatmap by month/day
    daily_pnl = daily_pnl.reset_index()
    daily_pnl['month'] = pd.to_datetime(daily_pnl['date']).dt.month
    daily_pnl['day'] = pd.to_datetime(daily_pnl['date']).dt.day
    pivot = daily_pnl.pivot(index='month', columns='day', values='exit_premium')
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, cmap='RdYlGn')
    plt.title('Monthly Returns Heatmap')
    plt.savefig('output/monthly_returns.png')
    plt.show()

def plot_trade_analysis(trades):
    if not trades:
        return
    completed = [t for t in trades if t['exit_time']]
    df_trades = pd.DataFrame(completed)
    df_trades['pnl'] = df_trades['exit_premium'] - df_trades['entry_premium']
    df_trades['duration'] = (df_trades['exit_time'] - df_trades['entry_time']).dt.total_seconds() / 60
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # PnL over time
    axes[0,0].plot(df_trades['exit_time'], df_trades['pnl'])
    axes[0,0].set_title('PnL Over Time')
    
    # Duration distribution
    axes[0,1].hist(df_trades['duration'], bins=20)
    axes[0,1].set_title('Trade Duration Distribution')
    
    # Win/Loss
    win_loss = df_trades['pnl'] > 0
    axes[1,0].pie([sum(win_loss), sum(~win_loss)], labels=['Wins', 'Losses'], autopct='%1.1f%%')
    axes[1,0].set_title('Win/Loss Ratio')
    
    # Cumulative PnL
    axes[1,1].plot(np.cumsum(df_trades['pnl']))
    axes[1,1].set_title('Cumulative PnL')
    
    plt.tight_layout()
    plt.savefig('output/trade_analysis.png')
    plt.show()