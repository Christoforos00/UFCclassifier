#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 10:12:26 2020

@author: chris
"""

from bs4 import BeautifulSoup 
import urllib
import datetime
from datetime import datetime
import pandas as pd

def make_soup(url):
    page = urllib.request.urlopen(url)                                      #turinng the page into a BeautifulSoup object
    data = BeautifulSoup(page,"html.parser")
    return data

def isFutureEvent(rawDate):                                                 #Returns true if the date is not a future date
    rawDate = rawDate.replace(",", "").replace(" ","/")                     #Useful , since we don't want to iterate through future fights
    month_name = rawDate[:rawDate.index("/")] 
    datetime_object =datetime.strptime(month_name, "%B")

    rawDate =  str(datetime_object.month)+rawDate[rawDate.index("/"):]
    matchDate = datetime.strptime(rawDate, '%m/%d/%Y')
                                  
    return matchDate > datetime.now()



def getEventURLs():                                                         #fetching all the urls from past events
    allEventURLs = []
    for i in range(15,23):                                                   #visiting the 23 event pages ( since they were 23 in  4/9/2020)
        
    
        currentSoup = make_soup( "http://www.ufcstats.com/statistics/events/completed?page="+str(i) )
        for row in currentSoup.findAll('tr'):
            currentDate =  str( row.find('span'))[60:80].strip()  
            
            if (len(currentDate) == 0  or isFutureEvent(currentDate) ):
                continue
            
    
            for data in row.findAll('i'):
                allEventURLs.append(row.find('a')['href'])
    #print(allEventURLs.__len__())
    return allEventURLs


def getFightURLs():                                                         #fetching every fight url of every event
    allFightURLs = []
    for eventURL in getEventURLs():
        currentSoup = make_soup( eventURL )
        for row in currentSoup.findAll('tr'):
            for data in row.findAll('i'):
                allFightURLs.append(row.find('a')['href'])
                break;
                
    return allFightURLs

def getFightInfo():                                                         #does the main work
        
    for fightURL in getFightURLs():
        try:
            currentSoup = make_soup( fightURL )
            allTables = pd.read_html(fightURL)                              #use this ready function to import the wanted table quickly
            fightStats = allTables[0]                                       #then rename the columns for the fighter A
            
            columnNamesA = fightStats.columns
            columnNamesA = [col+ " A" for col in columnNamesA]
            fightStats.columns = columnNamesA
            
            for col in columnNamesA[1:]:                                                    #spliting data for fighters A and B
                fightStats[col] = fightStats[col].str.replace(" of ","/")                   
                currentCell = fightStats[col].values[0]
                partB = currentCell[ currentCell.index(" "): ]
                fightStats[col.replace("A","B")] = partB
                fightStats[col] = currentCell[ :currentCell.index(" ") ]
                        
                    
            fighterA_tags = currentSoup.findAll(class_="b-fight-details__person")   
            result = fighterA_tags[0].findAll('i')[0].text.strip() 
            if ( result == "D"):
                continue
            fightStats["winnerA"] = int(result == "W")               #get the winner and split the 2 fighters' names in different columns
            fighterAname = fighterA_tags[0].findAll('a')[0].text.strip() 
            fightStats["Fighter B"] = fightStats["Fighter A"].values[0][ len(fighterAname) :  ].strip()
            fightStats["Fighter A"] = fighterAname
                    
            fightHeader = currentSoup.findAll(class_="b-fight-details__fight-title")   
            fightStats["Class"] = fightHeader[0].text.replace("Bout","").strip()                                                                #save the weight class and method of fight finish in new columns
            fightStats["Method"] = currentSoup.findAll(class_="b-fight-details__text-item_first")[0].findAll('i')[1].text.strip() 
            fightStats["Finish Round"] = currentSoup.findAll(class_="b-fight-details__text-item")[0].text.replace("Round:","").strip()                  #save the rounds and the scheduled rounds
            fightStats["Scheduled Rounds"] = currentSoup.findAll(class_="b-fight-details__text-item")[2].text.replace("Time format:","").strip()[0:1] 
           
            fightStats.to_csv("/home/chris/anaconda3/UFC DATA.csv" , mode='a', header=False)
        except :
            print("Err\n")                                                              #around 10 fights have irregular formating show the code above cannot be implemented to them
            
print(datetime.now())
getFightInfo()                                                  #observe the time of execution
print(datetime.now())