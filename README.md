# Robocicerone: Beer Recommendations

A prototype system for making recommendations for craft beer based on both content/style and similar user preferences.

## Jupyter notebooks

### BeerAdvocate-MongoScraper.ipynb

Notebook where for testing and prototyping web scraping python scripts to be used with AWS instances. Also uploads previously downloaded scraped HTML to MongoDB. (See [beer regression](https://github.com/aawiegel/Beer-Regression))

### RecommendationSystem.ipynb

Notebook for prototyping recommendation systems and storing them as model pickle files.

## Scraping scripts

### style_scrap.py

Script to scrape basic information about each style to be stored in the beer style collection.

### beer_link_scrape.py

Script to scrape basic information for each beer style for all beers that have 10 or more ratings.

### scraper-lite.py

Script to scrape lager user ratings and reviews and store in mongoDB.

### scraper-ale.py

Script to scrape ale user ratings and reviews and store in mongoDB
