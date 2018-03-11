from scrapy.linkextractors import LinkExtractor
from scrapy.link import Link


class NextPageLinkExtractor(LinkExtractor):
    def _extract_links(self, selector, response_url, response_encoding, base_url=None):
        result = []
        if 'currentPage' not in response_url:
            response_url = response_url + "?currentPage=1"
        if selector.xpath('//button[@class="css-1mf8x14"]/*[name()="svg" and @class="css-6952th"]'):
            result.append(
                Link(response_url.split('?')[0] + '?currentPage=' + str(int(response_url.split('=')[1]) + 1), u'',
                     nofollow=False))
        return result
