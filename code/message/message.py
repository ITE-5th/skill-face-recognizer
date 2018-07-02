class Message:
    def __init__(self, user_name=None):
        self._type = self.__class__.__name__
        self.user_name = user_name
        # pass
