# Code colors based on https://github.com/sainnhe/sonokai
import logging
import string


class Color:
    primary = '#f9c74f'
    white = '#ffffff'
    gray = '#373d45'
    light_gray = '#748191'
    mint = '#36d6a1'
    blue = '#3678d6'
    almost_white = '#dadfe6'
    almost_black = '#111314'
    dark_gray = '#1c1f24'
    code_gray = '#2a2f36'
    code_background = '#2a2f36'
    code_comments = '#7f8490'
    code_white = '#e2e2e2'
    code_yellow = '#e7c664'
    code_green = '#9ed072'
    code_orange = '#f39660'
    code_purple = '#b39df3'
    code_pink = '#fc5d7c'
    code_blue = '#76cce0'


class Font:
    def __init__(self, family='sans-serif', size='18px', weight=400):
        self.family = family
        self.size = size
        self.weight = weight
        self.size_int = int(''.join([x for x in size if x not in string.ascii_letters]))


class Margin:
    xsmall = 5
    small = 10
    medium = 15
    large = 20
    xlarge = 25
    xxlarge = 30


def hex_to_rgb(hex_str):
    """Returns a tuple representing the given hex string as RGB.

    Source: https://gist.github.com/leetrout/2382411"""
    if hex_str.startswith('#'):
        hex_str = hex_str[1:]
    return tuple([int(hex_str[i:i + 2], 16) for i in range(0, len(hex_str), 2)])


def rgb_to_hex(rgb):
    """Converts an rgb tuple to hex string for web.

    Source: https://gist.github.com/leetrout/2382411
    """
    return f"#{''.join(['%0.2X' % c for c in rgb])}"


def scale_rgb_tuple(rgb, down=True):
    """Scales an RGB tuple up or down to/from values between 0 and 1.

    Source: https://gist.github.com/leetrout/2382411
    """
    if not down:
        return tuple([int(c * 255) for c in rgb])
    return tuple([round(float(c) / 255, 2) for c in rgb])


def multiply(color, amount):
    output = []
    if isinstance(color, str) and color.startswith('#'):
        rgb = hex_to_rgb(color)
    elif isinstance(color, tuple) or isinstance(color, list):
        rgb = color
    else:
        logging.error('Not a valid color value')
        return

    for c in rgb:
        multiplied = c * amount

        # If not float
        if multiplied > 255:
            multiplied = 255
        elif multiplied > 1 and multiplied < 255:
            multiplied = int(multiplied)

        output.append(multiplied)
    return output


FONT = {'heading': Font('Montserrat', weight=800),
        'code': Font('JetBrains Mono'),
        'logo': Font('Sofia Sans', weight=800, size='32px'),
        'paragraph': Font('Inter')}

