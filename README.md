AirbnbScrape
============

Python Function To Scrape Airbnb

This code was made for Harvard CS109 Data Science Class
http://cs109.github.io/2014/

Purpose:
As a host of airbnb, we wanted to optimize the price of our listing, and wanted to understand things like: 
- How other people priced around me, relative to dimensions such as amenities, reviews, instant booking status, etc?
- Can I infer occupancy by looking at listing availability day over day and use that to optimize my price?
- What items appear to most influence the page rank, or how high up a listings appears on search results?

We wanted to be able to study this data, visualize it and see if we could glean additional insights than what is available on airbnb. 

###How To Use This Code:
The two main functions are:

1) **IterateMainPage()**  this function takes in a location string, and page limit as a parameter and downloads a list of dictionaries which correspond to all of the distinct listings for that location.  For example, calling IterateMainPage('Cambridge--MA', 10) will scrape all of the distinct listings that appear on pages 1-10 of the page listings for that location.  The output from this function will then be a list of dictionaries with each dictionary item corresponding to one unique listing on each page.  The location string is in the format of 'City--State', as that is how the URL is structured.  

2) **iterateDetail()**  this reads in the output of the function **IterateMainPage()** and visits each specific listing to get mroe detailed information.  If more detailed information is found, then the dictionary is updated to contain more values. 

