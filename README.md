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
While keeping database active, go to the sephoraCrawler directory and type 

`scrapy crawl sephorasp`

The spider runs automatially. 

# Implementation
This project is implemented using Scrapy Library with the help of Selenium Web driver to deal with lazy loading. The works mainly involves:
+ Items fields
+ Scrapy spider
+ Pipelines
+ Setting
### Items Fields
`items.py` defines what attributes an item (a skincare product) has. All the fields are fetched from 'sephora' web page except `is_safe` and `unsafe_ingredients` which are assigned in the pipelines. 
``` python
class SephoracrawlerItem(scrapy.Item):

    ingredients = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    url = scrapy.Field()
    brand = scrapy.Field()
    image = scrapy.Field()
    unsafe_ingredients = scrapy.Field()
    is_safe = scrapy.Field()
```
### Scrapy Spider
There are three parse levels in the spider. The work flow looks like this: 

`Skincare category(parse_first_level) => Skincare sub_category(parse_second_level) => Product(parse_item_page)`

#### Level 1: Skincare Category
In this step, just simply loop through all sub-category links except 'skin-care-tools' which has no ingredients information, and go to next level.
```python
    def parse_first_level(self, response):
        # Find the title of each category
        loop_urls = response.xpath('//div[@class="css-hcszpw"]//a[@class="css-6w3omd"]/@href').extract()
        # Loop through each category
        for url in loop_urls[3:]:
            if url == '/shop/skin-care-tools':
                continue
            # Go to the first page, prepare for parse_second_level function
            full_url = 'https://www.sephora.com' + url + '?currentPage=1'
            yield scrapy.Request(url=full_url, callback=self.parse_second_level)
```
#### Level 2: Sub-Category
Under each sub-category, products are displayed in a `div` container in HTML. Each page shows 60 items in total, and with lazy loading 12 items a time. Selenium web driver is used to scroll 5 times from top of the page to the end so that all 5 lazy loading components can be downloaded.
```python
    def parse_second_level(self, response):
        # Web driver gets involved, scroll to the end to the page to scan the lazy load information
        self.driver.get(response.url)
        self.scroll_till_end()
        # Extract products element and loop through each product
        products_urls = self.driver.find_elements_by_xpath('//div[@class="css-115paux"]/a[@class="css-1tguw7u"]')
        for url in products_urls:
            # Extract product's url then go to next level
            full_url = url.get_attribute('href')
            yield scrapy.Request(url=full_url, callback=self.parse_item_page)

        # if 'next page' button is active, then go to next page. If not, print 'Reach the End of One Category'
        try:
            self.driver.find_element_by_xpath('//button[@class="css-1mf8x14"]/*[name()="svg" and @class="css-6952th"]')
            next_page_url = response.url.split('?')[0] + '?currentPage=' + str(int(response.url.split('=')[1]) + 1)
            yield scrapy.Request(url=next_page_url, callback=self.parse_second_level)
        except NoSuchElementException:
            print("===========================Reach the End of one category===========================")
```
#### Level 3: Item Page
Use Xpath locator to find data for each field and yeild the item.
```python
    def parse_item_page(self, response):
        ingredients = 'None'
        if len(response.xpath('//div[@class="css-8tl366"]')) >= 2:
            ingredients = response.xpath('//div[@class="css-8tl366"]')[-1].xpath('./text()').extract()
        name = response.xpath('//span[@class="css-1g2jq23"]/text()').extract_first()
        price = response.xpath('//div[@class="css-18suhml"]/text()').extract_first()
        brand = response.xpath('//a[@class="css-zvvfrv"]/span[@class="css-cjz2sh"]/text()').extract_first()
        image = response.xpath('//svg[@class="css-8a9gku"]/image')[0].extract()
        image_url = 'www.sephora.com' + re.search('xlink:href="(.*)" onload', image).group(1)

        # In case some products has no sub-category
        if len(response.xpath('//div[@class="css-12alag6"]/a[@class="css-u2mtre"]/text()')) > 1:
            category = response.xpath('//div[@class="css-12alag6"]/a[@class="css-u2mtre"]/text()')[1].extract()
            sub_category = response.xpath('//div[@class="css-1lb5emk"]/a[@class="css-1i9riiu"]/text()').extract_first()
        else:
            category = response.xpath('//div[@class="css-1lb5emk"]/a[@class="css-1i9riiu"]/text()').extract()
            sub_category = "None"
        ...
```
### Pipelines
The purpose of pipelines is to check the ingridents field of each item, whether it contains unsafe ingredients or not. After processing, `is_safe` and `unsafe_ingredients` field is assigned to the items.
```python
    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                raise DropItem("Missing {0}!".format(data))
        if valid:
            unsafe_ingredients = self.check_safety(item['ingredients'])
            if unsafe_ingredients:
                item['unsafe_ingredients'] = unsafe_ingredients
                item['is_safe'] = False
            self.collection.insert(dict(item))
            log.msg("Product added to MongoDB database!",
                    level=log.DEBUG, spider=spider)
        return item

    def check_safety(self, ingredients):
        if not ingredients:
            return []
        contain_unsafe_ingredients = []
        for unsafe_ingredient in self.ten_skincare_ingredients_to_avoid:
            for tuples in ingredients:
                if unsafe_ingredient in tuples.lower():
                    contain_unsafe_ingredients.append(unsafe_ingredient)
        return contain_unsafe_ingredients
```
### Settings
In `Settings.py`, we mainly need to set up:
+ Connection to the database
```python
MONGO_SERVER = "localhost"
MONGO_PORT = 27017
MONGO_DB = "sephora"
MONGO_COLL = "sephora"
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

