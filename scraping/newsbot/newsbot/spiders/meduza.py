import json
from datetime import datetime

import scrapy
from newsbot.spiders.news import NewsSpider
from newsbot.spiders.news import NewsSpiderConfig
from scrapy import Request
from scrapy import Selector
from scrapy.linkextractors import LinkExtractor


class MeduzaSpider(NewsSpider):
    name = "meduza"
    page_link_tmpl = (
        "https://meduza.io/api/v3/search?chrono=news&page={}&per_page=24&locale=ru"
    )
    article_link_tmpl = "https://meduza.io/{}"
    start_urls = [page_link_tmpl.format(0)]
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
    fields = [
        "title",
        "topics",
        "authors",
        "edition",
        "url",
        "text",
        "date",
    ]

    config = NewsSpiderConfig(
        title_path='//h1[contains(@class,"RichTitle-root") or contains(@class,"SimpleTitle-root") or contains(@class,"RichTitle-root RichTitle-slide")]//text()',
        subtitle_path='//h3[contains(@class, "CardTitle-title") or contains(@class, "SimpleBlock-h3")]//text()',
        date_path='//time[contains(@class,"Timestamp-root")]/text()',
        date_format="%H:%M, %d %m %Y",
        text_path='//div[contains(@class,"GeneralMaterial-article") or contains(@class, "SlidesMaterial-layout") '
        + 'or contains(@class,"MediaCaption-caption")]//p//text() | //div[contains(@class, "MediaCaption-caption")]//text() | '
        + '//p[contains(@class,"SimpleBlock-p") or contains(@class,"SimpleBlock-lead")]//text()',
        topics_path="_",
        subtopics_path="_",
        authors_path='//p[contains(@class, "MaterialNote-note_caption")]/strong/text()',
        tags_path="_",
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
        last_page = False

        jsonresponse = json.loads(response.body_as_unicode())

        # Getting article items
        articles = [content for _, content in jsonresponse["documents"].items()]
        # Sorting them from the most recent to the most late one
        articles = sorted(articles, key=lambda x: x["published_at"], reverse=True)

        # Filtering out late articles and checking if we have reached the "until_date"
        filtered_articles = []
        for content in articles:
            pub_date = datetime.strptime(content["pub_date"], "%Y-%m-%d").date()
            if self.start_date >= pub_date >= self.until_date:

                filtered_articles.append(content)
            else:
                last_page = True

        # Iterating through news on this page
        for content in filtered_articles:
            full_url = self.article_link_tmpl.format(content["url"])

            yield scrapy.Request(url=full_url, callback=self.parse_document)

        # Requesting a new page if needed
        if not last_page and jsonresponse["has_next"]:
            page_depth = response.meta.get("page_depth", 1)

            link_url = self.page_link_tmpl.format(page_depth)

            yield scrapy.Request(
                url=link_url,
                priority=100,
                callback=self.parse,
                meta={"page_depth": page_depth + 1},
            )

    def parse_document(self, response):
        for res in super().parse_document(response):

            for field in self.fields:
                if field not in res:
                    res[field] = [""]
            for i, month in enumerate(self.months_ru):
                res["date"][0] = res["date"][0].replace(month, str(i + 1))

            yield res
