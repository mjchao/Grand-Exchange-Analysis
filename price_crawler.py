# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 21:39:45 2015

@author: mjchao
"""
import requests
import datetime
import re

'''
Stores daily and average price time series data for a commodity. The following
is a list of all data of which this object keeps track:

* name - the name of the commodity, e.g. Mithril ore
* year - the year values of the time series data, stored as a string of length 4
* month - the month values of the time series data, stored as a string of length 2
* day - the day values of the time series data, stored as a string of length 2
* daily - the daily integer prices of the time series data
* average - the average integer prices of the time series data

Given an index i within range, we can say that on the date
year[i]/month[i]/day[i], the daily price of <name> was daily[i] and the
average 180-day price of <name> was average[i].
'''
class CommodityPriceData( object ):
    
    def __init__( self , name , year , month , day , daily , average ):
        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.daily = daily
        self.average = average
        
    def __str__( self ):
        rtn = "Price data for " + self.name
        for i in range( 0 , len( self.year ) ):
            rtn += "\n[" + self.year[ i ] + "/" + self.month[ i ] + \
                "/" + self.day[ i ] + ", " + str( self.daily[ i ] ) + \
                ", " + str( self.average[ i ] ) + "]";
        return rtn
        
    def __eq__( self , other ):
        return self.name == other.name and \
            self.year == other.year and \
            self.month == other.month and \
            self.day == other.day and \
            self.daily == other.daily and \
            self.average == other.average
       
'''
Provides functions for obtaining Grand Exchange data.
'''
class PriceCrawler( object ):
    
    '''
    Gets price data for a given commodity from json provided by the
    Grand Exchange API.
    
    @param name - the name of the commodity.
    @param objectId - the Grand Exchange object ID for the commodity.
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
        
        years = []
        months = []
        days = []
        prices = []
        averages = []
        
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
            years.append( str( dateValues[ 0 ] ) )
            months.append( str( dateValues[ 1 ] ) )
            days.append( str( dateValues[ 2 ] ) )
            prices.append( int(priceData[ i+1 ]) )
            averages.append( int(averageData[ i+1 ]) )

        return CommodityPriceData( name , years , months , days , prices , averages )         

    '''
    Gets price data for a given commodity from the HTML of the Grand Exchange
    website. The name of the commodity is also automatically determined from
    the HTML.
    
    @param objectId - the Grand Exchange object ID of a commodity.
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
            return None
        
        #we can find the name in the title of the webpage.
        name = str( re.search( r'(?<=<title>)(.*)(?= - Grand Exchange)' , html ).group( 0 ) )
        
        #and the price data is always pushed to the graphs on the webpage
        #with the command "average180.push( ... )" so we are just interested
        #in lines with that command
        data = re.findall( r'average180.push.*' , html )
        
        years = []
        months = []
        days = []
        prices = []
        averages = []
        
        for datapoint in data:
            numbers = re.findall( r'\d+' , datapoint )
            
            #we'll keep years, months, and days in string form because
            #we want there to always be 4 digits in a year, 2 digits in 
            #a month and 2 digits in a day. If we converted them to integers,
            #we would lose a digit sometimes - e.g. 01 would be converted to 1
            #and we'd lose consistency.
            years.append( str( numbers[ 1 ] ) )
            months.append( str( numbers[ 2 ] ) )
            days.append( str( numbers[ 3 ] ) )
            
            #prices, on the other hand, can be converted to integers because
            #all commodities will always cost an integer number of coins.
            prices.append( int(numbers[ 4 ]) )
            averages.append( int(numbers[ 5 ]) )

        return CommodityPriceData( name , years , months , days , prices , averages )       
        
def main():
    test = PriceCrawler.get_price_data_from_json( "Mithril ore" , 447 ) 
    test2 = PriceCrawler.get_price_data_from_html( 447 )
    assert test == test2
    
    #type checks
    assert isinstance( test.year[ 0 ] , str )
    assert isinstance( test.month[ 0 ] , str )
    assert isinstance( test.day[ 0 ] , str )
    assert isinstance( test.daily[ 0 ] , int )
    assert isinstance( test.average[ 0 ] , int )
    assert isinstance( test2.year[ 0 ] , str )
    assert isinstance( test2.month[ 0 ] , str )
    assert isinstance( test2.day[ 0 ] , str )
    assert isinstance( test2.daily[ 0 ] , int )
    assert isinstance( test2.average[ 0 ] , int )
    
    print "Regression testing for price_crawler.py passed"
    
if __name__ == "__main__" : main()