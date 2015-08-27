# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 2015

@author: mjchao
"""

from price_crawler import PriceCrawler
from price_data import DataPoint , CommodityPriceData
import os
from date_utils import DateUtils

'''
Stores time series datapoints for a month and
provides methods to access that data.
'''
class MonthData( object ):        
    
    '''
    Creates a default MonthData object for the given month of the given year.
    All data is initialized with daily price = 0, average price = 0,
    and volume = 0
    
    @param month - the integer month for which this object will store data.
    @param year - the integer year for which this object will store data.
    '''
    def __init__( self , month , year ):
        self.month = month
        self.year = year
        self.numDays = DateUtils.get_num_days_in_month( month , year )
        self.data = []
        for i in range( 0 , self.numDays+1 ):
            self.data.append( DataPoint( year , month , i , 0 , 0 ) )
    
    '''
    Sets the time series DataPoint object for the given day
    of the month. 
    
    You can set some data for day 0 without getting an error,
    but your data will not be saved or used by any core functions.
    
    @param day - a valid day of the month, as an integer. Note that if the
    month that this MonthData represents has n days, you should not use
    any days greater than n.
    @param datapoint - the time series data for the given day of the month.
    This should be provided as a DataPoint object.
    '''
    def set( self , day , datapoint ):
        self.data[ day ] = datapoint

    '''
    Gets the time series DataPoint object for the given day
    of the month. 
    
    You can get data for day 0 without getting an error,
    but it will just be (0, 0) unless you set it to something else earlier.
    The data for day 0 is never saved or used by other core functions.
    
    @param day - a valid day of the month, as an integer. If this month
    has n days, you should not use any days greater than n.
    @return - the DataPoint object corresponding to the time series data
    of the given day of this month.
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
    
    @return - the string representation of a list of comma-separated-values 
    that is the price data of a commodity for this month.
    '''
    def __str__( self ):
        
        #we hard code the first print so that we can avoid having a
        #trailing newline at the end
        rtn = DateUtils.format_day( 1 ) + \
            "," + self.data[ 1 ].str_without_date()
            
        for i in range( 2 , self.numDays+1 ):
            rtn = rtn + "\n" + \
                DateUtils.format_day( i ) + \
                "," + self.data[ i ].str_without_date()
        
        return rtn

'''
Provides functions for reading in price data.
'''     
class PriceReader( object ):
    
    '''
    Reads in price data for a given month and returns a MonthData object
    with all that data. If the data does not exist, then all the datapoints
    will have daily price 0 and average price 0. Note that the name of the
    commodity is CASE SENSITIVE.
    
    @param month - the month of the price data to read, as an integer
    @param year - the year of the price data to read, as an integer
    @param commodity - the name of the commodity for which to look up price data,
    as a string. This string is CASE SENSITIVE.
    @return - a MonthData object with all the price information for the
    given commodity during the given month and year time period.
    '''
    @staticmethod
    def read_month_data( month , year , commodity ):
        rtn = MonthData( month , year )
        dir = "price_data/" + str( year ) + " " + DateUtils.format_month( month )
        try :
            file = open( dir + "/" + commodity + ".csv" , "r" )
            lines = file.readlines()
            for line in lines :
                datapoint = DataPoint.from_csv_month_data( year , month , line )
                rtn.set( int( datapoint.get_day() ) , datapoint )
        except IOError:
            
            #there is no data, so ignore the error and return default
            #values of 0 for daily and average prices
            pass
        
        return rtn
        
    '''
    Gets price data for a given commodity from a CSV file or returns
    None if the CSV file for the given commodity ID was not found
    
    @param commodityId - the ID of a commodity, as an integer
    @param filename - the name of the CSV file from which to read data, as
    a string. If the CSV file does not exist, None will be returned.
    @return - a CommodityPriceData object with all the 
    '''
    @staticmethod
    def get_price_data_from_csv( commodityId ):
        filename = "price_data/master_list/" + str( commodityId ) + ".csv"
        try:
            f = open( filename , "r" )
            
            #have to get rid of the \n at the end of the line
            name = f.readline()[0:-1]
            datapoints = []
            for line in f:
                datapoints.append( DataPoint.from_csv_data( line ) )
            return CommodityPriceData( commodityId , name , datapoints )
        except IOError:
            return None
        
'''
Provides functions for writing daily and average price data to the 
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
        PriceWriter.save_list_data( priceData )
    
    '''
    '''
    @staticmethod
    def save_list_data( priceData ):
        filename = "price_data/master_list/" + str( priceData.get_id() ) + ".csv"
        PriceWriter.write_price_data_to_csv( filename , priceData )
        
    '''
    Saves the data in a CommodityPriceData object to the 
    '''
    @staticmethod
    def save_month_data( priceData ):
        months = {}
        for i in range( 0 , priceData.get_num_datapoints() ):
            datapoint = priceData.get_data_at( i )
            key = (datapoint.get_month() , datapoint.get_year() )
            
            #read in the data for the month if it exists
            if ( not months.has_key( key ) ):
                months[ key ] = PriceReader.read_month_data( \
                    int(datapoint.get_month()) , int(datapoint.get_year()) , priceData.get_name() )
                    
            #the MonthData object must have been created and contains whatever
            #values were stored on the hard drive. We now merge
            #our price data into it.
            prevData = months[ key ].get( int(datapoint.get_day()) )
            
            #since json does not have volume data, it will always have
            #volumes of 0. If our past data has nonzero volumes already 
            #recorded, we don't want to lose that! So, we will merge
            #the old data's volume into the new data's volume.
            if ( prevData.get_volume() != 0 and datapoint.get_volume() == 0 ):
                datapoint.initialize_volume( prevData.get_volume() )
                
            #everything else, other than the volume, can be overwritten
            #by the merge.
            months[ key ].set( int(datapoint.get_day()) , datapoint )
        
        #after all data has been merged, we can rewrite the updated
        #data back to the hard drive
        for monthData in months.values() :
            PriceWriter.write_month_data_to_file( monthData , priceData.get_name() )
    
    '''
    Writes the month data for a given commodity to the appropriate file.
    
    @param monthData - the MonthData object to be saved
    @param commodity - the name of the commodity as a string
    '''
    @staticmethod
    def write_month_data_to_file( monthData , commodity ):
        month = DateUtils.format_month( monthData.month )
        year = str( monthData.year )
        datafile = "price_data/" + year + " " + month + "/" + commodity + ".csv" 
        
        #create the new month folder, if necessary
        if ( not os.path.exists( os.path.dirname( datafile ) ) ):
            os.makedirs( os.path.dirname( datafile ) )
            
        f = open( datafile , "w" )
        f.write( str( monthData ) )
                    
    '''
    Writes some price data to a CSV file.
    
    @param filename - the file to which to write price data
    @param priceData - the CommodityPriceData object to save to a CSV file
    '''      
    @staticmethod
    def write_price_data_to_csv( filename , priceData ):
        f = open( filename , "w" )
        f.write( priceData.get_name() + "\n" )
        for datapoint in priceData.get_all_datapoints():
            f.write( str( datapoint ) + "\n" )
        f.close()
    
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
    #Mithril ore
    priceData = PriceCrawler.get_price_data_from_html( 447 )
    PriceWriter.save_data( priceData )
    
    #Mithril bar
    priceData = PriceCrawler.get_price_data_from_html( 2359 )
    PriceWriter.save_data( priceData )
    
    priceData = PriceCrawler.get_price_data_from_json( "Mithril bar" , 2359 )
    PriceWriter.save_data( priceData )
    
    #404 Error
    priceData = PriceCrawler.get_price_data_from_html( 21736 )
    assert( priceData == None )
    
    assert PriceReader.get_price_data_from_csv( 447 ) == PriceCrawler.get_price_data_from_html( 447 )
    
    print "Regression testing for price_data_io.py passed."

if __name__ == "__main__" : main()