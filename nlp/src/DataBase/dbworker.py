import configparser
import os
import time

from uuid import uuid4

# Коннектор к базе данных
from dbconnector import UseDatabase


class Dbwriter(object):
    """
    Обертывает класс CSVCorpusReader, читает подготовленные файлы для загрузки
    и записывает данные в БД в таблицу сырых данных
    """

    def __init__(self, corpus):
        """
        corpus - класс CSVCorpusReader
        """
        self.corpus = corpus

    def __get_fileids(self, fileids=None, categories=None):
        fileids = self.corpus.check_arguments(fileids, categories)
        if fileids:
            return fileids
        return self.corpus.fileids()

    def __process(self, fileid):
        """
        Вызывается для файла и записывает данные из него в БД.
        """

        # получить название источника данных
        news_source = os.path.dirname(fileid)
        print(news_source)

        # database connect
        config = configparser.ConfigParser()
        config.read("../../config/db.ini")

        dbconfig = {
            "host": config["dev"]["host"],
            "dbname": config["dev"]["db"],
            "user": config["dev"]["user"],
            "password": config["dev"]["password"],
        }

        n_rows = 0
        started = time.time()
        with UseDatabase(dbconfig) as cursor:
            sql = "SELECT * FROM raw_data.news_source WHERE name= %s"

            cursor.execute(sql, (news_source,))
            query_results = cursor.fetchall()

            sql = """INSERT INTO raw_data.raw_data
                     (id_raw_data, id_news_source, date, url, edition, topics, authors, title, text, reposts_fb, reposts_vk, reposts_ok, reposts_twi, reposts_lj, reposts_tg, likes, views, comm_count, created_date, modified_date, batch_date)
                     VALUES
                     (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            for line in list(self.corpus.read_docs(fileid)):
                n_rows = n_rows + 1
                cursor.execute(
                    sql,
                    (
                        uuid4().hex,
                        query_results[0][0],
                        line["date"],
                        line["url"],
                        line["edition"],
                        line["topics"],
                        line["authors"],
                        line["title"],
                        line["text"],
                        line["reposts_fb"],
                        line["reposts_vk"],
                        line["reposts_ok"],
                        line["reposts_twi"],
                        line["reposts_lj"],
                        line["reposts_tg"],
                        line["likes"],
                        line["views"],
                        line["comm_count"],
                        "2019-12-02 22:43:00",
                        "2019-12-02 22:43:00",
                        "1900-01-01 00:00:00",
                    ),
                )

        print("Количество строк в файле " + fileid + ":", n_rows)
        print("Время обработки в секундах: " + str(time.time() - started))
        return fileid + " is done"

    def write_file(self, fileids=None, categories=None):
        # Получить имена файлов для обработки
        return [
            self.__process(fileid) for fileid in self.__get_fileids(fileids, categories)
        ]


class DataBaseCorpusReader(object):
    """Читает данные из базы"""

    def __init__(self):
        # database connect
        config = configparser.ConfigParser()
        config.read("../../config/db.ini")

        self.dbconfig = {
            "host": config["dev"]["host"],
            "dbname": config["dev"]["db"],
            "user": config["dev"]["user"],
            "password": config["dev"]["password"],
        }

    def get_news_source_raw(self):
        """
        Выводит все источники данных, которые есть в базе, в схеме сырых данных, с целью
        дальнейшего использования
        """

        with UseDatabase(self.dbconfig) as cursor:
            sql = """SELECT id_news_source, "name" FROM raw_data.news_source;"""

            cursor.execute(sql,)
            query_results = cursor.fetchall()

            for news_source in query_results:
                yield news_source

    def get_news_text_raw(self, source=None):
        """
        Выводит все новости со всеми полями, которые есть в базе, в схеме сырых данных, с целью
        дальнейшего использования, либо по конкретному идентификатору источника

        Параметры:
        source - идентификатор источника данных, полученный get_news_source_raw
        """
        with UseDatabase(self.dbconfig) as cursor:
            if source is None:
                sql = """SELECT id_raw_data, id_news_source, "date", url, edition, topics, authors, title, "text", 
                         reposts_fb, reposts_vk, reposts_ok, reposts_twi, reposts_lj, reposts_tg, likes, "views", 
                         comm_count, created_date, modified_date, batch_date 
                         FROM raw_data.raw_data"""
                cursor.execute(sql,)
            else:
                sql = """SELECT id_raw_data, id_news_source, "date", url, edition, topics, authors, title, "text", 
                                     reposts_fb, reposts_vk, reposts_ok, reposts_twi, reposts_lj, reposts_tg, likes, 
                                     "views", comm_count, created_date, modified_date, batch_date 
                                     FROM raw_data.raw_data
                                     WHERE id_news_source= %s"""
                cursor.execute(sql, (source,))

            query_results = cursor.fetchall()

            for text in query_results:
                yield text

    def get_news_only_text_raw(self, source=None):
        """
        Выводит все новости, но только их тексты, которые есть в базе, в схеме сырых данных, с целью
        дальнейшего использования, либо по конкретному идентифакатору источника

        Параметры:
        source - идентификатор источника данных, полученный get_news_source_raw
        """
        with UseDatabase(self.dbconfig) as cursor:
            if source is None:
                sql = """SELECT "text" 
                         FROM raw_data.raw_data"""
                cursor.execute(sql,)
            else:
                sql = """SELECT "text"
                         FROM raw_data.raw_data
                         WHERE id_news_source= %s"""
                cursor.execute(sql, (source,))

            query_results = cursor.fetchall()

            for text in query_results:
                yield text
