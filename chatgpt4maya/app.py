#!/usr/bin/env python3
"""app.py
Description of app.py.
Inspired by https://github.com/JiachengXuGit/ChatGPTforNuke
"""
import configparser
import logging
import random
import re
import string
import sys
import os
import time
from pathlib import Path
from maya import cmds
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui

from chatgpt4maya import styles, chatgpt, syntax

# Config
MENU = 'ChatGPTMenu'
BOT_USER = 'Chat GPT'
REPO_PATH = Path(__file__).parent / '..'
DATA_PATH = REPO_PATH / 'chatgpt4maya' / 'src'
CONFIG_PATH = REPO_PATH / 'config.ini'

# Load .env during development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class ConfigWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO make it programmaticly add fields
        # Config parser
        self.parser = configparser.ConfigParser()
        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('ChatGPTSettingsWindow')
        self.setWindowTitle('Settings (ChatGPT for Maya)')
        self.setGeometry(200, 200, 1000, 100)
        self.setStyleSheet(styles.STYLE)
        self.main_layout = QtWidgets.QVBoxLayout()
        self.buttons_layout = QtWidgets.QHBoxLayout()

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setMargin(styles.Margin.medium)
        self.form_layout.setSpacing(styles.Margin.medium)

        self.label_api_key = QtWidgets.QLabel('OpenAIApiKey')
        self.field_api_key = QtWidgets.QLineEdit()
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_api_key)
        self.form_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.field_api_key)

        self.label_openai_path = QtWidgets.QLabel('OpenAIPackagePath')
        self.field_openai_path = QtWidgets.QLineEdit()
        self.form_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_openai_path)
        self.form_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.field_openai_path)

        self.populate_fields()
        self.button_save = Button('Save')

        self.button_save.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        # self.button_save.clicked.connect(self.read)
        self.buttons_layout.addWidget(self.button_save)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def populate_fields(self):
        self.field_api_key.setText(self.read('OpenAIApiKey'))
        self.field_openai_path.setText(self.read('OpenAIPackagePath'))

    def read(self, key):
        self.parser.read(str(CONFIG_PATH.resolve()))
        logging.info(self.parser)

        return self.parser['DEFAULT'].get(key)


