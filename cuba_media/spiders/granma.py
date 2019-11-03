# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

class GranmaSpider(scrapy.Spider):
    name = 'granma'
    allowed_domains = ['granma.cu']
    start_urls = ['http://www.granma.cu/archivo']

    def parse(self, response):
        # follow links to article pages
        for href in response.css('article.g-searchpage-story > h2 > a::attr(href)'):
            yield response.follow(href, self.parse_article)

        # follow pagination links
        for href in response.css('ul.pagination > li > a::attr(href)'):
            yield response.follow(href, self.parse)

    def parse_article(self, response):
        def get_css(query):
            return response.css(query).get(default='').strip()

        def get_itemprop(prop):
            return get_css('[itemprop="%s"]::text' % prop)

        def strip_html(query):
            html_text = get_css(query)
            soup = BeautifulSoup(html_text, 'html.parser')
            return soup.get_text()

        yield {
            'url': response.url,
            'headline': get_css('[itemprop="headline"]::text'),
            'description': get_itemprop('description'),
            'author': response.css('[itemprop="author creator"] [itemprop="name"]::text')\
                              .getall(),
            'date': get_css('.dateline::attr(datetime)'),
            'media': get_css('[itemprop="associatedMedia"] [itemprop="url"]::attr(src)'),
            'media_copyright': get_css('[itemprop="associatedMedia"] [itemprop="description"] [itemprop="copyrightHolder"]::text'),
            'body': strip_html('[itemprop="articleBody"]')
        }
