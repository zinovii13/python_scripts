@ECHO OFF

ECHO START

:: switch to venv dir
cd ./pipenv

:: create venv
CALL python -m venv .\venv

:: activate venv
CALL .\venv\Scripts/activate

:: install pipenv
CALL pip install pipenv

:: load pipenv requirements
CALL pipenv install

ECHO DONE
PAUSE