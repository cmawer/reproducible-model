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

methods = dict(logistic=LogisticRegression,
               linear_regression=LinearRegression,
               xgboost=xgboost.XGBClassifier)

train_model_kwargs = ["split_data", "params", "fit", "compile"]


def split_data(X, y, train_size=1, test_size=0, validate_size=0, random_state=24, save_split_prefix=None):

    if y is not None:
        assert len(X) == len(y)
        include_y = True
    else:
        y = [0] * len(X)
        include_y = False
    if train_size + test_size + validate_size == 1:
        prop = True
    elif train_size + test_size + validate_size == len(X):
        prop = False
    else:
        raise ValueError("train_size + test_size + validate_size "
                         "must equal 1 or equal the number of rows in the dataset")

    if prop:
        train_size = int(np.round(train_size * len(X)))
        validate_size = int(np.round(validate_size * len(X)))
        test_size = int(len(X) - train_size - validate_size)

    if train_size == 1:
        X_train, y_train = X, y
    else:
        X_train, X_remain, y_train, y_remain = sklearn.model_selection.train_test_split(X, y, train_size=train_size,
                                                                                        random_state=random_state)

        X_validate, X_test, y_validate, y_test = sklearn.model_selection.train_test_split(X_remain, y_remain,
                                                                                          test_size=test_size,
                                                                                          random_state=random_state+1)
    print(type(X_train))
    X = dict(train=X_train)
    y = dict(train=y_train)

    if len(X_test) > 0:
        X["test"] = X_test
        y["test"] = y_test
    if len(X_validate) > 0:
        X["validate"] = X_validate
        y["validate"] = y_validate

    if save_split_prefix is not None:
        for split in X:
            pd.DataFrame(X[split]).to_csv("%s-%s-features.csv" % (save_split_prefix, split))
            if include_y:
                pd.DataFrame(y[split]).to_csv("%s-%s-targets.csv" % (save_split_prefix, split))

            logger.info("X_%s and y_%s saved to %s-%s-features.csv and %s-%s-targets.csv",
                        split, split,
                        save_split_prefix, split,
                        save_split_prefix, split)

    if not include_y:
        y = dict(train=None)

    return X, y


def train_model(df, method=None, save_tmo=None, **kwargs):

    assert method in methods.keys()

    if "choose_features" in kwargs:
        X = choose_features(df, **kwargs["choose_features"])
    else:
        X = df

    if "get_target" in kwargs:
        y = get_target(df, **kwargs["get_target"])
    else:
        y = None

    kwargs = fillin_kwargs(train_model_kwargs, kwargs)

    X, y = split_data(X, y, **kwargs["split_data"])

    model = methods[method](**kwargs["params"])

    if "validate" in X and "validate" in y:
        kwargs["fit"]["eval_set"] = [(X["validate"], y["validate"])]

    with Timer("model training", logger) as t:
        model.fit(X["train"], y["train"], **kwargs["fit"])

    if save_tmo is not None:
        with open(save_tmo, "wb") as f:
            pickle.dump(model, f)
        logger.info("Trained model object saved to %s", save_tmo)

    return model


def run_training(args):
    with open(args.config, "r") as f:
        config = yaml.load(f)

    if args.csv is not None:
        df = load_data(how="csv", csv=dict(path=args.csv))
    elif "load_data" in config:
        df = load_data(**config["load_data"])
    else:
        raise ValueError("Path to CSV for input data must be provided through --csv or "
                         "'load_data' configuration must exist in config file")

    tmo = train_model(df, **config["train_model"])

    if args.save is not None:
        with open(args.save, "wb") as f:
            pickle.dump(tmo, f)
        logger.info("Trained model object saved to %s", args.save)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train model")
    parser.add_argument('--config', help='path to yaml file with configurations')
    parser.add_argumemt('--csv', default=None, help="Path to CSV for input to model training")
    parser.add_argument('--save', default=None, help='Path to where the dataset should be saved to (optional')

    args = parser.parse_args()

    run_training(args)

