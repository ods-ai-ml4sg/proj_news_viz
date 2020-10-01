import matplotlib.pyplot as plt


def plot_metrics(
    range_topics: list = None,
    metric: list = None,
    title: str = None,
    fig_size: tuple = (8, 5),
    color: str = 'k',
    line_width: int = 3,
    marker: str = 'x',
) -> None:
    """
    plot any metricspip install

    Parameters
    ----------
    range_topics: list
        list range topics, like `[20, 25, 30, 35, 40]`
    metric : list
        value metric in the list
    title : string
        plot title. at default title start from 'метрика: [here your words]'
    fig_size: tuple (default = (10,5))
        figsize figure
    color: string (default = 'k')
        color line
    line_width : int (default = 3)
        line width
    marker : string (default = 'x')
        line marker
    """

    plt.figure(figsize=fig_size)
    plt.plot(range_topics, metric, color=color, linewidth=line_width, marker=marker)

    ax = plt.gca()
    ax.set_xticks(range_topics)
    plt.grid()
    plt.title(f'метрика: {title}')
    plt.ylabel(title)
    plt.xlabel('к-ство топиков')
