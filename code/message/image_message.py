from .message import Message


class ImageMessage(Message):
    def __init__(self, image):
        super().__init__()
        self.image = image
