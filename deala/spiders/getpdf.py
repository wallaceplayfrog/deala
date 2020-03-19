# -*- coding: utf-8 -*-
import scrapy
from deala.items import DealaItem
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # 使用无头浏览器
import re

# 无头浏览器设置
chrome_driver = r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

class GetpdfSpider(scrapy.Spider):
    name = 'getpdf'
    allowed_domains = ['www.cfae.cn']
    start_urls = ['http://www.cfae.cn/xxpl/dcm/fhpl/fxwj.html']

    def __init__(self):
        self.browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)  # 实例化一个浏览器对象
        super().__init__()

    def start_requests(self):
        url = "https://www.cfae.cn/xxpl/dcm/fhpl/fxwj.html"
        response = scrapy.Request(url, callback=self.parse_index)
        yield response
    
    # 获取每个发行文件的链接
    def parse_index(self, response):
        page_list = response.xpath("//div[@class='dis_n']/a/@href").extract()
        # print('============\n',page_list)
        for each in page_list:
            page_url = urllib.parse.urljoin(response.url, each[1:])
            #print('============\n',page_url)
            new_response = scrapy.Request(page_url, callback=self.parse_pdf)
            yield new_response
    
    def parse_pdf(self, response):
        item = DealaItem()
        
        urls = response.xpath("//span[@id='filesId']/a/@href").extract()
        names = response.xpath("//span[@id='filesId']/a/text()").extract()
        # print('============\n',urls, '\n', file_names)
        for url, name in zip(urls, names):
            if re.match('.*?募集说明书(\\(.*?\\))?.pdf', name):
                file_urls = urllib.parse.urljoin(response.url, url)
                file_name = name
                item["file_urls"] = [file_urls]
                item["file_name"] = file_name
                yield item

    # 爬取结束后关闭浏览器
    def close(self, spider):
        self.browser.quit()
