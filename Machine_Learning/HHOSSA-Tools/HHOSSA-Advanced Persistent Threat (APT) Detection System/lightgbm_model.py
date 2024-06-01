import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_lightgbm(df, target_column):
    """Train Light GBM model."""
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = lgb.LGBMClassifier()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Light GBM Accuracy: {accuracy}")
    
    return model

if __name__ == "__main__":
    from data_balancing import balance_data
    
    file_path = 'path_to_dataset/DAPT_2020.csv'
    df = preprocess_data(file_path)
    df_selected = select_features(df)
    df_balanced = balance_data(df_selected, 'target')
    model = train_lightgbm(df_balanced, 'target')
