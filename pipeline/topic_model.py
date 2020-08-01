import numpy as np
import pandas as pd
import artm
import os


class TopicModelWrapperARTM:
    def __init__(self, dir_path, name_dataset, n_topics=50):
        # '/home/sv9t/repas/proj_news_viz/pipeline/data/artm/'
        self.dir_path = dir_path
        # 'gazeta'
        self.name_dataset = name_dataset
        self.vwpath = f"{dir_path}/vwpath/{name_dataset}_input_bigartm.vw"
        self.model = None
        self.n_topics = n_topics

    # data, n_topics = 50
    def prepare_data(self, data):
        """
        data -- array of tokenized text
        """
        self.vwpath_dir = f"{self.dir_path}/vwpath/"
        if not os.path.exists(self.vwpath_dir):
            print("creating vw path...\n")
            os.makedirs(self.vwpath_dir)

        with open(self.vwpath, "w") as fp:
            for i, text in enumerate(data):
                fp.write("{} |default {}\n".format(i, text))

        self.batches_path = f"{self.dir_path}/batches/{self.name_dataset}"

        if not os.path.exists(self.batches_path):
            print("create folder...\n")
            os.makedirs(self.batches_path)

        self.batch_vectorizer = artm.BatchVectorizer(
            data_path=self.vwpath,
            data_format="vowpal_wabbit",
            target_folder=self.batches_path,
        )

        if not os.path.exists(f"{self.dir_path}/dicts/"):
            print("create folder...\n")
            os.makedirs(f"{self.dir_path}/dicts/")

    def init_model(self):
        dictionary = artm.Dictionary()
        dictionary.gather(data_path=self.batches_path)
        dictionary.filter(min_tf=10, max_df_rate=0.1)
        dictionary.save_text(f"{self.dir_path}/dicts/dict_{self.name_dataset}.txt")

        self.model = artm.ARTM(
            num_topics=self.n_topics, dictionary=dictionary, show_progress_bars=True
        )

        # scores
        self.model.scores.add(
            artm.PerplexityScore(name="PerplexityScore", dictionary=dictionary)
        )
        self.model.scores.add(artm.SparsityThetaScore(name="SparsityThetaScore"))
        self.model.scores.add(artm.SparsityPhiScore(name="SparsityPhiScore"))

        # regularizers
        self.model.regularizers.add(
            artm.SmoothSparsePhiRegularizer(name="SparsePhi", tau=-0.1)
        )
        self.model.regularizers.add(
            artm.SmoothSparseThetaRegularizer(name="SparseTheta", tau=-0.5)
        )
        self.model.regularizers.add(
            artm.DecorrelatorPhiRegularizer(name="DecorrelatorPhi", tau=1.5e5)
        )

    def fit(self):
        if self.model is None:
            self.init_model()
        self.model.fit_offline(
            batch_vectorizer=self.batch_vectorizer, num_collection_passes=50
        )

        sparsityTheta = self.model.score_tracker["SparsityThetaScore"].last_value
        sparsityPhi = self.model.score_tracker["SparsityPhiScore"].last_value
        perpl = self.model.score_tracker["PerplexityScore"].last_value

        print(f"\tSparsityThetaScore: {sparsityTheta}")
        print(f"\tSparsityPhiScore: {sparsityPhi}")
        print(f"\tPerplexityScore: {perpl}")

    def get_phi(self):
        assert not (self.model is None), "init and fit (or load) model first"
        phi = self.model.get_phi()
        phi["word"] = phi.index
        return phi

    def print_top_words(self):
        phi = self.get_phi()
        for topic in phi.columns:
            print(topic)
            top_words = (
                phi.sort_values(by=topic, ascending=False)["word"]
                .apply(lambda x: x[1])
                .values[:20]
            )
            print(top_words)
            print("==" * 5)

    def save_model(self, path):
        self.model.save(path)

    def load_model(self, path):
        if self.model is None:
            self.init_model()
        self.model.load(path)

    def transform(self):
        assert not (self.model is None), "init and fit (or load) model first"
        theta = self.model.transform(batch_vectorizer=self.batch_vectorizer)
        theta = theta.T
        return theta
