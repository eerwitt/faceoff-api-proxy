from collections import OrderedDict


class FaceOffException(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message

    def to_dict(self):
        return OrderedDict({"error": self.error_code, "message": self.message})

    def __str__(self):
        return str(self.to_dict())