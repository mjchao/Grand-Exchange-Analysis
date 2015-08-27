# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 21:39:45 2015

@author: mjchao
"""
import requests
import datetime
import re
from time import sleep
from price_data import DataPoint , CommodityPriceData
       
'''
Provides functions for obtaining Grand Exchange data.
'''
class PriceCrawler( object ):
    
    '''
    Gets price data for a given commodity from json provided by the
    Grand Exchange API. The trade volume is not reported, however, as the
    json values do not have that. If you need trade volume, get the
    data from the HTML instead.
    
    @param name - the name of the commodity, as a string.
    @param objectId - the Grand Exchange object ID for the commodity, as an integer.
    @return - a CommodityPriceData object that stores all the time 
    series data for the daily and average prices of the commodity.
    None is returned if the object ID was invalid.
    '''
    @staticmethod
    def get_price_data_from_json( name , objectId ):
        page = requests.get( "http://services.runescape.com/m=itemdb_oldschool/api/graph/" + str(objectId) + ".json" )        
        json = page.text
        
        #bad object ID
        if ( "404 - Page not found" in json ):
            return None
         
        #split the data given to us into the two halves: the first half
        #is our daily price data. the second half is our average price data
        dailyPriceJson = json[0:json.find( "average" )]
        averagePriceJson = json[json.find( "average"):len(json)]
        
        datapoints = []
        
        #data comes in the form {timestamp:value, timestamp:value, ...}
        #where all timestamps and prices are integer values,
        #so we can just parse out all the integer values and process them
        #in pairs of 2.
        
        #note that the average price data and daily price data must have
        #the same length, so we can iterate through both lists simultaneously
        priceData = re.findall( r'\d+' , dailyPriceJson )   
        averageData = re.findall( r'\d+' , averagePriceJson )
        for i in range( 0 , len( priceData ) , 2 ):
            
            timestamp = priceData[ i ]
            
            #have to add an extra 12 hours because Jagex is several hours ahead.
            #we just add 12 hours to be safe. We are only interested in dates
            #and the actual hour of day does not matter to us.
            dateValues = re.findall( r'\d+' , str(datetime.datetime.fromtimestamp( int(timestamp)/1000 + 43200 )) )
            year = str( dateValues[ 0 ] )
            month = str( dateValues[ 1 ] )
            day = str( dateValues[ 2 ] )
            price = int( priceData[ i+1 ] )
            average = int( averageData[ i+1 ] )
            datapoints.append( DataPoint( year , month , day , price , average ) )

        return CommodityPriceData( objectId , name , datapoints )         

    '''
    Gets price data for a given commodity from the HTML of the Grand Exchange
    website. The name of the commodity is also automatically determined from
    the HTML.
    
    @param objectId - the Grand Exchange object ID of a commodity, as an integer.
    @return - a CommodityPriceData object that stores time series data
    for the daily and average price of a commodity.
    None is returned if the given object ID was invalid.
    '''
    @staticmethod
    def get_price_data_from_html( objectId ):
        page = requests.get( "http://services.runescape.com/m=itemdb_oldschool/viewitem?obj=" + str( objectId ) )
        html = page.text
        
        #invalid object ID
        if ( "Sorry, there was a problem with your request." in html ):
            if ( "You've made too many requests recently." in html and \
                    "As a result, your IP address has been temporarily blocked. Please try again later." in html ):
                print "Computer IP has been blocked. Trying again in 15 seconds..."
                sleep( 15 )
                return PriceCrawler.get_price_data_from_html( objectId )
            return None
        
        #we can find the name in the title of the webpage.
        name = str( re.search( r'(?<=<title>)(.*)(?= - Grand Exchange)' , html ).group( 0 ) )
        
        #and the price data is always pushed to the graphs on the webpage
        #with the command "average180.push( ... )" so we are just interested
        #in lines with that command
        priceData = re.findall( r'average180.push.*' , html )
        volumeData = re.findall( r'trade180.push.*' , html )
        
        datapoints = []
        
        for price , volume in zip( priceData , volumeData ):
            priceNumbers = re.findall( r'\d+' , price )
            
            #we'll keep years, months, and days in string form because
            #we want there to always be 4 digits in a year, 2 digits in 
            #a month and 2 digits in a day. If we converted them to integers,
            #we would lose a digit sometimes - e.g. 01 would be converted to 1
            #and we'd lose consistency.
            year = str( priceNumbers[ 1 ] )
            month = str( priceNumbers[ 2 ] )
            day = str( priceNumbers[ 3 ] )
            
            #prices, on the other hand, can be converted to integers because
            #all commodities will always cost an integer number of coins.
            price = int( priceNumbers[ 4 ] )
            average = int( priceNumbers[ 5 ] )
            
            volumeNumbers = re.findall( r'\d+' , volume )
            
            #volume can also be converted to integers
            #because all commodities will have an integer volume each day
            volume = int( volumeNumbers[ 4 ] )
            
            datapoints.append( DataPoint( year , month , day , price , average , volume ) )

        return CommodityPriceData( objectId , name , datapoints )    
        
        
def main():
    test = PriceCrawler.get_price_data_from_json( "Mithril ore" , 447 ) 
    test2 = PriceCrawler.get_price_data_from_html( 447 )
    
    #type checks
    assert isinstance( test.get_data_at( 0 )._year , str )
    assert isinstance( test.get_data_at( 0 )._month , str )
    assert isinstance( test.get_data_at( 0 )._day , str )
    assert isinstance( test.get_data_at( 0 )._daily , int )
    assert isinstance( test.get_data_at( 0 )._average , int )
    assert isinstance( test2.get_data_at( 0 )._year , str )
    assert isinstance( test2.get_data_at( 0 )._month , str )
    assert isinstance( test2.get_data_at( 0 )._day , str )
    assert isinstance( test2.get_data_at( 0 )._daily , int )
    assert isinstance( test2.get_data_at( 0 )._average , int )
    
    print test2
    
    print "Regression testing for price_crawler.py passed"
    
    test3 = PriceCrawler.get_price_data_from_html( 1 )
    assert test3 == None
    
if __name__ == "__main__" : main()