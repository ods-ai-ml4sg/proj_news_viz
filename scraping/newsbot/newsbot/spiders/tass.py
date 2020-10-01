from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy import Request, Selector
from datetime import datetime
import re


class RussiaTassSpider(NewsSpider):
    name = "tass"
    start_urls = ["https://tass.ru/sitemap.xml"]
    config = NewsSpiderConfig(
        title_path='//h1[contains(@class, "news-header__title") or contains(@class, "explainer__title") or contains(@class, "article__title")]//text()',
        subtitle_path='//div[contains(@class, "news-header__lead")]//text()',
        date_path='//dateformat[@mode="abs"]/@time',
        date_format='%Y-%m-%dT%H%M%S%z',
        text_path='//div[contains(@class, "text-block")]/p//text()',
        topics_path='//title/text()',
        tags_path='//a[contains(@class, "tags__item")]//text()',
        subtopics_path='_',
        authors_path='_',
        reposts_fb_path='_',
        reposts_vk_path='_',
        reposts_ok_path='_',
        reposts_twi_path='_',
        reposts_lj_path='_',
        reposts_tg_path='_',
        likes_path='_',
        views_path='_',
        comm_count_path='_'
    )

    def parse(self, response):
        # Parse main sitemap
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        print(last_modif_dts[0], last_modif_dts[-1])
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%dT%H%M%S%z').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(
                    last_modif_dt.replace(':', ''), '%Y-%m-%dT%H%M%S%z')

                if last_modif_dt.date() >= self.until_date and last_modif_dt.date() <= self.start_date:
                    yield Request(url=link, callback=self.parse_sub_sitemap, priority=1)

    def parse_sub_sitemap(self, response):
        # Parse sub sitemaps
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%dT%H%M%S%z').date() >= self.until_date:
            print(max(last_modif_dts))
            print(len(links))
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(
                    last_modif_dt.replace(':', ''), '%Y-%m-%dT%H%M%S%z')
                if self.start_date >= last_modif_dt.date() >= self.until_date:
                    yield Request(url=link, callback=self.parse_document, priority=100, meta={'date': last_modif_dt.strftime('%Y-%m-%dT%H%M%S%z')})

    def parse_document(self, response):
        print('here')
        for item in super().parse_document(response):
            print('one more')
            item['date'] = [response.meta.get('date')]
            if 'text' in item:
                if re.search('/.+/. ([\d\D]+)', item['text'][0]):
                    item['text'][0] = re.search(
                        '/.+/. ([\d\D]+)', item['text'][0]).group(1)
            if 'topics' in item:
                item['topics'] = [re.search(r'-([\s\w]+)-', topic).group(1).strip()
                                  for topic in item['topics'] if re.search(r'-([\s\w]+)-', topic)]

            yield item
