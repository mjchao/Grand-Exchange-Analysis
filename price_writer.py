# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 2015

@author: mjchao
"""

import csv 
import os

'''
Stores daily price and average 180-day price data for a month and
provides methods to access that price data.
'''
class MonthData( object ):

    DAYS_IN_MONTH = {
        1 : 31 ,
        2 : 28 ,
        3 : 31 ,
        4 : 30 ,
        5 : 31 ,
        6 : 30 ,
        7 : 31 ,
        8 : 31 ,
        9 : 30 ,
        10 : 31 ,
        11 : 30 ,
        12 : 31
    }  
    
    '''
    Determines the number of days in a given month.
    
    @param month - the month as an integer
    @param year - the year as an integer. This will be used if the month is a 
    February which will have 28 or 29 days, depending on if it is a leap year.
    @return - the number of days in the given month as an integer
    '''
    @staticmethod 
    def get_num_days_in_month( month , year ):
        
        #all years divisible by 4 are leap years, except those divisible by 
        #100 but not 400.
        if ( month == 2 ):
            if ( year % 100 == 0 and year % 400 != 0 ):
                return 28
            else:
                return 29 if year % 4 == 0 else 28
        else :
            return MonthData.DAYS_IN_MONTH[ month ]

    '''
    Formats an integer month to be a string with length 2. This is just
    for consistency issues.
    
    @param month - a month as an integer
    @return - the given month as a string with length 2
    '''
    @staticmethod
    def format_month( month ):
        rtn = str( month )
        if ( len( rtn ) == 1 ):
            rtn = "0" + rtn
            
        return rtn
        
    '''
    Formats an integer day to be a string with length 2. This is just for
    consistency issues.
    
    @param day - a day as an integer
    @return - the given day as a string with length 2
    '''            
    @staticmethod
    def format_day( day ):
        rtn = str( day )
        if ( len( rtn ) == 1 ):
            rtn = "0" + rtn
            
        return rtn
    
    '''
    Creates a default MonthData object for the given month of the given year.
    All data is initialized with daily price = 0 and average price = 0.
    
    @param month - the integer month for which this object will store data.
    @param year - the integer year for which this object will store data.
    '''
    def __init__( self , month , year ):
        self.month = month
        self.year = year
        self.numDays = MonthData.get_num_days_in_month( month , year )
        self.data = []
        for i in range( 0 , self.numDays+1 ):
            self.data.append( (0 , 0) )
    
    '''
    Sets the (daily price , average price) data for the given day
    of the month. 
    
    You can set some data for day 0 without getting an error,
    but your data will not be saved or used by any core functions.
    
    @param day - a valid day of the month, as an integer. Note that if the
    month that this MonthData represents has n days, you should not use
    any days greater than n.
    @param dailyPrice - the daily price of a commodity on the given day,
    as an integer.
    @param averagePrice - the average 180-day price of a commodity on the
    given day, as an integer.
    '''
    def set( self , day , dailyPrice , averagePrice ):
        self.data[ day ] = ( dailyPrice , averagePrice )

    '''
    Gets the (daily price, average price) data tuple for the given day
    of the month. 
    
    You can get data for day 0 without getting an error,
    but it will just be (0, 0) unless you set it to something else earlier.
    The data for day 0 is never saved or used by other core functions.
    
    @param day - a valid day of the month, as an integer. If this month
    has n days, you should not use any days greater than n.
    '''        
    def get( self , day ):
        return self.data[ day ]
        
    '''
    Returns the comma-separated-value format for the price data of this
    month. The data for different days is separated onto different lines.
    It will be in a form like this:
            01,45,58
            02,34,69
            03,34,58
            ...
    where the daily price on day 1 was 45, and the average price on day 1
    was 58, and so on...
    
    @return - a list of comma-separated-values that is the price data
    of this month.
    '''
    def __str__( self ):
        
        #we hard code the first print so that we can avoid having a
        #trailing newline at the end
        rtn = MonthData.format_day( 1 ) + \
            "," + str( self.data[ 1 ][ 0 ] ) + \
            "," + str( self.data[ 1 ][ 1 ] )
            
        for i in range( 2 , self.numDays+1 ):
            rtn = rtn + "\n" + \
                MonthData.format_day( i ) + \
                "," + str( self.data[ i ][ 0 ] ) + \
                "," + str( self.data[ i ][ 1 ] )
        
        return rtn
        
class PriceReader( object ):
    
    '''
    Reads in price data for a given month and returns a MonthData object
    with all that data. If the data does not exist, then all the datapoints
    will have daily price 0 and average price 0.
    
    @param month - the month of the price data to read, as an integer
    @param year - the year of the price data to read, as an integer
    @param commodity - the name of the commodity for which to look up price data,
    as a string
    @return - a MonthData object with all the price information for the
    given commodity during the given month and year time period.
    '''
    @staticmethod
    def read_month_data( month , year , commodity ):
        rtn = MonthData( month , year )
        dir = "price_data/" + str( year ) + " " + MonthData.format_month( month )
        try :
            file = open( dir + "/" + commodity + ".csv" , "r" )
            fin = csv.reader( file , delimiter="," )
            for data in fin :
                rtn.set( int(data[ 0 ]) , data[ 1 ] , data[ 2 ] )
        except IOError:
            
            #there is no data, so ignore the error and return default
            #values of 0 for daily and average prices
            pass
        
        return rtn
        
'''
Provides functions for Writing daily and average price data to the 
appropriate files. 

The structure of the filesystem is as follows:
* All daily and average price data goes in the price_data folder
* Within the price_data folder are folders organized by the year and month,
such as "2015 08", "2015 09", and "2015 10" that separate time series data
into months.
* Within the folder for each month are the price data files for specific
commodities. For example, the price data for Mithril ore during the month
of September 2015 would be located in file "price_data/2015 09/Mithril ore.csv"
* Within the file for a specific commodity during a given month, the data
will be stored with the comma-separated-value format as follows:
            <day>,<daily price>,<average price>

Note that there is no need to store the year or the month, as it is already
specified in the file's path. As an example, if Mithril ore had a daily price
of 248 and average 180-day price of 308 on 2015/08/21, then in the file
"price_data/2015 08/Mithril ore.csv", we would find the entry 
"21,348,308" on line 21.
'''
class PriceWriter( object ):
    
    '''
    Saves the data in a CommodityPriceData object to the appropriate files.
    This function will take any previous price data for the commodity and
    merge the data in the CommodityPriceData object into the old data. In
    the case of overlaps, the old data is overwritten, but assuming the
    Grand Exchange API works correctly, whenever the new data overlaps with
    the old data, the prices should still be the same.
    
    @param priceData - a CommodityPriceData object with time series data
    that should be saved
    '''
    @staticmethod
    def save_data( priceData ):
        months = {}
        for i in range( 0 , len( priceData.year ) ):
            key = (priceData.month[ i ] , priceData.year[ i ] )
            
            #read in the data for the month if it exists
            if ( not months.has_key( key ) ):
                months[ key ] = PriceReader.read_month_data( \
                    int(priceData.month[ i ]) , int(priceData.year[ i ]) , priceData.name )
                    
            #the MonthData object must have been created and contains whatever
            #values were stored on the hard drive. We now merge
            #our price data into it, overwriting anything from before.
            months[ key ].set( int(priceData.day[ i ]) , priceData.daily[ i ] , \
                                                        priceData.average[ i ] )
        
        #after all data has been merged, we can rewrite the updated
        #data back to the hard drive
        for monthData in months.values() :
            PriceWriter.write_month_data_to_file( monthData , priceData.name )
    
    '''
    Writes the month data for a given commodity to the appropriate file.
    
    @param monthData - the month data to be saved
    @param commodity - the name of the commodity
    '''
    @staticmethod
    def write_month_data_to_file( monthData , commodity ):
        month = MonthData.format_month( monthData.month )
        year = str( monthData.year )
        datafile = "price_data/" + year + " " + month + "/" + commodity + ".csv" 
        
        #create the new month folder, if necessary
        if ( not os.path.exists( os.path.dirname( datafile ) ) ):
            os.makedirs( os.path.dirname( datafile ) )
            
        f = open( datafile , "w" )
        f.write( str( monthData ) )
    
def main():
    test = MonthData( 2 , 2012 )
    assert len( test.data ) == 30
    test = MonthData( 2 , 2013 )
    assert len( test.data ) == 29
    test = MonthData( 3 , 2014 )
    assert len( test.data ) == 32
    test = MonthData( 4 , 2014 )
    assert len( test.data ) == 31
    
    #test = MonthData( 8 , 2015 )
    #PriceWriter.write_month_data_to_file( test , "test" )
    #test = PriceReader.read_month_data( 8 , 2015 , "test" )
    #print test
    from price_crawler import PriceCrawler
    priceData = PriceCrawler.get_price_data_from_json( "Mithril ore" , 447 )
    PriceWriter.save_data( priceData )
    
    print "Regression testing for price_writer.py passed."
    pass

if __name__ == "__main__" : main()