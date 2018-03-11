# SephoraCrawler
This project is designed to gather information for Skincare Ingredients Look up Website Project. This web crawler download the detail information of all products on [www.sephora.com](www.sephora.com). MongoDB is used to store the data.
## Getting Started

Before running, set up database configuration in `setting.py`(See **Settings** part). 

While keeping database active, go to the sephoraCrawler directory and type 

`scrapy crawl sephoracsp`

The spider runs automatially. 

##Implementation

This project is implemented using Scrapy Library with the help of Selenium Web Driver to deal with lazy loading. The works mainly involves:
+ Item fields
+ Scrapy spider
+ Pipelines
+ Download Middleware
+ Settings
### Items Fields
`items.py` defines what attributes an item (a skincare product) has. All the fields are fetched from 'sephora' web page except `is_safe` and `unsafe_ingredients`, which are assigned in the pipelines. 
### Scrapy Spider

The spider extends from `CrawlSpider` class. It use several rules to filter the link on a web page and parse a product page in a callback function. 

```python
rules = (
    Rule(LinkExtractor(allow='shop', restrict_xpaths='//a[@class="css-6w3omd"]')),
    Rule(NextPageLinkExtractor(), follow=True),
    Rule(LinkExtractor(restrict_xpaths='//div[@class="css-115paux"]/a[@class="css-1tguw7u"]'), callback='parse_item_page')
)
```

+ The first rule search for all sub_categories links in the page.
+ The second finds the next page button and follow the link.
+ The last one follow the link to the product page and call a function to parse the items.

### Pipelines
The purpose of pipelines is to check the ingridents field of each item, whether it contains unsafe ingredients or not. After processing, `is_safe` and `unsafe_ingredients` field is assigned to the items.

### Middlewares

A download middleware is applied to deal with lazy loading of the products links. Selenium web driver is used to control a headless chrome browser in the middleware.

The loading is triggered only when user scroll the page down to a certain location. There are 5 groups of items that send AJAX seperately in different height, so I scroll 1/5 of the height of the page for 5 times, all the data is loaded.

### Settings
In `Settings.py`, we mainly need to set up:
+ Connection to the database
```python
MONGO_SERVER = "localhost" # Server address
MONGO_PORT = 27017 # Port
MONGO_DB = "sephora" # Database name
MONGO_COLL = "sephora" # Collection name
```
+ DOWNLOAD_DELAY & COOKIES_ENABLED(To avoid banned)
```python
DOWNLOAD_DELAY = 5
COOKIES_ENABLED = False
```

+ Activate pipelines
```python
ITEM_PIPELINES = {
    'sephoraCrawler.pipelines.SephoracrawlerPipeline': 300,
}
```
+ Activate middleware

```python
DOWNLOADER_MIDDLEWARES = {
    'sephoraCrawler.middlewares.DownloadMiddleware': 100,
}
```