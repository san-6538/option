def sma(series, window=1):
    return series.rolling(window).mean()