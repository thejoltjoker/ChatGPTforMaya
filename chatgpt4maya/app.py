#!/usr/bin/env python3
"""app.py
Description of app.py.
Inspired by https://github.com/JiachengXuGit/ChatGPTforNuke
"""
import logging
import sys
import os
from maya import cmds, mel
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui
from chatgpt4maya import styles, chatgpt, syntax, helpers, config
from chatgpt4maya.config import Config, MENU, BOT_USER, DATA_PATH
from chatgpt4maya.helpers import placeholder_text, get_code_parts, random_string, split_code_blocks

logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)

# Load .env during development
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class ConfigWindow(QtWidgets.QWidget):
    """
    A class representing the settings window for ChatGPT for Maya.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor for the ConfigWindow class.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None.
        """

        super().__init__(*args, **kwargs)

        # Create an instance of the Config class to access the settings data
        self.config = Config()

        # Set window properties
        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('ChatGPTSettingsWindow')
        self.setWindowTitle('Settings (ChatGPT for Maya)')
        self.setGeometry(200, 200, 1000, 100)
        self.setStyleSheet(styles.STYLE)

        # Create layout for widgets
        self.main_layout = QtWidgets.QVBoxLayout()
        self.buttons_layout = QtWidgets.QHBoxLayout()

        # Create form layout for settings
        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.setMargin(styles.Margin.medium)
        self.form_layout.setSpacing(styles.Margin.medium)

        # Add settings fields to form layout
        row = 0
        for section, keys in self.config.get_all().items():
            label_section = QtWidgets.QLabel(section)
            label_section.setProperty('selector', 'heading')
            self.form_layout.setWidget(row, QtWidgets.QFormLayout.LabelRole, label_section)
            row += 1
            for key, value in keys.items():
                label_key = QtWidgets.QLabel(key)
                field_value = QtWidgets.QLineEdit(value)
                field_value.textChanged.connect(self.action_changed)
                self.form_layout.addRow(label_key, field_value)
                row += 1

        # Create button to save changes
        self.button_save = Button('Save')
        self.button_save.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.button_save.clicked.connect(self.action_save)
        self.buttons_layout.addWidget(self.button_save)

        # Add form layout and buttons layout to main layout
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def action_changed(self):
        """Updates the appearance and text of the 'Save' button when an action is changed.
        """
        # Set the 'selector' property to 'changed' to update the appearance of the button
        self.button_save.setProperty('selector', 'changed')

        # Apply the custom stylesheet defined in the 'styles' module
        self.button_save.setStyleSheet(styles.STYLE)

        # Update the text of the button to 'Save'
        self.button_save.setText('Save')

    def action_save(self):
        """Saves the values in the form to the configuration file.

        This function iterates over the items in the form, extracts the label and field
        information, and saves each key-value pair to the configuration file using the
        ConfigParser module. If a section label is encountered, the subsequent keys and
        values will be saved to that section until another section label is encountered.

        After saving, the appearance and text of the 'Save' button are updated to indicate
        that the changes have been saved.
        """
        # Set the default section to 'DEFAULT'
        section = 'DEFAULT'

        # Iterate over the rows in the form layout
        for i in range(self.form_layout.rowCount()):
            # Get the label and field for the current row
            field = self.form_layout.itemAt(i, QtWidgets.QFormLayout.FieldRole)
            if field:
                label = self.form_layout.itemAt(i, QtWidgets.QFormLayout.LabelRole)

                # Extract the key and value from the label and field widgets
                key = label.widget().text()
                value = field.widget().text()

                # Log a message indicating the key-value pair being saved
                logging.info(f'Saving "{key} = {value}" to config')

                # Save the key-value pair to the configuration file
                self.config.set(section, key, value)
            else:
                # If a label is encountered without a corresponding field, it is assumed
                # to be a section label, and subsequent keys and values will be saved to
                # that section until another section label is encountered.
                label = self.form_layout.itemAt(i, QtWidgets.QFormLayout.LabelRole)
                widget = label.widget()
                if isinstance(widget, QtWidgets.QLabel):
                    section = widget.text()

        # Update the appearance and text of the 'Save' button to indicate that the changes
        # have been saved
        self.button_save.setText('Saved')
        self.button_save.setProperty('selector', 'saved')
        self.button_save.setStyleSheet(styles.STYLE)


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
        if response.get('error'):
            # Split response at code blocks
            response_message = [
                f"Uh oh, I must've gotten a little lost in my own thoughts there... Check the log for more info.",
                f"```{response['error']}```"]
            logging.warning(f'ChatGPT had an error "{response["error"][:48]}..."')
            self.response.emit([response_message])
        else:
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
        super().__init__(text=f'<p style="line-height: 1.4;">{content}</p>', selector='paragraph', selectable=True, *args, **kwargs)


