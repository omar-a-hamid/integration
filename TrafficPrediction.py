
##################################################################################################################

################################################# IMPORTS ########################################################

##################################################################################################################

import pandas as pd
import numpy as np
import os
import typing
import matplotlib.pyplot as plt

import pickle

from tensorflow import keras
import tensorflow as tf
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from tensorflow.keras import initializers

from keras.preprocessing.sequence import TimeseriesGenerator
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import mean_squared_error
import math

from tensorflow.keras.models import load_model


import typing
import time
from datetime import datetime
from datetime import timedelta
from sklearn.metrics import mean_squared_error
from math import sqrt
plt.rcParams["figure.figsize"] = (30,15)


##################################################################################################################

################################################## MACROS ########################################################

##################################################################################################################
HISTORICAL_DATA_FILE_PATH = "new_traffic_data.csv"
LSTM_FILE_PATH = 'LSTMS_7steps.h5'
SMOOTHING_FACTOR = 10
FREQ_GROUPER = '16T'
NEW_DATA_HISTORICAL = -100
FEATURES_COUNT = 634                    


##################################################################################################################

############################################### DATASET CLASS #####################################################

##################################################################################################################

class DataSet:
    def __init__(self, dataset = None,file_path = None ,folder_path = None,preprocessed = False,
        box_pts = 0,  convMode = 'same', freqGrouper= '16T',nanThreshold=0.2, varianceThreshold=100):
        
        self.folder_path = folder_path
        self.file_path = file_path
        self.box_pts = box_pts
        self.convMode = convMode
        self.freqGrouper= freqGrouper
        self.nanThreshold=nanThreshold
        self.varianceThreshold=varianceThreshold
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
        self.pd_DataFrame = pd.DataFrame() 



        self.data = dataset if dataset is not None else pd.DataFrame() 
        
        self.data = self.load_data() if self.folder_path is not None else self.data

        if self.file_path is not None:
            self.data = pd.read_csv(self.file_path , index_col='dateandtime',parse_dates=True) 
            self.pd_DataFrame = self.data
        else:
            self.data

        self.data = self.preprocessing() if preprocessed == False else ...

        
        if(box_pts != 0 ):
            self.data = self.smooth()
        else: 
            ...
        self.data = self.normalize()

    def load_data(self):
        df = pd.DataFrame()
        for path in self.folder_path:
            for file_name in os.listdir(path):
                try:
                    temp = pd.read_csv(path + "//" + file_name, index_col='dateandtime',parse_dates=True)
                    df = pd.concat([df, temp])
                except:
                    print(file_name)
                
        df = pd.pivot_table(df,index = 'dateandtime', values ='spdK/m' , columns ='edge')
        df = df.groupby([pd.Grouper(level='dateandtime'
                                       , freq = '16T'  #one reading every X freq
                                      )]).mean()
        self.pd_DataFrame = df
        return df
    
    
    def add_new_data(self, new_data = None):
        # csv_filename = csv_filename if csv_filename is not None else self.file_path
        # new_data = pd.read_csv(csv_filename , index_col='dateandtime',parse_dates=True)

        # new_data = new_data.fillna(new_data.max())

        # extended_datetime_index = pd.date_range(end=time.time() + pd.Timedelta(self.freqGrouper), 
        #                                         periods=len(new_data), 
        #                                         freq=self.freqGrouper)

        # self.time = self.time.append(extended_datetime_index)
         

        concat_data = pd.concat([self.pd_DataFrame, new_data], axis=0, ignore_index=True)  
        # concat_data = concat_data.groupby([
        #                 pd.Grouper(level='dateandtime'

        #                            , freq = self.freqGrouper  #one reading every X freq
        #                           )]).mean() 

        # print(len(self.pd_DataFrame))       
        # print(new_data.index[0])       
        # print(len(concat_data))       

        extended_datetime_index = pd.date_range(end=new_data.index[0] + pd.Timedelta(self.freqGrouper), 
                                                periods=len(self.pd_DataFrame) , 
                                                freq=self.freqGrouper) 

        extended_datetime_index = extended_datetime_index.append(pd.date_range(start=extended_datetime_index[-1] + pd.Timedelta('1T') , 
                                                periods=len(new_data) , 
                                                freq='1T'))


        self.pd_DataFrame = concat_data.fillna(concat_data.max())
        self.pd_DataFrame.index = extended_datetime_index
        self.pd_DataFrame.index.name = 'dateandtime'
        # self.time = extended_datetime_index

        new_data= self.pd_DataFrame

        self.data = self.preprocessing(new_data)
        try:
            if(self.box_pts != 0 ):
                new_data = self.smooth(new_data)
            else: 
                ...
        except:
            print("...")
        new_data = self.normalize(new_data)
        self.data = new_data # Concatenate arrays
        
        return self.data
    
                    
    def preprocessing(self, dataset = None, nanThreshold = None, varianceThreshold = None):
        dataset = dataset if dataset is not None else self.data
        nanThreshold = nanThreshold if nanThreshold is not None else self.nanThreshold
        varianceThreshold = varianceThreshold if varianceThreshold is not None else self.varianceThreshold

        try:
            dataset = dataset.groupby([
                        pd.Grouper(level='dateandtime'
                                   , freq = self.freqGrouper  #one reading every X freq
                                  )]).mean()
        except Exception as e:
            print("error",e)
                    
        if nanThreshold != 0:

            limitPer = len(dataset) * nanThreshold
            dataset = dataset.dropna(thresh=limitPer, axis=1) #drop edges with NAN values > 80%

        else:
            df = dataset
        # Compute the variance of each column in the dataframe
        df = dataset.fillna(dataset.max())
        df = df.loc[:, (dataset != 0).any(axis=0)]
        variances = df.var()

        # Find the columns with variances greater than 100
        
        if varianceThreshold != 0:
        
            high_variances = variances[variances > varianceThreshold]  

            dataset = df.loc[:, high_variances.index[:FEATURES_COUNT]]

        else:
            dataset = df.loc[:,df.index[:FEATURES_COUNT]]

        self.time  = dataset.index
        self.edges = dataset.columns 

        return dataset
        
        #Smooth curve
    def smooth(self, dataset = None):
        dataset = dataset if dataset is not None else self.data
        smoothed_ds = []
        for cntrDf in range(0, self.data.shape[-1]):
            box = np.ones(self.box_pts)/self.box_pts
            temp = np.convolve(dataset.values[:,cntrDf], box, mode=self.convMode)
            smoothed_ds.append(temp)
        dataset = np.array(smoothed_ds).T
        return dataset
    
    def normalize(self, dataset = None):
        dataset = dataset if dataset is not None else self.data
        # normalize the dataset
        dataset = self.scaler.fit_transform(np.array(dataset))
        return dataset


        
