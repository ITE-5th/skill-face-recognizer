HEAD = 'head'
PUT = 'put'
POST = 'post'
DELETE = 'delete'


def get_http_request_type(msg, user_name='guest', target_name=None):
    msg_type = msg.__class__.__name__
    if msg_type == 'VqaMessage':
        return "/api/vqa", POST

    if msg_type == 'ImageToTextMessage':
        return "/api/itt", POST

    url = "/api/face-recognition/" + user_name

    if msg_type == 'RegisterFaceRecognitionMessage':
        return url, POST

    if msg_type == 'StartFaceRecognitionMessage':
        return url, HEAD

    if msg_type == 'FaceRecognitionMessage':
        return url, POST

    if target_name is not None:
        url += "/" + target_name

    if msg_type == 'RemovePersonMessage':
        return url, DELETE

    if msg_type == 'AddPersonMessage':
        return url, PUT

    if msg_type == 'EndAddPersonMessage':
        return url, POST


def request_http(url, method, payload):
    import requests
    response = None
    if method == POST:
        response = requests.post(url)
    if method == PUT:
        response = requests.put(url, data=payload)
    if method == DELETE:
        response = requests.delete(url)
    if method == HEAD:
        response = requests.head(url)
    return response
