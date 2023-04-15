from chatgpt4maya.app import MENU, create_menu, delete_menu


def initializePlugin(*args, **kwargs):
    create_menu()


def uninitializePlugin(*args, **kwargs):
    delete_menu(MENU)
