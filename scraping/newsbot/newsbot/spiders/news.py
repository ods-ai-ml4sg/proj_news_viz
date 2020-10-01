from datetime import datetime
from datetime import timedelta
from urllib.parse import urlsplit

import scrapy
from newsbot.items import Document
from scrapy.loader import ItemLoader


class NewsSpiderConfig:
    def __init__(
            self,
            title_path,
            subtitle_path,
            date_path,
            date_format,
            text_path,
            topics_path,
            subtopics_path,
            tags_path,
            authors_path,
            reposts_fb_path,
            reposts_vk_path,
            reposts_ok_path,
            reposts_twi_path,
            reposts_lj_path,
            reposts_tg_path,
            likes_path,
            views_path,
            comm_count_path,
    ):
        self.title_path = title_path
        self.subtitle_path = subtitle_path
        self.date_path = date_path
        self.date_format = date_format
        self.text_path = text_path
        self.topics_path = topics_path
        self.subtopics_path = subtopics_path
        self.authors_path = authors_path
        self.tags_path = tags_path

        self.reposts_fb_path = reposts_fb_path
        self.reposts_vk_path = reposts_vk_path
        self.reposts_ok_path = reposts_ok_path
        self.reposts_twi_path = reposts_twi_path
        self.reposts_lj_path = reposts_lj_path
        self.reposts_tg_path = reposts_tg_path
        self.likes_path = likes_path
        self.views_path = views_path
        self.comm_count_path = comm_count_path


class NewsSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        assert self.config
        assert self.config.title_path
        assert self.config.subtitle_path
        assert self.config.date_path
        assert self.config.date_format
        assert self.config.text_path
        assert self.config.topics_path
        assert self.config.subtopics_path
        assert self.config.authors_path
        assert self.config.tags_path

        assert self.config.reposts_fb_path
        assert self.config.reposts_vk_path
        assert self.config.reposts_ok_path
        assert self.config.reposts_twi_path
        assert self.config.reposts_lj_path
        assert self.config.reposts_tg_path
        assert self.config.likes_path
        assert self.config.views_path
        assert self.config.comm_count_path

        # Trying to parse 'until_date' param as date
        if "until_date" in kwargs:
            kwargs["until_date"] = datetime.strptime(kwargs["until_date"],
                                                     "%d.%m.%Y").date()
        else:
            # If there's no 'until_date' param, get articles for today and yesterday
            kwargs["until_date"] = (datetime.now() - timedelta(days=1)).date()

        if "start_date" in kwargs:
            kwargs["start_date"] = datetime.strptime(kwargs["start_date"],
                                                     "%d.%m.%Y").date()
        else:
            kwargs["start_date"] = datetime.now().date()

        super().__init__(*args, **kwargs)

    def parse_document(self, response):
        url = response.url
        base_edition = urlsplit(self.start_urls[0])[1]
        edition = urlsplit(url)[1]

        l = ItemLoader(item=Document(), response=response)
        l.add_value("url", url)
        l.add_value("edition", "-" if edition == base_edition else edition)
        l.add_xpath("title", self.config.title_path)
        l.add_xpath("subtitle", self.config.subtitle_path)
        l.add_xpath("date", self.config.date_path)
        l.add_xpath("text", self.config.text_path)
        l.add_xpath("topics", self.config.topics_path)
        l.add_xpath("subtopics", self.config.subtopics_path)
        l.add_xpath("authors", self.config.authors_path)
        l.add_xpath("tags", self.config.tags_path)

        l.add_xpath("reposts_fb", self.config.reposts_fb_path)
        l.add_xpath("reposts_vk", self.config.reposts_vk_path)
        l.add_xpath("reposts_ok", self.config.reposts_ok_path)
        l.add_xpath("reposts_twi", self.config.reposts_twi_path)
        l.add_xpath("reposts_lj", self.config.reposts_lj_path)
        l.add_xpath("reposts_tg", self.config.reposts_tg_path)
        l.add_xpath("likes", self.config.likes_path)
        l.add_xpath("views", self.config.views_path)
        l.add_xpath("comm_count", self.config.comm_count_path)

        yield l.load_item()

    def process_title(self, title):
        return title

    def process_text(self, paragraphs):
        text = "\\n".join([p.strip() for p in paragraphs if p.strip()])
        return text

    def process_metric(self, metrics):
        # Remove whitespaces
        metrics = [i.strip() for i in metrics if i.strip()]
        return metrics[0]
