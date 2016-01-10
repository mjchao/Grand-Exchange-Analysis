# -*- coding: utf-8 -*-

from data_manager import DataManager
from price_data_io import PriceReader
import numpy as np


'''
Ranks items based on the liklihood of them
being profitable to trade with.
'''
class ProfitabilityRanker( object ):

    '''
    Calculates the expected profit to be gained from investing a given
    amount of funds on a current item.
    
    @param averageVolume - the average trade volume of the item
    @param totalFunds - the total amount of gold to be invested in this
                        commodity
    @param currentPrice - the current market price of the commodity. This
                          can be an estimate if the data is not completely
                          up to date
    @param averagePriceChange - the average price change of this commodity
                                for whatever investment duration is desired.
    @return - the expected profit from trading on this item, if
              one correctly buys low and sells high
    '''
    @staticmethod
    def __calculate_expected_profit__( averageVolume , totalFunds , currentPrice , averagePriceChange ):
        maxQty = min( averageVolume , int( totalFunds/currentPrice ) )
        return maxQty*averagePriceChange
       
    '''
    Calculates the expected item profitability if we invest in this
    item optimally during the given time frame.
    
    @param commodityId - the commodity in which to invest
    @param totalFunds - the amount of money to be invested
    @param duration - how long the money will be invested for at maximum,
                      as an integer number of days
    @return - an decimal quantity that is the expected amount of gold
              to be gained if investing optimally in the given commodity
              with the given amount of funds for the given duration
    '''
    @staticmethod
    def get_item_profitability( commodityId , totalFunds , duration ):
        data = PriceReader.get_price_data_from_csv( commodityId )
        datapoints = data.get_all_datapoints()
        
        #we exclude 0 volume datapoints because for some time, the
        #price database did not record volumes and they were reported
        #as 0. We don't want this to affect average volume
        volumes = np.array( [ x.get_volume() for x in datapoints if x.get_volume() != 0 ] )
        averageVolume = np.mean( volumes ) if volumes.size > 0 else 0
        
        prices = np.array( [ x.get_price() for x in datapoints ] )
        daysOfData = prices.size
        
        #record the maximum profits we could make by starting investment
        #on a given day and clearing it within the specified duration
        optimalPriceChanges = np.zeros( daysOfData-duration+1 )
        for i in range( 0 , daysOfData-duration+1 ):
            window = prices[ i:i+duration ]
            optimalPriceChanges[ i ] = np.max( window ) - np.min( window )
        averagePriceChange = np.mean( optimalPriceChanges )
        
        return ProfitabilityRanker.__calculate_expected_profit__( averageVolume , \
                                totalFunds , prices[-1] , averagePriceChange )
        

def main():
    print ProfitabilityRanker.get_item_profitability( 440 , 2000000 , 180 )

if __name__ == "__main__" : main()
