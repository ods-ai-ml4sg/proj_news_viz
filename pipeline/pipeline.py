import luigi
import configparser
import sys
import os
import logging
import pandas as pd
from preprocessing_tools import clean_text, lemmatize
import joblib
from rubric_classifier import make_feats

# from topic_extractor import apply_model

# TODO: set default paths
# TODO: add docstrings
# TODO: rename all tasks to *Task


class PreprocessorTask(luigi.Task):
    input_path = luigi.Parameter("./data/raw/")
    output_path = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(PreprocessorTask, self).__init__(*args, **kwargs)
        # TODO: check if is file
        self.fnames = os.listdir(self.input_path)

    def run(self):
        for fname in self.fnames:
            readpath = os.path.join(self.input_path, fname)
            writepath = os.path.join(self.output_path, fname)
            data = pd.read_csv(readpath, compression="gzip")
            data["cleaned_text"] = data["text"].apply(clean_text)
            data["lemmatized"] = data["cleaned_text"].apply(lemmatize)
            data[["date", "topics", "lemmatized"]].to_csv(
                writepath, index=False, compression="gzip"
            )

    def output(self):
        outputs = []
        for fname in self.fnames:
            writepath = os.path.join(self.output_path, fname)
            outputs.append(luigi.LocalTarget(writepath))
        return outputs


class RubricClassifierTask(luigi.Task):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    classifier_path = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(RubricClassifierTask, self).__init__(*args, **kwargs)
        # TODO: check if is file
        self.fnames = os.listdir(self.input_path)

    # fnames = os.listdir(input_path)

    def requires(self):
        return PreprocessorTask(output_path=self.input_path)

    def run(self):
        # TODO: add class to classname mapping
        model = joblib.load(self.classifier_path)
        for fname in self.fnames:
            readpath = os.path.join(self.input_path, fname)
            writepath = os.path.join(self.output_path, fname)
            data = pd.read_csv(readpath, compression="gzip")
            feats = make_feats(data["lemmatized"].values)
            preds = model.predict(feats)
            data["rubric_preds"] = preds
            data[["date", "rubric_preds"]].to_csv(
                writepath, index=False, compression="gzip"
            )

    def output(self):
        outputs = []
        for fname in self.fnames:
            writepath = os.path.join(self.output_path, fname)
            outputs.append(luigi.LocalTarget(writepath))
        return outputs


# DRAFT BELOW
class TopicPredictorTask(luigi.Task):
    input_path = luigi.Parameter()
    output_path = luigi.Parameter()
    model_path = luigi.Parameter()
    # fnames = os.listdir(input_path)
    # TODO: add config {class: n_topics}
    n_topics = luigi.IntParameter(10)

    def __init__(self, *args, **kwargs):
        super(TopicPredictorTask, self).__init__(*args, **kwargs)
        # TODO: check if is file
        self.fnames = os.listdir(self.input_path)

    def requires(self):
        return RubricClassifierTask(output_path=self.input_path)

    def run(self):
        for fname in self.fnames:
            readpath = os.path.join(self.input_path, fname)
            data = pd.read_csv(readpath, compression="gzip")
            classes = data["rubric_preds"].unique()
            for cl in classes:
                model = joblib.load(os.path.join(self.model_path, str(cl) + ".bin"))
                mask = data["rubric_preds"] == cl
                writepath = os.path.join(self.output_path, str(cl) + fname)
                model.apply_model(df=data[mask], n_topics=self.n_topics)
                preds = model.predict()
                preds.to_csv(writepath, compression="gzip")

    def output(self):
        outputs = []
        for fname in self.fnames:
            writepath = os.path.join(self.output_path, fname)
            outputs.append(luigi.LocalTarget(writepath))
        return outputs
