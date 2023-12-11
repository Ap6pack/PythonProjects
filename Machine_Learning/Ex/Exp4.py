from sklearn.model_selection import train_test_split
import pandas as pd
from Exp1 import housing, plt
from Exp2 import np

train_set, test_set = train_test_split(housing, test_size=0.2, random_state=42)

housing["income_cat"] = pd.cut(housing["median_income"], bins=[0., 1.5, 3.0, 4.5, 6., np.inf], labels=[1, 2, 3, 4, 5])

housing["income_cat"].hist()
plt.show()