class ChatGPTMessage(QtCore.QObject):
    response = QtCore.Signal(list)
    messages = QtCore.Signal(list)

    def __init__(self, api, content, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.api = api
        self.content = content

    def request(self):
        logging.info(f'Sending message "{self.content}"')
        response = self.api.send_message(self.content)
        # Split response at code blocks
        response_message = response['choices'][0]['message']
        response_content = response_message['content']
        split_content = split_code_blocks(response_content)
        logging.info(f'ChatGPT replied "{response_content[:48]}..."')
        self.response.emit(split_content)


class Button(QtWidgets.QPushButton):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setStyleSheet(styles.STYLE)
        self.setObjectName(f'button-{text.replace(" ", "-").lower()}')


class ChatBubbleText(QtWidgets.QLabel):
    def __init__(self, text, selector='paragraph', word_wrap=True, selectable=True, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setProperty('selector', selector)
        self.setWordWrap(word_wrap)
        if selectable:
            self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard)
        self.setText(text)


class ChatBubbleUsername(ChatBubbleText):
    def __init__(self, username, *args, **kwargs):
        super().__init__(text=username, selector='heading', selectable=False, *args, **kwargs)


class ChatBubbleCode(ChatBubbleText):
    def __init__(self, content, *args, **kwargs):
        super().__init__(text=content, selector='code', selectable=True, *args, **kwargs)
        text_document = self.findChild(QtGui.QTextDocument)
        highlight = syntax.PythonHighlighter(text_document)


class ChatBubbleParagraph(ChatBubbleText):
    def __init__(self, content, *args, **kwargs):
        super().__init__(text=content, selector='paragraph', selectable=True, *args, **kwargs)


class ChatBubble(QtWidgets.QFrame):
    # Define the __init__ method, which is called when an instance of the class is created
    def __init__(self, user: str, content: list, is_bot=True, parent=None):
        # Call the __init__ method of the parent class
        super().__init__(parent)

        # size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        # self.setSizePolicy(size_policy)

        # Determine the object name based on whether the user is a bot or a human
        if is_bot:
            object_name = 'chat-bubble-bot'
        else:
            object_name = 'chat-bubble-user'

        # Set the object name of the frame
        self.setObjectName(object_name)

        # Set the frame style and content margins
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.setContentsMargins(styles.Margin.medium, styles.Margin.large, styles.Margin.medium, styles.Margin.xlarge)

        # Create a ChatBubbleUsername object and add it to the layout
        label_user = ChatBubbleUsername(user)

        # Create a QVBoxLayout object and add the ChatBubbleUsername object to it
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_user)

        # Iterate through each part of the content and add it to the layout
        for part in content:
            # Check if the part contains code blocks
            code_parts = self.get_code_parts(part)
            if code_parts:
                # If it does, create a code block widget
                widget_content = self.code_block(code_parts)
            else:
                # If it doesn't, create a paragraph widget
                widget_content = ChatBubbleParagraph(part.strip())
            # Add the widget to the layout
            layout.addWidget(widget_content)

        # Set the layout of the frame to the QVBoxLayout object
        self.setLayout(layout)

    def code_block(self, code_parts):
        """Create a code block with syntax highlighting and run/copy buttons

        Args:
            code_parts:

        Returns:

        """
        self.code_block_id = random_string()
        frame = QtWidgets.QFrame()
        frame_layout = QtWidgets.QVBoxLayout()
        frame.setProperty('selector', 'code')
        # TODO remove this

        # Add code
        for code in code_parts:
            self.label_code = ChatBubbleCode(code.strip())
            self.label_code.setProperty('code-block-id', self.code_block_id)
            frame_layout.addWidget(self.label_code)
        frame.setLayout(frame_layout)

        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        self.button_run = Button('Run')
        self.button_run.setProperty('code-block-id', self.code_block_id)
        self.button_run.clicked.connect(self.run_code)

        self.button_copy = Button('Copy')
        self.button_copy.setProperty('code-block-id', self.code_block_id)
        self.button_copy.clicked.connect(self.copy_code)

        buttons_layout.addWidget(self.button_run)
        buttons_layout.addWidget(self.button_copy)
        frame_layout.addLayout(buttons_layout)
        return frame

    def run_code(self):
        logging.info(f'Running code block #{self.code_block_id}')
        exec(self.label_code.text())

    def copy_code(self):
        logging.info(f'Copying code block #{self.code_block_id}')
        app = QtWidgets.QApplication.instance()
        if app is None:
            # if it does not exist then a QApplication is created
            app = QtWidgets.QApplication([])
        clipboard = app.clipboard()
        clipboard.setText(self.label_code.text(), QtGui.QClipboard.Clipboard)

    def get_code_parts(self, part):
        pattern = r"```(?:\w+\n)?([\s\S]+?)```"
        code_parts = re.findall(pattern, part)
        return code_parts


