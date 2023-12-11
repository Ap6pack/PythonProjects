from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import sklearn

def load_housing_data():
    file_path = Path('/home/localhost/Projects/PythonProjects/Machine_Learning/')
    return pd.read_csv(Path("Datasets/housing.csv"))

housing = load_housing_data()

housing.hist(bins=50, figsize=(20,15))
plt.show()
print(housing.describe())