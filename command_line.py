# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 10:21:02 2016

@author: mjchao
"""

'''
Gets the price data for the given commodity.

@param commodityId - the ID of a commodity
@param return - the price data for the given commodity
'''
def get_data_by_id( commodityId ):
    from price_data_io import PriceReader
    return PriceReader.get_price_data_from_csv( commodityId )
    
'''
Plots the price of a commodity over time

@param commodityId - the ID of a commodity
'''
def plot_price_by_id( commodityId ):
    data = get_data_by_id( commodityId )
    data.plot_price_over_time()
   
'''
Plots the trade volume of a commodity over time

@param commodityId - the ID of a commodity
'''
def plot_volume_by_id( commodityId ):
    data = get_data_by_id( commodityId )
    data.plot_volume_over_time()
    
def get_id_from_name( commodityName ):
    from data_manager import DataManager
    DataManager.init()
    commodityName = commodityName.lower()
    return DataManager.nameToId[ commodityName ] if commodityName in DataManager.nameToId else None
    
'''
Gets the price data for the given commodity.

@param commodityName - the in-game name of a commodity
@param return - the price data for the given commodity
'''
def get_data_by_name( commodityName ):
    id = get_id_from_name( commodityName )
    if ( id is not None ):
        return get_data_by_id( id )
    else:
        print "Invalid commodity name."
        return None
    
'''
Plots the price of a commodity over time

@param commodityName - the name of a commodity
'''
def plot_price_by_name( commodityName ):
    id = get_id_from_name( commodityName )
    if ( id is not None ):
        plot_price_by_id( id )
    else:
        print "Invalid commodity name."
        
'''
Plots the trade volume of a commodity over time

@param commodityName - the name of a commodity
'''
def plot_volume_by_name( commodityName ):
    id = get_id_from_name( commodityName )
    if ( id is not None ):
        plot_volume_by_id( id )
    else:
        print "Invalid commodity name."
    
    
    