STYLE = f"""
* {{
    border: 0;
    margin: 0;
    padding: 0;
    font-family: {FONT['code'].family}, sans-serif;
    font-size: {FONT['paragraph'].size};
    font-weight: {FONT['paragraph'].weight};
    line-height: 1.4;
    color: {Color.almost_white};
    box-sizing: border-box;
    border-radius: {Margin.medium};
}}

QWidget {{
    background: {Color.dark_gray};
}}

QFrame#header{{
    border-radius: 0;
    background: {Color.almost_black};
}}
QLabel#logotype{{
    background: none;
    font-family: {FONT['logo'].family};
    font-weight: {FONT['logo'].weight};
    font-size: {FONT['logo'].size};
    width: 100%;
    text-align: center;
}}

ChatBubble {{
    padding: {Margin.medium}px;
    background: {Color.gray};
    border-radius: {Margin.medium};
}}

ChatBubble#chat-bubble-bot{{
  background: {Color.gray};
  margin-right: {Margin.xxlarge}px; 
  padding-right: {Margin.xxlarge / 2};
}}
ChatBubble#chat-bubble-user{{
  background: {Color.blue};
  margin-left: {Margin.xxlarge}px; 
  padding-left: {Margin.xxlarge / 2};
}}

Spinner {{
    padding: {Margin.large}px {Margin.medium}px {Margin.large}px;
    background: {Color.gray};
    border-radius: {Margin.medium};
    margin-right: {Margin.xxlarge}px; 
    padding-right: {Margin.xxlarge / 2};
}}

QPushButton {{
    border-radius: {Margin.small}px {Margin.small}px;
    border: none;
    background: {Color.almost_white};
    color: {Color.almost_black};
    font-family: {FONT['heading'].family};
    font-weight: {FONT['heading'].weight};
    font-size: {FONT['heading'].size};
    padding: {Margin.small}px {Margin.medium}px;
}}
QPushButton[selector='round'] {{
    border-radius: {FONT['heading'].size_int}px {FONT['heading'].size_int}px;
    padding: 13px 10px 10px;
}}

QLabel {{
    font-family: {FONT['paragraph'].family};
    line-height: 1.4;
    background: none;
}}
QLabel[selector='heading'] {{
    font-family: {FONT['heading'].family};
    font-weight: {FONT['heading'].weight};
    font-size: {FONT['heading'].size};
}}
QLabel[selector='paragraph'] {{
    font-family: {FONT['paragraph'].family};
    font-weight: {FONT['paragraph'].weight};
}}
QLabel[selector='code'] {{
    font-family: {FONT['code'].family};
    font-weight: {FONT['code'].weight};
}}

QFrame[selector='code'] {{
    font-family: {FONT['code'].family};
    font-weight: {FONT['code'].weight};
    background: {Color.dark_gray};
}}

QLineEdit {{
    background: rgba(0,0,0,0);
    font-family: {FONT['paragraph'].family};
    font-weight: {FONT['paragraph'].weight};
    color: {Color.light_gray}
}}

QFrame#input-section {{
    background: {Color.almost_black};
    height: {FONT['heading'].size_int + Margin.medium * 2 + Margin.xsmall * 2 + Margin.xsmall * 2}px;
    border-radius: {(FONT['heading'].size_int + Margin.medium * 2 + Margin.xsmall * 2 + Margin.xsmall * 2) / 2}px;
    padding: {Margin.xsmall}px {Margin.xsmall}px {Margin.xsmall}px {Margin.xxlarge}px;
}}

Button#button-send {{
    height: {FONT['heading'].size_int + Margin.medium * 2}px;
    padding: {Margin.xsmall}px {Margin.medium * 3}px;
    line-height: 1;
    border-radius: {(FONT['heading'].size_int + Margin.medium * 2 + Margin.xsmall * 2) / 2}px;
    background: {Color.almost_white}
}}
Button#button-send:hover {{
    transition: all 0.1s ease;
    background: {rgb_to_hex(multiply(Color.almost_white, 0.9))};
}}

Button#button-run {{
    background: {Color.mint};
}}
Button#button-run:hover {{
    background: {rgb_to_hex(multiply(Color.mint, 1.1))};
}}
Button#button-save {{
    height: {FONT['heading'].size_int + Margin.medium * 2}px;
    padding: {Margin.xsmall}px {Margin.medium * 3}px;
    line-height: 1;
    border-radius: {(FONT['heading'].size_int + Margin.medium * 2 + Margin.xsmall * 2) / 2}px;
    background: {Color.mint};
}}
Button#button-save:hover {{
    background: {rgb_to_hex(multiply(Color.mint, 1.1))};
}}
Button#button-save:hover {{
    background: {rgb_to_hex(multiply(Color.mint, 1.1))};
}}
Button#button-save[selector='saved']:hover {{
    background: {Color.mint};
}}
Button#button-save[selector='changed'] {{
    background:  {Color.light_gray};
}}
Button#button-save[selector='changed']:hover {{
    background:  {rgb_to_hex(multiply(Color.light_gray, 1.1))};
}}


Button#button-copy {{
    background: {Color.light_gray};
}}
Button#button-copy:hover {{
    background: {rgb_to_hex(multiply(Color.light_gray, 1.1))};
}}

QScrollArea{{
    padding: 0 {Margin.large}px;
}}

QScrollBar:vertical {{
    border: none;
    background: {Color.almost_black};
    width: {Margin.medium * 2};
    border-radius: {(Margin.medium - 3) / 2}px;
    margin: {Margin.xsmall}px 0 15px {Margin.medium}px;
}}
QScrollBar::handle:vertical {{
    background: {Color.gray};
    width: {Margin.medium};
    border-radius: {(Margin.medium - 3) / 2}px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical {{
    border: none;
    background: {Color.gray};
    height: 0;
    subcontrol-position: bottom;
    subcontrol-origin: margin;
}}

QScrollBar::sub-line:vertical {{
    border: none;
    background: {Color.gray};
    height: 0;
    subcontrol-position: top;
    subcontrol-origin: margin;
}}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
    border: none;
    width: 3px;
    height: 3px;
    background: white;
}}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
background: none;
}}

ConfigWindow {{
    background: {Color.gray};
    padding: {Margin.medium};
    font-family: {FONT['code'].family}, monospace;
    font-size: {FONT['paragraph'].size};
    font-weight: {FONT['paragraph'].weight};
}}
ConfigWindow QLabel {{
    font-family: {FONT['code'].family}, sans-serif;
    font-weight: {FONT['paragraph'].weight};
    padding: {Margin.medium};
}}
ConfigWindow QLineEdit {{
    background: {Color.dark_gray};
    font-family: {FONT['code'].family}, monospace;
    padding: {Margin.medium};
}}
"""
