import datetime


def fillin_kwargs(keywords, kwargs):
    keywords = [keywords] if type(keywords) != list else keywords
    for keyword in keywords:
        if keyword not in kwargs:
            kwargs[keyword] = {}
    return kwargs

class Timer:
    def __init__(self, function, logger):
        self.logger = logger
        self.function = function

    def __enter__(self):
        self.start = datetime.datetime.now()

        return self

    def __exit__(self, *args):
        self.end = datetime.datetime.now()
        self.interval = self.end - self.start
        self.logger.info("%s took %0.2f seconds", self.function, self.interval.total_seconds())