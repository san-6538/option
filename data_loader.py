import pandas as pd

def load_data(csv_path):
    """
    Load raw CSV data and prepare datetime index.
    """
    df = pd.read_csv(csv_path)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True)
    df.sort_index(inplace=True)
    return df