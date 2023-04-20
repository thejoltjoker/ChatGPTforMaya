import shutil
import tempfile
import configparser
import os
import sys
from pathlib import Path
import logging
import os
import venv
import subprocess

from chatgpt4maya import helpers

# Load .env during development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

MENU = 'ChatGPTMenu'
BOT_USER = 'ChatGPT'
REPO_PATH = Path(__file__).parent / '..'
DATA_PATH = REPO_PATH / 'chatgpt4maya' / 'src'
CONFIG_PATH = Path.home() / '.ChatGPTForMaya'
LOG_FORMAT = '%(asctime)s [ChatGPT]: %(message)s'
LOG_FORMAT_DEBUG = '%(asctime)s %(name)s %(levelname)s: %(message)s'

logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT_DEBUG)


def maya_script_path():
    paths = []
    environment = os.getenv('MAYA_SCRIPT_PATH')
    if environment:
        if sys.platform == 'win32':
            paths = environment.split(';')
        else:
            paths = environment.split(':')
    return paths


def config_path():
    output = CONFIG_PATH
    paths = maya_script_path()
    if paths:
        user_paths = [x for x in sorted(paths, key=len) if x.startswith(str(Path().home().as_posix())) and 'maya' in x]
        if user_paths:
            output = Path(paths[0]) / 'ChatGPTForMaya'
    return output


class Config:
    def __init__(self, path=None):
        """
        Initialize a new Config object with the given path to the configuration file.
        If no path is provided, the default path is used.
        If the configuration file does not exist, create it with some default values.

        Args:
            path (pathlib.Path, optional): Path to the configuration file. Defaults to None.
        """
        self.path = path if path else config_path() / 'config.ini'
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str

        # If the configuration file does not exist, create it with some default values
        if not self.path.is_file():
            self.parser['OpenAI'] = {'OpenAIApiKey': '',
                                     'OpenAILibraryPath': ''}
            if not self.path.parent.is_dir():
                self.path.parent.mkdir(exist_ok=True, parents=True)
            with self.path.open('w') as configfile:
                self.parser.write(configfile)

        # Setup openai api key
        if not self.get('OpenAI', 'OpenAIApiKey') and os.getenv('OPENAI_API_KEY'):
            self.set('OpenAI', 'OpenAIApiKey', os.getenv('OPENAI_API_KEY'))

        # Setup openai library path
        openai_txt_path = DATA_PATH / 'openai.txt'
        if not self.get('OpenAI', 'OpenAILibraryPath') and openai_txt_path.is_file():
            openai_pip_path = helpers.pip_location_to_path(openai_txt_path.read_text())
            library_path = str(openai_pip_path.resolve())
            self.set('OpenAI', 'OpenAILibraryPath', library_path)

    def _config_path_string(self):
        return str(self.path.resolve())

    def _read(self):
        # Read the configuration file
        self.parser.read(self._config_path_string())
        return self.parser

    def _write(self):
        with self.path.open('w') as configfile:
            self.parser.write(configfile)

    def get(self, section, key, fallback=None):
        """
        Read a value from the configuration file for the given key.

        Args:
            key (str): The key to read from the configuration file.

        Returns:
            str: The value associated with the key, or None if the key is not found.
        """
        self._read()
        value = fallback
        if self.parser.has_section(section):
            value = self.parser[section].get(key)
        else:
            logging.warning(f'Section "{section}" does not exist in {self.path.name}')
        return value

    def get_all(self):
        self._read()
        output = {}
        all_sections = self.parser.sections()
        all_sections.append('DEFAULT')
        for each_section in self.parser.sections():
            output[each_section] = {}
            for (each_key, each_val) in self.parser.items(each_section):
                output[each_section][each_key] = each_val

        return output

    def set(self, section, key, value):
        """
        Write a key-value pair to the configuration file.

        Args:
            key (str): The key to write to the configuration file.
            value (str): The value to associate with the key.
        """
        self._read()
        if not self.parser.has_section(section):
            self.parser[section] = {key: value}
        else:
            # Write the key-value pair to the configuration file
            self.parser[section][key] = value
        self._write()
        return self.parser


def setup_openai():
    # Set up a virtual environment using venv
    env_dir = config_path() / 'venv'
    env_dir.mkdir(exist_ok=True, parents=True)
    venv.create(env_dir, with_pip=True)

    # where requirements.txt is in same dir as this script
    subprocess.check_call([env_dir / 'bin/pip', "install", "openai"], cwd=dir)

    # Return path to virtual environment site-packages
    return os.path.join(env_dir, 'lib', 'python3.7', 'site-packages')


# def setup_openai():
#     temp_path = Path(tempfile.gettempdir())
#     url = 'https://github.com/openai/openai-python/archive/refs/heads/main.zip'
#     zip_file = download_file(url, temp_path / 'openai.zip')
#     unzipped = unzip(zip_file, temp_path / 'openai-repo')
#     config = Config()
#     # Copy files to mayascriptpath
#     for root, dirs, files in os.walk(unzipped):
#         root_path = Path(root)
#         if root_path.name == 'openai':
#             destination = Path(maya_script_path()[0] if maya_script_path() else REPO_PATH) / 'openai'
#             if not destination.is_dir():
#                 shutil.copytree(root_path, destination)
#                 config.set('OpenAI', 'OpenAIPackagePath', str(destination.parent.resolve().as_posix()))
#                 logging.info(f'Downloaded and extracted openai package to {destination.resolve()}')
#                 return True
#             else:
#                 logging.warning(f"There's already a folder called openai in {destination.parent.resolve()}")
#                 return False
#     logging.warning('Failed to download and extract openai')
#     return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    # setup_openai()
    print(config_path())