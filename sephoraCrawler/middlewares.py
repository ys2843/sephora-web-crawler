from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from scrapy.http import HtmlResponse
from selenium.webdriver.remote.remote_connection import LOGGER
import logging


def scroll_till_end(driver):
    # scroll 5 times to the end to load all 5 groups of products
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/5);")
    time.sleep(50.0 / 1000.0)
    driver.execute_script("window.scrollTo(document.body.scrollHeight/5, document.body.scrollHeight*2/5);")
    time.sleep(50.0 / 1000.0)
    driver.execute_script("window.scrollTo(document.body.scrollHeight*2/5, document.body.scrollHeight*3/5);")
    time.sleep(50.0 / 1000.0)
    driver.execute_script("window.scrollTo(document.body.scrollHeight*3/5, document.body.scrollHeight*4/5);")
    time.sleep(50.0 / 1000.0)
    driver.execute_script("window.scrollTo(document.body.scrollHeight*4/5, document.body.scrollHeight);")
    time.sleep(50.0 / 1000.0)


class DownloadMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):
        if '/shop/' in request.url:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome('./chromedriver', chrome_options=options)
            driver.get(request.url)
            LOGGER.setLevel(logging.WARNING)
            scroll_till_end(driver)
            body = driver.page_source.encode('utf-8')
            driver.quit()
            return HtmlResponse(request.url, encoding='utf-8', body=body, request=request)
        return None
