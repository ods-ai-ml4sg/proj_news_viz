import html
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Dict

import pymorphy2

PATH = Path("../..")
sys.path.append(str(PATH))

cache: Dict = {}
morph = pymorphy2.MorphAnalyzer()

# read stopwords for RU
try:
    with open(PATH / "data/features/stopwords_ru.txt", "r") as file:
        stopwords = file.read().splitlines()
except FileNotFoundError:
    print("can't load /data/features/stopwords_ru.txt")
    stopwords = []


def clean_text(text: str = None) -> str:
    """
    clean text, leaving only tokens for clustering
    parameters
    ----------
        text : string
            input text
    returns
    -------
        cleaned string text without lower case
    """

    if not isinstance(text, str):
        text = str(text)

    text = html.unescape(text)

    text = re.sub(r"https?:\/\/.*[\r\n]*", "", text)  # remove urls
    text = re.sub(r"\S+@\S+", "", text)  # remove emails
    text = re.sub(r"ё", "е", text)
    text = re.sub(r"\!|\"|\:|\;|\.|\,|[<>]|\?|\@|\[|\]|\^|\_|\`|[{}]|\~|[—–-]|[«»]|[()]", " ", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text)  # remove the long blanks

    text = text.strip()

    if len(text) < 3:
        return "TOREMOVE"
    else:
        return text


@lru_cache()
def get_morph4token(token: str = None) -> str:
    """
    get lemma for one tokens with decorator `@lru_cache`
    """

    return morph.parse(token)[0].normal_form


def lemmatize(text: str = None, char4split: str = " ") -> str:
    """
    lemmatizations text with cache
    parameters
    ----------
    input_text : string
        cleaned text
    char4split : string (default = " ")
        char-symbol how to split text
    returns
    -------
        lemmatized text
    """

    # get tokens from input text
    # in this case it's normal approach because we hard cleaned text
    if not isinstance(text, str):
        text = str(text)

    # get tokens from input text
    # in this case it's normal approach because we hard cleaned text
    list_tokens = text.split(char4split)

    words_lem = [get_morph4token(token) for token in list_tokens if token not in stopwords]

    if len(words_lem) < 3:
        return "TOREMOVE"
    else:
        return " ".join(words_lem)