class ChatBubble(QtWidgets.QFrame):
    # Define the __init__ method, which is called when an instance of the class is created
    def __init__(self, user: str, content: list, is_bot=True, parent=None):
        # Call the __init__ method of the parent class
        super().__init__(parent)

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
            code_parts = get_code_parts(part)
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
        code_block_id = random_string()
        frame = QtWidgets.QFrame()
        frame_layout = QtWidgets.QVBoxLayout()
        frame.setProperty('selector', 'code')

        # Add code
        for code in code_parts:
            label_code = ChatBubbleCode(code.strip())
            label_code.setProperty('code-block-id', code_block_id)
            label_code.setObjectName(code_block_id)
            frame_layout.addWidget(label_code)
        frame.setLayout(frame_layout)

        # Buttons
        buttons_layout = QtWidgets.QHBoxLayout()
        self.button_run = Button('Run')
        self.button_run.setProperty('code-block-id', code_block_id)
        self.button_run.clicked.connect(lambda: self.run_code(code_block_id))

        self.button_copy = Button('Copy')
        self.button_copy.setProperty('code-block-id', code_block_id)
        self.button_copy.clicked.connect(lambda: self.copy_code(code_block_id))

        buttons_layout.addWidget(self.button_run)
        buttons_layout.addWidget(self.button_copy)
        frame_layout.addLayout(buttons_layout)
        return frame

    def run_code(self, code_block_id):
        logging.info(f'Running code block #{code_block_id}')
        code_block_label = self.findChild(QtWidgets.QLabel, code_block_id)
        code = code_block_label.text()
        logging.debug(code)
        try:
            logging.debug('Running python')
            exec(code)
        except SyntaxError as e:
            try:
                logging.debug('Running mel')
                exec(f'mel.eval("{code}")')

            except Exception as e:
                logging.error(e)

    def copy_code(self, code_block_id):
        logging.info(f'Copying code block #{code_block_id}')
        code_block_label = self.findChild(QtWidgets.QLabel, code_block_id)
        logging.debug(code_block_label.text())
        app = QtWidgets.QApplication.instance()
        if app is None:
            # if it does not exist then a QApplication is created
            app = QtWidgets.QApplication([])
        clipboard = app.clipboard()
        clipboard.setText(code_block_label.text(), QtGui.QClipboard.Clipboard)


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
        self.config = Config()

        # Setup api
        self.api = chatgpt.ChatGPT(api_key=self.config.get('OpenAI', 'OpenAIApiKey', os.getenv('OPENAI_API_KEY')))

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
        self.input_field.setPlaceholderText(placeholder_text())
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

    def _print_args(self, *args, **kwargs):
        logging.debug(args)
        logging.debug(kwargs)

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
        self.label_new_conversation = QtWidgets.QLabel('+')
        self.label_new_conversation.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        new_conversation_icon_path = config.DATA_PATH / 'img' / 'new_conversation.png'
        new_conversation_pixmap = QtGui.QPixmap(str(new_conversation_icon_path.resolve()))
        new_conversation_pixmap_scaled = new_conversation_pixmap.scaled(QtCore.QSize(32, 32), QtCore.Qt.KeepAspectRatio)
        self.label_new_conversation.setPixmap(new_conversation_pixmap_scaled)

        self.label_new_conversation.mousePressEvent = self.action_clear

        header_layout.addWidget(QtWidgets.QLabel())  # filler to keep logo centered
        header_layout.addWidget(header_logo)
        header_layout.addWidget(self.label_new_conversation)

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

    def setup_fonts(self):
        font_db = QtGui.QFontDatabase()
        font_path = DATA_PATH / 'font'

        for font in font_path.iterdir():
            font_db.addApplicationFont(str(font.resolve()))

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
            self.input_field.setPlaceholderText('Waiting for reply')

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

    def action_clear(self, *args):
        """This is what happens when you click the clear button"""
        self.api.reset_conversation()

        # Reset input field
        self.input_field.clear()
        self.input_field.setPlaceholderText(placeholder_text())

        # Delete messages from window
        for i in reversed(range(self.conversation_layout.count())):
            if self.conversation_layout.itemAt(i):
                # self.conversation_layout.removeItem(self.conversation_layout.itemAt(i))
                self.conversation_layout.itemAt(i).widget().deleteLater()

        # Add default message
        self.update_conversation_layout()

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


