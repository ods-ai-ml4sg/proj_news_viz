import matplotlib.pyplot as plt


def plotFrequencyWords(vocab: list = None,
                       top_words: int = 30,
                       plt_background: str = None) -> None:
    """
    plot token frequency
    Parameters
    ----------
        vocab: list (defauld = None)
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
