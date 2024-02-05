import pandas as pd

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    """
    Calculate Bollinger Bands for a given DataFrame.

    Parameters:
    - data (pd.DataFrame): DataFrame with 'Close' column.
    - window (int): Rolling window size for moving average.
    - num_std_dev (int): Number of standard deviations for upper and lower bands.

    Returns:
    - pd.DataFrame: DataFrame with 'UpperBand', 'MiddleBand', and 'LowerBand' columns added.
    """
    # Calculate the rolling mean and standard deviation
    data['MiddleBand'] = data['Close'].rolling(window=window).mean()
    data['UpperBand'] = data['MiddleBand'] + num_std_dev * data['Close'].rolling(window=window).std()
    data['LowerBand'] = data['MiddleBand'] - num_std_dev * data['Close'].rolling(window=window).std()

    return data

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculate Moving Average Convergence Divergence (MACD) for a given DataFrame.

    Parameters:
    - data (pd.DataFrame): DataFrame with 'Close' column.
    - short_window (int): Short-term moving average window size.
    - long_window (int): Long-term moving average window size.
    - signal_window (int): Signal line window size.

    Returns:
    - pd.DataFrame: DataFrame with 'MACD', 'SignalLine', and 'MACD_Histogram' columns added.
    """
    # Calculate short-term and long-term exponential moving averages
    data['ShortEMA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['LongEMA'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Calculate MACD line
    data['MACD'] = data['ShortEMA'] - data['LongEMA']

    # Calculate Signal line
    data['SignalLine'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()

    # Calculate MACD Histogram
    data['MACD_Histogram'] = data['MACD'] - data['SignalLine']

    return data
