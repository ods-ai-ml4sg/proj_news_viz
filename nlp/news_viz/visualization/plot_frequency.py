from typing import List, Optional, Tuple

import matplotlib.pyplot as plt

Vocab = List[Tuple[str, float]]

def plotFrequencyWords(vocab: Vocab,
                       top_words: int = 30,
                       plt_background: Optional[str] = None) -> None:
    """
    plot token frequency
    parameters
    ----------
        vocab: Vocab
            list tuples words with them frequency
            like `[('на', 1330966), ... ]`
        top_words: int (defauld = 30)
            enter top words to plot
        plt_background : str {'dark'} (default = None)
            background stale for matplotlib.pyplot.plt
    """

    if plt_background == "dark":
        plt.style.use("dark_background")

    x, y = [], []
    for key, val in vocab[:top_words]:
        x.append(key)
        y.append(val)

    plt.figure(figsize=(20, 10), )
    plt.bar(x, y)
    plt.title(f"топ-{top_words} частотных слов")
    plt.xlabel("слова", horizontalalignment="center")
    plt.ylabel("частотность")
    plt.grid(linewidth=0.2)
