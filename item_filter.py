# -*- coding: utf-8 -*-

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
    A list of item data on which to perform logistic regression
    '''
    itemData = []
    itemDataMap = {}
    
    logreg = linear_model.LogisticRegression()
    
    '''
    Reads in and preprocesses all the item data from the file 
    price_data/item_stats.
    '''
    @staticmethod
    def init():
        f = open( "price_data/item_stats" , "r" )
        for line in f.readlines():
            data = [ int(i) for i in line.split( "," ) ]
            itemID = data[ 0 ]
            priceRange = data[ 1 ] - data[ 2 ]
            maxVolume = data[ 3 ]
            
            #item is never traded, so we automatically filter it out
            if ( maxVolume == 0 ):
                continue

            newItem = ItemData( itemID , priceRange , maxVolume )
            Filter.itemData.append( newItem )
            Filter.itemDataMap[ itemID ] = newItem
            
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
            trainingSetX.append( Filter.itemDataMap[ itemID ].to_array() )
            trainingSetY.append( y )
        
        Filter.logreg.fit( trainingSetX , trainingSetY )
        print "Training set accuracy: " + str( Filter.logreg.score( trainingSetX , trainingSetY ) )
        
    '''
    Predicts if the given commodity with the given ID will be promising to
    trade on.
    '''
    @staticmethod
    def predict( itemId ):
        return Filter.logreg.predict( Filter.itemDataMap[ itemId ].to_array() )
        
def main():
    Filter.init()        
    Filter.train()
    print Filter.predict( 11928 )

if __name__ == "__main__" : main()