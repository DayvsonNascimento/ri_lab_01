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
        with open('./seeds/oantagonista.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        if self.__check_limit_date(response.css('time.entry-date').attrib['datetime']):
            return

        doc_articles = response.css('article')

        for href in doc_articles.css('a.article_link::attr(href)'):
            yield response.follow(href, callback=self.__get_articles_data)

        next_page = "https://www.oantagonista.com/pagina/%d/" % (self.current_page_number)
        self.current_page_number += 1
            
        yield response.follow(next_page, callback=self.parse) 
           
    """
    Get the desired data from the articles.
    """
    def __get_articles_data(self, response):
        yield {
            'title': self.__get_title(response),
            'sub_title': None, #there are no subtitles on 'oantagonista'
            'author': self.__get_author(response), 
            'date': self.__get_date(response),
            'section': self.__get_section(response), 
            'text': self.__get_text(response),
            'url': self.__get_url(response),
        }
   
    """
    Get for the article's title.
    """
    def __get_title(self, response):
        return response.css('h1.entry-title::text').get()
    
    """
    Get for the article's author. Most of the articles on 'oantagonista' don't have 
    a author, in those cases, this informatition will be replaced with None.
    """
    def __get_author(self, response):
        author = response.css('header.entry-header div::text').get().replace('Por ','')
        return author if author.strip() else None
    
    """
    Get the article's date in dd/mm/yyyy hh:mi:ss format.
    """
    def __get_date(self, response):
        return self.__format_date(response.css('time.entry-date::attr(datetime)').get())
    
    """
    Get for the article's section.
    """
    def __get_section(self, response):
        return response.xpath('//span[@class="categoria"]/a/text()').get()
    
    """
    Get for ther article's text.
    """
    def __get_text(self, response):
        return "".join(response.css('div.entry-content p::text').getall())
    
    """
    Get for the article's url.
    """
    def __get_url(self, response):
        return response.request.url
    
    """
    Formats the date from Y-m-d H:M:S to d/m/Y H:M:S.
    """
    def __format_date(self, date):
        return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")

    """
    Checks if the limit date is greater or equals to the article's date.
    """
    def __check_limit_date(self, date):
        date = date.split(" ")[0]
        return self.date_treshold >= date