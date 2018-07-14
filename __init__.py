import socket
import sys
import traceback

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler
from mycroft.util.log import LOG

# TODO: Make sure "." before module name is not missing
from .code.message.add_person_message import AddPersonMessage
from .code.message.end_add_person_message import EndAddPersonMessage
from .code.message.face_recognition_message import FaceRecognitionMessage
from .code.message.remove_person_message import RemovePersonMessage
from .code.misc.camera import Camera
from .code.misc.http.api import get_http_request_type, request_http
from .code.misc.receiver import Receiver
from .code.misc.sender import Sender
from .default_config import DefaultConfig

LOG.warning('Running Skill Face Recognizer On Python ' + sys.version)

try:
    import picamera
    from googletrans import Translator
except ImportError:
    # re-install yourself
    from msm import MycroftSkillsManager

    msm = MycroftSkillsManager()
    msm.install("https://github.com/ITE-5th/skill-face-recognizer")


class FaceRecognizerSkill(MycroftSkill):
    def __init__(self):
        super(FaceRecognizerSkill, self).__init__(name="FaceRecognizerSkill")
        LOG.warning('Running Skill Face Recognizer')

        # if "server_url" not in self.settings:
        #     self.settings["server_url"] = DefaultConfig.server_url
        self.user_name = None
        self.socket = None
        self.receiver = None
        self.sender = None
        self.port = None
        self.host = None
        self.images_count = 0
        self.camera = Camera(width=800, height=600)
        self.connection_type = DefaultConfig.connection_type
        self.new_person = None
        self.connect()

    def connect(self):
        try:
            self.connection_type = self.settings.get("connection_type", DefaultConfig.connection_type)
            self.host = self.settings.get("server_url", DefaultConfig.server_url)
            self.port = DefaultConfig.FACE_RECOGNITION_PORT
            self.user_name = self.settings.get('user_name', DefaultConfig.user_name)
            if self.connection_type == 'socket':
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                LOG.info('connecting to server:' + self.host + ' : ' + str(self.port))
                self.socket.settimeout(10)
                self.socket.connect((self.host, self.port))
                self.receiver = Receiver(self.socket, json=True)
                self.sender = Sender(self.socket, json=True)
                #
                LOG.info('connected to server:' + self.host + ' : ' + str(self.port))

        except Exception as e:
            LOG.warning(str(e))

    def send_recv(self, msg, user_name=DefaultConfig.user_name, target_name=None):
        if self.connection_type == 'http':
            url, method = get_http_request_type(msg, user_name, target_name)
            url = self.host + url
            return request_http(url, method, msg)
        else:
            self.ensure_send(msg)
            result = self.receiver.receive()
            return result

    def ensure_send(self, msg):
        retries = 3
        while retries > 0:
            try:
                retries -= 1
                self.sender.send(msg)
                break
            except Exception as e:
                if retries <= 0:
                    raise ConnectionError()
                self.connect()
                LOG.warning(str(e))
        return True

    @intent_handler(IntentBuilder("RecognizeIntent").require('Face'))
    def handle_recognize_intent(self):
        try:
            image, _ = self.camera.take_image()
            LOG.warning(str(self.user_name))
            msg = FaceRecognitionMessage(image, self.user_name)
            response = self.send_recv(msg)

            LOG.info(response)
            recognise_result = response.get('result')
            if recognise_result == '':
                self.speak_dialog("EmptyResult")
                return True
            result = self.handle_message(recognise_result)
            self.speak_dialog("RecogniseResult", result)

        except ConnectionError as e:
            self.speak_dialog('ConnectionError')
            return True

        except Exception as e:
            LOG.info('Something is wrong')
            LOG.info(str(e))
            LOG.info(str(traceback.format_exc()))
            self.speak_dialog("UnknownError")
            self.connect()
            return False
        return True

    @intent_handler(IntentBuilder("AddFaceIntent").require('Add').optionally('PName'))
    def add(self, message=''):
        try:

            person_name = message.data.get("PName", None) if message.data else None
            if person_name is None:
                self.speak_dialog('GetPersonName')
                person_name = self.get_person_name()

            self.speak_dialog("AddPeronStart", {'p_name': person_name})
            self.new_person = person_name

        except LookupError as e:
            self.speak_dialog('GetPersonNameError')

        except ConnectionError as e:
            self.speak_dialog('ConnectionError')

        except Exception as e:
            LOG.info('Something is wrong')
            LOG.info(str(e))
            LOG.info(str(traceback.format_exc()))
            self.speak_dialog("UnknownError")
            self.connect()
        return True

    @intent_handler(IntentBuilder("RecognizeFaceIntent").require('Remove').optionally('PName'))
    def remove(self, message):
        LOG.info(message.data)
        try:
            person_name = message.data.get("PName", None)
            if person_name is None:
                self.speak_dialog('GetPersonName')
                person_name = self.get_person_name()

            msg = RemovePersonMessage(person_name, self.user_name)
            result = self.send_recv(msg)
            LOG.info(result)

            if not result or result.get('result', DefaultConfig.ERROR) == DefaultConfig.ERROR:
                self.speak_dialog("RemoveError", {'p_name': person_name})
                return True
            self.speak_dialog("RemoveSuccess", {'p_name': person_name})

        except LookupError as e:
            self.speak_dialog('GetPersonNameError')

        except ConnectionError as e:
            self.speak_dialog('ConnectionError')

        except Exception as e:
            LOG.info('Something is wrong')
            LOG.info(str(e))
            LOG.info(str(traceback.format_exc()))
            self.speak_dialog("UnknownError")
            self.connect()
        return True

    @intent_handler(IntentBuilder("CaptureFaceIntent").require('Capture'))
    def capture(self, message):
        try:
            if self.new_person is None:
                self.speak('Adding new friend')
                self.add()
                return True
            image, _ = self.camera.take_image(1)
            if image is None:
                self.speak_dialog("PersonCountError")
                return True
            msg = AddPersonMessage(image, self.user_name)
            result = self.send_recv(msg)
            if not result or result.get('result', DefaultConfig.ERROR) == DefaultConfig.ERROR:
                self.speak_dialog("AddError", {'p_name': self.new_person})
                return True
            LOG.info(result)

            self.images_count += 1
            self.speak_dialog("AddSuccess", {'p_name': self.new_person, 'img_number': self.images_count})
            # END ADD
            if self.images_count >= DefaultConfig.MaxImagesCount:
                msg = EndAddPersonMessage(self.new_person, self.user_name)
                result = self.send_recv(msg)
                if not result:
                    self.speak_dialog("EndAddError", {'p_name': self.new_person})
                    return True
                LOG.info(result)
                self.images_count = 0
                self.speak_dialog("EndAddSuccess", {'p_name': self.new_person})
                self.new_person = None
        except LookupError as e:
            self.speak_dialog('GetPersonNameError')

        except ConnectionError as e:
            self.speak_dialog('ConnectionError')

        except Exception as e:
            LOG.info('Something is wrong')
            LOG.info(str(e))
            LOG.info(str(traceback.format_exc()))
            self.speak_dialog("UnknownError")
            self.connect()
        return True

    @staticmethod
    def handle_message(response):
        """
        converts server response to meaningful sentence
        :param response: string of people names includes unknown
        :return: dictionary contains sentence in result
        """
        unknown = 'Unknown'
        persons = response.split(',')
        unk_count = sum([x.split(' ').count(unknown) for i, x in enumerate(persons)])

        # remove Unknown
        persons = [x for i, x in enumerate(persons) if x.split(' ')[0] != unknown]
        for idx, person in enumerate(persons):
            person = person.split(' ')
            persons[idx] = person[0].replace('_', ' ').title()
            persons[idx] += ','
            # persons[idx] += ' With probability of {} Percent . '.format(person[1])

        if unk_count > 0:
            persons.append(str(unk_count) + ' Unknown ' + ('persons' if unk_count > 1 else 'person'))

        persons_count = len(persons)
        phrase = ''
        for i in range(persons_count):
            phrase += persons[i]
            phrase += ' and ' if i == persons_count - 2 and persons_count > 1 else ''
        return {'result': phrase}

    def stop(self):
        super(FaceRecognizerSkill, self).shutdown()
        LOG.info("Face Recognizer Skill CLOSED")
        if self.socket:
            self.socket.close()

    def get_person_name(self):
        phrase = self.get_phrase(lang='ar-AE')
        accepted_chars = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')
        translator = Translator()
        translated = translator.translate(phrase, dest='en')
        # translated_text = translated.text.replace('Al ', 'Al')
        # translated_text = ''.join(filter(lambda x: x in accepted_chars, translated_text))
        translated_phoneme = translated.extra_data['translation'][1][-1].replace('Al ', 'Al')
        translated_phoneme = ''.join(filter(lambda x: x in accepted_chars, translated_phoneme))
        # p_name = translated_text if len(phrase.split(' ')) == len(
        p_name = translated_phoneme
        return p_name

    @staticmethod
    def get_phrase(lang='en-US'):
        import speech_recognition as sr
        r = sr.Recognizer()

        with sr.Microphone() as source:
            print('recording...')
            audio = r.listen(source)
        print('fin recording...')

        try:
            text = r.recognize_google(audio, language=lang)
            print("Google Speech Recognition thinks you said " + text)

            if text is not None or text.strip() != "":
                return text
            raise LookupError()

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            raise LookupError()
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            raise LookupError()

    #  Deprecated because every message server checks if user is registered
    # def register_face(self):
    #     def has_error(message):
    #         if not message or message.get('result', DefaultConfig.ERROR) == DefaultConfig.ERROR:
    #             self.speak_dialog('RegisterError', {'user_name': self.user_name})
    #             return False
    #
    #     LOG.info("register face")
    #
    #     # START FACE MESSAGE
    #     msg = StartFaceRecognitionMessage(self.user_name)
    #     result = self.send_recv(msg)
    #
    #     if has_error(result):
    #         return False
    #
    #     LOG.info(result)
    #     self.speak_dialog("RegisterSuccess", {'user_name': self.user_name})
    #     return True


def create_skill():
    return FaceRecognizerSkill()