def delete_menu(menu_id):
    """
    Delete a menu

    Args:
        menu_id (str): The ID of the menu to be deleted.
    """
    if cmds.menu(menu_id, exists=True):  # Check if the menu exists
        cmds.deleteUI(menu_id)  # Delete the menu


def create_menu():
    """
    Create a menu with options for the ChatGPT plugin.
    """
    # Delete menu if it already exists
    delete_menu(MENU)

    # Create menu
    menu = cmds.menu(MENU,
                     parent='MayaWindow',
                     label='ChatGPT',
                     tearOff=True)

    # Add menu items
    cmds.menuItem(parent=MENU,
                  label='Open chat',
                  # i=os.path.join(ICONS_PATH, 'reload.png'),
                  enable=True,
                  c=open_chat)
    cmds.menuItem(optionBox=True, c=open_config)
    cmds.menuItem(parent=MENU,
                  label='Quick command',
                  # i=os.path.join(ICONS_PATH, 'reload.png'),
                  enable=False)
    cmds.menuItem(parent=MENU,
                  label='Get API key...',
                  # i=os.path.join(ICONS_PATH, 'reload.png'),
                  enable=True,
                  c=open_api_key_url)


def open_api_key_url(*args):
    """
    Opens a web browser to the OpenAI API key management page.
    """
    url = 'https://platform.openai.com/account/api-keys'  # URL of the API key management page
    logging.info(f'Opening web browser to {url}')  # Log the URL that is being opened
    helpers.open_url(url)  # Open the URL in the user's default web browser


def open_chat(*args):
    """
    Opens the ChatGPT chat window.

    Args:
        *args: Unused.

    Returns:
        ui (ChatWindow): The ChatWindow instance.
    """
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()  # Get the pointer to the Maya main window
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)  # Convert the pointer to a QWidget
    ui = ChatWindow(parent=mayaMainWindow)  # Create a ChatWindow instance with the Maya window as the parent
    ui.show()  # Show the chat window
    return ui  # Return the ChatWindow instance


def open_config(*args):
    """
    Opens the ChatGPT configuration window.

    Args:
        *args: Unused.

    Returns:
        ui (ConfigWindow): The ConfigWindow instance.
    """
    mayaMainWindowPtr = omui.MQtUtil.mainWindow()  # Get the pointer to the Maya main window
    mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QtWidgets.QWidget)  # Convert the pointer to a QWidget
    ui = ConfigWindow(parent=mayaMainWindow)  # Create a ConfigWindow instance with the Maya window as the parent
    ui.show()  # Show the configuration window
    return ui  # Return the ConfigWindow instance


def open_chat_standalone(*args):
    """
    Opens a standalone version of the chat window as a separate application.

    Returns:
        None
    """
    # Create a new QApplication instance
    app = QtWidgets.QApplication(sys.argv)
    # Set attribute to use high DPI pixmaps
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    # Create a new QMainWindow instance
    main_window = QtWidgets.QMainWindow()
    # Create a new ChatWindow instance and set it as the central widget of the main window
    chat_window = ChatWindow(main_window)
    main_window.setCentralWidget(chat_window)
    # Show the main window
    chat_window.show()

    # TODO Remove before commit
    chat_window.input_field.setText('Test')
    chat_window.action_send()
    # END

    # Start the application event loop
    sys.exit(app.exec_())


def open_config_standalone(*args):
    """
    Opens a standalone version of the configuration window as a separate application.

    Returns:
        None
    """
    # Create a new QApplication instance
    app = QtWidgets.QApplication(sys.argv)
    # Set attribute to use high DPI pixmaps
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    # Create a new QMainWindow instance
    main_window = QtWidgets.QMainWindow()
    # Create a new ConfigWindow instance and set it as the central widget of the main window
    settings_window = ConfigWindow(main_window)
    main_window.setCentralWidget(settings_window)
    # Show the main window
    settings_window.show()
    # Start the application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    # open_config_standalone()
    open_chat_standalone()

    # TODO Clean up
    # TODO Clear button
