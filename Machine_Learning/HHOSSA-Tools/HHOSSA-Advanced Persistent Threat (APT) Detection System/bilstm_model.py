import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split

def train_bilstm(df, target_column):
    """Train Bi-LSTM model."""
    X = df.drop(columns=[target_column]).values
    y = df[target_column].values
    X = X.reshape((X.shape[0], 1, X.shape[1]))  # Reshaping to (samples, timesteps, features)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = Sequential()
    model.add(LSTM(128, return_sequences=True, input_shape=(1, X_train.shape[2])))
    model.add(LSTM(128))
    model.add(Dense(1, activation='sigmoid'))
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test))
    
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Bi-LSTM Accuracy: {accuracy}")
    
    return model

if __name__ == "__main__":
    from data_balancing import balance_data
    
    file_path = 'path_to_dataset/DAPT_2020.csv'
    df = preprocess_data(file_path)  # Ensure this function is defined
    df_selected = select_features(df)  # Ensure this function is defined
    df_balanced = balance_data(df_selected, 'target')  # Ensure correct import and usage
    model = train_bilstm(df_balanced, 'target')