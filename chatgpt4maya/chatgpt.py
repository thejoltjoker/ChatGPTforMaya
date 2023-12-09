import json
import logging
import os
import sys
from pathlib import Path
from pprint import pprint

from chatgpt4maya import config

logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
# Load .env during development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Insert path to openai dependencies
sys.path.insert(0, str(Path(config.Config().get('OpenAI', 'OpenAILibraryPath')).resolve()))

# Import openai
try:
    from openai import OpenAI

    logging.info('Imported openai')
except Exception as e:
    logging.error(e)
    logging.error('openai package could not be imported')
    openai = None


class ChatGPT:
    def __init__(self, api_key=None, save=True):
        self.client = None

        # Get api key
        api_key = api_key if api_key else os.getenv('OPENAI_API_KEY')
        if api_key:
            # Set api key
            self.client = OpenAI(api_key=api_key)
        else:
            logging.error('No api key given/found')
            raise Exception('No api key given/found')

        self.model = 'gpt-3.5-turbo'
        self.system_message = {'role': 'system',
                               'content': 'Helpful assistant. '
                                          'Help with Autodesk Maya, python, mel, Maya expression.'}
        self.messages = [self.system_message]

        # Save history
        self.history = {}
        self.file = Path(config.config_path() / 'history.json')
        self.save = save

    def _save_conversation(self):
        data = []
        if self.file.is_file():
            with self.file.open('r') as read_file:
                data = json.load(read_file)

        with self.file.open('w') as write_file:
            data.append(self.history)
            json.dump(data, write_file)
        return self.file

    def _get_mock_response(self):
        """Send a request to httpbin"""
        # url = 'https://httpbin.org/json'
        # logging.info(f'Sending request to {url}')
        logging.info('Pretending to send request to openai')
        # res = urllib.request.urlopen(url)
        # res_body = res.get()
        # response = json.loads(res_body.decode("utf-8"))

        response = {'choices': [{'finish_reason': 'stop',
                                 'index': 0,
                                 'message': {'content': "Here's how to create a cube in Maya "
                                                        'using MEL:\n'
                                                        '\n'
                                                        '```\n'
                                                        'polyCube -w 1 -h 1 -d 1;\n'
                                                        '```\n'
                                                        '\n'
                                                        "And here's how to create a cube in Maya "
                                                        'using Python:\n'
                                                        '\n'
                                                        '```\n'
                                                        'import maya.cmds as cmds\n'
                                                        '\n'
                                                        'cmds.polyCube(w=1, h=1, d=1)\n'
                                                        '```\n'
                                                        '\n'
                                                        'Both of these commands will create a '
                                                        'cube with a width, height, and depth of '
                                                        '1 unit. You can adjust the values to '
                                                        'create a cube of any size.',
                                             'role': 'assistant'}}],
                    'created': 1682008110,
                    'id': 'chatcmpl-77RR0y31Q4Rp8I2q6xFQdyIN86hkM',
                    'model': 'gpt-3.5-turbo-0301',
                    'object': 'chat.completion',
                    'usage': {'completion_tokens': 106,
                              'prompt_tokens': 36,
                              'total_tokens': 142}}

        return response

    def _get_response(self):
        """
        Generate a chat response using the GPT-3.5 model and the previous messages.

        Returns:
            dict: The response generated by the GPT-3.5 model.
        """
        response = {}
        try:
            # Create a chat completion using OpenAI's API
            response = self.client.chat.completions.create(model=self.model,
                                                           messages=self.messages,
                                                           temperature=0,
                                                           max_tokens=2048,
                                                           top_p=1)
            # Log the response for debugging purposes
            logging.debug(response)

        except Exception as e:
            # Log any exceptions that occur during the chat completion process
            logging.error(e)
            response = {'error': e}

        return response

    def _append_message(self, content, role='user'):
        self.messages.append({'role': 'user', 'content': content})
        return self.messages

    def reset_conversation(self):
        self.messages = [self.system_message]
        return self.messages

    def send_message(self, message):
        # Append user message
        self._append_message(message)

        # Get response from api
        # response = self._get_mock_response()  # mock api for testing
        response = self._get_response()

        # Save history
        self.history = response
        if self.save:
            self._save_conversation()

        # Get the message content
        response_message = response['choices'][0]['message']
        logging.debug(f'ChatGPT: {response_message}')

        # Append response message
        self._append_message(**response_message)

        return response

    def hello_world(self):
        return 'Hello world'


if __name__ == '__main__':
    api = ChatGPT()
    api._append_message('example create cube in mel and python')
    pprint(api._get_response())
