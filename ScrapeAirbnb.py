# -*- coding: utf-8 -*-
"""
Created on Sat Nov  1 20:29:41 2014

@author: Hamel Husain, TODO: Name Everyone In Group
CS109 Harvard Intro To Data Science
Scraping Airbnb
"""

import mechanize
import cookielib
from lxml import html
import csv
import json
import re
from random import randint
from time import sleep
from lxml.etree import tostring
import bs4



# Browser
br = mechanize.Browser()


#learned necessary configuration from 
#http://stockrt.github.io/p/emulating-a-browser-in-python-with-mechanize/

# Allow cookies
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
#specify browser to emulate
br.addheaders = [('User-agent', 
'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

#######################################
#  Wrapper Functions    ###############
#######################################

def IterateMainPage(location_string, loop_limit): 
    MainResults = []
    """
    input: 
        location_string (string) - this is a location string that conforms to the 
                                   pattern on airbnb for example, 
                                   Cambridge, MA is "Cambridge--MA"
        loop_limit (integer) -    this is the maximum number of pages you want to parse.
        
    output:
        list of dictionaries, with each list element corresponding to a unique listing
        
    This function iterates through the main listing pages where different properties
    are listed and there is a map, and collects the list of properties available along
    with the limited amount of information that is available in that page.  This function
    returns a list of dictionaries with each list element corresponding to a unique listing. 
    Other functions will take the output from this function and iterate over them to explore
    the details of individual listings.  
    """  
        
    base_url = 'https://www.airbnb.com/s/'
    page_url = '?page='
    
    
    try:
        for n in range(1, loop_limit+1):
            print 'Processing Main Page %s out of %s' % (str(n), str(loop_limit))
            #Implement random time delay for scraping
            sleep(randint(10,30))
            current_url = ''.join([base_url, location_string, page_url, str(n)])
            MainResults += ParseMainXML(current_url, n)
        
            
    except:
        print 'This URL did not return results: %s ' % current_url
    
    print 'Done Processing Main Page'
    return MainResults



    
#######################################
#  Main Page    #######################
#######################################


def ParseMainXML(url= 'https://www.airbnb.com/s/Cambridge--MA--United-States', pg = 0):
    
    """
    input: url (string )
            
            this is the url for the type of listings you want to search. 
            default is to use the generic url to search for listings 
            in Cambridge, MA
    input: pg (integer)
        
            this is an integer corresponding to the page number, this is meant
            to be passed in by the wrapper function and collected in the dictionary.
            
    output: dict
    ------
    This funciton parses the main page with mulitple airbnb listings, and 
    returns a list of dictionaries corresponding to the attributes found
    """   
    n = 1
    ListingDB = []
           
    try:
        
        tree = html.fromstring(br.open(url).get_data())
        listings = tree.xpath('//div[@class="listing"]')

        #TODO: add error handling    
        for listing in listings:
            dat = {}
            dat['baseurl'] = url
            dat['Lat'] = listing.attrib.get('data-lat', 'Unknown')
            dat['Long'] = listing.attrib.get('data-lng', 'Unknown')
            dat['Title'] = listing.attrib.get('data-name', 'Unknown')
            dat['ListingID'] = listing.attrib.get('data-id', 'Unknown')
            dat['UserID'] = listing.attrib.get('data-user', 'Unknown')
            dat['Price'] = ''.join(listing.xpath('div//span[@class="h3 price-amount"]/text()'))
            dat['PageCounter'] = n
            dat['OverallCounter'] = n * pg
            dat['PageNumber'] = pg
            
            ShortDesc = listing.xpath('div//div[@class="media"]/div/a')
            
            if len(ShortDesc) > 0:
                dat['ShortDesc'] = ShortDesc[0].text
            
            if len(listing.xpath('div/div//span/i')) > 0:
                dat['BookInstantly'] = 'Yes'
            
            else:
                dat['BookInstantly']  = 'No'
                
            ListingDB.append(dat)
            n += 1
        
        return ListingDB
        
    except:
        print 'Error Parsing Page - Skipping: %s' % url
        #if there is an error, just return an empty list
        return ListingDB
        
    

#######################################
#  Detail Pages #######################
#######################################

def iterateDetail(mainResults):
    """
    This function takes the list of dictionaries returned by the
    IterateMainPage, and "enriches" the data with detailed data
    from the particular listing's info - if there is an error
    with getting that particular listing's info, the dictionary
    will be populated with default values of "Not Found"
    """
    finalResults = []
    counter = 0
    
    baseURL = 'https://www.airbnb.com/rooms/'    
    for listing in mainResults:
        counter += 1      
        print 'Processing Listing %s out of %s' % (str(counter), str(len(mainResults)))
        
        #Construct URL
        currentURL = ''.join([baseURL, str(listing['ListingID'])])
        
        #Get the tree         
        tree = getTree(currentURL)
        
        #Parse the data out of the tree      
        DetailResults = collectDetail(tree, listing['ListingID'])
        
        #Collect Data
        newListing = dict(listing.items() + DetailResults.items())
        
        #Append To Final Results
        finalResults.append(newListing)
        
    return finalResults
        
        
def getTree(url):
    """
    input
        url (string): this is a url string.  example: "http://www.google.com"
    
    output
        tree object:  will return a tree object if the url is found, 
        otherwise will return a blank string
    """
    try:
        #Implement random time delay for scraping
        sleep(randint(10,30))
        tree = html.fromstring(br.open(url).get_data())
        return tree
        
    except:
        #Pass An Empty String And Error Handling Of Children Functions Will Do 
        #Appropriate Things
        print 'Was not able to fetch data from %s' % url
        return ''


def collectDetail(treeObject, ListingID):
    Results = {'AboutListing': 'Not Found', 
                     'TheSpace': 'Not Found',
                     'HostName': 'Not Found',
                     'RespRate': 'Not Found',
                     'RespTime': 'Not Found',
                     'MemberDate': 'Not Found',
                     'R_acc' : 'Not Found',
                     'R_comm' : 'Not Found',
                     'R_clean' : 'Not Found',
                     'R_loc': 'Not Found',
                     'R_CI' : 'Not Found',
                     'R_val' : 'Not Found',
                     'R_clean' : 'Not Found'
                     }     
    try: 
        #Hamel's Functions
        ###################                    
        Results['AboutListing'] = getAboutListing(treeObject, ListingID)
        Results['TheSpace'] = getSpaceInfo(treeObject, ListingID)
        
        #Yi's Functions
        ####################
        Results['HostName'] = getHostName(TreeToSoup(treeObject), ListingID)
        Results['RespRate'], Results['RespTime'] = getHostResponse(TreeToSoup(treeObject), ListingID)
        Results['MemberDate'] = getMemberDate(TreeToSoup(treeObject), ListingID)
        
        #accuracy, communication, cleanliness, location, checkin, value
        Results['R_acc'], Results['R_comm'], Results['R_clean'], Results['R_loc'], \
        Results['R_CI'], Results['R_val'] = getStars(TreeToSoup(treeObject), ListingID)
        #price
        """
         {'ExtraPeople': 'Not Found', 'CleaningFee': 'Not Found', 'SecurityDeposit': 'Not Found', 
       'WeeklyPrice': 'Not Found','MonthlyPrice': 'Not Found','Cancellation' : 'Not Found'} 
    
        """
        PriceData = getPriceInfo(treeObject, ListingID)
        Results['P_ExtraPeople'] = PriceData['ExtraPeople']
        Results['P_Cleaning'] = PriceData['CleaningFee']
        Results['P_Deposit'] = PriceData['SecurityDeposit']
        Results['P_Weekly'] = PriceData['WeeklyPrice']
        Results['P_Monthly'] = PriceData['MonthlyPrice'] 
        Results['Cancellation'] = PriceData['Cancellation']
        
        
        return Results
        
    except:
        #Just Return Initialized Dictionary
        return Results



def TreeToSoup(treeObject):
    """
    input: HTML element tree
    output: soup object (Beautiful Soup)
    This function converts an HTML element tree to a soup object
    """
    source = tostring(treeObject)
    soup = bs4.BeautifulSoup(source)
    return soup
    
#############################################
### Yi's Functions #########################    

def getHostName(soup, ListingID): 
    """
    Written by Yi
    """
    host_name = 'Not Found'
    
    try:
        host_name = soup.find_all("h4", {"class" : "row-space-4"})[2].text.strip("\n ").encode('utf8')
        host_name = host_name.split(", ")[1]
        return host_name
    
    except:
        print 'Unable to parse host name for listing id: %s' % str(ListingID)
        return host_name

def getHostResponse(soup, ListingID):
    """
    Written by Yi
    """
    response_rate, response_time = ['Not Found'] * 2
    
    try:
        host_member = soup.find_all("div", {"class" : "col-6"})[-1]
        response_rate = host_member.find_all("strong")[0].text.encode('utf8')
        response_time = host_member.find_all("strong")[1].text.encode('utf8')
        return response_rate, response_time          
        
    except:
        print 'Unable to parse host name for listing id: %s' % str(ListingID)
        return response_rate, response_time     


def getMemberDate(soup, ListingID):
    """
    Written by Yi
    """
    membership_date = 'Not Found'    
    
    try:
        host_member = soup.find_all("div", {"class" : "col-6"})[-2]
        membership_date = host_member.find_all("div")[1].text.encode('utf8').strip("\n ")
        membership_date = membership_date.replace("Member since", "")
        return membership_date
        
    except:
        print 'Unable to parse membership date for listing id: %s' % str(ListingID)
        return membership_date      


def singlestar(index, soup):
    """
    Written by Yi
    """
    stars = soup.find_all("div", {"class" : "foreground"})[index]
    full_star = stars.find_all("i", {"class" : "icon icon-pink icon-beach icon-star"})
    half_star=  stars.find_all("i", {"class" : "icon icon-pink icon-beach icon-star-half"})
    total_star = len(full_star)+len(half_star)*0.5
    return total_star


def getStars(soup, ListingID):
    """
    Written by Yi
    """
    accuracy, communication, cleanliness, location, checkin, value = ['Not Found'] * 6
    
    try:
        #accuracy starts at the thrid stars, right after the total reviews 
        accuracy = singlestar(2, soup)
        communication = singlestar(3, soup)
        cleanliness = singlestar(4, soup)
        location = singlestar(5,soup)
        checkin = singlestar(6,soup)
        value = singlestar(7,soup)
        return accuracy, communication, cleanliness, location, checkin, value
    
    except:
        print 'Unable to parse stars listing id: %s' % str(ListingID)
        return accuracy, communication, cleanliness, location, checkin, value

#########################################
## Hamel's Functions ####################     

def getAboutListing(tree, ListingID):
    """
    input: xmltree object
    output: string
    -----------------
    This function parses an individual listing's page to find 
    the "About This Listing" and extracts the associated text
    """  
    try:
    #Go To The Panel-Body
        elements = tree.xpath('//div[@class="panel-body"]/h4')

        #Search For "About This Listing" In Elements    
        for element in elements:
            if element.text.find('About This Listing') >= 0:
                #When You Find, it return the text that comes afterwards
                return element.getnext().text

    except:
        print 'Error finding *About Listing* for listing ID: %s' % ListingID
        return 'No Description Found'

        
        
def getSpaceInfo(tree, ListingID = 'Test'):  
    
    """
    input: xmltree object
    output: dict
    -----------------
    This function parses an individual listing's page to find 
    the all of the data in the "Space" row, such as Number of 
    Bedrooms, Number of Bathrooms, Check In/Out Time, etc.
    """ 
    #Initialize Values
    dat = {'PropType': 'Not Found', 'Accommodates': 'Not Found', 
           'Bedrooms': 'Not Found', 'Bathrooms' : 'Not Found',
           'NumBeds': 'Not Found', 'BedType': 'Not Found', 
           'CheckIn': 'Not Found', 'CheckOut': 'Not Found'}    
    
    try:
        #Get Nodes That Contain The Grey Text, So That You Can Search For Sections
        elements = tree.xpath('//*[@class="text-muted"]')
    
          #find The space portion of the page, 
          #then go back up one level and sideways one level
        for element in elements:
          
            if element.text.find('The Space') >= 0:
                #If you find what you are looking for Go Up One Level Then Go Sideways
                targetelement = element.getparent().getnext()
                break
            
        #Depth - First Search of The Target Node
        descendants = targetelement.iterdescendants()
        
        for descendant in descendants:
            #check to make sure there is text in descendant
            if descendant.text:                
                ##Find Property Type##
                if descendant.text.find('Property type:') >= 0:  
                    prop =  descendant.xpath('.//strong/*')
                
                    if len(prop) >= 1:
                        dat['PropType'] = prop[0].text
                
                ##Find Accomodates ####
                if descendant.text.find('Accommodates:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['Accommodates'] = prop[0].text
                        
                ##Find Bedrooms ####
                if descendant.text.find('Bedrooms:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['Bedrooms'] = prop[0].text
                        
                ##Find Bathrooms ####
                if descendant.text.find('Bathrooms:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['Bathrooms'] = prop[0].text
                        
                ##Find Number of Beds ####
                if descendant.text.find('Beds:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['NumBeds'] = prop[0].text
               
               ##Find Bed Type ####
                if descendant.text.find('Bed type:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['BedType'] = prop[0].text               
               
               ##Find Check In Time ####
                if descendant.text.find('Check In:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['CheckIn'] = prop[0].text  
                
                ##Find Check Out Time ####
                if descendant.text.find('Check Out:') >= 0:
                    prop =  descendant.xpath('.//strong')
                    if len(prop) >= 1:
                        dat['CheckOut'] = prop[0].text   
        return dat
        
    except:
        print 'Error in getting Space Elements for listing iD: %s' % str(ListingID)
        return dat
        
#######################################
#  Xi's Functions #####################
#######################################

def getPriceInfo(tree, ListingID):      
    """
    input: xmltree object
    output: dict
    -----------------
    This function parses an individual listing's page to find 
    the all of the data in the "Price" row, such as Cleaning Fee, Security Deposit, Weekly Price, etc.
    """ 
    #Initialize Values
    dat = {'ExtraPeople': 'Not Found', 'CleaningFee': 'Not Found', 'SecurityDeposit': 'Not Found', 
       'WeeklyPrice': 'Not Found','MonthlyPrice': 'Not Found','Cancellation' : 'Not Found'} 
    
    try:
        #Get Nodes That Contain The Grey Text, So That You Can Search For Sections
        elements = tree.xpath('//*[@class="text-muted"]')
    
          #find The price portion of the page, 
          #then go back up one level and sideways one level
        for element in elements:
          
            if element.text.find('Prices') >= 0:
                #If you find what you are looking for Go Up One Level Then Go Sideways
                targetelement = element.getparent().getnext()
                break
            
        #Depth - First Search of The Target Node
        descendants = targetelement.iterdescendants()
        
        for descendant in descendants:
            #check to make sure there is text in descendant
            if descendant.text:                
                ##Find Extra People Free ##
                if descendant.text.find('Extra people:') >= 0:  
                    prop =  descendant.xpath('.//strong/*')
                    if len(prop) >= 1:
                        dat['ExtraPeople'] = prop[0].text
                
                ##Find Cleaning Fee ####
                if descendant.text.find('Cleaning Fee:') >= 0:
                    prop =  descendant.xpath('.//strong/*')
                    if len(prop) >= 1:
                        dat['CleaningFee'] = prop[0].text
                        
                ##Find Security Deposit ####
                if descendant.text.find('Security Deposit:') >= 0:
                    prop =  descendant.xpath('.//strong/*')
                    if len(prop) >= 1:
                        dat['SecurityDeposit'] = prop[0].text
                        
                ##Find Weekly Price ####
                if descendant.text.find('Weekly Price:') >= 0:
                    prop =  descendant.xpath('.//strong/*')
                    if len(prop) >= 1:
                        dat['WeeklyPrice'] = prop[0].text
                        
                ##Find Monthly Price ####
                if descendant.text.find('Monthly Price:') >= 0:
                    prop =  descendant.xpath('.//strong/*')
                    if len(prop) >= 1:
                        dat['MonthlyPrice'] = prop[0].text
                
                ##Find Cancellation ####
                if descendant.text.find('Cancellation:') >= 0:
                    prop =  descendant.xpath('.//strong/*')
                    if len(prop) >= 1:
                        dat['Cancellation'] = prop[0].text  
        return dat
        
    except:
        print 'Error in getting Space Elements for listing iD: %s' % str(ListingID)
        return dat
        
        
#######################################
#  Testing ############################
#######################################

if __name__ == '__main__':   
    
    test = IterateMainPage('Cambridge--MA', 1)
    test2 = iterateDetail(test)
    print test2