class Spinner(QtWidgets.QFrame):
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel()
        self.setObjectName('spinner')

        spinner_path = DATA_PATH / 'img' / 'spinner.gif'
        spinner = QtGui.QMovie(str(spinner_path.resolve()))

        # Load as pixmap to scale and keep aspect ratio
        pixmap = QtGui.QPixmap(str(spinner_path.resolve()))
        scaled_pixmap = pixmap.scaled(size, size, QtCore.Qt.KeepAspectRatio)

        spinner.setScaledSize(scaled_pixmap.size())
        spinner.start()
        label.setMovie(spinner)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class ChatWindow(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(ChatWindow, self).__init__(*args, **kwargs)
        # Setup api
        self.api = chatgpt.ChatGPT()

        self.user = os.getlogin().title()
        self.margin = styles.Margin.large

        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('ChatGPTWindow')
        self.setWindowTitle('ChatGPT for Maya')
        self.setGeometry(200, 200, 1000, 1200)
        # Setup custom fonts
        self.setup_fonts()
        self.setStyleSheet(styles.STYLE)

        # Set window properties
        # self.setFixedSize(QtCore.QSize(400, 500))

        # Create layout for central widget
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setMargin(0)

        # conversation section
        self.conversation_scroll_area = QtWidgets.QScrollArea()
        self.scrollbar = QtWidgets.QScrollBar()
        self.conversation_scroll_area.setVerticalScrollBar(self.scrollbar)
        self.conversation_scroll_area.setWidgetResizable(True)
        self.conversation_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.conversation_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollbar.rangeChanged.connect(self.scroll_to_bottom)

        # The widget to fill the scroll area
        self.conversation_scroll_area_widget = QtWidgets.QWidget(self.conversation_scroll_area)

        # The actual messages layout
        self.conversation_layout = QtWidgets.QVBoxLayout(self.conversation_scroll_area_widget)
        self.conversation_layout.setStretch(0, 0)
        self.conversation_layout.setObjectName('conversation-layout')
        self.conversation_layout.setMargin(0)
        self.conversation_layout.setContentsMargins(0, self.margin, 0, 0)
        self.conversation_layout.setSpacing(self.margin)
        self.conversation_layout.setAlignment(QtCore.Qt.AlignTop)
        self.conversation_scroll_area.setWidget(self.conversation_scroll_area_widget)
        self.conversation_scroll_area.setFrameStyle(QtWidgets.QFrame.NoFrame)

        # Input section
        # Set up a vertical box layout for the input container
        frame_input_container = QtWidgets.QVBoxLayout()
        frame_input_container.setSpacing(0)
        frame_input_container.setMargin(self.margin)
        frame_input_container.setObjectName('input-container')

        # Set up a frame to contain the input section
        self.frame_input = QtWidgets.QFrame()
        self.frame_input.setObjectName('input-section')

        # Set up a horizontal box layout for the input section
        self.frame_input_layout = QtWidgets.QHBoxLayout()
        self.frame_input_layout.setSpacing(0)
        self.frame_input_layout.setMargin(0)
        self.conversation_layout.setObjectName('input-layout')

        # Set up a QLineEdit widget for the input field
        self.input_field = QtWidgets.QLineEdit()
        self.input_field.textChanged.connect(self.input_field_text_color_white)
        self.input_field.setPlaceholderText(self.placeholder_text())
        self.input_field.returnPressed.connect(self.action_send)

        # Create buttons and add actions
        self.button_send = Button('Send')
        self.button_send.clicked.connect(self.action_send)
        self.button_send.setDefault(True)
        self.button_send.setAutoDefault(True)

        self.frame_input_layout.addWidget(self.input_field)
        self.frame_input_layout.addWidget(self.button_send)
        self.frame_input.setLayout(self.frame_input_layout)
        frame_input_container.addWidget(self.frame_input)

        # Header
        header = self.create_header()

        # Assemble sections into main layout
        self.main_layout.addWidget(header)
        self.main_layout.addWidget(self.conversation_scroll_area)
        self.main_layout.addLayout(frame_input_container)

        # Update the conversation from the messages in the api
        self.update_conversation_layout()
        self.setLayout(self.main_layout)

        self.input_field.setFocus()

    def get_response(self, n):
        self.action_response_received()

    def create_header(self):
        """
        Creates a header frame widget for the application.

        Returns:
            QtWidgets.QFrame: A header frame widget.
        """
        # Create the header frame widget.
        header = QtWidgets.QFrame()
        header.setObjectName('header')

        # Create a horizontal layout for the header frame widget.
        header_layout = QtWidgets.QHBoxLayout()

        # Create a label widget for the header logo and set its alignment and object name.
        header_logo = QtWidgets.QLabel('ChatGPT for Maya')
        header_logo.setAlignment(QtCore.Qt.AlignCenter)
        header_logo.setObjectName('logotype')

        # Add the header logo label widget to the header layout.
        header_layout.addWidget(header_logo)

        # Set the margin and spacing for the header layout.
        header_layout.setMargin(self.margin)
        header_layout.setSpacing(0)

        # Set the header layout for the header frame widget.
        header.setLayout(header_layout)

        # Return the header frame widget.
        return header

    @QtCore.Slot(int, int)
    def scroll_to_bottom(self, minimum, maximum):
        self.scrollbar.setValue(maximum)

    def input_field_text_color_white(self):
        self.input_field.setStyleSheet(f'color: {styles.Color.almost_white};')

    def input_field_text_color_gray(self):
        self.input_field.setStyleSheet(f'color: {styles.Color.light_gray};')

    def placeholder_text(self):
        placeholders = ["Create a new polygon object", "Rename a selected object",
                        "Move an object to a specified location", "Scale an object to a specified size",
                        "Rotate an object to a specified angle", "Set the visibility of an object",
                        "Create a new camera", "Set the camera's position and rotation", "Create a new light",
                        "Set the light's intensity and color", "Parent one object to another", "Create a new group",
                        "Set the group's pivot point", "Create a new material", "Assign a material to an object",
                        "Create a new texture", "Assign a texture to a material",
                        "Create a new keyframe for an object's animation", "Move an object along a path",
                        "Create a new particle system", "Set the particle system's properties",
                        "Create a new constraint", "Set the constraint's target object", "Set the constraint's weight",
                        "Save the current scene to a file",
                        "Create a new polygon object and add it to the scene",
                        "Rename a selected object and change its display name in the viewport",
                        "Move an object to a specified location and set its pivot point",
                        "Scale an object to a specified size and uniformly scale its UVs",
                        "Rotate an object to a specified angle and align it to a surface",
                        "Set the visibility of an object and keyframe its visibility over time",
                        "Create a new camera and set its resolution gate",
                        "Set the camera's position and rotation and keyframe its animation",
                        "Create a new light and set its type and attributes",
                        "Set the light's intensity and color and keyframe its animation",
                        "Parent one object to another and set its local transformation",
                        "Create a new group and add objects to it",
                        "Set the group's pivot point and its transformation",
                        "Create a new material and set its attributes",
                        "Assign a material to an object and adjust its texture coordinates",
                        "Create a new texture and set its properties",
                        "Assign a texture to a material and adjust its UV mapping",
                        "Create a new keyframe for an object's animation and set its interpolation",
                        "Move an object along a path and adjust its tangents",
                        "Create a new particle system and set its emitter",
                        "Set the particle system's properties and adjust its attributes",
                        "Create a new constraint and set its target object",
                        "Set the constraint's weight and keyframe it over time",
                        "Save the current scene to a file and export selected objects to a new file"]
        placeholder_text = random.choice(placeholders)
        return placeholder_text

    def setup_fonts(self):
        font_db = QtGui.QFontDatabase()
        font_path = DATA_PATH / 'font'

        for font in font_path.iterdir():
            font_db.addApplicationFont(str(font.resolve()))
        # font = QtGui.QFont('Inter')
        # font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        # self.setFont(font)

    def action_send(self):
        """This is what happens when you click the send button"""
        user = self.user
        content = self.input_field.text()
        if content:
            # Setup multithreading to avoid gui freezing when waiting for response
            self.thread = QtCore.QThread()
            self.worker = ChatGPTMessage(self.api, content)
            self.worker.moveToThread(self.thread)
            # Connect correct methods
            self.thread.started.connect(self.worker.request)
            self.worker.response.connect(self.action_response_received)
            self.worker.response.connect(self.thread.quit)
            self.worker.response.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.button_send.setEnabled(False)
            # User message
            user_message = ChatBubble(user, [content], is_bot=False)
            self.conversation_layout.insertWidget(self.conversation_layout.count(), user_message)

            # Clear input field
            self.input_field.clear()

            # Add response
            self.spinner = Spinner()
            self.conversation_layout.addWidget(self.spinner)
            self.thread.start()

    def action_response_received(self, response):
        self.conversation_layout.removeWidget(self.spinner)
        self.spinner.close()
        response_message = ChatBubble(BOT_USER, response, is_bot=True)
        self.conversation_layout.insertWidget(self.conversation_layout.count(), response_message)

        self.button_send.setEnabled(True)
        # Reset text color
        self.input_field_text_color_gray()
        self.input_field.setPlaceholderText('Give further instructions')

    def action_clear(self):
        """This is what happens when you click the clear button"""
        self.api.reset_conversation()

        # Delete messages from window
        for i in reversed(range(self.conversation_layout.count())):
            if self.conversation_layout.itemAt(i):
                # self.conversation_layout.removeItem(self.conversation_layout.itemAt(i))
                self.conversation_layout.itemAt(i).widget().deleteLater()

        # Add default message
        self.update_conversation_layout()

    def action_copy(self):
        app = QtWidgets.QApplication()
        app.clipboard().setText('test')

    def update_conversation_layout(self):
        for msg in self.api.messages:
            if msg['role'] == 'system':
                user = BOT_USER
                content = ["Hi! \nI'm ChatGPT, how can I assist you today?"]
            elif msg['role'] == 'assistant':
                user = BOT_USER
                content = msg['content']
            else:
                user = self.user
                content = msg['content']
            self.conversation_layout.addWidget(ChatBubble(user, content))


def random_string(length=16):
    return ''.join([random.choice(string.ascii_letters) for x in range(length)])


def split_code_blocks(input_string):
    """Split a string at triple ticks ``` code blocks

    Returns:
        list: list of str

    """
    # Regex to find code blocks
    pattern = r'(```(?:\w+\n)?(?:[\s\S]+?)```)'
    return re.split(pattern, input_string)


def delete_menu(menu_id):
    """Delete a menu

    Args:
        menu_id (str):
    """
    if cmds.menu(menu_id, exists=True):
        cmds.deleteUI(menu_id)


def create_menu():
    # Delete menu if it already exists
    delete_menu(MENU)

    # Create menu
    menu = cmds.menu(MENU,
                     parent='MayaWindow',
                     label='ChatGPT',
                     tearOff=True)
    cmds.menuItem(parent=MENU,
                  label='Open chat',
                  # i=os.path.join(ICONS_PATH, 'reload.png'),
                  enable=True,
                  c=open_chat,
                  optionBox=True)
    cmds.menuItem(parent=MENU,
                  label='Quick commands',
                  # i=os.path.join(ICONS_PATH, 'reload.png'),
                  enable=False)
    cmds.menuItem(parent=MENU,
                  label='Get API key...',
                  # i=os.path.join(ICONS_PATH, 'reload.png'),
                  enable=False)


def open_chat(*args):
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)
    ui = ChatWindow(parent=mayaMainWindow)
    ui.show()
    return ui


