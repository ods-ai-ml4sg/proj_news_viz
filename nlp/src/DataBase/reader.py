import codecs
import csv
import os
import sys
import time
from collections import Counter
from enum import Enum

from nltk.corpus.reader.api import CategorizedCorpusReader
from nltk.corpus.reader.api import CorpusReader
from razdel import sentenize
from razdel import tokenize


class PathPattern(Enum):

    doc_pattern = r".*\.csv"
    cat_pattern = r"(\w+)/*"


class CSVCorpusReader(CategorizedCorpusReader, CorpusReader):
    """
    Объект чтения csv файлов для получения возможности
    дополнительной предварительной обработки.
    """

    def __init__(self,
                 root,
                 fileids=PathPattern.doc_pattern.value,
                 encoding="utf8",
                 **kwargs):
        """
        Инициализирует объект чтения промежуточного обработанных файлов
        корпуса.
        """

        # Добавить шаблон категорий, если он не был передан в класс явно
        if not any(key.startswitch("cat_") for key in kwargs.keys()):
            kwargs["cat_pattern"] = PathPattern.cat_pattern.value

        # Инициализировать объекты чтения корпуса из NLTK
        CategorizedCorpusReader.__init__(self, kwargs)
        CorpusReader.__init__(self, root, fileids, encoding)

        # Инициировать список для сбора токенов
        self.__tokens = Counter()

    @property
    def get_tokens(self):
        """
        Возвращает список токенов, полученных в ходе метода get_descriptions
        """
        return self.__tokens

    def check_arguments(self, fileids, categories):
        """
        Возвращает список идентификаторов файлов или названий директорий,
        которые передаются каждой внутренний функции объекта чтения корпуса.
        """
        if fileids is not None and categories is not None:
            raise ValueError(
                "Укажите либо файлы, либо категории, а не оба параметра")

        if categories is not None:
            return self.fileids(categories)
        return fileids

    def read_docs(self, fileids=None, categories=None):
        """
        Возвращает содержимое документа csv, закрывая его
        по завершении чтения.
        """
        # Получить список файлов для чтения
        fileids = self.check_arguments(fileids, categories)

        # Создать генератор загружающий документы в память
        # по одному. Следующий блок увеличивает размер ячейки
        # чтения csv файла
        maxInt = sys.maxsize
        decrement = True

        while decrement:
            # decrease the maxInt value by factor 10
            # as long as the OverflowError occurs.

            decrement = False
            try:
                csv.field_size_limit(maxInt)
            except OverflowError:
                maxInt = int(maxInt / 10)
                decrement = True

        for path, encoding in self.abspaths(fileids, include_encoding=True):
            with codecs.open(path, "r", encoding=encoding) as f:
                reader = list(
                    csv.DictReader(f,
                                   delimiter=",",
                                   quotechar='"',
                                   escapechar="\\"))
                # reader = list(csv.DictReader(f, delimiter=';', quotechar='"', escapechar='\\'))
                for row in reader:
                    yield (row)

    def get_sizes(self, fileids=None, categories=None):
        """
        Возвращает список из идентификатора файла и его размера.
        Эта функция используется для выявления необычно больших файлов.
        """
        # Получить список файлов
        fileids = self.check_arguments(fileids, categories)

        # Создать генератор, возвращающий имена и размеры файла
        for path in self.abspaths(fileids):
            yield path, os.path.getsize(path)

    def read_columns(self, fileids=None, categories=None, key="text"):
        """
        Возвращает содержимое по указанному имени столбца из файла csv, в виде списка
        """
        for doc in self.read_docs(fileids, categories):
            yield (doc[key])

    def get_descriptions(self, fileids=None, categories=None):
        """
        Обходит все документы и возвращает словарь с разнообразными
        оценками, описывающими состояние корпуса
        """
        started = time.time()

        # Структура для подсчета
        counts = Counter()

        # Выполнить обход всех новостей из csv, выделить предложения и слова,
        # подсчитать их
        for i in self.read_docs(fileids, categories):
            counts["rows"] += 1
            sents = list(sentenize(i["text"]))
            sentence = [_.text for _ in sents]

            for sent in sentence:
                counts["sents"] += 1
                if len(sent) == 0:
                    continue
                for word in [_.text for _ in list(tokenize(sent))]:
                    counts["words"] += 1
                    self.__tokens[word.lower()] += 1

        # Определить число файлов и категорий в корпусе
        n_fileids = len(
            self.check_arguments(fileids, categories) or self.fileids())
        n_topics = len(
            self.categories(self.check_arguments(fileids, categories)))

        # Составить список новостей
        list_news = list(self.read_columns(fileids, categories))
        # Вернуть структуру с информацией
        return {
            "Количество файлов":
            n_fileids,
            "Количество источников новостей":
            n_topics,
            "Количество обработанных новостей":
            counts["rows"],
            "Количество предложений":
            counts["sents"],
            "Количество слов":
            counts["words"],
            "Количество токенов (словарь)":
            len(self.get_tokens),
            "Коэффициент лексического разнообразия (lexical diversity)":
            float(counts["words"]) / float(len(self.get_tokens)),
            "Среднее количество новостей по отношению к файлам":
            float(counts["rows"]) / float(n_fileids),
            "Среднее количество предложений в новостях":
            float(counts["sents"]) / float(counts["rows"]),
            "Начальная дата в обработке":
            min(self.read_columns(fileids, categories, "date")),
            "Конечная дата в обработке":
            max(self.read_columns(fileids, categories, "date")),
            "Количество повторяющихся новостей":
            len(list_news) - len(set(list_news)),
            "Количество пустых новостных элементов":
            len([item for item in list_news if len(item) == 0]),
            "Время обработки в секундах":
            time.time() - started,
        }
