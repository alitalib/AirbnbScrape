import pandas as pd 
import numpy as np
import datetime as dt
import sexmachine.detector as gender

# Read data as a pandas dataframe
def DataClean(data):
    
    #convert datetime to membership length 
    data['MemberDateNew'] = pd.DataFrame(data['MemberDate']).applymap(DeleteSpace).MemberDate
    data['MemberLength'] = dt.datetime.strptime('2014-11-25', '%Y-%m-%d') - data.MemberDateNew.apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))  
    data.loc[:, 'MemberLength'] = data['MemberLength'].apply(TimeDelta)
    
    # Define d to detect gender 
    data['HostGender'] = gender(data)
    
    #parse short description 
    data['SD_PropType'] = data.ShortDesc.apply(getPropType)
    data['SD_NumReviews'] = data.ShortDesc.apply(getNumReviews)
    data['SD_Neighborhood'] = data.ShortDesc.apply(getNeighborhood)
    
    # Save the clearned dat
    data.to_csv('Final_v2.csv')
    
    #return the cleaned variables 
    return data[['MemberLength', 'HostGender','SD_PropType','SD_NumReviews', 'SD_Neighborhood']]
    
# Create a new variable 'MemberDateNew' indicating the date when the host became a member
# The 1st day of the month is used for all hosts
def DeleteSpace(x): 
    try:
        return str(dt.datetime.strptime(' ' .join(x.split(' ')[-2:]), '%B %Y').date())
    except:
        return '9999-01-01'   # for errorneous values return 9999-01-01

# Create a new variable 'Memberlength' indicating days of membership of the host
def TimeDelta(x):
    days = x.astype('timedelta64[D]')
    return days / np.timedelta64(1, 'D')

# Create a list of host genders and attach the list to the dataset
def gender(dataframe):
    gender_list = []
    
    import sexmachine.detector as gender
    d = gender.Detector()
    
    #read in host names 
    host_name = dataframe["HostName"]
    
    #for loop to loop in every host name and judge the gender 
    for hostname in host_name:
        if "&" in hostname or "And" in hostname or "/" in hostname:
            gender = "couple"
        else :
            first_name = hostname.split(" ")[0]
            gender = d.get_gender(first_name).encode('utf8')
        gender_list.append(gender)
     
    return gender_list

def parseShortDesc(x, index):
    """
    This is a helper function that parses the ShortDesc field in the raw data into a 
    list of three distinct values
    """
    parsedVals = []
    finalVals = []
    
    #The data had two different type of "delimiters" in the Short Desc field, we try one, and if that doesn't 
    #work, we try the other one. 
    
    vals =  x.split('\xcc\xe2\xe5\xe1')
    if len(vals) < 2:
        vals = x.split('\x95\xc0_\x95\xc0_')
    
    #Clean Up non-essential words in the results set such as spaces, newlines and the word "reviews"
    for val in vals:
        temp = val.strip().replace(' reviews', '').replace(' review', '')
        parsedVals.append(temp)
    
    #Determine if there are missing values in the list and fill in the blanks
    if len(parsedVals) == 3:
        finalVals = parsedVals[:]
            
    if len(parsedVals) == 2:
        finalVals = [parsedVals[0], 0, parsedVals[1]]
    
    if len(parsedVals) < 2: 
        finalVals = ['Unknown', 0, 'Unknown']
    
    return finalVals[index]


def getPropType(x):
    """
    Gets the property type from the 
    ShortDesc field
    """
    return parseShortDesc(x, 0)

def getNumReviews(x):
    """
    Gets the number of reviews from the 
    ShortDesc field
    """
    return parseShortDesc(x,1)

def getNeighborhood(x):
    """
    Gets the neighborhood from the 
    ShortDesc field
    """
    return parseShortDesc(x, 2)
