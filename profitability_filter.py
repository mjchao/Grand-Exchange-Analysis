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
    
    @param data - the price data for a given commodity
    @param totalFunds - the amount of money to be invested
    @param duration - how long the money will be invested for at maximum,
                      as an integer number of days
    @return - an decimal quantity that is the expected amount of gold
              to be gained if investing optimally in the given commodity
              with the given amount of funds for the given duration
    '''
    @staticmethod
    def get_item_profitability( data , totalFunds , duration ):
        datapoints = data.get_all_datapoints()

        #use the average price data over the last 180 days to
        #see if a given commodity changes trend enough to be
        #profitable to trade on
        averagePrices = []
        for i in range(len(datapoints)-180 , len(datapoints)):    
            averagePrices.append( datapoints[ i ].get_average180_price() )
        averagePrices = np.array( averagePrices )
        
        #calculate number of trend reversals in the average price trends
        differences = np.diff( averagePrices )
        differences =  differences[ differences != 0 ]
        isPositive = (differences > 0).astype( int )
        isNegatve = (differences < 0).astype( int )
        trends = (isPositive - isNegatve)
        isTrendChange = (np.abs( np.diff( trends )) == 2)
        trendChanges = np.sum( isTrendChange )

        #if the trend rarely changes, the item probably has 
        #a consistently falling price and we're not going
        #to make any profit off that
        if ( trendChanges <= 5 ):
            return 0
        
        
        #we exclude 0 volume datapoints because for some time, the
        #price database did not record volumes and they were reported
        #as 0. We don't want this to affect average volume
        volumes = np.array( [ x.get_volume() for x in datapoints if x.get_volume() != 0 ] )
        averageVolume = np.mean( volumes )/2 if volumes.size > 0 else 0
        
        prices = np.array( [ x.get_price() for x in datapoints ] )
        
        #record the maximum profits we could make by starting investment
        #on a given day and clearing it within the specified duration
        profitSum = 0
        daysOfProfit = 0
        for i in range( 0 , prices.size ):
            window = prices[ i:i+duration ]
            buyPrice = window[ 0 ]
            sellPrice = window[ 0 ]
            for j in range( 0 , len(window) ):
                if ( sellPrice < window[ j ] ):
                    sellPrice = window[ j ]
            bestProfit = sellPrice - buyPrice
            if ( bestProfit > 0 ):
                profitSum += bestProfit
                daysOfProfit += 1
                
        averagePriceChange = profitSum / daysOfProfit if profitSum != 0 else 0
        
        return ProfitabilityRanker.__calculate_expected_profit__( averageVolume , \
                                totalFunds , prices[-1] , averagePriceChange )
        
    '''
    Gets the profitability rankings of all known commodities, sorted in
    descending order by profitability
    
    @param totalFunds - the total amount of gold with which to invest
    @param duration - the maximum duration of the investment
    @return - the profitability rankings
    '''
    @staticmethod
    def get_profitability_rankings( totalFunds , duration ):
        f = open( "price_data/item_ids" , 'r' )
        rankings = []
        for line in f.readlines():
            commodityId = int(line.split( "," )[ 1 ])
            data = PriceReader.get_price_data_from_csv( commodityId )
            rankings.append( (data , ProfitabilityRanker.get_item_profitability( data , totalFunds , duration ) ) )
            
        rankings.sort( key=lambda x: -1*x[1] )
        return rankings
        

def main():
    
    
    #data = PriceReader.get_price_data_from_csv( 1038 )
    #print ProfitabilityRanker.get_item_profitability( data , 2000000 , 30 )
    
    
    rankings = ProfitabilityRanker.get_profitability_rankings( 2000000 , 30 )
    f = open( "trade_data/item_rankings.csv" , "w" )
    for ranking in rankings:
        f.write( str(ranking[ 0 ].get_name()) + "," + str(ranking[ 0 ].get_id()) + "," + str(ranking[ 1 ]) + "\n" )
    #''' 
  
'''      
Team-4 cape : 23383320.7886
Mist rune : 17322152.9333
Tiara : 17316149.626
Lantern lens : 16341747.8883
Basket : 11500876.9794
Uncut opal : 10807575.7263
Unblessed symbol : 10703217.1971
'''

if __name__ == "__main__" : main()
