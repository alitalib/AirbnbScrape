#create dummy variables 
import pandas as pd

def cleanGender(x):
    """
    This is a helper funciton that will help cleanup the gender variable
    """
    if x in ['female', 'mostly_female']:
        return 'female'

    if x in ['male', 'mostly_male']:
        return 'male'

    if x in ['couple'] :
        return 'couple'
    else:
        return 'unknownGender'
    

def cleanBath(x):
    """
    This is a helper function to cleanup the number of bathrooms
    """
    #replacing 8+ rooms with 8 rooms
    if x == '8+':
        return 8
    
    #if the value is less than 8 and is a number keep it!
    if float(x) < 8:
        return x
    
    #all the other numbers look like garbage values
    #replace those with 1 bathroom since that is 90% of all properties
    else:
        return 1
    
def cleanBedrooms(x):
    """
    This is a helper function to cleanup the number of bedrooms
    """
    
    #All the valid values appear to be <= 6
    if float(x) <= 6:
        return x
    
    #replace those with 1 bedroom since that is 90% of all properties
    else:
        return 1
    
    
def cleanNumBeds(x):
    """
    This is a helper function to cleanup the number of physical beds
    """
    
    #All the valid values appear to be <= 6
    if float(x) <= 9:
        return x
    
    #replace those with 1 bed since that is 90% of all properties
    else:
        return 1
    
def cleanNumBeds(x):
    """
    This is a helper function to cleanup the number of physical beds
    """
    
    #All the valid values appear to be <= 6
    if float(x) <= 9:
        return x
    
    #replace those with 1 bed since that is 90% of all properties
    else:
        return 1
    
    
def cleanRespRate(x):
    """
    This is a helper function to cleanup the response rate
    """
    
    val =  str(x).replace('%', '').replace('$', '').strip()
    
    if str(x) == 'nan':
        return 93.8
    else:
        return val

def dummyCode(x,  cols = [u'BookInstantly', u'Cancellation', u'RespTime', u'S_BedType', u'S_PropType', u'SD_PropType', 
                          'HostGender']):   
    """
    This function turns selected categorical variables into dummy values
    and appends the new dummy values onto the dataframe

    """
    import pandas as pd
    
    dfCopy = x[:]
    
    dfCopy.RespRate = x.RespRate.apply(cleanRespRate)
    dfCopy.Price = x.Price.apply(cleanRespRate)
    dfCopy.HostGender = x.HostGender.apply(cleanGender)
    dfCopy.S_Bathrooms = x.S_Bathrooms.apply(cleanBath)
    dfCopy.S_Bedrooms = x.S_Bedrooms.apply(cleanBedrooms)
    dfCopy.S_NumBeds = x.S_NumBeds.apply(cleanNumBeds)
    
    for col in cols:
        DC = pd.get_dummies(x[col], col)
        dfCopy = pd.concat([dfCopy, DC], axis = 1)
    
    #GitRid Of Columns That Were Dummy Coded
    retainedCols = [a for a in dfCopy.columns if a not in cols]
    
    return dfCopy[retainedCols]
        

