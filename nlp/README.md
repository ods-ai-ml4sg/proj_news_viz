news_viz
--------

```
├── config                          <- config files
│       └── ...
│
├── data
│   ├── external                    <- Data from third party sources.
│   ├── interim                     <- Intermediate data that has been transformed.
│   ├── processed                   <- The final, canonical data sets for modeling.
│   └── raw                         <- The original, immutable data dump.
│
├── experiments                     <- Some experiments
│   ├── analtsis_sources
│   │   └── ...
│   │── topic_models
│   │   ├── gensim
│   |   ├── bigartm
│   |   ├── cor_ex
│   |   ├── guided_lda
│   |   ├── sklearn
│   |   └── topsbm        
│
├── models                          <- Trained and serialized models, model predictions, or model summaries
│
├── news_viz                        <- Source code for use in this project         
│   ├── __init__.py                 <- makes src a Python module
│   ├── data                        <- scripts to process data
│   │   └── ...
│   ├── models                      <- scripts to our models
│   │   └── ...
│   ├── ner                         <- scripts to NER
│   │   └── ...
│   ├── visualization               <- scripts to any evaluation (custom metrics, visualization & etc.)
│   │   └── ... 
│   └── ...
│
├── notebooks                       <- Jupyter notebooks
│
├── references                      <- Data dictionaries, manuals, and all other explanatory materials.
│   ├── vt-cleaned_names.ipynb
│   ├── teacharticle
│   │   └── ...
│
├── requirements.txt                <- The requirements file for reproducing the analysis environment, e.g.
│                                       generated with `pip freeze > requirements.txt`
```
