from chatgpt4maya.app import create_menu, delete_menu
from chatgpt4maya.config import MENU


def initializePlugin(*args, **kwargs):
    create_menu()


def uninitializePlugin(*args, **kwargs):
    delete_menu(MENU)
