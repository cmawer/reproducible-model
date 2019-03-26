import argparse
import logging
import logging.config

from test.test import run_tests
from src.score_model import run_scoring
from src.generate_features import run_features
from src.train_model import run_training


if __name__ == '__main__':

    logging.config.fileConfig("config/logging/local.conf")
    logger = logging.getLogger("run")
    parser = argparse.ArgumentParser(description="Run components of the model source code")
    subparsers = parser.add_subparsers()

    # FEATURE subparser
    sb_features = subparsers.add_parser("generate_features", description="Generate features")
    sb_features.add_argument('--config', help='path to yaml file with configurations')
    sb_features.add_argument('--csv', default=None, help="Path to CSV for input to model scoreing")
    sb_features.add_argument('--save', default=None, help='Path to where the dataset should be saved to (optional')
    sb_features.set_defaults(func=run_features)

    # TRAIN subparser
    sb_train = subparsers.add_parser("train_model", description="Train model")
    sb_train.add_argument('--config', help='path to yaml file with configurations')
    sb_train.add_argument('--csv', default=None, help="Path to CSV for input to model training")
    sb_train.add_argument('--save', default=None, help='Path to where the dataset should be saved to (optional')
    sb_train.set_defaults(func=run_training)

    # SCORE subparser
    sb_score = subparsers.add_parser("score_model", description="Score model")
    sb_score.add_argument('--config', help='path to yaml file with configurations')
    sb_score.add_argument('--csv', default=None, help="Path to CSV for input to model scoring")
    sb_score.add_argument('--save', default=None, help='Path to where the dataset should be saved to (optional')
    sb_score.set_defaults(func=run_scoring)

    # TEST subparser
    sb_test = subparsers.add_parser("test", description="Test whether the expected outputs are produced")
    sb_test.add_argument("--path", default="test/test_config.yml", help="Path to the test configuration file")
    sb_test.set_defaults(func=run_tests)

    args = parser.parse_args()
    args.func(args)
