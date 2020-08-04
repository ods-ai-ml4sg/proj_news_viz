import luigi
import configparser
import sys
import os
import logging
import pandas as pd
from preprocessing_tools import clean_text, lemmatize
import joblib
import topic_model

# TODO: set default paths
# TODO: add docstrings


class PreprocessorTask(luigi.Task):
    # input_path = luigi.Parameter("./data/raw/")
    # output_path = luigi.Parameter()
    conf = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(PreprocessorTask, self).__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read(self.conf)
        self.input_path = self.config["common"]["raw_path"]
        self.output_path = self.config["preprocessor"]["output_path"]
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
    # input_path = luigi.Parameter()
    # output_path = luigi.Parameter()
    # classifier_path = luigi.Parameter()
    # ftransformer_path = luigi.Parameter()
    conf = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(RubricClassifierTask, self).__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read(self.conf)
        self.input_path = self.config["preprocessor"]["output_path"]
        self.output_path = self.config["classifier"]["output_path"]
        self.classifier_path = self.config["classifier"]["classifier_path"]
        self.ftransformer_path = self.config["classifier"]["ftransformer_path"]

        # TODO: check if is file
        self.fnames = os.listdir(self.input_path)

    def requires(self):
        return PreprocessorTask(conf=self.conf)

    def run(self):
        # TODO: add class to classname mapping
        model = joblib.load(self.classifier_path)
        feats_trnsfr = joblib.load(self.ftransformer_path)

        for fname in self.fnames:
            readpath = os.path.join(self.input_path, fname)
            writepath = os.path.join(self.output_path, fname)
            data = pd.read_csv(readpath, compression="gzip")
            feats = feats_trnsfr.transform(data["lemmatized"].values)
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


class TopicPredictorTask(luigi.Task):
    # --input_path_c= --input_path_l= --output_path= --model_path=
    # input_path_c = luigi.Parameter()
    # input_path_l = luigi.Parameter()
    # output_path = luigi.Parameter()
    # model_path = luigi.Parameter() # /path/to/model{1.bin}
    conf = luigi.Parameter()

    def __init__(self, *args, **kwargs):
        super(TopicPredictorTask, self).__init__(*args, **kwargs)
        self.config = configparser.ConfigParser()
        self.config.read(self.conf)
        self.input_path_c = self.config["classifier"]["output_path"]
        self.input_path_l = self.config["preprocessor"]["output_path"]
        self.output_path = self.config["topic"]["output_path"]
        self.model_path = self.config["topic"]["model_path"]
        self.dict_path = self.config["topic"]["dict_path"]

        # TODO: check if is file
        self.fnames = os.listdir(self.input_path_c)

    def requires(self):
        return RubricClassifierTask(conf=self.conf)

    def run(self):
        for fname in self.fnames:
            readpath_c = os.path.join(self.input_path_c, fname)
            readpath_l = os.path.join(self.input_path_l, fname)
            data_c = pd.read_csv(readpath_c, compression="gzip")
            data_l = pd.read_csv(readpath_l, compression="gzip")
            classes = data_c["rubric_preds"].unique()
            source_name = fname.split(".")[0]
            for cl in classes:
                tm = topic_model.TopicModelWrapperARTM(self.output_path, source_name)
                mask = data_c["rubric_preds"] == cl
                writepath = os.path.join(
                    self.output_path, source_name + str(cl) + ".csv.gz"
                )
                tm.load_model(self.model_path + str(cl) + ".bin", self.dict_path)
                tm.prepare_data(data_l[mask]["lemmatized"].values)
                theta = tm.transform()
                result = theta.merge(
                    data_c[mask].copy().reset_index()[["date"]],
                    left_index=True,
                    right_index=True,
                )

                result.to_csv(writepath, compression="gzip", index=False)

    def output(self):
        outputs = []
        for fname in self.fnames:
            readpath_c = os.path.join(self.input_path_c, fname)
            data_c = pd.read_csv(readpath_c, compression="gzip")
            classes = data_c["rubric_preds"].unique()
            for cl in classes:
                source_name = fname.split(".")[0]
                writepath = os.path.join(
                    self.output_path, source_name + str(cl) + ".csv.gz"
                )
                outputs.append(luigi.LocalTarget(writepath))
        return outputs


# TODO Pass raw path as input for all task then compute dependency path
