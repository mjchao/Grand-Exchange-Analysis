# -*- coding: utf-8 -*-
from price_crawler import PriceCrawler
from price_data_io import PriceWriter
from time import sleep

import matplotlib.pyplot as plt

#DataManager.init()
#mithrilBarData = DataManager.get_data_by_date_range( "Mithril bar" , 2 , 2015 , 8 , 2015 )
#mithrilOreData = DataManager.get_data_by_date_range( "Mithril ore" , 2 , 2015 , 8 , 2015 )
#coalData = DataManager.get_data_by_date_range( "Coal" , 2 , 2015 , 8 , 2015 )

#DO NOT USE IF YOU ARE UPDATING DATA - ONLY USE IF YOU ARE DOWNLOADING FROM SCRATCH
def download_data_by_id( id ):
    priceData = PriceCrawler.get_price_data_from_html( id )
    if ( priceData != None ):
        f = open( "price_data/item_ids" , "a" )
        f.write( priceData.get_name() + "," + str( id ) + "\n" )
        f.close()
        PriceWriter.write_price_data_to_csv( "price_data/master_list/" + str(id) + ".csv" , priceData )
    
f = open( "price_data/item_stats" , "r" )
startID = 2134
endID = 12520
for line in f:
    data = line.split( "," )
    itemID = int( data[ 0 ] )
    if ( startID <= itemID and itemID <= endID ):
        print "Processing " + str( itemID )
        download_data_by_id( itemID )
        print "Sleeping 2"
        sleep( 2 )
    
    
