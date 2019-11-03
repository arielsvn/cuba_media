# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy.spiders import SitemapSpider

class CubadebateSpider(SitemapSpider):
    name = 'cubadebate'
    allowed_domains = ['www.cubadebate.cu']
    sitemap_urls = ['http://www.cubadebate.cu/sitemap.xml']
    sitemap_follow = ['/sitemap-pt-post-2016-06']

    def parse(self, response):
        if 'http://www.cubadebate.cu' not in response.url:
            # there're other sites that we want to ignore
            # razonesdecuba.cubadebate.cu
            # mesaredonda.cubadebate.cu
            return

        def get_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'url': response.url,
            'headline': get_css('h2.title::text'),
            'breadcrumps': response.css('.breadcrumbs > [rel="category tag"]::text').getall(),
            'author': response.xpath('//div[@id="taxonomies"]//strong[contains(text(), "Por")]/..//a/text()').getall(),
            'published_in': response.xpath('//div[@id="taxonomies"]//strong[contains(text(), "Publicado en")]/..//a/text()').getall(),
            'keywords': response.xpath('//div[@id="taxonomies"]//strong[contains(text(), "En este")]/..//a/text()').getall(),
            'date': get_css('.meta time::attr(datetime)'),
            'media': get_css('[name="twitter:image"]::attr(content)'),
            'comment_count': get_css('.post > .meta > .comment_count > a:not(.no_comment)::text'),
            'body': get_cubadebate_post_content(get_css('.entry .note_content')),
        }


def get_cubadebate_post_content(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')

    # remove image captions
    for div in soup.find_all("div", {'class':'wp-caption'}):
        div.decompose()

    # remove more posts
    moreposts = soup.find('div', id="moreposts")
    if moreposts: moreposts.decompose()

    return soup.get_text().strip()