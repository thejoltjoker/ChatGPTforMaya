import logging
import random
import re
import string
import urllib.request
import webbrowser
import zipfile
from pathlib import Path


def placeholder_text():
    """Returns a random placeholder text from a list of options"""
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
    return random.choice(placeholders)


def random_bot_handle() -> str:
    """
    Generates a random bot handle from a list of pre-defined bot names.

    Returns:
        str: A randomly selected bot name.

    """
    bot_handles = [
        "BotMaster3000",
        "RoboPal42",
        "AI_Assistant2",
        "AutoBotX99",
        "CyberHelper100",
        "TechBot3600",
        "GeniusBotX7",
        "SmartAI_Helper21",
        "Botitude3",
        "DigiPal88",
        "TheBotWhisperer9",
        "BotGenius77",
        "RoboChamp2022",
        "AI_Savant10",
        "AutoAssistX5",
        "BotWizard",
        "CyberSage",
        "TechGuruBot",
        "GeniusAI",
        "BotThinkTank",
        "DigitalHelper",
        "ArtificialBrain",
        "AI_Buddy",
        "AutoGenie",
        "CyberCompanion",
        "TechSavvyBot",
        "GeniusMind",
        "BotLogic",
        "DigitalExpert",
        "ArtificialMindset",
        "AI_Mentor",
        "AutoMind",
        "CyberCoach",
        "TechWizardBot",
        "GeniusGenie",
        "BotProdigy",
        "DigitalBrain",
        "ArtificialWhiz",
        "AI_Ninja",
        "AutoSherpa",
        "CyberSensei",
        "TechMasterBot",
        "GeniusProdigy",
        "BotBrainiac",
        "DigitalSavant",
        "ArtificialHelper",
        "AI_Wisdom",
        "AutoWhiz",
        "CyberGuru",
        "TechSageBot",
        "GeniusSavvy",
        "BotSavant",
        "DigitalScribe",
        "ArtificialSolutions",
        "AI_Support"
    ]
    return random.choice(bot_handles)  # return a randomly selected bot name from the list


def get_code_parts(part):
    """
    Extracts code parts from a given string using regex pattern matching.

    Args:
        part (str): The string to extract code parts from.

    Returns:
        list[str]: A list of strings containing the code parts found in the input string.

    """
    pattern = r"```(?:\w+\n)?([\s\S]+?)```"  # regex pattern to match code parts
    code_parts = re.findall(pattern, part)  # extract code parts from input string using regex pattern matching
    return code_parts  # return the list of code parts found in the input string


def random_string(length=16):
    """
    Generates a random string of the specified length.

    Args:
        length (int, optional): The length of the generated string. Defaults to 16.

    Returns:
        str: The generated random string.

    """
    # Use list comprehension to generate a list of random letters from the ascii_letters string
    # Join the list of letters into a single string
    return ''.join([random.choice(string.ascii_letters) for x in range(length)])


def split_code_blocks(input_string):
    """
    Splits a string at triple ticks ``` code blocks.

    Args:
        input_string (str): The string to split.

    Returns:
        list[str]: A list of strings containing the code blocks and the text outside of the code blocks.

    """
    # Regex pattern to find code blocks
    pattern = r'(```(?:\w+\n)?(?:[\s\S]+?)```)'
    return re.split(pattern, input_string)  # split the input string at the code blocks using the regex pattern


def download_file(url, path):
    """
    Downloads a file from the specified URL and saves it to the specified path.

    Args:
        url (str): The URL of the file to download.
        path (str): The path to save the downloaded file to.

    Returns:
        str: The path to the saved file.

    """
    urllib.request.urlretrieve(url, path)  # download the file from the URL and save it to the specified path
    return path  # return the path to the saved file


def unzip(path, output_path=None):
    """
    Extracts a zip file to a specified output directory.

    Args:
        path (Path): The path to the zip file to extract.
        output_path (Path, optional): The directory to extract the contents to. If not specified, the contents will be
            extracted to a new directory with the same name as the zip file in the same parent directory. Defaults to None.

    Returns:
        Path: The path to the directory containing the extracted contents.


    """
    output_path = output_path if output_path else path.parent / path.stem  # set default output path if not specified
    with zipfile.ZipFile(path, 'r') as zip_ref:  # open the zip file
        zip_ref.extractall(output_path)  # extract all files to output directory
    return output_path  # return the path to the extracted directory


def pip_location_to_path(pip_show: str):
    location = None
    for line in pip_show.split('\n'):
        if line.startswith('Location'):
            location = Path(line.replace('Location: ', ''))

    return location
def open_url(url):
    webbrowser.open(url, new=0, autoraise=True)

if __name__ == '__main__':
    open_url('https://platform.openai.com/account/api-keys')