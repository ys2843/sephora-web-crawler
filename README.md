# SephoraCrawler
This project is designed to gather information for Skincare Ingredients Look up Website Project. This web crawler can download the detail information of all products, about 2289 items, under 'skincare' category on [www.sephora.com](www.sephora.com). The data is sent and stored into MongoDB.
# Getting Started
Before running, please set up database configuration in `setting.py`. 

```
MONGO_SERVER = "localhost" 
MONGO_PORT = 27017 
MONGO_DB = "sephora" 
MONGO_COLL = "sephora" 
```

Then to run the crawler, go to directory in command line and type 

`scrapy crawl sephorasp`

The spider runs automatially. 
