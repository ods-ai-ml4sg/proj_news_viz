import re
from datetime import datetime
from datetime import timedelta

import lxml.html
import scrapy
from newsbot.spiders.news import NewsSpider
from newsbot.spiders.news import NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor


class RiaSpider(NewsSpider):
    name = "ria"
    dt = datetime.now()
    link_tmpl = "https://www.ria.ru/{}/"
    start_urls = [link_tmpl.format(str(dt.year) + str(dt.month) + str(dt.day))]
    config = NewsSpiderConfig(
        title_path='//h1[contains(@class, "article__title")]/text()',
        subtitle_path="_",
        date_path='//div[contains(@class, "endless__item")]/@data-published',
        date_format="%Y-%m-%dT%H:%MZ",
        text_path='//div[contains(@class, "article__block") and @data-type = "text"]//text()',
        topics_path='//div[contains(@class, "endless__item")]/@data-analytics-rubric',
        subtopics_path="_",
        authors_path="_",
        tags_path='//div[contains(@class, "endless__item")]/@data-keywords',
        reposts_fb_path="_",
        reposts_vk_path="_",
        reposts_ok_path="_",
        reposts_twi_path="_",
        reposts_lj_path="_",
        reposts_tg_path="_",
        likes_path='//span[contains(@class,"m-value")]/text()',
        views_path='//span[contains(@class,"statistic__item m-views")]/text()',
        comm_count_path="_",
    )
    news_le = LinkExtractor(restrict_css="div.lenta__item")

    def parse(self, response):
        news_le = LinkExtractor(restrict_css="div.lenta__item")

        article_links = news_le.extract_links(response)

        for link in article_links:
            yield scrapy.Request(
                url=link.url, callback=self.parse_document, priority=100
            )

        adding = response.xpath('//div[contains(@class, "list-more")]/@data-url').get()
        if adding:
            new_url = "https://www.ria.ru" + adding
            if self.start_date >= self.dt.date() >= self.until_date:
                yield scrapy.Request(url=new_url, callback=self.parse_next)

        self.dt -= timedelta(days=1)

        if self.start_date >= self.dt.date() >= self.until_date:
            new_url = self.link_tmpl.format(
                str(self.dt.year) + str(self.dt.month) + str(self.dt.day)
            )
            yield scrapy.Request(url=new_url, callback=self.parse)

    def parse_next(self, response):

        news_le = LinkExtractor(restrict_css="div.list-item__content")

        article_links = news_le.extract_links(response)
        for link in article_links:
            yield scrapy.Request(
                url=link.url, callback=self.parse_document, priority=100
            )

        adding = response.xpath(
            '//div[contains(@class, "list-items-loaded")]/@data-next-url'
        ).get()

        if adding:
            new_url = "https://www.ria.ru" + adding
            yield scrapy.Request(
                url=new_url,
                callback=self.parse_next,
            )

    def parse_document(self, response):
        for res in super().parse_document(response):

            authors = re.search(r"- РИА Новости, ([\w\s,]+)", res["text"][0])
            if authors:
                res["authors"] = authors.group(1).split(", ")
            res["text"] = res["text"][1:]

            yield res
