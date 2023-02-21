from sklearn.preprocessing import StandardScaler

from data import csv2data

if __name__ == '__main__':
    test_data = csv2data('test_csv_path')
    model = xgboost.load('model_path')
    
    featur_list = [] # add feature list here, same as feature used in train
    
    predict = model.predict(test_data[featur_list])

    label_cleaner = StandardScaler()
    predict = label_cleaner.inverse_transform(predict)
    df['pred'] = predict
    df.to_csv('csv_path')
