#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 13:33:14 2017

@author: aaron
"""

import pymongo
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os
import re
import requests
import time
import random

ua = UserAgent()


with open("mongo_pass.txt", "r") as file:
    mongo_pass = file.read().split("\n")[0]
    
base_url = "https://www.beeradvocate.com"

def parse_beer_formongo(page):
    """
    Takes a text file of html
    Returns a dictionary of beer information to update mongodb with
    """

    soup = BeautifulSoup(page, "lxml")

    desc = str(soup.find('div', {'style':'float:right; width:70%;'}))

    beer_stats = str(soup.find(id="item_stats"))

    rating_tags = soup.findAll(id="rating_fullview_container")
    reviews = []
    for rating_tag in rating_tags:
        ba_user_id = rating_tag['ba-user']
        reviews.append({ba_user_id : str(rating_tag)})


    beer_field = {'description' : desc, 'beer_stats' : beer_stats, 'reviews' : reviews}

    return beer_field


client = pymongo.MongoClient("mongodb://aawiegel:"+mongo_pass+"@52.53.236.232")

# Get lagers
db = client.beer_styles

lager_ids = []
for style in db.beer_styles.find({'category' : 'Lager'}):
    lager_ids.append(style['style_id'])
    
db = client.beer_reviews

failed_urls = []

for lager_style in lager_ids:
    
    print(lager_style+" is starting.")
    for beer in db.beer_reviews.find({"style_ba_id" : lager_style}):
        
        page_num = beer["ratings"] // 25 + 1
        
        print(str(page_num)+" pages to parse.")
        
        beer_url = base_url + beer['url']
        
        beer_id = beer['beer_ba_id']
        
        try:
            user_agent = {'User-agent': ua.random}
            
            r = requests.get(beer_url, headers = user_agent)
            beer_entry = parse_beer_formongo(r.text)

           

            time.sleep(random.uniform(3, 5))
        except:
            print("Could not retrieve "+beer_url)
            print("Will try again later.")
            time.sleep(random.uniform(25, 35))
            failed_urls.append(beer_url)
            
        if(beer_entry):
            result = db.beer_reviews.update_one({'beer_ba_id' : beer_id}, 
                                                {'$addToSet' : {'reviews' : { '$each' : beer_entry['reviews'] }}})
            result = db.beer_reviews.update_one({'beer_ba_id' : beer_id},
                                                {'$set' : {'description' : beer_entry['description']}})
            result = db.beer_reviews.update_one({'beer_ba_id' : beer_id},
                                                {'$set' : {'beer_stats' : beer_entry['beer_stats']}})
        

            
        
        for i in range(1,page_num+1):
            
            
            
            next_url = beer_url+"?view=beer&sort=&start="+str(i*25)
            
            try:
                user_agent = {'User-agent': ua.random}
                r = requests.get(next_url, headers = user_agent)
                
                beer_entry = parse_beer_formongo(r.text)
                

                time.sleep(random.uniform(3, 5))
            except:
                print("Could not retrieve "+next_url)
                print("Will try again later.")
                time.sleep(random.uniform(25, 35))
                failed_urls.append(next_url)
                
            if(beer_entry):
                result = db.beer_reviews.update_one({'beer_ba_id' : beer_id}, 
                                                    {'$addToSet' : {'reviews' : { '$each' : beer_entry['reviews'] }}}) 
            

            
    print(lager_style+" is finished.")

print(str(len(failed_urls))+' urls failed:')
print(failed_urls)

failed_urls_str = ",".join(failed_urls)

with open("failed_urls_"+str(len(failed_urls))+".txt", "w") as file:
    file.write(failed_urls_str)


