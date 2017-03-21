import pandas as pd
import numpy as np
import talib
from pandas_datareader import data
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
import sklearn

#Import open, high, low, close, and volume data from Yahoo using DataReader
OIL = data.DataReader('CFD','yahoo', '2017-01-01') #Import historical stock from 2010 data for training

#Convert Volume from Int to Float
OIL.Volume = OIL.Volume.astype(float)

#Doing that some values are NaN WHY???
OIL['MA50'] = talib.MA(OIL['Close'].values, timeperiod=50, matype=0)
OIL['UPPERBAND'], OIL['MIDDLEBAND'], OIL['LOWERBAND'] = talib.BBANDS(OIL['Close'].values, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

OIL['NextDayPrice'] = OIL['Close'].shift(-1)

#Copy dataframe and clean data

OIL_cleanData = OIL.copy()
OIL_cleanData.dropna(inplace=True)

X_all = OIL_cleanData.ix[:, OIL_cleanData.columns != 'NextDayPrice']  # feature values for all days
y_all = OIL_cleanData['NextDayPrice']  # corresponding targets/labels
#print (X_all.head())  # print the first 5 rows

#Split the data into training and testing sets using the given feature as the target
X_train, X_test, y_train, y_test = sklearn.model_selection.train_test_split(X_all, y_all, test_size=0.30, random_state=42)

#Train Model

from sklearn.linear_model import LinearRegression


#Create a decision tree regressor and fit it to the training set
regressor = LinearRegression()

regressor.fit(X_train,y_train)

print ("Training set: {} samples".format(X_train.shape[0]))
print ("Test set: {} samples".format(X_test.shape[0]))


#Evaluate Model

from sklearn import cross_validation

scores = cross_validation.cross_val_score(regressor, X_test, y_test, cv=10)
print ("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() / 2))    

from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_test, regressor.predict(X_test))
print("MSE: %.4f" % mse)


#Predict

X=OIL[-1:]
print(X)

#print OIL_cleanData