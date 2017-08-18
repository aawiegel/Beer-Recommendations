#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 15:18:56 2017

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

def find_style_num(page):
    """
    style_file: html file in style list
    Returns the total number of beers in the style category
    """
    
    soup = BeautifulSoup(page,"lxml")
        
    # Find number of beers for the style

    beer_num_tag = soup.find('table').find('span').find('b').text
    
    # Find 'word' directly to the left of a parentheses
    criteria = re.compile('\w+\)')

    found = re.search(criteria, beer_num_tag)
    
    return int(found.group(0).split(')')[0])
    
def parse_beer_style(style_page, style_id):
    """
    style_url: html file in style list
    beer_links: reference to dictionary of beers to update
    Updates dictionary with each beer, its associated data,
    and a link to its review page
    Returns True if a beer on the page had less than 10 ratings
    Returns False otherwise
    """
    
    beer_entries = []
    
    soup = BeautifulSoup(style_page, "lxml")
        
    beer_rows = soup.find("table").findAll("tr")
    
    # Flag to stop reading entries when number of ratings is less than 10
    stop_flag = False
    
    for beer_row in beer_rows[3:len(beer_rows)-1]:
        beer_entry = dict()

        
        table_entries = beer_row.findAll("td")
        namelink = table_entries[0].find("a")
    
        beer_link = namelink['href']
        beer_name = namelink.text
        
        brewery = table_entries[1].find("a").text

        
        abv = table_entries[2].find("span").text
        
        score = table_entries[3].find("b").text
        
        ratings = int(re.sub(",", "", table_entries[4].find("b").text))
        
        if ratings < 10:
            stop_flag = True
        
        split_link = beer_link.split('/')
        
        beer_entry['brewery'] = brewery
        beer_entry['beer'] = beer_name
        beer_entry['url'] = beer_link
        beer_entry['brewery_ba_id'] = split_link[-3]
        beer_entry['style_ba_id'] = style_id
        beer_entry['beer_ba_id'] = split_link[-2]
        beer_entry['abv'] = abv
        beer_entry['avg_score'] = score
        beer_entry['ratings'] = ratings
    
        beer_entries.append(beer_entry)
    
    return beer_entries, stop_flag

def parse_beer_formongo(beer, url):
    """
    Takes a key value pair from a dictionary of beers and links
    Returns a dictionary of beer information to update mongodb with
    """
    beer_dir = os.path.join(os.path.curdir, "data", "beers")
       
    beer_path = os.path.join(beer_dir, beer+".html")
    beer_id = url.split("/")[-2]

    with open(beer_path, 'r') as file:
        page = file.read()

    soup = BeautifulSoup(page, "lxml")

    desc = str(soup.find('div', {'style':'float:right; width:70%;'}))

    beer_stats = str(soup.find(id="item_stats"))

    rating_tags = soup.findAll(id="rating_fullview_container")
    reviews = []
    for rating_tag in rating_tags:
        ba_user_id = rating_tag['ba-user']
        reviews.append({ba_user_id : str(rating_tag)})


    beer_field = {'description' : desc, 'beer_stats' : beer_stats, 'reviews' : reviews}

    return beer_id, beer_field

with open("mongo_pass.txt", "r") as file:
    mongo_pass = file.read().split("\n")[0]
    
base_url = "https://www.beeradvocate.com"
start_url = base_url+"/beer/style/"


#
client = pymongo.MongoClient("mongodb://aawiegel:"+mongo_pass+"@52.53.236.232/beer_styles")

db = client.beer_styles

style_ids = []
for entry in db.beer_styles.find():
    style_ids.append(entry['style_id'])
    
client.close()

client = pymongo.MongoClient("mongodb://aawiegel:"+mongo_pass+"@52.53.236.232/beer_reviews")

db = client.beer_reviews

## Get all reviews based on first page

already_added = []
        
for style_id in style_ids:
    
    style_url = start_url+style_id+"/"
    
    if(db.beer_reviews.find({'style_id' : style_id}).count() < 1):
        print(style_id+" is already added.")
        continue
    
    user_agent = {'User-agent': ua.random}
    
    r = requests.get(style_url, headers = user_agent)
    
    first_style_page = r.text
    
    beer_count = find_style_num(first_style_page)
    
    page_num = beer_count // 50
    
    print(page_num)
    
    beer_list, _ = parse_beer_style(first_style_page, style_id)
    
    for beer in beer_list:
        if (db.beer_reviews.find({'beer_ba_id' : beer['beer_ba_id']}).count() < 1):
            db.beer_reviews.insert_one(beer)
        else:
            already_added.append(beer['beer_ba_id'])
    time.sleep(random.uniform(3, 5))
    # Get all pages that link to reviews of beer
    
    for i in range(1,page_num+1):
        
        user_agent = {'User-agent': ua.random}
        
        url_next = url + "?sort=revsD&start="+str(i*50)
        
        r = requests.get(url_next, headers = user_agent)
        
        beer_list, stop_flag = parse_beer_style(r.text, style_id)
        
        for beer in beer_list:
            if (db.beer_reviews.find({'beer_ba_id' : beer['beer_ba_id']}).count() < 1):
                db.beer_reviews.insert_one(beer)
            else:
                already_added.append(beer['beer_ba_id'])
        
        if(stop_flag):
            time.sleep(random.uniform(15, 20))
            break
        
        time.sleep(random.uniform(3, 5))
        
        
    print("Completed "+style_id)
    
print(str(len(already_added))+" beers already added.")



