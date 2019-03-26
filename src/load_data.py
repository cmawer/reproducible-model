import logging
import argparse
import yaml
import os
import subprocess
import re
import boto3
import sqlalchemy
import pandas as pd

logger = logging.getLogger(__name__)


def ifin(param, dictionary, alt=None):

    assert type(dictionary) == dict
    if param in dictionary:
        return dictionary[param]
    else:
        return alt


def copy_file_from_s3(path, s3path, s3=None):
    if s3 is None:
        s3 = boto3.resource("s3")
    regex = r"s3://([\w._-]+)/([\w./_-]+)"

    m = re.match(regex, s3path)
    s3bucket = m.group(1)
    s3path = m.group(2)

    bucket = s3.Bucket(s3bucket)

    s3path = os.path.join(s3path, path)

    bucket.download_file(s3path, path)


def copy_files_from_s3(s3path, destpath):
    s3path = [s3path] if type(s3path) != list else s3path
    destpath = [destpath] if type(destpath) != list else destpath

    assert len(s3path) == len(destpath)

    for s3p, destp in zip(s3path, destpath):
        command = "aws s3 --recursive cp {s3path} {destpath}".format(s3path=s3p, destpath=destp)
        subprocess.check_output(command.split())


def format_sql(sql, replace_sqlvar=None, replace_var=None, python=True):
    if replace_sqlvar is not None:
        for var in replace_sqlvar:
            sql = sql.replace("${var:%s}" % var, replace_sqlvar[var])

    if replace_var is not None:
        sql = sql.format(**replace_var)

    if python:
        sql = sql.replace("%", "%%")

    return sql


def load_sql(path_to_sql, load_comments=False, replace_sqlvar=None, replace_var=None, python=True):
    sql = ""
    with open(path_to_sql, "r") as f:
        for line in f.readlines():
            if not load_comments and not line.startswith("--"):
                sql += line

    sql = format_sql(replace_sqlvar=replace_sqlvar, replace_var=replace_var, python=python)

    return sql


def create_connection(host='127.0.0.1', database="", sqltype="mysql+pymysql", port=3308,
                      user_env="amazonRDS_user", password_env="amazonRDS_pw",
                      username=None, password=None, dbconfig=None):

    if dbconfig is not None:
        with open(args.dbconfig, "r") as f:
            db = yaml.load(f)

        host = db["host"]
        database = ifin("dbname", db, "")
        sqltype = ifin("type", db, sqltype)
        port = db["port"]
        user_env = db["user_env"]
        password_env = db["password_env"]

    username = os.environ.get(user_env) if username is None else username
    password = os.environ.get(password_env) if password is None else password

    engine_string = "{sqltype}://{username}:{password}@{host}:{port}/{database}"
    engine_string = engine_string.format(sqltype=sqltype, username=username,
                                         password=password, host=host, port=port, database=database)
    conn = sqlalchemy.create_engine(engine_string)

    return conn


def query_data(sql=None, path_to_sql=None, dbconfig="config/dbconfig.yml", conn=None,
               load_comments=False, replace_sqlvar=None, replace_var=None, python=True):
    if sql is None and path_to_sql is not None:
        sql = load_sql(path_to_sql,
                       load_comments=load_comments,
                       replace_sqlvar=replace_sqlvar,
                       replace_var=replace_var,
                       python=python)
    elif sql is not None:
        sql = format_sql(sql,
                         replace_sqlvar=replace_sqlvar,
                         replace_var=replace_var,
                         python=python)
    else:
        raise ValueError("Only sql or path_to_sql should be provided")

    if conn is None:
        conn = create_connection(dbconfig=dbconfig)

    df = pd.read_sql(sql, con=conn)

    logger.info("Dataframe with %i rows loaded from query", len(df))

    return df


def read_csv(path, **kwargs):

    if "usecols" in kwargs:
        logging.debug("Columns being read from csv: %s", ",".join(kwargs["usecols"]))
    df = pd.read_csv(path, **kwargs)

    logger.info("Dataframe with %i rows loaded from %s", len(df), path)

    return df


def load_data(how, query=None, csv=None):
    """

    Args:
        how: How to load data. Options are one of remaining keyword args (e.g. query, read_csv)
        query: Dictionary of inputs to `query_data()`, None if how="csv"
        csv:  Dictionary of inputs to `read_csv()`, None if how="query"

    Returns: Pandas dataframe

    """

    if how.lower() == "query":
        query = {} if query is None else query
        data = query_data(**query)
    elif how.lower() == "csv":
        if csv is None or "path" not in csv:
            raise ValueError("csv['path'] must exist be provided")
        data = read_csv(**csv)
    else:
        raise ValueError("how must be given as 'query' or 'csv'")
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--config', help='path to yaml file with configurations')

    parser.add_argument('--save', default=None, help='Path to where the dataset should be saved to (optional')

    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = yaml.load(f)

    df = load_data(**config["load_data"])

    if args.save is not None:
        df.to_csv(args.save)
