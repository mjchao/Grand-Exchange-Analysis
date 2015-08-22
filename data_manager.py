# -*- coding: utf-8 -*-

from price_crawler import PriceCrawler
from price_data_io import PriceWriter, PriceReader , MonthData

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
    def downloadDataByNameAndId( name , id ):
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
    def downloadDataByName( objectName ):
        name = objectName.lower()
        id = DataManager.nameToId[ name ]
        caseSensitiveName = DataManager.idToName[ id ]
        DataManager.downloadDataByNameAndId( caseSensitiveName , id )
        
    '''
    Downloads the most recent data for all given commodities.
    
    @param names - a list of names (as strings) of commodities for which to 
    download price data. The names are case insensitive.
    '''
    @staticmethod
    def downloadDataByNames( *names ):
        for name in names:
            DataManager.downloadDataByName( name )
    
    '''
    Downloads the most recent data for the commodity with the given ID.
    
    @param objectId - the ID of the commodity, as an integer
    '''
    @staticmethod
    def downloadDataById( objectId ):
        id = objectId
        name = DataManager.idToName[ id ]
        DataManager.downloadDataByNameAndId( name , id )
        
    @staticmethod
    def getData( name , startMonth , startYear , endMonth , endYear ):
        caseSensitiveName = DataManager.idToName[ DataManager.nameToId[ name.lower() ] ]
        
        rtn = []
        currYear = startYear
        currMonth = startMonth
        while( currYear <= endYear ):
            if ( currYear < endYear ):
                while( currMonth <= 12 ):
                    monthData = PriceReader.read_month_data( currMonth , currYear , caseSensitiveName )
                    for day in range( 1 , len( monthData.data ) ):
                        prices = monthData.get( day )
                        if ( prices[ 0 ] != 0 and prices[ 1 ] != 0 ):
                            rtn.append( (currYear , currMonth , day , prices[ 0 ] , prices[ 1 ] ) )
                    currMonth = currMonth + 1
            elif ( currYear == endYear ):
                while( currMonth <= endMonth ):
                    monthData = PriceReader.read_month_data( currMonth , currYear , name )
                    for day in range( 1 , len( monthData.data ) ):
                        prices = monthData.get( day )
                        if ( prices[ 0 ] != 0 and prices[ 1 ] != 0 ):
                            rtn.append( (currYear , currMonth , day , prices[ 0 ] , prices[ 1 ] ) )
                    currMonth = currMonth + 1
                
            currYear = currYear + 1
        
        return rtn
    
def main():
    DataManager.init()
    #DataManager.downloadDataByNames( "mithril ore" , "mithril bar" , "coal" , "iron ore" , "steel bar" )
    test = DataManager.getData( "Mithril ore" , 8 , 2015 , 8 , 2015 )
    print test

if __name__ == "__main__" : main() 
