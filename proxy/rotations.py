class NoServersAvailableException(Exception):
    pass


class ServerRotation(object):

    def __init__(self, server_names, *args, **kwargs):
        self.server_names = server_names

    def pick(self, *args, **kwargs):
        raise NotImplementedError()


class RoundRobin(ServerRotation):

    def __init__(self, server_names, *args, **kwargs):
        super(RoundRobin, self).__init__(server_names, args, kwargs)
        self.current = 0

    def pick(self, *args, **kwargs):
        if len(self.server_names) == 0:
            raise NoServersAvailableException()

        if self.current >= len(self.server_names):
            self.current = 0

        server = self.server_names[self.current]
        self.current += 1
        return server