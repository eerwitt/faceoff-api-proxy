class UserFinder(object):
    """
    This class should be extended if you are interested in authenticating your endpoint against users.
    """
    def __init__(self, **kwargs):
        """
        This init is super generic and takes in any kwargs parameters.  You can tighten this up in your implementation
        """
        for x in kwargs:
            setattr(self, x, kwargs[x])

    def find(self, **kwargs):
        """
        This find method should find a dictionary for the user find by the kwargs passed in.  This dictionary should,
        at minimum, have an 'id' entry.  If there is no User, return None.
        """
        return None


class MockUserFinder(UserFinder):
    def find(self, **kwargs):
        user_id = kwargs.get('id')
        if user_id is None:
            user_id = 123
        return {"id": user_id,
                "device-ids": ["ipad-xyz", "iphone-abc", "android-foo"],
                "facebook-id": "31337",
                "full-name": "Nick Vlku"}
