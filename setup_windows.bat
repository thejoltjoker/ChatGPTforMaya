@echo off

set /P MAYA_VERSION=What Maya version are you using? (2021, 2022, etc): 

set MAYA_BIN_PATH=C:\Program Files\Autodesk\Maya%MAYA_VERSION%\bin\
set VENV_PATH=%~dp0chatgpt4maya\src\venv
set MODULE_PATH=%~dp0module
IF EXIST "%USERPROFILE%\Documents" (
    set USER_MODULE_PATH=%USERPROFILE%\Documents\maya\%MAYA_VERSION%\modules
) ELSE (
    set USER_MODULE_PATH=%MODULE_PATH%
    setx MAYA_MODULE_PATH %MODULE_PATH%;%MAYA_MODULE_PATH%
)
set MODULE=%USER_MODULE_PATH%\chatGPTForMayaModule.mod


echo ###############################
echo # Creating symlink for mayapy #
echo ###############################
cd %MAYA_BIN_PATH%
mklink python.exe mayapy.exe

echo:
echo ####################################
echo # Installing virtualenv for mayapy #
echo ####################################
"%MAYA_BIN_PATH%mayapy.exe" -m pip install --user virtualenv

echo:
echo ################################
echo # Creating virtual environment #
echo ################################
"%MAYA_BIN_PATH%python.exe" -m virtualenv %VENV_PATH%

echo:
echo #####################
echo # Installing openai #
echo #####################
%VENV_PATH%\Scripts\pip install openai
cd %~dp0
%VENV_PATH%\Scripts\pip show openai > .\chatgpt4maya\src\openai.txt

echo:
echo #####################
echo # Installing module #
echo #####################
>%MODULE%    echo + ChatGPTForMaya 0.1 %~dp0
>>%MODULE%   echo PYTHONPATH += %~dp0
>>%MODULE%   echo PYTHONPATH += %~dp0chatgpt4maya\src\venv\Lib\site-packages
>>%MODULE%   echo MAYA_PLUG_IN_PATH += %~dp0plugin