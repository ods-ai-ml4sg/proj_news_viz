from datetime import datetime

import requests
from newsbot.spiders.news import NewsSpider
from newsbot.spiders.news import NewsSpiderConfig
from scrapy import Request
from scrapy import Selector


class IzSpider(NewsSpider):
    name = "iz"
    start_urls = ["https://iz.ru/sitemap.xml"]
    config = NewsSpiderConfig(
        title_path='//h1[contains(@itemprop, "headline")]/span/text()',
        subtitle_path="_",
        date_path='//meta[contains(@property, "published_time")]/@content',
        date_format="%Y-%m-%dT%H:%M:%S%z",
        text_path="//article//p//text()",
        topics_path='//div[contains(@itemprop, "genre")]//'
        'a[contains(@href, "rubric") or contains(@href, "press-release")]//text()',
        subtopics_path="_",
        authors_path='//div[contains(@itemprop, "author")]//a[contains(@href, "author")]//text()',
        tags_path='//div[contains(@class, "hash_tags")]//a//text()',
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
        # Parse last sitemap xml number
        # (in this case: "1"): https://iz.ru/export/sitemap/1/xml
        sitemap_n = int(links[-1].split("sitemap/")[1].split("/")[0])

        # Get last empty sitemap link (main "sitemap.xml" on this site isn't updated frequently enough)
        # by iterating sitemap links adding "number" to it
        sitemap_n += 1
        while True:
            link = "https://iz.ru/export/sitemap/{}/xml".format(sitemap_n)
            body = requests.get(link).content

            sitemap_links = Selector(text=body).xpath("//loc/text()").getall()
            # If there are links in this sitemap
            if sitemap_links:
                links.append(link)
                sitemap_n += 1
            else:
                break

        # Get all links from sitemaps until reach "until_date"
        for link in links[::-1]:
            yield Request(url=link, callback=self.parse_sitemap)

    def parse_sitemap(self, response):
        # Parse sub sitemaps
        body = response.body
        links = Selector(text=body).xpath("//loc/text()").getall()
        last_modif_dts = Selector(text=body).xpath("//lastmod/text()").getall()

        # Sort news by modification date descending
        news = [
            (link, last_modif_dt) for link, last_modif_dt in zip(links, last_modif_dts)
        ]
        sorted_news = sorted(news, key=lambda x: x[1], reverse=True)

        # Iterate news and parse them
        for link, last_modif_dt in sorted_news:
            # Convert last_modif_dt to datetime
            last_modif_dt = datetime.strptime(last_modif_dt, "%Y-%m-%d")

            if self.start_date >= last_modif_dt.date() >= self.until_date:
                yield Request(url=link, callback=self.parse_document)

    def parse_document(self, response):
        for res in super().parse_document(response):
            # Remove ":" in timezone
            pub_dt = res["date"][0]
            res["date"] = [pub_dt[:-3] + pub_dt[-3:].replace(":", "")]

            # If it is a video article, allow it not to have text
            if "/video/" in res["url"][0]:
                if "text" not in res:
                    res["text"] = [""]

            yield res

    def _get_last_page_dt(self, link):
        body = requests.get(link).content

        pub_dts = Selector(text=body).xpath("//lastmod/text()").getall()
        return datetime.strptime(pub_dts[0], "%Y-%m-%d")
