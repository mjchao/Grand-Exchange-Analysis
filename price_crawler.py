# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 21:39:45 2015

@author: mjchao
"""
import requests
import datetime
import re

'''
Represents one data point of time series data. A DataPoint keeps track of
the following data:

* year - the year values of the time series data, stored as a string of length 4
* month - the month values of the time series data, stored as a string of length 2
* day - the day values of the time series data, stored as a string of length 2
* daily - the daily integer prices of the time series data
* average - the average integer prices of the time series data
* traded - the quantity traded on a givne day, stored as an integer
'''
class DataPoint( object ):
    
    @staticmethod
    def from_csv_data( year , month , data ):
        values = data.split( "," )
        day = str( values[ 0 ] )
        daily = int( values[ 1 ] )
        average = int( values[ 2 ] )
        traded = int( values[ 3 ] )
        return DataPoint( year , month , day , daily , average , traded )
    '''
    Creates a DataPoint object with the following data:
    
    * year - the year values of the time series data, stored as a string of length 4
    * month - the month values of the time series data, stored as a string of length 2
    * day - the day values of the time series data, stored as a string of length 2
    * daily - the daily integer prices of the time series data
    * average - the average integer prices of the time series data
    * traded - the quantity traded on a givne day, stored as an integer
    '''
    def __init__( self , year , month , day , daily=0 , average=0 , traded=0 ):
        self._year = year
        self._month = month
        self._day = day
        self._daily = daily
        self._average = average
        self._traded = traded

    '''
    Determines the textual representation of this data point as a comma
    separated value.
    
    @return - the representation of this data point in CSV format
    '''
    def __str__( self ):
        return self._year + "," + self._month + "," + self._day + "," + \
                str( self._daily ) + "," + str( self._average ) + "," + \
                str( self._traded )
                
    '''
    Determines the textual representation of this data point as a
    comma separated value without the year, month, and date. This
    makes it more memory-efficient to store in a filesystem that
    is already indexed by dates.
    
    @return - the representation of this data point in CSV format
    without the date
    '''
    def str_without_date( self ):
        return str( self._daily ) + "," + str( self._average ) + "," + \
                str( self._traded )
                
    def __eq__( self , other ):
        return self._year == other._year and \
            self._month == other._month and \
            self._day == other._day and \
            self._daily == other._daily and \
            self._average == other._average and \
            self._traded == other._traded
       
    '''
    @return - the year of this data point, as a string of length 4
    '''
    def get_year( self ):
        return self._year
        
    '''
    @return - the month of this data point, as a string of length 2
    '''
    def get_month( self ):
        return self._month
        
    '''
    @return - the day of this data point, as a string of length 2
    '''
    def get_day( self ):
        return self._day
    
    '''
    @return - the price on YYYY/MM/DD of the commodity this data point
    represents, as an integer.
    '''
    def get_price( self ):
        return self._daily
        
    '''
    @return - the average 180-day price on YYYY/MM/DD of the commodity this 
    data point represents, as an integer
    '''
    def get_average180_price( self ):
        return self._average
        
    '''
    @return - the quantity of the commodity that was traded on YYYY/MM/DD,
    as an integer
    '''
    def get_volume( self ):
        return self._traded 
        
    '''
    Sets the volume of this DataPoint. This should only be used if
    the volume is 0 because the data was parsed from json (the json
    data does not have volume data).
    
    @param volume - the quantity of the commodity that was traded on
    YYYY/MM/DD, as an integer
    '''
    def initialize_volume( self , volume ):
        self._traded = volume
    
'''
Stores daily and average price time series data for a commodity. 

This object maintains a list of DataPoint objects. What specific data is stored
is determined by the DataPoint class structure.
'''
class CommodityPriceData( object ):
    
    '''
    Creates a CommodityPriceData object with the given time series data.
    
    @param name - the name of the commodity, as a string
    @param datapoints - the time series data of the prices of this commodity
    as a list of DataPoint objects
    '''
    def __init__( self , name , datapoints ):
        self._name = name
        self._datapoints = datapoints
        
    '''
    @return - the name of this commodity, as a string
    '''
    def get_name( self ):
        return self._name
        
    '''
    @return - the DataPoint object stored at the given index. This should not
    be modified externally!
    '''
    def get_data_at( self , index ):
        return self._datapoints[ index ]
        
    '''
    @return - the number of DataPoint objects stored
    '''
    def get_num_datapoints( self ):
        return len( self._datapoints )
      
    '''
    @return - the list of all DataPoint objects stored. This should not
    be modified externally!
    '''
    def get_all_datapoints( self ):
        return self._datapoints
        
    def __str__( self ):
        rtn = "Price data for " + self._name
        for i in range( 0 , len( self._datapoints ) ):
            rtn += "\n[" + str( self._datapoints[ i ] ) + "]";
        return rtn
        
    def __eq__( self , other ):
        return self._name == other._name and \
            self._datapoints == other._datapoints
       
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

        return CommodityPriceData( name , datapoints )         

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

        return CommodityPriceData( name , datapoints )       
        
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
    
if __name__ == "__main__" : main()