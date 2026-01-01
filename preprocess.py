import pandas as pd

def preprocess(csv_path):
    """
    Preprocess raw option data into a clean 1-minute time series
    suitable for the assignment's straddle strategy.
    """
    df = pd.read_csv(csv_path)
    print("CSV columns:", df.columns.tolist())

    
    df['option_type'] = df['Ticker'].str[-2:]
    df['strike'] = df['Ticker'].str.extract(r'(\d{4})(?=CE|PE)', expand=False)
    df['strike'] = pd.to_numeric(df['strike'], errors='coerce')

    
    if 'Date' in df.columns and 'Time' in df.columns:
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
        df.drop(['Date', 'Time'], axis=1, inplace=True)
    elif 'datetime' not in df.columns:
        raise ValueError("CSV must contain 'datetime' column or 'Date' and 'Time' columns. Found: " + str(df.columns.tolist()))

    
    if 'strike' in df.columns:
        strike_mode = df['strike'].mode()
        if not strike_mode.empty:
            df = df[df['strike'] == strike_mode[0]]
            print(f"Selected strike: {strike_mode[0]}")

    
    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'straddle_premium': 'Close'  
    }

    
    df.rename(columns={v: k for k, v in column_mapping.items() if v in df.columns}, inplace=True)

    
    if 'close' not in df.columns and 'straddle_premium' in df.columns:
        df['close'] = df['straddle_premium']

    
    df.set_index('datetime', inplace=True)

    
    df.sort_index(inplace=True)

    ohlcv = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'straddle_premium': 'last'
    }

    df = df.resample('1min').agg(ohlcv)

    
    df[['open', 'high', 'low', 'close', 'straddle_premium']] = (
        df[['open', 'high', 'low', 'close', 'straddle_premium']].ffill()
    )

    
    df['volume'] = df['volume'].fillna(0)

    
    df = df.between_time("09:15", "15:30")

    
    df['sma_1min'] = df['straddle_premium'].expanding().mean()

    
    df['diff'] = (
        (df['straddle_premium'] - df['sma_1min']).abs()
        / df['sma_1min']
    )

    return df
