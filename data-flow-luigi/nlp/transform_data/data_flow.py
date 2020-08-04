import configparser
import time
from datetime import datetime

import luigi
from luigi.contrib.postgres import PostgresTarget
from py_scripts.dbconnector import UseDatabase
from py_scripts.dbconnector import UseDatabaseCusror
from py_scripts.preprocessing_tools import clean_text
from py_scripts.preprocessing_tools import lemmatize
from razdel import sentenize
# Коннектор к базе данных


class WriteDataToDatabase(luigi.Task):
    """
    Функция ищет строки в таблице raw_data.raw_data,
    которые еще не были записаны в таблицу prepared_data.news
    обрабатывает их и затем вставляет в таблицу prepared_data.news
    """

    run_date = luigi.DateParameter(default=datetime.now().date())
    config = configparser.ConfigParser()
    config.read("config/db.ini")

    dbconfig = {
        "host": config["dev"]["host"],
        "dbname": config["dev"]["db"],
        "user": config["dev"]["user"],
        "password": config["dev"]["password"],
    }

    def __iter_row(self, from_cursor, dt_now, size):
        rows = from_cursor.fetchmany(size)
        for row in rows:
            sents = list(sentenize(str(row[5]).lower()))
            clean_sentence = [clean_text(_.text) for _ in sents]
            lemma_sentence = [lemmatize(sent) for sent in clean_sentence]
            yield (
                str(row[0]),
                str(row[1]),
                "4847c8c7-a14f-4d59-8f62-a1c622db4aab",
                "4847c8c7-a14f-4d59-8f62-a1c622db4aab",
                row[2],
                row[3],
                row[4],
                str(lemma_sentence),
                dt_now,
                dt_now,
                "1900-01-01 00:00:00",
            )

    def run(self):
        started = time.time()
        dt_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print("Время начала обработки: " + str(time.asctime()))

        with UseDatabaseCusror(self.dbconfig) as from_cursor:
            sql = """SELECT id_raw_data, id_news_source, date, url, title, text
                    FROM raw_data.raw_data
                    where batch_date = '1900-01-01 00:00:00'
                    order by id_raw_data """
            t = time.time()
            from_cursor.execute(sql)
            print("Exec SQL is - ", str(time.time() - t))

            with UseDatabase(self.dbconfig) as to_cursor:
                while True:
                    records = list(self.__iter_row(from_cursor, dt_now, 10))
                    if not records:
                        break
                    to_cursor.executemany(
                        """
                                INSERT INTO prepared_data.news
                                (id_news, id_topic, id_news_source, id_author, date_news, link_news, title, text_news, created_date, modified_date, batch_date)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                """,
                        records,
                    )

            self.get_target().touch()
        print("Время обработки в секундах: " + str(time.time() - started))

    def get_target(self):
        return PostgresTarget(
            host=self.config["dev"]["host"],
            database=self.config["dev"]["db"],
            user=self.config["dev"]["user"],
            password=self.config["dev"]["password"],
            table="prepared_data.news",
            update_id=str(self.run_date),
        )

    def output(self):
        return self.get_target()


# python data_flow.py UpdateBatchDate --local-scheduler
class UpdateBatchDate(luigi.Task):
    """
    Функция обновляется поле batch_date в таблице raw_data.raw_data
    для тех строк, которые были записаны в таблицу prepared_data.news.
    Зависит от выполнения WriteDataToDatabase
    """

    config = configparser.ConfigParser()
    config.read("config/db.ini")

    dbconfig = {
        "host": config["dev"]["host"],
        "dbname": config["dev"]["db"],
        "user": config["dev"]["user"],
        "password": config["dev"]["password"],
    }

    def requires(self):
        return WriteDataToDatabase()

    def run(self):
        started = time.time()
        print("Время начала обработки: " + str(time.asctime()))

        with UseDatabase(self.dbconfig) as cursor:
            batch_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            sql = """UPDATE raw_data.raw_data
                     SET batch_date= %s
                     WHERE raw_data.raw_data.id_raw_data in (
                        select prepared_data.news.id_news
                        from prepared_data.news
                        where prepared_data.news.batch_date = '1900-01-01 00:00:00');"""

            cursor.execute(sql, (batch_date, ))

            sql = """UPDATE prepared_data.news
                     SET batch_date= %s
                     WHERE prepared_data.news.batch_date = '1900-01-01 00:00:00';"""

            cursor.execute(sql, (batch_date, ))

        print("Время обработки в секундах: " + str(time.time() - started))


if __name__ == "__main__":
    luigi.run()
