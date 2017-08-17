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

def download_parse_ba(style_file, url):
    """
    sytle_file: file to be written (including subdirectory)
    url: url to read from
    Reads a url from BeerAdvocate.com and dumps
    its main content into a local HTML file
    """
    
    user_agent = {'User-agent': ua.random}
    
    r = requests.get(url, headers = user_agent)
    soup = BeautifulSoup(r.text, "lxml")
    main_content = soup.find(id='ba-content')
    
    with open(style_file, 'w') as file:
        file.write(str(main_content))
    
    time.sleep(random.uniform(2, 4))
    
    return







def create_style_entry(category, style, url):
    style = {"style_name": style,
             "category": category,
             "style_id": url.split('/')[-2],
             "url" : url}
    return style




with open("mongo_pass.txt", "r") as file:
    mongo_pass = file.read().split("\n")[0]
    
base_url = "https://www.beeradvocate.com"


ua = UserAgent()

styles = os.path.join(os.path.curdir, "data", "styles.html")

## get first styles page

if not os.path.exists(styles):
    os.makedirs("data")
    r = requests.get(start_url)
    page = r.text
    with open(styles, 'w') as file:
        file.write(page)
else:
    with open(styles, 'r') as file:
        page = file.read()
        
soup = BeautifulSoup(page,"lxml")

# Type = Ale, Lager, or Hybrid
type_tables = soup.find('table').findAll('table')


# get style links
style_link_dict = dict()
for type_table in type_tables:
    beer_type = type_table.find('span').text.split(" ")[0]
    style_link_dict[beer_type] = dict()
    for style in type_table.findAll('a'):
        style_name = re.sub("/", "", style_name)
        style_name = re.sub("&", "And", style_name)
        style_name = style_name.split("(")[0]
        style_name = re.sub("è", "e", style_name)
        style_name = re.sub("ö", "o", style_name)
        style_name = re.sub("ä", "a", style_name)
        style_link_dict[beer_type][style_name] = base_url+style['href']



print("Adding entries to mongodb")

client = pymongo.MongoClient("mongodb://aawiegel:"+mongo_pass+"@52.53.236.232/beer_styles")

db.beer_styles.createIndex('style_id', unique=True)

for category, style_links in style_link_dict.items():        
    for style, url in style_links.items():
        style_entry = create_style_entry(category, style, url)
        style_id = style_entry['style_id']
        if(db.beer_styles.find({'style_id': style_id}).count() < 1):
            db.beer_styles.insert_one(style_entry)
        else:
            already_added.append(style_id)

print(str(len(already_added))+" styles were already added.")



