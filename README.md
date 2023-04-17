<p align="center">
    <h1 align="center">
        <b>ChatGPT for Maya</b>
    </h1>
    <p align="center">
    The power of ChatGPT directly in Autodesk Maya
    <br />
    <a href="https://chat.openai.com"><strong>chat.openai.com</strong></a>
    <br />
    <br />
    <a href="https://img.shields.io/eclipse-marketplace/l/https://spdx.org/licenses/BSD-3-Clause.html">
    <img src="https://img.shields.io/static/v1?label=Licence&message=BSD-3&color=000" />
    </a>
    <img src="https://img.shields.io/static/v1?label=Stage&message=Beta&color=2BB4AB" />
    <br />
    <br />
    <img src="https://github.com/thejoltjoker/ChatGPTforMaya/blob/master/chatgpt4maya/src/img/screenshot_01.png" alt=Screenshot">
  </p>
</p>

# Features

- Interactive chat window with ChatGPT
- Get AI generated tips, instructions or ideas
- Automate tasks in a simple manner
- Run and/or copy the code blocks from within chat window

# Installation

## Windows

### Automatic installation

1. Download this repository and place it somewhere permanently*
2. Right click on `setup_windows.bat` and choose _Run as administrator_
3. Get an API key from [openai.com](https://platform.openai.com/account/api-keys)
4. Open Maya and load the plugin `chatGPTForMayaPlugin.py` from the list
5. A new Maya menu should show up called `ChatGPT`
6. Click on the option box for _ChatGPT > Open chat_
7. Enter your API key into `OpenAiApiKey` and save settings

_Notes:_

- If you move it later you might have to re-run the setup

### Manual installation

**Setup virtual environment**

_Setting up a virtual environment is optional but recommended to avoid conflicts with libraries and potentially cause
instability in Maya._

1. Create a symlink for `mayapy.exe` called `python.exe` in the same folder
    - https://help.autodesk.com/view/MAYACRE/ENU/?guid=GUID-6AF99E9C-1473-481E-A144-357577A53717
2. Create a virtual environment using `python.exe`
3. Run `pip install openai` in your virtual environment
4. Run `pip show openai` and copy the path from _Location:_

**Setup openai**

_Skip this section if you did the steps in the virtual environment section_

1. Create a symlink for `mayapy.exe` called `python.exe` in the same folder
    - https://help.autodesk.com/view/MAYACRE/ENU/?guid=GUID-6AF99E9C-1473-481E-A144-357577A53717
2. Create a virtual environment using `python.exe`
3. Run `pip install openai` in your virtual environment
4. Run `pip show openai` and copy the path from _Location:_

**Setup repository**

1. Clone this repository
2. Modify contents of _module/chatGPTForMayaModule.mod_ to look something like this:
    ```
   + ChatGPTForMaya 0.1 C:\path\to\ChatGPTforMaya\
   PYTHONPATH += C:\path\to\ChatGPTforMaya\
   PYTHONPATH += C:\path\to\virtualenv\ChatGPTforMaya\chatgpt4maya\src\venv\Lib\site-packages
   MAYA_PLUG_IN_PATH += C:\path\to\ChatGPTforMaya\plugin
   ```
3. Add `C:\path\to\ChatGPTforMaya\module` to `MAYA_MODULE_PATH` environment variable
4. Get an api key from [openai.com](https://platform.openai.com/account/api-keys)
    - _Optional:_ Add API key to `OPENAI_API_KEY` environment variable
6. Open Maya and load the plugin `chatGPTForMayaPlugin.py` from the list
7. A new Maya menu should show up called `ChatGPT`
8. Click on the option box for _ChatGPT > Open chat_
9. Enter your API key into `OpenAiApiKey`
10. Enter the path you got from `pip show open` into `OpenAILibraryPath`

# links:

- https://github.com/openai/openai-cookbook/blob/main/techniques_to_improve_reliability.md

# License

This project is licensed under a [Modified BSD license](https://spdx.org/licenses/BSD-3-Clause.html).

```
Copyright (c) 2023 Johannes Andersson.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
    3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

# Disclaimer

I am not affiliated, associated, authorized, endorsed by, or in any way officially connected with Autodesk, OpenAI,
ChatGPT, or any of its subsidiaries or its affiliates.

The official ChatGPT website can be found at https://chat.openai.com.

The official Autodesk website can be found at https://autodesk.com.

The names OpenAI and ChatGPT as well as related names, marks, emblems and images are registered trademarks of their
respective owners.

# Todo:

- Write usage instructions
- Add clear conversation button
- Add quick command feature