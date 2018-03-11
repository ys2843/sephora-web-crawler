from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from next_page_extractor import NextPageLinkExtractor


class SephoraCrawlSpider(CrawlSpider):
    name = 'sephoracsp'
    start_urls = [
        'https://www.sephora.com/shop/body-moisturizers',
        # 'https://www.sephora.com/shop/makeup-cosmetics',
        # "https://www.sephora.com/shop/skincare",
        # "https://www.sephora.com/shop/fragrance",
        # "https://www.sephora.com/shop/hair-products",
        # "https://www.sephora.com/shop/men",
        # "https://www.sephora.com/shop/bath-body"
    ]
    rules = (
        Rule(LinkExtractor(allow='shop', restrict_xpaths='//a[@class="css-6w3omd"]')),
        Rule(LinkExtractor(restrict_xpaths='//div[@class="css-115paux"]/a[@class="css-1tguw7u"]'),
             callback='parse_item_page'),
        Rule(NextPageLinkExtractor(), follow=True),

    )

    def parse_item_page(self, response):
        print("=======parse_item_page worked!============")
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
