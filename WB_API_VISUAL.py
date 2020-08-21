# This python scrpt will grab the Data from Worl dbank API and draw the NASA 'Blue marble' Image on world map, pointing the user given countries according to their income level and shows latest values of DP Growth, GDP and GNI per capita. 
# Also, that will show the GDP Growth, GDP and GNI per capita growth comparison by line graph. 
  
# To run:
# python World_Data.py India "United States" Zimbabwe Brazil
###########################
'''

import sys
import wbdata
import pandas
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from numpy.random import randn

# Save countries in a Dictionary and checking that use must give at least one Country
countries=[]
if(len(sys.argv) >=2):
    for i in range(1,len(sys.argv)):
        countries.append(str(sys.argv[i]))
else:
    print "Error you passed", len(sys.argv)-1, 'countries'
    quit()

# Save the details about the country in a Dictionary
country_dict={}
for c in countries:
    # Get data about the countries using World bank Data API, if the country name is not in data set tell user that that perticuler country is not in dataset
    dat= wbdata.search_countries(c, incomelevel=False, lendingtype=False, display=False)
    if len(dat) == 0: 
        raise SystemExit ('The country '+ c + ' is not in dataset.')
    else:
        name = dat[0][u'name']
        latitude = dat[0][u'latitude']
        longitude = dat[0][u'longitude']
        region = dat[0][u'region'][u'value']
        capital = dat[0][u'capitalCity']
        income_level = dat[0][u'incomeLevel'][u'value']
        country_code = dat[0][u'iso2Code']
        country_dict[name]={"latitude":latitude,"longitude":longitude,"country_code":country_code, "region":region, "capital_city":capital, "income_level":income_level}

# Save the country name as per country code becasue GDP, GNI per capita and GDP growth indicators work with country code
code_list=[]
for c in countries:
    dat= wbdata.search_countries(c, incomelevel=False, lendingtype=False, display=False)
    name = dat[0][u'name']
    code_list.append(country_dict[name]["country_code"])

#set up the indicator 
indicatorGDP = {'NY.GDP.MKTP.CD':'GDP'}
indicatorGDPGrowth = {'NY.GDP.MKTP.KD.ZG':'GDP Growth (Annual %)'}
indicatorGNI = {'NY.GNP.PCAP.CD':'GNI per capita, Atlas method (Current US$)'}

#grab indicators above for countires above and load into data frame
dfGDP = wbdata.get_dataframe(indicatorGDP, country=code_list, convert_date=False)
dfGDP.sort_index(inplace=True)
dfGDPGrowth = wbdata.get_dataframe(indicatorGDPGrowth, country=code_list, convert_date=False)
dfGDPGrowth.sort_index(inplace=True)
dfGNI = wbdata.get_dataframe(indicatorGNI, country=code_list, convert_date=False)
dfGNI.sort_index(inplace=True)

#df is "pivoted", pandas' unstack function helps reshape it into something plottable
dfu = dfGDP.unstack(level=0)
dfu1 = dfGDPGrowth.unstack(level=0)
dfu2 = dfGNI.unstack(level=0)
 
#A line graph which shows GDP
dfu.plot();
plt.legend(loc='best');
plt.title("GDP ($USD)");
plt.xlabel('Date'); plt.ylabel('GDP ($USD)');
plt.show()


#A line graph which shows GDP Growth Annual
dfu1.plot();
plt.legend(loc='best');
plt.title("GDP Growth (Annual %)");
plt.xlabel('Date'); plt.ylabel("GDP Growth (Annual %)");
plt.show()

#A line graph which shows GNI per Capita
dfu2.plot();
plt.legend(loc='best');
plt.title('GNI per capita, Atlas method (Current US$)');
plt.xlabel('Date'); plt.ylabel('GNI per capita, Atlas method (Current US$)');
plt.show()


# Make a function which gives the recent value of the indicator
def getRecentValue(dict):
    keys = dict.keys()
    keys.sort(reverse=True)
    for k in keys:
        # This will ingonore all missing values
        if pandas.notnull(dict[k]):
            return dict[k]
#Make a function which gives the recent value of the indicator year
def getRecentValueYear(dict):
    keys = dict.keys()
    keys.sort(reverse=True)
    for k in keys:
        # This will ingonore all missing values
        if pandas.notnull(dict[k]):
            return k

# Get the recent value of GDP
# Set the counter which takes only one country code from the list
cntr = 0
# This dictionary will save the the latest value of GDP 
dictGDP={}
# This dictionary will save the the year for which the recent GDP is available
dictGDPY={}
for c in countries:
    dfGDP = wbdata.get_dataframe(indicatorGDP, country=code_list[cntr], convert_date=False)
    cntr += 1
    GDPDict = {}
    for index, row in dfGDP.iterrows():
        GDPDict[index] = row[0]
    dictGDP[c]=getRecentValue(GDPDict)
    dictGDPY[c]=getRecentValueYear(GDPDict)
    GDPDict.clear()

# Get the recent value of GDP Growth
cntr = 0
# This dictionary will save the the latest value of GDPGrowth
dictGDPGrowth={}
# This dictionary will save the the year for which the recent GDPGrowth is available
dictGDPGrowthY={}
for c in countries:
    dfGDPGrowth = wbdata.get_dataframe(indicatorGDPGrowth, country=code_list[cntr], convert_date=False)
    cntr += 1
    GDPGrowthDict = {}
    for index, row in dfGDPGrowth.iterrows():
        GDPGrowthDict[index] = row[0]
    dictGDPGrowth[c]=getRecentValue(GDPGrowthDict)
    dictGDPGrowthY[c]=getRecentValueYear(GDPGrowthDict)
    GDPGrowthDict.clear()

# Get the recent value of GNI per capita
cntr = 0
# This dictionary will save the the latest value of GNI
dictGNI={}
# This dictionary will save the the year for which the recent GNI is available
dictGNIY={}
for c in countries:
    dfGNI = wbdata.get_dataframe(indicatorGNI, country=code_list[cntr], convert_date=False)
    cntr += 1
    GNIDict = {}
    for index, row in dfGNI.iterrows():
        GNIDict[index] = row[0]
    dictGNI[c]=getRecentValue(GNIDict)
    dictGNIY[c]=getRecentValueYear(GNIDict)
    GNIDict.clear()



text_add=""
# Draw a map showing the location of the country referring it's capital city 
for c in country_dict:
    m = Basemap(projection='mill')
    LAlon, LAlat = float(country_dict[c]['longitude']), float(country_dict[c]['latitude'])  
    xpt, ypt = m(LAlon, LAlat)
    plt.text(xpt,ypt,c, fontsize=10, weight= 'bold', color='w')
    # If the country income level is Low income then it will be represented with Red Dot  
    if (country_dict[c]['income_level'] == 'Low income'):
        m.plot(xpt, ypt, 'ro', markersize=8)
    # If the country income level is Lower middle income then it will be represented with Yellow Dot  
    if (country_dict[c]['income_level'] == 'Lower middle income'):
        m.plot(xpt, ypt, 'yo', markersize=8)
    # If the country income level is Upper middle income then it will be represented with Blue Dot      
    if (country_dict[c]['income_level'] == 'Upper middle income'):
        m.plot(xpt, ypt, 'bo', markersize=8)
    # If the country income level is High income then it will be represented with Green Dot  
    if (country_dict[c]['income_level'] == 'High income'):
        m.plot(xpt, ypt, 'go', markersize=8)
    # Add the text information to show on the plot 
    text_add+="Country: "+ c + "\nCapital City: "+ country_dict[c]["capital_city"]+ "\nIncome Level: "+country_dict[c]["income_level"]+"\nGDP Growth("+str(dictGDPGrowthY[c]) +"): "+ str(dictGDPGrowth[c])[:5]+" %"+"\nGNI per Capita("+str(dictGNIY[c]) +"): $"+str(dictGNI[c])+"\nGDP("+str(dictGDPY[c]) +"): $" +str(float(dictGDP[c]/1000000000000))[:5]+" Trillion"  + "\n\n"

# Make and plot legend for income level
# Draw the coastlines on worldmap
m.drawcoastlines()
# Draw the country bounderis on worldmap
m.drawcountries()
# Draw the NASA 'Blue marble' Image
m.bluemarble()
z = randn(10)
# Defining legends
red_dot, = plt.plot(z, "ro", markersize=6)
yellow_dot, = plt.plot(z, "yo", markersize=6)
blue_dot, = plt.plot(z, "bo", markersize=6)
green_dot, = plt.plot(z, "go", markersize=6)
plt.legend([red_dot, yellow_dot, blue_dot, green_dot],["Low income", "Lower middle income", "Upper middle income", "High income"], loc=4)
plt.text(0,0,text_add, fontsize=8, weight='bold',color='r')
#Show the graph showing the text, map and legends
plt.show()