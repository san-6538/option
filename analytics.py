import numpy as np

def calculate_analytics(trades):
    completed = [t for t in trades if t['exit_time'] is not None]

    if not completed:
        return {}

    pnls = np.array([
        t['exit_premium'] - t['entry_premium']
        for t in completed
    ])

    wins = pnls[pnls > 0]
    losses = pnls[pnls <= 0]

    cumulative = np.cumsum(pnls)
    drawdown = np.maximum.accumulate(cumulative) - cumulative

    durations = [
        (t['exit_time'] - t['entry_time']).total_seconds() / 60
        for t in completed
    ]

    return {
        'total_trades': len(pnls),
        'win_rate': len(wins) / len(pnls),
        'total_pnl': pnls.sum(),
        'avg_pnl': pnls.mean(),
        'max_profit': pnls.max(),
        'max_loss': pnls.min(),
        'profit_factor': (
            wins.sum() / abs(losses.sum())
            if losses.sum() != 0 else 0
        ),
        'sharpe_ratio': (
            pnls.mean() / pnls.std()
            if pnls.std() > 0 else 0
        ),
        'sortino_ratio': (
            pnls.mean() / losses.std()
            if len(losses) > 1 and losses.std() > 0 else 0
        ),
        'max_drawdown': drawdown.max(),
        'avg_trade_duration': np.mean(durations)
    }