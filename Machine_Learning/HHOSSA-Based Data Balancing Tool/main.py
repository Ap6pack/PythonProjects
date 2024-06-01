import sys
from data_preprocessing import load_and_preprocess_data
from hhosmote import hhosmote

def main(file_path):
    X_train, X_test, y_train, y_test = load_and_preprocess_data(file_path)
    X_balanced, y_balanced = hhosmote(X_train, y_train)
    
    # Save the balanced dataset
    import pandas as pd
    balanced_data = pd.DataFrame(X_balanced)
    balanced_data['target'] = y_balanced
    balanced_data.to_csv('balanced_dataset.csv', index=False)
    
    print("Balanced dataset saved to 'balanced_dataset.csv'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_dataset>")
    else:
        main(sys.argv[1])
