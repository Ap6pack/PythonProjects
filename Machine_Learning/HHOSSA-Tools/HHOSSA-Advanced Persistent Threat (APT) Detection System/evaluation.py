from sklearn.metrics import accuracy_score, roc_auc_score, precision_recall_curve, auc

def evaluate_model(model, X_test, y_test):
    """Evaluate the model using various metrics."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred)
    precision, recall, _ = precision_recall_curve(y_test, y_pred)
    prc_auc = auc(recall, precision)
    
    return {
        "accuracy": accuracy,
        "roc_auc": roc_auc,
        "prc_auc": prc_auc
    }

if __name__ == "__main__":
    from lightgbm_model import train_lightgbm
    
    file_path = 'path_to_dataset/DAPT_2020.csv'
    df = preprocess_data(file_path)
    df_selected = select_features(df)
    df_balanced = balance_data(df_selected, 'target')
    model = train_lightgbm(df_balanced, 'target')
    
    X_test = df_balanced.drop(columns=['target']).values
    y_test = df_balanced['target'].values
    metrics = evaluate_model(model, X_test, y_test)
    print(metrics)
