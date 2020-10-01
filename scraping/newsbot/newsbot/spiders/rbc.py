import json
import time
from datetime import datetime

import scrapy
from newsbot.spiders.news import NewsSpider, NewsSpiderConfig
from scrapy.http import HtmlResponse


class RbcSpider(NewsSpider):
    name = "rbc"
    link_tmpl = (
        "https://www.rbc.ru/v10/ajax/get-news-feed/project/rbcnews/lastDate/{}/limit/22"
    )
    start_urls = [link_tmpl.format(int(time.time()))]
    config = NewsSpiderConfig(
        title_path='//span[contains(@class, "js-slide-title")]//text()',
        subtitle_path='//div[contains(@class, "article__text__overview")]/span//text()',
        date_path="_",
        date_format="%Y-%m-%d %H:%M:%S",
        text_path='(.//div[contains(@class, "article__text")])'
        '/*[not(self::script) and not(self::div[@class="subscribe-infographic"])]//text()',
        topics_path='(.//a[contains(@class, "article__header__category")])[1]//text()',
        subtopics_path="_",
        authors_path='//div[contains(@class, "article__authors")]/text()',
        tags_path='//div[contains(@class, "article__tags")]//a//text()',
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
        items = json.loads(response.body.decode("utf-8"))["items"]

        pub_dt = None
        for i in items:
            resp = HtmlResponse(url="", body=i["html"], encoding="utf8")

            link = resp.xpath("//a/@href").extract()[0]
            pub_dt = datetime.fromtimestamp(i["publish_date_t"])

            if self.start_date >= pub_dt.date() >= self.until_date:
                yield scrapy.Request(
                    url=link, callback=self.parse_document, meta={"pub_dt": pub_dt}
                )

        # Requesting page if publication date of the last article is above "until_date"
        if pub_dt and self.start_date >= pub_dt.date() >= self.until_date:
            # Forming the next page link
            link_url = self.link_tmpl.format(int(pub_dt.timestamp()))

            yield scrapy.Request(
                url=link_url,
                priority=100,
                callback=self.parse,
                meta={"page_depth": response.meta.get("page_depth", 1) + 1},
            )

    def parse_document(self, response):
        for res in super().parse_document(response):
            res["date"] = [response.meta["pub_dt"].strftime(self.config.date_format)]

            # If the article is located in "www.rbc.ru" url, then return it
            # (not "sportrbc.ru", "delovtb.rbc.ru" e t.c. because they have another html layout)
            if "topics" in res:
                res["topics"] = [topics.strip(",") for topics in res["topics"]]
            if "tags" in res:
                res["tags"] = [
                    ", ".join([j.strip() for j in i.split(",") if j.strip()])
                    for i in res["tags"]
                ]
            if res["edition"][0] == "-":
                if "authors" in res:
                    res["authors"] = [
                        i.replace("\n", "").strip()
                        for i in res["authors"]
                        if i.replace("\n", "").strip()
                    ]
                    res["authors"] = [authors.strip(".") for authors in res["authors"]]

                res["text"] = [i.replace("\xa0", " ") for i in res["text"]]

                yield res
