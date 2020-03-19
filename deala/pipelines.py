# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline
import scrapy

class DealaPipeline(object):
    def process_item(self, item, spider):
        return item

class DealaFilesPipeline(FilesPipeline):
    # 重写父类的下面两个方法
    def get_media_requests(self, items, info):
        # 该方法在发送下载请求前调用，此方法作用就是发送下载请求
        
        file_name = items['file_name']
        for file_url in items['file_urls']:
            yield scrapy.Request(file_url, meta={'file_name': file_name}) # 继续传递文件名
        
    def file_path(self, request, response = None, info = None):
        # 该方法实在文件被存储的时候调用，来获取文件的存储路径
        
        file_name = "%s" % (request.meta['file_name'])
        return file_name