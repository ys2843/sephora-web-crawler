import scrapy
import re
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
import time


class SephoraSpider(scrapy.Spider):
    # The name of the spider
    name = "sephorasp"

    def __init__(self, **kwargs):
        super(SephoraSpider, self, **kwargs)
        # Initialize the web driver,
        self.driver = webdriver.Chrome('./chromedriver')

    def start_requests(self):
        # Start page is 'https://www.sephora.com/shop/skincare'
        url = 'https://www.sephora.com/shop/skincare'
        yield scrapy.Request(url=url, callback=self.parse_first_level)
        # url = 'https://www.sephora.com/shop/inner-beauty-products?currentPage=1'
        # yield scrapy.Request(url=url, callback=self.parse_second_level)

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
            # print(full_url)

        # if 'next page' button is active, then go to next page. If not, print 'Reach the End of One Category'
        try:
            self.driver.find_element_by_xpath('//button[@class="css-1mf8x14"]/*[name()="svg" and @class="css-6952th"]')
            next_page_url = response.url.split('?')[0] + '?currentPage=' + str(int(response.url.split('=')[1]) + 1)
            yield scrapy.Request(url=next_page_url, callback=self.parse_second_level)
        except NoSuchElementException:
            print("===============================Reach the End of one category================================")

    def parse_item_page(self, response):
        # In case some products have no ingredients
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

        url = response.url
        yield {'name': name,
               'ingredients': ingredients,
               'price': price,
               'category': category,
               'sub_category': sub_category,
               'url': url,
               'brand': brand,
               'image': image_url,
               'unsafe_ingredients': 'None',
               'is_safe': True}

    def scroll_till_end(self):
        # scroll 5 times to the end to load all 5 groups of products
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/5);")
        time.sleep(50.0 / 1000.0)
        self.driver.execute_script("window.scrollTo(document.body.scrollHeight/5, document.body.scrollHeight*2/5);")
        time.sleep(50.0 / 1000.0)
        self.driver.execute_script("window.scrollTo(document.body.scrollHeight*2/5, document.body.scrollHeight*3/5);")
        time.sleep(50.0 / 1000.0)
        self.driver.execute_script("window.scrollTo(document.body.scrollHeight*3/5, document.body.scrollHeight*4/5);")
        time.sleep(50.0 / 1000.0)
        self.driver.execute_script("window.scrollTo(document.body.scrollHeight*4/5, document.body.scrollHeight);")
        time.sleep(50.0 / 1000.0)
