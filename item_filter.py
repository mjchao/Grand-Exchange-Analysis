# -*- coding: utf-8 -*-

from data_manager import DataManager
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model

'''
Separates the volatile items from the non-volatile items using logistic
regression.
'''
class VolatilityFilter( object ):

    '''
    All price data for all known commodities.
    '''
    priceData = []
    
    '''
    A list of item data on which to perform logistic regression
    '''
    itemData = []
    
    itemDataMap = {}
    
    logreg = linear_model.LogisticRegression()
    
    '''
    Creates a feature vector given the price data for a given commodity.
    Here are the features we think will be useful
        * Standard deviation of the daily price to average daily price ratio
        * Standard deviation of daily price changes to average daily price ratio
        * Number of trend reversals
        
    
    @param priceData - some price data for a commodity
    @return - the feature vector on which we will perform logistic regression
    for the given object, as an array of floats
    '''
    @staticmethod
    def get_feature_vector( priceData ):
        datapoints = priceData.get_all_datapoints()
        dailyPrices = np.array( [ x.get_price() for x in datapoints ] )

        #compute average daily price        
        averageDaily = np.average( dailyPrices )
        
        #compute standard deviation of daily price
        stddevDaily = np.std( dailyPrices ) / averageDaily
        
        #compute standard deviation of daily price changes
        dailyChange = np.diff( dailyPrices )
        stddevChange = np.std( dailyChange ) / averageDaily
        
        #compute number of trend reversals:
        #we give all positive trend changes value 1
        #and all negative trend changes value 0.
        #Now, if the trend changes from positive to negative
        #or negative to positive, then the difference will be non-zero.
        #We'll take the sum of the absolute value of all these differences
        #to get us the number of trend changes
        positiveTrendChanges = dailyChange > 0
        negativeTrendChanges = dailyChange < 0
        trendChanges = dailyChange
        trendChanges[ positiveTrendChanges ] = 1
        trendChanges[ negativeTrendChanges ] = 0
        numTrendChanges = np.sum( np.abs( np.diff( trendChanges ) ) )
        
        #compute standard deviation of the trend change size to price ratio
        
            
        return [ stddevDaily , stddevChange , numTrendChanges ]
    
    '''
    Reads in and preprocesses all the item data from the file 
    price_data/item_stats.
    '''
    @staticmethod
    def init():
        DataManager.init()
        for id in DataManager.idToName.keys():
            priceData = DataManager.get_data_by_id( id )
            VolatilityFilter.priceData.append( priceData )
            features = VolatilityFilter.get_feature_vector( priceData )
            VolatilityFilter.itemData.append( features )
            VolatilityFilter.itemDataMap[ id ] = features       
            
    '''
    Trains the logisitic classifier on the training data in
    the file price_data/volatility_train.
    '''
    @staticmethod
    def train():
        trainingSetX = []
        trainingSetY = []
        f = open( "price_data/volatility_train" , "r" )
        for line in f.readlines():
            data = [int(i) for i in line.split( "," ) ]
            itemID = data[ 0 ]
            y = data[ 1 ]
            trainingSetX.append( VolatilityFilter.itemDataMap[ itemID ] )
            trainingSetY.append( y )
        
        #trainingSetX = np.array( trainingSetX )
        #scaledX = preprocessing.scale( trainingSetX )
        VolatilityFilter.logreg.fit( trainingSetX , trainingSetY )
        print "Training set accuracy: " + str( VolatilityFilter.logreg.score( trainingSetX , trainingSetY ) )
        
    '''
    Predicts if the given commodity with the given ID will be promising to
    trade on.
    '''
    @staticmethod
    def predict( itemId ):
        return VolatilityFilter.logreg.predict( VolatilityFilter.itemDataMap[ itemId ] )
        
def main():
    VolatilityFilter.init()        
    VolatilityFilter.train()

if __name__ == "__main__" : main()