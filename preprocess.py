import pandas as pd

def preprocess(csv_path):
    """
    Preprocess raw option data into a clean 1-minute time series
    suitable for the assignment's straddle strategy.
    """

    # ------------------------------------------------------------
    # 1. Load raw CSV and parse datetime
    # ------------------------------------------------------------
    df = pd.read_csv(csv_path)

    # Print columns for debugging
    print("CSV columns:", df.columns.tolist())

    # Parse Ticker to extract strike and option type
    df['option_type'] = df['Ticker'].str[-2:]
    df['strike'] = df['Ticker'].str.extract(r'(\d{4})(?=CE|PE)', expand=False)
    df['strike'] = pd.to_numeric(df['strike'], errors='coerce')

    # Handle separate date and time columns
    if 'Date' in df.columns and 'Time' in df.columns:
        df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], dayfirst=True)
        df.drop(['Date', 'Time'], axis=1, inplace=True)
    elif 'datetime' not in df.columns:
        raise ValueError("CSV must contain 'datetime' column or 'Date' and 'Time' columns. Found: " + str(df.columns.tolist()))

    # Select the most common strike (assuming ATM)
    if 'strike' in df.columns:
        strike_mode = df['strike'].mode()
        if not strike_mode.empty:
            df = df[df['strike'] == strike_mode[0]]
            print(f"Selected strike: {strike_mode[0]}")

    # Assume standard column names; adjust if needed
    column_mapping = {
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'straddle_premium': 'Close'  # Use Close as straddle premium for selected strike
    }

    # Rename columns if they exist
    df.rename(columns={v: k for k, v in column_mapping.items() if v in df.columns}, inplace=True)

    # Ensure 'close' column exists (for OHLC aggregation)
    if 'close' not in df.columns and 'straddle_premium' in df.columns:
        df['close'] = df['straddle_premium']

    # Set datetime as index
    df.set_index('datetime', inplace=True)

    # ------------------------------------------------------------
    # 2. CRITICAL STEP: sort by time before any time-based operation
    # ------------------------------------------------------------
    df.sort_index(inplace=True)

    # ------------------------------------------------------------
    # 3. Resample to 1-minute timeframe (assignment requirement)
    # ------------------------------------------------------------
    ohlcv = {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'straddle_premium': 'last'
    }

    df = df.resample('1min').agg(ohlcv)

    # ------------------------------------------------------------
    # 4. Conservative handling of missing minutes
    # ------------------------------------------------------------
    # Forward-fill state variables; do not fabricate prices
    df[['open', 'high', 'low', 'close', 'straddle_premium']] = (
        df[['open', 'high', 'low', 'close', 'straddle_premium']].ffill()
    )

    # Volume is cumulative per minute; missing minutes imply zero trades
    df['volume'] = df['volume'].fillna(0)

    # ------------------------------------------------------------
    # 5. Restrict to regular Indian market hours
    # ------------------------------------------------------------
    df = df.between_time("09:15", "15:30")

    # ------------------------------------------------------------
    # 6. Indicator: 1-minute Simple Moving Average (literal requirement)
    # ------------------------------------------------------------
    # Use expanding mean as per assignment example
    df['sma_1min'] = df['straddle_premium'].expanding().mean()

    # ------------------------------------------------------------
    # 7. Percentage deviation from SMA (assignment trigger)
    # ------------------------------------------------------------
    df['diff'] = (
        (df['straddle_premium'] - df['sma_1min']).abs()
        / df['sma_1min']
    )

    return df
