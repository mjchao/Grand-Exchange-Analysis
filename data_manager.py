# -*- coding: utf-8 -*-

from price_crawler import PriceCrawler
from price_data_io import PriceWriter, PriceReader , MonthData

class IDManager( object ):
    
    '''
    Writes the list of interesting IDs for which we should retain data.
    The criteria for interesting is:
            Price >= 10000 OR Traded Volume >= 50000
    This way, we filter out useless items like Steel Longsword which
    nobody wants to trade.
    '''
    @staticmethod
    def get_interesting_ids():
        pass
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
    DataManager.init()
    #DataManager.download_data_by_names( "mithril ore" , "mithril bar" , "coal" , "iron ore" , "steel bar" )
    test = DataManager.get_data( "Mithril bar" , 12 , 2014 , 12 , 2015 )
    print test

if __name__ == "__main__" : main() 
