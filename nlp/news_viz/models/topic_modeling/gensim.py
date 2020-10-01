from datetime import datetime
from gensim.models import CoherenceModel, LdaMulticore


def fit_tm_gensim(
    corpus: 'gensim.corpus' = None,
    dictionary: 'Dictionary' = None,
    text: list = None,
    range_topics: list = None,
    passes: int = 10,
    per_word_topics: bool = True,
) -> (list, list, list):
    """
    fit topic modeling model gensim, multicore (using LdaMulticore)
    
    Parameters
    ----------
    corpus : 'gensim.corpus' aka {iterable of list of (int, float), scipy.sparse.csc}
        Stream of document vectors or sparse matrix of shape (`num_terms`, `num_documents`)
    dictionary: 'Dictionary' aka {dict of (int, str),  :class:`gensim.corpora.dictionary.Dictionary`}
        Mapping from word IDs to words. It is used to determine the vocabulary size,
        as well as for debugging and topic printing.
    text : list
        list text tokens like text at `corpora.Dictionary`
    range_topics: list
        list range topics, like `[20, 25, 30, 35, 40]`
    passes: int (default = 10)
        number of passes through the corpus during training
    per_word_topics : bool (default = True)
        if True, the model also computes a list of topics, sorted in descending order of most likely
        topics for each word, along with their phi values multiplied by the feature length (i.e. word count)
    Returns
    -------
    meta_model : dict
        meta model fitted model
        with next items: model, coherence, perplexity, time
    """

    meta_model = {}

    for num_topic in range_topics:
        print(f'#topic {num_topic} ..........')
        time_start = datetime.now()

        # fit models TM
        model_gensim = LdaMulticore(
            corpus=corpus, id2word=dictionary, num_topics=num_topic, passes=passes, per_word_topics=True
        )

        # evaluation
        # coherence
        coherence_model = CoherenceModel(model=model_gensim, texts=text, dictionary=dictionary, coherence='c_v')
        coherence_value = coherence_model.get_coherence()
        print(f'\tcoherence score: {coherence_value}')

        # perplexity
        perplexity_value = model_gensim.log_perplexity(corpus)
        print(f'\tperplexity score: {perplexity_value}')

        # time
        time_end = datetime.now() - time_start
        print(f'\n\ttime: {time_end}')

        sec = time_end.seconds
        hours = sec // 3600
        minutes = (sec // 60) - (hours * 60)

        meta_model[num_topic] = {
            'model': model_gensim,
            'coherence': coherence_value,
            'perplexity': perplexity_value,
            'time_fit': {'hours': hours, 'min': minutes, 'sec': sec},
        }

    return meta_model
