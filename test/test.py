import subprocess
import yaml
import logging
import os
import xmltodict
import argparse
import filecmp

dict_file_types = ["json", "xml", "yml", "yaml"]


def open_dictlike_file(fname):
    with open(fname, "r") as f:
        if fname.endswith("json"):
            fdict = yaml.load(f)
        elif fname.endswith("yaml") or fname.endswith("yml"):
            fdict = yaml.load(f)
        elif fname.endswith("xml"):
            fdict = xmltodict.parse(f.read())
        else:
            logging.warning("%s not a known dictionary-like file type", fname)
    return fdict


def compare_dict(dicta, dictb):

    mismatch_keys = []
    for k in dicta:
        if k in dictb:
            if type(dicta[k]) == dict:
                same, mismatch = compare_dict(dicta[k], dictb[k])
            else:
                same = (dicta[k] == dictb[k])
        else:
            same = False
        if not same:
           mismatch_keys.append(k)

    dicts_are_same = False if len(mismatch_keys) > 0 else True

    return dicts_are_same, mismatch_keys


def run_tests(args=None, config_path=None):
    """ Runs a provided command and compares the files produced to those that are expected.

    Test is configured by a yaml file that has the following format:

    ```yaml
    test_name:
        command: <command that should be run to produce the files being tested>
        true_dir: <path to directory holding expected outputs of command>
        test_dir: <path to where the command saves the outputs produced>
        files_to_compare:
            - <list of files that should be produced into the test directory when the>
            - <command is run and should already exist in the true directory for comparison>
    ```


    Args:
        args: If fed args from argparse, args.path should exist and give the path to the testing configuration file
        config_path: Path to the testing configuration file

    Returns:
        all_passed (bool): True if all tests pass, False if not
        results (dict): Dictionary of tests and their corresponding list of files that did not match

    """

    if args is not None:
        config_path = args.path

    with open(config_path, "r") as f:
        tests = yaml.load(f)

    all_passed = True
    for test in tests:
        testconf = tests[test]

        true_dir, test_dir = testconf["true_dir"], testconf["test_dir"]

        no_true_to_compare = []
        for file in testconf["files_to_compare"]:
            test_file = os.path.join(test_dir, file)
            true_file = os.path.join(true_dir, file)

            # Remove test files if they have already been produced previously
            # Otherwise, your code may not actually be producing that file but the test will pass
            if os.path.exists(test_file):
                os.remove(test_file)
                logging.debug("%s removed to be recreated", test_file)

            # Check if the file actually exists in the true directory
            if not os.path.exists(true_file):
                logging.warning("%s does not exist to be compared to", true_file)
                no_true_to_compare.append(file)

        # Run command being tested
        subprocess.check_output(testconf["command"].split())

        # Compare files that were produced that are not versions of dictionaries where order is not deterministic
        files_to_compare = [
            f for f in testconf["files_to_compare"]
            if f.split('.')[-1] not in dict_file_types and f not in no_true_to_compare
        ]

        match, mismatch, errors = filecmp.cmpfiles(true_dir, test_dir,
                                                   files_to_compare, shallow=True)

        # Compare files that are versions of dictionaries where order is not deterministic
        dicts_to_compare = [
            f for f in testconf["files_to_compare"]
            if f.split('.')[-1] in dict_file_types and f not in no_true_to_compare
        ]

        dict_mismatch = []
        for fname in dicts_to_compare:
            true_dict = open_dictlike_file(os.path.join(true_dir, fname))
            test_dict = open_dictlike_file(os.path.join(test_dir, fname))

            dicts_are_same, mismatch_keys = compare_dict(true_dict, test_dict)
            if not dicts_are_same:
                dict_mismatch.append(fname)
                with open(os.path.join(true_dir, "true_%s.yml") % fname, "w") as f:
                    yaml.dump(true_dict, f)
                with open(os.path.join(test_dir, "test_%s.yml") % fname, "w") as f:
                    yaml.dump(test_dict, f)
                logging.warning("%s keys are not the same", ",".join(mismatch_keys))

        mismatch += no_true_to_compare
        mismatch += dict_mismatch

        if len(mismatch) > 0:
                logging.warning("%s file(s) does not match or did not exist, %s test FAILED",
                                ", ".join(mismatch), test)
                all_passed = False
        else:
            logging.warning("%s test PASSED" % test)

    if all_passed:
        logging.warning("Success, all tests passed!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test whether the expected outputs are produced")
    parser.add_argument("--path", default="test/test_config.yml", help="Path to the test configuration file")
    args = parser.parse_args()
    run_tests(config_path=args.path)

import subprocess
import yaml
import logging
import os
import argparse
import filecmp
import logging.config
import xmltodict

dict_file_types = ["json", "xml", "yml", "yaml"]


def open_dictlike_file(fname):
    with open(fname, "r") as f:
        if fname.endswith("json"):
            fdict = yaml.load(f)
        elif fname.endswith("yaml") or fname.endswith("yml"):
            fdict = yaml.load(f)
        elif fname.endswith("xml"):
            fdict = xmltodict.parse(f.read())
        else:
            logging.warning("%s not a known dictionary-like file type", fname)
    return fdict


def compare_dict(dicta, dictb):

    mismatch_keys = []
    for k in dicta:
        if k in dictb:
            if type(dicta[k]) == dict:
                same, mismatch = compare_dict(dicta[k], dictb[k])
            else:
                same = (dicta[k] == dictb[k])
        else:
            same = False
        if not same:
           mismatch_keys.append(k)

    dicts_are_same = False if len(mismatch_keys) > 0 else True

    return dicts_are_same, mismatch_keys


def run_tests(args=None, config_path=None, logger=None):
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel("DEBUG")

    if args is not None:
        config_path = args.path

    with open(config_path, "r") as f:
        tests = yaml.load(f)

    all_passed = True
    results = {}
    for test in tests:
        testconf = tests[test]

        for file in testconf["files_to_compare"]:
            test_file = os.path.join(testconf["test_dir"], file)
            true_file = os.path.join(testconf["true_dir"], file)
            if os.path.exists(test_file):
                os.remove(test_file)
                logging.debug("%s removed to be recreated", test_file)
            if not os.path.exists(true_file):
                logging.warning("%s does not exist to be compared to", true_file)

        subprocess.check_output(testconf["command"].split())

        match, mismatch, errors = filecmp.cmpfiles(testconf["true_dir"], testconf["test_dir"],
                                                   testconf["files_to_compare"], shallow=True)
        for file in testconf["files_to_compare"]:
            test_file = os.path.join(testconf["test_dir"], file)
            if not os.path.exists(test_file):
                logging.warning("%s does not exist to be compared to", test_file)
                if file not in mismatch:
                    mismatch.append(file)

        if len(mismatch) > 0:
                logging.warning("%s file(s) does not match, %s test FAILED" % (", ".join(mismatch), test))
                all_passed = False
        else:
            logging.warning("%s test PASSED" % test)
        results[test] = mismatch

    if all_passed:
        logging.warning("Success, all tests passed!")

    return all_passed, results


if __name__ == '__main__':
    logging.config.fileConfig("config/logging/local.conf")
    logger = logging.getLogger(__name__)
    logger.setLevel("DEBUG")

    parser = argparse.ArgumentParser(description="Test whether the expected outputs are produced")
    parser.add_argument("--path", default="test/test_config.yml", help="Path to the test configuration file")
    args = parser.parse_args()
    run_tests(config_path=args.path, logger=logger)
