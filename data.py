import os

import pandas as pd

from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler


def csv2data(csv_path: str):
    sys_list = []
    for file in sorted(os.listdir(csv_path)):
        data = pd.read_csv(os.path.join(path,file))
        data['group'] = file
        sys_list.append(data)
    train_data = pd.concat(sys_list)
    return train_data

def feature_select(train_data: pd.DataFrame):
    selector = VarianceThreshold(threshold=0.0)
    selector.fit(df)
    useless = set(selector.feature_names_in_) - set(selector.get_feature_names_out())
    return list(useless)

def label_normalization(train_data: pd.DataFrame):
    label_cleaner = StandardScaler()
    train_data[['系统性能均值']] = label_cleaner.fit_transform(df[['系统性能均值']])
    return train_data
