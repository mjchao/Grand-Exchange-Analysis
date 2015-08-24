# -*- coding: utf-8 -*-

from price_crawler import PriceCrawler
from price_data_io import PriceWriter, PriceReader , MonthData
from random import randint
from time import sleep

class IDManager( object ):
    
    '''
    Records the maximum price, minimum price, and volume for all 
    commodities. This data will later be used to determine what
    the promising commodities to trade. For example, we'd like to
    trade on Mithril Ore because the volume is high and the price
    fluctuates quite a bit, but we don't want to trade on
    Steel Longsword because nobody trades it and the price doesn't
    move that much.
    
    Note: This function appends to the price_data/item_stats file.
    Make sure you look through the file first before giving it
    a start and end ID.
    
    @param startId - the first ID for which to record commodity stats
    @param endId - one greater than the last ID for which to record
    commodity stats (the range includes the start, but does not include
    the end ID)
    '''
    @staticmethod
    def record_commodity_stats( startId , endId ):
        for i in range( startId , endId ):
            print "Processing " + str( i )
            testData = PriceCrawler.get_price_data_from_html( i )
            if ( not testData is None ):
                maxPrice = 0
                minPrice = 999999999
                maxVolume = 0
                minVolume = 999999999
                allPoints = testData.get_all_datapoints()
                
                #we do not include the last data point because
                #that is today's data, which may be incomplete
                #and so the volume may be much less than what it
                #really is.
                for datapoint in allPoints[1:len(allPoints)-1]:

                    #prices and volumes of 0 are invalid                    
                    if ( datapoint.get_price != 0 ):
                        maxPrice = max( datapoint.get_price() , maxPrice )
                        minPrice = min( datapoint.get_price() , minPrice )
                    
                    if ( datapoint.get_volume() != 0 ):
                        maxVolume = max( datapoint.get_volume() , maxVolume )
                        minVolume = min( datapoint.get_volume() , minVolume )
                    
                out = open( "price_data/item_stats" , "a" )
                out.write( str(i) + "," + str(maxPrice) + "," + str(minPrice) + \
                    "," + str(maxVolume) + "," + str(minVolume) + "\n" )
                out.close()
            else:
                print str( i ) + " was not a valid id"
                
            #let's not get blocked for too many requests
            sleepInterval = randint( 1 , 30 )
            print "Sleeping " + str( sleepInterval )
            sleep( sleepInterval )
            
'''
Provides functions for managing data. 

There are two steps to this project: downloading and analyzing. 
Downloading requires lots of file IO and can be inefficient, 
so you want to minimize redundant downloads. That said, you must
download all your data before you can analyze it.
'''
class DataManager( object ):

    '''
    Maps integer object IDs to their commodity string names
    '''    
    idToName = {}
    
    '''
    Maps string names of commodities to their integer object IDs
    '''
    nameToId = {}
    
    '''
    Initializes the DataManager. You cannot perform any data operations
    using the DataManager if init() has not yet been called.
    '''
    @staticmethod
    def init():
        f = open( "price_data/item_ids" )
        lines = f.readlines()
        for line in lines :
            pairing = line.split( ";" )
            objName = pairing[ 0 ]
            objID = int( pairing[ 1 ] )
            DataManager.idToName[ objID ] = objName
            DataManager.nameToId[ objName.lower() ] = objID
            
    '''
    Downloads the most recent data for the commodity with the given name
    and id. The name IS CASE SENSITIVE and should appear with the same
    capitalization as in the file price_data/item_ids. If you do not
    know the correct capitalization, do not use this function!
    
    @param name - the name of the commodity, as a string. It is CASE SENSITIVE!
    @param id - the object id of the commodity, as an integer
    '''
    @staticmethod
    def download_data_by_name_and_id( name , id ):
        data = PriceCrawler.get_price_data_from_json( name , id )
        if ( data != None ) :
            PriceWriter.save_data( data )
        else :
            raise "Invalid commodity name or id."
    
    '''
    Downloads the most recent data for the commodity with the given name.

    @param objectName - the name of the commodity, as a string. The name is
    case insensitive
    '''    
    @staticmethod
    def download_data_by_name( objectName ):
        name = objectName.lower()
        id = DataManager.nameToId[ name ]
        caseSensitiveName = DataManager.idToName[ id ]
        DataManager.download_data_by_name_and_id( caseSensitiveName , id )
        
    '''
    Downloads the most recent data for all given commodities.
    
    @param names - a list of names (as strings) of commodities for which to 
    download price data. The names are case insensitive.
    '''
    @staticmethod
    def download_data_by_names( *names ):
        for name in names:
            DataManager.download_data_by_name( name )
    
    '''
    Downloads the most recent data for the commodity with the given ID.
    
    @param objectId - the ID of the commodity, as an integer
    '''
    @staticmethod
    def download_data_by_id( objectId ):
        id = objectId
        name = DataManager.idToName[ id ]
        DataManager.download_data_by_name_and_id( name , id )
        
    '''
    Gets all price data for a given commodity starting at the given start
    date and ending at the given end date. These dates are inclusive.
    
    @param name - the name of a commodity. This is a case insensitive string.
    @param startMonth - the month of the start date, as an integer.
    @param startYear - the year of the start date, as an integer.
    @param endMonth - the month of the end date, as an integer.
    @param endYear - the year of the end date, as an integer.
    '''
    @staticmethod
    def get_data( name , startMonth , startYear , endMonth , endYear ):
        caseSensitiveName = DataManager.idToName[ DataManager.nameToId[ name.lower() ] ]
        
        rtn = []
        
        #iterate through month by month, year by year from the start to the
        #end and add any nonzero datapoints to the list of data
        currYear = startYear
        currMonth = startMonth
        while( currYear <= endYear ):
            
            #if the current year is before the end year, then we just
            #iterate through all months
            if ( currYear < endYear ):
                while( currMonth <= 12 ):
                    monthData = PriceReader.read_month_data( currMonth , currYear , caseSensitiveName )
                    for day in range( 1 , len( monthData.data ) ):
                        prices = monthData.get( day )
                        
                        #we only add nonzero prices becauase prices of 0
                        #means that there was no price data for that given date
                        if ( prices[ 0 ] != 0 and prices[ 1 ] != 0 ):
                            rtn.append( (currYear , currMonth , day , prices[ 0 ] , prices[ 1 ] ) )
                    currMonth = currMonth + 1
                    
                #have to reset the month back to 1 after we've gone through
                #all 12 months in the current year
                currMonth = 1
                
            #if the current year is the end year, then we can only iterate
            #up to the end month
            elif ( currYear == endYear ):
                while( currMonth <= endMonth ):
                    monthData = PriceReader.read_month_data( currMonth , currYear , name )
                    for day in range( 1 , len( monthData.data ) ):
                        prices = monthData.get( day )
                        if ( prices[ 0 ] != 0 and prices[ 1 ] != 0 ):
                            rtn.append( (currYear , currMonth , day , prices[ 0 ] , prices[ 1 ] ) )
                    currMonth = currMonth + 1
                
            #move on to the next year
            currYear = currYear + 1
        
        return rtn
    
def main():
    #DataManager.init()
    #DataManager.download_data_by_names( "mithril ore" , "mithril bar" , "coal" , "iron ore" , "steel bar" )
    #test = DataManager.get_data( "Mithril bar" , 12 , 2014 , 12 , 2015 )
    #print test
    IDManager.record_commodity_stats( 101 , 201 )
    #test = PriceCrawler.get_price_data_from_html( 12621 )
    #print IDManager.is_interesting( test )

if __name__ == "__main__" : main() 
