import requests


class Client(object):
    def __init__(self, token):
        self.session = requests.Session()
        self.base_uri = 'https://api.telegram.org/bot' + token

    def send_message(self, chat_id, text, mode):
        self.session.post(url=self.base_uri + '/sendMessage',
                          json={
                             'chat_id': chat_id,
                             'text': text,
                              'disable_web_page_preview': True,
                              'parse_mode' : mode
                          })