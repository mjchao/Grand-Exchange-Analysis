# -*- coding: utf-8 -*-

from data_manager import DataManager
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model, datasets


'''
Stores data about and item. As of right now, the relevant data that we will
use for logistic regression will be the id, price range and the maximum volume.
The id, price range, and maximum volume should all be integer values.
'''
class ItemData( object ):
    
    '''
    Creates an ItemData object for the object with the given ID.
    
    @param id - the ID of an object, as an integer
    @param range - the price range of the object (max price - min price), as an
    integer
    @param maxVolume - the maximum trade volume of the object, as an integer
    '''
    def __init__( self , id , range , maxVolume ):
        self._id = id
        self._range = range
        self._maxVolume = maxVolume
    
    '''
    Returns the textual representation of this ItemData object as a 
    comma separated list of values in the form
    <id>,<range>,<maxVolume>
    '''
    def __str__( self ):
        return  str( self._id ) + "," + str( self._range ) + "," + \
                str( self._maxVolume )
                
    '''
    Returns an array representing the ItemData object to be used in
    training a logistic classifier.
    '''
    def to_array( self ):
        return [ self._range , self._maxVolume ]

'''
Separates the promising items from the unpromising items using logistic
regression.
'''
class Filter( object ):

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
        * Standard deviation of the daily price - index 0
        * Standard deviation of daily price changes - index 1
        * Number of trend reversals - index 2
        * Average volume - index 3
        
    
    @param priceData - some price data for a commodity
    @return - the feature vector on which we will perform logistic regression
    for the given object, as an array of floats
    '''
    @staticmethod
    def get_feature_vector( priceData ):
        datapoints = priceData.get_all_datapoints()
        dailyPrices = np.array( [ x.get_price() for x in datapoints ] )
        dailyVolumes = np.array( [ x.get_volume() for x in datapoints ] )
        
        #compute standard deviation of daily price
        stddevDaily = np.std( dailyPrices )
        
        #compute standard deviation of daily price changes
        dailyChange = np.diff( dailyPrices )
        stddevChange = np.std( dailyChange )
        
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
        numTrendChanges = np.sum( np.diff( np.abs( trendChanges ) ) )
        
        #compute average daily volume.
        #if the volume was 0 on a day, we ignore that day
        nonzeroVolumes = dailyVolumes > 0
        dailyVolumes = dailyVolumes[ nonzeroVolumes ]
        totalTraded = np.sum( dailyVolumes )
        numDays = dailyVolumes.size
        
        #if the item was never traded, we define it to have
        #average volume of 0
        if ( numDays == 0 ):
            averageVolume = 0
        else:
            averageVolume = float( totalTraded ) / float( numDays )
            
        return [ stddevDaily , stddevChange , numTrendChanges , averageVolume ]
    
    '''
    Reads in and preprocesses all the item data from the file 
    price_data/item_stats.
    '''
    @staticmethod
    def init():
        DataManager.init()
        for id in DataManager.idToName.keys():
            priceData = DataManager.get_data_by_id( id )
            features = Filter.get_feature_vector( priceData )
            Filter.itemData.append( features )
            Filter.itemDataMap[ id ] = features       
            
    '''
    Trains the logisitic classifier on the training data in
    the file price_data/item_stats_train.
    '''
    @staticmethod
    def train():
        trainingSetX = []
        trainingSetY = []
        f = open( "price_data/item_stats_train" , "r" )
        for line in f.readlines():
            data = [int(i) for i in line.split( "," ) ]
            itemID = data[ 0 ]
            y = data[ 1 ]
            trainingSetX.append( Filter.itemDataMap[ itemID ] )
            trainingSetY.append( y )
        
        Filter.logreg.fit( trainingSetX , trainingSetY )
        print "Training set accuracy: " + str( Filter.logreg.score( trainingSetX , trainingSetY ) )
        
    '''
    Predicts if the given commodity with the given ID will be promising to
    trade on.
    '''
    @staticmethod
    def predict( itemId ):
        return Filter.logreg.predict( Filter.itemDataMap[ itemId ] )
        
def main():
    Filter.init()        
    Filter.train()
    print Filter.predict( 11928 )

if __name__ == "__main__" : main()