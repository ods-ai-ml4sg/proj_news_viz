import json
from datetime import datetime

import scrapy
from newsbot.spiders.news import NewsSpider
from newsbot.spiders.news import NewsSpiderConfig
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor


class VedomostiSpider(NewsSpider):
    name = "vedomosti"
    start_urls = ["https://www.vedomosti.ru/newsline"]
    config = NewsSpiderConfig(
        title_path='(.//div[contains(@class, "b-news-item__title")]//h1)[1]/text()',
        subtitle_path="_",
        date_path='//time[@class="b-newsline-item__time"]/@pubdate',
        date_format="%Y-%m-%d %H:%M:%S %z",  # 2019-03-02 20:08:47 +0300
        text_path='(.//div[contains(@class, "b-news-item__text")])[1]/p//text()',
        topics_path='(.//div[contains(@class, "io-category")])[1]/text()',
        subtopics_path="_",
        authors_path="_",
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
    news_le = LinkExtractor(
        restrict_xpaths='//div[contains(@class, "b-newsline-item__title")]'
    )

    def parse(self, response):
        if response.meta.get("page_depth", 1) > 1:
            # If this is the second page and later we get a JSON object with html field in response,
            # so we should reform a response object and get links the other way
            d = json.loads(response.body.decode("utf-8"))["html"]
            resp = HtmlResponse(url=response.url, body=d, encoding="utf8")

            links = [
                "https://www.vedomosti.ru/{}".format(i)
                for i in resp.xpath("//a/@href").extract()
            ]

            # Getting publication date for every article
            pub_dts = resp.xpath(self.config.date_path).extract()
            # Convert datetimes of publication from string to datetime
            pub_dts = [datetime.strptime(dt, self.config.date_format) for dt in pub_dts]
        else:
            # Getting publication date for every article
            pub_dts = response.xpath(self.config.date_path).extract()
            # Convert datetimes of publication from string to datetime
            pub_dts = [datetime.strptime(dt, self.config.date_format) for dt in pub_dts]

            links = [i.url for i in self.news_le.extract_links(response)]

        for link, pub_dt in zip(links, pub_dts):
            if pub_dt.date() >= self.until_date:
                yield scrapy.Request(
                    url=link, callback=self.parse_document, meta={"date": pub_dt}
                )

        # Get the last page in the page to see, whether we need another page
        last_dt = list(pub_dts)[-1]

        # Determine if this is the last page
        if last_dt.date() >= self.until_date:
            # Example: https://www.vedomosti.ru/newsline/more/2019-02-27%2017:18:41%20+0300
            link_url = "{}/more/{}%20{}%20{}".format(
                self.start_urls[0],
                last_dt.strftime("%Y-%m-%d"),
                last_dt.strftime("%H:%M:%S"),
                last_dt.strftime("%z"),
            )

            yield scrapy.Request(
                url=link_url,
                priority=100,
                callback=self.parse,
                meta={"page_depth": response.meta.get("page_depth", 1) + 1},
            )

    def parse_document(self, response):
        for res in super().parse_document(response):
            res["date"] = [response.meta.get("date").strftime(self.config.date_format)]

            res["text"] = [text.strip() for text in res["text"]]
            res["title"] = [text.strip() for text in res["title"]]
            res["topics"] = [text.strip() for text in res["topics"]]

            yield res
