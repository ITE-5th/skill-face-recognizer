import base64
import time

import picamera


class Camera:

    def __init__(self, width=800, height=600, vflip=True, hflip=True):
        self.vflip = vflip
        self.hflip = hflip
        self.resolution = (width, height)

    def take_image(self, face_count=0):
        import os

        temp_dir = './temp/'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        file_name = temp_dir + time.strftime("%Y%m%d-%H%M%S") + '.jpg'

        with picamera.PiCamera() as camera:
            camera.vflip = self.vflip
            camera.hflip = self.hflip
            camera.resolution = self.resolution
            camera.capture(file_name)
        with open(file_name, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        if face_count > 0:
            return encoded_string, file_name if self.check_faces(file_name=file_name, faces_count=face_count) else -1
        # with open("../Image.jpg", "rb") as image_file:
        #     encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string, file_name

    def check_faces(self, file_name='./temp/Image.jpg', faces_count=1):
        import dlib
        from skimage import io
        print('analysing faces count')
        detector = dlib.get_frontal_face_detector()
        image = io.imread(file_name)
        rects = detector(image, 1)
        has_one_face = len(rects) == faces_count
        print(has_one_face)
        return has_one_face

if __name__ == '__main__':
    c = Camera(width=800, height=600)
    for i in range(10):
        print('taking photo')
        time.sleep(1)
        x = c.take_image()
        if x == -1:
            print('Sorry,Please Take a new Image.')
