# -*- coding: utf-8 -*-
import scrapy
import json
import datetime

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class OantagonistaSpider(scrapy.Spider):
    name = 'oantagonista'
    allowed_domains = ['oantagonista.com']
    start_urls = []
    current_page_number = 1
    date_treshold = "2018-01-01"

    def __init__(self, *a, **kw):
        super(OantagonistaSpider, self).__init__(*a, **kw)
        with open('../seeds/oantagonista.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        if self.checkDateLimit(response.css('time.entry-date').attrib['datetime']):
            return
        
        articles = response.css('article')

        for href in articles.css('a.article_link::attr(href)'):
            yield response.follow(href, callback=self.__get_articles_data)
        
        next_page = "https://www.oantagonista.com/pagina/%d/" % (self.current_page_number)
        self.current_page_number += 1
            
        yield response.follow(next_page, callback=self.parse) 
           
    def __get_articles_data(self, response):
        articleAuthor = response.css('header.entry-header div::text').get().replace('Por ','')
        
        yield {
            'title': response.css('h1.entry-title::text').get(),
            'sub_title': None,
            'author': articleAuthor if articleAuthor.strip() else None, 
            'date': self.__format_date(response.css('time.entry-date::attr(datetime)').get()),
            'section': response.xpath('//span[@class="categoria"]/a/text()').get(), 
            'text': "".join(response.css('div.entry-content p::text').getall()),
            'url': response.request.url,
        }

    def __format_date(self, date):
        return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")

    def __check_limit_date(self, date):
        date = date.split(" ")[0]
        
        return self.date_treshold >= date