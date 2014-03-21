__version__ = "0.1"


class _general_config(object):

    def __init__(self):
        # just for the sake of information
        self.instance = "Instance at %d" % self.__hash__()


_general_config = _general_config()

def general_config(): return _general_config