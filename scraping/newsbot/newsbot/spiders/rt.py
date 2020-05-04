from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy import Request, Selector

from datetime import datetime


class RussiaTodaySpider(NewsSpider):
    name = "rt"

    start_urls = ["https://russian.rt.com/sitemap.xml"]

    config = NewsSpiderConfig(
        title_path="//h1/text()",
        date_path='//meta[contains(@name, "mediator_published_time")]/@content'
        ' | //span[@class="main-page-heading__date"]/text()',
        date_format="%Y-%m-%dT%H:%M:%S",
        text_path='//div[contains(@class, "article__text")]'
        '//*[not(contains(@class, "read-more")) and '
        'not(contains(@class, "article__cover"))]//text()'
        ' | //meta[contains(@name, "description")]/@content'
        ' | //div[@class="page-content"]/p/text()'
        ' | //div[@class="page-content"]/blockquote/p/text()'
        ' | //div[@class="page-content"]/p/a/text()'
        ' | //div[@class="page-content"]/h2/strong/text()',
        topics_path='//meta[contains(@name, "mediator_theme")]/@content'
        ' | //h2[@class="main-page-heading__tag"]/text()',
        authors_path='//meta[contains(@name, "mediator_author")]/@content'
        ' | //span[@class="main-page-heading__author"]/text()',
        reposts_fb_path="_",
        reposts_vk_path="_",
        reposts_ok_path="_",
        reposts_twi_path="_",
        reposts_lj_path="_",
        reposts_tg_path="_",
        likes_path="_",
        views_path="_",
        comm_count_path="_",
    )

    def parse(self, response):
        """Parse first main sitemap.xml by initial parsing method.
        Getting sub_sitemaps.
        """
        body = response.body
        links = Selector(text=body).xpath("//loc/text()").getall()

        for link in links:
            yield Request(url=link, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        """Parse each sub_sitemap. There is no today's news.
        """
        body = response.body
        links = Selector(text=body).xpath("//loc/text()").getall()
        lm_datetimes = Selector(text=body).xpath("//lastmod/text()").getall()

        for i in range(len(links)):
            if "https://russian.rt.com/tag/" not in links[i]:
                if (
                    datetime.strptime(
                        lm_datetimes[i][:22] + "00", "%Y-%m-%dT%H:%M:%S%z"
                    ).date()
                    >= self.until_date
                ):
                    yield Request(url=links[i], callback=self.parse_document)

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
            return datetime.strptime(raw_date[0], "%d %m %Y,").strftime(
                "%Y-%m-%dT%H:%M:%S"
            )

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
            item["date"] = self.fix_date(item["date"])
            item["text"] = self.cut_instagram(item["text"])
            yield item
