from .message import Message


class ImageMessage(Message):
    def __init__(self, image=None, user_name=None):
        super().__init__(user_name)
        self.image = image
