# -*- coding: utf-8 -*-

from price_crawler import PriceCrawler
from price_data_io import PriceWriter

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
            DataManager.nameToId[ objName ] = objID
            
    '''
    Downloads the most recent data for the commodity with the given name
    and id. You must be sure that the data has been downloaded before you
    can use it for analysis.
    
    @param name - the name of the commodity, as a string
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
    You must be sure that the data has been downloaded before you can use
    it for analysis.
    
    @param objectName - the name of the commodity, as a string
    '''    
    @staticmethod
    def downloadDataByName( objectName ):
        name = objectName
        id = DataManager.nameToId[ name ]
        DataManager.downloadDataByNameAndId( name , id )
    
    '''
    Downloads the most recent data for the commodity with the given ID.
    You must be sure that the data has been downloaded before you can use
    it for analysis.
    
    @param objectId - the ID of the commodity, as an integer
    '''
    @staticmethod
    def downloadDataById( objectId ):
        id = objectId
        name = DataManager.idToName[ id ]
        DataManager.downloadDataByNameAndId( name , id )
    
    
def main():
    DataManager.init()
    DataManager.downloadDataById( 447 )

if __name__ == "__main__" : main()
