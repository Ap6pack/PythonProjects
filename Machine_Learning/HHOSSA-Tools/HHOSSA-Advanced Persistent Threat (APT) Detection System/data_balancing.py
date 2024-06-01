from imblearn.over_sampling import SMOTE

def balance_data(df, target_column):
    """Balance the dataset using HHOSSA-SMOTE."""
    smote = SMOTE()
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_res, y_res = smote.fit_resample(X, y)
    df_resampled = pd.concat([X_res, y_res], axis=1)
    return df_resampled

if __name__ == "__main__":
    from feature_selection import select_features
    from data_preprocessing import preprocess_data
    
    file_path = 'path_to_dataset/DAPT_2020.csv'
    df = preprocess_data(file_path)
    df_selected = select_features(df)
    df_balanced = balance_data(df_selected, 'target')
    print(df_balanced.head())
