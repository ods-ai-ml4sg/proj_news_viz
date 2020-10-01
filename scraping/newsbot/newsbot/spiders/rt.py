from datetime import datetime

from newsbot.spiders.news import NewsSpider
from newsbot.spiders.news import NewsSpiderConfig
from scrapy import Request
from scrapy import Selector


class RussiaTodaySpider(NewsSpider):
    name = "rt"

    start_urls = ["https://russian.rt.com/sitemap.xml"]

    config = NewsSpiderConfig(
        title_path='//h1[contains(@class, "article__heading")]/text()',
        subtitle_path='_',
        date_path='//meta'
        '[contains(@name, "mediator_published_time")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S",
        text_path='//div[contains(@class, "article__text") or contains(@class, "article__summary")]//text()',
        topics_path='//meta[contains(@name, "mediator_theme")]/@content',
        subtopics_path='//a[@data-trends-link=substring(//div[contains(@class, "layout__control-width")]/script, 50, 24)]//text()',
        authors_path='//meta[contains(@name, "mediator_author")]/@content',
        tags_path='//a[contains(@rel, "tag")]//text()',
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
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%d').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(
                    last_modif_dt.replace(':', ''), '%Y-%m-%d')

                if last_modif_dt.date() >= self.until_date and last_modif_dt.date() <= self.start_date:
                    yield Request(url=link, callback=self.parse_sub_sitemap, priority=1)

    def parse_sub_sitemap(self, response):
        # Parse sub sitemaps
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%dT%H%M%S%z').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(
                    last_modif_dt.replace(':', ''), '%Y-%m-%dT%H%M%S%z')
                if self.start_date >= last_modif_dt.date() >= self.until_date:
                    yield Request(url=link, callback=self.parse_document, priority=100)

        '''def parse_articles_sitemap(self, response):
        # Parse sub sitemaps
        body = response.body
        links = Selector(text=body).xpath('//loc/text()').getall()
        last_modif_dts = Selector(text=body).xpath('//lastmod/text()').getall()
        print('gere', len(links))
        if self.start_date >= datetime.strptime(max(last_modif_dts).replace(':', ''), '%Y-%m-%dT%H%M%S%z').date() >= self.until_date:
            for link, last_modif_dt in zip(links, last_modif_dts):
                # Convert last_modif_dt to datetime
                last_modif_dt = datetime.strptime(last_modif_dt.replace(':', ''), '%Y-%m-%dT%H%M%S%z')

                if last_modif_dt.date() >= self.until_date and last_modif_dt.date() <= self.start_date:
                    if link.endswith('.shtml') and not link.endswith('index.shtml'):
                        yield Request(url=link, callback=self.parse_document, priority=1000)'''

    def fix_date(self, raw_date):
        """Fix date for regular and authors articles
        """
        months_ru = [
            "января",
            "февраля",
            "марта",
            "апреля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сентября",
            "октября",
            "ноября",
            "декабря",
        ]

        if len(raw_date[0]) == 25:
            raw_date[0] = raw_date[0][:19]
            return raw_date
        else:
            for i, month in enumerate(months_ru):
                raw_date[0] = raw_date[0].replace(month, str(i + 1))
            return datetime.strptime(raw_date[0],
                                     "%d %m %Y,").strftime("%Y-%m-%dT%H:%M:%S")

    def cut_instagram(self, raw_text):
        """Cut instagram quote
        """
        clear_text = []
        i = 0
        while i < len(raw_text):
            if " Посмотреть эту публикацию в Instagram" == raw_text[i]:

                while "PDT" not in raw_text[i]:
                    i += 1
                i += 1
            else:
                clear_text.append(raw_text[i])
                i += 1
        return clear_text

    def parse_document(self, response):
        """Final parsing method.
        Parse each article."""
        for item in super().parse_document(response):
            # Try to drop timezone postfix.
            if 'tags' in item:
                item['tags'] = [tag.strip()
                                for tag in item['tags'] if tag.strip()]
            if 'subtitle' in item:
                item['subtitle'] = [s.strip()
                                    for s in item['subtitle'] if s.strip()]
            try:
                item['date'] = self._fix_syntax(item['date'], -6)
            except KeyError:
                print('Error. No date value.')
            else:
                yield item
