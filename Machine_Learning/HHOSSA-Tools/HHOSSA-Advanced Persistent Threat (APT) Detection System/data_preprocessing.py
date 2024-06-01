import pandas as pd
import numpy as np

def load_data(file_path):
    """Load the dataset from a CSV file."""
    return pd.read_csv(file_path)

def clean_data(df):
    """Clean the dataset by handling missing values."""
    df.fillna(method='ffill', inplace=True)
    return df

def feature_engineering(df):
    """Extract time-domain statistical features and relevant data attributes."""
    # Example: Add your own feature engineering steps here
    df['feature1'] = df['raw_feature'].apply(lambda x: np.mean(x))
    return df

def preprocess_data(file_path):
    """Load, clean, and preprocess the dataset."""
    df = load_data(file_path)
    df = clean_data(df)
    df = feature_engineering(df)
    return df

if __name__ == "__main__":
    file_path = 'path_to_dataset/DAPT_2020.csv'
    df = preprocess_data(file_path)
    print(df.head())