def open_chat_standalone(*args):
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    main_window = QtWidgets.QMainWindow()
    chat_window = ChatWindow(main_window)
    main_window.setCentralWidget(chat_window)
    chat_window.show()
    # TODO Remove this code on commit
    # chat_window.conversation_layout.addWidget(
    #     ChatBubble('Johannes', ['Create a cube and position them in a row using python'], is_bot=False))
    # response = "Here's an example code to create a row of cubes using Python in Maya:\n\n```python\nimport maya.cmds as cmds\n\n# Set the number of cubes and the distance between them\nnum_cubes = 5\ndistance = 2\n\n# Create a loop to create and position the cubes\nfor i in range(num_cubes):\n    # Create a new cube\n    cube = cmds.polyCube()[0]\n    # Position the cube based on the index and distance\n    cmds.move(i * distance, 0, 0, cube)\n```\n\nThis code will create 5 cubes and position them in a row with a distance of 2 units between each cube. You can adjust the `num_cubes` and `distance` variables to create a different number of cubes or change the distance between them."
    # split_response = chatgpt.split_code_blocks(response)
    # chat_window.conversation_layout.addWidget(ChatBubble(BOT_USER, split_response))
    # END

    sys.exit(app.exec_())


def open_settings_standalone(*args):
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    main_window = QtWidgets.QMainWindow()
    settings_window = ConfigWindow(main_window)
    main_window.setCentralWidget(settings_window)
    settings_window.show()
    # TODO Remove this code on commit
    # chat_window.conversation_layout.addWidget(
    #     ChatBubble('Johannes', ['Create a cube and position them in a row using python'], is_bot=False))
    # response = "Here's an example code to create a row of cubes using Python in Maya:\n\n```python\nimport maya.cmds as cmds\n\n# Set the number of cubes and the distance between them\nnum_cubes = 5\ndistance = 2\n\n# Create a loop to create and position the cubes\nfor i in range(num_cubes):\n    # Create a new cube\n    cube = cmds.polyCube()[0]\n    # Position the cube based on the index and distance\n    cmds.move(i * distance, 0, 0, cube)\n```\n\nThis code will create 5 cubes and position them in a row with a distance of 2 units between each cube. You can adjust the `num_cubes` and `distance` variables to create a different number of cubes or change the distance between them."
    # split_response = chatgpt.split_code_blocks(response)
    # chat_window.conversation_layout.addWidget(ChatBubble(BOT_USER, split_response))
    # END

    sys.exit(app.exec_())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    open_settings_standalone()
    # open_chat_standalone()
    # TODO Clean up
    # TODO QThread
    # TODO Clear button
