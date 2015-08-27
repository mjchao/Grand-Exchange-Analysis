# -*- coding: utf-8 -*-

class DateUtils( object ):
    
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
    
    @param month - a month, as an integer
    @param year - a year, as an integer. This will be used if the month is a 
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
            return DateUtils.DAYS_IN_MONTH[ month ]
            
        '''
    Formats an integer month to be a string with length 2. This is just
    for consistency issues.
    
    @param month - a month, as an integer
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
    
    @param day - a day, as an integer
    @return - the given day as a string with length 2
    '''            
    @staticmethod
    def format_day( day ):
        rtn = str( day )
        if ( len( rtn ) == 1 ):
            rtn = "0" + rtn
            
        return rtn
        
    '''
    Determines if a given {year, month, day} date is after
    a {refYear, refMonth, refDay} date. All values should be
    provided as integers.
    
    @param refYear - the reference year, as an integer
    @param refMonth - the reference month, as an integer
    @param refDay - the reference day, as an integer
    @param year - the year of the date to compare to the reference date,
    as an integer
    @param month - the month of the date to compare to the reference date,
    as an integer
    @param day - the day of the date to compare to the reference date,
    as an integer
    '''
    @staticmethod
    def is_after( refYear , refMonth , refDay , year , month , day ):
        if ( year > refYear ):
            return True
        elif( year < refYear ):
            return False
        else:
            if ( month > refMonth ):
                return True
            elif( month < refMonth ):
                return False
            else:
                if ( day > refDay ):
                    return True;
                else:
                    return False