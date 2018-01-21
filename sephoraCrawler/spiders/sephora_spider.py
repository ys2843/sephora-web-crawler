import json

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
# from scrapy.utils.response import get_base_url

from sephoraCrawler.items import SephoracrawlerItem
import urlparse


class SephoraSpider(CrawlSpider):
    name = "sephora"
    custom_settings = {"IMAGES_STORE": '../images/sephora'}

    allowed_domains = ["sephora.com"]
    start_urls = [
        'http://www.sephora.com/search/search.jsp?keyword=skincare&mode=all'
    ]

    rules = (
        Rule(LinkExtractor(
            # restrict_xpaths='//ul/li/a[contains(@href, "page")])'),
            allow=(r'.*Npp.*', )),
            callback='parse_items',
            follow=True
        ),
        # Rule(LinkExtractor(
        #     restrict_xpaths='//ul[@class="refineItemOptions"][0]/li/a'),
        #     # allow=(),
        #     callback='parse_category',
        #     follow=True
        # ),
    )

    def parse_start_url(self, response):
        print("entered")
        cat_json = response.xpath(
            '//script[@id="searchResult"]/text()').extract_first()
        f = open('sample_json.json', 'w+')
        f.write(cat_json.encode("utf-8"))
        f.close()
        all_url_data = json.loads(cat_json)
        all_links = []
        category = all_url_data['categories']['name']
        for each_sub_category in all_url_data['categories']['sub_categories']:
            link = each_sub_category['seo_path'].replace("/", "")
            print("mylink", link)
            full_url = "http://www.sephora.com/rest/products/"\
                       "?pageSize=-1&   &"\
                       "categoryName={0}&include_categories=true"\
                       "&include_refinements=true".format(link)
            print("url", full_url)
            my_request = scrapy.Request(
                full_url,
                self.parse_items)
            my_request.meta['category'] = {
                "sub_category": each_sub_category['name'],
                "category": category,
                "to_replace": "currentPage=1"
            }
            print ("meta", my_request.meta)
            all_links.append(my_request)
        print(all_links)
        return all_links

    def parse_items(self, response):
        print("---------------------------------------------")
        category = response.meta['category']['category']
        sub_category = response.meta['category']['sub_category']
        print(category, sub_category)
        website = "sephora.com"
        data = json.loads(response.body)
        print(data.keys())
        if "products" not in data:
            return
        for each_item in data["products"]:
            name = each_item["display_name"]
            price = each_item['derived_sku']["list_price"]
            image_urls = urlparse.urljoin(response.url, each_item['hero_image'])
            image_urls = [image_urls]
            brand = each_item["brand_name"]
            affiliate_link = urlparse.urljoin(response.url, each_item["product_url"])
            item = SephoracrawlerItem(
                name=name.strip(),
                price=price.strip(),
                image_urls=image_urls,
                brand=brand.strip(),
                affiliate_link=affiliate_link,
                category=category,
                sub_category=sub_category,
                website=website
            )
            yield item

        to_replace = response.meta['to_replace']
        next_number = int(to_replace.replace("currentPage=", "")) + 1
        next_link = response.url.replace(
            to_replace, "currentPage=" + str(next_number))
        my_request = scrapy.Request(
            next_link,
            self.parse_items)
        my_request.meta['category'] = {
            "sub_category": sub_category,
            "category": category,
            "to_replace": "currentPage=" + str(next_number)
        }
        yield my_request
