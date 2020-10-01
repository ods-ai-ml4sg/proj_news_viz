# -*- coding: utf-8 -*-
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import datetime


class NewsbotPipeline(object):
    def open_spider(self, spider):
        self.file = open(spider.name + ".csv", "w", encoding="utf8")
        self.writer = csv.writer(self.file, delimiter=",")
        # Write header to the resulting file
        self._fields = [
            "date",
            "url",
            "edition",
            "topics",
            "subtopics",
            "authors",
            "tags",
            "title",
            "subtitle",
            "text",
        ]
        self._metrics = [
            "reposts_fb",
            "reposts_vk",
            "reposts_ok",
            "reposts_twi",
            "reposts_lj",
            "reposts_tg",
            "likes",
            "views",
            "comm_count",
        ]
        self.file.write(",".join(self._fields + self._metrics) + "\n")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        dt = datetime.datetime.strptime(item["date"][0], spider.config.date_format)

        item["title"] = spider.process_title(item["title"][0])
        item["subtitle"] = "; ".join(spider.process_title(item.get("subtitle", "-")))
        item["topics"] = ", ".join(item.get("topics", "-"))
        item["subtopics"] = ", ".join(item.get("subtopics", "-"))
        item["authors"] = ", ".join(item.get("authors", "-"))
        item["tags"] = ", ".join(item.get("tags", "-"))

        item["edition"] = item["edition"][0]
        item["url"] = item["url"][0]
        item["text"] = spider.process_text(item["text"])
        item["date"] = dt.strftime("%Y-%m-%d %H:%M:%S")

        item = self._process_metrics(spider, item, self._metrics)

        # Filtering out too late items
        if dt.date() >= spider.until_date and dt.date() <= spider.start_date:
            line = (
                item["date"],
                item["url"],
                item["edition"],
                item["topics"],
                item["subtopics"],
                item["authors"],
                item["tags"],
                item["title"],
                item["subtitle"],
                item["text"],
                item["reposts_fb"],
                item["reposts_vk"],
                item["reposts_ok"],
                item["reposts_twi"],
                item["reposts_lj"],
                item["reposts_tg"],
                item["likes"],
                item["views"],
                item["comm_count"],
            )
            self.writer.writerow(line)

        return item

    def _process_metrics(self, spider, item, metrics):
        for m in metrics:
            if spider.config.__getattribute__(m + "_path") == "_":
                item[m] = "-"
            else:
                item[m] = spider.process_metric(item.get(m, ["0"]))

        return item
