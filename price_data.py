# -*- coding: utf-8 -*-

from date_utils import DateUtils 
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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
    
    '''
    Creates a DataPoint from some CSV data that contains the
    day, daily price, average price, and trade volume of a data point.
    
    @param year - the year of the DataPoint, as a string of length 4
    @param month - the month of the DataPoint, as a string of length 2
    @param data - the CSV data
    '''
    @staticmethod
    def from_csv_month_data( year , month , data ):
        values = data.split( "," )
        day = str( values[ 0 ] )
        daily = int( values[ 1 ] )
        average = int( values[ 2 ] )
        traded = int( values[ 3 ] )
        return DataPoint( year , month , day , daily , average , traded )
     
    '''
    Creates a DataPoint from some CSV data that contains the 
    year, month, day, daily price, average price, and trade volume of
    a DataPoint.
    
    @param data - the CSV data
    '''
    @staticmethod
    def from_csv_data( data ):
        values = data.split( "," )
        year = str( values[ 0 ] )
        month = str( values[ 1 ] )
        day = str( values[ 2 ] )
        daily = int( values[ 3 ] )
        average = int( values[ 4 ] )
        traded = int( values[ 5 ] )
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
    Determines if this DataPoint comes before another DataPoint's time.
    
    @param otherDatapoint - another Datapoint with which to compare precedence
    '''        
    def is_before( self , otherDatapoint ):
        return DateUtils.is_after( int( self._year ) , int( self._month ) , \
            int( self._day ) , int( otherDatapoint._year ) , \
            int( otherDatapoint._month ) , int( otherDatapoint._day ) )
    
'''
Stores daily and average price time series data for a commodity. 

This object maintains a list of DataPoint objects. What specific data is stored
is determined by the DataPoint class structure.
'''
class CommodityPriceData( object ):
    
    '''
    Creates a CommodityPriceData object with the given time series data.
    
    @param id - the ID of the commodity, as an integer
    @param name - the name of the commodity, as a string
    @param datapoints - the time series data of the prices of this commodity
    as a list of DataPoint objects
    '''
    def __init__( self , id , name , datapoints ):
        self._id = id
        self._name = name
        self._datapoints = datapoints

    '''
    @return - the ID of this commodity, as an integer
    '''        
    def get_id( self ):
        return self._id
        
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
        
    '''
    Adds the given datapoint to the end of the list of datapoints. 
    WARNING: There are no checks. You must make sure you do not append
    an out of order datapoint! In particular, the datapoint
    you are appending should come after all previous datapoints
    
    @param datapoint - the DataPoint obejct to append
    '''
    def append_datapoint( self , datapoint ):
        self._datapoints.append( datapoint )
        
    def __str__( self ):
        rtn = "Price data for " + self._name
        for i in range( 0 , len( self._datapoints ) ):
            rtn += "\n[" + str( self._datapoints[ i ] ) + "]";
        return rtn
        
    def __eq__( self , other ):
        return self._id == other._id and \
            self._name == other._name and \
            self._datapoints == other._datapoints
            
    '''
    Plots the price of this commodity over time.
    '''
    def plot_price_over_time( self ):
        times = np.array( [ datetime.strptime( x.get_year() + "-" + \
                    x.get_month() + "-" + x.get_day() , "%Y-%m-%d" ) \
                    for x in self._datapoints ] )
        prices = np.array([ x.get_price() for x in self._datapoints ])
        plt.clf()
        plt.plot( times , prices , marker="o" )
        plt.suptitle( self._name )
        plt.xlabel( "t" )
        plt.ylabel( "Price" )
        plt.show()
            
def main():
    p1 = DataPoint( "2015" , "08" , "01" )
    p2 = DataPoint( "2015" , "08" , "22" )
    assert p1.is_before( p2 )
    assert p2.is_before( p1 ) == False
    
    print "Regression testing for price_data passed."

if __name__ == "__main__" : main()