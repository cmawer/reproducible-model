import logging
import argparse
import yaml
import os
import subprocess
import re
import datetime

import pickle

import sklearn
import xgboost
import pandas as pd
import numpy as np

from src.load_data import load_data
from src.helpers import Timer, fillin_kwargs
from src.generate_features import choose_features, get_target
from sklearn.linear_model import LogisticRegression, LinearRegression

logger = logging.getLogger(__name__)

score_model_kwargs = ["predict"]


def score_model(df, path_to_tmo, save_scores=None, **kwargs):

    with open(path_to_tmo, "rb") as f:
        model = pickle.load(f)

    kwargs = fillin_kwargs(score_model_kwargs, kwargs)
    with Timer("scoring", logger):
        y_predicted = model.predict(df.values, **kwargs["predict"])

    if save_scores is not None:
        pd.DataFrame(y_predicted).to_csv(save_scores,  index=False)

    return y_predicted


def run_scoring(args):
    with open(args.config, "r") as f:
        config = yaml.load(f)

    if args.csv is not None:
        df = load_data(how="csv", csv=dict(path=args.csv))
    elif "load_data" in config:
        df = load_data(**config["load_data"])
    else:
        raise ValueError("Path to CSV for input data must be provided through --csv or "
                         "'load_data' configuration must exist in config file")

    y_predicted = score_model(df, **config["score_model"])

    if args.save is not None:
        pd.DataFrame(y_predicted).to_csv(args.save, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Score model")
    parser.add_argument('--config', help='path to yaml file with configurations')
    parser.add_argumemt('--csv', default=None, help="Path to CSV for input to model scoring")
    parser.add_argument('--save', default=None, help='Path to where the scores should be saved to (optional)')

    args = parser.parse_args()

    run_scoring(args)