##################################################################################################################

################################################# LSTM CLASS #####################################################

##################################################################################################################


class LSTM_Model:
    
    def __init__(self,Data, split_ratio=0.5, valid_ratio=0.5, epochs = 500, hidden_states = 170, lookback=42, predict = 7):
        self.class_dataset = Data
        self.data   = Data.data
        self.time   = Data.time
        self.edges  = Data.edges
        self.scaler = Data.scaler
        self.freqGrouper = Data.freqGrouper
    
        self.ratio  = split_ratio
        self.epochs = epochs
        
        self.hidden_states = hidden_states
        self.lookback = lookback
        self.predict = predict
        self.valid_ratio = valid_ratio
        
        self.callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)

        self.dataX = []
        self.dataY = []
    
    def shuffle_time_series(self,dataset=None, periodicity = 90):
        
        dataset = dataset if dataset is not None else self.data

        data_length = len(dataset[:,0])
        num_segments = data_length // periodicity

        # Split the data into segments
        segments = np.split(dataset[:num_segments * periodicity,:], num_segments)

        # Shuffle the segments
        np.random.shuffle(segments)

        # Concatenate the shuffled segments
        shuffled_data = np.concatenate(segments)
        return shuffled_data

    
    def train_test_split(self,dataset=None):
        dataset = dataset if dataset is not None else self.data

        length = np.asarray(dataset).shape[0] 

        train_size = int(length * self.ratio)
        test_size = length - train_size
        self.train = np.asarray(dataset[:train_size])
        self.test =  np.asarray(dataset[train_size:])
        return self.train, self.test

    # convert an array of values into a dataset matrix
    def create_dataset(self, dataset=None, look_back=None,predict=None):
        ls_x =[]
        ls_y =[]
        
        dataset = dataset if dataset is not None else self.data
        look_back = look_back if look_back is not None else self.lookback
        predict = predict if predict is not None else self.predict
        
        for i in range(look_back, len(dataset)-predict+1):
            a = dataset[i-look_back:i, :]
            ls_x.append(a)
            ls_y.append(dataset[i + predict-1, :])
        
        # reshape input to be [samples, time steps, features]
        self.dataX = np.array(ls_x)
        self.dataX = np.reshape(self.dataX, (self.dataX.shape[0], self.dataX.shape[1], self.dataX.shape[-1]))
        self.dataY = np.array(ls_y)
        
        return self.dataX, self.dataY

    def create_model(self,lookback=None,train=None,hidden_states=None,learning_rate = 0.001):
        
        lookback = lookback if lookback is not None else self.lookback
        train = train if train is not None else self.dataX
        hidden_states = hidden_states if hidden_states is not None else self.hidden_states
        # How many record to take into account
        features = train.shape[-1]


        # Define the model
        self.model = Sequential()

        # Add LSTM layers
        self.model.add(LSTM(hidden_states, 
                            return_sequences=True, 
                            input_shape=(lookback,features)))
        self.model.add(LSTM( int(hidden_states/2), return_sequences=True))   # Add feedforward hidden layer
        self.model.add(LSTM(int(hidden_states/2)))   # Add feedforward hidden layer
        
        # Add feedforward hidden layer    
        self.model.add(Dense(int(2*features), activation='relu'))
        
        self.model.add(Dropout(0.1))

        # Add output layer
        self.model.add(Dense(features))

        # Compile the model
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss='mean_absolute_error')
        
    def train_model(self,look_back=None,predict=None,hidden_states=170,train=None,val=None,test=None):
        look_back = look_back if look_back is not None else self.lookback
        predict = predict if predict is not None else self.predict

        if train is not None:
            ...
        else:
            train, test = self.train_test_split()
            # val,test  = self.train_test_split(ds)

        self.trainX, self.trainY  = self.create_dataset(train,look_back ,predict)
        # self.val_X,  self.val_Y   = self.create_dataset(val,look_back ,predict)
        self.test_X, self.test_Y  = self.create_dataset(test,look_back ,predict)

        callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=20)


        self.create_model(look_back,self.trainX,hidden_states)


        history = self.model.fit(self.trainX,self.trainY,epochs=self.epochs, 
                  validation_split=0.2,
                  # batch_size = 120,
                  callbacks=callback
                  )


        trainPredict = self.model.predict(self.trainX)
        # validPredict = self.model.predict(self.val_X)
        testPredict = self.model.predict(self.test_X)

        mse_values = []

        try:
                # calculate root mean squared error
            trainScore = math.sqrt(mean_squared_error(self.trainY[: ,0], trainPredict[:,0]))
            # print('Train Score: %.5f RMSE' % (trainScore))
            testScore = math.sqrt(mean_squared_error(testPredict[:,0],self.test_Y[:,0]))
            print('Test Score: %.5f RMSE' % (testScore))        
            mse_values.append(testScore)
            # print("hidden_states = " , hidden_states , "mse = ", testScore)

        except Exception as e:
            print("Error:", str(e))
        try:

            # plot_graphs(train,trainPredict,predict+look_back-1, 0)
            # plot_graphs(val,validPredict,predict+look_back-1, 0)
            plt.plot(self.trainY[: ,0])
            plt.plot(trainPredict[:,0])
            plt.show()
            plt.plot(self.test_Y[: ,0])
            plt.plot(testPredict[:,0])
            plt.show()

            # plot_graphs(test,testPredict,predict+look_back-1, 0)
            plt.plot(history.history['loss'])
            plt.plot(history.history['val_loss'])
            plt.title('model accuracy')
            plt.ylabel('accuracy')
            plt.xlabel('epoch')
            plt.legend(['train', 'validation'], loc='upper right')

            plt.grid()
            plt.show()
        except Exception as e:
            print("Error:", str(e))
        return self.model, mse_values, trainPredict, testPredict
   
    def load_model(self,path):
        self.model = tf.keras.models.load_model(path)

    
    def fit_new_data(self, new_data=None):
        new_data = new_data if new_data is not None else self.data
        
        self.create_dataset(new_data) 
        
        self.model.fit(self.dataX,self.dataY,epochs=self.epochs, 
                  validation_split=self.valid_ratio,
                  callbacks = self.callback)
        
    def predict_data(self, data=None):
        data = data if data is not None else self.data
        
        self.create_dataset(data)
        
        predictedData = self.model.predict(self.dataX)
        # self.forecast = np.concatenate((self.data, predictedData[ - self.predict:]), axis=0)
        
        self.forecast = self.scaler.inverse_transform(predictedData)

        
    def to_dataframe(self):
        extended_datetime_index = pd.date_range(start=self.class_dataset.time[-1] + pd.Timedelta(self.freqGrouper), 
                                                periods=self.predict, 
                                                freq=self.freqGrouper)

        # combined_datetime_index = self.time.append(extended_datetime_index)[-self.forecast.shape]
        
        self.predict_df = pd.DataFrame(self.forecast[-self.predict:,:], columns=self.edges, index=extended_datetime_index)
        self.predict_df.index.name = 'dateandtime'
        
    def fit_predict_new_data(self, new_data = None,  save_to_csv = False):
        new_data = new_data if new_data is not None else self.data
        new_data= new_data[NEW_DATA_HISTORICAL:,:]
        # print(csv_file_name)
        self.fit_new_data(new_data)
        self.predict_data(new_data)
        self.to_dataframe()
        df = self.predict_df
        try:
            df.to_csv(csv_file_name) if save_to_csv else ...
        except Exception  as e:
            print("Error:",e)
        return df





##################################################################################################################

############################################## INITIALIZATION ####################################################

##################################################################################################################



# my_dataset = DataSet(file_path = HISTORICAL_DATA_FILE_PATH,box_pts = SMOOTHING_FACTOR ,freqGrouper= FREQ_GROUPER)
# lstm_object = LSTM_Model(my_dataset)
# lstm_object.load_model(path = LSTM_FILE_PATH)