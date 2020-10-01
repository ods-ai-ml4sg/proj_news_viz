from datetime import datetime
from datetime import timedelta

import scrapy
from newsbot.spiders.news import NewsSpider
from newsbot.spiders.news import NewsSpiderConfig
from scrapy.linkextractors import LinkExtractor


class KommersantSpider(NewsSpider):
    name = "kommersant"

    base_url = "https://www.kommersant.ru"
    link_tmpl = "https://www.kommersant.ru/archive/list/77/{}"
    # Start with the current date
    page_dt = datetime.now()
    start_urls = [link_tmpl.format(page_dt.strftime("%Y-%m-%d"))]

    # Ignore "robots.txt" for this spider only
    custom_settings = {"ROBOTSTXT_OBEY": "False"}

    config = NewsSpiderConfig(
        title_path='//h2[contains(@class, "article_name")]//text()',
        subtitle_path='//h1[contains(@class, "article_subhead")]//text()',
        date_path='//meta[contains(@property, "published_time")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S%z",  # 2019-03-09T12:03:10+03:00
        text_path='//p[@class="b-article__text"]//text()',
        topics_path='//meta[contains(@name, "category")]/@content',
        subtopics_path="_",
        authors_path='//p[contains(@class, "document_authors")]//text()',
        tags_path='//meta[contains(@name, "keywords")]/@content',
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
    news_le = LinkExtractor(restrict_xpaths='//div[@class="archive_result__item_text"]')

    def parse(self, response):
        # Parse most recent news
        for i in self.news_le.extract_links(response):
            yield scrapy.Request(
                url=i.url, callback=self.parse_document, meta={"page_dt": self.page_dt}
            )

        # If it's not the end of the page, request more news from archive by calling recursive "parse_page" function
        more_link = response.xpath(
            '//button[contains(@class, "lazyload-button")]/@data-lazyload-url'
        ).extract()
        if more_link:
            yield scrapy.Request(
                url="{}{}".format(self.base_url, more_link[0]),
                callback=self.parse_page,
                meta={"page_dt": self.page_dt},
            )

        # Requesting the next page if we need to
        self.page_dt -= timedelta(days=1)
        if self.start_date >= self.page_dt.date() >= self.until_date:
            link_url = self.link_tmpl.format(self.page_dt.strftime("%Y-%m-%d"))

            yield scrapy.Request(
                url=link_url,
                priority=100,
                callback=self.parse,
                meta={
                    "page_depth": response.meta.get("page_depth", 1) + 1,
                    "page_dt": self.page_dt,
                },
            )

    def parse_page(self, response):
        # Parse all articles on page
        for i in self.news_le.extract_links(response):
            yield scrapy.Request(url=i.url, callback=self.parse_document)

        # Take a link from "more" button
        more_link = response.xpath(
            '//button[contains(@class, "lazyload-button")]/@data-lazyload-url'
        ).extract()
        if more_link:
            yield scrapy.Request(
                url="{}{}".format(self.base_url, more_link[0]),
                callback=self.parse_page,
                meta={
                    "page_depth": response.meta.get("page_depth", 1),
                    "page_dt": response.meta["page_dt"],
                },
            )

    def parse_document(self, response):
        for res in super().parse_document(response):
            # If it's a gallery (no text) or special project then don't return anything (have another html layout)
            if "text" not in res or "title" not in res:
                break
            res["tags"] = [tags.strip(",").replace(",", ", ") for tags in res["tags"]]

            if "Ъ-FM" in res["topics"][0]:
                l = res["topics"][0].split(",")
                if len(l) > 1:
                    print(res["topics"][0])
                    res["topics"][0] = ", ".join(l[1:])
                else:
                    res["topics"][0] = ""
            else:
                res["topics"][0] = res["topics"][0].replace(",", ", ")
                res["topics"][0] = res["topics"][0].replace(".", ", ")

            # Remove ":" in timezone
            pub_dt = res["date"][0]
            res["date"] = [pub_dt[:-3] + pub_dt[-3:].replace(":", "")]

            yield res
