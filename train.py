import xgboost
from sklearn.model_selection import train_test_split

from data import csv2data, feature_select, label_normalization


if __name__ == '__main__':
    train_data = csv2data('datapath')
    
    useless_feature = feature_select(train_data)
    useless_feature += ['系统性能均值','index','block','group_id','diff']

    useful_feature = [i for i in df.columns if i not in useless_feature]

    feature = train_data[useful_feature]
    label = train_data['系统性能均值']

    # memory release
    del train_data

    (
        feature_train, 
        feature_test, 
        label_train, 
        label_test
    ) = train_test_split(feature,label,test_size=0.3, random_state=0)

    model = xgboost.XGBRegressor(
                                    n_estimators=1000, 
                                    max_depth=10, 
                                    eta=0.1, 
                                    subsample=0.7, 
                                    colsample_bytree=0.8,
                                    tree_method='gpu_hist'
                                )

    xgboost_model = model.fit(feature_train, label_train)
    xgboost_model.score(feature_test, label_test)