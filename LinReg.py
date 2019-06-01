#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 23:18:14 2019

@author: abhishek
"""
import os

from EDA import EDA
import quandl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge, Lasso

quandl.ApiConfig.api_key = "rR9RqufYNmrUGvb-as-G"

INSTRUMENT = 'ETFs/spy.us.txt'

INDICES = ['CME_GC1', 'CBOE_VX1', 'ICE_DX1', 'CME_SP1', 'CME_NG1', 'CME_CL1']
MARKET_FEATURES = ['CHRIS/' + item for item in INDICES]


def standardize(df):
    scaler = preprocessing.StandardScaler()
    columns = df.columns
    
    scaled_df = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_df, columns=columns)
    
    return scaled_df


def linear_regression(df, features=None, target=None, regularization=None,
                      debug=None):
    X = pd.DataFrame(df[features])    
    y = pd.DataFrame(df[target])
  
    X = standardize(X)
    y = standardize(y)

    if debug:
        print(f"Shape X = {X.shape}, y = {y.shape}")

    if regularization:
        if regularization.lower() == 'l1':
            model = Lasso(alpha=0.1)
        elif regularization.lower() == 'l2':
            model = Ridge(alpha=0.01)
    else:
        model = LinearRegression()
    
    """ Do not use KFold CV. Its not logical to use data from 2014 and 2016 to
    predict 2015.
    scores = []
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    
    for i, (train, test) in enumerate(kfold.split(X, y)):
        model.fit(X.iloc[train,:], y.iloc[train,:])
        if debug:
            print(f'Intercept and Coeffs: {model.intercept_}, {model.coef_}')
        scores.append(model.score(X.iloc[test,:], y.iloc[test,:]))
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,
                                                        random_state=0)
    model.fit(X_train, y_train)
    scores = (model.score(X_test, y_test))
    
    if debug:
        print(f'Scores ({features}, {target}): {scores}')
    else:
        if regularization:
            print(f'{regularization} scores: {scores}')
        else:
            print(f'Scores: {scores}')
    
    if X.shape == y.shape:
        plt.scatter(X, y)
        plt.show()


def add_market_features(df, args, start_date=None, end_date=None):
    if start_date and end_date:
        for arg in args:
            try:
                feature = quandl.get(arg, start_date=start_date, 
                                     end_date=end_date)
                feature.rename(columns={name:arg + ' ' + name 
                                        for name in feature.columns},
                               inplace=True)
                df = df.join(feature)
            except Exception as e:
                print(f'{e}')
                return
    else:
        print('No start and end date provided')
        return

    return df


def techical_indicators_linreg(df):
    df = df.fillna(method='backfill')
    
    features = list(df.columns)[12:]
    linear_regression(df, features=features, target='Close_open')
    linear_regression(df, features=features, target='Close_open', 
                      regularization='L1')
    linear_regression(df, features=features, target='Close_open', 
                      regularization='L2')    


def macro_indicators_linreg(df):
    df = add_market_features(df, MARKET_FEATURES, start_date=df.index[0],
                             end_date=df.index[-1])

    df = df.fillna(method='backfill')

    df = df.interpolate(method='linear')
    
    if np.isnan(df.values).any():
        print('NaN values still present, abort...')
        return

    features = list(df.columns)[12:]
    linear_regression(df, features=features, target='Close_open')
    linear_regression(df, features=features, target='Close_open', 
                      regularization='L1')
    linear_regression(df, features=features, target='Close_open', 
                      regularization='L2')

def main():
    #os.chdir(PROJ_DIR)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    df = EDA(INSTRUMENT, False, True)
    techical_indicators_linreg(df)

    df = EDA(INSTRUMENT)
    macro_indicators_linreg(df)


if __name__ == '__main__':
    main()

#df = EDA('ETFs/spy.us.txt', True, '2016-01-01', '2016-01-20')
#print(df['Close_close'])
#print(df['Close_close'].interpolate()
#linear_regression(df, input='Close_close', target='Close_open')

#df = df.fillna(method='backfill')

#for column in df.columns:
#    if column not in ['Close_open']:
#        LinReg(df, input=column, target='Close_open')

#df = EDA('ETFs/spy.us.txt')

#macro_indicators_linreg('ETFs/spy.us.txt')
#df = df.fillna(method='backfill')

#print(df.info())
#print(df.head())

#df.to_csv(path_or_buf='spy_test.csv', sep=',')

#for column in df.columns:
#    if column not in ['Close_open', 'OpenInt']:
#        linear_regression(df, free=column, target='Close_open')
