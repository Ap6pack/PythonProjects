from hhos import HHOSSA  # Assume HHOSSA is implemented in this module

def select_features(df):
    """Select the most significant attributes using HHOSSA."""
    hhos = HHOSSA()
    selected_features = hhos.select(df)
    return df[selected_features]

if __name__ == "__main__":
    from data_preprocessing import preprocess_data
    
    file_path = 'path_to_dataset/DAPT_2020.csv'
    df = preprocess_data(file_path)
    df_selected = select_features(df)
    print(df_selected.head())
