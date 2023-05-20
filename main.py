import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error
import xgboost as xgb

df = pd.read_csv('PJME_hourly.csv')
df = df.set_index('Datetime')
df.index = pd.to_datetime(df.index)
color_pal = sns.color_palette()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    df.plot(style='.',
            figsize=(15, 5),
            color=color_pal[1],
            title='PJME Energy Use in MW')
    #train test and split portion
    #Any data from 2002-2015 (exlusive) will be used as our training data
    train = df.loc[df.index < '01-01-2015']
    test = df.loc[df.index >= '01-01-2015']
    fig, ax = plt.subplots(figsize=(15, 5))
    train.plot(ax=ax, label='Training Data', title='Data Train/Test Split')
    test.plot(ax=ax, label='Testing Data')
    ax.axvline('01-01-2015', color='black', ls='--')
    ax.legend(['Training Data', 'Test Data'])

    df.loc[(df.index > '01-01-2010') & (df.index < '01-08-2010')] \
        .plot(figsize=(15, 5), title='Week Of Data')

    def create_features(df):
        """
        Create time series features based on time series index.
        """
        df = df.copy()
        df['hour'] = df.index.hour
        df['dayofweek'] = df.index.dayofweek
        df['quarter'] = df.index.quarter
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['dayofyear'] = df.index.dayofyear
        df['dayofmonth'] = df.index.day
        df['weekofyear'] = df.index.isocalendar().week
        return df
        df = create_features(df)

    train = create_features(train)
    test = create_features(test)

    FEATURES = ['dayofyear', 'hour', 'dayofweek', 'quarter', 'month', 'year']
    TARGET = 'PJME_MW'

    X_train = train[FEATURES]
    y_train = train[TARGET]

    X_test = test[FEATURES]
    y_test = test[TARGET]

    reg = xgb.XGBRegressor(base_score=0.5, booster='gbtree',
                           n_estimators=1000,
                           early_stopping_rounds=50,
                           objective='reg:linear',
                           max_depth=3,
                           learning_rate=0.01)
    """
        Retrieve the validation scores for the test and train data
        Use the RSME to represent validation score
        The lower the score, the better
        Include a verbose score of 100 to print out a training and validation
        score for every 100 trees that are built
    """
    reg.fit(X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            verbose=100)

    fi = pd.DataFrame(data=reg.feature_importances_,
                      index=reg.feature_names_in_,
                      columns=['importance'])
    fi.sort_values('importance').plot(kind='barh', title='Feature Importance')

    test['prediction'] = reg.predict(X_test)
    df = df.merge(test[['prediction']], how='left', left_index=True, right_index=True)
    ax = df[['PJME_MW']].plot(figsize=(15, 5))
    df['prediction'].plot(ax=ax, style='.')
    plt.legend(['Truth Data', 'Predictions'])
    ax.set_title('Raw Dat and Prediction')
    plt.show()
