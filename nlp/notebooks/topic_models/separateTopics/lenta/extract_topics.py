import argparse
import os
import re

import artm
import pandas as pd

import preprocessing_tools as pr
from cleanedNames import KeyProc


def preprocess_text(dir_path: str = '',
                    name_dataset: str = '') -> pd.DataFrame:
    """
    Preprocess text for topic modelling.

    Args:
        dir_path: path to directory with data
        name_dataset: name of the dataset

    Returns:
        processed dataframe

    """
    data = pd.read_csv(f'{dir_path}/{name_dataset}.csv.bz2')
    data = data[data.text != 'text']

    # get dates
    data['date_raw'] = data['url'].apply(re.compile('(\d{4})/(\d{2})/(\d{2})').findall)
    data['year'] = data['date_raw'].apply(lambda x: int(x[0][0]))
    data['month'] = data['date_raw'].apply(lambda x: int(x[0][1]))

    # clean text
    data.text = data.text.apply(pr.clean_text)
    cn = KeyProc()
    data.text = data.text.apply(cn.replaceKeywords)

    # lemmatization
    data['lemmatized_text'] = data.text.apply(pr.lemmatization)

    # add docID
    data['docID'] = list(range(data.shape[0]))
    data = data[['docID', 'year', 'month', 'lemmatized_text']]

    return data


def apply_model(df: pd.DataFrame = None,
                dir_path: str = None,
                name_dataset: str = '',
                n_topics: int = 20) -> pd.DataFrame:
    """
    Apply artm model


    Args:
        df: processed dataframe. If not provided, tries to read the processed
        dataframe from the disk
        dir_path: path to directory with data
        name_dataset: name of the dataset
        n_topics: number of topics to extract

    Returns:
        dataframe with topics

    """
    if df is not None:
        pass
    elif dir_path:
        df = pd.read_csv(f'{dir_path}/{name_dataset}.csv.bz2')
    else:
        raise ValueError('Define either dataframe or path')

    # prepare
    vwpath = f'{dir_path}/vwpath/{name_dataset}_input_bigartm.vw'

    if not os.path.exists(f'{dir_path}/vwpath/'):
        print('create folder...\n')
        os.makedirs(f'{dir_path}/vwpath/')

    with open(vwpath, 'w', encoding='utf-8') as fp:
        for text, did in df[['lemmatized_text', 'docID']].values:
            fp.write('{} | {}\n'.format(did, ' '.join(text)))

    id_date = df[['docID', 'year', 'month']].copy()

    # collect batches and collect the dictionary
    batches_path = f'{dir_path}/batches/{name_dataset}'

    if not os.path.exists(batches_path):
        print('create folder...\n')
        os.makedirs(batches_path)

    batch_vectorizer = artm.BatchVectorizer(data_path=vwpath,
                                            data_format='vowpal_wabbit',
                                            target_folder=batches_path)

    dictionary = artm.Dictionary()
    dictionary.gather(data_path=batches_path)
    dictionary.filter(min_tf=10, max_df_rate=0.1)
    dictionary.save_text(f'data/dicts/dict_{name_dataset}.txt')

    # train the model
    model = artm.ARTM(num_topics=n_topics, dictionary=dictionary, show_progress_bars=True)

    # scores
    model.scores.add(artm.PerplexityScore(name='PerplexityScore', dictionary=dictionary))
    model.scores.add(artm.SparsityThetaScore(name='SparsityThetaScore'))
    model.scores.add(artm.SparsityPhiScore(name='SparsityPhiScore'))

    # regularizers
    model.regularizers.add(artm.SmoothSparsePhiRegularizer(name='SparsePhi', tau=-0.1))
    model.regularizers.add(artm.SmoothSparseThetaRegularizer(name='SparseTheta', tau=-0.5))
    model.regularizers.add(artm.DecorrelatorPhiRegularizer(name='DecorrelatorPhi', tau=1.5e+5))

    model.fit_offline(batch_vectorizer=batch_vectorizer, num_collection_passes=50)

    sparsityTheta = model.score_tracker['SparsityThetaScore'].last_value
    sparsityPhi = model.score_tracker['SparsityPhiScore'].last_value
    perpl = model.score_tracker['PerplexityScore'].last_value

    print(f'\tSparsityThetaScore: {sparsityTheta}')
    print(f'\tSparsityPhiScore: {sparsityPhi}')
    print(f'\tPerplexityScore: {perpl}')

    phi = model.get_phi()
    phi['word'] = phi.index

    # get topics-docs matrix
    theta = model.transform(batch_vectorizer=batch_vectorizer)
    theta = theta.T
    joined = id_date.join(theta)
    if not os.path.exists(f'./{dir_path}/topicsProbability/'):
        print('create folder...\n')
        os.makedirs(f'./{dir_path}/topicsProbability/')
    joined.to_csv(f'''./{dir_path}/topicsProbability/{'-'.join(name_dataset.split('.'))}.csv''', index=False)

    return joined


if __name__ == '__main__':
    """
    Example of usage:
    >>> python extract_topics.py --name_dataset=economic --n_topics=10

    """

    parser = argparse.ArgumentParser(description="Tematizer")
    parser.add_argument("--dir_path", help="path to directory", type=str,
                        default='')
    parser.add_argument("--name_dataset", help="name of dataset", type=str, default='economic')
    parser.add_argument("--n_topics", help="number of topics", type=int, default=2)

    args = parser.parse_args()
    df = preprocess_text(args.dir_path, args.name_dataset)

    joined = apply_model(df=df, name_dataset=args.name_dataset, n_topics=args.n_topics)
